"""
Integração do modelo ML treinado no ensemble de predição
Substitui pesos fixos por modelo real treinado com dados históricos

ARQUITETURA DUAL-MODEL (SEGURA) - MULTI-MARKET:
- Liga models: xgboost_1x2.pkl (880 partidas)
- Cup models: 9 mercados treinados (450 partidas FA Cup)
  * 1X2, BTTS, O/U 1.5/2.5/3.5
  * Double Chance, Home/Away Totals, Odd/Even
- Seleção automática baseada em is_cup
- Fallback: Se modelo de copas falhar, usa Poisson
"""
import logging
import joblib
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class MLModel:
    """
    Modelo ML multi-market com suporte dual (ligas + copas)
    
    MERCADOS SUPORTADOS:
    - 1X2 (Home/Draw/Away)
    - BTTS (Both Teams To Score)
    - O/U 1.5, 2.5, 3.5
    - Double Chance (1X/12/X2)
    - Home Totals, Away Totals
    - Odd/Even Goals
    
    DUAL-MODEL SUPPORT:
    - Carrega modelos de ligas (se existirem)
    - Carrega modelos de copas (9 mercados)
    - Seleção automática baseada em is_cup flag
    """
    
    def __init__(self):
        """
        Carrega TODOS os modelos disponíveis (ligas + copas)
        """
        base_path = Path(__file__).resolve().parent.parent.parent.parent
        
        # DIRETÓRIOS
        league_dir = base_path / 'ml_training' / 'trained_models'
        cup_dir = base_path / 'ml_models'
        
        # MERCADOS DISPONÍVEIS
        markets = ['1x2', 'btts', 'ou15', 'ou25', 'ou35', 'dc', 'home_totals', 'away_totals', 'odd_even']
        
        self.league_models = {}
        self.cup_models = {}
        
        logger.info(f"🔧 Carregando modelos ML...")
        
        # CARREGAR MODELOS DE LIGAS (opcional - só 1X2 existe)
        for market in markets:
            league_path = league_dir / f'xgboost_{market}.pkl'
            if league_path.exists():
                try:
                    self.league_models[market] = joblib.load(league_path)
                    logger.info(f"✅ Liga  {market.upper()}: {league_path.name}")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao carregar liga {market}: {e}")
        
        # CARREGAR MODELOS DE COPAS (9 mercados treinados)
        for market in markets:
            cup_path = cup_dir / f'xgboost_{market}_cups.pkl'
            if cup_path.exists():
                try:
                    self.cup_models[market] = joblib.load(cup_path)
                    logger.info(f"✅ Copa  {market.upper()}: {cup_path.name}")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao carregar copa {market}: {e}")
        
        logger.info(f"\n📊 MODELOS CARREGADOS:")
        logger.info(f"   Ligas: {len(self.league_models)} mercados")
        logger.info(f"   Copas: {len(self.cup_models)} mercados")
        
        if not self.league_models and not self.cup_models:
            raise FileNotFoundError("Nenhum modelo ML encontrado!")
    
    def _select_model(self, market, is_cup=False):
        """
        Seleciona modelo correto baseado no mercado e tipo (liga/copa)
        
        Returns:
            model ou None
        """
        if is_cup and market in self.cup_models:
            return self.cup_models[market]
        elif market in self.league_models:
            return self.league_models[market]
        else:
            return None
    
    def predict_1x2(self, features, is_cup=False):
        """
        Prevê probabilidades 1X2 usando modelo treinado
        
        Returns:
            dict: {'home_win': float, 'draw': float, 'away_win': float}
        """
        model = self._select_model('1x2', is_cup)
        
        if model is None:
            logger.warning("⚠️ Modelo 1X2 não disponível - fallback uniforme")
            return {'home_win': 0.33, 'draw': 0.33, 'away_win': 0.33, 'model': 'fallback'}
        
        try:
            flat_features = self._flatten_features(features)
            X = self._prepare_features(flat_features)
            
            probs = model.predict_proba(X)[0] if hasattr(model, 'predict_proba') else np.ones(3) / 3
            
            return {
                'home_win': float(probs[0]),
                'draw': float(probs[1]),
                'away_win': float(probs[2]),
                'model': f'{"cup" if is_cup else "league"}_1x2',
                'model_type': 'cup' if is_cup else 'league'
            }
        except ValueError as e:
            # Erro de shape ou features
            logger.error(f"❌ Erro predict_1x2: {e}")
            return {'home_win': 0.33, 'draw': 0.33, 'away_win': 0.33, 'model': 'error_fallback'}
        except Exception as e:
            logger.error(f"❌ Erro inesperado predict_1x2: {type(e).__name__}: {e}")
            return {'home_win': 0.33, 'draw': 0.33, 'away_win': 0.33, 'model': 'error_fallback'}
    
    def predict_btts(self, features, is_cup=False):
        """BTTS: Both Teams To Score"""
        model = self._select_model('btts', is_cup)
        if model is None:
            return None
        
        try:
            flat_features = self._flatten_features(features)
            X = self._prepare_features(flat_features)
            probs = model.predict_proba(X)[0] if hasattr(model, 'predict_proba') else [0.5, 0.5]
            return {'no': float(probs[0]), 'yes': float(probs[1])}
        except:
            return None
    
    def predict_over_under(self, features, threshold, is_cup=False):
        """O/U genérico para 1.5, 2.5, 3.5"""
        market_map = {1.5: 'ou15', 2.5: 'ou25', 3.5: 'ou35'}
        market = market_map.get(threshold)
        
        if market is None:
            return None
        
        model = self._select_model(market, is_cup)
        if model is None:
            return None
        
        try:
            flat_features = self._flatten_features(features)
            X = self._prepare_features(flat_features)
            probs = model.predict_proba(X)[0] if hasattr(model, 'predict_proba') else [0.5, 0.5]
            return {'under': float(probs[0]), 'over': float(probs[1])}
        except:
            return None
    
    def _prepare_features(self, flat_features):
        """Prepara vetor de features para predição (preenche com zeros para features faltando)"""
        # Converter valores para numéricos
        values = [v if not isinstance(v, (str, bool, type(None))) else (1 if v is True else 0) 
                 for v in flat_features.values()]
        
        # PROTEÇÃO: Se modelo espera menos features, truncar
        # Isso permite funcionar enquanto modelo não é retreinado
        X = np.array([values])
        
        expected_features = 98  # Modelo atual foi treinado com 98 features
        actual_features = X.shape[1]
        
        if actual_features != expected_features:
            logger.warning(f"⚠️ Feature mismatch: modelo espera {expected_features}, recebeu {actual_features}")
            if actual_features > expected_features:
                logger.info(f"   Truncando features extras ({actual_features - expected_features} removidas)")
                X = X[:, :expected_features]
            else:
                logger.warning(f"   ❌ Features insuficientes! Modelo não funcionará corretamente")
                logger.warning(f"   ⚠️ Recomendação: Retreine o modelo com as novas {actual_features} features")
        
        return X
    
    def _flatten_features(self, features):
        """
        Converte nested dict de features em flat dict
        IDÊNTICO ao usado no treino (collect_historical_data.py)
        Garante que TODOS os valores sejam numéricos (XGBoost rejeita strings)
        """
        flat = {}
        
        for category, values in features.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    # Converter booleanos para int
                    if isinstance(value, bool):
                        value = int(value)
                    
                    # Converter None para 0
                    if value is None:
                        value = 0
                    
                    # CRÍTICO: Ignorar strings (weather.condition, weather.weather_impact, etc.)
                    # XGBoost rejeita valores não numéricos
                    if isinstance(value, str):
                        # Tentar converter para número se possível
                        try:
                            value = float(value)
                        except (ValueError, TypeError):
                            # String não numérica - usar 0 (será ignorada se não estiver em expected_features)
                            continue
                    
                    flat[f"{category}.{key}"] = value
            else:
                # Valor não-dict na raiz - aplicar mesma lógica
                if isinstance(values, bool):
                    values = int(values)
                if values is None:
                    values = 0
                if isinstance(values, str):
                    try:
                        values = float(values)
                    except (ValueError, TypeError):
                        continue
                
                flat[category] = values
        
        return flat


# ATUALIZAÇÃO DO ModelEnsemble PARA USAR ML

class ModelEnsembleML:
    """
    Ensemble ATUALIZADO: Poisson + ML + Market Odds
    Usa novos modelos multi-market com suporte dual (ligas + copas)
    """
    
    def __init__(self, use_market_prior=True):
        from .statistical_models import PoissonBivariateModel
        
        self.poisson = PoissonBivariateModel()
        
        # Tentar carregar modelos ML multi-market
        try:
            self.ml = MLModel()  # SEM argumentos - carrega todos os modelos
            self.has_ml = True
            logger.info(f"✅ Ensemble com ML multi-market ({len(self.ml.cup_models)} copas, {len(self.ml.league_models)} ligas)")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao carregar ML - usando LogisticRegressionModel: {e}")
            from .statistical_models import LogisticRegressionModel
            self.ml = LogisticRegressionModel()
            self.has_ml = False
        
        self.use_market_prior = use_market_prior
        logger.info(f"🎯 Ensemble: Poisson + {'ML' if self.has_ml else 'Logística'}{' + Market' if use_market_prior else ''}")
    
    def predict(self, features, home_strength, away_strength, weather_impact=0.0, league_id=None,
                home_defense=None, away_defense=None, knockout_adjustment=1.0, context_analysis=None):
        """
        Combina Poisson + ML + Market Odds
        
        Pesos otimizados para ML + AJUSTE CONTEXTUAL:
        - Poisson: 20% (xG puro, sem contexto)
        - ML: 50% (TODAS as features, treinado em 5000+ jogos)
        - Market: 30% (benchmark profissional)
        
        NOVO: Se context_analysis fornecido, ajusta pesos baseado em padrões detectados.
        
        Args:
            knockout_adjustment: Fator de ajuste para competições de copa (0.75-1.0)
                                Aplica redução no xG em jogos eliminatórios
            context_analysis: Análise contextual do ContextAnalyzer (opcional)
        """
        logger.info(f"\n{'='*80}")
        logger.info("🎯 ENSEMBLE ML - Combinando modelos")
        logger.info(f"{'='*80}")
        
        # 1. Previção Poisson (com ajuste de copa)
        poisson_pred = self.poisson.predict(home_strength, away_strength, weather_impact, league_id,
                                           home_defense, away_defense, knockout_adjustment)
        
        # 2. Previsão ML (ou Logística se ML não disponível)
        # Detectar se é copa pelas features de competição
        competition_features = features.get('competition', {})
        is_cup = competition_features.get('is_cup', False)
        
        # Chamar predict_1x2 com ou sem is_cup baseado no tipo de modelo
        if self.has_ml:
            ml_pred = self.ml.predict_1x2(features, is_cup=is_cup)
        else:
            # LogisticRegressionModel não tem parâmetro is_cup
            ml_pred = self.ml.predict_1x2(features)
        
        # 3. Market Odds Prior
        market = features.get('market', {})
        market_prior = {
            'home_win': market.get('market_home_prob', 0.33),
            'draw': market.get('market_draw_prob', 0.33),
            'away_win': market.get('market_away_prob', 0.33)
        }
        
        # 4. Pesos do ensemble (OTIMIZADOS PARA ML + AJUSTE CONTEXTUAL)
        # NOVO: Ajustar pesos baseado em contexto se disponível
        if context_analysis:
            weights = self._adjust_weights_for_context(context_analysis)
            weight_poisson = weights['poisson']
            weight_ml = weights['ml']
            weight_market = weights['market']
        else:
            # Pesos padrão (sem contexto)
            if self.has_ml:
                # COM ML TREINADO: ML domina (50%), Market complementa (30%), Poisson base (20%)
                if self.use_market_prior and sum(market_prior.values()) > 0.9:
                    weight_poisson = 0.20
                    weight_ml = 0.50
                    weight_market = 0.30
                else:
                    # Sem market: ML 70%, Poisson 30%
                    weight_poisson = 0.30
                    weight_ml = 0.70
                    weight_market = 0.0
            else:
                # SEM ML (fallback logística): pesos originais
                if self.use_market_prior and sum(market_prior.values()) > 0.9:
                    weight_poisson = 0.25
                    weight_ml = 0.40
                    weight_market = 0.35
                else:
                    weight_poisson = 0.45
                    weight_ml = 0.55
                    weight_market = 0.0
        
        logger.info(f"\n⚖️ Pesos do Ensemble {'(COM ML TREINADO)' if self.has_ml else '(Logística Baseline)'}:")
        logger.info(f"   Poisson: {weight_poisson*100:.0f}%")
        logger.info(f"   {'ML' if self.has_ml else 'Logística'}: {weight_ml*100:.0f}%")
        if weight_market > 0:
            logger.info(f"   Market Prior: {weight_market*100:.0f}%")
        
        # 5. Consensus (média ponderada)
        consensus = {
            'home_win': (
                poisson_pred['probabilities']['home_win'] * weight_poisson +
                ml_pred['home_win'] * weight_ml +
                market_prior['home_win'] * weight_market
            ),
            'draw': (
                poisson_pred['probabilities']['draw'] * weight_poisson +
                ml_pred['draw'] * weight_ml +
                market_prior['draw'] * weight_market
            ),
            'away_win': (
                poisson_pred['probabilities']['away_win'] * weight_poisson +
                ml_pred['away_win'] * weight_ml +
                market_prior['away_win'] * weight_market
            )
        }
        
        # 6. Normalizar (garantir soma = 1.0)
        total = sum(consensus.values())
        consensus = {k: v/total for k, v in consensus.items()}
        
        logger.info(f"\n🎯 CONSENSUS FINAL:")
        logger.info(f"   Casa: {consensus['home_win']*100:.1f}%")
        logger.info(f"   Empate: {consensus['draw']*100:.1f}%")
        logger.info(f"   Fora: {consensus['away_win']*100:.1f}%")
        logger.info(f"{'='*80}\n")
        
        return {
            'consensus': consensus,
            'poisson': poisson_pred,
            'ml': ml_pred,
            'market_prior': market_prior,
            'weights': {
                'poisson': weight_poisson,
                'ml': weight_ml,
                'market': weight_market
            },
            'has_ml_model': self.has_ml
        }
    
    def _adjust_weights_for_context(self, context_analysis: dict) -> dict:
        """
        Ajusta pesos do ensemble baseado em padrões contextuais detectados.
        
        Lógica:
        - Padrões motivacionais/contextuais (low_motivation, asymmetric_motivation, derby):
          → Aumentar ML (vê motivação, lesões, contexto)
          → Reduzir Poisson (só vê força histórica)
        
        - Padrões estatísticos puros (open_game com histórico forte):
          → Balancear Poisson e ML
        
        Args:
            context_analysis: Output do ContextAnalyzer
            
        Returns:
            dict: {'poisson': 0.X, 'ml': 0.Y, 'market': 0.Z}
        """
        patterns = context_analysis.get('patterns', [])
        
        # Identificar tipo de padrões dominantes
        motivational_patterns = ['low_motivation_both', 'asymmetric_motivation', 'derby_context']
        contextual_patterns = ['critical_injuries', 'upset_potential']
        statistical_patterns = ['open_game', 'defensive_fatigue_game']
        
        # Contar padrões por tipo
        motivational_count = sum(1 for p in patterns if p['name'] in motivational_patterns)
        contextual_count = sum(1 for p in patterns if p['name'] in contextual_patterns)
        statistical_count = sum(1 for p in patterns if p['name'] in statistical_patterns)
        
        # Pegar maior confiança entre padrões motivacionais/contextuais
        max_context_confidence = 0
        for pattern in patterns:
            if pattern['name'] in motivational_patterns + contextual_patterns:
                if pattern['confidence'] > max_context_confidence:
                    max_context_confidence = pattern['confidence']
        
        # DECISÃO: Ajustar pesos se contexto forte
        if max_context_confidence >= 0.80:
            # Contexto muito forte → ML domina (conhece contexto)
            logger.info(f"\n⚖️ Ajustando pesos: Contexto forte ({max_context_confidence:.0%})")
            logger.info(f"   Padrões: {', '.join([p['name'] for p in patterns])}")
            
            if self.has_ml:
                weights = {
                    'poisson': 0.10,  # Reduzir (ignora contexto)
                    'ml': 0.70,       # Aumentar (usa features contextuais)
                    'market': 0.20    # Manter
                }
            else:
                # Sem ML, manter pesos padrão
                weights = {
                    'poisson': 0.25,
                    'ml': 0.40,
                    'market': 0.35
                }
            
            logger.info(f"   Novo: Poisson {weights['poisson']:.0%}, ML {weights['ml']:.0%}, Market {weights['market']:.0%}")
            
        elif max_context_confidence >= 0.65:
            # Contexto moderado → Ajuste leve
            logger.info(f"\n⚖️ Ajustando pesos: Contexto moderado ({max_context_confidence:.0%})")
            
            if self.has_ml:
                weights = {
                    'poisson': 0.15,
                    'ml': 0.60,
                    'market': 0.25
                }
            else:
                weights = {
                    'poisson': 0.25,
                    'ml': 0.40,
                    'market': 0.35
                }
            
            logger.info(f"   Novo: Poisson {weights['poisson']:.0%}, ML {weights['ml']:.0%}, Market {weights['market']:.0%}")
            
        else:
            # Contexto fraco → Pesos padrão
            logger.info(f"\n⚖️ Contexto fraco ({max_context_confidence:.0%}) - mantendo pesos padrão")
            
            if self.has_ml:
                if self.use_market_prior:
                    weights = {'poisson': 0.20, 'ml': 0.50, 'market': 0.30}
                else:
                    weights = {'poisson': 0.30, 'ml': 0.70, 'market': 0.0}
            else:
                if self.use_market_prior:
                    weights = {'poisson': 0.25, 'ml': 0.40, 'market': 0.35}
                else:
                    weights = {'poisson': 0.45, 'ml': 0.55, 'market': 0.0}
        
        return weights

