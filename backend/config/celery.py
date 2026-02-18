"""
Configuração do Celery para BetInsight

Este arquivo configura o Celery para execução de tasks assíncronas:
- Geração automática de bilhetes diários
- Validação de resultados
- Outras tasks em background
"""

import os
import logging
from celery import Celery
from celery.schedules import crontab

# Suprimir logs de erro de conexão Redis (modo degradado)
logging.getLogger('celery').setLevel(logging.CRITICAL)
logging.getLogger('kombu').setLevel(logging.CRITICAL)
logging.getLogger('redis').setLevel(logging.CRITICAL)

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Criar app Celery
app = Celery('betinsight')

# Carregar configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descobrir tasks em todos os apps instalados
app.autodiscover_tasks()

# Configurar schedule para tasks periódicas (Celery Beat)
app.conf.beat_schedule = {
    # Gerar bilhetes diários - 06:00 UTC (09:00 Maputo) todos os dias
    'generate-daily-bets': {
        'task': 'analysis.generate_daily_bets',
        'schedule': crontab(hour=6, minute=0),  # 06:00 UTC
        'options': {
            'expires': 3600,  # Expirar após 1h se não executar
        }
    },
    
    # Validar apostas pendentes - A cada 1 hora
    'validate-daily-bets': {
        'task': 'analysis.validate_daily_bets',
        'schedule': crontab(minute=0),  # A cada hora em ponto
        'options': {
            'expires': 1800,  # Expirar após 30min
        }
    },
    
    # Limpar apostas antigas - Domingo às 03:00 UTC (semanal)
    'cleanup-old-daily-bets': {
        'task': 'analysis.cleanup_old_daily_bets',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Domingo 03:00
        'options': {
            'expires': 7200,  # Expirar após 2h
        }
    },
}

# Configurações adicionais
app.conf.update(
    task_track_started=True,  # Rastrear quando task inicia
    task_time_limit=30 * 60,  # Timeout de 30 minutos por task
    task_soft_time_limit=25 * 60,  # Soft timeout de 25 minutos
    worker_prefetch_multiplier=1,  # Processar 1 task por vez
    worker_max_tasks_per_child=50,  # Reiniciar worker após 50 tasks
)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Task de debug para testar Celery"""
    print(f'Request: {self.request!r}')
