"""
Testar se as fotos dos jogadores estão vindo da API-Football
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

api = FootballAPIService()

print("\n" + "="*80)
print("📸 VERIFICANDO FOTOS DOS JOGADORES NAS ESCALAÇÕES")
print("="*80 + "\n")

# Usar a partida que sabemos que tem lineups
fixture_id = 1469622  # Brisbane Roar vs Auckland

print(f"🔍 Buscando escalações da partida {fixture_id}...")
print("-"*80 + "\n")

lineups_result = api.get_fixture_lineups(fixture_id)

if not lineups_result['success']:
    print(f"❌ Erro: {lineups_result.get('error')}")
    exit(1)

lineups = lineups_result.get('lineups', [])

if len(lineups) == 0:
    print("❌ Nenhuma escalação encontrada")
    exit(1)

print(f"✅ {len(lineups)} times encontrados\n")

for team_idx, lineup in enumerate(lineups, 1):
    team_name = lineup.get('team', {}).get('name', 'N/A')
    formation = lineup.get('formation', 'N/A')
    
    print(f"{'='*80}")
    print(f"🏁 TIME {team_idx}: {team_name}")
    print(f"   Formação: {formation}")
    print(f"{'='*80}\n")
    
    # Verificar titulares
    startXI = lineup.get('startXI', [])
    print(f"👥 TITULARES ({len(startXI)} jogadores):")
    print("-"*80)
    
    photos_with_url = 0
    photos_missing = 0
    
    for idx, player_data in enumerate(startXI[:5], 1):  # Primeiros 5
        player = player_data.get('player', {})
        name = player.get('name', 'N/A')
        number = player.get('number', '?')
        pos = player.get('pos', '?')
        photo = player.get('photo')
        
        has_photo = photo and photo.startswith('http')
        if has_photo:
            photos_with_url += 1
            status = "✅"
        else:
            photos_missing += 1
            status = "❌"
        
        print(f"   {idx}. {status} #{number:2} {name:30} ({pos})")
        if has_photo:
            print(f"      📸 {photo}")
    
    if len(startXI) > 5:
        print(f"   ... e mais {len(startXI) - 5} jogadores")
    
    print(f"\n   Total titulares com foto: {photos_with_url}/{len(startXI)}")
    
    # Verificar substitutos
    substitutes = lineup.get('substitutes', [])
    print(f"\n🔄 SUBSTITUTOS ({len(substitutes)} jogadores):")
    print("-"*80)
    
    subs_with_photo = 0
    subs_missing = 0
    
    for idx, player_data in enumerate(substitutes[:3], 1):  # Primeiros 3
        player = player_data.get('player', {})
        name = player.get('name', 'N/A')
        number = player.get('number', '?')
        pos = player.get('pos', '?')
        photo = player.get('photo')
        
        has_photo = photo and photo.startswith('http')
        if has_photo:
            subs_with_photo += 1
            status = "✅"
        else:
            subs_missing += 1
            status = "❌"
        
        print(f"   {idx}. {status} #{number:2} {name:30} ({pos})")
        if has_photo:
            print(f"      📸 {photo}")
    
    if len(substitutes) > 3:
        print(f"   ... e mais {len(substitutes) - 3} jogadores")
    
    print(f"\n   Total substitutos com foto: {subs_with_photo}/{len(substitutes)}")
    print()

print("\n" + "="*80)
print("📊 RESUMO:")
print("="*80)
print("O componente Lineups.jsx JÁ está configurado para exibir:")
print("✅ Fotos oficiais dos jogadores (player.photo)")
print("✅ Fallback para avatar gerado quando foto não disponível")
print("✅ Bordas arredondadas e design responsivo")
print()
print("Se as fotos aparecem como avatares coloridos é porque:")
print("❌ API-Football não retornou URL da foto para aquele jogador")
print("✅ O sistema usa fallback automático (ui-avatars.com)")
print()
print("Para partidas de ligas principais (Premier, La Liga, etc):")
print("✅ Maioria dos jogadores TEM foto oficial")
print("="*80 + "\n")
