"""
Teste direto da API para verificar se está retornando partidas
"""
import os
import sys
import django
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

def test_api():
    print("=" * 60)
    print("TESTE DA API-FOOTBALL")
    print("=" * 60)
    
    service = FootballAPIService()
    today = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\nBuscando partidas para: {today}")
    print("-" * 60)
    
    result = service.get_fixtures_by_date(today)
    
    if not result['success']:
        print(f"\n❌ ERRO: {result['error']}")
        return
    
    fixtures = result['fixtures']
    print(f"\n✅ Sucesso! {len(fixtures)} partidas encontradas")
    print("-" * 60)
    
    if fixtures:
        print("\nPRIMEIRAS 5 PARTIDAS:")
        for i, fixture in enumerate(fixtures[:5], 1):
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            league = fixture['league']['name']
            status = fixture['fixture']['status']['short']
            date = fixture['fixture']['date']
            
            print(f"\n{i}. {home} vs {away}")
            print(f"   Liga: {league}")
            print(f"   Status: {status}")
            print(f"   Data: {date}")
    else:
        print("\n⚠️ Nenhuma partida encontrada para hoje")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    test_api()
