"""
Testar season 2024
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

football_api = FootballAPIService()

print("\nTestando season 2024 (Premier League)...")
result = football_api.get_fixtures_by_league(39, season=2024, next_matches=10)

print(f"Sucesso: {result['success']}")
print(f"Total: {result.get('count', 0)}")

if result.get('fixtures'):
    print("\nPartidas encontradas:")
    for i, f in enumerate(result['fixtures'][:5], 1):
        home = f['teams']['home']['name']
        away = f['teams']['away']['name']
        date = f['fixture']['date'][:10]
        status = f['fixture']['status']['short']
        print(f"{i}. {home} vs {away} - {date} ({status})")
