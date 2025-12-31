"""
Testar se agora o frontend recebe api_football_id correto
"""
import os, django, sys
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.views import MatchViewSet
from rest_framework.test import APIRequestFactory

print("\n" + "="*100)
print("✅ TESTE: Verificar se from_api retorna api_football_id")
print("="*100 + "\n")

factory = APIRequestFactory()
request = factory.get('/api/matches/from_api/?date=2025-12-30')

view = MatchViewSet.as_view({'get': 'from_api'})
response = view(request)

if response.status_code == 200:
    data = response.data
    matches = data.get('matches', [])
    
    print(f"✅ {len(matches)} partidas retornadas\n")
    
    # Verificar Maniema
    maniema = [m for m in matches if 'Maniema' in m['home_team']['name']]
    
    if maniema:
        match = maniema[0]
        print(f"🎯 PARTIDA: {match['home_team']['name']} vs {match['away_team']['name']}")
        print("-"*100)
        print(f"   id: {match.get('id')}")
        print(f"   api_football_id: {match.get('api_football_id', '❌ AUSENTE')}")
        print(f"   Status: {match.get('status')}")
        
        if match.get('api_football_id'):
            print(f"\n✅ SUCESSO! api_football_id presente")
            print(f"   Frontend pode usar: match.api_football_id = {match['api_football_id']}")
            print(f"   Backend vai buscar dados completos da API")
            print(f"   IA vai receber: predictions + fixture_details + (H2H se tiver football_data_id)")
        else:
            print(f"\n❌ PROBLEMA! api_football_id ausente")
            print(f"   Frontend vai enviar api_id=null")
            print(f"   Backend não vai buscar dados da API")
            print(f"   IA vai receber apenas nomes = confiança 1 estrela")
    else:
        print("❌ Partida Maniema não encontrada")
else:
    print(f"❌ Erro: {response.status_code}")

print("\n" + "="*100)
print("✅ TESTE CONCLUÍDO")
print("="*100 + "\n")
