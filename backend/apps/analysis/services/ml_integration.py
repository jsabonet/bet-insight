"""
Integração do modelo ML treinado no ensemble de predição
Substitui pesos fixos por modelo real treinado com dados históricos
"""
import logging
import joblib
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)


class MLModel:
    """
    Modelo ML treinado (XGBoost/LightGBM) para predição 1X2
    Substitui a LogisticRegressionModel com pesos fixos
    """
    
    def __init__(self, model_path='ml_training/trained_models/xgboost_1x2.pkl'):
        """
        Carrega modelo treinado do disco
        
        Args:
            model_path: Caminho relativo ao backend/ para o modelo .pkl
        """
        try:
            # Caminho absoluto: de apps/analysis/services/ -> backend/
            base_path = Path(__file__).resolve().parent.parent.parent.parent
            full_path = base_path / model_path
            
            if not full_path.exists():
                raise FileNotFoundError(f"Modelo não encontrado: {full_path}")
            
            self.model = joblib.load(full_path)
            self.model_name = model_path.split('/')[-1].replace('.pkl', '')
            
            logger.info(f"✅ Modelo ML carregado: {self.model_name}")
            logger.info(f"   Path: {full_path}")
            
            # Carregar feature names
            feature_path = full_path.parent / "feature_names.json"
            if feature_path.exists():
                import json
                with open(feature_path, 'r') as f:
                    self.expected_features = json.load(f)
                logger.info(f"   Features: {len(self.expected_features)}")
            else:
                self.expected_features = None
                logger.warning(f"⚠️ feature_names.json não encontrado - compatibilidade não garantida")
        
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo ML: {e}")
            raise
    
    def predict_1x2(self, features):
        """
        Prevê probabilidades 1X2 usando modelo treinado
        
        Args:
            features (dict): Features engineered (nested dict)
        
        Returns:
            dict: {
                'home_win': float,
                'draw': float,
                'away_win': float,
                'model': 'xgboost' ou 'lightgbm'
            }
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🤖 MODELO ML ({self.model_name.upper()}) - Calculando 1X2")
        logger.info(f"{'='*80}")
        
        try:
            # 1. Flatten features (mesmo processo do treino)
            flat_features = self._flatten_features(features)
            
            # 2. Alinhar com features esperadas
            if self.expected_features:
                feature_vector = []
                missing_features = []
                
                for expected_feature in self.expected_features:
                    if expected_feature in flat_features:
                        value = flat_features[expected_feature]
                        
                        # Converter booleanos para int
                        if isinstance(value, bool):
                            value = int(value)
                        
                        # Garantir valor numérico
                        if value is None:
                            value = 0
                        
                        feature_vector.append(value)
                    else:
                        # Feature faltando - usar 0
                        feature_vector.append(0)
                        missing_features.append(expected_feature)
                
                if missing_features:
                    logger.warning(f"⚠️ {len(missing_features)} features faltando (preenchidas com 0):")
                    for feat in missing_features[:5]:  # Log primeiras 5
                        logger.warning(f"   - {feat}")
                
                X = np.array([feature_vector])
            else:
                # Fallback: usar features como vieram (arriscado)
                logger.warning(f"⚠️ Sem lista de features esperadas - usando todas disponíveis")
                X = np.array([list(flat_features.values())])
            
            # 3. Predizer probabilidades
            # XGBoost/LightGBM retornam probs para cada classe [P(casa), P(empate), P(fora)]
            if hasattr(self.model, 'predict_proba'):
                probs = self.model.predict_proba(X)[0]
            else:
                # Fallback se modelo não tem predict_proba
                logger.warning(f"⚠️ Modelo sem predict_proba - usando predict + one-hot")
                prediction = self.model.predict(X)[0]
                probs = np.zeros(3)
                probs[int(prediction)] = 1.0
            
            home_win = float(probs[0])
            draw = float(probs[1])
            away_win = float(probs[2])
            
            logger.info(f"\n📊 Probabilidades ML:")
            logger.info(f"   Casa: {home_win*100:.1f}%")
            logger.info(f"   Empate: {draw*100:.1f}%")
            logger.info(f"   Fora: {away_win*100:.1f}%")
            logger.info(f"{'='*80}\n")
            
            return {
                'home_win': home_win,
                'draw': draw,
                'away_win': away_win,
                'model': self.model_name
            }
        
        except Exception as e:
            logger.error(f"❌ Erro ao executar predição ML: {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            # Fallback: probabilidades uniformes
            logger.warning(f"⚠️ Usando probabilidades uniformes como fallback")
            return {
                'home_win': 0.33,
                'draw': 0.33,
                'away_win': 0.33,
                'model': f'{self.model_name}_fallback'
            }
    
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
    Substitui LogisticRegressionModel por modelo ML treinado
    """
    
    def __init__(self, use_market_prior=True, ml_model_path='ml_training/trained_models/xgboost_1x2.pkl'):
        from .statistical_models import PoissonBivariateModel
        
        self.poisson = PoissonBivariateModel()
        
        # Tentar carregar modelo ML
        try:
            self.ml = MLModel(model_path=ml_model_path)
            self.has_ml = True
            logger.info(f"✅ Ensemble inicializado com ML ({self.ml.model_name})")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao carregar ML - usando LogisticRegressionModel: {e}")
            from .statistical_models import LogisticRegressionModel
            self.ml = LogisticRegressionModel()
            self.has_ml = False
        
        self.use_market_prior = use_market_prior
        logger.info(f"🎯 Ensemble: Poisson + {'ML' if self.has_ml else 'Logística'}{' + Market' if use_market_prior else ''}")
    
    def predict(self, features, home_strength, away_strength, weather_impact=0.0, league_id=None,
                home_defense=None, away_defense=None):
        """
        Combina Poisson + ML + Market Odds
        
        Pesos otimizados para ML:
        - Poisson: 20% (xG puro, sem contexto)
        - ML: 50% (TODAS as features, treinado em 5000+ jogos)
        - Market: 30% (benchmark profissional)
        """
        logger.info(f"\n{'='*80}")
        logger.info("🎯 ENSEMBLE ML - Combinando modelos")
        logger.info(f"{'='*80}")
        
        # 1. Previsão Poisson
        poisson_pred = self.poisson.predict(home_strength, away_strength, weather_impact, league_id,
                                           home_defense, away_defense)
        
        # 2. Previsão ML (ou Logística se ML não disponível)
        ml_pred = self.ml.predict_1x2(features)
        
        # 3. Market Odds Prior
        market = features.get('market', {})
        market_prior = {
            'home_win': market.get('market_home_prob', 0.33),
            'draw': market.get('market_draw_prob', 0.33),
            'away_win': market.get('market_away_prob', 0.33)
        }
        
        # 4. Pesos do ensemble (OTIMIZADOS PARA ML)
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
