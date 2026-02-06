"""
Verificar resultado real da partida 1508602
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService
import requests
import json

fixture_id = 1508602

# Tentar buscar direto da API
api = APIFootballService()

# Buscar detalhes completos
url = f"https://v3.football.api-sports.io/fixtures?id={fixture_id}"
headers = {
    'x-rapidapi-host': 'v3.football.api-sports.io',
    'x-rapidapi-key': os.getenv('APIFOOTBALL_KEY')
}

print(f"\nBuscando partida {fixture_id} diretamente da API...")
print("="*80)

response = requests.get(url, headers=headers)
data = response.json()

if data.get('response') and len(data['response']) > 0:
    fixture = data['response'][0]
    
    # Informações básicas
    teams = fixture.get('teams', {})
    home = teams.get('home', {}).get('name', 'N/A')
    away = teams.get('away', {}).get('name', 'N/A')
    
    # Placar
    goals = fixture.get('goals', {})
    home_score = goals.get('home')
    away_score = goals.get('away')
    
    # Status
    status = fixture.get('fixture', {}).get('status', {})
    status_short = status.get('short', 'N/A')
    status_long = status.get('long', 'N/A')
    
    # Data
    date = fixture.get('fixture', {}).get('date', 'N/A')
    
    # Liga
    league_info = fixture.get('league', {})
    league_name = league_info.get('name', 'N/A')
    round_info = league_info.get('round', 'N/A')
    
    print(f"\nPARTIDA: {home} vs {away}")
    print(f"LIGA: {league_name}")
    print(f"RODADA: {round_info}")
    print(f"DATA: {date}")
    print(f"STATUS: {status_long} ({status_short})")
    
    if home_score is not None and away_score is not None:
        print(f"\nPLACAR FINAL: {home} {home_score} x {away_score} {away}")
        
        if home_score > away_score:
            result = f"Vitoria {home}"
        elif away_score > home_score:
            result = f"Vitoria {away}"
        else:
            result = "Empate"
        
        print(f"RESULTADO: {result}")
        
        # Estatísticas se disponíveis
        stats = fixture.get('score', {})
        halftime = stats.get('halftime', {})
        fulltime = stats.get('fulltime', {})
        
        if halftime.get('home') is not None:
            print(f"\nINTERVALO: {home} {halftime.get('home')} x {halftime.get('away')} {away}")
        
        if fulltime.get('home') is not None:
            print(f"TEMPO NORMAL: {home} {fulltime.get('home')} x {fulltime.get('away')} {away}")
        
        # Pênaltis se houver
        penalty = stats.get('penalty', {})
        if penalty.get('home') is not None:
            print(f"PENALTIS: {home} {penalty.get('home')} x {penalty.get('away')} {away}")
        
        # Extra time se houver
        extratime = stats.get('extratime', {})
        if extratime.get('home') is not None:
            print(f"PRORROGACAO: {home} {extratime.get('home')} x {extratime.get('away')} {away}")
            
    else:
        print(f"\nPLACAR: Nao disponivel")
        print(f"Partida pode nao ter sido finalizada ou dados incompletos")
    
    # Exibir JSON completo para debug
    print(f"\n" + "="*80)
    print("JSON COMPLETO (goals e score):")
    print("="*80)
    print(f"goals: {json.dumps(goals, indent=2)}")
    print(f"score: {json.dumps(stats, indent=2)}")
    
else:
    print("Nenhum dado retornado pela API")
    print(f"Response: {json.dumps(data, indent=2)[:500]}")
