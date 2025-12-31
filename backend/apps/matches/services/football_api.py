"""
Serviços de integração com APIs de futebol
Inclui API-Football e Football-Data.org
"""
import requests
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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
        # Sessão com retry/backoff para maior resiliência
        self.session: Session = requests.Session()
        self.session.headers.update(self.headers)
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
    
    def get_fixtures_by_date(self, date: str = None) -> Dict:
        """Buscar partidas por data"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            logger.info(f"Buscando partidas para {date}")
            response = self.session.get(
                f'{self.base_url}/fixtures',
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
        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, 'status_code', 500)
            logger.error(f"Erro HTTP ao buscar partidas: {e}")
            return {'success': False, 'error': 'Falha HTTP ao buscar partidas', 'details': str(e), 'http_status': status_code, 'error_code': 'HTTP_ERROR'}
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.error(f"Erro de rede ao buscar partidas: {e}")
            return {'success': False, 'error': 'Erro de rede ao buscar partidas', 'details': str(e), 'http_status': 503, 'error_code': 'NETWORK_ERROR'}
        except Exception as e:
            logger.error(f"Erro ao buscar partidas: {e}")
            return {'success': False, 'error': 'Erro desconhecido ao buscar partidas', 'details': str(e), 'http_status': 500, 'error_code': 'UNKNOWN_ERROR'}
    
    def get_fixtures_by_league(self, league_id: int, from_date: str = None, to_date: str = None, season: int = None, next_matches: int = 50) -> Dict:
        """Buscar partidas por liga"""
        try:
            params = {'league': league_id}
            
            # Usar from/to se fornecido
            if from_date and to_date:
                params['from'] = from_date
                params['to'] = to_date
                logger.info(f"Buscando partidas da liga {league_id} entre {from_date} e {to_date}")
            elif season:
                # Usar season
                params['season'] = season
                logger.info(f"Buscando partidas da liga {league_id} - temporada {season}")
            else:
                # Usar next
                params['next'] = next_matches
                logger.info(f"Buscando próximas {next_matches} partidas da liga {league_id}")
            
            response = self.session.get(
                f'{self.base_url}/fixtures',
                params=params,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'count': len(data.get('response', [])),
                'fixtures': data.get('response', [])
            }
        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, 'status_code', 500)
            logger.error(f"Erro HTTP ao buscar partidas da liga: {e}")
            return {'success': False, 'error': 'Falha HTTP ao buscar partidas da liga', 'details': str(e), 'http_status': status_code, 'error_code': 'HTTP_ERROR'}
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.error(f"Erro de rede ao buscar partidas da liga: {e}")
            return {'success': False, 'error': 'Erro de rede ao buscar partidas da liga', 'details': str(e), 'http_status': 503, 'error_code': 'NETWORK_ERROR'}
        except Exception as e:
            logger.error(f"Erro ao buscar partidas da liga: {e}")
            return {'success': False, 'error': 'Erro desconhecido ao buscar partidas da liga', 'details': str(e), 'http_status': 500, 'error_code': 'UNKNOWN_ERROR'}
    
    def get_live_fixtures(self) -> Dict:
        """Buscar partidas ao vivo"""
        try:
            logger.info("Buscando partidas ao vivo")
            response = self.session.get(
                f'{self.base_url}/fixtures',
                params={'live': 'all'},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'success': True,
                'count': len(data.get('response', [])),
                'fixtures': data.get('response', [])
            }
        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, 'status_code', 500)
            logger.error(f"Erro HTTP ao buscar partidas ao vivo: {e}")
            return {'success': False, 'error': 'Falha HTTP ao buscar partidas ao vivo', 'details': str(e), 'http_status': status_code, 'error_code': 'HTTP_ERROR'}
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.error(f"Erro de rede ao buscar partidas ao vivo: {e}")
            return {'success': False, 'error': 'Erro de rede ao buscar partidas ao vivo', 'details': str(e), 'http_status': 503, 'error_code': 'NETWORK_ERROR'}
        except Exception as e:
            logger.error(f"Erro ao buscar partidas ao vivo: {e}")
            return {'success': False, 'error': 'Erro desconhecido ao buscar partidas ao vivo', 'details': str(e), 'http_status': 500, 'error_code': 'UNKNOWN_ERROR'}
    
    def get_fixture_by_id(self, fixture_id: int) -> Dict:
        """Buscar detalhes de uma partida específica"""
        try:
            response = self.session.get(
                f'{self.base_url}/fixtures',
                params={'id': fixture_id},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('response'):
                return {'success': True, 'fixture': data['response'][0]}
            return {'success': False, 'error': 'Partida não encontrada'}
        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, 'status_code', 500)
            logger.error(f"Erro HTTP ao buscar partida: {e}")
            return {'success': False, 'error': 'Falha HTTP ao buscar partida', 'details': str(e), 'http_status': status_code, 'error_code': 'HTTP_ERROR'}
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.error(f"Erro de rede ao buscar partida: {e}")
            return {'success': False, 'error': 'Erro de rede ao buscar partida', 'details': str(e), 'http_status': 503, 'error_code': 'NETWORK_ERROR'}
        except Exception as e:
            logger.error(f"Erro ao buscar partida: {e}")
            return {'success': False, 'error': 'Erro desconhecido ao buscar partida', 'details': str(e), 'http_status': 500, 'error_code': 'UNKNOWN_ERROR'}
    
    def get_fixture_statistics(self, fixture_id: int) -> Dict:
        """Buscar estatísticas de uma partida específica"""
        try:
            response = self.session.get(
                f'{self.base_url}/fixtures/statistics',
                params={'fixture': fixture_id},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('response'):
                return {'success': True, 'statistics': data['response']}
            return {'success': False, 'error': 'Estatísticas não disponíveis'}
        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, 'status_code', 500)
            logger.error(f"Erro HTTP ao buscar estatísticas: {e}")
            return {'success': False, 'error': 'Falha HTTP ao buscar estatísticas', 'details': str(e), 'http_status': status_code, 'error_code': 'HTTP_ERROR'}
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.error(f"Erro de rede ao buscar estatísticas: {e}")
            return {'success': False, 'error': 'Erro de rede ao buscar estatísticas', 'details': str(e), 'http_status': 503, 'error_code': 'NETWORK_ERROR'}
        except Exception as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            return {'success': False, 'error': 'Erro desconhecido ao buscar estatísticas', 'details': str(e), 'http_status': 500, 'error_code': 'UNKNOWN_ERROR'}
    
    def get_predictions(self, fixture_id: int) -> Dict:
        """Buscar previsões e odds de uma partida"""
        try:
            response = self.session.get(
                f'{self.base_url}/predictions',
                params={'fixture': fixture_id},
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('response'):
                return {'success': True, 'predictions': data['response'][0]}
            return {'success': False, 'error': 'Previsões não disponíveis'}
        except requests.exceptions.HTTPError as e:
            status_code = getattr(e.response, 'status_code', 500)
            logger.error(f"Erro HTTP ao buscar previsões: {e}")
            return {'success': False, 'error': 'Falha HTTP ao buscar previsões', 'details': str(e), 'http_status': status_code, 'error_code': 'HTTP_ERROR'}
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.error(f"Erro de rede ao buscar previsões: {e}")
            return {'success': False, 'error': 'Erro de rede ao buscar previsões', 'details': str(e), 'http_status': 503, 'error_code': 'NETWORK_ERROR'}
        except Exception as e:
            logger.error(f"Erro ao buscar previsões: {e}")
            return {'success': False, 'error': 'Erro desconhecido ao buscar previsões', 'details': str(e), 'http_status': 500, 'error_code': 'UNKNOWN_ERROR'}


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
