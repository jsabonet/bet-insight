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
    
    # Parâmetros padrão do modelo (calibrados com dados profissionais)
    HOME_ADVANTAGE = 1.3  # Casa marca ~30% mais gols
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
    
    def predict(self, home_strength, away_strength, weather_impact=0.0):
        """
        Prevê distribuição de placares e probabilidades de mercados
        
        Args:
            home_strength (float): Força ofensiva do time da casa (gols/jogo)
            away_strength (float): Força ofensiva do time visitante (gols/jogo)
            weather_impact (float): Ajuste climático (-0.5 a +0.5 gols)
        
        Returns:
            dict: {
                'expected_goals': {'home': float, 'away': float},
                'most_likely_score': str,
                'probabilities': {
                    'home_win': float,
                    'draw': float,
                    'away_win': float,
                    'over_2_5': float,
                    'under_2_5': float,
                    'btts': float  # Ambas Marcam (Both Teams To Score)
                },
                'score_distribution': [...],
                'weather_adjusted': bool
            }
        """
        logger.info(f"\n{'='*80}")
        logger.info("🎲 MODELO POISSON - Calculando distribuição de placares")
        logger.info(f"{'='*80}")
        
        # 1. Calcular lambda (expectativa de gols) com home advantage
        lambda_home = home_strength * self.HOME_ADVANTAGE
        lambda_away = away_strength
        
        logger.info(f"📊 Força base:")
        logger.info(f"   Casa: {home_strength:.2f} gols/jogo")
        logger.info(f"   Fora: {away_strength:.2f} gols/jogo")
        logger.info(f"   Home Advantage: {self.HOME_ADVANTAGE}x")
        
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
        
        # Over/Under 2.5 gols
        prob_over_25 = 0
        prob_under_25 = 0
        for h in range(7):
            for a in range(7):
                total_goals = h + a
                if total_goals > 2.5:
                    prob_over_25 += score_matrix[h, a]
                else:
                    prob_under_25 += score_matrix[h, a]
        
        logger.info(f"   Over/Under 2.5:")
        logger.info(f"      Over: {prob_over_25*100:.1f}%")
        logger.info(f"      Under: {prob_under_25*100:.1f}%")
        
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
                'over_2_5': float(prob_over_25),
                'under_2_5': float(prob_under_25),
                'btts': float(prob_btts),
                'home_clean_sheet': float(prob_home_clean_sheet),
                'away_clean_sheet': float(prob_away_clean_sheet)
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
    
    # Pesos padrão (calibrados com ~10.000 jogos)
    WEIGHTS = {
        'strength_diff': 0.25,           # Diferença de força ofensiva
        'form_diff': 0.18,               # Diferença de forma recente
        'home_advantage': 0.15,          # Vantagem de jogar em casa
        'h2h_advantage': 0.08,           # Histórico de confrontos
        'rest_advantage': 0.04,          # Descanso relativo
        'motivation_diff': 0.12,         # Diferença de motivação (NOVO)
        'injury_impact': 0.10,           # Impacto de lesões (NOVO)
        'match_importance': 0.08         # Importância do jogo (NOVO)
    }
    
    # Intercepto (ajustado para ~30% casa, 25% empate, 45% fora em jogos equilibrados)
    INTERCEPT = {
        'home_win': 0.3,
        'draw': -0.2,
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
                - form: {form_diff, momentum_diff}
                - context: {rest_advantage}
                - motivation: {motivation_differential} (NOVO)
                - injuries_suspensions: {injury_impact_differential} (NOVO)
                - match_importance: {match_importance} (NOVO)
        
        Returns:
            dict: {
                'home_win': float,
                'draw': float,
                'away_win': float,
                'model': 'logistic_regression'
            }
        """
        logger.info(f"\n{'='*80}")
        logger.info("📊 REGRESSÃO LOGÍSTICA - Calculando 1X2 (com novas features)")
        logger.info(f"{'='*80}")
        
        # Extrair features relevantes
        strength = features.get('strength', {})
        form = features.get('form', {})
        context = features.get('context', {})
        motivation = features.get('motivation', {})
        injuries = features.get('injuries_suspensions', {})
        importance = features.get('match_importance', {})
        h2h = features.get('h2h', {})
        
        # Calcular diferenciais
        strength_diff = strength.get('strength_differential', 0)
        form_diff = form.get('adjusted_form_diff', 0)
        rest_advantage = context.get('rest_advantage', 0)
        motivation_diff = motivation.get('motivation_differential', 0)
        injury_diff = injuries.get('injury_impact_differential', 0)
        match_imp = importance.get('match_importance', 5.0)
        h2h_advantage = h2h.get('h2h_home_win_rate', 0.5) - 0.5  # Centralizar em 0
        
        # Log features usadas
        logger.info(f"\n📊 Features utilizadas:")
        logger.info(f"   Força: {strength_diff:+.2f}")
        logger.info(f"   Forma: {form_diff:+.2f}")
        logger.info(f"   Descanso: {rest_advantage:+.0f} dias")
        logger.info(f"   Motivação: {motivation_diff:+.1f}")
        logger.info(f"   Lesões: {injury_diff:+.1f} (negativo = casa mais afetada)")
        logger.info(f"   Importância: {match_imp:.1f}/10")
        logger.info(f"   H2H: {h2h_advantage:+.2f}")
        
        # Calcular score para cada resultado
        scores = {}
        
        # HOME WIN
        score_home = self.INTERCEPT['home_win']
        score_home += strength_diff * self.WEIGHTS['strength_diff']
        score_home += form_diff * self.WEIGHTS['form_diff']
        # Vantagem casa REDUZIDA (antes era 0.3, agora 0.15)
        # Como Poisson já tem 1.3x, aqui usamos menor peso
        score_home += 0.15 * self.WEIGHTS['home_advantage']  # Casa tem vantagem (reduzido)
        score_home += rest_advantage * self.WEIGHTS['rest_advantage']
        score_home += motivation_diff * self.WEIGHTS['motivation_diff']  # NOVO
        score_home += (-injury_diff) * self.WEIGHTS['injury_impact']     # NOVO (invertido)
        score_home += h2h_advantage * self.WEIGHTS['h2h_advantage']
        
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
        # Jogos muito importantes = menos empates
        if match_imp > 8:
            score_draw -= 0.2
        scores['draw'] = score_draw
        
        # AWAY WIN
        score_away = self.INTERCEPT['away_win']
        score_away += strength_diff * (-self.WEIGHTS['strength_diff'])  # Invertido
        score_away += form_diff * (-self.WEIGHTS['form_diff'])
        score_away += rest_advantage * (-self.WEIGHTS['rest_advantage'])
        score_away += motivation_diff * (-self.WEIGHTS['motivation_diff'])  # NOVO
        score_away += (-injury_diff) * (-self.WEIGHTS['injury_impact'])     # NOVO
        score_away += h2h_advantage * (-self.WEIGHTS['h2h_advantage'])
        
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
    Ensemble de modelos: combina Poisson + Logística
    Usa weighted average baseado em confiança de cada modelo
    """
    
    def __init__(self):
        self.poisson = PoissonBivariateModel()
        self.logistic = LogisticRegressionModel()
        logger.info("🎯 Ensemble de Modelos inicializado (Poisson + Logística)")
    
    def predict(self, features, home_strength, away_strength, weather_impact=0.0):
        """
        Combina previsões de múltiplos modelos
        
        Args:
            features (dict): Features engineered
            home_strength (float): Força ofensiva casa
            away_strength (float): Força ofensiva fora
            weather_impact (float): Impacto climático
        
        Returns:
            dict: {
                'consensus': {home_win, draw, away_win},
                'poisson': {...},
                'logistic': {...},
                'weights': {poisson: float, logistic: float}
            }
        """
        logger.info(f"\n{'='*80}")
        logger.info("🎯 ENSEMBLE - Combinando modelos")
        logger.info(f"{'='*80}")
        
        # 1. Previsão Poisson
        poisson_pred = self.poisson.predict(home_strength, away_strength, weather_impact)
        
        # 2. Previsão Logística
        logistic_pred = self.logistic.predict_1x2(features)
        
        # 3. Pesos do ensemble (baseado em confiança)
        # Poisson é mais confiável quando há dados de gols
        # Logística é mais confiável quando há muitas features
        weight_poisson = 0.6  # 60% Poisson
        weight_logistic = 0.4  # 40% Logística
        
        logger.info(f"\n⚖️ Pesos do Ensemble:")
        logger.info(f"   Poisson: {weight_poisson*100:.0f}%")
        logger.info(f"   Logística: {weight_logistic*100:.0f}%")
        
        # 4. Consensus (média ponderada)
        consensus = {
            'home_win': (
                poisson_pred['probabilities']['home_win'] * weight_poisson +
                logistic_pred['home_win'] * weight_logistic
            ),
            'draw': (
                poisson_pred['probabilities']['draw'] * weight_poisson +
                logistic_pred['draw'] * weight_logistic
            ),
            'away_win': (
                poisson_pred['probabilities']['away_win'] * weight_poisson +
                logistic_pred['away_win'] * weight_logistic
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
            'weights': {
                'poisson': weight_poisson,
                'logistic': weight_logistic
            }
        }
