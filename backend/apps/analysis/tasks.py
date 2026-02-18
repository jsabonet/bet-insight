"""
Celery Tasks para Geração e Validação de Bilhetes Diários

Tasks:
1. generate_daily_bets: Gera bilhetes e value bets automaticamente (diário às 06:00 UTC)
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
    Task executada diariamente para gerar bilhetes e value bets automáticos
    
    Agenda sugerida: 06:00 UTC (horário com poucas requisições de usuários)
    
    Esta task:
    - Analisa todas as partidas do dia
    - Gera bilhetes múltiplos (3x, 5x, 7x)
    - Gera value bets individuais
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
        
        logger.info(f"\n{'=' * 100}")
        logger.info("✅ TASK CONCLUÍDA COM SUCESSO")
        logger.info(f"{'=' * 100}")
        logger.info(f"📋 Bilhetes múltiplos: {results['multiple_count']}")
        logger.info(f"⚡ Value bets: {results['value_count']}")
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
        
        for bet in pending_bets:
            logger.info(f"\n{'─' * 80}")
            logger.info(f"Validando: {bet}")
            logger.info(f"   Data: {bet.date.strftime('%d/%m/%Y')}")
            logger.info(f"   Tipo: {bet.get_bet_type_display()}")
            logger.info(f"   Seleções: {len(bet.selections)}")
            
            # Tentar validar
            was_validated = bet.validate_result()
            
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
