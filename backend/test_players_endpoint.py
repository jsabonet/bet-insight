"""
Testar endpoint /players com ID específico do jogador
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
import json

api = FootballAPIService()

print("\n" + "="*80)
print("🔍 TESTANDO ENDPOINT /players COM ID DO JOGADOR")
print("="*80 + "\n")

# ID do jogador que encontramos nos lineups
player_id = 47247  # David Soria (Getafe)

print(f"📋 Buscando dados do jogador ID {player_id}...")
print("-"*80 + "\n")

try:
    response = api.session.get(
        f'{api.base_url}/players',
        params={
            'id': player_id,
            'season': 2025
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        
        if len(data.get('response', [])) > 0:
            player_data = data['response'][0]
            
            print("✅ SUCESSO! Dados do jogador encontrados:\n")
            print(f"Nome: {player_data.get('player', {}).get('name')}")
            print(f"ID: {player_data.get('player', {}).get('id')}")
            
            # FOTO DO JOGADOR
            photo = player_data.get('player', {}).get('photo')
            print(f"\n📸 FOTO: {photo}")
            
            # Estatísticas
            stats = player_data.get('statistics', [])
            if stats:
                print(f"\n📊 Time atual: {stats[0].get('team', {}).get('name')}")
                print(f"   Liga: {stats[0].get('league', {}).get('name')}")
            
            print("\n" + "="*60)
            print("🎯 ESTRUTURA COMPLETA DO PLAYER:")
            print("="*60)
            print(json.dumps(player_data, indent=2)[:1500])
            print("\n... (dados truncados)")
            
        else:
            print("⚠️  Nenhum dado retornado para este jogador")
    else:
        print(f"❌ Erro: Status {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n\n" + "="*80)
print("💡 DESCOBERTA:")
print("="*80)
print("""
✅ A API-Football TEM endpoint /players que retorna FOTOS!

Estrutura da requisição:
  GET https://v3.football.api-sports.io/players
  Params: { id: PLAYER_ID, season: YEAR }

Estrutura da resposta:
  {
    "player": {
      "id": 47247,
      "name": "David Soria",
      "photo": "https://media.api-sports.io/football/players/47247.png"
    },
    "statistics": [...]
  }

🎯 SOLUÇÃO PROPOSTA:
1. Criar modelo Player no Django para cache
2. Criar método get_player_photo(player_id, season)
3. Ao buscar lineups, enriquecer com fotos dos jogadores
4. Salvar no cache para próximas vezes
""")

print("="*80 + "\n")
