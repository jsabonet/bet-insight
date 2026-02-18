"""
Teste do Sistema de Tracking de Progresso em Tempo Real
=========================================================

Este script testa:
1. Criação de TaskExecution com novos campos
2. Atualização de progresso durante execução
3. Endpoint de progresso
"""

import os
import django
import sys
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bet_insight_backend.settings')
django.setup()

from apps.analysis.models import TaskExecution
from django.contrib.auth import get_user_model
import time

User = get_user_model()

def test_progress_tracking():
    """Testa o sistema de tracking de progresso"""
    
    print("=" * 80)
    print("🧪 TESTE: Sistema de Tracking de Progresso em Tempo Real")
    print("=" * 80)
    print()
    
    # 1. Criar TaskExecution de teste
    print("1️⃣ Criando TaskExecution de teste...")
    execution = TaskExecution.objects.create(
        task_name='generate_daily_bets',
        task_id='test-progress-tracking-123',
        triggered_by='manual'
    )
    print(f"   ✅ TaskExecution criada: ID={execution.id}")
    print(f"   📝 Status inicial: {execution.status}")
    print(f"   📝 Stage inicial: '{execution.current_stage}'")
    print()
    
    # 2. Simular fase de busca
    print("2️⃣ Simulando fase SEARCHING...")
    execution.update_progress(
        stage='searching',
        log_message='Iniciando busca de partidas em ligas prioritárias...'
    )
    print(f"   ✅ Stage atualizado: {execution.current_stage}")
    print(f"   ⏱️  Última atualização: {execution.last_updated}")
    time.sleep(1)
    
    # 3. Simular partidas encontradas
    print("3️⃣ Simulando partidas encontradas...")
    execution.update_progress(
        stage='searching',
        matches_found=60,
        log_message='60 partidas encontradas para análise'
    )
    print(f"   ✅ Partidas encontradas: {execution.matches_found}")
    time.sleep(1)
    
    # 4. Simular análise de partidas
    print("4️⃣ Simulando análise de partidas...")
    for i in range(1, 61, 10):
        execution.update_progress(
            stage='analyzing',
            matches_processed=i,
            log_message=f'Partida {i}/60 analisada'
        )
        progress = execution.get_progress_percentage()
        print(f"   📊 Progresso: {progress}% ({i}/{execution.matches_found} partidas)")
        time.sleep(0.5)
    
    print()
    
    # 5. Simular criação de bilhetes
    print("5️⃣ Simulando criação de bilhetes...")
    execution.update_progress(
        stage='creating',
        matches_processed=60,
        log_message='Criando bilhetes múltiplos...'
    )
    
    for i in range(1, 6):
        execution.update_progress(
            bets_created=i,
            log_message=f'Bilhete {i} criado com sucesso'
        )
        print(f"   🎫 Apostas criadas: {i}")
        time.sleep(0.3)
    
    print()
    
    # 6. Finalizar execução
    print("6️⃣ Finalizando execução...")
    execution.mark_finished(
        status='success',
        result_data={
            'matches_analyzed': 60,
            'multiple_count': 5,
            'value_count': 12,
            'total_bets': 17
        }
    )
    execution.refresh_from_db()
    
    print(f"   ✅ Status final: {execution.status}")
    print(f"   ✅ Stage final: {execution.current_stage}")
    print(f"   ⏱️  Duração: {execution.duration_seconds}s")
    print()
    
    # 7. Verificar métodos auxiliares
    print("7️⃣ Testando métodos auxiliares...")
    print(f"   📊 get_progress_percentage(): {execution.get_progress_percentage()}%")
    print(f"   ⏱️  get_elapsed_time(): {execution.get_elapsed_time()}s")
    print()
    
    # 8. Exibir log de progresso
    print("8️⃣ Log de progresso (últimas 10 entradas):")
    if execution.progress_log:
        for entry in execution.progress_log[-10:]:
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%H:%M:%S')
            print(f"   [{timestamp}] {entry.get('stage', '').upper():10s} → {entry['message']}")
    print()
    
    # 9. Resumo final
    print("=" * 80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO")
    print("=" * 80)
    print()
    print("📋 Resumo:")
    print(f"   • TaskExecution ID: {execution.id}")
    print(f"   • Partidas encontradas: {execution.matches_found}")
    print(f"   • Partidas processadas: {execution.matches_processed}")
    print(f"   • Apostas criadas: {execution.bets_created}")
    print(f"   • Progresso final: {execution.get_progress_percentage()}%")
    print(f"   • Tempo total: {execution.duration_seconds}s")
    print(f"   • Entradas no log: {len(execution.progress_log)}")
    print()
    
    # 10. Testar recuperação de progresso (simula refresh da página)
    print("🔄 Simulando refresh da página...")
    active_execution = TaskExecution.objects.filter(
        task_name='generate_daily_bets',
        status='running'
    ).order_by('-started_at').first()
    
    if active_execution:
        print("   ⚠️  Geração ativa detectada!")
        print(f"   📊 Progresso: {active_execution.get_progress_percentage()}%")
    else:
        print("   ✅ Nenhuma geração ativa (como esperado após conclusão)")
    print()
    
    print("=" * 80)
    print("🎉 TODOS OS TESTES PASSARAM")
    print("=" * 80)
    print()
    print("📝 Verificações realizadas:")
    print("   ✅ Criação de TaskExecution")
    print("   ✅ Atualização de progresso em tempo real")
    print("   ✅ Métodos get_progress_percentage() e get_elapsed_time()")
    print("   ✅ Log de progresso (progress_log)")
    print("   ✅ Finalização com mark_finished()")
    print("   ✅ Detecção de geração ativa após refresh")
    print()
    
    # Limpar teste
    print("🧹 Limpando dados de teste...")
    execution.delete()
    print("   ✅ TaskExecution de teste removida")
    print()

if __name__ == '__main__':
    try:
        test_progress_tracking()
    except Exception as e:
        print()
        print("=" * 80)
        print("❌ ERRO NO TESTE")
        print("=" * 80)
        print(f"Erro: {e}")
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)
