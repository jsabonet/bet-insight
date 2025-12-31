"""
Serviço de Enriquecimento de Dados de Partidas
Adiciona contexto completo para análises mais precisas
"""
import logging
import time
from datetime import datetime, timedelta
from .api_football_service import APIFootballService

logger = logging.getLogger(__name__)

class MatchDataEnricher:
    """Enriquece dados básicos da partida com contexto adicional"""
    
    def __init__(self):
        self.api_service = APIFootballService()
    
    def enrich(self, match_data):
        """
        Enriquece dados da partida com contexto completo
        
        Args:
            match_data (dict): Dados básicos da partida
        
        Returns:
            dict: Dados enriquecidos com contexto adicional
        """
        logger.info("\n" + "="*80)
        logger.info("🔄 INICIANDO ENRIQUECIMENTO DE DADOS")
        logger.info("="*80)
        
        api_id = match_data.get('api_id')
        
        if not api_id:
            logger.warning("⚠️ api_id não fornecido - enriquecimento limitado")
            return match_data
        
        # Buscar detalhes da partida primeiro
        fixture_details = self.api_service.fetch_fixture_details(api_id)
        
        if not fixture_details:
            logger.warning("⚠️ Detalhes da partida não encontrados")
            return match_data
        
        # Extrair IDs
        home_team_id = fixture_details['home_team']['id']
        away_team_id = fixture_details['away_team']['id']
        league_id = fixture_details['league']['id']
        season = fixture_details['league']['season']
        match_date = fixture_details.get('date', '')
        
        # Buscar contexto da tabela primeiro (usado por motivação)
        table_context = self._get_table_context(league_id, season, home_team_id, away_team_id)
        
        enriched = {
            **match_data,
            'fixture_details': fixture_details,
            'table_context': table_context,
            'injuries': self._get_injuries(api_id, home_team_id, away_team_id),
            'odds': self._get_odds(api_id),
            'home_stats': self._get_team_statistics(home_team_id, league_id, season),
            'away_stats': self._get_team_statistics(away_team_id, league_id, season),
            'rest_context': self._calculate_rest_context(home_team_id, away_team_id, league_id, season, match_date),
            'motivation': self._assess_motivation(table_context),
            'trends': self._calculate_trends(home_team_id, away_team_id, league_id, season),
            'season_context': self._get_season_context(fixture_details)
        }
        
        logger.info("\n" + "="*80)
        logger.info("✅ ENRIQUECIMENTO CONCLUÍDO")
        logger.info("="*80 + "\n")
        
        return enriched
    
    def _get_table_context(self, league_id, season, home_team_id, away_team_id):
        """Busca posição na tabela e pontos dos times"""
        logger.info("\n📊 Buscando contexto da tabela...")
        time.sleep(0.5)  # Delay para respeitar rate limit
        
        standings = self.api_service.fetch_standings(league_id, season)
        
        if not standings:
            return None
        
        home_standing = standings.get(home_team_id, {})
        away_standing = standings.get(away_team_id, {})
        
        context = {
            'home': {
                'position': home_standing.get('position'),
                'points': home_standing.get('points'),
                'form': home_standing.get('form', ''),
                'goal_difference': home_standing.get('goal_difference', 0),
                'home_record': home_standing.get('home_record', ''),
                'away_record': home_standing.get('away_record', '')
            },
            'away': {
                'position': away_standing.get('position'),
                'points': away_standing.get('points'),
                'form': away_standing.get('form', ''),
                'goal_difference': away_standing.get('goal_difference', 0),
                'home_record': away_standing.get('home_record', ''),
                'away_record': away_standing.get('away_record', '')
            }
        }
        
        logger.info(f"   ✅ Casa: {context['home']['position']}º lugar, {context['home']['points']} pts")
        logger.info(f"   ✅ Fora: {context['away']['position']}º lugar, {context['away']['points']} pts")
        
        return context
    
    def _get_injuries(self, fixture_id, home_team_id, away_team_id):
        """Busca lesões e suspensões"""
        logger.info("\n🚑 Buscando lesões e suspensões...")
        time.sleep(0.5)  # Delay para respeitar rate limit
        
        injuries_data = self.api_service.fetch_injuries(fixture_id)
        
        if not injuries_data:
            return {'home': [], 'away': []}
        
        home_count = len(injuries_data.get('home', []))
        away_count = len(injuries_data.get('away', []))
        
        logger.info(f"   ✅ {home_count} lesões/suspensões (casa), {away_count} (fora)")
        
        return injuries_data
    
    def _get_odds(self, fixture_id):
        """Busca odds das casas de apostas"""
        logger.info("\n💰 Buscando odds...")
        time.sleep(0.5)  # Delay para respeitar rate limit
        
        odds = self.api_service.fetch_odds(fixture_id)
        
        if odds:
            logger.info(f"   ✅ Odds: Casa {odds.get('home_win', 'N/A')} | "
                       f"Empate {odds.get('draw', 'N/A')} | "
                       f"Fora {odds.get('away_win', 'N/A')}")
        else:
            logger.info("   ⚠️ Odds não disponíveis")
        
        return odds
    
    def _get_team_statistics(self, team_id, league_id, season):
        """Busca estatísticas detalhadas do time"""
        logger.info(f"\n📈 Buscando estatísticas (Team {team_id})...")
        time.sleep(0.5)  # Delay para respeitar rate limit
        
        stats = self.api_service.fetch_team_statistics(team_id, league_id, season)
        
        if stats:
            logger.info(f"   ✅ {stats.get('games_played', 0)} jogos, "
                       f"média {stats.get('goals_per_game_avg', 0):.2f} gols/jogo")
        else:
            logger.info("   ⚠️ Estatísticas não disponíveis")
        
        return stats
    
    def _calculate_rest_context(self, home_team_id, away_team_id, league_id, season, match_date):
        """Calcula dias de descanso real"""
        logger.info("\n⏱️ Calculando contexto de descanso...")
        time.sleep(0.5)  # Delay para respeitar rate limit
        
        from datetime import datetime
        
        # Buscar última fixture de cada time
        home_fixtures = self.api_service.fetch_team_fixtures(home_team_id, league_id, season, last=1)
        time.sleep(0.5)
        away_fixtures = self.api_service.fetch_team_fixtures(away_team_id, league_id, season, last=1)
        
        home_days = None
        away_days = None
        advantage = 'equal'
        
        try:
            match_datetime = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
            
            if home_fixtures and len(home_fixtures) > 0:
                last_home = datetime.fromisoformat(home_fixtures[0]['date'].replace('Z', '+00:00'))
                home_days = (match_datetime - last_home).days
            
            if away_fixtures and len(away_fixtures) > 0:
                last_away = datetime.fromisoformat(away_fixtures[0]['date'].replace('Z', '+00:00'))
                away_days = (match_datetime - last_away).days
            
            # Determinar vantagem
            if home_days and away_days:
                if home_days > away_days + 1:
                    advantage = 'home'
                elif away_days > home_days + 1:
                    advantage = 'away'
                    
        except Exception as e:
            logger.warning(f"   ⚠️ Erro ao calcular descanso: {e}")
        
        context = {
            'home_days_rest': home_days,
            'away_days_rest': away_days,
            'advantage': advantage
        }
        
        if home_days and away_days:
            logger.info(f"   ✅ Descanso: Casa {home_days} dias, Fora {away_days} dias (Vantagem: {advantage})")
            logger.info(f"   📊 CONSOLE LOG - REST_CONTEXT: {context}")
        else:
            logger.info("   ⚠️ Dados de descanso incompletos")
            logger.info(f"   📊 CONSOLE LOG - REST_CONTEXT (incompleto): {context}")
        
        return context
    
    def _assess_motivation(self, table_context):
        """Avalia motivação dos times baseado em posição na tabela"""
        logger.info("\n🎖️ Avaliando motivação...")
        
        if not table_context:
            logger.info("   ⚠️ Sem dados de tabela para avaliar motivação")
            return {'home': 'medium', 'away': 'medium', 'context': 'Unknown'}
        
        home_pos = table_context['home'].get('position')
        away_pos = table_context['away'].get('position')
        home_pts = table_context['home'].get('points', 0)
        away_pts = table_context['away'].get('points', 0)
        
        def assess_team_motivation(position, points):
            """Avalia motivação individual"""
            if position is None:
                return 'medium', 'Mid-table'
            
            if position <= 3:
                return 'very_high', 'Luta pelo título'
            elif position <= 4:
                return 'high', 'Luta por Champions League'
            elif position <= 6:
                return 'high', 'Luta por Europa League'
            elif position >= 18:  # Zona de rebaixamento (assumindo 20 times)
                return 'very_high', 'Luta contra rebaixamento'
            elif position >= 15:
                return 'medium', 'Risco de rebaixamento'
            else:
                return 'low', 'Mid-table sem objetivos'
        
        home_level, home_reason = assess_team_motivation(home_pos, home_pts)
        away_level, away_reason = assess_team_motivation(away_pos, away_pts)
        
        # Detectar confronto direto
        context = 'Normal league match'
        if home_pos and away_pos:
            pos_diff = abs(home_pos - away_pos)
            if home_pos <= 4 and away_pos <= 4:
                context = '🔥 Confronto direto pelo topo da tabela'
            elif home_pos >= 17 and away_pos >= 17:
                context = '⚠️ Confronto direto pela permanência'
            elif pos_diff <= 2 and home_pos <= 10:
                context = 'Confronto direto importante'
        
        motivation = {
            'home': home_level,
            'home_reason': home_reason,
            'away': away_level,
            'away_reason': away_reason,
            'context': context
        }
        
        logger.info(f"   ✅ Casa: {home_level} ({home_reason})")
        logger.info(f"   ✅ Fora: {away_level} ({away_reason})")
        logger.info(f"   📍 Contexto: {context}")
        logger.info(f"   📊 CONSOLE LOG - MOTIVATION: {motivation}")
        
        return motivation
    
    def _calculate_trends(self, home_team_id, away_team_id, league_id, season):
        """Calcula tendências Over/Under e BTTS"""
        logger.info("\n📈 Calculando tendências...")
        time.sleep(0.5)  # Delay para respeitar rate limit
        
        # Buscar últimos 10 jogos de cada time
        home_fixtures = self.api_service.fetch_team_fixtures(home_team_id, league_id, season, last=10)
        time.sleep(0.5)
        away_fixtures = self.api_service.fetch_team_fixtures(away_team_id, league_id, season, last=10)
        
        trends = {
            'home': {'over_25_pct': 0, 'btts_pct': 0, 'games_analyzed': 0},
            'away': {'over_25_pct': 0, 'btts_pct': 0, 'games_analyzed': 0}
        }
        
        # Calcular para time da casa
        if home_fixtures:
            home_over = sum(1 for f in home_fixtures if f['over_25'])
            home_btts = sum(1 for f in home_fixtures if f['btts'])
            total_home = len(home_fixtures)
            
            trends['home'] = {
                'over_25_pct': (home_over / total_home * 100) if total_home > 0 else 0,
                'btts_pct': (home_btts / total_home * 100) if total_home > 0 else 0,
                'games_analyzed': total_home
            }
        
        # Calcular para time visitante
        if away_fixtures:
            away_over = sum(1 for f in away_fixtures if f['over_25'])
            away_btts = sum(1 for f in away_fixtures if f['btts'])
            total_away = len(away_fixtures)
            
            trends['away'] = {
                'over_25_pct': (away_over / total_away * 100) if total_away > 0 else 0,
                'btts_pct': (away_btts / total_away * 100) if total_away > 0 else 0,
                'games_analyzed': total_away
            }
        
        # Calcular probabilidade combinada
        if trends['home']['games_analyzed'] > 0 and trends['away']['games_analyzed'] > 0:
            trends['combined_over_25_pct'] = (trends['home']['over_25_pct'] + trends['away']['over_25_pct']) / 2
            trends['combined_btts_pct'] = (trends['home']['btts_pct'] + trends['away']['btts_pct']) / 2
            
            logger.info(f"   ✅ Over 2.5: Casa {trends['home']['over_25_pct']:.0f}%, Fora {trends['away']['over_25_pct']:.0f}%")
            logger.info(f"   ✅ BTTS: Casa {trends['home']['btts_pct']:.0f}%, Fora {trends['away']['btts_pct']:.0f}%")
            logger.info(f"   📊 CONSOLE LOG - TRENDS: {trends}")
        else:
            logger.info("   ⚠️ Dados insuficientes para calcular tendências")
            logger.info(f"   📊 CONSOLE LOG - TRENDS (incompleto): {trends}")
        
        return trends
    
    def _get_season_context(self, fixture_details):
        """Analisa fase da temporada"""
        logger.info("\n📅 Analisando fase da temporada...")
        
        round_info = fixture_details['league'].get('round', '')
        
        context = {
            'round': round_info,
            'season': fixture_details['league']['season'],
            'stage': 'mid',  # early, mid, late
            'note': 'Fase da temporada'
        }
        
        logger.info(f"   ✅ Rodada: {round_info}, Temporada: {context['season']}")
        
        return context
