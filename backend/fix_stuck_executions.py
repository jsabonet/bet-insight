"""
Script para limpar execuções travadas de TaskExecution
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.analysis.models import TaskExecution
from django.utils import timezone

print("\n" + "="*80)
print("🔧 LIMPEZA DE EXECUÇÕES TRAVADAS")
print("="*80 + "\n")

# Buscar execuções com status 'running'
stuck_executions = TaskExecution.objects.filter(status='running')

print(f"📊 Execuções travadas encontradas: {stuck_executions.count()}\n")

if stuck_executions.count() == 0:
    print("✅ Nenhuma execução travada! Sistema está limpo.\n")
    sys.exit(0)

for execution in stuck_executions:
    print(f"\n{'─'*80}")
    print(f"ID: {execution.id}")
    print(f"Task: {execution.get_task_name_display()}")
    print(f"Iniciado: {execution.started_at.strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Tempo decorrido: {execution.get_elapsed_time()} segundos")
    print(f"Stage: {execution.current_stage or 'N/A'}")
    print(f"Partidas: {execution.matches_processed}/{execution.matches_found}")
    
    # Marcar como falhada se passou mais de 30 minutos
    elapsed = execution.get_elapsed_time()
    if elapsed > 1800:  # 30 minutos
        print(f"\n⚠️  TIMEOUT: Execução travada há {elapsed//60} minutos")
        execution.mark_finished(
            status='failed',
            error_message='Timeout: Execução não finalizou em tempo hábil (limpeza automática)'
        )
        print("✅ Marcada como FAILED")
    else:
        print(f"\n⏳ Ainda dentro do tempo limite ({elapsed//60} minutos)")

print(f"\n{'='*80}")
print("✅ LIMPEZA CONCLUÍDA")
print("="*80 + "\n")
