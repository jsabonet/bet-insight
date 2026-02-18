"""
Script de teste para o sistema HÍBRIDO de geração de bilhetes
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.daily_bet_generator import DailyBetGenerator
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(asctime)s %(name)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

print("\n" + "=" * 100)
print("🧪 TESTE DO SISTEMA HÍBRIDO DE GERAÇÃO DE BILHETES")
print("=" * 100 + "\n")

generator = DailyBetGenerator()

# Testar modo hybrid (padrão)
mode = 'hybrid'

print("=" * 100)
print(f"🔬 TESTANDO MODO: {mode.upper()}")
print("=" * 100 + "\n")

try:
    results = generator.generate_for_today(days_ahead=1, mode=mode)
    
    print("\n" + "─" * 100)
    print(f"📊 RESULTADOS - MODO {mode.upper()}")
    print("─" * 100)
    print(f"🔍 Modo de busca: {results.get('search_mode', 'N/A')}")
    print(f"📡 Total de fixtures encontradas: {results.get('total_fixtures_found', 0)}")
    print(f"📋 Partidas agendadas: {results.get('scheduled_fixtures', 0)}")
    print(f"⚽ Partidas analisadas: {results.get('matches_analyzed', 0)}")
    print(f"🎯 Bilhetes múltiplos criados: {results.get('multiple_count', 0)}")
    print(f"⚡ Value bets criadas: {results.get('value_count', 0)}")
    print(f"📊 Total de apostas: {results.get('total_bets', 0)}")
    print(f"🌐 API calls: {results.get('api_calls', 0)}")
    print("─" * 100)
    
except Exception as e:
    print(f"\n❌ ERRO NO TESTE ({mode}): {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 100)
print("✅ TESTE CONCLUÍDO")
print("=" * 100 + "\n")
