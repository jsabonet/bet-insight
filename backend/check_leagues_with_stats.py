"""
Verificar quais ligas oferecem estatísticas completas na API-Football
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from datetime import datetime, timedelta

api = FootballAPIService()

print("\n" + "="*80)
print("🔍 VERIFICANDO LIGAS COM ESTATÍSTICAS COMPLETAS")
print("="*80 + "\n")

# 1. Buscar partidas de ontem e hoje (maior chance de ter dados)
print("📅 Buscando partidas recentes para análise...")
print("-"*80)

dates = [
    (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),  # Ontem
    datetime.now().strftime('%Y-%m-%d'),  # Hoje
]

all_fixtures = []

for date in dates:
    result = api.get_fixtures_by_date(date)
    if result['success']:
        all_fixtures.extend(result['fixtures'])
        print(f"{date}: {len(result['fixtures'])} partidas")

print(f"\n✅ Total: {len(all_fixtures)} partidas encontradas\n")

# 2. Agrupar por liga e verificar disponibilidade de dados
print("📊 Analisando disponibilidade de dados por liga...")
print("-"*80 + "\n")

leagues_data = {}

# Pegar amostra de partidas (primeiras 50 para não gastar muito da API)
sample_fixtures = all_fixtures[:50]

for idx, fixture in enumerate(sample_fixtures, 1):
    fixture_id = fixture['fixture']['id']
    league_name = fixture['league']['name']
    league_country = fixture['league'].get('country', 'N/A')
    league_key = f"{league_country} - {league_name}"
    
    # Verificar se a partida já começou ou terminou
    status = fixture['fixture']['status']['short']
    if status in ['NS', 'TBD', 'CANC', 'ABD', 'AWD', 'WO']:  # Não começou ou cancelada
        continue
    
    if league_key not in leagues_data:
        leagues_data[league_key] = {
            'country': league_country,
            'name': league_name,
            'logo': fixture['league'].get('logo', ''),
            'fixtures_tested': 0,
            'has_lineups': 0,
            'has_statistics': 0,
            'has_events': 0,
        }
    
    # Testar apenas primeira partida de cada liga (economizar chamadas API)
    if leagues_data[league_key]['fixtures_tested'] >= 1:
        continue
    
    print(f"[{idx}/{len(sample_fixtures)}] Testando {league_key}...", end=" ")
    
    # Buscar dados
    lineups = api.get_fixture_lineups(fixture_id)
    stats = api.get_fixture_statistics(fixture_id)
    events = api.get_fixture_events(fixture_id)
    
    leagues_data[league_key]['fixtures_tested'] += 1
    
    if lineups['success'] and len(lineups.get('lineups', [])) > 0:
        leagues_data[league_key]['has_lineups'] += 1
    
    if stats['success'] and len(stats.get('statistics', [])) > 0:
        leagues_data[league_key]['has_statistics'] += 1
    
    if events['success'] and len(events.get('events', [])) > 0:
        leagues_data[league_key]['has_events'] += 1
    
    has_all = (lineups['success'] and stats['success'] and 
               len(lineups.get('lineups', [])) > 0 and 
               len(stats.get('statistics', [])) > 0)
    
    status_emoji = "✅" if has_all else "❌"
    print(status_emoji)

print("\n" + "="*80)
print("📋 RESULTADO: LIGAS COM DADOS COMPLETOS")
print("="*80 + "\n")

# Separar ligas com e sem dados completos
leagues_with_full_data = []
leagues_partial_data = []
leagues_no_data = []

for league_key, data in leagues_data.items():
    if data['fixtures_tested'] == 0:
        continue
    
    has_lineups = data['has_lineups'] > 0
    has_stats = data['has_statistics'] > 0
    
    league_info = {
        'key': league_key,
        'country': data['country'],
        'name': data['name'],
        'has_lineups': has_lineups,
        'has_stats': has_stats,
        'has_events': data['has_events'] > 0,
    }
    
    if has_lineups and has_stats:
        leagues_with_full_data.append(league_info)
    elif has_lineups or has_stats:
        leagues_partial_data.append(league_info)
    else:
        leagues_no_data.append(league_info)

# Exibir resultados
print("✅ LIGAS COM DADOS COMPLETOS (Lineups + Statistics):")
print("-"*80)
if leagues_with_full_data:
    for idx, league in enumerate(sorted(leagues_with_full_data, key=lambda x: x['country']), 1):
        print(f"{idx:2d}. {league['country']:20s} - {league['name']}")
else:
    print("   Nenhuma liga com dados completos na amostra")

print("\n⚠️  LIGAS COM DADOS PARCIAIS:")
print("-"*80)
if leagues_partial_data:
    for idx, league in enumerate(sorted(leagues_partial_data, key=lambda x: x['country']), 1):
        lineups_icon = "📋" if league['has_lineups'] else "  "
        stats_icon = "📊" if league['has_stats'] else "  "
        print(f"{idx:2d}. {league['country']:20s} - {league['name']:40s} {lineups_icon}{stats_icon}")
else:
    print("   Nenhuma liga com dados parciais")

print("\n❌ LIGAS SEM DADOS:")
print("-"*80)
if leagues_no_data:
    for idx, league in enumerate(sorted(leagues_no_data, key=lambda x: x['country']), 1):
        print(f"{idx:2d}. {league['country']:20s} - {league['name']}")
else:
    print("   Nenhuma liga sem dados")

print("\n" + "="*80)
print("📊 RESUMO:")
print("="*80)
print(f"Total de ligas analisadas: {len(leagues_data)}")
print(f"✅ Com dados completos: {len(leagues_with_full_data)}")
print(f"⚠️  Com dados parciais: {len(leagues_partial_data)}")
print(f"❌ Sem dados: {len(leagues_no_data)}")
print()
print("💡 DICA: Ligas principais (Premier League, La Liga, etc.) sempre têm dados completos")
print("="*80 + "\n")
