"""
Fase 4: Sistema de Enriquecimento Paralelo
Reduz tempo de enriquecimento de 15-20s para 3-5s usando asyncio + ThreadPoolExecutor
"""

import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from .api_football_service import APIFootballService
from .weather_service import WeatherService, STADIUM_COORDINATES

logger = logging.getLogger(__name__)


class ParallelMatchEnricher:
    """
    Versão otimizada do MatchDataEnricher com execução paralela.
    
    Speedup esperado: 3-5x mais rápido
    - Antes: 15-20s (sequencial)
    - Depois: 3-5s (paralelo)
    """
    
    def __init__(self):
        self.api_service = APIFootballService()
        self.weather_service = WeatherService()
        self.executor = ThreadPoolExecutor(max_workers=8)
    
    async def enrich_async(self, match_data):
        """
        Enriquece dados da partida com execução paralela.
        
        Fases paralelas:
        1. Fixture details (bloqueante - precisa dos IDs)
        2. Todos os demais em paralelo (standings, stats, injuries, odds, etc)
        
        Args:
            match_data (dict): Dados básicos da partida
            
        Returns:
            dict: Dados enriquecidos
        """
        logger.info("\n" + "="*80)
        logger.info("⚡ ENRIQUECIMENTO PARALELO - FASE 4")
        logger.info("="*80)
        
        import time
        start_time = time.time()
        
        api_id = match_data.get('api_id')
        
        if not api_id:
            logger.warning("⚠️ api_id não fornecido - enriquecimento limitado")
            return match_data
        
        # FASE 1: Buscar detalhes da partida (bloqueante)
        loop = asyncio.get_event_loop()
        fixture_details = await loop.run_in_executor(
            self.executor,
            self.api_service.fetch_fixture_details,
            api_id
        )
        
        if not fixture_details:
            logger.warning("⚠️ Detalhes da partida não encontrados")
            return match_data
        
        # Extrair IDs para próximas chamadas
        home_team_id = fixture_details['home_team']['id']
        away_team_id = fixture_details['away_team']['id']
        league_id = fixture_details['league']['id']
        season = fixture_details['league']['season']
        match_date = fixture_details.get('date', '')
        
        logger.info(f"📊 Partida: {fixture_details['home_team']['name']} vs {fixture_details['away_team']['name']}")
        logger.info(f"⚡ Iniciando 9 chamadas paralelas...")
        
        # FASE 2: Executar todas as chamadas em paralelo
        tasks = [
            # 1. Standings (usado por motivação)
            loop.run_in_executor(
                self.executor,
                self.api_service.fetch_standings,
                league_id,
                season
            ),
            # 2. Home team statistics
            loop.run_in_executor(
                self.executor,
                self.api_service.fetch_team_statistics,
                home_team_id,
                league_id,
                season
            ),
            # 3. Away team statistics
            loop.run_in_executor(
                self.executor,
                self.api_service.fetch_team_statistics,
                away_team_id,
                league_id,
                season
            ),
            # 4. Injuries
            loop.run_in_executor(
                self.executor,
                self.api_service.fetch_injuries,
                api_id
            ),
            # 5. Odds
            loop.run_in_executor(
                self.executor,
                self.api_service.fetch_odds,
                api_id
            ),
            # 6. Home recent fixtures (para rest context)
            loop.run_in_executor(
                self.executor,
                self.api_service.fetch_recent_fixtures,
                home_team_id,
                1
            ),
            # 7. Away recent fixtures (para rest context)
            loop.run_in_executor(
                self.executor,
                self.api_service.fetch_recent_fixtures,
                away_team_id,
                1
            ),
            # 8. Home last 10 (para trends)
            loop.run_in_executor(
                self.executor,
                self.api_service.fetch_recent_fixtures,
                home_team_id,
                10
            ),
            # 9. Away last 10 (para trends)
            loop.run_in_executor(
                self.executor,
                self.api_service.fetch_recent_fixtures,
                away_team_id,
                10
            ),
        ]
        
        # Aguardar TODAS as chamadas completarem
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Desempacotar resultados
        (
            standings_data,
            home_stats,
            away_stats,
            injuries_data,
            odds_data,
            home_last_1,
            away_last_1,
            home_last_10,
            away_last_10
        ) = results
        
        # Processar standings em table_context
        table_context = self._process_standings(
            standings_data if not isinstance(standings_data, Exception) else {},
            home_team_id,
            away_team_id
        )
        
        # Calcular rest context (já temos os dados)
        rest_context = self._calculate_rest_parallel(
            home_last_1 if not isinstance(home_last_1, Exception) else [],
            away_last_1 if not isinstance(away_last_1, Exception) else [],
            match_date
        )
        
        # Calcular trends (já temos os dados)
        trends = self._calculate_trends_parallel(
            home_last_10 if not isinstance(home_last_10, Exception) else [],
            away_last_10 if not isinstance(away_last_10, Exception) else []
        )
        
        # Buscar clima (independente, não paralelizável com as outras por ser API diferente)
        weather_data = await loop.run_in_executor(
            self.executor,
            self._get_weather_sync,
            fixture_details
        )
        
        elapsed = time.time() - start_time
        
        logger.info(f"⚡ Enriquecimento paralelo concluído em {elapsed:.2f}s")
        logger.info(f"   Speedup estimado: ~{15/elapsed:.1f}x mais rápido")
        
        enriched = {
            **match_data,
            'fixture_details': fixture_details,
            'table_context': table_context,
            'injuries': injuries_data if not isinstance(injuries_data, Exception) else {},
            'odds': odds_data if not isinstance(odds_data, Exception) else None,
            'home_stats': home_stats if not isinstance(home_stats, Exception) else {},
            'away_stats': away_stats if not isinstance(away_stats, Exception) else {},
            'rest_context': rest_context,
            'motivation': self._assess_motivation(table_context),
            'trends': trends,
            'season_context': self._get_season_context(fixture_details),
            'weather': weather_data,
            '_performance': {
                'enrichment_time': elapsed,
                'mode': 'parallel'
            }
        }
        
        logger.info("="*80 + "\n")
        
        return enriched
    
    def _process_standings(self, standings_data, home_team_id, away_team_id):
        """Processa dados de standings em table_context"""
        if not standings_data or isinstance(standings_data, Exception):
            return None
        
        home_standing = standings_data.get(home_team_id, {})
        away_standing = standings_data.get(away_team_id, {})
        
        return {
            'home': {
                'position': home_standing.get('position'),
                'points': home_standing.get('points'),
                'form': home_standing.get('form', ''),
                'goal_difference': home_standing.get('goal_difference', 0),
            },
            'away': {
                'position': away_standing.get('position'),
                'points': away_standing.get('points'),
                'form': away_standing.get('form', ''),
                'goal_difference': away_standing.get('goal_difference', 0),
            }
        }
    
    def _calculate_rest_parallel(self, home_fixtures, away_fixtures, match_date):
        """Calcula rest context usando dados já carregados"""
        try:
            from datetime import datetime
            match_dt = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
            
            home_days = 7
            away_days = 7
            
            if home_fixtures and len(home_fixtures) > 0:
                last_home = home_fixtures[0]
                last_date = datetime.fromisoformat(last_home['fixture']['date'].replace('Z', '+00:00'))
                home_days = (match_dt - last_date).days
            
            if away_fixtures and len(away_fixtures) > 0:
                last_away = away_fixtures[0]
                last_date = datetime.fromisoformat(last_away['fixture']['date'].replace('Z', '+00:00'))
                away_days = (match_dt - last_date).days
            
            advantage = 'balanced'
            if abs(home_days - away_days) >= 2:
                advantage = 'home' if home_days > away_days else 'away'
            
            return {
                'home_days_rest': home_days,
                'away_days_rest': away_days,
                'advantage': advantage
            }
        except:
            return {'home_days_rest': 7, 'away_days_rest': 7, 'advantage': 'balanced'}
    
    def _calculate_trends_parallel(self, home_fixtures, away_fixtures):
        """Calcula trends usando dados já carregados"""
        trends = {
            'home': {'over_25_pct': 0, 'btts_pct': 0, 'games_analyzed': 0},
            'away': {'over_25_pct': 0, 'btts_pct': 0, 'games_analyzed': 0},
            'combined_over_25_pct': 0,
            'combined_btts_pct': 0
        }
        
        try:
            # Home trends
            if home_fixtures:
                over_count = 0
                btts_count = 0
                for fixture in home_fixtures:
                    goals = fixture.get('goals', {})
                    home_g = goals.get('home', 0) or 0
                    away_g = goals.get('away', 0) or 0
                    total = home_g + away_g
                    
                    if total > 2.5:
                        over_count += 1
                    if home_g > 0 and away_g > 0:
                        btts_count += 1
                
                count = len(home_fixtures)
                trends['home'] = {
                    'over_25_pct': (over_count / count * 100) if count > 0 else 0,
                    'btts_pct': (btts_count / count * 100) if count > 0 else 0,
                    'games_analyzed': count
                }
            
            # Away trends
            if away_fixtures:
                over_count = 0
                btts_count = 0
                for fixture in away_fixtures:
                    goals = fixture.get('goals', {})
                    home_g = goals.get('home', 0) or 0
                    away_g = goals.get('away', 0) or 0
                    total = home_g + away_g
                    
                    if total > 2.5:
                        over_count += 1
                    if home_g > 0 and away_g > 0:
                        btts_count += 1
                
                count = len(away_fixtures)
                trends['away'] = {
                    'over_25_pct': (over_count / count * 100) if count > 0 else 0,
                    'btts_pct': (btts_count / count * 100) if count > 0 else 0,
                    'games_analyzed': count
                }
            
            # Combined
            trends['combined_over_25_pct'] = (trends['home']['over_25_pct'] + trends['away']['over_25_pct']) / 2
            trends['combined_btts_pct'] = (trends['home']['btts_pct'] + trends['away']['btts_pct']) / 2
            
        except Exception as e:
            logger.error(f"Erro ao calcular trends: {e}")
        
        return trends
    
    def _assess_motivation(self, table_context):
        """Avalia motivação dos times"""
        if not table_context:
            return {}
        
        home_pos = table_context.get('home', {}).get('position', 10)
        away_pos = table_context.get('away', {}).get('position', 10)
        
        def get_motivation(position):
            if position <= 4:
                return 'high', 'Briga por título/Champions'
            elif position <= 7:
                return 'medium', 'Briga por Europa'
            elif position >= 17:
                return 'very_high', 'Luta contra rebaixamento'
            else:
                return 'low', 'Mid-table sem objetivos'
        
        home_mot, home_reason = get_motivation(home_pos)
        away_mot, away_reason = get_motivation(away_pos)
        
        return {
            'home': home_mot,
            'home_reason': home_reason,
            'away': away_mot,
            'away_reason': away_reason,
            'context': 'Normal league match'
        }
    
    def _get_season_context(self, fixture_details):
        """Analisa fase da temporada"""
        round_info = fixture_details['league'].get('round', '')
        
        return {
            'round': round_info,
            'season': fixture_details['league']['season'],
            'stage': 'mid',
            'note': 'Fase da temporada'
        }
    
    def _get_weather_sync(self, fixture_details):
        """Versão síncrona do get_weather para usar com executor"""
        try:
            venue_name = fixture_details.get('venue', {}).get('name', '')
            venue_city = fixture_details.get('venue', {}).get('city', '')
            match_date_str = fixture_details.get('date', '')
            
            if not venue_name or not match_date_str:
                return None
            
            try:
                match_datetime = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
            except:
                return None
            
            now = datetime.now(match_datetime.tzinfo)
            time_diff = match_datetime - now
            
            if time_diff.total_seconds() < 0 or time_diff.days > 7:
                return None
            
            coordinates = STADIUM_COORDINATES.get(venue_name)
            
            if not coordinates:
                coordinates = self.weather_service.get_stadium_coordinates(venue_name, venue_city)
                if not coordinates:
                    return None
            
            latitude, longitude = coordinates
            weather = self.weather_service.get_weather_for_match(latitude, longitude, match_datetime)
            
            return weather
            
        except Exception as e:
            logger.error(f"Erro ao buscar clima: {str(e)}")
            return None
