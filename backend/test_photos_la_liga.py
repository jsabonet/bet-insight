"""
Testar fotos com partida de LIGA MAIOR (La Liga)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

api = FootballAPIService()

print("\n" + "="*80)
print("📸 TESTE: FOTOS DE JOGADORES EM LIGA PRINCIPAL")
print("="*80 + "\n")

# Getafe vs Real Sociedad (La Liga) - partida ao vivo
fixture_id = 1391001

print(f"🔍 Testando partida {fixture_id} (La Liga)...")
print("-"*80 + "\n")

lineups_result = api.get_fixture_lineups(fixture_id)

if not lineups_result['success']:
    print(f"❌ Erro: {lineups_result.get('error')}")
    print("\nVamos buscar a lista de partidas recentes de La Liga com lineups...")
    
    # Buscar partidas recentes de La Liga
    from datetime import datetime, timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    fixtures_result = api.get_fixtures_by_date(yesterday)
    if fixtures_result['success']:
        la_liga_fixtures = [
            f for f in fixtures_result['fixtures']
            if 'La Liga' in f['league']['name']
        ]
        
        print(f"\n✅ {len(la_liga_fixtures)} partidas de La Liga encontradas")
        
        for fixture in la_liga_fixtures[:3]:
            test_id = fixture['fixture']['id']
            print(f"\nTestando {test_id}...")
            test_lineups = api.get_fixture_lineups(test_id)
            
            if test_lineups['success'] and len(test_lineups.get('lineups', [])) > 0:
                print(f"✅ TEM lineups! Usando {test_id}")
                fixture_id = test_id
                lineups_result = test_lineups
                break
    
    if not lineups_result['success']:
        print("❌ Nenhuma partida de La Liga com lineups encontrada")
        exit(1)

lineups = lineups_result.get('lineups', [])

if len(lineups) == 0:
    print("❌ Nenhuma escalação encontrada")
    exit(1)

print(f"\n✅ {len(lineups)} times com escalações completas\n")

total_with_photos = 0
total_players = 0

for team_idx, lineup in enumerate(lineups, 1):
    team_name = lineup.get('team', {}).get('name', 'N/A')
    formation = lineup.get('formation', 'N/A')
    
    print(f"{'='*80}")
    print(f"⚽ {team_name} ({formation})")
    print(f"{'='*80}\n")
    
    startXI = lineup.get('startXI', [])
    substitutes = lineup.get('substitutes', [])
    all_players = startXI + substitutes
    
    print(f"📋 TODOS OS JOGADORES ({len(all_players)} total):\n")
    
    with_photo = 0
    without_photo = 0
    
    for idx, player_data in enumerate(all_players, 1):
        player = player_data.get('player', {})
        name = player.get('name', 'N/A')
        number = player.get('number', '?')
        pos = player.get('pos', '?')
        photo = player.get('photo')
        
        has_photo = photo and photo.startswith('http')
        
        if has_photo:
            with_photo += 1
            total_with_photos += 1
        else:
            without_photo += 1
        
        total_players += 1
        
        # Mostrar apenas primeiros 3 com e 3 sem foto
        if (has_photo and with_photo <= 3) or (not has_photo and without_photo <= 3):
            status = "✅" if has_photo else "❌"
            print(f"{status} #{number:2} {name:25} ({pos})")
            if has_photo and with_photo <= 3:
                print(f"   📸 {photo[:60]}...")
    
    print(f"\n📊 Resumo {team_name}:")
    print(f"   ✅ Com foto: {with_photo}/{len(all_players)} ({with_photo/len(all_players)*100:.1f}%)")
    print(f"   ❌ Sem foto: {without_photo}/{len(all_players)} ({without_photo/len(all_players)*100:.1f}%)")
    print()

print("\n" + "="*80)
print("📊 RESUMO GERAL:")
print("="*80)
print(f"Total de jogadores analisados: {total_players}")
print(f"✅ Com foto oficial: {total_with_photos} ({total_with_photos/total_players*100:.1f}%)")
print(f"❌ Sem foto: {total_players - total_with_photos} ({(total_players - total_with_photos)/total_players*100:.1f}%)")
print()

if total_with_photos > 0:
    print("✅ SUCESSO! A API-Football RETORNA fotos para ligas principais!")
    print("   O componente Lineups.jsx já está configurado corretamente.")
    print()
    print("🌐 Teste no navegador:")
    print(f"   http://localhost:3001/match/{fixture_id}")
else:
    print("⚠️  API-Football não retornou fotos para esta partida.")
    print("   Isso pode acontecer se a partida for muito antiga ou de liga menor.")

print("="*80 + "\n")
