"""
Serviço de análise de forma recente com contexto de adversários
FASE 2: Forma Recente com Adversários
"""
import logging
from typing import Dict, List
from .api_football_service import APIFootballService

logger = logging.getLogger(__name__)


class FormAnalysisService:
    """Analisa forma recente dos times considerando força dos adversários"""
    
    def __init__(self):
        self.api_service = APIFootballService()
    
    def analyze_recent_form(self, team_id: int, league_id: int, season: int = 2025, last_n: int = 5) -> Dict:
        """
        Analisa últimos N jogos do time com contexto de adversários
        
        Args:
            team_id: ID do time
            league_id: ID da liga
            season: Temporada
            last_n: Número de jogos a analisar (padrão: 5)
        
        Returns:
            dict: {
                'games': [
                    {
                        'date': str,
                        'opponent': str,
                        'opponent_position': int,
                        'venue': str,  # 'Casa' ou 'Fora'
                        'score': str,  # '2-1'
                        'result': str,  # 'W', 'D', 'L'
                        'goals_scored': int,
                        'goals_conceded': int
                    }
                ],
                'summary': {
                    'wins': int,
                    'draws': int,
                    'losses': int,
                    'goals_scored': int,
                    'goals_conceded': int,
                    'points': int,
                    'strength_of_schedule': float,  # 0-10
                    'avg_opponent_position': float
                }
            }
        """
        logger.info(f"📊 Analisando forma recente - Team: {team_id}, Últimos {last_n} jogos")
        
        # Buscar fixtures recentes
        fixtures = self.api_service.fetch_team_fixtures(
            team_id=team_id,
            league_id=league_id,
            season=season,
            last=last_n
        )
        
        if not fixtures:
            logger.warning(f"⚠️ Nenhum jogo encontrado para team {team_id}")
            return self._empty_form_result()
        
        # Buscar classificação para contextualizar adversários
        standings = self.api_service.fetch_standings(league_id, season)
        
        # Processar cada jogo
        games = []
        wins = draws = losses = 0
        total_goals_scored = total_goals_conceded = 0
        opponent_positions = []
        
        for fixture in fixtures:
            # Determinar adversário
            if fixture['is_home']:
                opponent_id = fixture['away_team_id']
                opponent_name = fixture['away_team']
                venue = 'Casa'
                goals_scored = fixture['goals_home']
                goals_conceded = fixture['goals_away']
                score = f"{goals_scored}-{goals_conceded}"
            else:
                opponent_id = fixture['home_team_id']
                opponent_name = fixture['home_team']
                venue = 'Fora'
                goals_scored = fixture['goals_away']
                goals_conceded = fixture['goals_home']
                score = f"{goals_scored}-{goals_conceded}"
            
            # Posição do adversário
            opponent_data = standings.get(opponent_id, {})
            opponent_position = opponent_data.get('position', 99)
            opponent_positions.append(opponent_position)
            
            # Construir dados do jogo
            game_data = {
                'date': fixture['date'],
                'opponent': opponent_name,
                'opponent_position': opponent_position,
                'venue': venue,
                'score': score,
                'result': fixture['result'],
                'goals_scored': goals_scored,
                'goals_conceded': goals_conceded
            }
            games.append(game_data)
            
            # Contadores
            if fixture['result'] == 'W':
                wins += 1
            elif fixture['result'] == 'D':
                draws += 1
            else:
                losses += 1
            
            total_goals_scored += goals_scored
            total_goals_conceded += goals_conceded
        
        # Calcular Strength of Schedule (SoS)
        # Quanto menor a média de posição dos adversários, mais forte foi o calendário
        # Escala: 0-10 (10 = adversários muito fortes, 0 = adversários fracos)
        avg_opponent_position = sum(opponent_positions) / len(opponent_positions) if opponent_positions else 99
        
        # Normalizar: posição 1 = 10 pontos, posição 20 = 0 pontos
        # SoS = 10 - ((avg_position - 1) / 19) * 10
        total_teams = 20  # Assumir 20 times na liga (ajustar se necessário)
        sos = 10 - ((avg_opponent_position - 1) / (total_teams - 1)) * 10 if avg_opponent_position <= total_teams else 0
        sos = max(0, min(10, sos))  # Garantir entre 0-10
        
        # Calcular pontos (3 por vitória, 1 por empate)
        points = (wins * 3) + draws
        
        summary = {
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_scored': total_goals_scored,
            'goals_conceded': total_goals_conceded,
            'points': points,
            'strength_of_schedule': round(sos, 2),
            'avg_opponent_position': round(avg_opponent_position, 1)
        }
        
        logger.info(f"✅ Forma: {wins}W-{draws}D-{losses}L | SoS: {sos:.2f} | Avg Opp Pos: {avg_opponent_position:.1f}")
        
        return {
            'games': games,
            'summary': summary
        }
    
    def compare_forms(self, home_team_id: int, away_team_id: int, league_id: int, season: int = 2025) -> Dict:
        """
        Compara forma recente de ambos os times
        
        Returns:
            dict: {
                'home': {...},
                'away': {...},
                'comparison': {
                    'points_diff': int,
                    'sos_diff': float,
                    'better_form': str  # 'home', 'away', 'equal'
                }
            }
        """
        logger.info(f"⚖️ Comparando formas - Home: {home_team_id} vs Away: {away_team_id}")
        
        home_form = self.analyze_recent_form(home_team_id, league_id, season)
        away_form = self.analyze_recent_form(away_team_id, league_id, season)
        
        # Comparação
        points_diff = home_form['summary']['points'] - away_form['summary']['points']
        sos_diff = home_form['summary']['strength_of_schedule'] - away_form['summary']['strength_of_schedule']
        
        # Determinar melhor forma (considerando pontos e SoS)
        # Se diferença de pontos > 3, usar pontos
        # Senão, considerar SoS
        if abs(points_diff) > 3:
            better_form = 'home' if points_diff > 0 else 'away'
        elif abs(points_diff) >= 1:
            # Empate técnico em pontos, usar SoS como desempate
            if abs(sos_diff) > 1:
                better_form = 'home' if sos_diff > 0 else 'away'
            else:
                better_form = 'equal'
        else:
            better_form = 'equal'
        
        comparison = {
            'points_diff': points_diff,
            'sos_diff': round(sos_diff, 2),
            'better_form': better_form
        }
        
        logger.info(f"✅ Comparação: {better_form} | Pts: {points_diff:+d} | SoS: {sos_diff:+.2f}")
        
        return {
            'home': home_form,
            'away': away_form,
            'comparison': comparison
        }
    
    def _empty_form_result(self) -> Dict:
        """Retorna estrutura vazia quando não há dados"""
        return {
            'games': [],
            'summary': {
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_scored': 0,
                'goals_conceded': 0,
                'points': 0,
                'strength_of_schedule': 0,
                'avg_opponent_position': 99
            }
        }
