import requests
from datetime import datetime

API_KEY = '96f5a59919eb0648a28a5bcd06d5d98e'
BASE_URL = 'https://v3.football.api-sports.io'

headers = {'x-apisports-key': API_KEY}
today = datetime.now().strftime('%Y-%m-%d')

print(f"\n🔍 Buscando TODAS as partidas de {today}...\n")

# Buscar SEM filtro de liga (sem season)
response = requests.get(
    f'{BASE_URL}/fixtures',
    headers=headers,
    params={'date': today},
    timeout=15
)

data = response.json()
fixtures = data.get('response', [])

print(f"✅ Total de partidas encontradas: {len(fixtures)}\n")

if fixtures:
    print("Primeiras 15 partidas:")
    print("-" * 80)
    for i, fixture in enumerate(fixtures[:15], 1):
        teams = fixture.get('teams', {})
        league = fixture.get('league', {})
        home = teams.get('home', {}).get('name', 'N/A')
        away = teams.get('away', {}).get('name', 'N/A')
        league_name = league.get('name', 'N/A')
        league_id = league.get('id', 'N/A')
        
        print(f"{i:2}. {home} vs {away}")
        print(f"    Liga: {league_name} (ID: {league_id})")
