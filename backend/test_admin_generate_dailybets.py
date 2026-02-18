"""
Script para testar a geração de Daily Bets via admin
Simula a requisição POST /api/daily-bets/admin/generate-now/
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.analysis.services.daily_bet_generator import DailyBetGenerator
from apps.analysis.models import TaskExecution
from django.utils import timezone
import uuid

print("=" * 80)
print("🎯 TESTE: GERAÇÃO DE DAILY BETS VIA ADMIN")
print("=" * 80)

# Verificar se existe admin
User = get_user_model()
admin = User.objects.filter(is_staff=True).first()

if not admin:
    print("❌ Nenhum usuário admin encontrado!")
    print("Crie um admin com: python manage.py createsuperuser")
    sys.exit(1)

print(f"✅ Admin encontrado: {admin.email}\n")

# Simular o endpoint admin_generate_now
print("-" * 80)
print("📡 SIMULANDO POST /api/daily-bets/admin/generate-now/")
print("-" * 80)

try:
    # Criar ID único para esta execução
    task_id = str(uuid.uuid4())
    print(f"Task ID: {task_id}")
    
    # Criar registro de execução
    print("\n1️⃣ Criando registro TaskExecution...")
    execution = TaskExecution.objects.create(
        task_name='generate_daily_bets',
        task_id=task_id,
        triggered_by='admin_manual',
        triggered_by_user=admin
    )
    print(f"   ✅ Execution ID: {execution.id}")
    
    # Executar geração
    print("\n2️⃣ Executando DailyBetGenerator.generate_for_today()...")
    print("-" * 80)
    
    generator = DailyBetGenerator()
    results = generator.generate_for_today()
    
    print("-" * 80)
    print("\n3️⃣ Resultados da geração:")
    print(f"   📋 Bilhetes múltiplos: {results['multiple_count']}")
    print(f"   ⚡ Value bets: {results['value_count']}")
    print(f"   ⚽ Partidas analisadas: {results['matches_analyzed']}")
    print(f"   🔌 API calls: {results.get('api_calls', 'N/A')}")
    
    # Atualizar registro de execução
    print("\n4️⃣ Atualizando TaskExecution...")
    result_data = {
        'status': 'success',
        'task_id': task_id,
        'timestamp': timezone.now().isoformat(),
        'results': results
    }
    execution.mark_finished(status='success', result_data=result_data)
    print("   ✅ TaskExecution marcada como success")
    
    # Simular resposta do endpoint
    print("\n" + "=" * 80)
    print("📤 RESPOSTA DO ENDPOINT (simulada):")
    print("=" * 80)
    print(f"""{{
    "status": "success",
    "task_id": "{task_id}",
    "execution_id": {execution.id},
    "message": "✅ Daily Bets gerados! {results['multiple_count']} múltiplos, {results['value_count']} value bets",
    "results": {{
        "multiple_count": {results['multiple_count']},
        "value_count": {results['value_count']},
        "matches_analyzed": {results['matches_analyzed']}
    }}
}}""")
    
    print("\n" + "=" * 80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 80)
    
except Exception as e:
    print("\n" + "=" * 80)
    print("❌ ERRO DURANTE EXECUÇÃO:")
    print("=" * 80)
    print(f"Erro: {str(e)}")
    import traceback
    traceback.print_exc()
    
    # Se houver erro, marcar execução como falha
    if 'execution' in locals():
        execution.mark_finished(status='failed', error_message=str(e))
        print(f"\n⚠️ TaskExecution ID {execution.id} marcada como failed")
    
    sys.exit(1)
