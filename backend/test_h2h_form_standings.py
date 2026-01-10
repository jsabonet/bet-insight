"""
Investigar endpoints da API-Football para H2H, Form e Standings
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
import json

api = FootballAPIService()

print("\n" + "="*80)
print("🔍 INVESTIGANDO DADOS DISPONÍVEIS NA API-FOOTBALL")
print("="*80 + "\n")

# IDs para teste (Getafe vs Real Sociedad - La Liga)
fixture_id = 1391001
team1_id = 546  # Getafe
team2_id = 548  # Real Sociedad
league_id = 140  # La Liga
season = 2025

# 1. HEAD TO HEAD (H2H)
print("1️⃣ HEAD TO HEAD (H2H):")
print("-"*80)

try:
    response = api.session.get(
        f'{api.base_url}/fixtures/headtohead',
        params={
            'h2h': f'{team1_id}-{team2_id}',
            'last': 10  # Últimos 10 confrontos
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        fixtures = data.get('response', [])
        
        print(f"✅ Endpoint funciona!")
        print(f"📊 Total de confrontos encontrados: {len(fixtures)}")
        
        if len(fixtures) > 0:
            print(f"\nPrimeiro confronto:")
            match = fixtures[0]
            print(f"   {match['teams']['home']['name']} {match['goals']['home']} x {match['goals']['away']} {match['teams']['away']['name']}")
            print(f"   Data: {match['fixture']['date'][:10]}")
            print(f"   Liga: {match['league']['name']}")
    else:
        print(f"❌ Erro: {response.status_code}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

# 2. ÚLTIMOS JOGOS DO TIME (FORM)
print("\n\n2️⃣ ÚLTIMOS JOGOS DO TIME:")
print("-"*80)

try:
    response = api.session.get(
        f'{api.base_url}/fixtures',
        params={
            'team': team1_id,
            'last': 5,
            'season': season
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        fixtures = data.get('response', [])
        
        print(f"✅ Endpoint funciona!")
        print(f"📊 Últimos jogos de Getafe: {len(fixtures)}")
        
        if len(fixtures) > 0:
            print(f"\nÚltimo jogo:")
            match = fixtures[0]
            print(f"   {match['teams']['home']['name']} {match['goals']['home']} x {match['goals']['away']} {match['teams']['away']['name']}")
            print(f"   Data: {match['fixture']['date'][:10]}")
    else:
        print(f"❌ Erro: {response.status_code}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

# 3. CLASSIFICAÇÃO (STANDINGS)
print("\n\n3️⃣ CLASSIFICAÇÃO NA LIGA:")
print("-"*80)

try:
    response = api.session.get(
        f'{api.base_url}/standings',
        params={
            'league': league_id,
            'season': season
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        standings = data.get('response', [])
        
        print(f"✅ Endpoint funciona!")
        
        if len(standings) > 0:
            league_standings = standings[0].get('league', {}).get('standings', [[]])[0]
            
            # Encontrar Getafe e Real Sociedad
            for team in league_standings:
                if team['team']['id'] in [team1_id, team2_id]:
                    print(f"\n{team['rank']}º - {team['team']['name']}")
                    print(f"   Pontos: {team['points']} | V: {team['all']['win']} E: {team['all']['draw']} D: {team['all']['lose']}")
                    print(f"   Forma: {team['form']}")
    else:
        print(f"❌ Erro: {response.status_code}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n\n" + "="*80)
print("📋 ESTRUTURA DOS DADOS:")
print("="*80)

print("""
✅ H2H (Head to Head):
   Endpoint: /fixtures/headtohead
   Params: { h2h: 'team1-team2', last: 10 }
   Retorna: Lista de partidas entre os times

✅ Últimos Jogos:
   Endpoint: /fixtures
   Params: { team: team_id, last: 5, season: year }
   Retorna: Últimos 5 jogos do time

✅ Classificação:
   Endpoint: /standings
   Params: { league: league_id, season: year }
   Retorna: Tabela completa da liga

💡 TODOS OS ENDPOINTS ESTÃO DISPONÍVEIS!
""")

print("="*80 + "\n")
