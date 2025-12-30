import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from datetime import datetime, timedelta

print("⚽ Buscando partidas de Janeiro 2026\n")
print("="*80)

api = FootballAPIService()

# Testar datas específicas em janeiro
dates_to_test = [
    '2026-01-01',
    '2026-01-02',
    '2026-01-03',
    '2026-01-04',
    '2026-01-05',
]

total = 0

for date in dates_to_test:
    print(f"\n📅 {date}...")
    result = api.get_fixtures_by_date(date)
    
    if result['success']:
        count = result['count']
        total += count
        
        if count > 0:
            print(f"✅ {count} partidas encontradas!")
            
            for i, fixture in enumerate(result['fixtures'][:3], 1):
                home = fixture['teams']['home']['name']
                away = fixture['teams']['away']['name']
                league = fixture['league']['name']
                time = fixture['fixture']['date'][11:16]
                
                print(f"  {i}. {time} | {home} vs {away} ({league})")
        else:
            print(f"  ⚠️ 0 partidas")
    else:
        print(f"  ❌ Erro: {result['error']}")

print("\n" + "="*80)
print(f"\n📊 TOTAL: {total} partidas em Janeiro 2026!")
