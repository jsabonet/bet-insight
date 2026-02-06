"""
Script de Teste: Configuração Celery e Geração de Bilhetes

COMO USAR:
1. Terminal 1 - Redis:
   docker run -d -p 6379:6379 redis:7-alpine

2. Terminal 2 - Celery Worker:
   cd backend
   celery -A config worker --loglevel=info --pool=solo

3. Terminal 3 - Este script:
   cd backend
   python test_celery_setup.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.tasks import generate_daily_bets
from apps.analysis.models import DailyBet
from apps.matches.models import Match
from django.utils import timezone
from datetime import timedelta


def test_celery_connection():
    """Testa conexão com Redis/Celery"""
    print("\n" + "="*80)
    print("🔍 TESTE 1: Conexão Celery/Redis")
    print("="*80)
    
    try:
        from celery import current_app
        
        # Tentar inspecionar workers ativos
        inspect = current_app.control.inspect()
        active_workers = inspect.active()
        
        if active_workers:
            print(f"✅ Workers ativos: {list(active_workers.keys())}")
            return True
        else:
            print("⚠️  Nenhum worker detectado. Certifique-se que worker está rodando:")
            print("   celery -A config worker --loglevel=info --pool=solo")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao conectar com Celery: {e}")
        return False


def test_matches_available():
    """Verifica se há partidas disponíveis para análise"""
    print("\n" + "="*80)
    print("⚽ TESTE 2: Partidas Disponíveis")
    print("="*80)
    
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    matches = Match.objects.filter(
        match_date__gte=timezone.now(),
        match_date__lt=timezone.now() + timedelta(days=1),
        status__in=['not_started', 'scheduled', 'NS', 'TBD']
    ).count()
    
    print(f"📅 Partidas do dia ({today}): {matches}")
    
    if matches > 0:
        print(f"✅ {matches} partidas disponíveis para geração de bilhetes")
        return True
    else:
        print("⚠️  Nenhuma partida encontrada para hoje")
        print("   Os bilhetes serão criados quando houver partidas agendadas")
        return False


def test_manual_generation():
    """Testa geração manual de bilhetes"""
    print("\n" + "="*80)
    print("🎯 TESTE 3: Geração Manual de Bilhetes")
    print("="*80)
    
    try:
        print("Executando generate_daily_bets() de forma síncrona...")
        
        # Contar bilhetes antes
        before_count = DailyBet.objects.filter(date=timezone.now().date()).count()
        print(f"📋 Bilhetes existentes antes: {before_count}")
        
        # Executar geração
        result = generate_daily_bets()
        
        # Contar bilhetes depois
        after_count = DailyBet.objects.filter(date=timezone.now().date()).count()
        print(f"📋 Bilhetes existentes depois: {after_count}")
        
        if after_count > before_count:
            print(f"✅ {after_count - before_count} novos bilhetes gerados!")
            
            # Listar bilhetes criados
            bets = DailyBet.objects.filter(date=timezone.now().date()).order_by('-id')[:5]
            print("\n📋 Bilhetes criados:")
            for bet in bets:
                print(f"   • {bet.get_bet_type_display()} | Odd: {bet.total_odd} | Prob: {bet.combined_probability*100:.1f}%")
            
            return True
        else:
            print("⚠️  Nenhum bilhete novo gerado (pode não haver partidas elegíveis)")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao gerar bilhetes: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_async_task():
    """Testa task assíncrona via Celery"""
    print("\n" + "="*80)
    print("🚀 TESTE 4: Task Assíncrona (Celery)")
    print("="*80)
    
    try:
        print("Disparando task assíncrona...")
        
        # Disparar task para execução em background
        task = generate_daily_bets.delay()
        
        print(f"✅ Task disparada com sucesso!")
        print(f"   Task ID: {task.id}")
        print(f"   Status: {task.status}")
        print("\nAguarde alguns segundos e verifique os logs do worker.")
        print("O worker deve processar a task e gerar os bilhetes.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao disparar task assíncrona: {e}")
        print("\nCertifique-se que:")
        print("1. Redis está rodando (docker run -d -p 6379:6379 redis:7-alpine)")
        print("2. Worker está rodando (celery -A config worker --loglevel=info --pool=solo)")
        return False


def test_beat_schedule():
    """Verifica configuração do Celery Beat"""
    print("\n" + "="*80)
    print("⏰ TESTE 5: Configuração Celery Beat")
    print("="*80)
    
    try:
        from celery import current_app
        
        schedule = current_app.conf.beat_schedule
        
        if 'generate-daily-bets' in schedule:
            task_config = schedule['generate-daily-bets']
            print(f"✅ Task 'generate-daily-bets' configurada:")
            print(f"   Schedule: {task_config['schedule']}")
            print(f"   Task: {task_config['task']}")
            
            if 'validate-daily-bets' in schedule:
                task_config = schedule['validate-daily-bets']
                print(f"\n✅ Task 'validate-daily-bets' configurada:")
                print(f"   Schedule: {task_config['schedule']}")
                
            return True
        else:
            print("❌ Task 'generate-daily-bets' não encontrada no beat_schedule")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar beat_schedule: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "TESTE DE CONFIGURAÇÃO CELERY" + " "*30 + "║")
    print("╚" + "="*78 + "╝")
    
    results = {
        'celery_connection': test_celery_connection(),
        'matches_available': test_matches_available(),
        'beat_schedule': test_beat_schedule(),
        'manual_generation': test_manual_generation(),
    }
    
    # Teste assíncrono apenas se conexão OK
    if results['celery_connection']:
        results['async_task'] = test_async_task()
    
    # Resumo
    print("\n" + "="*80)
    print("📊 RESUMO DOS TESTES")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print("\n" + "="*80)
    print(f"🎯 RESULTADO FINAL: {passed}/{total} testes passaram")
    print("="*80)
    
    if passed == total:
        print("\n✅ Sistema configurado corretamente!")
        print("   Bilhetes serão gerados automaticamente às 06:00 UTC diariamente.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique:")
        print("   1. Redis rodando: docker run -d -p 6379:6379 redis:7-alpine")
        print("   2. Worker rodando: celery -A config worker --loglevel=info --pool=solo")
        print("   3. Partidas agendadas no banco de dados")
    
    print("\n")


if __name__ == "__main__":
    main()
