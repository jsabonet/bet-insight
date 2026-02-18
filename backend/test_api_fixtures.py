import requests
from datetime import datetime, timedelta

API_KEY = '96f5a59919eb0648a28a5bcd06d5d98e'
BASE_URL = 'https://v3.football.api-sports.io'

headers = {'x-apisports-key': API_KEY}

print("\n" + "=" * 80)
print("🔍 TESTE DE BUSCA DE PARTIDAS - Diferentes Métodos")
print("=" * 80 + "\n")

# Teste 1: Buscar por timezone (hoje local)
print("TESTE 1: Buscar com timezone=Europe/Lisbon")
response1 = requests.get(
    f'{BASE_URL}/fixtures',
    headers=headers,
    params={'date': datetime.now().strftime('%Y-%m-%d'), 'timezone': 'Europe/Lisbon'},
    timeout=15
)
data1 = response1.json()
print(f"Resultado: {len(data1.get('response', []))} partidas\n")

# Teste 2: Buscar sem season
print("TESTE 2: Buscar apenas com date (sem season)")
response2 = requests.get(
    f'{BASE_URL}/fixtures',
    headers=headers,
    params={'date': datetime.now().strftime('%Y-%m-%d')},
    timeout=15
)
data2 = response2.json()
print(f"Resultado: {len(data2.get('response', []))} partidas\n")

# Teste 3: Buscar fixtures live
print("TESTE 3: Buscar partidas ao vivo")
response3 = requests.get(
    f'{BASE_URL}/fixtures',
    headers=headers,
    params={'live': 'all'},
    timeout=15
)
data3 = response3.json()
print(f"Resultado: {len(data3.get('response', []))} partidas ao vivo\n")

# Teste 4: Verificar status da API
print("TESTE 4: Status da API")
print(f"Errors no response: {data2.get('errors', {})}")
print(f"Results: {data2.get('results', 0)}")

# Teste 5: Listar próximas N fixtures
print("\nTESTE 5: Buscar próximas fixtures (next=50)")
response5 = requests.get(
    f'{BASE_URL}/fixtures',
    headers=headers,
    params={'next': 50},
    timeout=15
)
data5 = response5.json()
fixtures_next = data5.get('response', [])
print(f"Resultado: {len(fixtures_next)} próximas partidas\n")

if fixtures_next:
    print("Primeiras 10 partidas encontradas:")
    print("-" * 80)
    for i, fixture in enumerate(fixtures_next[:10], 1):
        teams = fixture.get('teams', {})
        league = fixture.get('league', {})
        fixture_data = fixture.get('fixture', {})
        home = teams.get('home', {}).get('name', 'N/A')
        away = teams.get('away', {}).get('name', 'N/A')
        league_name = league.get('name', 'N/A')
        match_date = fixture_data.get('date', '')
        
        print(f"{i:2}. {home} vs {away}")
        print(f"    Liga: {league_name} | Data: {match_date[:16]}")
