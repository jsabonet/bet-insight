import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from datetime import datetime

print("⚽ Buscando partidas de ligas específicas...\n")
print("="*80)

api = FootballAPIService()

# IDs das principais ligas na API-Football
leagues = {
    'Premier League': 39,
    'La Liga': 140,
    'Serie A': 135,
    'Bundesliga': 78,
    'Ligue 1': 61,
    'Brasileirão': 71,
    'Champions League': 2,
    'Primeira Liga': 94,
}

season = 2024  # Temporada atual
total_matches = 0

print(f"🔍 Buscando próximas 10 partidas de cada liga (Temporada {season})...\n")

for league_name, league_id in leagues.items():
    result = api.get_fixtures_by_league(league_id, season)
    
    if result['success']:
        count = result['count']
        total_matches += count
        
        if count > 0:
            print(f"\n🏆 {league_name}: {count} partidas encontradas")
            
            # Mostrar primeiras 5 partidas
            for i, fixture in enumerate(result['fixtures'][:5], 1):
                home = fixture['teams']['home']['name']
                away = fixture['teams']['away']['name']
                date = fixture['fixture']['date'][:10]
                time = fixture['fixture']['date'][11:16]
                status = fixture['fixture']['status']['short']
                
                print(f"  {i}. {date} {time} | {home} vs {away} [{status}]")
        else:
            print(f"\n🏆 {league_name}: 0 partidas")
    else:
        print(f"\n❌ {league_name}: Erro - {result['error']}")

print("\n" + "="*80)
print(f"\n📊 Total: {total_matches} partidas encontradas")

# Buscar partidas ao vivo
print("\n\n🔴 Buscando partidas AO VIVO...")
live_result = api.get_live_fixtures()

if live_result['success']:
    live_count = live_result['count']
    print(f"✅ {live_count} partidas ao vivo encontradas")
    
    if live_count > 0:
        for fixture in live_result['fixtures'][:10]:
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            league = fixture['league']['name']
            elapsed = fixture['fixture']['status']['elapsed']
            home_score = fixture['goals']['home'] or 0
            away_score = fixture['goals']['away'] or 0
            
            print(f"  🔴 {home} {home_score}-{away_score} {away} ({league}) - {elapsed}'")
