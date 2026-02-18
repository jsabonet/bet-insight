import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService

# IDs das principais ligas
TOP_LEAGUES = [
    39,   # Premier League
    140,  # La Liga
    135,  # Serie A
    78,   # Bundesliga
    61,   # Ligue 1
    94,   # Primeira Liga
    88,   # Eredivisie
    144,  # Jupiler Pro League
    203,  # Süper Lig
    2,    # Champions League
    3,    # Europa League
    848,  # Conference League
    45,   # FA Cup
    137,  # Copa del Rey
]

LEAGUE_NAMES = {
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

def buscar_partidas_hoje():
    api = APIFootballService()
    
    # Buscar próximos 3 dias
    today = datetime.now()
    dates_to_search = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(3)]
    
    all_fixtures = []
    
    print("=" * 80)
    print("🔍 BUSCANDO PARTIDAS")
    print("=" * 80)
    
    for date_str in dates_to_search:
        print(f"\n📅 Data: {date_str}")
        print("-" * 80)
        
        for league_id in TOP_LEAGUES:
            response = api.get_fixtures_by_date(date_str, league_id=league_id, season=2025)
            
            if response and response.get('response'):
                fixtures = response['response']
                if fixtures:
                    league_name = LEAGUE_NAMES.get(league_id, f"Liga {league_id}")
                    print(f"\n🏆 {league_name} - {len(fixtures)} partida(s)")
                    
                    for fixture in fixtures:
                        fixture_data = fixture.get('fixture', {})
                        teams = fixture.get('teams', {})
                        league_info = fixture.get('league', {})
                        
                        fixture_id = fixture_data.get('id')
                        home_team = teams.get('home', {}).get('name', 'N/A')
                        away_team = teams.get('away', {}).get('name', 'N/A')
                        match_date = fixture_data.get('date', 'N/A')
                        status = fixture_data.get('status', {}).get('short', 'NS')
                        round_info = league_info.get('round', 'N/A')
                        
                        # Converter data para formato legível
                        try:
                            dt = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
                            time_str = dt.strftime('%H:%M')
                        except:
                            time_str = 'N/A'
                        
                        print(f"   ⚽ {home_team} vs {away_team}")
                        print(f"      Horário: {time_str} | Status: {status} | Rodada: {round_info}")
                        
                        all_fixtures.append({
                            'id': fixture_id,
                            'home': home_team,
                            'away': away_team,
                            'league': league_name,
                            'date': match_date,
                            'status': status
                        })
    
    print("\n" + "=" * 80)
    print(f"📊 RESUMO")
    print("=" * 80)
    print(f"Total de partidas encontradas: {len(all_fixtures)}")
    
    # Agrupar por status
    status_count = {}
    for fixture in all_fixtures:
        status = fixture['status']
        status_count[status] = status_count.get(status, 0) + 1
    
    print("\nPartidas por status:")
    for status, count in status_count.items():
        status_name = {
            'NS': 'Não iniciada',
            'TBD': 'A definir',
            'LIVE': 'Ao vivo',
            'FT': 'Finalizada',
            'PST': 'Adiada',
            'CANC': 'Cancelada'
        }.get(status, status)
        print(f"  {status_name}: {count}")
    
    # Agrupar por liga
    league_count = {}
    for fixture in all_fixtures:
        league = fixture['league']
        league_count[league] = league_count.get(league, 0) + 1
    
    print("\nPartidas por liga:")
    for league, count in sorted(league_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {league}: {count}")
    
    print("=" * 80)
    
    return all_fixtures

if __name__ == '__main__':
    fixtures = buscar_partidas_hoje()
