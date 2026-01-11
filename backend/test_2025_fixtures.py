"""
Testar busca de partidas com season 2025
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

print("\n" + "="*80)
print("TESTE: Buscar partidas da temporada 2025")
print("="*80)

football_api = FootballAPIService()

# Testar ligas com season 2025
major_leagues = {
    'Premier League': 39,
    'La Liga': 140,
    'Serie A': 135,
    'Bundesliga': 78,
    'Ligue 1': 61
}

print("\n1. Buscando partidas da temporada 2025:")
for league_name, league_id in major_leagues.items():
    result = football_api.get_fixtures_by_league(
        league_id, 
        season=2025,
        next_matches=50
    )
    
    count = result.get('count', 0) if result['success'] else 0
    print(f"   {league_name}: {count} partidas")
    
    if count > 0 and result.get('fixtures'):
        # Mostrar primeiras 3
        print(f"      Exemplos:")
        for i, fixture in enumerate(result['fixtures'][:3], 1):
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            date = fixture['fixture']['date'][:10]
            status = fixture['fixture']['status']['short']
            print(f"      {i}. {home} vs {away} - {date} ({status})")

# Testar com range de datas de 2025
print("\n2. Buscando partidas entre 2025-08-01 e 2025-12-31:")
result = football_api.get_fixtures_by_league(
    39,  # Premier League
    from_date='2025-08-01',
    to_date='2025-12-31'
)

count = result.get('count', 0) if result['success'] else 0
print(f"   Premier League (2025): {count} partidas")

if count > 0:
    # Contar por status
    fixtures = result.get('fixtures', [])
    status_count = {}
    for f in fixtures:
        status = f['fixture']['status']['short']
        status_count[status] = status_count.get(status, 0) + 1
    
    print(f"\n   Por status:")
    for status, cnt in sorted(status_count.items()):
        print(f"      {status}: {cnt} partidas")

print("\n" + "="*80)
