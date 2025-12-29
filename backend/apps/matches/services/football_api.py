"""
Serviços de integração com APIs de futebol
Inclui API-Football e Football-Data.org
"""
import requests
from django.conf import settings
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class FootballAPIService:
    """Serviço para API-Football (api-sports.io)"""
    
    def __init__(self):
        self.api_key = settings.API_FOOTBALL_KEY
        self.base_url = settings.API_FOOTBALL_URL
        self.headers = {'x-apisports-key': self.api_key}
    
    def get_fixtures_by_date(self, date: str = None) -> Dict:
        """Buscar partidas por data"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            logger.info(f"Buscando partidas para {date}")
            response = requests.get(
                f'{self.base_url}/fixtures',
                headers=self.headers,
                params={'date': date},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'count': len(data.get('response', [])),
                'fixtures': data.get('response', [])
            }
        except Exception as e:
            logger.error(f"Erro ao buscar partidas: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_fixture_by_id(self, fixture_id: int) -> Dict:
        """Buscar detalhes de uma partida específica"""
        try:
            response = requests.get(
                f'{self.base_url}/fixtures',
                headers=self.headers,
                params={'id': fixture_id},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('response'):
                return {'success': True, 'fixture': data['response'][0]}
            return {'success': False, 'error': 'Partida não encontrada'}
        except Exception as e:
            logger.error(f"Erro ao buscar partida: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_predictions(self, fixture_id: int) -> Dict:
        """Buscar previsões e odds de uma partida"""
        try:
            response = requests.get(
                f'{self.base_url}/predictions',
                headers=self.headers,
                params={'fixture': fixture_id},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('response'):
                return {'success': True, 'predictions': data['response'][0]}
            return {'success': False, 'error': 'Previsões não disponíveis'}
        except Exception as e:
            logger.error(f"Erro ao buscar previsões: {e}")
            return {'success': False, 'error': str(e)}


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
