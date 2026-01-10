"""
Testar se as URLs das fotos foram adicionadas corretamente
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("🧪 TESTANDO IMPLEMENTAÇÃO: URLs DE FOTOS DOS JOGADORES")
print("="*80 + "\n")

# Testar com partida de La Liga
fixture_id = 1391001

print(f"📋 Testando partida {fixture_id} (La Liga)...")
print("-"*80 + "\n")

try:
    response = requests.get(
        f"{BASE_URL}/api/matches/api_detail/",
        params={'id': fixture_id},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        match = data.get('match', {})
        lineups = match.get('lineups', [])
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Escalações encontradas: {len(lineups)} times\n")
        
        if len(lineups) > 0:
            total_players = 0
            players_with_photos = 0
            
            for idx, lineup in enumerate(lineups, 1):
                team_name = lineup.get('team', {}).get('name', 'N/A')
                startXI = lineup.get('startXI', [])
                substitutes = lineup.get('substitutes', [])
                all_players = startXI + substitutes
                
                print(f"{'='*80}")
                print(f"⚽ TIME {idx}: {team_name}")
                print(f"{'='*80}\n")
                
                team_with_photos = 0
                
                # Verificar primeiros 3 jogadores
                for player_data in all_players[:3]:
                    player = player_data.get('player', {})
                    name = player.get('name', 'N/A')
                    player_id = player.get('id')
                    photo = player.get('photo')
                    
                    has_photo = photo and photo.startswith('http')
                    
                    if has_photo:
                        team_with_photos += 1
                        players_with_photos += 1
                        status = "✅"
                    else:
                        status = "❌"
                    
                    total_players += 1
                    
                    print(f"{status} {name}")
                    if has_photo:
                        print(f"   📸 {photo}")
                    else:
                        print(f"   ⚠️  Sem foto (ID: {player_id})")
                
                print(f"\n... e mais {len(all_players) - 3} jogadores")
                print(f"Total: {len(all_players)} jogadores\n")
            
            print("="*80)
            print("📊 RESUMO:")
            print("="*80)
            print(f"Total de jogadores: {total_players}")
            print(f"✅ Com foto URL: {players_with_photos}/{total_players}")
            
            if players_with_photos > 0:
                print(f"\n🎉 SUCESSO! URLs de fotos foram adicionadas!")
                print(f"\n🌐 Teste no navegador:")
                print(f"   http://localhost:3001/match/{fixture_id}")
                print(f"\n💡 As fotos reais aparecerão no campo e nos substitutos!")
                print(f"   Se alguma foto não carregar, o sistema usa avatar automático.")
            else:
                print(f"\n⚠️  Nenhuma foto foi adicionada")
                print(f"   Verifique se o código foi salvo corretamente")
        else:
            print("❌ Nenhuma escalação encontrada")
    else:
        print(f"❌ Erro: Status {response.status_code}")
        print(response.text[:500])
        
except requests.exceptions.ConnectionError:
    print("❌ Backend não está rodando!")
    print("Execute: python manage.py runserver")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "="*80 + "\n")
