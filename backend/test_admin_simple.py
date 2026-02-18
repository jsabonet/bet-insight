import os
import sys
import django
import logging
from datetime import datetime
import uuid

# Configurar path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Silenciar todos os logs exceto erros críticos
logging.basicConfig(level=logging.ERROR)
for logger_name in ['analysis_orchestrator', 'decision_engine', 'match_enricher', 
                     'api_football_service', 'ai_analyzer', 'daily_bet_generator']:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

django.setup()

from django.contrib.auth import get_user_model
from apps.analysis.models import TaskExecution
from apps.analysis.services.daily_bet_generator import DailyBetGenerator

User = get_user_model()

print("=" * 70)
print("TESTE ADMIN: GERACAO DE DAILY BETS")
print("=" * 70)
print()

# 1. Encontrar usuário admin
admin = User.objects.filter(is_staff=True).first()
if not admin:
    print("[ERRO] Nenhum usuário admin encontrado!")
    sys.exit(1)

print(f"[OK] Admin encontrado: {admin.username}")
print()

# 2. Criar registro de execução
task_id = str(uuid.uuid4())
execution = TaskExecution.objects.create(
    task_name='generate_daily_bets',
    task_id=task_id,
    triggered_by='admin_manual',
    triggered_by_user=admin
)
print(f"[OK] TaskExecution criado (ID: {execution.id})")
print()

# 3. Executar geração
print("[EXECUTANDO] DailyBetGenerator().generate_for_today()...")
print("             (Isso pode levar 1-2 minutos...)")
print()

try:
    generator = DailyBetGenerator()
    results = generator.generate_for_today()
    
    # 4. Atualizar execução
    result_data = {
        'multiple_count': results.get('multiple_count', 0),
        'value_count': results.get('value_count', 0),
        'matches_analyzed': results.get('matches_analyzed', 0),
        'total_bets': results.get('total_bets', 0)
    }
    
    execution.mark_finished(status='success', result_data=result_data)
    
    # 5. Mostrar resultado
    print()
    print("=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    print()
    print(f"[OK] Status: SUCCESS")
    print(f"[MULTIPLOS] {results.get('multiple_count', 0)} gerados")
    print(f"[VALUE BETS] {results.get('value_count', 0)} geradas")
    print(f"[PARTIDAS] {results.get('matches_analyzed', 0)} analisadas")
    print(f"[TOTAL] {results.get('total_bets', 0)} apostas")
    print()
    print(f"[TASK ID] {task_id}")
    print(f"[EXECUTION ID] {execution.id}")
    print()
    
    # Simular resposta HTTP
    print("=" * 70)
    print("RESPOSTA HTTP SIMULADA (200 OK)")
    print("=" * 70)
    print()
    print(f"""{{
    "status": "success",
    "task_id": "{task_id}",
    "execution_id": {execution.id},
    "message": "[OK] Daily Bets gerados! {results.get('multiple_count', 0)} multiplos, {results.get('value_count', 0)} value bets",
    "results": {{
        "multiple_count": {results.get('multiple_count', 0)},
        "value_count": {results.get('value_count', 0)},
        "matches_analyzed": {results.get('matches_analyzed', 0)},
        "total_bets": {results.get('total_bets', 0)}
    }}
}}""")
    print()
    
except Exception as e:
    # Marcar como falha
    execution.mark_finished(status='failed', result_data={'error': str(e)})
    
    print()
    print("=" * 70)
    print("[ERRO] ERRO NA EXECUCAO")
    print("=" * 70)
    print()
    print(f"Erro: {str(e)}")
    print()
    print(f"[TASK ID] {task_id}")
    print(f"[EXECUTION ID] {execution.id}")
    print()
    raise

print("=" * 70)
print("TESTE CONCLUÍDO")
print("=" * 70)
