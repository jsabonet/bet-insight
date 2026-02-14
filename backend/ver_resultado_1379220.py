"""
Ver resultado da partida 1379220
"""
import os
import django
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService

def main():
    match_id = 1379220
    
    api = APIFootballService()
    fixture = api.fetch_fixture_details(match_id)
    
    if not fixture:
        print("Partida não encontrada")
        return
    
    print("\n" + "="*80)
    print(f"PARTIDA {match_id}")
    print("="*80 + "\n")
    
    teams = fixture.get('teams', {})
    home = teams.get('home', {}).get('name', 'Casa')
    away = teams.get('away', {}).get('name', 'Fora')
    
    league = fixture.get('league', {})
    league_name = league.get('name', 'N/A')
    
    fixture_data = fixture.get('fixture', {})
    date = fixture_data.get('date', 'N/A')
    status = fixture_data.get('status', {})
    status_short = status.get('short', 'NS')
    status_long = status.get('long', 'Not Started')
    
    goals = fixture.get('goals', {})
    home_goals = goals.get('home')
    away_goals = goals.get('away')
    
    print(f"Partida: {home} vs {away}")
    print(f"Liga: {league_name}")
    print(f"Data: {date}")
    print(f"Status: {status_long} ({status_short})")
    
    if home_goals is not None and away_goals is not None:
        print(f"\nPLACAR: {home} {home_goals} - {away_goals} {away}")
        total_goals = home_goals + away_goals
        
        print(f"\n✅ Total de gols: {total_goals}")
        print(f"✅ Over 2.5: {'GREEN' if total_goals > 2.5 else 'RED'}")
        print(f"✅ BTTS: {'GREEN' if home_goals > 0 and away_goals > 0 else 'RED'}")
        
        if home_goals > away_goals:
            print(f"✅ Resultado: Casa venceu")
        elif away_goals > home_goals:
            print(f"✅ Resultado: Fora venceu")
        else:
            print(f"✅ Resultado: Empate")
    else:
        print(f"\n⏳ Partida ainda não foi realizada")
    
    print("\n" + "="*80 + "\n")

if __name__ == '__main__':
    main()
