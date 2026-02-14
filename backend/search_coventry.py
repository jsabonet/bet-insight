import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

api = FootballAPIService()
result = api.get_fixtures_by_date('2026-02-07')

if result:
    fixtures = result.get('response', [])
    print(f'\nTotal de partidas hoje (07/02/2026): {len(fixtures)}')
    
    coventry_matches = [
        f for f in fixtures 
        if 'Coventry' in f['teams']['home']['name'] 
        or 'Coventry' in f['teams']['away']['name']
    ]
    
    print(f'Partidas do Coventry: {len(coventry_matches)}\n')
    
    for match in coventry_matches:
        fixture_id = match['fixture']['id']
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        status = match['fixture']['status']['short']
        league = match['league']['name']
        print(f'API ID: {fixture_id}')
        print(f'Partida: {home} vs {away}')
        print(f'Liga: {league}')
        print(f'Status: {status}')
        print('-' * 60)
else:
    print('Erro ao buscar fixtures da API')
