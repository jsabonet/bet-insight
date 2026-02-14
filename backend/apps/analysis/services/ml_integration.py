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
from apps.analysis.config import EnsembleWeights, ContextConfidence, Fallbacks

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
        Carrega TODOS os modelos disponíveis (ligas + copas + NOVO XGBoost otimizado)
        
        PRIORIDADE DE MODELOS (1X2):
        1. XGBoost Balanced (NOVO) - 84.79% acurácia em 3,400 partidas
        2. Modelos específicos (ligas/copas)
        3. Fallback uniforme
        """
        base_path = Path(__file__).resolve().parent.parent.parent.parent
        
        # DIRETÓRIOS
        league_dir = base_path / 'ml_training' / 'trained_models'
        cup_dir = base_path / 'ml_models'
        ml_training_dir = base_path / 'ml_training'
        
        # MERCADOS DISPONÍVEIS
        markets = ['1x2', 'btts', 'ou15', 'ou25', 'ou35', 'dc', 'home_totals', 'away_totals', 'odd_even']
        
        self.league_models = {}
        self.cup_models = {}
        self.xgboost_optimized = None  # DESABILITADO: Exagera empates (48% vs 25% real)
        
        logger.info(f"🔧 Carregando modelos ML...")
        
        # DESABILITADO: XGBoost Balanced exagera empates - usando modelos por liga
        # xgb_pattern = list(ml_training_dir.glob('xgboost_balanced_*.json'))
        # if xgb_pattern:
        #     # Ordenar por data de modificação e pegar o mais recente
        #     xgb_path = sorted(xgb_pattern, key=lambda p: p.stat().st_mtime, reverse=True)[0]
        #     try:
        #         import xgboost as xgb
        #         self.xgboost_optimized = xgb.Booster()
        #         self.xgboost_optimized.load_model(str(xgb_path))
        #         logger.info(f"✅ ⭐ XGBoost OTIMIZADO: {xgb_path.name} (84.79% acurácia)")
        #         logger.info(f"       Validado em 3,400 partidas (DB + Copa)")
        #         logger.info(f"       Features: 107 real stats (não genéricas)")
        #     except Exception as e:
        #         logger.warning(f"⚠️ Erro ao carregar XGBoost otimizado: {e}")
        
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
        logger.info(f"   XGBoost Otimizado: {'SIM ⭐' if self.xgboost_optimized else 'NÃO'}")
        logger.info(f"   Ligas: {len(self.league_models)} mercados")
        logger.info(f"   Copas: {len(self.cup_models)} mercados")
        
        if not self.xgboost_optimized and not self.league_models and not self.cup_models:
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
        
        PRIORIDADE:
        1. XGBoost Balanced (NOVO) - 84.79% acurácia, funciona para ligas E copas
        2. Modelos específicos (liga/copa) - fallback
        3. Uniforme - último recurso
        
        Returns:
            dict: {'home_win': float, 'draw': float, 'away_win': float}
        """
        # PRIORIDADE 1: XGBoost Otimizado (NOVO - funciona para tudo)
        if self.xgboost_optimized:
            try:
                import xgboost as xgb
                
                # Preparar features para XGBoost otimizado (107 features)
                flat_features = self._flatten_features(features)
                X = self._prepare_features_for_xgboost(flat_features)
                
                # Criar DMatrix e fazer predição
                dmatrix = xgb.DMatrix(X)
                probs = self.xgboost_optimized.predict(dmatrix)[0]
                
                # XGBoost retorna [Casa, Empate, Fora] - ordem das classes durante treino
                # Verificar metadata do modelo para confirmar ordem
                return {
                    'home_win': float(probs[1]),   # Casa
                    'draw': float(probs[0]),       # Empate  
                    'away_win': float(probs[2]),   # Fora
                    'model': 'xgboost_optimized',
                    'model_type': 'optimized',
                    'accuracy': 0.8479  # 84.79% validado
                }
            except Exception as e:
                logger.warning(f"⚠️ XGBoost otimizado falhou: {e} - usando fallback")
                # Continuar para fallback
        
        # PRIORIDADE 2: Modelos específicos (antigos)
        model = self._select_model('1x2', is_cup)
        
        if model is None:
            logger.warning("⚠️ Modelo 1X2 não disponível - fallback uniforme")
            fallback = Fallbacks.UNIFORM_DISTRIBUTION.copy()
            fallback['model'] = 'fallback'
            return fallback
        
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
    
    def _prepare_features_for_xgboost(self, flat_features):
        """
        Prepara vetor de features para XGBoost otimizado (107 features reais)
        
        O novo modelo espera 107 features calculadas de estatísticas reais,
        não as 98 features genéricas dos modelos antigos.
        
        Returns:
            np.array: Vetor de features preparado
        """
        # Converter valores para numéricos
        values = [v if not isinstance(v, (str, bool, type(None))) else (1 if v is True else 0) 
                 for v in flat_features.values()]
        
        X = np.array([values])
        
        expected_features = 107  # Novo modelo treinado com 107 features reais
        actual_features = X.shape[1]
        
        if actual_features != expected_features:
            logger.warning(f"⚠️ Feature mismatch XGBoost: modelo espera {expected_features}, recebeu {actual_features}")
            if actual_features > expected_features:
                logger.info(f"   Truncando features extras ({actual_features - expected_features} removidas)")
                X = X[:, :expected_features]
            else:
                # Preencher com zeros para features faltando
                logger.warning(f"   Preenchendo {expected_features - actual_features} features faltando com zeros")
                missing = np.zeros((1, expected_features - actual_features))
                X = np.hstack([X, missing])
        
        return X


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
        
        Returns:
            Dictionary com probabilidades, xG, e detalhes de consenso
        """
        print("\n" + "="*100)
        print(">>> INICIANDO PREDICT() DO ENSEMBLE <<<")
        print(f">>> use_market_prior={self.use_market_prior}, has_ml={self.has_ml}")
        print("="*100 + "\n")
        
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
        
        # 4. Pesos do ensemble (CONFIGURAÇÃO CENTRALIZADA)
        # CORREÇÃO DEFINITIVA: Detectar favorito claro TEM PRIORIDADE MÁXIMA
        max_market_prob = max(market_prior.values())
        is_clear_favorite = max_market_prob > 0.55  # Odd < 1.80
        
        print(f"\n{'='*80}")
        print(f"DEBUG ENSEMBLE - max_market_prob: {max_market_prob:.1%}")
        print(f"DEBUG ENSEMBLE - is_clear_favorite: {is_clear_favorite}")
        print(f"DEBUG ENSEMBLE - use_market_prior: {self.use_market_prior}")
        print(f"DEBUG ENSEMBLE - has_ml: {self.has_ml}")
        print(f"{'='*80}\n")
        
        logger.info(f"📊 Detecção favorito: max_market_prob={max_market_prob:.1%}, is_clear_favorite={is_clear_favorite}")
        logger.info(f"   Condições: use_market_prior={self.use_market_prior}, has_ml={self.has_ml}")
        
        config_source = "padrão"
        
        # PRIORIDADE ABSOLUTA: Favorito claro (IGNORA contexto)
        # Poisson é MUITO melhor em jogos desbalanceados
        if is_clear_favorite and self.use_market_prior and self.has_ml:
            # ✅ CORREÇÃO: Para favoritos MUITO claros (>56%), ML pode estar descalibrado
            # Verificar se ML discorda fortemente do mercado
            
            # Filtrar apenas chaves de resultado (ignorar 'model', 'accuracy', etc)
            ml_outcomes = {k: v for k, v in ml_pred.items() if k in ['home_win', 'draw', 'away_win']}
            market_outcomes = {k: v for k, v in market_prior.items() if k in ['home_win', 'draw', 'away_win']}
            
            # Identificar resultado mais provável segundo cada modelo
            ml_max_outcome = max(ml_outcomes.items(), key=lambda x: x[1])[0]
            market_max_outcome = max(market_outcomes.items(), key=lambda x: x[1])[0]
            
            # Calcular divergência entre ML e Market
            ml_agrees_with_market = (ml_max_outcome == market_max_outcome)
            
            if not ml_agrees_with_market and max_market_prob > 0.56:
                # ML DISCORDA do mercado em favorito MUITO claro → Ignorar ML completamente
                logger.warning(f"ML DESCALIBRADO DETECTADO - Favorito muito claro mas ML discorda!")
                logger.warning(f"   Market diz: {market_max_outcome} ({market_outcomes[market_max_outcome]*100:.1f}%)")
                logger.warning(f"   ML diz: {ml_max_outcome} ({ml_outcomes[ml_max_outcome]*100:.1f}%)")
                logger.warning(f"   SOLUCAO: Market 80% (favorito muito claro), Poisson 20%, ML 0%")
                
                # Para favorito MUITO claro, confiar MUITO MAIS no mercado (80%)
                weights = {'poisson': 0.20, 'ml': 0.0, 'market': 0.80}
                config_source = "CLEAR_FAVORITE_NO_ML (Market 80%, Poisson 20%, ML descalibrado ignorado)"
            else:
                # ML concorda ou favorito não tão extremo → Usar CLEAR_FAVORITE normal
                weights = EnsembleWeights.CLEAR_FAVORITE
                config_source = "CLEAR_FAVORITE (Poisson 70%)"
            
            weight_poisson = weights['poisson']
            weight_ml = weights['ml']
            weight_market = weights['market']
            logger.info(f"CLEAR_FAVORITE ATIVADO - Usando Poisson {weight_poisson*100:.0f}%")
            logger.info(f"Pesos: P={weight_poisson*100:.0f}%, ML={weight_ml*100:.0f}%, M={weight_market*100:.0f}%")
            logger.info(f"Razao: Favorito claro (prob={max_market_prob:.1%} > 55%)")
        
        # SE NÃO FOR FAVORITO CLARO: verificar contexto ou usar padrão
        else:
            # Verificar se há contexto forte
            has_strong_context = (
                context_analysis and 
                isinstance(context_analysis, dict) and 
                context_analysis.get('patterns') and 
                len(context_analysis.get('patterns', [])) > 0
            )
            
            if has_strong_context:
                weights = self._adjust_weights_for_context(context_analysis)
                config_source = "contexto"
                weight_poisson = weights['poisson']
                weight_ml = weights['ml']
                weight_market = weights['market']
                logger.info(f"📊 Usando pesos de CONTEXTO (jogo equilibrado)")
            else:
                # Pesos padrão (sem favorito claro e sem contexto)
                if self.has_ml:
                    if self.use_market_prior and sum(market_prior.values()) > 0.9:
                        weights = EnsembleWeights.DEFAULT_WITH_MARKET
                        config_source = "DEFAULT_WITH_MARKET"
                    else:
                        weights = EnsembleWeights.DEFAULT_WITHOUT_MARKET
                        config_source = "DEFAULT_WITHOUT_MARKET"
                    weight_poisson = weights['poisson']
                    weight_ml = weights['ml']
                    weight_market = weights['market']
                else:
                    # SEM ML (fallback logística)
                    if self.use_market_prior and sum(market_prior.values()) > 0.9:
                        weights = EnsembleWeights.LOGISTIC_WITH_MARKET
                        config_source = "LOGISTIC_WITH_MARKET"
                    else:
                        weights = EnsembleWeights.LOGISTIC_WITHOUT_MARKET
                        config_source = "LOGISTIC_WITHOUT_MARKET"
                    weight_poisson = weights['poisson']
                    weight_ml = weights['ml']
                    weight_market = weights['market']
        
        logger.info(f"\n⚖️ Config: {config_source} | Pesos: P={weight_poisson*100:.0f}% ML={weight_ml*100:.0f}% M={weight_market*100:.0f}%")
        
        # DEBUG: Mostrar valores ANTES do consensus
        print(f"\n{'='*100}")
        print(f"DEBUG CONSENSUS - Valores ANTES de combinar:")
        print(f"  Poisson: Casa={poisson_pred['probabilities']['home_win']*100:.1f}%, Empate={poisson_pred['probabilities']['draw']*100:.1f}%, Fora={poisson_pred['probabilities']['away_win']*100:.1f}%")
        print(f"  ML:      Casa={ml_pred['home_win']*100:.1f}%, Empate={ml_pred['draw']*100:.1f}%, Fora={ml_pred['away_win']*100:.1f}%")
        print(f"  Market:  Casa={market_prior['home_win']*100:.1f}%, Empate={market_prior['draw']*100:.1f}%, Fora={market_prior['away_win']*100:.1f}%")
        print(f"  Pesos:   P={weight_poisson*100:.0f}%, ML={weight_ml*100:.0f}%, M={weight_market*100:.0f}%")
        print(f"{'='*100}\n")
        
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
        
        # DEBUG: Mostrar resultado do consensus
        print(f"\n{'='*100}")
        print(f"DEBUG CONSENSUS - Resultado APÓS combinar:")
        print(f"  Casa={consensus['home_win']*100:.1f}%, Empate={consensus['draw']*100:.1f}%, Fora={consensus['away_win']*100:.1f}%")
        print(f"{'='*100}\n")
        
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
          -> Aumentar ML (vê motivação, lesões, contexto)
          -> Reduzir Poisson (só vê força histórica)
        
        - Padrões estatísticos puros (open_game com histórico forte):
          -> Balancear Poisson e ML
        
        Args:
            context_analysis: Output do ContextAnalyzer
            
        Returns:
            dict: pesos do ensemble {'poisson': float, 'ml': float, 'market': float}
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
        
        # DECISÃO: Ajustar pesos se contexto forte (USANDO CONFIG)
        if max_context_confidence >= ContextConfidence.STRONG_CONTEXT_THRESHOLD:
            # Contexto muito forte → ML tem mais peso, mas ainda controlado
            logger.info(f"\n⚖️ Ajustando pesos: Contexto forte ({max_context_confidence:.0%})")
            logger.info(f"   Padrões: {', '.join([p['name'] for p in patterns])}")
            
            if self.has_ml:
                weights = EnsembleWeights.STRONG_CONTEXT
            else:
                # Sem ML, manter pesos padrão
                weights = {
                    'poisson': 0.25,
                    'ml': 0.40,
                    'market': 0.35
                }
            
            logger.info(f"   Novo: Poisson {weights['poisson']:.0%}, ML {weights['ml']:.0%}, Market {weights['market']:.0%}")
            
        elif max_context_confidence >= ContextConfidence.MODERATE_CONTEXT_THRESHOLD:
            # Contexto moderado → Ajuste leve
            logger.info(f"\n⚖️ Ajustando pesos: Contexto moderado ({max_context_confidence:.0%})")
            
            if self.has_ml:
                weights = EnsembleWeights.MODERATE_CONTEXT
            else:
                    weights = EnsembleWeights.LOGISTIC_WITH_MARKET
            logger.info(f"   Novo: Poisson {weights['poisson']:.0%}, ML {weights['ml']:.0%}, Market {weights['market']:.0%}")
            
        else:
            # Contexto fraco → Pesos padrão (USANDO CONFIG)
            logger.info(f"\n⚖️ Contexto fraco ({max_context_confidence:.0%}) - mantendo pesos padrão")
            
            if self.has_ml:
                if self.use_market_prior:
                    weights = EnsembleWeights.DEFAULT_WITH_MARKET
                else:
                    weights = {'poisson': 0.30, 'ml': 0.70, 'market': 0.0}
            else:
                if self.use_market_prior:
                    weights = {'poisson': 0.25, 'ml': 0.40, 'market': 0.35}
                else:
                    weights = {'poisson': 0.45, 'ml': 0.55, 'market': 0.0}
        
        return weights

