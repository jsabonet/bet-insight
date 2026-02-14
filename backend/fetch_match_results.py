"""Buscar resultados das partidas e validar apostas"""
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet, Match
from apps.matches.services.football_api import FootballAPIService

print('\n' + '='*80)
print('🔍 BUSCANDO RESULTADOS DAS PARTIDAS')
print('='*80)

# IDs das partidas pendentes
match_ids = [3098, 3095, 3093, 3105]

api = FootballAPIService()

for match_id in match_ids:
    print(f'\n📊 Buscando Match ID: {match_id}')
    
    # Tentar buscar do banco primeiro
    try:
        match = Match.objects.get(id=match_id)
        print(f'   ✅ Encontrado no banco: {match.home_team} vs {match.away_team}')
        print(f'      Status: {match.status}')
        
        if match.status == 'FT':
            print(f'      Placar: {match.home_score} - {match.away_score}')
        else:
            print(f'      ⏳ Status: {match.status} (não finalizado)')
    except Match.DoesNotExist:
        print(f'   ❌ Match não encontrado no banco')
        
        # Tentar buscar da API usando fixture ID
        result = api.get_fixture_details(match_id)
        if result.get('success'):
            fixture = result.get('fixture')
            if fixture:
                status = fixture['fixture']['status']['short']
                home_team = fixture['teams']['home']['name']
                away_team = fixture['teams']['away']['name']
                
                print(f'   ✅ Encontrado na API: {home_team} vs {away_team}')
                print(f'      Status: {status}')
                
                if status == 'FT':
                    home_score = fixture['goals']['home']
                    away_score = fixture['goals']['away']
                    print(f'      Placar: {home_score} - {away_score}')
                else:
                    print(f'      ⏳ Status: {status} (não finalizado)')
        else:
            print(f'   ❌ Erro na API: {result.get("error")}')

print('\n' + '='*80)
print('✅ Busca concluída')
print('='*80 + '\n')
