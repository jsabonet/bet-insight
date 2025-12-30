import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from datetime import datetime, timedelta

print("⚽ Buscando partidas dos próximos 7 dias...\n")
print("="*80)

api = FootballAPIService()
total_matches = 0

for day_offset in range(7):
    date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
    result = api.get_fixtures_by_date(date)
    
    if result['success']:
        count = result['count']
        total_matches += count
        
        if count > 0:
            print(f"\n📅 {date}: {count} partidas")
            
            # Mostrar primeiras 3 partidas
            for fixture in result['fixtures'][:3]:
                home = fixture['teams']['home']['name']
                away = fixture['teams']['away']['name']
                league = fixture['league']['name']
                time = fixture['fixture']['date'][11:16]  # HH:MM
                
                print(f"  {time} | {home} vs {away} ({league})")
        else:
            print(f"📅 {date}: 0 partidas")
    else:
        print(f"❌ Erro ao buscar {date}: {result['error']}")

print("\n" + "="*80)
print(f"\n📊 Total: {total_matches} partidas encontradas nos próximos 7 dias")
