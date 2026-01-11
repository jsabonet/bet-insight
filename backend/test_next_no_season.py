"""
Testar next sem season
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

football_api = FootballAPIService()

major_leagues = {
    'Premier League': 39,
    'La Liga': 140,
    'Serie A': 135,
}

print("\nTestando 'next' sem especificar season:")
total = 0
for league_name, league_id in major_leagues.items():
    result = football_api.get_fixtures_by_league(league_id, next_matches=10)
    count = result.get('count', 0) if result['success'] else 0
    total += count
    print(f"{league_name}: {count} partidas")
    
    if count > 0:
        for i, f in enumerate(result['fixtures'][:3], 1):
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            date = f['fixture']['date'][:16]
            status = f['fixture']['status']['short']
            print(f"  {i}. {home} vs {away} - {date} ({status})")

print(f"\nTotal: {total} partidas")
