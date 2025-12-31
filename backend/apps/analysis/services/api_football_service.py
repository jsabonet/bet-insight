"""
Serviço para buscar dados adicionais da API-Football (RapidAPI)
Usado para enriquecer análises com contexto completo
"""
import requests
import logging
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class APIFootballService:
    """Serviço para buscar dados da API-Football com cache"""
    
    def __init__(self):
        self.base_url = settings.API_FOOTBALL_URL
        self.headers = {
            "x-apisports-key": settings.API_FOOTBALL_KEY
        }
        self.cache_ttl = getattr(settings, 'CACHE_TTL', {})
    
    def _get_cache_key(self, endpoint, params):
        """Gera chave única para cache baseada em endpoint e parâmetros"""
        sorted_params = sorted(params.items()) if params else []
        params_str = '_'.join([f"{k}={v}" for k, v in sorted_params])
        return f"api_football:{endpoint}:{params_str}"
    
    def _make_request(self, endpoint, params=None, cache_type=None):
        """Faz requisição para a API-Football com cache"""
        # Gerar chave de cache
        cache_key = self._get_cache_key(endpoint, params)
        
        # Tentar buscar do cache primeiro
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"📦 Cache HIT: {endpoint} (params: {params})")
            return cached_data
        
        # Se não estiver no cache, fazer requisição
        logger.info(f"🌐 Cache MISS: {endpoint} - Buscando da API...")
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            result = data.get('response', [])
            
            # Armazenar no cache com TTL apropriado
            ttl = self.cache_ttl.get(cache_type, 3600) if cache_type else 3600
            cache.set(cache_key, result, ttl)
            logger.info(f"✅ Armazenado no cache por {ttl}s")
            
            return result
        except Exception as e:
            logger.error(f"Erro ao buscar {endpoint}: {str(e)}")
            return None
    
    def fetch_standings(self, league_id, season=2025):
        """
        Busca classificação da liga
        
        Returns:
            dict: {
                'team_id': {
                    'position': int,
                    'points': int,
                    'form': str,  # 'WWDLL'
                    'goals_for': int,
                    'goals_against': int
                }
            }
        """
        logger.info(f"📊 Buscando standings - League: {league_id}, Season: {season}")
        
        data = self._make_request('standings', {'league': league_id, 'season': season}, cache_type='standings')
        
        if not data or not data[0].get('league', {}).get('standings'):
            logger.warning(f"⚠️ Standings não encontrados para league {league_id}")
            return {}
        
        standings_dict = {}
        for standing in data[0]['league']['standings'][0]:
            team_id = standing['team']['id']
            standings_dict[team_id] = {
                'position': standing['rank'],
                'points': standing['points'],
                'form': standing.get('form', ''),
                'goals_for': standing['all']['goals']['for'],
                'goals_against': standing['all']['goals']['against'],
                'goal_difference': standing['goalsDiff'],
                'home_record': f"W{standing['home']['win']}-D{standing['home']['draw']}-L{standing['home']['lose']}",
                'away_record': f"W{standing['away']['win']}-D{standing['away']['draw']}-L{standing['away']['lose']}"
            }
        
        logger.info(f"✅ {len(standings_dict)} times na tabela")
        return standings_dict
    
    def fetch_injuries(self, fixture_id):
        """
        Busca lesões e suspensões da partida
        
        Returns:
            dict: {
                'home': [{'player': str, 'reason': str, 'type': str}],
                'away': [...]
            }
        """
        logger.info(f"🚑 Buscando lesões - Fixture: {fixture_id}")
        
        data = self._make_request('injuries', {'fixture': fixture_id}, cache_type='injuries')
        
        if not data:
            logger.warning(f"⚠️ Nenhuma lesão encontrada para fixture {fixture_id}")
            return {'home': [], 'away': []}
        
        injuries = {'home': [], 'away': []}
        
        for injury in data:
            player_data = {
                'player': injury['player']['name'],
                'reason': injury['player']['reason'],
                'type': injury['player']['type']  # Missing, Suspended, etc
            }
            
            # Identificar time (home/away)
            # Como não temos info direta, vamos retornar tudo junto
            # O backend deverá separar por team_id
            if 'team' in injury:
                team_key = 'home' if injury['team'].get('home') else 'away'
                injuries[team_key].append(player_data)
        
        logger.info(f"✅ Lesões: {len(injuries['home'])} casa, {len(injuries['away'])} fora")
        return injuries
    
    def fetch_odds(self, fixture_id):
        """
        Busca odds das casas de apostas
        
        Returns:
            dict: {
                'home_win': float,
                'draw': float,
                'away_win': float,
                'over_25': float,
                'under_25': float,
                'btts_yes': float,
                'btts_no': float
            }
        """
        logger.info(f"💰 Buscando odds - Fixture: {fixture_id}")
        
        data = self._make_request('odds', {'fixture': fixture_id}, cache_type='odds')
        
        if not data or not data[0].get('bookmakers'):
            logger.warning(f"⚠️ Odds não encontradas para fixture {fixture_id}")
            return None
        
        odds_result = {}
        
        # Pegar odds da primeira bookmaker (geralmente Bet365)
        bookmaker = data[0]['bookmakers'][0]
        
        for bet_type in bookmaker['bets']:
            if bet_type['name'] == 'Match Winner':
                for value in bet_type['values']:
                    if value['value'] == 'Home':
                        odds_result['home_win'] = float(value['odd'])
                    elif value['value'] == 'Draw':
                        odds_result['draw'] = float(value['odd'])
                    elif value['value'] == 'Away':
                        odds_result['away_win'] = float(value['odd'])
            
            elif bet_type['name'] == 'Goals Over/Under':
                for value in bet_type['values']:
                    if '2.5' in value['value']:
                        if 'Over' in value['value']:
                            odds_result['over_25'] = float(value['odd'])
                        elif 'Under' in value['value']:
                            odds_result['under_25'] = float(value['odd'])
            
            elif bet_type['name'] == 'Both Teams Score':
                for value in bet_type['values']:
                    if value['value'] == 'Yes':
                        odds_result['btts_yes'] = float(value['odd'])
                    elif value['value'] == 'No':
                        odds_result['btts_no'] = float(value['odd'])
        
        logger.info(f"✅ Odds obtidas: {len(odds_result)} mercados")
        return odds_result
    
    def fetch_team_statistics(self, team_id, league_id, season=2025):
        """
        Busca estatísticas detalhadas do time
        
        Returns:
            dict: {
                'form': str,
                'goals_per_game_avg': float,
                'goals_conceded_avg': float,
                'clean_sheets': int,
                'btts_percentage': int,
                'over_25_percentage': int,
                'avg_corners': float
            }
        """
        logger.info(f"📈 Buscando estatísticas - Team: {team_id}, League: {league_id}")
        
        data = self._make_request('teams/statistics', {
            'team': team_id,
            'league': league_id,
            'season': season
        }, cache_type='team_statistics')
        
        if not data:
            logger.warning(f"⚠️ Estatísticas não encontradas para team {team_id}")
            return None
        
        fixtures = data.get('fixtures', {})
        goals = data.get('goals', {}).get('for', {}).get('total', {})
        
        stats = {
            'form': data.get('form', ''),
            'games_played': fixtures.get('played', {}).get('total', 0),
            'goals_per_game_avg': goals.get('average', {}).get('total', 0),
            'goals_conceded_avg': data.get('goals', {}).get('against', {}).get('average', {}).get('total', 0),
            'clean_sheets': data.get('clean_sheet', {}).get('total', 0),
            'biggest_streak': {
                'wins': data.get('biggest', {}).get('streak', {}).get('wins', 0),
                'draws': data.get('biggest', {}).get('streak', {}).get('draws', 0),
                'loses': data.get('biggest', {}).get('streak', {}).get('loses', 0)
            }
        }
        
        logger.info(f"✅ Estatísticas obtidas para team {team_id}")
        return stats
    
    def fetch_fixture_details(self, fixture_id):
        """
        Busca detalhes completos da partida
        
        Returns:
            dict: Informações detalhadas incluindo times, horário, venue, etc
        """
        logger.info(f"🏟️ Buscando detalhes - Fixture: {fixture_id}")
        
        data = self._make_request('fixtures', {'id': fixture_id}, cache_type='fixture_details')
        
        if not data:
            logger.warning(f"⚠️ Detalhes não encontrados para fixture {fixture_id}")
            return None
        
        fixture = data[0]
        
        details = {
            'fixture_id': fixture['fixture']['id'],
            'date': fixture['fixture']['date'],
            'venue': fixture['fixture']['venue']['name'],
            'referee': fixture['fixture']['referee'],
            'home_team': {
                'id': fixture['teams']['home']['id'],
                'name': fixture['teams']['home']['name'],
                'logo': fixture['teams']['home']['logo']
            },
            'away_team': {
                'id': fixture['teams']['away']['id'],
                'name': fixture['teams']['away']['name'],
                'logo': fixture['teams']['away']['logo']
            },
            'league': {
                'id': fixture['league']['id'],
                'name': fixture['league']['name'],
                'season': fixture['league']['season'],
                'round': fixture['league']['round']
            },
            'status': fixture['fixture']['status']['short']
        }
        
        logger.info(f"✅ Detalhes obtidos para fixture {fixture_id}")
        return details
    
    def fetch_team_fixtures(self, team_id, league_id=None, season=None, last=10):
        """
        Busca últimas fixtures de um time
        
        Args:
            team_id: ID do time
            league_id: ID da liga (opcional)
            season: Temporada (opcional)
            last: Número de fixtures (padrão: 10)
        
        Returns:
            list: Lista de fixtures com placares e resultados
        """
        logger.info(f"📅 Buscando últimas {last} fixtures do time {team_id}")
        
        params = {
            'team': team_id,
            'last': last,
            'status': 'FT'  # Apenas jogos finalizados
        }
        
        if league_id:
            params['league'] = league_id
        if season:
            params['season'] = season
        
        data = self._make_request('fixtures', params, cache_type='fixtures')
        
        if not data:
            logger.warning(f"⚠️ Nenhuma fixture encontrada para team {team_id}")
            return []
        
        fixtures = []
        for fixture in data:
            fixture_info = {
                'fixture_id': fixture['fixture']['id'],
                'date': fixture['fixture']['date'],
                'home_team_id': fixture['teams']['home']['id'],
                'away_team_id': fixture['teams']['away']['id'],
                'home_team': fixture['teams']['home']['name'],
                'away_team': fixture['teams']['away']['name'],
                'goals_home': fixture['goals']['home'],
                'goals_away': fixture['goals']['away'],
                'total_goals': fixture['goals']['home'] + fixture['goals']['away'],
                'is_home': fixture['teams']['home']['id'] == team_id,
                'result': None  # Será calculado abaixo
            }
            
            # Determinar resultado (do ponto de vista do time)
            if fixture_info['is_home']:
                if fixture_info['goals_home'] > fixture_info['goals_away']:
                    fixture_info['result'] = 'W'
                elif fixture_info['goals_home'] < fixture_info['goals_away']:
                    fixture_info['result'] = 'L'
                else:
                    fixture_info['result'] = 'D'
            else:
                if fixture_info['goals_away'] > fixture_info['goals_home']:
                    fixture_info['result'] = 'W'
                elif fixture_info['goals_away'] < fixture_info['goals_home']:
                    fixture_info['result'] = 'L'
                else:
                    fixture_info['result'] = 'D'
            
            # BTTS (Ambos marcaram)
            fixture_info['btts'] = fixture_info['goals_home'] > 0 and fixture_info['goals_away'] > 0
            
            # Over 2.5
            fixture_info['over_25'] = fixture_info['total_goals'] > 2.5
            
            fixtures.append(fixture_info)
        
        logger.info(f"✅ {len(fixtures)} fixtures obtidas")
        return fixtures
