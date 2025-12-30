import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

print("⚽ Buscando PRÓXIMAS partidas (sem filtro de temporada)\n")
print("="*80)

api = FootballAPIService()

leagues = {
    'Premier League': 39,
    'La Liga': 140,
    'Serie A': 135,
    'Bundesliga': 78,
    'Ligue 1': 61,
}

total = 0

for league_name, league_id in leagues.items():
    print(f"\n🔍 {league_name}...")
    result = api.get_fixtures_by_league(league_id, season=None, next_matches=10)
    
    if result['success']:
        count = result['count']
        total += count
        
        if count > 0:
            print(f"✅ {count} partidas!")
            
            for i, fixture in enumerate(result['fixtures'][:3], 1):
                home = fixture['teams']['home']['name']
                away = fixture['teams']['away']['name']
                date = fixture['fixture']['date'][:16]
                status = fixture['fixture']['status']['short']
                
                print(f"  {i}. {date} | {home} vs {away} [{status}]")
        else:
            print(f"⚠️ Nenhuma partida")
    else:
        print(f"❌ Erro: {result['error']}")

print("\n" + "="*80)
print(f"\n📊 TOTAL: {total} partidas!")
