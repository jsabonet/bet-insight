"""
Testar DIRETAMENTE a API-Football para partida ao vivo
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

api = FootballAPIService()

print("\n" + "="*80)
print("🔍 TESTE DIRETO: API-FOOTBALL (partida ao vivo)")
print("="*80 + "\n")

# 1. Buscar partidas ao vivo
print("1️⃣ Buscar partidas ao vivo")
print("-"*80)

live_result = api.get_live_fixtures()

if live_result['success'] and len(live_result['fixtures']) > 0:
    fixture = live_result['fixtures'][0]
    fixture_id = fixture['fixture']['id']
    
    home = fixture['teams']['home']['name']
    away = fixture['teams']['away']['name']
    status = fixture['fixture']['status']['short']
    
    print(f"✅ Partida: [{fixture_id}] {home} vs {away} ({status})\n")
    
    # 2. Buscar EVENTOS
    print("2️⃣ Buscar EVENTOS (gols, cartões)")
    print("-"*80)
    events_result = api.get_fixture_events(fixture_id)
    
    if events_result['success']:
        events = events_result.get('events', [])
        print(f"✅ Total: {len(events)} eventos")
        
        if len(events) > 0:
            print("\nPrimeiros 3 eventos:")
            for idx, event in enumerate(events[:3], 1):
                time = event.get('time', {}).get('elapsed', '?')
                team = event.get('team', {}).get('name', 'N/A')
                player = event.get('player', {}).get('name', 'N/A')
                event_type = event.get('type', 'N/A')
                print(f"   {idx}. {time}' - {team}: {player} ({event_type})")
        else:
            print("   ⚠️  Nenhum evento ainda (partida pode ter acabado de começar)")
    else:
        print(f"❌ Erro: {events_result.get('error')}")
    
    # 3. Buscar ESTATÍSTICAS
    print("\n3️⃣ Buscar ESTATÍSTICAS")
    print("-"*80)
    stats_result = api.get_fixture_statistics(fixture_id)
    
    if stats_result['success']:
        statistics = stats_result.get('statistics', [])
        print(f"✅ Total: {len(statistics)} times")
        
        if len(statistics) > 0:
            for team_stats in statistics:
                team = team_stats.get('team', {}).get('name', 'N/A')
                stats = team_stats.get('statistics', [])
                
                print(f"\n   {team}:")
                for stat in stats[:5]:
                    stat_type = stat.get('type', 'N/A')
                    stat_value = stat.get('value', 'N/A')
                    print(f"      - {stat_type}: {stat_value}")
        else:
            print("   ⚠️  Nenhuma estatística ainda")
    else:
        print(f"❌ Erro: {stats_result.get('error')}")
    
    # 4. Buscar ESCALAÇÕES
    print("\n4️⃣ Buscar ESCALAÇÕES")
    print("-"*80)
    lineups_result = api.get_fixture_lineups(fixture_id)
    
    if lineups_result['success']:
        lineups = lineups_result.get('lineups', [])
        print(f"✅ Total: {len(lineups)} times")
        
        if len(lineups) > 0:
            for lineup in lineups:
                team = lineup.get('team', {}).get('name', 'N/A')
                formation = lineup.get('formation', 'N/A')
                coach = lineup.get('coach', {}).get('name', 'N/A')
                startXI_count = len(lineup.get('startXI', []))
                subs_count = len(lineup.get('substitutes', []))
                
                print(f"\n   {team}:")
                print(f"      Formação: {formation}")
                print(f"      Técnico: {coach}")
                print(f"      Titulares: {startXI_count}")
                print(f"      Reservas: {subs_count}")
        else:
            print("   ⚠️  Escalações não disponíveis")
    else:
        print(f"❌ Erro: {lineups_result.get('error')}")
    
    print("\n" + "="*80)
    print("🎯 CONCLUSÃO:")
    print("="*80)
    
    has_events = events_result['success'] and len(events_result.get('events', [])) > 0
    has_stats = stats_result['success'] and len(stats_result.get('statistics', [])) > 0
    has_lineups = lineups_result['success'] and len(lineups_result.get('lineups', [])) > 0
    
    print(f"Eventos: {'✅' if has_events else '⚠️'}")
    print(f"Estatísticas: {'✅' if has_stats else '⚠️'}")
    print(f"Escalações: {'✅' if has_lineups else '⚠️'}")
    
    if not (has_events or has_stats or has_lineups):
        print("\n⚠️  API-Football NÃO está retornando dados para esta partida ao vivo")
        print("    Isso pode acontecer se:")
        print("    - A partida é de uma liga menor")
        print("    - A partida acabou de começar")
        print("    - A API-Football ainda não coletou os dados")
    else:
        print("\n✅ API-Football está retornando alguns dados!")
    
else:
    print("❌ Nenhuma partida ao vivo encontrada")

print("="*80 + "\n")
