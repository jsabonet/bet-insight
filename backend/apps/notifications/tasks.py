import logging
import hashlib
import json
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.db.models import Q

from apps.analysis.models import Analysis
from apps.matches.models import Match
from apps.matches.services.football_api import FootballAPIService
from .delivery import deliver_push_once
from .models import PushSubscription
from .push import web_push_is_configured

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='notifications.send_analysis_ready_push', max_retries=3, default_retry_delay=60)
def send_analysis_ready_push(self, analysis_id):
    if not web_push_is_configured():
        return {'sent': 0, 'configured': False}

    analysis = Analysis.objects.select_related(
        'user', 'match__home_team', 'match__away_team', 'match__league',
    ).filter(pk=analysis_id).first()
    if not analysis or not analysis.user.push_enabled:
        return {'sent': 0}

    subscriptions = PushSubscription.objects.filter(
        user=analysis.user,
        active=True,
        analysis_ready_enabled=True,
    ).select_related('user')
    payload = {
        'title': 'Análise pronta',
        'body': f"{analysis.match.home_team.name} vs {analysis.match.away_team.name}",
        'url': f'/match/{analysis.match_id}',
        'tag': f'analysis-ready-{analysis.pk}',
    }
    sent = 0
    failed = False
    for subscription in subscriptions:
        delivered = deliver_push_once(subscription, f'analysis-ready:{analysis.pk}', payload)
        if delivered:
            sent += 1
        elif PushSubscription.objects.filter(pk=subscription.pk, active=True).exists():
            failed = True

    if failed:
        raise self.retry(exc=RuntimeError('Falha temporária ao enviar uma notificação push'))
    return {'sent': sent}


@shared_task(bind=True, name='notifications.send_analyzed_match_reminders', max_retries=3, default_retry_delay=60)
def send_analyzed_match_reminders(self):
    if not web_push_is_configured():
        return {'sent': 0, 'configured': False}

    now = timezone.now()
    starts_after = now + timedelta(minutes=55)
    starts_before = now + timedelta(minutes=65)
    analyses = Analysis.objects.filter(
        match__match_date__gt=starts_after,
        match__match_date__lte=starts_before,
        match__status__in=('scheduled', 'NS', 'TBD'),
        user__push_enabled=True,
    ).select_related('user', 'match__home_team', 'match__away_team')

    sent = 0
    failed = False
    for analysis in analyses:
        subscriptions = PushSubscription.objects.filter(
            user=analysis.user,
            active=True,
            match_reminders_enabled=True,
        ).select_related('user')
        payload = {
            'title': 'Partida analisada em breve',
            'body': f"{analysis.match.home_team.name} vs {analysis.match.away_team.name} começa em cerca de 1 hora.",
            'url': f'/match/{analysis.match_id}',
            'tag': f'match-reminder-{analysis.match_id}',
        }
        for subscription in subscriptions:
            delivered = deliver_push_once(
                subscription,
                f'match-reminder:{analysis.match_id}:60m',
                payload,
            )
            if delivered:
                sent += 1
            elif PushSubscription.objects.filter(pk=subscription.pk, active=True).exists():
                failed = True

    if failed:
        raise self.retry(exc=RuntimeError('Falha temporária ao enviar lembretes push'))
    return {'sent': sent}


def _classify_match_event(event):
    event_type = (event.get('type') or '').strip().lower()
    detail = (event.get('detail') or '').strip()
    detail_lower = detail.lower()

    if event_type == 'goal':
        if 'penalty' in detail_lower:
            return 'penalty'
        return 'goal'
    if event_type == 'card':
        if 'red' in detail_lower or 'second yellow' in detail_lower:
            return 'red_card'
        if 'yellow' in detail_lower:
            return 'yellow_card'
    if event_type in ('subst', 'substitution'):
        return 'substitution'
    if event_type == 'var':
        return 'var'
    return None


def _match_event_payload(match, event):
    event_kind = _classify_match_event(event)
    team = (event.get('team') or {}).get('name') or 'Uma equipa'
    minute = (event.get('time') or {}).get('elapsed')
    minute_text = f' aos {minute}′' if minute is not None else ''
    detail = (event.get('detail') or '').strip()
    player = (event.get('player') or {}).get('name')
    assist = (event.get('assist') or {}).get('name')

    if event_kind == 'goal':
        title = 'Golo na partida analisada'
        description = f'{team} marcou{minute_text}.'
        if detail:
            description = f'{team} marcou{minute_text} ({detail.lower()}).'
    elif event_kind == 'penalty':
        title = 'Penálti na partida analisada'
        description = f'{team}: {detail.lower()}{minute_text}.'
    elif event_kind == 'red_card':
        if 'second yellow' in detail.lower():
            title = 'Expulsão por segundo amarelo'
            description = f'{team} ficou com um jogador expulso por segundo amarelo{minute_text}.'
        else:
            title = 'Cartão vermelho'
            description = f'{team} recebeu cartão vermelho{minute_text}.'
    elif event_kind == 'yellow_card':
        title = 'Cartão amarelo'
        description = f'{team} recebeu cartão amarelo{minute_text}.'
    elif event_kind == 'substitution':
        reason = f"{detail} {event.get('comments') or ''}".lower()
        injury_reported = any(term in reason for term in ('injury', 'lesion', 'lesão'))
        title = 'Substituição por lesão' if injury_reported else 'Substituição na partida'
        description = f'{team}: {player or "jogador"}'
        if assist:
            description += f' saiu; {assist} entrou'
        if injury_reported:
            description += ' (lesão indicada no evento)'
        description += f'{minute_text}.'
    else:
        title = 'Atualização do VAR'
        description = f'{team}: {detail or "revisão VAR"}{minute_text}.'

    return {
        'title': title,
        'body': description[:180],
        'url': f'/match/{match.pk}',
        'tag': f'match-event-{match.pk}-{event_kind}',
    }


@shared_task(bind=True, name='notifications.poll_analyzed_match_events', max_retries=2, default_retry_delay=60)
def poll_analyzed_match_events(self):
    if not web_push_is_configured():
        return {'sent': 0, 'configured': False}
    if not settings.API_FOOTBALL_KEY:
        logger.warning('Push de eventos ao vivo ignorado: API_FOOTBALL_KEY não está configurada')
        return {'sent': 0, 'api_configured': False}

    now = timezone.now()
    match_ids = Analysis.objects.filter(
        user__push_enabled=True,
        match__status__in=('live', 'scheduled'),
        match__match_date__gte=now - timedelta(hours=4),
        match__match_date__lte=now + timedelta(hours=1),
        match__api_football_id__isnull=False,
        user__push_subscriptions__active=True,
        user__push_subscriptions__match_events_enabled=True,
    ).values_list('match_id', flat=True).distinct()
    matches = list(
        Match.objects.filter(pk__in=match_ids)
        .select_related('home_team', 'away_team')
        .order_by('match_date')
    )
    if not matches:
        return {'sent': 0, 'matches': 0}

    api = FootballAPIService()
    live_result = api.get_live_fixtures()
    if not live_result.get('success'):
        logger.warning('Não foi possível consultar partidas ao vivo para push: %s', live_result.get('error'))
        return {'sent': 0, 'matches': 0, 'api_error': live_result.get('error')}

    live_fixture_ids = {
        (fixture.get('fixture') or {}).get('id')
        for fixture in live_result.get('fixtures', [])
    }
    monitored = [match for match in matches if match.api_football_id in live_fixture_ids]
    sent = 0
    failures = 0

    for match in monitored:
        result = api.get_fixture_events(match.api_football_id)
        if not result.get('success'):
            failures += 1
            logger.warning(
                'Falha ao obter eventos ao vivo da partida %s: %s',
                match.api_football_id,
                result.get('error'),
            )
            continue

        for event in result.get('events', []):
            event_kind = _classify_match_event(event)
            if not event_kind:
                continue
            identity = {
                'time': event.get('time'),
                'team': (event.get('team') or {}).get('id'),
                'type': event.get('type'),
                'detail': event.get('detail'),
                'player': (event.get('player') or {}).get('id'),
                'assist': (event.get('assist') or {}).get('id'),
            }
            serialized_event = json.dumps(identity, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
            event_hash = hashlib.sha256(serialized_event.encode('utf-8')).hexdigest()
            event_key = f'match-event:{match.pk}:{event_hash}'
            payload = _match_event_payload(match, event)
            subscriptions = PushSubscription.objects.filter(
                user__analyses__match=match,
                user__push_enabled=True,
                active=True,
                match_events_enabled=True,
            ).select_related('user').distinct()

            for subscription in subscriptions:
                if deliver_push_once(subscription, event_key, payload):
                    sent += 1
                elif PushSubscription.objects.filter(pk=subscription.pk, active=True).exists():
                    failures += 1

    return {'sent': sent, 'matches': len(monitored), 'failures': failures}


def enqueue_affiliate_push(user_id, event_type, event_key, title, body):
    try:
        send_affiliate_push.delay(user_id, event_type, event_key, title, body)
    except Exception:
        logger.exception('Não foi possível agendar push de afiliado %s para usuário %s', event_type, user_id)


@shared_task(bind=True, name='notifications.send_affiliate_push', max_retries=3, default_retry_delay=60)
def send_affiliate_push(self, user_id, event_type, event_key, title, body):
    if not web_push_is_configured():
        return {'sent': 0, 'configured': False}

    subscriptions = PushSubscription.objects.filter(
        user_id=user_id,
        user__push_enabled=True,
        active=True,
        affiliate_notifications_enabled=True,
    ).select_related('user')

    sent = 0
    failed = False
    payload = {
        'title': title,
        'body': body,
        'url': '/affiliate',
        'tag': f'affiliate-{event_type}-{event_key}',
    }
    for subscription in subscriptions:
        delivered = deliver_push_once(
            subscription,
            f'affiliate:{event_type}:{event_key}',
            payload,
        )
        if delivered:
            sent += 1
        elif PushSubscription.objects.filter(pk=subscription.pk, active=True).exists():
            failed = True

    if failed:
        raise self.retry(exc=RuntimeError('Falha temporária ao enviar notificação push de afiliado'))
    return {'sent': sent}


def enqueue_premium_daily_bets_push(target_date, multiple_count, value_count):
    if multiple_count + value_count <= 0:
        return
    try:
        send_premium_daily_bets_push.delay(
            target_date.isoformat(),
            multiple_count,
            value_count,
        )
    except Exception:
        logger.exception('Não foi possível agendar alerta de bilhetes Premium para %s', target_date)


@shared_task(bind=True, name='notifications.send_premium_daily_bets_push', max_retries=3, default_retry_delay=60)
def send_premium_daily_bets_push(self, target_date, multiple_count, value_count):
    if not web_push_is_configured():
        return {'sent': 0, 'configured': False}

    now = timezone.now()
    subscriptions = PushSubscription.objects.filter(
        user__is_premium=True,
        user__push_enabled=True,
        active=True,
        premium_bets_enabled=True,
    ).filter(
        Q(user__premium_until__gte=now)
        | Q(user__premium_until__isnull=True, user__subscriptions__status='active',
            user__subscriptions__plan_slug__in=('premium_vitalicio', 'premium_vitalicio_teste'),
            user__subscriptions__end_date__isnull=True)
    ).distinct().select_related('user')
    total = multiple_count + value_count
    payload = {
        'title': 'Bilhetes automáticos disponíveis',
        'body': (
            f'{total} novo(s) bilhete(s) para {target_date}: '
            f'{multiple_count} múltiplo(s) e {value_count} value bet(s).'
        ),
        'url': '/daily-bets',
        'tag': f'premium-daily-bets-{target_date}',
    }

    sent = 0
    failed = False
    event_key = f'premium-daily-bets:{target_date}'
    for subscription in subscriptions:
        delivered = deliver_push_once(subscription, event_key, payload)
        if delivered:
            sent += 1
        elif PushSubscription.objects.filter(pk=subscription.pk, active=True).exists():
            failed = True

    if failed:
        raise self.retry(exc=RuntimeError('Falha temporária ao enviar alerta de bilhetes Premium'))
    return {'sent': sent, 'recipients': subscriptions.count()}