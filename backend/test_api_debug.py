import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from datetime import datetime

print("=" * 80)
print("🔍 TESTANDO CONEXÃO COM API-FOOTBALL")
print("=" * 80)

api = FootballAPIService()

print(f"✅ API Key: {api.api_key[:20]}...")
print(f"✅ URL: {api.base_url}")
print()

# Teste 1: Buscar próximas partidas da Premier League
print("📋 Teste 1: Próximas partidas da Premier League (ID: 39)")
print("-" * 80)
result = api.get_fixtures_by_league(39, next_matches=10)
print(f"Sucesso: {result['success']}")
print(f"Total: {result['count']}")
if result['count'] > 0:
    print("\nPrimeiras 3 partidas:")
    for i, fix in enumerate(result['fixtures'][:3], 1):
        home = fix['teams']['home']['name']
        away = fix['teams']['away']['name']
        date = fix['fixture']['date']
        print(f"  {i}. {home} vs {away} - {date}")
else:
    print(f"Erro ou sem dados: {result.get('error', 'Nenhuma partida encontrada')}")

print()

# Teste 2: Buscar partidas ao vivo
print("📋 Teste 2: Partidas AO VIVO agora")
print("-" * 80)
result = api.get_live_fixtures()
print(f"Sucesso: {result['success']}")
print(f"Total: {result['count']}")
if result['count'] > 0:
    print("\nPartidas ao vivo:")
    for i, fix in enumerate(result['fixtures'][:5], 1):
        home = fix['teams']['home']['name']
        away = fix['teams']['away']['name']
        league = fix['league']['name']
        print(f"  {i}. {home} vs {away} ({league})")
else:
    print("Nenhuma partida ao vivo no momento")

print()

# Teste 3: Buscar por data específica (hoje)
print("📋 Teste 3: Partidas de HOJE")
print("-" * 80)
today = datetime.now().strftime('%Y-%m-%d')
result = api.get_fixtures_by_date(today)
print(f"Data: {today}")
print(f"Sucesso: {result['success']}")
print(f"Total: {result['count']}")
if result['count'] > 0:
    print("\nPrimeiras 5 partidas de hoje:")
    for i, fix in enumerate(result['fixtures'][:5], 1):
        home = fix['teams']['home']['name']
        away = fix['teams']['away']['name']
        league = fix['league']['name']
        print(f"  {i}. {home} vs {away} ({league})")
else:
    print("Nenhuma partida hoje")

print()

# Teste 4: Teste com season=2024 para Premier League
print("📋 Teste 4: Premier League Season 2024")
print("-" * 80)
result = api.get_fixtures_by_league(39, season=2024, next_matches=10)
print(f"Sucesso: {result['success']}")
print(f"Total: {result['count']}")
if result['count'] > 0:
    print("\nPrimeiras 3 partidas:")
    for i, fix in enumerate(result['fixtures'][:3], 1):
        home = fix['teams']['home']['name']
        away = fix['teams']['away']['name']
        date = fix['fixture']['date']
        print(f"  {i}. {home} vs {away} - {date}")
else:
    print(f"Erro ou sem dados: {result.get('error', 'Nenhuma partida encontrada')}")

print()
print("=" * 80)
print("✅ Testes concluídos!")
print("=" * 80)
