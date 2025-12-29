import requests
from django.conf import settings
from datetime import datetime, timedelta


class FootballDataService:
    """Serviço para Football-Data.org API"""
    
    BASE_URL = "https://api.football-data.org/v4"
    
    def __init__(self):
        self.api_key = settings.FOOTBALL_DATA_API_KEY
        self.headers = {'X-Auth-Token': self.api_key}
    
    def get_upcoming_matches(self, days=7):
        """Buscar partidas futuras"""
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        url = f"{self.BASE_URL}/matches"
        params = {
            'dateFrom': date_from,
            'dateTo': date_to,
            'status': 'SCHEDULED'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar partidas: {e}")
            return None
    
    def get_match_details(self, match_id):
        """Buscar detalhes de uma partida"""
        url = f"{self.BASE_URL}/matches/{match_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar detalhes da partida: {e}")
            return None
    
    def get_team_stats(self, team_id):
        """Buscar estatísticas de um time"""
        url = f"{self.BASE_URL}/teams/{team_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar estatísticas do time: {e}")
            return None
    
    def get_h2h(self, match_id):
        """Buscar histórico direto (H2H)"""
        url = f"{self.BASE_URL}/matches/{match_id}/head2head"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar H2H: {e}")
            return None
