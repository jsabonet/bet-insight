"""
Diagnóstico: Por que não há partidas reais?
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from datetime import datetime, timedelta

print("\n" + "="*80)
print("DIAGNOSTICO: Partidas Reais")
print("="*80)

football_api = FootballAPIService()

# Testar API Key
print(f"\n1. API KEY configurada: {'Sim' if football_api.api_key else 'Nao'}")
if football_api.api_key:
    print(f"   Key: {football_api.api_key[:20]}...")

# Testar conexão com API
print(f"\n2. Testando conexao com API-Football...")

# Buscar partidas de hoje
today = datetime.now().strftime('%Y-%m-%d')
result = football_api.get_fixtures_by_date(today)

print(f"\n3. Partidas para hoje ({today}):")
print(f"   Sucesso: {result['success']}")
print(f"   Total: {result.get('count', 0)} partidas")

if not result['success']:
    print(f"   Erro: {result.get('error')}")
    print(f"   Detalhes: {result.get('details')}")
    print(f"   Codigo: {result.get('error_code')}")
else:
    if result.get('fixtures'):
        print(f"\n   Primeiras 3 partidas:")
        for i, fixture in enumerate(result['fixtures'][:3], 1):
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            league = fixture['league']['name']
            status = fixture['fixture']['status']['short']
            print(f"   {i}. {home} vs {away} ({league}) - Status: {status}")
    else:
        print(f"   Nenhuma partida encontrada para hoje")

# Testar próximos 7 dias
print(f"\n4. Testando proximos 7 dias:")
total_found = 0
for day_offset in range(7):
    search_date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
    result = football_api.get_fixtures_by_date(search_date)
    
    if result['success']:
        count = result.get('count', 0)
        total_found += count
        print(f"   {search_date}: {count} partidas")
    else:
        print(f"   {search_date}: ERRO - {result.get('error')}")

print(f"\n   Total em 7 dias: {total_found} partidas")

# Testar partidas ao vivo
print(f"\n5. Partidas ao vivo agora:")
live_result = football_api.get_live_fixtures()
print(f"   Sucesso: {live_result['success']}")
print(f"   Total: {live_result.get('count', 0)} partidas")

if live_result.get('fixtures'):
    print(f"\n   Partidas ao vivo:")
    for i, fixture in enumerate(live_result['fixtures'][:5], 1):
        home = fixture['teams']['home']['name']
        away = fixture['teams']['away']['name']
        league = fixture['league']['name']
        status = fixture['fixture']['status']['short']
        elapsed = fixture['fixture']['status'].get('elapsed', 'N/A')
        print(f"   {i}. {home} vs {away} ({league}) - {elapsed}' - Status: {status}")

# Testar ligas específicas (EPL, La Liga, Serie A)
print(f"\n6. Testando ligas principais:")
major_leagues = {
    'Premier League': 39,
    'La Liga': 140,
    'Serie A': 135,
    'Bundesliga': 78,
    'Ligue 1': 61
}

for league_name, league_id in major_leagues.items():
    result = football_api.get_fixtures_by_league(league_id, next_matches=10)
    count = result.get('count', 0) if result['success'] else 0
    status = "OK" if result['success'] else "ERRO"
    print(f"   {league_name} (ID {league_id}): {count} partidas - {status}")

print("\n" + "="*80)
print("CONCLUSAO:")
print("="*80)

if total_found > 0:
    print("✅ API-Football esta funcionando e retornando partidas")
    print(f"   Total encontrado: {total_found} partidas nos proximos 7 dias")
    print("\n⚠️  Se o frontend ainda mostra partidas de exemplo:")
    print("   1. Limpe o cache do Django")
    print("   2. Recarregue a pagina do frontend (Ctrl+Shift+R)")
    print("   3. Verifique os logs do backend")
else:
    print("❌ API-Football NAO esta retornando partidas")
    print("\nPossiveis causas:")
    print("   1. Problema com API Key")
    print("   2. Limite de requisicoes atingido")
    print("   3. Periodo sem partidas programadas")
    print("   4. Problema de conexao com API")

print("\n" + "="*80)
