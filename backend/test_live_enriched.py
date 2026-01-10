"""
Testar endpoint /api/matches/live/ com dados enriquecidos (statistics, lineups)
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("🧪 TESTE: PARTIDAS AO VIVO COM ESTATÍSTICAS E ESCALAÇÕES")
print("="*80 + "\n")

print("🔴 Buscando partidas ao vivo...")
print("-"*80)

try:
    response = requests.get(f"{BASE_URL}/api/matches/live/", timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Total de partidas: {data['count']}")
        print(f"✅ Source: {data['source']}\n")
        
        if data['count'] > 0:
            # Verificar primeira partida em detalhes
            match = data['matches'][0]
            
            home = match['home_team']['name']
            away = match['away_team']['name']
            score_h = match['home_score']
            score_a = match['away_score']
            status = match['status']
            fixture_id = match['id']
            
            print(f"📋 PARTIDA DE EXEMPLO:")
            print(f"   [{fixture_id}] {home} {score_h} x {score_a} {away}")
            print(f"   Status: {status}\n")
            
            # Verificar EVENTS
            has_events = 'events' in match and len(match['events']) > 0
            events_count = len(match.get('events', []))
            events_emoji = "✅" if has_events else "⚠️"
            
            print(f"{events_emoji} EVENTOS (gols, cartões):")
            print(f"   Total: {events_count}")
            if has_events:
                for idx, event in enumerate(match['events'][:3], 1):
                    time = event.get('time', {}).get('elapsed', '?')
                    team = event.get('team', {}).get('name', 'N/A')
                    player = event.get('player', {}).get('name', 'N/A')
                    event_type = event.get('type', 'N/A')
                    detail = event.get('detail', '')
                    print(f"   {idx}. {time}' - {team}: {player} ({event_type} {detail})")
            print()
            
            # Verificar STATISTICS
            has_stats = 'statistics' in match and len(match['statistics']) > 0
            stats_count = len(match.get('statistics', []))
            stats_emoji = "✅" if has_stats else "⚠️"
            
            print(f"{stats_emoji} ESTATÍSTICAS:")
            print(f"   Total de times: {stats_count}")
            if has_stats:
                for team_stats in match['statistics']:
                    team = team_stats.get('team', {}).get('name', 'N/A')
                    stats = team_stats.get('statistics', [])
                    print(f"\n   {team}:")
                    for stat in stats[:5]:  # Primeiras 5
                        stat_type = stat.get('type', 'N/A')
                        stat_value = stat.get('value', 'N/A')
                        print(f"      - {stat_type}: {stat_value}")
            print()
            
            # Verificar LINEUPS
            has_lineups = 'lineups' in match and len(match['lineups']) > 0
            lineups_count = len(match.get('lineups', []))
            lineups_emoji = "✅" if has_lineups else "⚠️"
            
            print(f"{lineups_emoji} ESCALAÇÕES:")
            print(f"   Total de times: {lineups_count}")
            if has_lineups:
                for lineup in match['lineups']:
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
            print()
            
            print("="*80)
            print("🎯 RESUMO:")
            print("="*80)
            print(f"Eventos: {events_emoji} ({events_count} itens)")
            print(f"Estatísticas: {stats_emoji} ({stats_count} times)")
            print(f"Escalações: {lineups_emoji} ({lineups_count} times)")
            print()
            
            if has_events and has_stats and has_lineups:
                print("✅ SUCESSO! Partidas ao vivo COM dados completos!")
            elif has_events or has_stats or has_lineups:
                print("⚠️  PARCIAL: Alguns dados estão disponíveis")
                print("    (Pode ser normal se a partida acabou de começar)")
            else:
                print("❌ FALTANDO: Nenhum dado adicional encontrado")
                print("    (Verifique se a API-Football está retornando os dados)")
            
            print(f"\n🌐 Teste no navegador:")
            print(f"   http://localhost:3001/match/{fixture_id}")
            print("="*80)
        else:
            print("⚠️  Nenhuma partida ao vivo no momento")
            
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"Resposta: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Backend não está rodando!")
    print("Execute: python manage.py runserver")
except requests.exceptions.Timeout:
    print("⏱️  TIMEOUT: Requisição demorou muito (>30s)")
    print("   Isso é normal se há muitas partidas ao vivo")
    print("   O backend está buscando statistics e lineups para cada partida")
except Exception as e:
    print(f"❌ Erro: {e}")

print()
