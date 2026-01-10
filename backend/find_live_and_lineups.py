"""
Buscar partidas AO VIVO e partidas com LINEUPS disponíveis
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from datetime import datetime, timedelta

# Inicializar serviço
api = FootballAPIService()

print("\n" + "="*80)
print("🔍 BUSCANDO PARTIDAS AO VIVO E COM LINEUPS")
print("="*80 + "\n")

# 1. BUSCAR PARTIDAS AO VIVO
print("1️⃣ PARTIDAS AO VIVO AGORA:")
print("-"*80)

live_result = api.get_live_fixtures()

if live_result['success']:
    live_fixtures = live_result['fixtures']
    print(f"✅ {len(live_fixtures)} partidas ao vivo encontradas\n")
    
    if len(live_fixtures) > 0:
        for idx, fixture in enumerate(live_fixtures[:5], 1):  # Mostrar primeiras 5
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            score_home = fixture['goals']['home'] or 0
            score_away = fixture['goals']['away'] or 0
            status = fixture['fixture']['status']['elapsed']
            fixture_id = fixture['fixture']['id']
            
            print(f"   {idx}. [{fixture_id}] {home} {score_home} x {score_away} {away}")
            print(f"      ⏱️  {status}' - Status: {fixture['fixture']['status']['short']}")
            print()
    else:
        print("   ⚠️  Nenhuma partida ao vivo no momento\n")
else:
    print(f"   ❌ Erro: {live_result.get('error')}\n")

# 2. BUSCAR PARTIDAS RECENTES (últimas 3 horas) - maior chance de ter lineups
print("\n2️⃣ PARTIDAS RECENTES (últimas 3h) - COM LINEUPS:")
print("-"*80)

# Buscar partidas de hoje
today = datetime.now().strftime('%Y-%m-%d')
fixtures_result = api.get_fixtures_by_date(today)

if fixtures_result['success']:
    fixtures = fixtures_result['fixtures']
    print(f"✅ {len(fixtures)} partidas de hoje encontradas\n")
    
    # Filtrar partidas que já aconteceram ou estão em andamento
    now = datetime.now()
    recent_fixtures = []
    
    for fixture in fixtures:
        fixture_date = datetime.fromisoformat(fixture['fixture']['date'].replace('Z', '+00:00'))
        time_diff = (now - fixture_date.replace(tzinfo=None)).total_seconds() / 3600
        
        # Partidas que começaram nas últimas 6 horas ou estão ao vivo
        status = fixture['fixture']['status']['short']
        if time_diff >= -1 and time_diff <= 6:  # -1h até +6h
            recent_fixtures.append(fixture)
    
    print(f"   📊 {len(recent_fixtures)} partidas recentes/em andamento\n")
    
    if len(recent_fixtures) > 0:
        # Verificar lineups para as primeiras 5
        for idx, fixture in enumerate(recent_fixtures[:5], 1):
            fixture_id = fixture['fixture']['id']
            home = fixture['teams']['home']['name']
            away = fixture['teams']['away']['name']
            status = fixture['fixture']['status']['short']
            
            # Tentar buscar lineups
            lineups_result = api.get_fixture_lineups(fixture_id)
            
            has_lineups = lineups_result['success'] and len(lineups_result.get('lineups', [])) > 0
            
            status_emoji = "🟢" if status in ['1H', '2H', 'HT', 'ET', 'P', 'LIVE'] else "⚪" if status == 'FT' else "🔵"
            lineups_emoji = "✅" if has_lineups else "❌"
            
            print(f"   {idx}. {status_emoji} [{fixture_id}] {home} vs {away}")
            print(f"      Status: {status} | Lineups: {lineups_emoji}")
            
            if has_lineups:
                lineups = lineups_result['lineups']
                for lineup in lineups:
                    team = lineup['team']['name']
                    formation = lineup.get('formation', 'N/A')
                    print(f"         {team}: {formation}")
            print()
    else:
        print("   ⚠️  Nenhuma partida recente encontrada\n")
else:
    print(f"   ❌ Erro: {fixtures_result.get('error')}\n")

# 3. BUSCAR PARTIDAS DE ONTEM (mais garantia de ter lineups)
print("\n3️⃣ PARTIDAS DE ONTEM - LINEUPS GARANTIDOS:")
print("-"*80)

yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
yesterday_result = api.get_fixtures_by_date(yesterday)

if yesterday_result['success']:
    fixtures = yesterday_result['fixtures']
    print(f"✅ {len(fixtures)} partidas de ontem encontradas\n")
    
    # Verificar lineups para as primeiras 3
    fixtures_with_lineups = []
    
    for fixture in fixtures[:10]:  # Verificar primeiras 10
        fixture_id = fixture['fixture']['id']
        lineups_result = api.get_fixture_lineups(fixture_id)
        
        if lineups_result['success'] and len(lineups_result.get('lineups', [])) > 0:
            fixtures_with_lineups.append({
                'fixture': fixture,
                'lineups': lineups_result['lineups']
            })
            
            if len(fixtures_with_lineups) >= 3:  # Parar após encontrar 3
                break
    
    print(f"   📋 {len(fixtures_with_lineups)} partidas com lineups disponíveis\n")
    
    for idx, item in enumerate(fixtures_with_lineups, 1):
        fixture = item['fixture']
        lineups = item['lineups']
        
        fixture_id = fixture['fixture']['id']
        home = fixture['teams']['home']['name']
        away = fixture['teams']['away']['name']
        score_home = fixture['goals']['home']
        score_away = fixture['goals']['away']
        
        print(f"   {idx}. ✅ [{fixture_id}] {home} {score_home} x {score_away} {away}")
        
        for lineup in lineups:
            team = lineup['team']['name']
            formation = lineup.get('formation', 'N/A')
            startXI = len(lineup.get('startXI', []))
            subs = len(lineup.get('substitutes', []))
            print(f"         {team}: {formation} ({startXI} titulares, {subs} reservas)")
        print()
else:
    print(f"   ❌ Erro: {yesterday_result.get('error')}\n")

print("="*80)
print("🎯 RECOMENDAÇÕES:")
print("="*80)
print("📍 Para testar PARTIDAS AO VIVO:")
print("   Use os IDs das partidas da seção 1️⃣ acima")
print()
print("📍 Para testar LINEUPS:")
print("   Use os IDs marcados com ✅ das seções 2️⃣ ou 3️⃣")
print()
print("🌐 Acesse no navegador:")
print("   http://localhost:3001/match/{FIXTURE_ID}")
print("="*80 + "\n")
