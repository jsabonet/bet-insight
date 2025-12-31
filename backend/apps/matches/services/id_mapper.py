"""
Serviço para mapear IDs entre API-Football e Football-Data.org
Como as APIs usam sistemas de ID diferentes, fazemos lookup por time + data
"""
import logging
from datetime import datetime, timedelta
from django.conf import settings
import requests
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class APIIDMapper:
    """Mapeia IDs entre API-Football e Football-Data.org usando similaridade de nomes"""
    
    BASE_URL = "https://api.football-data.org/v4"
    
    def __init__(self):
        self.api_key = settings.FOOTBALL_DATA_API_KEY
        self.headers = {'X-Auth-Token': self.api_key}
    
    def similarity(self, a, b):
        """Calcula similaridade entre duas strings (0-1)"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def normalize_team_name(self, name):
        """Normaliza nomes de times para melhor matching"""
        # Remove palavras comuns que variam entre APIs
        replacements = {
            'fc': '',
            'sc': '',
            'ac': '',
            'cf': '',
            'ud': '',
            'cd': '',
            'afc': '',
            'bfc': '',
            '.': '',
            '-': ' ',
            '  ': ' '
        }
        
        normalized = name.lower().strip()
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        return normalized.strip()
    
    def find_football_data_id(self, home_team, away_team, match_date):
        """
        Busca o football_data_id correspondente ao jogo usando times e data
        
        Args:
            home_team (str): Nome do time da casa (da API-Football)
            away_team (str): Nome do time visitante (da API-Football)
            match_date (datetime): Data do jogo
            
        Returns:
            int or None: football_data_id se encontrado, None caso contrário
        """
        try:
            # Buscar jogos num intervalo de +/- 1 dia (para lidar com timezone)
            date_from = (match_date - timedelta(days=1)).strftime('%Y-%m-%d')
            date_to = (match_date + timedelta(days=1)).strftime('%Y-%m-%d')
            
            url = f"{self.BASE_URL}/matches"
            params = {
                'dateFrom': date_from,
                'dateTo': date_to
            }
            
            logger.info(f"🔍 [ID Mapper] Buscando jogo: {home_team} vs {away_team} em {match_date.strftime('%Y-%m-%d')}")
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('matches'):
                logger.warning(f"⚠️ [ID Mapper] Nenhum jogo encontrado no período")
                return None
            
            # Normalizar nomes dos times para comparação
            home_normalized = self.normalize_team_name(home_team)
            away_normalized = self.normalize_team_name(away_team)
            
            logger.info(f"🔍 [ID Mapper] Times normalizados: '{home_normalized}' vs '{away_normalized}'")
            
            best_match = None
            best_score = 0.0
            
            # Procurar o jogo que melhor corresponde
            for match in data['matches']:
                fd_home = match['homeTeam']['name']
                fd_away = match['awayTeam']['name']
                
                fd_home_normalized = self.normalize_team_name(fd_home)
                fd_away_normalized = self.normalize_team_name(fd_away)
                
                # Calcular similaridade para ambos os times
                home_sim = self.similarity(home_normalized, fd_home_normalized)
                away_sim = self.similarity(away_normalized, fd_away_normalized)
                
                # Score médio de similaridade
                avg_score = (home_sim + away_sim) / 2
                
                logger.debug(f"   Comparando: '{fd_home}' vs '{fd_away}' - Score: {avg_score:.2f}")
                
                # Se encontrou match com alta confiança (>0.7 = 70%)
                if avg_score > best_score and avg_score > 0.7:
                    best_score = avg_score
                    best_match = match
            
            if best_match:
                football_data_id = best_match['id']
                logger.info(f"✅ [ID Mapper] Match encontrado! football_data_id={football_data_id} (score: {best_score:.2%})")
                logger.info(f"   📋 {best_match['homeTeam']['name']} vs {best_match['awayTeam']['name']}")
                return football_data_id
            else:
                logger.warning(f"❌ [ID Mapper] Nenhum match com confiança suficiente (melhor score: {best_score:.2%})")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [ID Mapper] Erro na requisição: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ [ID Mapper] Erro inesperado: {e}", exc_info=True)
            return None
    
    def populate_football_data_id(self, match_obj):
        """
        Popula o football_data_id num objeto Match do Django
        
        Args:
            match_obj: Instância do modelo Match
            
        Returns:
            bool: True se populado com sucesso, False caso contrário
        """
        # Se já tem football_data_id, não precisa buscar
        if match_obj.football_data_id:
            logger.info(f"ℹ️ [ID Mapper] Match {match_obj.id} já tem football_data_id={match_obj.football_data_id}")
            return True
        
        # Buscar football_data_id
        football_data_id = self.find_football_data_id(
            home_team=match_obj.home_team,
            away_team=match_obj.away_team,
            match_date=match_obj.match_date
        )
        
        if football_data_id:
            match_obj.football_data_id = football_data_id
            match_obj.save(update_fields=['football_data_id'])
            logger.info(f"✅ [ID Mapper] Match {match_obj.id} atualizado com football_data_id={football_data_id}")
            return True
        else:
            logger.warning(f"⚠️ [ID Mapper] Não foi possível encontrar football_data_id para Match {match_obj.id}")
            return False
