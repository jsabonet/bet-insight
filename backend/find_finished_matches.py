"""Buscar partidas finalizadas recentes para testar acurácia"""
import os, sys, django
from datetime import datetime, timedelta
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

print('\n' + '='*80)
print('🔍 BUSCANDO PARTIDAS FINALIZADAS RECENTES')
print('='*80)

api = FootballAPIService()

# Buscar dos últimos 10 dias
finished_matches = []

for days_ago in range(10):
    date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    print(f'\n📅 Buscando partidas de {date}...')
    
    result = api.get_fixtures_by_date(date)
    
    if result.get('success'):
        fixtures = result.get('fixtures', [])
        finished = [f for f in fixtures if f['fixture']['status']['short'] == 'FT']
        
        print(f'   Total: {len(fixtures)} | Finalizadas: {len(finished)}')
        
        # Adicionar apenas algumas partidas de cada dia
        finished_matches.extend(finished[:5])  # Máximo 5 por dia
        
        if finished:
            print(f'   Exemplos:')
            for match in finished[:3]:
                home = match['teams']['home']['name']
                away = match['teams']['away']['name']
                score_home = match['goals']['home']
                score_away = match['goals']['away']
                league = match['league']['name']
                fixture_id = match['fixture']['id']
                
                print(f'      • {home} {score_home}-{score_away} {away} ({league}) [ID: {fixture_id}]')
    else:
        print(f'   ❌ Erro: {result.get("error")}')
    
    # Limitar a busca se já temos matches suficientes
    if len(finished_matches) >= 20:
        print(f'\n✅ Já temos {len(finished_matches)} partidas finalizadas, parando busca')
        break

print(f'\n' + '='*80)
print(f'📊 TOTAL: {len(finished_matches)} partidas finalizadas encontradas')
print('='*80 + '\n')

if len(finished_matches) > 0:
    print('💾 Salvando IDs das partidas para teste...')
    
    # Salvar os IDs em um arquivo
    import json
    match_data = []
    for match in finished_matches:
        match_data.append({
            'fixture_id': match['fixture']['id'],
            'home_team': match['teams']['home']['name'],
            'away_team': match['teams']['away']['name'],
            'home_score': match['goals']['home'],
            'away_score': match['goals']['away'],
            'league': match['league']['name'],
            'date': match['fixture']['date']
        })
    
    with open('finished_matches_for_testing.json', 'w', encoding='utf-8') as f:
        json.dump(match_data, f, indent=2, ensure_ascii=False)
    
    print(f'   ✅ Salvos em: finished_matches_for_testing.json')
else:
    print('⚠️ Nenhuma partida finalizada encontrada')
