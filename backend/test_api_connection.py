import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from datetime import datetime, timedelta

print("🔍 Testando API-Football...\n")
print("="*80)

api = FootballAPIService()

# Verificar se a chave está configurada
if not api.api_key or api.api_key == 'YOUR_API_KEY_HERE':
    print("❌ API Key não configurada!")
    print("Configure a API_FOOTBALL_KEY no arquivo .env")
    print("Obtenha sua chave em: https://dashboard.api-football.com/register")
    exit(1)

print(f"✅ API Key configurada: {api.api_key[:20]}...")
print(f"✅ Base URL: {api.base_url}\n")

# Testar busca de partidas de hoje
print("📅 Buscando partidas de hoje...")
today = datetime.now().strftime('%Y-%m-%d')
result = api.get_fixtures_by_date(today)

if result['success']:
    print(f"✅ Sucesso! {result['count']} partidas encontradas\n")
    
    if result['count'] > 0:
        print("🎯 Primeiras 5 partidas:\n")
        for i, fixture in enumerate(result['fixtures'][:5], 1):
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            league = fixture['league']['name']
            status_short = fixture['fixture']['status']['short']
            match_date = fixture['fixture']['date']
            
            print(f"{i}. {home} vs {away}")
            print(f"   Liga: {league}")
            print(f"   Status: {status_short}")
            print(f"   Data: {match_date}\n")
    else:
        print("ℹ️ Nenhuma partida hoje. Tentando amanhã...")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        result = api.get_fixtures_by_date(tomorrow)
        
        if result['success'] and result['count'] > 0:
            print(f"✅ {result['count']} partidas encontradas para amanhã\n")
            
            print("🎯 Primeiras 5 partidas:\n")
            for i, fixture in enumerate(result['fixtures'][:5], 1):
                home = fixture['teams']['home']['name']
                away = fixture['teams']['away']['name']
                league = fixture['league']['name']
                
                print(f"{i}. {home} vs {away}")
                print(f"   Liga: {league}\n")
else:
    print(f"❌ Erro: {result['error']}")
    print("\nVerifique:")
    print("1. Sua chave API está correta")
    print("2. Você tem créditos disponíveis")
    print("3. Sua conexão com a internet está funcionando")

print("="*80)
print("\n💡 Dica: A API-Football oferece 100 requisições/dia no plano gratuito")
