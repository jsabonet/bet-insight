"""
Teste detalhado de geração de Daily Bets
"""
import os
import sys
import django
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Configurar logging para ver tudo
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(name)s %(message)s'
)

django.setup()

from apps.analysis.services.daily_bet_generator import DailyBetGenerator
from django.utils import timezone

print("=" * 80)
print("TESTE DETALHADO: GERAÇÃO DE DAILY BETS")
print("=" * 80)
print()

today = timezone.now().date()
print(f"Data: {today.strftime('%Y-%m-%d')}")
print()

# Testar busca de fixtures primeiro
from apps.analysis.services.api_football_service import APIFootballService

api = APIFootballService()
today_str = today.strftime('%Y-%m-%d')

print("Testando busca de fixtures para hoje...")
print()

# Testar algumas ligas
test_leagues = [39, 140, 135, 78, 61]  # Premier, La Liga, Serie A, Bundesliga, Ligue 1

for league_id in test_leagues:
    try:
        response = api.get_fixtures_by_date(today_str, league_id=league_id, season=2026)
        if response and response.get('response'):
            fixtures = response['response']
            print(f"Liga {league_id}: {len(fixtures)} fixtures encontradas")
            
            # Mostrar status das fixtures
            for f in fixtures[:3]:  # Primeiras 3
                status = f.get('fixture', {}).get('status', {})
                teams = f.get('teams', {})
                print(f"  - {teams.get('home', {}).get('name')} vs {teams.get('away', {}).get('name')}")
                print(f"    Status: {status.get('short')} ({status.get('long')})")
        else:
            print(f"Liga {league_id}: Nenhuma fixture encontrada")
    except Exception as e:
        print(f"Liga {league_id}: ERRO - {e}")
    print()

print()
print("=" * 80)
print("INICIANDO GERAÇÃO COMPLETA")
print("=" * 80)
print()

try:
    generator = DailyBetGenerator()
    results = generator.generate_for_today()
    
    print()
    print("=" * 80)
    print("RESULTADO")
    print("=" * 80)
    print(f"Partidas analisadas: {results.get('matches_analyzed', 0)}")
    print(f"Múltiplos gerados: {results.get('multiple_count', 0)}")
    print(f"Value bets geradas: {results.get('value_count', 0)}")
    print(f"Total de apostas: {results.get('total_bets', 0)}")
    print()
    
except Exception as e:
    print(f"ERRO: {e}")
    import traceback
    traceback.print_exc()
