import requests
import json

API_KEY = "e80d6c82ac7c1d03170757f605d83531"
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    'x-apisports-key': API_KEY
}

print("=" * 80)
print("🔍 TESTE DIRETO COM A API-FOOTBALL")
print("=" * 80)

# Teste 1: Status da API
print("\n📋 Teste 1: Status da conta")
print("-" * 80)
response = requests.get(f"{BASE_URL}/status", headers=headers, timeout=10)
print(f"Status Code: {response.status_code}")
data = response.json()
print(json.dumps(data, indent=2))

# Teste 2: Buscar partidas da Premier League
print("\n📋 Teste 2: Próximas partidas Premier League (season=2024)")
print("-" * 80)
response = requests.get(
    f"{BASE_URL}/fixtures",
    headers=headers,
    params={'league': 39, 'season': 2024},
    timeout=10
)
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Total de partidas: {len(data.get('response', []))}")
print(f"Erros: {data.get('errors', 'Nenhum')}")
if data.get('response'):
    print(f"Primeira partida: {data['response'][0]['teams']['home']['name']} vs {data['response'][0]['teams']['away']['name']}")

# Teste 3: Partidas de hoje
print("\n📋 Teste 3: Partidas de hoje (2025-12-29)")
print("-" * 80)
response = requests.get(
    f"{BASE_URL}/fixtures",
    headers=headers,
    params={'date': '2025-12-29'},
    timeout=10
)
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Total de partidas: {len(data.get('response', []))}")

# Teste 4: Buscar com last (últimas partidas)
print("\n📋 Teste 4: Últimas 10 partidas da Premier League")
print("-" * 80)
response = requests.get(
    f"{BASE_URL}/fixtures",
    headers=headers,
    params={'league': 39, 'season': 2024, 'last': 10},
    timeout=10
)
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"Total de partidas: {len(data.get('response', []))}")
print(f"Erros: {data.get('errors', 'Nenhum')}")
if data.get('response'):
    print("\nÚltimas partidas:")
    for i, fix in enumerate(data['response'][:5], 1):
        home = fix['teams']['home']['name']
        away = fix['teams']['away']['name']
        date = fix['fixture']['date'][:10]
        print(f"  {i}. {home} vs {away} - {date}")

print("\n" + "=" * 80)
