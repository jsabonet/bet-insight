import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from datetime import datetime, timedelta

print("⚽ Buscando partidas RECENTES (últimos 10 dias)\n")
print("="*80)

api = FootballAPIService()
total = 0

for days_ago in range(10):
    date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    result = api.get_fixtures_by_date(date)
    
    if result['success']:
        count = result['count']
        total += count
        
        if count > 0:
            print(f"\n✅ {date}: {count} partidas")
            
            for i, fixture in enumerate(result['fixtures'][:3], 1):
                home = fixture['teams']['home']['name']
                away = fixture['teams']['away']['name']
                league = fixture['league']['name']
                status = fixture['fixture']['status']['short']
                
                home_score = fixture['goals']['home'] if fixture['goals']['home'] is not None else '-'
                away_score = fixture['goals']['away'] if fixture['goals']['away'] is not None else '-'
                
                print(f"  {home} {home_score}-{away_score} {away} ({league}) [{status}]")
        else:
            print(f"⚠️ {date}: 0 partidas")
    else:
        print(f"❌ {date}: Erro")

print("\n" + "="*80)
print(f"\n📊 TOTAL: {total} partidas nos últimos 10 dias!")

if total > 0:
    print("\n✅ SUCESSO! API-Football está funcionando!")
    print("Sistema irá exibir esses dados reais no lugar dos dados de exemplo.")
