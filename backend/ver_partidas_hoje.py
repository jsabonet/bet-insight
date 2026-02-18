"""
Script simples para buscar partidas do dia
"""
import requests
from datetime import datetime, timedelta

API_KEY = '96f5a59919eb0648a28a5bcd06d5d98e'
BASE_URL = 'https://v3.football.api-sports.io'

TOP_LEAGUES = {
    39: "Premier League",
    140: "La Liga",
    135: "Serie A",
    78: "Bundesliga",
    61: "Ligue 1",
    94: "Primeira Liga",
    88: "Eredivisie",
    144: "Jupiler Pro League",
    203: "Süper Lig",
    2: "Champions League",
    3: "Europa League",
    848: "Conference League",
    45: "FA Cup",
    137: "Copa del Rey",
}

def buscar_partidas():
    headers = {
        'x-apisports-key': API_KEY
    }
    
    today = datetime.now()
    all_fixtures = []
    
    print("\n" + "=" * 80)
    print("🔍 PARTIDAS ENCONTRADAS (Próximos 3 dias)")
    print("=" * 80 + "\n")
    
    for i in range(3):
        date = today + timedelta(days=i)
        date_str = date.strftime('%Y-%m-%d')
        
        print(f"📅 {date.strftime('%d/%m/%Y')} ({date.strftime('%A')})")
        print("-" * 80)
        
        day_count = 0
        
        for league_id, league_name in TOP_LEAGUES.items():
            try:
                url = f"{BASE_URL}/fixtures"
                params = {
                    'date': date_str,
                    'league': league_id,
                    'season': 2025
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                data = response.json()
                
                if data.get('response'):
                    fixtures = data['response']
                    
                    if fixtures:
                        print(f"\n🏆 {league_name} ({len(fixtures)} partida{'s' if len(fixtures) > 1 else ''})")
                        
                        for fixture in fixtures:
                            fixture_data = fixture.get('fixture', {})
                            teams = fixture.get('teams', {})
                            
                            home_team = teams.get('home', {}).get('name', 'N/A')
                            away_team = teams.get('away', {}).get('name', 'N/A')
                            match_date = fixture_data.get('date', '')
                            
                            try:
                                dt = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
                                time_str = dt.strftime('%H:%M')
                            except:
                                time_str = 'N/A'
                            
                            print(f"   ⚽ {home_team} vs {away_team} - {time_str}")
                            all_fixtures.append(fixture)
                            day_count += 1
                        
            except Exception as e:
                pass  # Silenciar erros
        
        if day_count == 0:
            print("   Nenhuma partida encontrada")
        
        print()
    
    print("=" * 80)
    print(f"📊 TOTAL: {len(all_fixtures)} partidas encontradas")
    print("=" * 80 + "\n")
    
    return all_fixtures

if __name__ == '__main__':
    partidas = buscar_partidas()
