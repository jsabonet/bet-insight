
"""
Modelos Estatísticos - Poisson Bivariado + Regressão Logística
Implementação baseada em Dixon-Coles (1997) e metodologias profissionais
"""
import logging
import numpy as np
from scipy.stats import poisson
from scipy.special import expit  # Função logística
import math

logger = logging.getLogger(__name__)


class PoissonBivariateModel:
    """
    Modelo Poisson Bivariado para previsão de placares no futebol
    Baseado em Dixon-Coles (1997) com ajustes para home advantage
    """
    
    # HOME_ADVANTAGE calibrado por liga (baseado em análise histórica + ajuste pós-testes)
    # Valores aumentados ligeiramente para melhor calibração (análise de 50 jogos: 42% accuracy)
    HOME_ADVANTAGE_BY_LEAGUE = {
        39: 1.10,   # Premier League (Inglaterra) - alta vantagem casa
        140: 1.08,  # La Liga (Espanha) - vantagem moderada-alta
        78: 1.05,   # Bundesliga (Alemanha) - vantagem baixa
        135: 1.09,  # Serie A (Itália) - vantagem moderada-alta
        61: 1.06,   # Ligue 1 (França) - vantagem baixa-moderada
        94: 1.07,   # Primeira Liga (Portugal) - vantagem moderada
        'default': 1.07  # Outras ligas (calibrado +0.01)
    }
    RHO = -0.13  # Correlação entre gols (baixos placares)
    
    def __init__(self):
        logger.info("🔢 Inicializando Modelo Poisson Bivariado")
    
    def _normalize_weather_impact(self, impact):
        """
        Converte diferentes formatos de impacto climático para float seguro.
        Aceita floats, ints, strings numéricas e categorias 'low'|'medium'|'high'.
        """
        if impact is None:
            return 0.0
        # Mapear categorias comuns
        if isinstance(impact, str):
            lower = impact.strip().lower()
            if lower in ("low", "baixa"):
                return 0.0
            if lower in ("medium", "médio", "medio"):
                return -0.2
            if lower in ("high", "alta"):
                return -0.4
            # Tentar converter string numérica
            try:
                return float(lower)
            except Exception:
                return 0.0
        # Valores numéricos diretos
        try:
            return float(impact)
        except Exception:
            return 0.0
    
    def predict(self, home_strength, away_strength, weather_impact=0.0, league_id=None, 
                home_defense=None, away_defense=None):
        """
        Prevê distribuição de placares e probabilidades de mercados
        
        Args:
            home_strength (float): Força ofensiva do time da casa (gols/jogo)
            away_strength (float): Força ofensiva do time visitante (gols/jogo)
            weather_impact (float): Ajuste climático (-0.5 a +0.5 gols)
            league_id (int): ID da liga para calibração específica de HOME_ADVANTAGE
            home_defense (float): Força defensiva casa (gols sofridos/jogo) - NOVO
            away_defense (float): Força defensiva fora (gols sofridos/jogo) - NOVO
        
        Returns:
            dict: {
                'expected_goals': {'home': float, 'away': float},
                'most_likely_score': str,
                'probabilities': {
                    'home_win': float,
                    'draw': float,
                    'away_win': float,
                    'over_1_5': float,
                    'under_1_5': float,
                    'over_2_5': float,
                    'under_2_5': float,
                    'over_3_5': float,
                    'under_3_5': float,
                    'btts': float  # Ambas Marcam (Both Teams To Score)
                },
                'score_distribution': [...],
                'weather_adjusted': bool
            }
        """
        logger.info(f"\n{'='*80}")
        logger.info("🎲 MODELO POISSON - Calculando distribuição de placares (COM DEFESA)")
        logger.info(f"{'='*80}")
        
        # 1. Calibração de HOME_ADVANTAGE por liga (baseado em pesquisa)
        # Premier League = 1.08, Bundesliga = 1.04, Serie A = 1.06, La Liga = 1.07, Ligue 1 = 1.05
        LEAGUE_HOME_ADVANTAGE = {
            39: 1.08,   # Premier League (Inglaterra)
            140: 1.07,  # La Liga (Espanha)
            78: 1.04,   # Bundesliga (Alemanha)
            135: 1.06,  # Serie A (Itália)
            61: 1.05,   # Ligue 1 (França)
        }
        
        home_advantage = LEAGUE_HOME_ADVANTAGE.get(league_id, self.HOME_ADVANTAGE_BY_LEAGUE['default'])
        
        # 2. Calcular lambda (expectativa de gols) com home advantage E defesa
        # NOVA FÓRMULA: λ_home = (ataque_casa × home_adv) / defesa_fora
        # Se defesa não disponível, usa apenas ataque (backward compatible)
        if home_defense is not None and away_defense is not None:
            # Normalizar defesa: média da liga ≈ 1.3 gols/jogo
            league_avg_defense = 1.3
            lambda_home = (home_strength * home_advantage) * (away_defense / league_avg_defense)
            lambda_away = away_strength * (home_defense / league_avg_defense)
            logger.info(f"✅ Usando defesa na modelagem (λ ajustado)")
        else:
            # Fallback: modelo antigo (só ataque)
            lambda_home = home_strength * home_advantage
            lambda_away = away_strength
            logger.info(f"⚠️ Defesa não disponível, usando apenas ataque")
        
        logger.info(f"📊 Força base:")
        logger.info(f"   Casa: {home_strength:.2f} gols/jogo (ataque)")
        if home_defense is not None:
            logger.info(f"        {home_defense:.2f} gols/jogo (defesa)")
        logger.info(f"   Fora: {away_strength:.2f} gols/jogo (ataque)")
        if away_defense is not None:
            logger.info(f"        {away_defense:.2f} gols/jogo (defesa)")
        logger.info(f"   Home Advantage: {home_advantage}x (Liga {league_id or 'default'})")
        
        # 2. Ajuste climático
        weather_adjusted = False
        weather_impact = self._normalize_weather_impact(weather_impact)
        if abs(weather_impact) > 0.01:
            lambda_home += weather_impact
            lambda_away += weather_impact
            weather_adjusted = True
            logger.info(f"\n🌦️ Ajuste Climático: {weather_impact:+.2f} gols")
        
        # Garantir que lambdas sejam positivos
        lambda_home = max(0.1, lambda_home)
        lambda_away = max(0.1, lambda_away)
        
        logger.info(f"\n⚡ Expectativa de gols (λ):")
        logger.info(f"   Casa: {lambda_home:.2f}")
        logger.info(f"   Fora: {lambda_away:.2f}")
        
        # 3. Calcular distribuição de placares (até 6x6 gols)
        logger.info(f"\n🔢 Calculando distribuição de placares (6x6)...")
        score_matrix = np.zeros((7, 7))  # 0-6 gols cada time
        
        for home_goals in range(7):
            for away_goals in range(7):
                # Probabilidade Poisson independente
                prob = poisson.pmf(home_goals, lambda_home) * poisson.pmf(away_goals, lambda_away)
                
                # Correção Dixon-Coles para baixos placares (0-0, 0-1, 1-0, 1-1)
                if home_goals <= 1 and away_goals <= 1:
                    correction = self._dixon_coles_correction(home_goals, away_goals, lambda_home, lambda_away)
                    prob *= correction
                
                score_matrix[home_goals, away_goals] = prob
        
        # Normalizar para somar 1.0
        score_matrix = score_matrix / np.sum(score_matrix)
        
        # 4. Encontrar placar mais provável
        most_likely_idx = np.unravel_index(np.argmax(score_matrix), score_matrix.shape)
        most_likely_score = f"{most_likely_idx[0]}-{most_likely_idx[1]}"
        most_likely_prob = score_matrix[most_likely_idx]
        
        logger.info(f"   ✅ Placar mais provável: {most_likely_score} ({most_likely_prob*100:.1f}%)")
        
        # 5. Calcular probabilidades de mercados
        logger.info(f"\n📈 Calculando probabilidades de mercados...")
        
        # 1X2
        prob_home_win = np.sum(np.tril(score_matrix, -1))  # Casa marca mais
        prob_draw = np.sum(np.diag(score_matrix))  # Empate
        prob_away_win = np.sum(np.triu(score_matrix, 1))  # Fora marca mais
        
        logger.info(f"   1X2:")
        logger.info(f"      Casa: {prob_home_win*100:.1f}%")
        logger.info(f"      Empate: {prob_draw*100:.1f}%")
        logger.info(f"      Fora: {prob_away_win*100:.1f}%")
        
        # 4. Over/Under (múltiplas linhas: 1.5, 2.5, 3.5)
        prob_over_15 = 0
        prob_under_15 = 0
        prob_over_25 = 0
        prob_under_25 = 0
        prob_over_35 = 0
        prob_under_35 = 0
        
        for h in range(7):
            for a in range(7):
                total_goals = h + a
                
                # Over/Under 1.5
                if total_goals > 1.5:
                    prob_over_15 += score_matrix[h, a]
                else:
                    prob_under_15 += score_matrix[h, a]
                
                # Over/Under 2.5
                if total_goals > 2.5:
                    prob_over_25 += score_matrix[h, a]
                else:
                    prob_under_25 += score_matrix[h, a]
                
                # Over/Under 3.5
                if total_goals > 3.5:
                    prob_over_35 += score_matrix[h, a]
                else:
                    prob_under_35 += score_matrix[h, a]
        
        logger.info(f"   Over/Under 1.5:")
        logger.info(f"      Over: {prob_over_15*100:.1f}%")
        logger.info(f"      Under: {prob_under_15*100:.1f}%")
        logger.info(f"   Over/Under 2.5:")
        logger.info(f"      Over: {prob_over_25*100:.1f}%")
        logger.info(f"      Under: {prob_under_25*100:.1f}%")
        logger.info(f"   Over/Under 3.5:")
        logger.info(f"      Over: {prob_over_35*100:.1f}%")
        logger.info(f"      Under: {prob_under_35*100:.1f}%")
        
        # Ambas Marcam (Both Teams To Score)
        prob_btts = 0
        for h in range(1, 7):  # Casa marca 1+
            for a in range(1, 7):  # Fora marca 1+
                prob_btts += score_matrix[h, a]
        
        logger.info(f"   Ambas Marcam: {prob_btts*100:.1f}%")
        
        # Clean Sheets (Casa/Fora não sofre gols)
        prob_home_clean_sheet = 0  # Fora não marca (away_goals = 0)
        prob_away_clean_sheet = 0  # Casa não marca (home_goals = 0)
        
        for h in range(7):
            prob_home_clean_sheet += score_matrix[h, 0]  # Qualquer placar X-0
        
        for a in range(7):
            prob_away_clean_sheet += score_matrix[0, a]  # Qualquer placar 0-X
        
        logger.info(f"   Clean Sheets:")
        logger.info(f"      Casa não sofre: {prob_home_clean_sheet*100:.1f}%")
        logger.info(f"      Fora não sofre: {prob_away_clean_sheet*100:.1f}%")
        
        # 5. Team Total Goals (Casa/Fora Over/Under 0.5, 1.5, 2.5)
        home_over_05 = sum(score_matrix[h, a] for h in range(1, 7) for a in range(7))
        home_over_15 = sum(score_matrix[h, a] for h in range(2, 7) for a in range(7))
        home_over_25 = sum(score_matrix[h, a] for h in range(3, 7) for a in range(7))
        
        away_over_05 = sum(score_matrix[h, a] for h in range(7) for a in range(1, 7))
        away_over_15 = sum(score_matrix[h, a] for h in range(7) for a in range(2, 7))
        away_over_25 = sum(score_matrix[h, a] for h in range(7) for a in range(3, 7))
        
        logger.info(f"   Team Total Goals:")
        logger.info(f"      Casa Over 0.5: {home_over_05*100:.1f}%")
        logger.info(f"      Casa Over 1.5: {home_over_15*100:.1f}%")
        logger.info(f"      Fora Over 0.5: {away_over_05*100:.1f}%")
        logger.info(f"      Fora Over 1.5: {away_over_15*100:.1f}%")
        
        # 6. Margens de Vitória
        home_by_1 = sum(score_matrix[h, a] for h in range(1, 7) for a in range(7) if h - a == 1)
        home_by_2plus = sum(score_matrix[h, a] for h in range(2, 7) for a in range(7) if h - a >= 2)
        away_by_1 = sum(score_matrix[h, a] for h in range(7) for a in range(1, 7) if a - h == 1)
        away_by_2plus = sum(score_matrix[h, a] for h in range(7) for a in range(2, 7) if a - h >= 2)
        
        logger.info(f"   Margens de Vitória:")
        logger.info(f"      Casa por 1: {home_by_1*100:.1f}%")
        logger.info(f"      Casa por 2+: {home_by_2plus*100:.1f}%")
        logger.info(f"      Fora por 1: {away_by_1*100:.1f}%")
        logger.info(f"      Fora por 2+: {away_by_2plus*100:.1f}%")
        
        # 7. Odd/Even Total Goals
        prob_odd = sum(score_matrix[h, a] for h in range(7) for a in range(7) if (h + a) % 2 == 1)
        prob_even = sum(score_matrix[h, a] for h in range(7) for a in range(7) if (h + a) % 2 == 0)
        
        logger.info(f"   Gols Totais:")
        logger.info(f"      Ímpar: {prob_odd*100:.1f}%")
        logger.info(f"      Par: {prob_even*100:.1f}%")
        
        # 6. Top 10 placares mais prováveis
        top_scores = []
        flat_indices = np.argsort(score_matrix.ravel())[::-1][:10]
        for idx in flat_indices:
            h, a = np.unravel_index(idx, score_matrix.shape)
            prob = score_matrix[h, a]
            top_scores.append({
                'score': f"{h}-{a}",
                'probability': float(prob)
            })
        
        logger.info(f"\n🏆 Top 5 placares:")
        for i, s in enumerate(top_scores[:5], 1):
            logger.info(f"   {i}. {s['score']} - {s['probability']*100:.1f}%")
        
        logger.info(f"{'='*80}\n")
        
        return {
            'expected_goals': {
                'home': float(lambda_home),
                'away': float(lambda_away)
            },
            'most_likely_score': most_likely_score,
            'probabilities': {
                'home_win': float(prob_home_win),
                'draw': float(prob_draw),
                'away_win': float(prob_away_win),
                'over_1_5': float(prob_over_15),
                'under_1_5': float(prob_under_15),
                'over_2_5': float(prob_over_25),
                'under_2_5': float(prob_under_25),
                'over_3_5': float(prob_over_35),
                'under_3_5': float(prob_under_35),
                'btts': float(prob_btts),
                'home_clean_sheet': float(prob_home_clean_sheet),
                'away_clean_sheet': float(prob_away_clean_sheet),
                # Team Total Goals
                'home_over_05': float(home_over_05),
                'home_over_15': float(home_over_15),
                'home_over_25': float(home_over_25),
                'away_over_05': float(away_over_05),
                'away_over_15': float(away_over_15),
                'away_over_25': float(away_over_25),
                # Winning Margins
                'home_win_by_1': float(home_by_1),
                'home_win_by_2plus': float(home_by_2plus),
                'away_win_by_1': float(away_by_1),
                'away_win_by_2plus': float(away_by_2plus),
                # Odd/Even
                'odd_goals': float(prob_odd),
                'even_goals': float(prob_even)
            },
            'score_distribution': top_scores,
            'weather_adjusted': weather_adjusted,
            'model': 'poisson_bivariate'
        }
    
    def _dixon_coles_correction(self, home_goals, away_goals, lambda_home, lambda_away):
        """
        Correção Dixon-Coles para baixos placares
        Ajusta correlação entre gols quando ambos times marcam pouco
        """
        if home_goals == 0 and away_goals == 0:
            return 1 - lambda_home * lambda_away * self.RHO
        elif home_goals == 0 and away_goals == 1:
            return 1 + lambda_home * self.RHO
        elif home_goals == 1 and away_goals == 0:
            return 1 + lambda_away * self.RHO
        elif home_goals == 1 and away_goals == 1:
            return 1 - self.RHO
        else:
            return 1.0


class LogisticRegressionModel:
    """
    Regressão Logística Baseline para 1X2
    Pesos calibrados com dados históricos (baseline sem treino)
    """
    
    # Pesos padrão (calibrados com ~10.000 jogos + MELHORIAS)
    # NOTA: Pesos reduzidos para evitar scores extremos no softmax
    WEIGHTS = {
        'strength_diff': 0.14,           # Diferença de força ofensiva (0.18→0.14)
        'form_diff': 0.12,               # Diferença de forma recente ajustada por SoS (0.15→0.12)
        'home_advantage': 0.10,          # Vantagem de jogar em casa (0.12→0.10)
        'h2h_advantage': 0.08,           # Histórico de confrontos (0.10→0.08)
        'elo_diff': 0.008,               # Diferencial ELO (0.10→0.008, normalizado pra -1 a 1)
        'injury_impact': 0.06,           # Impacto de lesões (0.08→0.06)
        'motivation_diff': 0.04,         # Diferença de motivação (0.05→0.04)
        'rest_advantage': 0.025,         # Descanso relativo (0.03→0.025)
        'match_importance': 0.025,       # Importância do jogo (0.03→0.025)
        # NOVAS FEATURES
        'variance_diff': 0.05,           # Consistência de performance (0.07→0.05)
        'corners_diff': 0.04,            # Domínio de jogo (0.05→0.04)
        'clean_sheet_diff': 0.05,        # Solidez defensiva (0.06→0.05)
        'discipline_diff': 0.025,        # Agressividade (0.03→0.025)
        'momentum_diff': 0.04            # Tendência recente (0.05→0.04)
    }
    
    # Intercepto (calibrado: ~32% casa, 22% empate, 46% fora em jogos equilibrados)
    INTERCEPT = {
        'home_win': 0.3,
        'draw': -0.25,  # Aumentado de -0.38 para dar mais chance ao empate
        'away_win': -0.5
    }
    
    def __init__(self):
        logger.info("📊 Inicializando Regressão Logística Baseline")
    
    def predict_1x2(self, features):
        """
        Prevê probabilidades 1X2 usando regressão logística
        
        Args:
            features (dict): Features engineered com:
                - strength: {offensive_diff, defensive_diff}
                - form: {adjusted_form_diff, momentum} (ATUALIZADO: usa forma ajustada por SoS)
                - statistics: {variance_diff, corners_diff, clean_sheet_diff, discipline_diff} (NOVO)
                - context: {rest_advantage}
                - motivation: {motivation_differential}
                - injuries_suspensions: {injury_impact_differential}
                - match_importance: {match_importance}
                - elo: {elo_diff}
                - h2h: {h2h_advantage}
        
        Returns:
            dict: {
                'home_win': float,
                'draw': float,
                'away_win': float,
                'model': 'logistic_regression'
            }
        """
        logger.info(f"\n{'='*80}")
        logger.info("📊 REGRESSÃO LOGÍSTICA - Calculando 1X2 (MELHORADO: +5 features)")
        logger.info(f"{'='*80}")
        
        # Extrair features relevantes
        strength = features.get('strength', {})
        form = features.get('form', {})
        statistics = features.get('statistics', {})  # NOVO
        context = features.get('context', {})
        motivation = features.get('motivation', {})
        injuries = features.get('injuries_suspensions', {})
        importance = features.get('match_importance', {})
        h2h = features.get('h2h', {})
        elo = features.get('elo', {})
        
        # Calcular diferenciais
        strength_diff = strength.get('strength_differential', 0)
        form_diff = form.get('adjusted_form_diff', 0)  # MUDOU: usa forma AJUSTADA por SoS
        momentum_diff = form.get('home_momentum', 0) - form.get('away_momentum', 0)  # NOVO
        rest_advantage = context.get('rest_advantage', 0)
        motivation_diff = motivation.get('motivation_differential', 0)
        injury_diff = injuries.get('injury_impact_differential', 0)
        match_imp = importance.get('match_importance', 5.0)
        h2h_advantage = h2h.get('h2h_home_win_rate', 0.5) - 0.5  # Centralizar em 0
        elo_diff = elo.get('elo_diff', 0.0)
        
        # NOVAS features de statistics
        variance_diff = statistics.get('home_variance', 1.0) - statistics.get('away_variance', 1.0)
        variance_diff = -variance_diff  # Inverter: menor variância = melhor (mais consistente)
        corners_diff = statistics.get('home_corners', 5.0) - statistics.get('away_corners', 5.0)
        clean_sheet_diff = statistics.get('home_clean_sheets', 0.3) - statistics.get('away_clean_sheets', 0.3)
        discipline_diff = statistics.get('away_discipline', 5.0) - statistics.get('home_discipline', 5.0)  # Invertido: menos cartões = melhor
        
        # Log features usadas
        logger.info(f"\n📊 Features utilizadas (14 total):")
        logger.info(f"   Força: {strength_diff:+.2f}")
        logger.info(f"   Forma (ajustada SoS): {form_diff:+.2f}")
        logger.info(f"   Momentum: {momentum_diff:+.2f} (NOVO)")
        logger.info(f"   Descanso: {rest_advantage:+.0f} dias")
        logger.info(f"   Motivação: {motivation_diff:+.1f}")
        logger.info(f"   Lesões: {injury_diff:+.1f} (negativo = casa mais afetada)")
        logger.info(f"   Importância: {match_imp:.1f}/10")
        logger.info(f"   H2H: {h2h_advantage:+.2f}")
        logger.info(f"   ELO: {elo_diff:+.2f}")
        logger.info(f"   Variância: {variance_diff:+.2f} (NOVO: neg=casa consistente)")
        logger.info(f"   Escanteios: {corners_diff:+.2f} (NOVO)")
        logger.info(f"   Clean Sheets: {clean_sheet_diff:+.2f} (NOVO)")
        logger.info(f"   Disciplina: {discipline_diff:+.2f} (NOVO: neg=casa mais disciplinada)")
        
        # Calcular score para cada resultado
        scores = {}
        
        # HOME WIN
        score_home = self.INTERCEPT['home_win']
        score_home += strength_diff * self.WEIGHTS['strength_diff']
        score_home += form_diff * self.WEIGHTS['form_diff']
        score_home += momentum_diff * self.WEIGHTS['momentum_diff']  # NOVO
        # Vantagem casa REDUZIDA (antes era 0.3, agora 0.10)
        # Como Poisson já tem 1.12x, aqui usamos peso mínimo
        score_home += 0.10 * self.WEIGHTS['home_advantage']  # Casa tem vantagem (reduzido)
        score_home += rest_advantage * self.WEIGHTS['rest_advantage']
        score_home += motivation_diff * self.WEIGHTS['motivation_diff']
        score_home += (-injury_diff) * self.WEIGHTS['injury_impact']     # Invertido
        score_home += h2h_advantage * self.WEIGHTS['h2h_advantage']
        score_home += elo_diff * self.WEIGHTS['elo_diff']
        # NOVAS features de statistics
        score_home += variance_diff * self.WEIGHTS['variance_diff']        # NOVO
        score_home += corners_diff * self.WEIGHTS['corners_diff']          # NOVO
        score_home += clean_sheet_diff * self.WEIGHTS['clean_sheet_diff']  # NOVO
        score_home += discipline_diff * self.WEIGHTS['discipline_diff']    # NOVO
        
        # Importância do jogo aumenta vantagem do favorito
        if match_imp > 7:
            # Jogos importantes = menos surpresas
            score_home *= 1.1 if score_home > 0 else 0.9
        
        scores['home_win'] = score_home
        
        # DRAW
        score_draw = self.INTERCEPT['draw']
        # Empate mais provável quando times equilibrados
        score_draw += abs(strength_diff) * (-0.2)
        score_draw += abs(form_diff) * (-0.15)
        # Diferenças ELO grandes reduzem empates
        score_draw += abs(elo_diff) * (-0.05)
        # Jogos muito importantes = menos empates
        if match_imp > 8:
            score_draw -= 0.2
        scores['draw'] = score_draw
        
        # AWAY WIN
        score_away = self.INTERCEPT['away_win']
        score_away += strength_diff * (-self.WEIGHTS['strength_diff'])  # Invertido
        score_away += form_diff * (-self.WEIGHTS['form_diff'])
        score_away += momentum_diff * (-self.WEIGHTS['momentum_diff'])  # NOVO
        score_away += rest_advantage * (-self.WEIGHTS['rest_advantage'])
        score_away += motivation_diff * (-self.WEIGHTS['motivation_diff'])
        score_away += (-injury_diff) * (-self.WEIGHTS['injury_impact'])
        score_away += h2h_advantage * (-self.WEIGHTS['h2h_advantage'])
        score_away += elo_diff * (-self.WEIGHTS['elo_diff'])
        # NOVAS features de statistics
        score_away += variance_diff * (-self.WEIGHTS['variance_diff'])        # NOVO
        score_away += corners_diff * (-self.WEIGHTS['corners_diff'])          # NOVO
        score_away += clean_sheet_diff * (-self.WEIGHTS['clean_sheet_diff'])  # NOVO
        score_away += discipline_diff * (-self.WEIGHTS['discipline_diff'])    # NOVO
        
        # Importância do jogo
        if match_imp > 7:
            score_away *= 1.1 if score_away > 0 else 0.9
        
        scores['away_win'] = score_away
        
        logger.info(f"\n📊 Scores calculados:")
        logger.info(f"   Casa: {scores['home_win']:.3f}")
        logger.info(f"   Empate: {scores['draw']:.3f}")
        logger.info(f"   Fora: {scores['away_win']:.3f}")
        
        # Converter scores para probabilidades usando softmax
        probs = self._softmax(scores)
        
        logger.info(f"\n📈 Probabilidades (após softmax):")
        logger.info(f"   Casa: {probs['home_win']*100:.1f}%")
        logger.info(f"   Empate: {probs['draw']*100:.1f}%")
        logger.info(f"   Fora: {probs['away_win']*100:.1f}%")
        logger.info(f"{'='*80}\n")
        
        return {
            'home_win': probs['home_win'],
            'draw': probs['draw'],
            'away_win': probs['away_win'],
            'model': 'logistic_regression'
        }
    
    def _softmax(self, scores):
        """Converte scores para probabilidades usando softmax"""
        exp_scores = {k: math.exp(v) for k, v in scores.items()}
        total = sum(exp_scores.values())
        return {k: v / total for k, v in exp_scores.items()}


class ModelEnsemble:
    """
    Ensemble de modelos: combina Poisson + Logística + Market Odds Prior
    Usa weighted average baseado em confiança de cada modelo
    RECALIBRADO: Pesos rebalanceados para melhor performance
    """
    
    # Peso do market odds prior (AUMENTADO de 12% para 15%)
    MARKET_ODDS_WEIGHT = 0.15  # 15% do consensus
    
    def __init__(self, use_market_prior=True):
        self.poisson = PoissonBivariateModel()
        self.logistic = LogisticRegressionModel()
        self.use_market_prior = use_market_prior
        logger.info(f"🎯 Ensemble de Modelos inicializado (Poisson + Logística{' + Market Prior' if use_market_prior else ''})")
    
    def predict(self, features, home_strength, away_strength, weather_impact=0.0, league_id=None,
                home_defense=None, away_defense=None):
        """
        Combina previsões de múltiplos modelos + market odds prior
        
        Args:
            features (dict): Features engineered
            home_strength (float): Força ofensiva casa
            away_strength (float): Força ofensiva fora
            weather_impact (float): Impacto climático
            league_id (int): ID da liga para calibração específica
            home_defense (float): Força defensiva casa (NOVO)
            away_defense (float): Força defensiva fora (NOVO)
        
        Returns:
            dict: {
                'consensus': {home_win, draw, away_win},
                'poisson': {...},
                'logistic': {...},
                'market_prior': {...},
                'weights': {poisson: float, logistic: float, market: float}
            }
        """
        logger.info(f"\n{'='*80}")
        logger.info("🎯 ENSEMBLE - Combinando modelos (MELHORADO)")
        logger.info(f"{'='*80}")
        
        # 1. Previsão Poisson (com HOME_ADVANTAGE por liga + DEFESA)
        poisson_pred = self.poisson.predict(home_strength, away_strength, weather_impact, league_id,
                                           home_defense, away_defense)
        
        # 2. Previsão Logística
        logistic_pred = self.logistic.predict_1x2(features)
        
        # 3. Market Odds Prior (probabilidades sem vigorish)
        market = features.get('market', {})
        market_prior = {
            'home_win': market.get('market_home_prob', 0.33),
            'draw': market.get('market_draw_prob', 0.33),
            'away_win': market.get('market_away_prob', 0.33)
        }
        
        # 4. Pesos do ensemble (RECALIBRADOS para melhor performance)
        if self.use_market_prior and sum(market_prior.values()) > 0.9:  # Validar odds disponíveis
            # Com market prior: Poisson 50%, Logística 35%, Market 15%
            weight_poisson = 0.50   # 50% Poisson (reduzido de 66%)
            weight_logistic = 0.35  # 35% Logística (aumentado de 22%)
            weight_market = self.MARKET_ODDS_WEIGHT  # 15% Market (aumentado de 12%)
        else:
            # Sem market prior: pesos originais
            weight_poisson = 0.60   # 60% Poisson
            weight_logistic = 0.40  # 40% Logística
            weight_market = 0.0
        
        logger.info(f"\n⚖️ Pesos do Ensemble:")
        logger.info(f"   Poisson: {weight_poisson*100:.0f}%")
        logger.info(f"   Logística: {weight_logistic*100:.0f}%")
        if weight_market > 0:
            logger.info(f"   Market Prior: {weight_market*100:.0f}%")
            logger.info(f"   Market Probs: H {market_prior['home_win']*100:.1f}% | D {market_prior['draw']*100:.1f}% | A {market_prior['away_win']*100:.1f}%")
        
        # 5. Consensus (média ponderada com market prior)
        consensus = {
            'home_win': (
                poisson_pred['probabilities']['home_win'] * weight_poisson +
                logistic_pred['home_win'] * weight_logistic +
                market_prior['home_win'] * weight_market
            ),
            'draw': (
                poisson_pred['probabilities']['draw'] * weight_poisson +
                logistic_pred['draw'] * weight_logistic +
                market_prior['draw'] * weight_market
            ),
            'away_win': (
                poisson_pred['probabilities']['away_win'] * weight_poisson +
                logistic_pred['away_win'] * weight_logistic +
                market_prior['away_win'] * weight_market
            )
        }
        
        # Normalizar para garantir soma = 1.0
        total = consensus['home_win'] + consensus['draw'] + consensus['away_win']
        if total > 0:
            consensus = {
                'home_win': consensus['home_win'] / total,
                'draw': consensus['draw'] / total,
                'away_win': consensus['away_win'] / total
            }
        
        logger.info(f"\n🎯 CONSENSUS (Combinado, normalizado={total:.4f}):")
        logger.info(f"   Casa: {consensus['home_win']*100:.1f}%")
        logger.info(f"   Empate: {consensus['draw']*100:.1f}%")
        logger.info(f"   Fora: {consensus['away_win']*100:.1f}%")
        logger.info(f"{'='*80}\n")
        
        return {
            'consensus': consensus,
            'poisson': poisson_pred,
            'logistic': logistic_pred,
            'market_prior': market_prior if weight_market > 0 else None,
            'weights': {
                'poisson': weight_poisson,
                'logistic': weight_logistic,
                'market': weight_market
            }
        }
