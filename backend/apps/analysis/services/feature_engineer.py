"""
Feature Engineering Service - TIER 1
Extrai features avançadas dos dados da API-Football para modelos estatísticos
"""
import logging
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class FeatureEngineer:
    """
    Engenharia de features usando dados da API-Football
    Extrai variáveis objetivas e calculadas para modelos estatísticos
    """
    
    def __init__(self):
        pass
    
    def engineer_all_features(self, enriched_data):
        """
        Extrai TODAS as features TIER 1 de dados enriquecidos
        
        Args:
            enriched_data (dict): Dados da partida já enriquecidos pelo match_enricher
        
        Returns:
            dict: {
                'strength': {...},      # Força ofensiva/defensiva
                'form': {...},          # Forma ponderada, momentum, SoS
                'statistics': {...},    # Corners, cartões, gols temporais, variância
                'context': {...},       # Fadiga, descanso
                'market': {...},        # Probabilidades implícitas das odds
                'weather': {...}        # Dados climáticos e impacto
            }
        """
        logger.info(f"\n{'='*80}")
        logger.info("🔧 FEATURE ENGINEERING - TIER 1 COMPLETO (40 VARIÁVEIS)")
        logger.info(f"{'='*80}\n")
        
        # Extrair dados necessários
        standings = enriched_data.get('table_context', {})
        home_stats = enriched_data.get('home_stats', {})
        away_stats = enriched_data.get('away_stats', {})
        odds = enriched_data.get('odds', {})
        rest_context = enriched_data.get('rest_context', {})
        weather = enriched_data.get('weather', {})
        recent_form = enriched_data.get('recent_form', {})  # Fase 2
        h2h = enriched_data.get('h2h', [])
        statistics = enriched_data.get('statistics', {})  # Estatísticas detalhadas da partida
        
        logger.info("📥 Dados disponíveis:")
        logger.info(f"   Standings: {bool(standings)}")
        logger.info(f"   Home Stats: {bool(home_stats)}")
        logger.info(f"   Away Stats: {bool(away_stats)}")
        logger.info(f"   Odds: {bool(odds)}")
        logger.info(f"   Rest Context: {bool(rest_context)}")
        logger.info(f"   Weather: {bool(weather)}")
        logger.info(f"   Recent Form: {bool(recent_form)}")
        logger.info(f"   H2H: {len(h2h) if h2h else 0} jogos")
        logger.info(f"   Statistics: {bool(statistics)}")
        
        features = {}
        
        # 1. FORÇA OFENSIVA/DEFENSIVA RELATIVA (#12-14)
        logger.info("\n1️⃣ Calculando features de FORÇA...")
        features['strength'] = self._calculate_strength_features(standings, home_stats, away_stats)
        logger.info(f"   ✅ {len(features['strength'])} features de força")
        
        # 2. FORMA PONDERADA, MOMENTUM E SOS (#19-21)
        logger.info("\n2️⃣ Calculando features de FORMA...")
        features['form'] = self._calculate_form_features(standings, recent_form)
        logger.info(f"   ✅ {len(features['form'])} features de forma")
        
        # 3. ESTATÍSTICAS AVANÇADAS (#23-24, #26-27)
        logger.info("\n3️⃣ Calculando features de ESTATÍSTICAS...")
        features['statistics'] = self._calculate_statistics_features(home_stats, away_stats, statistics)
        logger.info(f"   ✅ {len(features['statistics'])} features de estatísticas")
        
        # 4. CONTEXTO (Fadiga, Descanso) (#33-34)
        logger.info("\n4️⃣ Calculando features de CONTEXTO...")
        features['context'] = self._calculate_context_features(rest_context)
        logger.info(f"   ✅ {len(features['context'])} features de contexto")
        
        # 5. MERCADO (Probabilidades implícitas)
        logger.info("\n5️⃣ Calculando features de MERCADO...")
        features['market'] = self._calculate_market_features(odds)
        logger.info(f"   ✅ {len(features['market'])} features de mercado")
        
        # 6. CLIMA (Impacto climático)
        logger.info("\n6️⃣ Calculando features de CLIMA...")
        features['weather'] = self._calculate_weather_features(weather)
        logger.info(f"   ✅ {len(features['weather'])} features de clima")
        if weather:
            logger.info(f"      Weather Impact: {weather.get('weather_impact', 0.0)} gols")
            logger.info(f"      Condition: {weather.get('description', 'N/A')}")
            logger.info(f"      Temperature: {weather.get('temperature', 'N/A')}°C")
        
        # 7. H2H (Histórico direto)
        logger.info("\n7️⃣ Calculando features de H2H...")
        features['h2h'] = self._calculate_h2h_features(h2h)
        logger.info(f"   ✅ {len(features['h2h'])} features de H2H")
        
        # 8. MATCH IMPORTANCE (Nova implementação)
        logger.info("\n8️⃣ Calculando features de IMPORTÂNCIA DO JOGO...")
        features['match_importance'] = self._calculate_match_importance_features(
            enriched_data, standings
        )
        logger.info(f"   ✅ {len(features['match_importance'])} features de importância")
        
        # 9. INJURIES/SUSPENSIONS (Nova implementação)
        logger.info("\n9️⃣ Calculando features de LESÕES/SUSPENSÕES...")
        features['injuries_suspensions'] = self._calculate_injuries_suspensions_features(
            enriched_data
        )
        logger.info(f"   ✅ {len(features['injuries_suspensions'])} features de lesões/suspensões")
        
        # 10. MOTIVATION (Nova implementação)
        logger.info("\n🔟 Calculando features de MOTIVAÇÃO...")
        features['motivation'] = self._calculate_motivation_features(
            standings, enriched_data
        )
        logger.info(f"   ✅ {len(features['motivation'])} features de motivação")
        
        total_features = sum(len(v) for v in features.values())
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ TOTAL: {total_features} features engineered")
        logger.info(f"{'='*80}\n")
        
        return features
    
    def _calculate_strength_features(self, standings, home_stats, away_stats):
        """
        VARIÁVEIS #12, #13, #14: Força ofensiva/defensiva relativa
        
        Normaliza força dos times pela média da liga
        """
        # Tratar caso quando standings é None (friendlies, etc)
        if standings is None:
            standings = {}
        
        home_standing = standings.get('home', {})
        away_standing = standings.get('away', {})
        
        # Extrair dados básicos
        home_goals_for = home_standing.get('goals_for', 0)
        home_goals_against = home_standing.get('goals_against', 0)
        home_games = home_standing.get('games_played', 1)
        
        away_goals_for = away_standing.get('goals_for', 0)
        away_goals_against = away_standing.get('goals_against', 0)
        away_games = away_standing.get('games_played', 1)
        
        # Médias por jogo
        home_goals_per_game = home_goals_for / max(home_games, 1)
        home_conceded_per_game = home_goals_against / max(home_games, 1)
        
        away_goals_per_game = away_goals_for / max(away_games, 1)
        away_conceded_per_game = away_goals_against / max(away_games, 1)
        
        # Assumir média da liga ~ 1.5 gols/jogo (pode ser calculada dinamicamente depois)
        league_avg_goals = 1.5
        
        # VARIÁVEL #12: Força ofensiva relativa
        home_attack_strength = home_goals_per_game / league_avg_goals if league_avg_goals > 0 else 1.0
        away_attack_strength = away_goals_per_game / league_avg_goals if league_avg_goals > 0 else 1.0
        
        # VARIÁVEL #13: Força defensiva relativa (inverso - maior = melhor defesa)
        home_defense_strength = league_avg_goals / home_conceded_per_game if home_conceded_per_game > 0 else 1.0
        away_defense_strength = league_avg_goals / away_conceded_per_game if away_conceded_per_game > 0 else 1.0
        
        # VARIÁVEL #14: Diferencial de força
        strength_differential = (home_attack_strength * away_defense_strength) - \
                              (away_attack_strength * home_defense_strength)
        
        # Usar estatísticas reais da API se disponíveis
        if home_stats and away_stats:
            # API retorna goals_per_game_avg e goals_conceded_avg
            home_goals_per_game = float(home_stats.get('goals_per_game_avg', home_goals_per_game))
            home_conceded_per_game = float(home_stats.get('goals_conceded_avg', home_conceded_per_game))
            away_goals_per_game = float(away_stats.get('goals_per_game_avg', away_goals_per_game))
            away_conceded_per_game = float(away_stats.get('goals_conceded_avg', away_conceded_per_game))
            
            # Recalcular strength com dados reais
            home_attack_strength = home_goals_per_game / league_avg_goals if league_avg_goals > 0 else 1.0
            away_attack_strength = away_goals_per_game / league_avg_goals if league_avg_goals > 0 else 1.0
            home_defense_strength = league_avg_goals / home_conceded_per_game if home_conceded_per_game > 0 else 1.0
            away_defense_strength = league_avg_goals / away_conceded_per_game if away_conceded_per_game > 0 else 1.0
            strength_differential = (home_attack_strength * away_defense_strength) - \
                                  (away_attack_strength * home_defense_strength)
        
        # Fator casa padrão (pode ser melhorado com dados específicos casa/fora se disponíveis)
        home_advantage_factor = 1.2
        
        return {
            'home_attack_strength': round(home_attack_strength, 2),
            'home_defense_strength': round(home_defense_strength, 2),
            'away_attack_strength': round(away_attack_strength, 2),
            'away_defense_strength': round(away_defense_strength, 2),
            'strength_differential': round(strength_differential, 2),
            'home_advantage_factor': round(max(1.0, min(1.5, home_advantage_factor)), 2),
            'home_goals_per_game': round(home_goals_per_game, 2),
            'away_goals_per_game': round(away_goals_per_game, 2),
            'home_conceded_per_game': round(home_conceded_per_game, 2),
            'away_conceded_per_game': round(away_conceded_per_game, 2)
        }
    
    def _calculate_form_features(self, standings, recent_form):
        """
        VARIÁVEIS #19, #20, #21: Forma ponderada, momentum e Strength of Schedule
        
        Pondera jogos recentes (mais recente = mais peso)
        Detecta tendência (melhorando ou piorando)
        Incorpora força dos adversários enfrentados (SoS)
        """
        # Tratar caso quando standings é None
        if standings is None:
            standings = {}
        
        home_standing = standings.get('home', {})
        away_standing = standings.get('away', {})
        
        home_form = home_standing.get('form', '')
        away_form = away_standing.get('form', '')
        
        # Calcular forma ponderada e momentum para cada time
        home_form_data = self._process_form_string(home_form)
        away_form_data = self._process_form_string(away_form)
        
        # VARIÁVEL #21: Strength of Schedule (SoS)
        # Força dos adversários enfrentados nos últimos jogos
        home_sos = 0
        away_sos = 0
        sos_differential = 0
        
        if recent_form:
            home_summary = recent_form.get('home', {}).get('summary', {})
            away_summary = recent_form.get('away', {}).get('summary', {})
            
            home_sos = home_summary.get('strength_of_schedule', 0)
            away_sos = away_summary.get('strength_of_schedule', 0)
            sos_differential = home_sos - away_sos
            
            logger.info(f"      SoS - Casa: {home_sos:.2f}, Fora: {away_sos:.2f}, Diff: {sos_differential:+.2f}")
        
        # Ajustar forma baseada em SoS
        # Se enfrentou adversários fortes (SoS alto), forma ponderada vale mais
        home_adjusted_form = home_form_data['weighted_form'] * (1 + (home_sos / 20))
        away_adjusted_form = away_form_data['weighted_form'] * (1 + (away_sos / 20))
        
        return {
            'home_weighted_form': home_form_data['weighted_form'],
            'home_momentum': home_form_data['momentum'],
            'home_recent_points': home_form_data['recent_points'],
            'home_sos': round(home_sos, 2),
            'home_adjusted_form': round(home_adjusted_form, 2),
            'away_weighted_form': away_form_data['weighted_form'],
            'away_momentum': away_form_data['momentum'],
            'away_recent_points': away_form_data['recent_points'],
            'away_sos': round(away_sos, 2),
            'away_adjusted_form': round(away_adjusted_form, 2),
            'form_differential': round(home_form_data['weighted_form'] - away_form_data['weighted_form'], 2),
            'sos_differential': round(sos_differential, 2),
            'adjusted_form_diff': round(home_adjusted_form - away_adjusted_form, 2)
        }
    
    def _process_form_string(self, form_string):
        """
        Processa string de forma (ex: "WWLDW") em métricas
        
        Forma ponderada: jogos recentes valem mais
        Momentum: tendência (últimos 3 vs primeiros 2)
        """
        if not form_string or len(form_string) == 0:
            return {
                'weighted_form': 1.5,
                'momentum': 0,
                'recent_points': 0
            }
        
        # Converter resultados em pontos
        points = []
        for result in form_string:
            if result == 'W':
                points.append(3)
            elif result == 'D':
                points.append(1)
            else:
                points.append(0)
        
        # Pesos para forma ponderada (mais recente = maior peso)
        # Últimos 5 jogos: [1.0, 1.1, 1.2, 1.3, 1.5]
        n_games = len(points)
        if n_games >= 5:
            weights = [1.0, 1.1, 1.2, 1.3, 1.5]
            points_to_use = points[-5:]
        else:
            # Se tiver menos de 5, ajustar pesos
            weights = [1.0 + (i * 0.1) for i in range(n_games)]
            points_to_use = points
        
        # Forma ponderada
        weighted_sum = sum(p * w for p, w in zip(points_to_use, weights))
        weight_sum = sum(weights)
        weighted_form = weighted_sum / weight_sum if weight_sum > 0 else 1.5
        
        # Momentum (tendência)
        if n_games >= 5:
            first_half = points[:2]  # Primeiros 2
            second_half = points[-3:]  # Últimos 3
            
            first_avg = sum(first_half) / len(first_half) if first_half else 0
            second_avg = sum(second_half) / len(second_half) if second_half else 0
            
            momentum = second_avg - first_avg
        else:
            momentum = 0
        
        # Pontos recentes (últimos 5)
        recent_points = sum(points_to_use)
        
        return {
            'weighted_form': round(weighted_form, 2),
            'momentum': round(momentum, 2),
            'recent_points': recent_points
        }
    
    def _calculate_statistics_features(self, home_stats, away_stats, statistics):
        """
        VARIÁVEIS #23, #24, #26, #27: Variância, 1T vs 2T, Disciplina, Corners
        
        Extrai métricas de estatísticas detalhadas
        """
        # Corners
        home_corners = home_stats.get('corners_per_game', 0)
        away_corners = away_stats.get('corners_per_game', 0)
        
        # Cartões (disciplina) - VARIÁVEL #26
        home_yellow = home_stats.get('yellow_cards', 0)
        home_red = home_stats.get('red_cards', 0)
        home_games = home_stats.get('games_played', 1)
        
        away_yellow = away_stats.get('yellow_cards', 0)
        away_red = away_stats.get('red_cards', 0)
        away_games = away_stats.get('games_played', 1)
        
        # Cartões por jogo (vermelho conta x2)
        home_cards_per_game = (home_yellow + home_red * 2) / max(home_games, 1)
        away_cards_per_game = (away_yellow + away_red * 2) / max(away_games, 1)
        
        # Disciplina score (0-1, 1 = muito disciplinado)
        home_discipline = 1 / (1 + home_cards_per_game / 3)
        away_discipline = 1 / (1 + away_cards_per_game / 3)
        
        # Clean sheets e failed to score
        home_clean_sheets = home_stats.get('clean_sheets', 0)
        away_clean_sheets = away_stats.get('clean_sheets', 0)
        
        home_clean_sheet_rate = home_clean_sheets / max(home_games, 1)
        away_clean_sheet_rate = away_clean_sheets / max(away_games, 1)
        
        # VARIÁVEL #23: Variância de performance (consistência)
        # Calcula desvio padrão de gols nos últimos jogos
        home_variance = self._calculate_variance(home_stats)
        away_variance = self._calculate_variance(away_stats)
        
        # VARIÁVEL #24: Performance 1T vs 2T
        # Extrai estatísticas de gols por tempo da API
        home_1t_performance = self._calculate_half_performance(statistics, 'home')
        away_1t_performance = self._calculate_half_performance(statistics, 'away')
        
        return {
            # Corners (#27)
            'home_corners_per_game': round(home_corners, 2),
            'away_corners_per_game': round(away_corners, 2),
            'total_corners_expected': round(home_corners + away_corners, 2),
            
            # Disciplina (#26)
            'home_cards_per_game': round(home_cards_per_game, 2),
            'away_cards_per_game': round(away_cards_per_game, 2),
            'home_discipline_score': round(home_discipline, 2),
            'away_discipline_score': round(away_discipline, 2),
            
            # Clean sheets
            'home_clean_sheet_rate': round(home_clean_sheet_rate, 2),
            'away_clean_sheet_rate': round(away_clean_sheet_rate, 2),
            
            # Variância (#23)
            'home_variance': round(home_variance, 2),
            'away_variance': round(away_variance, 2),
            'variance_differential': round(home_variance - away_variance, 2),
            
            # Performance 1T vs 2T (#24)
            'home_1st_half_pct': round(home_1t_performance, 2),
            'away_1st_half_pct': round(away_1t_performance, 2),
            'first_half_differential': round(home_1t_performance - away_1t_performance, 2)
        }
    
    def _calculate_context_features(self, rest_context):
        """
        VARIÁVEIS #33, #34: Fadiga e descanso relativo
        
        Dias desde último jogo e diferencial de descanso
        """
        home_rest_days = rest_context.get('home_rest_days', 7)
        away_rest_days = rest_context.get('away_rest_days', 7)
        
        # Fadiga (jogos com menos de 3 dias = fadiga)
        home_is_fatigued = home_rest_days < 3
        away_is_fatigued = away_rest_days < 3
        
        # Descanso relativo (vantagem de descanso)
        rest_advantage = home_rest_days - away_rest_days
        
        return {
            'home_rest_days': home_rest_days,
            'away_rest_days': away_rest_days,
            'home_is_fatigued': home_is_fatigued,
            'away_is_fatigued': away_is_fatigued,
            'rest_advantage': rest_advantage,
            'fatigue_impact': -0.1 if (home_is_fatigued or away_is_fatigued) else 0
        }
    
    def _calculate_market_features(self, odds):
        """
        Converter odds em probabilidades implícitas
        Detectar consenso de mercado
        """
        if not odds:
            return {
                'market_home_prob': 0.33,
                'market_draw_prob': 0.33,
                'market_away_prob': 0.33,
                'bookmaker_margin': 0.05
            }
        
        home_odd = odds.get('home_win', 3.0)
        draw_odd = odds.get('draw', 3.4)
        away_odd = odds.get('away_win', 3.0)
        
        # Probabilidades implícitas
        home_prob = 1 / home_odd if home_odd > 0 else 0.33
        draw_prob = 1 / draw_odd if draw_odd > 0 else 0.33
        away_prob = 1 / away_odd if away_odd > 0 else 0.33
        
        # Margem da casa (overround)
        total_prob = home_prob + draw_prob + away_prob
        margin = total_prob - 1
        
        # Probabilidades "justas" (sem margem)
        if total_prob > 0:
            fair_home_prob = home_prob / total_prob
            fair_draw_prob = draw_prob / total_prob
            fair_away_prob = away_prob / total_prob
        else:
            fair_home_prob = fair_draw_prob = fair_away_prob = 0.33
        
        # Odds over/under
        over_25_odd = odds.get('over_25', 2.0)
        under_25_odd = odds.get('under_25', 2.0)
        
        over_prob = 1 / over_25_odd if over_25_odd > 0 else 0.5
        under_prob = 1 / under_25_odd if under_25_odd > 0 else 0.5
        
        total_ou = over_prob + under_prob
        fair_over_prob = over_prob / total_ou if total_ou > 0 else 0.5
        fair_under_prob = under_prob / total_ou if total_ou > 0 else 0.5
        
        return {
            'market_home_prob': round(fair_home_prob, 3),
            'market_draw_prob': round(fair_draw_prob, 3),
            'market_away_prob': round(fair_away_prob, 3),
            'market_over_prob': round(fair_over_prob, 3),
            'market_under_prob': round(fair_under_prob, 3),
            'bookmaker_margin': round(margin, 3),
            'odds_home': home_odd,
            'odds_draw': draw_odd,
            'odds_away': away_odd,
            'odds_over_25': over_25_odd,
            'odds_under_25': under_25_odd
        }
    
    def _calculate_weather_features(self, weather):
        """
        Extrai features de dados climáticos (Fase 3)
        
        Args:
            weather (dict): Dados climáticos do WeatherService
                {
                    'temp': 18.5,
                    'feels_like': 16.2,
                    'humidity': 75,
                    'condition': 'Rain',
                    'description': 'light rain',
                    'wind_speed': 12.5,
                    'precipitation': 3.2,
                    'cloud_coverage': 80,
                    'impact': 'medium'
                }
        
        Returns:
            dict: Features climáticas processadas
        """
        if not weather:
            return {
                'has_weather': False,
                'weather_impact': 'low',
                'weather_severity': 0.0,
                'has_rain': False,
                'has_snow': False,
                'has_wind': False,
                'temperature': 20.0,
                'condition': 'Clear',
                'goal_impact': 0.0
            }
        
        # Calcular impacto nos gols (redução esperada)
        # Impacto alto: -0.3 a -0.5 gols
        # Impacto médio: -0.1 a -0.3 gols
        # Impacto baixo: 0 a -0.1 gols
        impact_level = weather.get('impact', 'low')
        goal_impact_map = {
            'high': -0.4,
            'medium': -0.2,
            'low': 0.0
        }
        goal_impact = goal_impact_map.get(impact_level, 0.0)
        
        # Severity score (0-10)
        severity = 0.0
        if impact_level == 'high':
            severity = 8.0
        elif impact_level == 'medium':
            severity = 5.0
        elif impact_level == 'low':
            severity = 2.0
        
        return {
            'has_weather': True,
            'weather_impact': impact_level,
            'weather_severity': severity,
            'has_rain': weather.get('condition') in ['Rain', 'Drizzle', 'Thunderstorm'],
            'has_snow': weather.get('condition') == 'Snow',
            'has_wind': weather.get('wind_speed', 0) > 10,
            'temperature': weather.get('temp', 20.0),
            'feels_like': weather.get('feels_like', 20.0),
            'humidity': weather.get('humidity', 50),
            'condition': weather.get('condition', 'Clear'),
            'description': weather.get('description', 'clear sky'),
            'wind_speed': weather.get('wind_speed', 0),
            'precipitation': weather.get('precipitation', 0),
            'cloud_coverage': weather.get('cloud_coverage', 0),
            'goal_impact': goal_impact
        }
    
    def _calculate_variance(self, team_stats):
        """
        VARIÁVEL #23: Variância de performance
        
        Calcula desvio padrão de gols marcados nos últimos jogos
        Menor variância = time mais consistente
        """
        # Tentar obter histórico de gols por jogo
        # Se disponível em team_stats como array
        goals_history = team_stats.get('goals_history', [])
        
        if not goals_history or len(goals_history) < 3:
            # Fallback: usar média e estimar variância conservadora
            goals_per_game = team_stats.get('goals_per_game_avg', 1.5)
            # Assumir variância típica de ~0.8-1.0 para times médios
            return 0.9
        
        # Calcular desvio padrão
        mean = sum(goals_history) / len(goals_history)
        variance = sum((x - mean) ** 2 for x in goals_history) / len(goals_history)
        std_dev = variance ** 0.5
        
        return std_dev
    
    def _calculate_half_performance(self, statistics, side):
        """
        VARIÁVEL #24: Performance 1º Tempo vs 2º Tempo
        
        Calcula % de gols marcados no 1º tempo
        Útil para apostas de intervalo
        """
        if not statistics:
            return 0.5  # 50% default (distribuição uniforme)
        
        # Procurar dados de gols por tempo nas statistics
        team_stats = statistics.get(side, [])
        
        goals_1st_half = 0
        goals_2nd_half = 0
        total_goals = 0
        
        for stat in team_stats:
            stat_type = stat.get('type', '')
            value = stat.get('value', 0)
            
            if 'goals' in stat_type.lower():
                if '1st' in stat_type or 'first' in stat_type:
                    goals_1st_half = int(value) if value else 0
                elif '2nd' in stat_type or 'second' in stat_type:
                    goals_2nd_half = int(value) if value else 0
        
        total_goals = goals_1st_half + goals_2nd_half
        
        if total_goals == 0:
            return 0.5  # Se não marcou gols, assume distribuição uniforme
        
        # Retorna % de gols no 1º tempo
        return goals_1st_half / total_goals
    
    def _calculate_h2h_features(self, h2h_data):
        """
        Features de histórico direto (H2H)
        
        Analisa confrontos diretos anteriores
        """
        if not h2h_data or len(h2h_data) == 0:
            return {
                'h2h_games': 0,
                'h2h_home_wins': 0,
                'h2h_draws': 0,
                'h2h_away_wins': 0,
                'h2h_avg_goals': 0,
                'h2h_btts_rate': 0
            }
        
        total_games = len(h2h_data)
        home_wins = 0
        draws = 0
        away_wins = 0
        total_goals = 0
        btts_games = 0
        
        for match in h2h_data:
            home_goals = match.get('homeTeam', {}).get('score', 0)
            away_goals = match.get('awayTeam', {}).get('score', 0)
            
            if home_goals is None or away_goals is None:
                continue
            
            total_goals += home_goals + away_goals
            
            if home_goals > away_goals:
                home_wins += 1
            elif away_goals > home_goals:
                away_wins += 1
            else:
                draws += 1
            
            if home_goals > 0 and away_goals > 0:
                btts_games += 1
        
        avg_goals = total_goals / total_games if total_games > 0 else 0
        btts_rate = btts_games / total_games if total_games > 0 else 0
        
        return {
            'h2h_games': total_games,
            'h2h_home_wins': home_wins,
            'h2h_draws': draws,
            'h2h_away_wins': away_wins,
            'h2h_home_win_rate': round(home_wins / total_games, 2) if total_games > 0 else 0,
            'h2h_avg_goals': round(avg_goals, 2),
            'h2h_btts_rate': round(btts_rate, 2)
        }
    
    def _calculate_match_importance_features(self, enriched_data, standings):
        """
        Calcula a importância do jogo baseado em:
        - Fase da competição
        - Posição na tabela
        - Distância para objetivos (título, Europa, rebaixamento)
        - Derby/rivalidade
        
        Returns 8 variáveis de importância do jogo
        """
        if standings is None:
            standings = {}
        
        home_standing = standings.get('home', {})
        away_standing = standings.get('away', {})
        
        # Posições na tabela
        home_position = home_standing.get('position', 10)
        away_position = away_standing.get('position', 10)
        
        # Total de times na liga (assumir 20 se não disponível)
        total_teams = home_standing.get('total_teams', 20)
        
        # Calcular distância para zonas críticas
        # Top 4 = Champions League, 5-6 = Europa League, Bottom 3 = Relegation
        home_distance_to_top4 = max(0, home_position - 4)
        away_distance_to_top4 = max(0, away_position - 4)
        
        home_distance_to_relegation = max(0, (total_teams - 2) - home_position)
        away_distance_to_relegation = max(0, (total_teams - 2) - home_position)
        
        # Importância baseada em posição (0-10 scale)
        # Times brigando por título ou contra rebaixamento = alta importância
        def calculate_position_importance(position, total_teams):
            if position <= 4:  # Briga por título/Champions
                return 8 + (4 - position)  # 8-11
            elif position >= total_teams - 3:  # Zona de rebaixamento
                return 7 + (total_teams - position)  # 7-10
            elif position <= 7:  # Briga por Europa League
                return 6
            else:  # Meio de tabela
                return 3
        
        home_importance = calculate_position_importance(home_position, total_teams)
        away_importance = calculate_position_importance(away_position, total_teams)
        
        # Importância combinada do jogo
        match_importance = (home_importance + away_importance) / 2
        
        # Derby detection (se times da mesma cidade/região)
        fixture_data = enriched_data.get('fixture', {})
        home_team_name = fixture_data.get('home_team', '').lower()
        away_team_name = fixture_data.get('away_team', '').lower()
        
        # Detectar derbies conhecidos
        is_derby = self._detect_derby(home_team_name, away_team_name)
        
        # Se é derby, importância aumenta
        if is_derby:
            match_importance = min(10, match_importance + 2)
        
        # Fase da competição (rodadas finais = mais importante)
        league_round = fixture_data.get('round', 'Regular Season - 1')
        try:
            round_number = int(''.join(filter(str.isdigit, league_round)))
        except:
            round_number = 1
        
        # Assumir 38 rodadas (pode variar)
        total_rounds = 38
        season_progress = round_number / total_rounds  # 0-1
        
        # Jogos da última parte da temporada são mais importantes
        season_importance_multiplier = 1.0 + (season_progress * 0.5)  # 1.0 a 1.5
        
        match_importance_adjusted = min(10, match_importance * season_importance_multiplier)
        
        return {
            'home_position': home_position,
            'away_position': away_position,
            'position_differential': abs(home_position - away_position),
            'home_importance': round(home_importance, 1),
            'away_importance': round(away_importance, 1),
            'match_importance': round(match_importance_adjusted, 1),
            'is_derby': is_derby,
            'season_progress': round(season_progress, 2),
            'home_distance_to_top4': home_distance_to_top4,
            'away_distance_to_top4': away_distance_to_top4,
            'home_distance_to_relegation': home_distance_to_relegation,
            'away_distance_to_relegation': away_distance_to_relegation
        }
    
    def _detect_derby(self, home_team, away_team):
        """
        Detecta se é um derby baseado em nomes dos times
        """
        # Derbies famosos
        derbies = [
            ['manchester united', 'manchester city'],
            ['liverpool', 'everton'],
            ['arsenal', 'tottenham'],
            ['chelsea', 'arsenal'],
            ['real madrid', 'atletico madrid'],
            ['barcelona', 'espanyol'],
            ['milan', 'inter'],
            ['roma', 'lazio'],
            ['bayern', 'dortmund'],
            ['boca', 'river'],
            ['benfica', 'sporting'],
            ['porto', 'benfica'],
            ['flamengo', 'fluminense'],
            ['corinthians', 'palmeiras'],
            ['celtic', 'rangers']
        ]
        
        for derby_pair in derbies:
            if (derby_pair[0] in home_team and derby_pair[1] in away_team) or \
               (derby_pair[1] in home_team and derby_pair[0] in away_team):
                return True
        
        return False
    
    def _calculate_injuries_suspensions_features(self, enriched_data):
        """
        Calcula impacto numérico de lesões e suspensões
        
        Features:
        - Número de jogadores indisponíveis por time
        - Impacto ponderado por posição (GK=10, DEF=7, MID=8, ATT=9)
        - Impacto ponderado por importância do jogador (titular vs reserva)
        - Diferencial de impacto entre times
        
        Returns 12 variáveis de lesões/suspensões
        """
        fixture_data = enriched_data.get('fixture', {})
        
        # Dados de lesões vem do enricher (API-Football)
        injuries = fixture_data.get('injuries', [])
        
        home_team = fixture_data.get('home_team', '')
        away_team = fixture_data.get('away_team', '')
        
        home_injured = []
        away_injured = []
        
        for injury in injuries:
            player_team = injury.get('team', {}).get('name', '')
            if home_team.lower() in player_team.lower():
                home_injured.append(injury)
            elif away_team.lower() in player_team.lower():
                away_injured.append(injury)
        
        # Calcular impacto ponderado
        home_impact = self._calculate_injury_impact(home_injured)
        away_impact = self._calculate_injury_impact(away_injured)
        
        impact_differential = home_impact['total_impact'] - away_impact['total_impact']
        
        # Ajustar força baseado em lesões
        # Cada ponto de impacto reduz ~2% da força
        home_strength_adjustment = max(-0.3, -0.02 * home_impact['total_impact'])
        away_strength_adjustment = max(-0.3, -0.02 * away_impact['total_impact'])
        
        return {
            'home_injured_count': home_impact['count'],
            'away_injured_count': away_impact['count'],
            'home_suspended_count': home_impact['suspended_count'],
            'away_suspended_count': away_impact['suspended_count'],
            'home_injury_impact': round(home_impact['total_impact'], 1),
            'away_injury_impact': round(away_impact['total_impact'], 1),
            'injury_impact_differential': round(impact_differential, 1),
            'home_key_players_out': home_impact['key_players_out'],
            'away_key_players_out': away_impact['key_players_out'],
            'home_strength_adjustment': round(home_strength_adjustment, 2),
            'away_strength_adjustment': round(away_strength_adjustment, 2),
            'total_absences': home_impact['count'] + away_impact['count']
        }
    
    def _calculate_injury_impact(self, injuries_list):
        """
        Calcula impacto ponderado de lesões
        
        Pesos por posição:
        - GK (Goleiro): 10 (mais crítico)
        - DEF (Defesa): 7
        - MID (Meio-campo): 8
        - ATT (Atacante): 9
        
        Peso por tipo de jogador:
        - Titular: peso × 1.0
        - Reserva importante: peso × 0.5
        - Reserva: peso × 0.3
        """
        if not injuries_list:
            return {
                'count': 0,
                'suspended_count': 0,
                'total_impact': 0,
                'key_players_out': 0
            }
        
        position_weights = {
            'Goalkeeper': 10,
            'Defender': 7,
            'Midfielder': 8,
            'Attacker': 9
        }
        
        total_impact = 0
        key_players_out = 0
        suspended_count = 0
        
        for injury in injuries_list:
            player = injury.get('player', {})
            position = player.get('type', 'Midfielder')  # Default midfielder
            reason = injury.get('player', {}).get('reason', '').lower()
            
            # Detectar suspensão
            if 'suspend' in reason or 'yellow card' in reason or 'red card' in reason:
                suspended_count += 1
            
            # Peso base da posição
            base_weight = position_weights.get(position, 7)
            
            # Ajustar por importância do jogador (heurística)
            # Se tiver "key", "star", "captain" no nome/descrição = titular
            player_name = player.get('name', '').lower()
            is_key_player = any(word in player_name for word in ['captain', 'star']) or \
                           any(word in reason for word in ['key', 'important'])
            
            if is_key_player:
                importance_multiplier = 1.0
                key_players_out += 1
            else:
                importance_multiplier = 0.5  # Assumir reserva
            
            total_impact += base_weight * importance_multiplier
        
        return {
            'count': len(injuries_list),
            'suspended_count': suspended_count,
            'total_impact': total_impact,
            'key_players_out': key_players_out
        }
    
    def _calculate_motivation_features(self, standings, enriched_data):
        """
        Calcula motivação dos times baseado em objetivos da temporada
        
        Motivação vem de:
        - Distância para título (top 1-3)
        - Distância para Champions League (top 4)
        - Distância para Europa League (top 5-6)
        - Perigo de rebaixamento (bottom 3)
        - Sequência de resultados (pressão)
        
        Returns 10 variáveis de motivação
        """
        if standings is None:
            return {
                'home_motivation': 5.0,
                'away_motivation': 5.0,
                'motivation_differential': 0,
                'home_title_pressure': False,
                'away_title_pressure': False,
                'home_relegation_pressure': False,
                'away_relegation_pressure': False,
                'home_objective': 'mid_table',
                'away_objective': 'mid_table',
                'combined_pressure': 5.0
            }
        
        home_standing = standings.get('home', {})
        away_standing = standings.get('away', {})
        
        home_position = home_standing.get('position', 10)
        away_position = away_standing.get('position', 10)
        total_teams = home_standing.get('total_teams', 20)
        
        # Pontos
        home_points = home_standing.get('points', 0)
        away_points = away_standing.get('points', 0)
        
        # Calcular motivação (escala 1-10)
        def calculate_team_motivation(position, points, total_teams):
            """
            10 = Máxima motivação (luta por título ou contra rebaixamento)
            1 = Mínima motivação (meio de tabela sem objetivos)
            """
            # Zona de título (1-3)
            if position <= 3:
                # Quanto mais perto do topo, mais motivação
                return min(10, 9 + (3 - position))
            
            # Zona Champions (4-5)
            elif position <= 5:
                return 8
            
            # Zona Europa League (6-7)
            elif position <= 7:
                return 7
            
            # Zona de rebaixamento (últimos 3)
            elif position >= total_teams - 2:
                # Quanto mais fundo, mais motivação
                distance_from_bottom = total_teams - position
                return min(10, 8 + (3 - distance_from_bottom))
            
            # Próximo da zona de rebaixamento (últimos 5-7)
            elif position >= total_teams - 6:
                return 6
            
            # Meio de tabela
            else:
                return 4
        
        home_motivation = calculate_team_motivation(home_position, home_points, total_teams)
        away_motivation = calculate_team_motivation(away_position, away_points, total_teams)
        
        # Detectar pressões específicas
        home_title_pressure = home_position <= 3
        away_title_pressure = away_position <= 3
        
        home_relegation_pressure = home_position >= total_teams - 5
        away_relegation_pressure = away_position >= total_teams - 5
        
        # Objetivos
        def determine_objective(position, total_teams):
            if position <= 1:
                return 'title'
            elif position <= 4:
                return 'champions_league'
            elif position <= 7:
                return 'europa_league'
            elif position >= total_teams - 2:
                return 'avoid_relegation'
            else:
                return 'mid_table'
        
        home_objective = determine_objective(home_position, total_teams)
        away_objective = determine_objective(away_position, total_teams)
        
        # Pressão combinada do jogo
        combined_pressure = (home_motivation + away_motivation) / 2
        
        # Diferencial de motivação (importante para prever resultado)
        motivation_differential = home_motivation - away_motivation
        
        # Forma recente afeta motivação
        home_form = home_standing.get('form', '')
        away_form = away_standing.get('form', '')
        
        # Se está em má fase E em zona de perigo = motivação extra
        home_bad_form = home_form.count('L') > 2 if home_form else False
        away_bad_form = away_form.count('L') > 2 if away_form else False
        
        if home_bad_form and home_relegation_pressure:
            home_motivation = min(10, home_motivation + 1)
        
        if away_bad_form and away_relegation_pressure:
            away_motivation = min(10, away_motivation + 1)
        
        return {
            'home_motivation': round(home_motivation, 1),
            'away_motivation': round(away_motivation, 1),
            'motivation_differential': round(motivation_differential, 1),
            'home_title_pressure': home_title_pressure,
            'away_title_pressure': away_title_pressure,
            'home_relegation_pressure': home_relegation_pressure,
            'away_relegation_pressure': away_relegation_pressure,
            'home_objective': home_objective,
            'away_objective': away_objective,
            'combined_pressure': round(combined_pressure, 1)
        }

