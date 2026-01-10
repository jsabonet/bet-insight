"""
Listar partidas AO VIVO apenas das ligas com cobertura completa
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from datetime import datetime

api = FootballAPIService()

# Ligas principais com cobertura completa
MAJOR_LEAGUES = [
    # Europa Top 5
    'Premier League', 'Championship', 'FA Cup', 'League Cup',
    'La Liga', 'Segunda División', 'Copa del Rey',
    'Bundesliga', '2. Bundesliga', 'DFB Pokal',
    'Serie A', 'Serie B', 'Coppa Italia',
    'Ligue 1', 'Ligue 2', 'Coupe de France',
    
    # Europa - Outros
    'Primeira Liga', 'Liga Portugal 2',
    'Eredivisie',
    'Pro League',
    'Super Lig', '1. Lig',
    'Premier League',  # Rússia
    'Premiership',  # Escócia
    
    # UEFA
    'Champions League', 'Europa League', 'Conference League', 
    'Euro', 'Nations League',
    
    # Brasil
    'Serie A', 'Serie B', 'Copa do Brasil', 'Paulista A1', 'Carioca A',
    'Brasileirão', 'Brasileiro',  # Variações
    
    # América Latina
    'Liga Profesional', 'Copa Argentina',
    'Liga MX',
    'MLS', 'USL Championship',
    'Primera A',  # Colômbia
    'Primera División',  # Chile
    'Copa Libertadores', 'Copa Sudamericana', 'Copa América',
    
    # Ásia/Oceania
    'J1 League',
    'K League 1',
    'Pro League',  # Arábia Saudita
    'Super League',  # China
    'A-League',
    
    # África
    'Premier Division',  # África do Sul
    'Premier League',  # Egito
    
    # Mundial
    'World Cup', 'Club World Cup',
]

print("\n" + "="*80)
print("🔴 PARTIDAS AO VIVO - LIGAS COM COBERTURA COMPLETA")
print("="*80 + "\n")

print("📡 Buscando partidas ao vivo...")
print("-"*80)

live_result = api.get_live_fixtures()

if not live_result['success']:
    print(f"❌ Erro: {live_result.get('error')}")
    exit(1)

all_fixtures = live_result['fixtures']
print(f"✅ {len(all_fixtures)} partidas ao vivo no total\n")

# Filtrar apenas ligas principais
major_fixtures = []

for fixture in all_fixtures:
    league_name = fixture['league']['name']
    
    # Verificar se é liga principal (match parcial para cobrir variações)
    is_major = any(
        major.lower() in league_name.lower() 
        for major in MAJOR_LEAGUES
    )
    
    if is_major:
        major_fixtures.append(fixture)

print("="*80)
print(f"🏆 {len(major_fixtures)} PARTIDAS AO VIVO DE LIGAS PRINCIPAIS")
print("="*80 + "\n")

if len(major_fixtures) == 0:
    print("⚠️  Nenhuma partida de liga principal ao vivo no momento")
    print()
    print("💡 DICA: As ligas principais geralmente têm jogos em:")
    print("   • Fins de semana (sábado e domingo)")
    print("   • Meio de semana (terça e quarta - Champions/Europa League)")
    print("   • Horários: 14h-22h (horário europeu) = 10h-18h (horário de Brasília)")
    print()
    print("📅 Todas as partidas ao vivo agora:")
    print("-"*80)
    
    for idx, fixture in enumerate(all_fixtures[:10], 1):
        home = fixture['teams']['home']['name']
        away = fixture['teams']['away']['name']
        league = fixture['league']['name']
        country = fixture['league'].get('country', '?')
        status = fixture['fixture']['status']['short']
        score_h = fixture['goals']['home'] or 0
        score_a = fixture['goals']['away'] or 0
        
        print(f"{idx:2d}. [{status}] {home} {score_h} x {score_a} {away}")
        print(f"    📍 {league} ({country})\n")
else:
    # Agrupar por liga
    by_league = {}
    
    for fixture in major_fixtures:
        league_key = f"{fixture['league'].get('country', 'Mundial')} - {fixture['league']['name']}"
        
        if league_key not in by_league:
            by_league[league_key] = []
        
        by_league[league_key].append(fixture)
    
    # Exibir por liga
    for league_key in sorted(by_league.keys()):
        fixtures = by_league[league_key]
        league_name = fixtures[0]['league']['name']
        league_country = fixtures[0]['league'].get('country', 'Mundial')
        
        print(f"🏁 {league_country.upper()} - {league_name}")
        print(f"   ({len(fixtures)} {'partida' if len(fixtures) == 1 else 'partidas'})")
        print("-"*80)
        
        for fixture in fixtures:
            fixture_id = fixture['fixture']['id']
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            status = fixture['fixture']['status']
            elapsed = status.get('elapsed', '?')
            score_h = fixture['goals']['home'] or 0
            score_a = fixture['goals']['away'] or 0
            venue = fixture['fixture'].get('venue', {}).get('name', 'N/A')
            
            # Status emoji
            status_short = status['short']
            if status_short == '1H':
                status_emoji = "⚽ 1º Tempo"
            elif status_short == 'HT':
                status_emoji = "⏸️  Intervalo"
            elif status_short == '2H':
                status_emoji = "⚽ 2º Tempo"
            elif status_short in ['ET', 'P']:
                status_emoji = "⏱️  Prorrogação"
            else:
                status_emoji = f"🔴 {status_short}"
            
            print(f"\n   [{fixture_id}] {home} {score_h} x {score_a} {away}")
            print(f"   {status_emoji} - {elapsed}' | 🏟️  {venue}")
            print(f"   🌐 http://localhost:3001/match/{fixture_id}")
        
        print()

print("\n" + "="*80)
print("📊 RESUMO")
print("="*80)
print(f"Total ao vivo: {len(all_fixtures)} partidas")
print(f"Ligas principais: {len(major_fixtures)} partidas")
print(f"Ligas sem cobertura: {len(all_fixtures) - len(major_fixtures)} partidas")
print()

if len(major_fixtures) > 0:
    print("✅ PARTIDAS RECOMENDADAS PARA ANÁLISE:")
    print("-"*80)
    for idx, fixture in enumerate(major_fixtures[:3], 1):
        fixture_id = fixture['fixture']['id']
        home = fixture['teams']['home']['name']
        away = fixture['teams']['away']['name']
        league = fixture['league']['name']
        
        print(f"{idx}. {home} vs {away} ({league})")
        print(f"   🔗 http://localhost:3001/match/{fixture_id}")
        print()

print("💡 Estas partidas têm:")
print("   ✅ Escalações completas")
print("   ✅ Estatísticas em tempo real")
print("   ✅ Eventos (gols, cartões, substituições)")
print("="*80 + "\n")
