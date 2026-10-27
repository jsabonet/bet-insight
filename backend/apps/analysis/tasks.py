"""
Celery Tasks para Geração e Validação de Bilhetes Diários

Tasks:
1. generate_daily_bets: Gera bilhetes múltiplos diariamente às 06:00 UTC
2. validate_daily_bets: Valida resultados de apostas pendentes (a cada 1 hora)
"""

import logging
from celery import shared_task
from django.utils import timezone
from django.db import models
from datetime import timedelta

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='analysis.generate_daily_bets')
def generate_daily_bets(self, triggered_by='celery', user_id=None):
    """
    Task executada diariamente para gerar bilhetes múltiplos automáticos
    
    Agenda sugerida: 06:00 UTC (horário com poucas requisições de usuários)
    
    Esta task:
    - Analisa todas as partidas do dia
    - Gera bilhetes múltiplos (3x, 5x, 7x)
    - Usa HybridAnalysisOrchestrator existente
    """
    from apps.analysis.services.daily_bet_generator import DailyBetGenerator
    from apps.analysis.models import TaskExecution
    from django.contrib.auth import get_user_model
    logger.info("=" * 100)
    logger.info("🎯 TASK: GENERATE DAILY BETS - INICIANDO")
    logger.info("=" * 100)
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"Timestamp: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Criar registro de execução
    User = get_user_model()
    execution = TaskExecution.objects.create(
        task_name='generate_daily_bets',
        task_id=self.request.id,
        triggered_by=triggered_by,
        triggered_by_user=User.objects.get(id=user_id) if user_id else None
    )
    
    try:
        generator = DailyBetGenerator()
        
        # Gerar bilhetes e value bets
        results = generator.generate_for_today()
        if results.get('total_bets', 0) > 0:
            from apps.notifications.tasks import enqueue_premium_daily_bets_push
            enqueue_premium_daily_bets_push(
                timezone.localdate(),
                results.get('multiple_count', 0),
                results.get('value_count', 0),
            )
        
        logger.info(f"\n{'=' * 100}")
        logger.info("✅ TASK CONCLUÍDA COM SUCESSO")
        logger.info(f"{'=' * 100}")
        logger.info(f"📋 Bilhetes múltiplos: {results['multiple_count']}")
        logger.info(f"⚡ Seleções de valor geradas: {results['value_count']}")
        logger.info(f"⚽ Partidas analisadas: {results['matches_analyzed']}")
        logger.info(f"🔌 Requisições API (estimado): {results['api_calls']}")
        logger.info(f"{'=' * 100}\n")
        
        result = {
            'status': 'success',
            'task_id': self.request.id,
            'timestamp': timezone.now().isoformat(),
            'results': results
        }
        
        # Atualizar registro de execução
        execution.mark_finished(status='success', result_data=result)
        
        return result
        
    except Exception as e:
        logger.error(f"\n{'=' * 100}")
        logger.error("❌ ERRO NA TASK")
        logger.error(f"{'=' * 100}")
        logger.error(f"Erro: {str(e)}", exc_info=True)
        logger.error(f"{'=' * 100}\n")
        
        # Atualizar registro de execução
        execution.mark_finished(status='failed', error_message=str(e))
        
        # Re-raise para Celery marcar como falha
        raise


@shared_task(bind=True, name='analysis.validate_daily_bets')
def validate_daily_bets(self, triggered_by='celery', user_id=None):
    """
    Task executada periodicamente para validar resultados de apostas após jogos finalizarem
    
    Agenda sugerida: A cada 1 hora
    
    Esta task:
    - Busca apostas pendentes dos últimos 7 dias
    - Verifica se jogos finalizaram
    - Valida resultados automaticamente
    - Atualiza status (won/lost/partial/cancelled)
    """
    from apps.analysis.models import DailyBet, TaskExecution
    from django.contrib.auth import get_user_model
    
    logger.info("=" * 100)
    logger.info("🔍 TASK: VALIDATE DAILY BETS - INICIANDO")
    logger.info("=" * 100)
    logger.info(f"Task ID: {self.request.id}")
    logger.info(f"Timestamp: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Criar registro de execução
    User = get_user_model()
    execution = TaskExecution.objects.create(
        task_name='validate_daily_bets',
        task_id=self.request.id,
        triggered_by=triggered_by,
        triggered_by_user=User.objects.get(id=user_id) if user_id else None
    )
    
    try:
        # Buscar apostas pendentes dos últimos 7 dias
        cutoff_date = timezone.now().date() - timedelta(days=7)
        
        pending_bets = DailyBet.objects.filter(
            status='pending',
            is_validated=False,
            date__gte=cutoff_date
        ).order_by('date')
        
        logger.info(f"\n📊 Apostas pendentes encontradas: {pending_bets.count()}")
        
        if pending_bets.count() == 0:
            logger.info("   ℹ️  Nenhuma aposta pendente para validar")
            logger.info(f"{'=' * 100}\n")
            return {
                'status': 'success',
                'task_id': self.request.id,
                'validated_count': 0,
                'pending_count': 0
            }
        
        validated_count = 0
        still_pending_count = 0

        # Sincronizar resultados oficiais das datas com bilhetes pendentes.
        # Os fixtures dos bilhetes podem não existir como Match local, por isso
        # o mapa de resultados vem da API e é reutilizado por todos os bilhetes.
        from .services.match_result_sync import sync_results_for_date

        dates = sorted(set(pending_bets.values_list('date', flat=True)))
        results_map = {}
        for pending_date in dates:
            try:
                results_map.update(sync_results_for_date(pending_date))
            except Exception:
                logger.exception("Falha ao sincronizar resultados de %s", pending_date)

        logger.info(f"📡 Resultados sincronizados: {len(results_map)} fixtures")

        for bet in pending_bets:
            logger.info(f"\n{'─' * 80}")
            logger.info(f"Validando: {bet}")
            logger.info(f"   Data: {bet.date.strftime('%d/%m/%Y')}")
            logger.info(f"   Tipo: {bet.get_bet_type_display()}")
            logger.info(f"   Seleções: {len(bet.selections)}")
            
            # Tentar validar
            was_validated = bet.validate_result(results_map=results_map)
            
            if was_validated:
                validated_count += 1
                logger.info(f"   ✅ Validado: {bet.get_status_display()}")
                logger.info(f"   Resultado: {bet.actual_result}")
            else:
                still_pending_count += 1
                logger.info(f"   ⏳ Ainda aguardando jogos finalizarem")
        
        logger.info(f"\n{'=' * 100}")
        logger.info("✅ VALIDAÇÃO CONCLUÍDA")
        logger.info(f"{'=' * 100}")
        logger.info(f"✔️  Apostas validadas: {validated_count}")
        logger.info(f"⏳ Ainda pendentes: {still_pending_count}")
        logger.info(f"{'=' * 100}\n")
        
        result = {
            'status': 'success',
            'task_id': self.request.id,
            'timestamp': timezone.now().isoformat(),
            'validated_count': validated_count,
            'pending_count': still_pending_count
        }
        
        # Atualizar registro de execução
        execution.bets_validated = validated_count
        execution.mark_finished(status='success', result_data=result)
        
        return result
        
    except Exception as e:
        logger.error(f"\n{'=' * 100}")
        logger.error("❌ ERRO NA VALIDAÇÃO")
        logger.error(f"{'=' * 100}")
        logger.error(f"Erro: {str(e)}", exc_info=True)
        logger.error(f"{'=' * 100}\n")
        
        # Atualizar registro de execução
        execution.mark_finished(status='failed', error_message=str(e))
        
        # Re-raise para Celery marcar como falha
        raise


@shared_task(bind=True, name='analysis.cleanup_old_daily_bets')
def cleanup_old_daily_bets(self):
    """
    Task para limpar apostas diárias antigas (opcional)
    
    Agenda sugerida: Semanal (domingo às 03:00 UTC)
    
    Remove apostas validadas com mais de 90 dias para manter banco limpo.
    Mantém estatísticas agregadas antes de deletar.
    """
    from apps.analysis.models import DailyBet
    from django.db.models import Count, Avg, Sum
    
    logger.info("=" * 100)
    logger.info("🧹 TASK: CLEANUP OLD DAILY BETS - INICIANDO")
    logger.info("=" * 100)
    
    try:
        cutoff_date = timezone.now().date() - timedelta(days=90)
        
        old_bets = DailyBet.objects.filter(
            date__lt=cutoff_date,
            is_validated=True
        )
        
        count = old_bets.count()
        
        if count == 0:
            logger.info("   ℹ️  Nenhuma aposta antiga para limpar")
            logger.info(f"{'=' * 100}\n")
            return {'status': 'success', 'deleted_count': 0}
        
        # Calcular estatísticas antes de deletar (opcional - salvar em modelo de stats)
        stats = old_bets.aggregate(
            total=Count('id'),
            won=Count('id', filter=models.Q(status='won')),
            avg_odd=Avg('total_odd'),
            avg_ev=Avg('expected_value')
        )
        
        logger.info(f"\n📊 Estatísticas das apostas a serem removidas:")
        logger.info(f"   Total: {stats['total']}")
        logger.info(f"   Ganhas: {stats['won']}")
        logger.info(f"   Odd média: {stats['avg_odd']:.2f}")
        logger.info(f"   EV médio: {stats['avg_ev']:.1f}%")
        
        # Deletar
        old_bets.delete()
        
        logger.info(f"\n✅ {count} apostas antigas removidas")
        logger.info(f"{'=' * 100}\n")
        
        return {
            'status': 'success',
            'deleted_count': count,
            'stats': stats
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no cleanup: {e}", exc_info=True)
        raise


@shared_task(bind=True, name='analysis.sync_match_results')
def sync_match_results(self, target_date=None, triggered_by='celery'):
    """
    Sincroniza status e placares oficiais de uma data.

    Agenda sugerida: 20:00, 22:00 e 23:45 (Africa/Maputo), para que a
    validação dos bilhetes tenha resultados frescos ao fim do dia.
    """
    from django.utils.dateparse import parse_date
    from apps.analysis.models import TaskExecution
    from .services.match_result_sync import sync_results_for_date

    target = parse_date(str(target_date)) if target_date else (timezone.localdate() - timedelta(days=1))
    if not target:
        target = timezone.localdate() - timedelta(days=1)

    execution = TaskExecution.objects.create(
        task_name='sync_match_results',
        task_id=self.request.id,
        triggered_by=triggered_by,
    )

    try:
        results = sync_results_for_date(target)
        finished = sum(1 for info in results.values() if info.get('status') == 'finished')

        result = {
            'status': 'success',
            'date': target.isoformat(),
            'fixtures': len(results),
            'finished': finished,
        }
        execution.mark_finished(status='success', result_data=result)

        logger.info(
            "sync_match_results %s: %s fixtures, %s finalizados",
            target,
            len(results),
            finished,
        )
        return result
    except Exception as exc:
        execution.mark_finished(status='failed', error_message=str(exc))
        raise


@shared_task(bind=True, name='analysis.precompute_match_previews')
def precompute_match_previews(self, max_matches=20):
    """Aquece o mesmo cache de preview consumido pela página de detalhes."""
    from rest_framework.test import APIRequestFactory
    from rest_framework.permissions import AllowAny
    from apps.matches.models import Match
    from apps.matches.views import MatchViewSet

    now = timezone.now()
    matches = list(
        Match.objects.filter(
            status='scheduled',
            api_football_id__isnull=False,
            match_date__gte=now,
            match_date__lt=now + timedelta(hours=36),
        )
        .select_related('league', 'home_team', 'away_team')
        .order_by('match_date')[:max_matches]
    )
    if not matches:
        return {'warmed': 0, 'failed': 0}

    factory = APIRequestFactory()
    preview_view = MatchViewSet.as_view(
        {'post': 'statistical_preview'}, permission_classes=[AllowAny],
    )
    warmed = 0
    failed = 0
    for match in matches:
        request = factory.post(
            '/api/matches/statistical_preview/',
            {
                'home_team': match.home_team.name,
                'away_team': match.away_team.name,
                'league': match.league.name,
                'date': match.match_date.isoformat(),
                'match_id': match.id,
                'api_football_id': match.api_football_id,
                'match_status': 'scheduled',
            },
            format='json',
        )
        try:
            response = preview_view(request)
            if response.status_code == 200:
                warmed += 1
            else:
                failed += 1
                logger.warning(
                    'Preview não pré-calculado para fixture %s: HTTP %s',
                    match.api_football_id,
                    response.status_code,
                )
        except Exception:
            failed += 1
            logger.exception('Falha ao pré-calcular fixture %s', match.api_football_id)

    result = {'warmed': warmed, 'failed': failed}
    logger.info('Pré-cálculo de previews concluído: %s', result)
    return result
