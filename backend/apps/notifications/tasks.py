import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.analysis.models import Analysis
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