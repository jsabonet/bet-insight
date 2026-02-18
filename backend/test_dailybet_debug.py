"""
Teste de debug do DailyBetGenerator
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

print("=" * 80)
print("DEBUG: DailyBetGenerator")
print("=" * 80)
print()

generator = DailyBetGenerator()

# Teste 1: Ver quantas partidas a API retorna
from django.utils import timezone
today = timezone.now().date()
today_str = today.strftime('%Y-%m-%d')

print(f"Data de hoje: {today_str}")
print()

print("=" * 80)
print("TESTE 1: Buscar fixtures da API")
print("=" * 80)

# Testar apenas 3 ligas primeiro
test_leagues = [39, 140, 61]  # Premier League, La Liga, Ligue 1

for league_id in test_leagues:
    try:
        response = generator.api.get_fixtures_by_date(today_str, league_id=league_id, season=2026)
        if response and response.get('response'):
            fixtures = response['response']
            scheduled = [f for f in fixtures if f.get('fixture', {}).get('status', {}).get('short') in ['NS', 'TBD', 'PST']]
            print(f"Liga {league_id}: {len(fixtures)} total, {len(scheduled)} agendadas")
            
            # Mostrar primeiras 3 partidas
            for idx, f in enumerate(scheduled[:3], 1):
                teams = f.get('teams', {})
                home = teams.get('home', {}).get('name', 'Unknown')
                away = teams.get('away', {}).get('name', 'Unknown')
                print(f"  {idx}. {home} vs {away}")
        else:
            print(f"Liga {league_id}: Nenhuma partida encontrada")
    except Exception as e:
        print(f"Liga {league_id}: ERRO - {e}")
    print()

print()
print("=" * 80)
print("TESTE 2: Executar generate_for_today() buscando próximos 3 dias")
print("=" * 80)
print()

# Executar geração completa (próximos 3 dias)
results = generator.generate_for_today(days_ahead=3)

print()
print("=" * 80)
print("RESULTADO:")
print("=" * 80)
print(f"Partidas analisadas: {results.get('matches_analyzed', 0)}")
print(f"Múltiplos gerados: {results.get('multiple_count', 0)}")
print(f"Value bets geradas: {results.get('value_count', 0)}")
print(f"Total de apostas: {results.get('total_bets', 0)}")
print()
