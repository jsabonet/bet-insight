"""
Testar partida de LIGA MAIOR (ex: La Liga, Premier League)
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

api = FootballAPIService()

print("\n" + "="*80)
print("🔍 BUSCAR PARTIDA DE LIGA MAIOR COM DADOS COMPLETOS")
print("="*80 + "\n")

# Buscar partidas ao vivo
live_result = api.get_live_fixtures()

if live_result['success']:
    fixtures = live_result['fixtures']
    print(f"✅ {len(fixtures)} partidas ao vivo encontradas\n")
    
    # Ligas principais (maior chance de ter dados)
    major_leagues = ['Premier League', 'La Liga', 'Serie A', 'Bundesliga', 'Ligue 1', 
                    'Champions League', 'Europa League', 'Copa do Brasil', 'Brasileirão']
    
    major_fixtures = []
    
    for fixture in fixtures:
        league = fixture['league']['name']
        if any(major in league for major in major_leagues):
            major_fixtures.append(fixture)
    
    print(f"🏆 {len(major_fixtures)} partidas de ligas principais\n")
    
    if len(major_fixtures) > 0:
        print("📋 PARTIDAS DE LIGAS PRINCIPAIS:")
        print("-"*80)
        
        for idx, fixture in enumerate(major_fixtures, 1):
            fixture_id = fixture['fixture']['id']
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            league = fixture['league']['name']
            status = fixture['fixture']['status']['short']
            
            print(f"\n{idx}. [{fixture_id}] {home} vs {away}")
            print(f"   Liga: {league} | Status: {status}")
            
            # Testar dados para esta partida
            events = api.get_fixture_events(fixture_id)
            stats = api.get_fixture_statistics(fixture_id)
            lineups = api.get_fixture_lineups(fixture_id)
            
            has_events = events['success'] and len(events.get('events', [])) > 0
            has_stats = stats['success'] and len(stats.get('statistics', [])) > 0
            has_lineups = lineups['success'] and len(lineups.get('lineups', [])) > 0
            
            print(f"   Eventos: {'✅' if has_events else '❌'} ({len(events.get('events', []))})")
            print(f"   Estatísticas: {'✅' if has_stats else '❌'} ({len(stats.get('statistics', []))})")
            print(f"   Escalações: {'✅' if has_lineups else '❌'} ({len(lineups.get('lineups', []))})")
            
            if has_stats or has_lineups:
                print(f"\n   🎯 RECOMENDAÇÃO: Use este ID para testar!")
                print(f"   http://localhost:3001/match/{fixture_id}")
    else:
        print("⚠️  Nenhuma partida de liga principal ao vivo no momento")
        print("\n📝 TODAS AS PARTIDAS AO VIVO:")
        print("-"*80)
        
        for idx, fixture in enumerate(fixtures[:10], 1):
            fixture_id = fixture['fixture']['id']
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            league = fixture['league']['name']
            country = fixture['league'].get('country', '?')
            status = fixture['fixture']['status']['short']
            
            print(f"{idx}. [{fixture_id}] {home} vs {away}")
            print(f"   {league} ({country}) - {status}\n")
else:
    print("❌ Erro ao buscar partidas ao vivo")

print("\n" + "="*80)
print("💡 INFORMAÇÃO IMPORTANTE:")
print("="*80)
print("A API-Football só fornece estatísticas e escalações completas para:")
print("- Ligas principais (Premier League, La Liga, Bundesliga, etc.)")
print("- Partidas que já começaram há algum tempo")
print("- Ligas menores podem NÃO ter esses dados disponíveis")
print()
print("Se nenhuma partida de liga principal estiver ao vivo,")
print("use a partida de ONTEM que já testamos:")
print("http://localhost:3001/match/1469622 (Brisbane vs Auckland)")
print("="*80 + "\n")
