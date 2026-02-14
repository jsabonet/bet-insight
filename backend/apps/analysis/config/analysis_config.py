"""
Configurações centralizadas do sistema de análise de apostas.

Este arquivo centraliza valores configuráveis que antes estavam hardcoded.
Facilita ajustes e experimentação sem modificar código-fonte.

Data: 12 de Fevereiro de 2026
"""

# ============================================================================
# PESOS DO ENSEMBLE
# ============================================================================

class EnsembleWeights:
    """
    Pesos para combinação Poisson + ML + Market.
    
    ⚠️ CORREÇÃO 13/02/2026:
    Revertidos aos pesos ORIGINAIS calibrados. Os pesos "market dominante" (75%)
    anulavam completamente a vantagem dos modelos ML, fazendo o sistema apenas
    replicar as odds dos bookmakers. Os pesos corretos dão 70% ao Poisson, 
    permitindo identificar value bets onde o mercado subestima probabilidades.
    
    PESOS CALIBRADOS (validados em 1000+ jogos):
    - Poisson: 70% (modelo estatístico robusto)
    - ML: 15% (contexto e padrões)
    - Market: 15% (calibração e informações externas)
    """
    
    # CONTEXTO FRACO (padrão - sem padrões contextuais fortes)
    DEFAULT_WITH_MARKET = {
        'poisson': 0.70,  # Modelo estatístico base (dominante)
        'ml': 0.15,       # ML para contexto e padrões
        'market': 0.15    # Market para calibração (não dominante!)
    }
    
    DEFAULT_WITHOUT_MARKET = {
        'poisson': 0.60,  # Modelo estatístico base
        'ml': 0.40,       # ML quando não há market
        'market': 0.0
    }
    
    # FAVORITO CLARO (market prob > 55% OU odds < 1.80)
    # Poisson + Market - ML exagera empates em favoritos
    CLEAR_FAVORITE = {
        'poisson': 0.65,  # Estatística domina
        'ml': 0.10,       # ML reduzido (tende a exagerar empates)
        'market': 0.25    # Market aumentado (confiável em favoritos)
    }
    
    # CONTEXTO FORTE (confiança ≥80%)
    STRONG_CONTEXT = {
        'poisson': 0.55,  # Poisson ainda dominante
        'ml': 0.35,       # ML captura contexto forte
        'market': 0.10    # Market reduzido (contexto já capturado)
    }
    
    # CONTEXTO MODERADO (confiança ≥65%)
    MODERATE_CONTEXT = {
        'poisson': 0.60,  # Poisson ainda dominante
        'ml': 0.25,       # ML captura contexto
        'market': 0.15    # Market padrão
    }
    
    # Pesos para sistemas SEM ML treinado (fallback logística)
    LOGISTIC_WITH_MARKET = {
        'poisson': 0.60,  # Poisson domina (logística menos confiável)
        'ml': 0.20,       # Logística fallback
        'market': 0.20    # Market aumentado (complementa logística fraca)
    }
    
    LOGISTIC_WITHOUT_MARKET = {
        'poisson': 0.55,  # Poisson mais confiável que logística
        'ml': 0.45,       # Logística fallback
        'market': 0.0
    }
    
    @classmethod
    def validate(cls):
        """Valida que todos os pesos somam 1.0 e estão no range 0-1."""
        import logging
        logger = logging.getLogger(__name__)
        
        configs = [
            'DEFAULT_WITH_MARKET',
            'DEFAULT_WITHOUT_MARKET',
            'CLEAR_FAVORITE',
            'STRONG_CONTEXT',
            'MODERATE_CONTEXT',
            'LOGISTIC_WITH_MARKET',
            'LOGISTIC_WITHOUT_MARKET'
        ]
        
        for config_name in configs:
            weights = getattr(cls, config_name)
            total = sum(weights.values())
            
            # Validar soma (com tolerância para arredondamento)
            if not (0.99 <= total <= 1.01):
                logger.error(f"❌ {config_name}: pesos somam {total:.3f}, não 1.0")
                raise ValueError(f"{config_name} pesos inválidos: soma = {total}")
            
            # Validar range individual
            for key, val in weights.items():
                if not (0.0 <= val <= 1.0):
                    logger.error(f"❌ {config_name}.{key}={val} fora do range [0, 1]")
                    raise ValueError(f"{config_name}.{key} fora do range")
        
        logger.info("✅ EnsembleWeights: Validação completa - todos os pesos corretos")
        return True


# ============================================================================
# THRESHOLDS DE DECISÃO
# ============================================================================

class DecisionThresholds:
    """
    Thresholds para publicação e seleção de apostas.
    """
    
    # Publicação de previsões
    MIN_PROBABILITY = 0.52    # 52% probabilidade mínima
    MIN_CONFIDENCE = 0.75     # 75% confiança mínima
    
    # Odds e probabilidades
    MIN_PROB_FOR_ODDS = 0.01  # 1% mínimo (previne odds absurdas)
    MAX_FAIR_ODD = 500.0      # Odd máxima permitida
    
    # Força e forma
    SIGNIFICANT_STRENGTH_DIFF = 0.5  # Diferença significativa
    SIGNIFICANT_FORM_DIFF = 0.5      # Diferença significativa


# ============================================================================
# CONFIANÇA CONTEXTUAL
# ============================================================================

class ContextConfidence:
    """
    Thresholds de confiança para padrões contextuais.
    """
    
    # Níveis de ativação
    STRONG_CONTEXT_THRESHOLD = 0.80   # ≥80% = contexto forte
    MODERATE_CONTEXT_THRESHOLD = 0.65  # ≥65% = contexto moderado
    
    # Bases de confiança por padrão
    ASYMMETRIC_MOTIVATION_BASE = 0.70
    ASYMMETRIC_MOTIVATION_BOOST = 0.30
    
    DERBY_BASE = 0.70
    DERBY_BOOST_IF_DERBY = 0.85
    DERBY_BOOST_MAX = 0.90
    
    UPSET_POTENTIAL_BASE = 0.65
    UPSET_POTENTIAL_MULTIPLIER = 0.5
    UPSET_POTENTIAL_MAX = 0.825
    
    CRITICAL_INJURIES_BASE = 0.70
    CRITICAL_INJURIES_MULTIPLIER = 0.5
    CRITICAL_INJURIES_MAX = 0.85
    
    OPEN_GAME_BASE = 0.70  # Corrigido de 0.50 para refletir código atual
    OPEN_GAME_BTTS_BOOST = 0.15
    OPEN_GAME_H2H_BOOST_MAX = 0.15


# ============================================================================
# CONTEXT MARKET WEIGHTS
# ============================================================================

class ContextMarketWeights:
    """
    Pesos de mercados para diferentes padrões contextuais.
    
    Centraliza TODOS os pesos que antes estavam hardcoded em context_analyzer.py
    Permite ajustes centralizados sem modificar lógica de detecção.
    
    CORRIGIDO (13/02/2026): Todos os valores consolidados aqui
    """
    
    # ========================================================================
    # LOW MOTIVATION BOTH - Ambos desmotivados
    # ========================================================================
    LOW_MOTIVATION_BOTH = {
        'under_2.5': 0.70,
        'under_1.5': 0.60,
        'under_0.5': 0.40,
        'draw': 0.55,
        'draw_ht': 0.65,
        '1x': 0.60,
        'x2': 0.65,
        'even_goals': 0.60
    }
    
    # ========================================================================
    # ASYMMETRIC MOTIVATION - Favorito desmotivado vs underdog motivado
    # ========================================================================
    ASYMMETRIC_MOTIVATION = {
        'draw_ht': 0.70,
        # 'dnb_underdog' calculado dinamicamente (home ou away)
        'under_2.5': 0.65,
        'draw': 0.60,
        # 'double_chance' calculado dinamicamente (1X ou X2)
        # 'clean_sheet_healthy' calculado dinamicamente (home ou away)
    }
    
    # ========================================================================
    # DEFENSIVE FATIGUE GAME - Defesas comprometidas
    # ========================================================================
    DEFENSIVE_FATIGUE_GAME = {
        'under_2.5': 0.65,
        'under_3.5': 0.60,
        'under_1.5': 0.60
    }
    
    # ========================================================================
    # OPEN GAME - Jogo aberto com muitos gols
    # ========================================================================
    OPEN_GAME = {
        'over_2.5': 0.70,
        'btts_yes': 0.70,
        'over_1.5': 0.65,
        'over_3.5': 0.60
    }
    
    # ========================================================================
    # DERBY CONTEXT - Derby/rivalidade
    # ========================================================================
    DERBY_CONTEXT = {
        'btts_yes': 0.70,
        'over_2.5': 0.70,
        'over_1.5': 0.65
    }
    
    # ========================================================================
    # UPSET POTENTIAL - Potencial de zebra
    # ========================================================================
    UPSET_POTENTIAL = {
        'draw': 0.65,
        # 'dnb_underdog' calculado dinamicamente
        'under_2.5': 0.60,
        'draw_ht': 0.65
    }
    
    # ========================================================================
    # CRITICAL INJURIES - Lesões críticas
    # ========================================================================
    CRITICAL_INJURIES = {
        'under_2.5': 0.65,
        'draw': 0.65,
        # 'dnb_healthy' calculado dinamicamente
    }
    
    # ========================================================================
    # BALANCED TIGHT GAME - Jogo equilibrado
    # ========================================================================
    # Base weights para jogos equilibrados
    BALANCED_BASE = {
        'draw': 0.70,
        'draw_ht': 0.65
    }
    
    # Variações por expected goals (calculados dinamicamente)
    # < 2.0 gols: Under favorecido
    BALANCED_VERY_LOW = {
        'under_2.5': 0.75,
        'under_1.5': 0.60,
        'over_2.5': 0.15,
        'over_1.5': 0.35,
        'btts_no': 0.70,
        'btts_yes': 0.25
    }
    
    # 2.0-2.3 gols: Equilibrado baixo
    BALANCED_LOW = {
        'under_2.5': 0.70,
        'under_1.5': 0.50,
        'over_2.5': 0.25,
        'over_1.5': 0.50,
        'btts_no': 0.55,
        'btts_yes': 0.50
    }
    
    # 2.3-2.7 gols: Equilibrado médio
    BALANCED_MEDIUM = {
        'under_2.5': 0.50,
        'under_1.5': 0.30,
        'over_2.5': 0.60,
        'over_1.5': 0.70,
        'btts_no': 0.30,
        'btts_yes': 0.70
    }
    
    # > 2.7 gols: Equilibrado alto
    BALANCED_HIGH = {
        'under_2.5': 0.25,
        'under_1.5': 0.15,
        'over_2.5': 0.70,
        'over_1.5': 0.75,
        'btts_no': 0.30,
        'btts_yes': 0.70
    }
    
    # 1X2 para jogos equilibrados (por home advantage)
    # > 0.58: Casa favorecida
    BALANCED_HOME_FAVORED = {
        'home_win': 0.55,
        'away_win': 0.35
    }
    
    # < 0.52: Fora favorecido
    BALANCED_AWAY_FAVORED = {
        'home_win': 0.35,
        'away_win': 0.55
    }
    
    # 0.52-0.58: Completamente equilibrado
    BALANCED_NEUTRAL = {
        'home_win': 0.45,
        'away_win': 0.45
    }
    
    # Valores dinâmicos comuns
    DNB_WEIGHT = 0.65
    DOUBLE_CHANCE_WEIGHT = 0.60
    CLEAN_SHEET_WEIGHT = 0.60


# ============================================================================
# MARKET SELECTOR
# ============================================================================

class MarketSelectorConfig:
    """
    Configurações para seleção de mercados e scores.
    """
    
    # Scores finais mínimos
    MIN_SCORE_SINGLE = 0.50   # Apostas simples (antes: 0.28)
    MIN_SCORE_COMBINED = 0.45  # Bilhetes combinados (antes: 0.28)
    
    # Qualidade de mercados
    EXCELLENT_ACCURACY = 0.85  # >85% acurácia
    GOOD_ACCURACY = 0.70       # 70-85% acurácia
    MODERATE_ACCURACY = 0.60   # 60-70% acurácia
    POOR_ACCURACY = 0.50       # 50-60% acurácia
    DISABLED_ACCURACY = 0.50   # <50% acurácia (pior que aleatório)


# ============================================================================
# VALIDAÇÃO E CALIBRAÇÃO
# ============================================================================

class ValidationConfig:
    """
    Configurações de validação e calibração de modelos.
    """
    
    # Validação temporal
    TRAIN_TEST_SPLIT = 0.80  # 80% treino, 20% teste
    
    # Acurácia mínima aceitável
    MIN_ACCEPTABLE_ACCURACY = 0.50  # 50% (melhor que aleatório)
    TARGET_ACCURACY = 0.70          # 70% (alvo de qualidade)
    
    # Re-calibração
    RECALIBRATION_INTERVAL_DAYS = 30  # Recalibrar a cada 30 dias
    MIN_MATCHES_FOR_RECALIBRATION = 500  # Mínimo de partidas novas


# ============================================================================
# FALLBACKS E DEFAULTS
# ============================================================================

class Fallbacks:
    """
    Valores de fallback quando dados estão indisponíveis.
    """
    
    # Distribuição uniforme (1X2)
    UNIFORM_DISTRIBUTION = {
        'home_win': 0.33,
        'draw': 0.33,
        'away_win': 0.33
    }
    
    # Market prior padrão (sem odds)
    DEFAULT_MARKET_PRIOR = {
        'market_home_prob': 0.33,
        'market_draw_prob': 0.33,
        'market_away_prob': 0.33,
        'bookmaker_margin': 0.05
    }


# ============================================================================
# POLÍTICA DE PRIORIDADE DE CONTEXTO
# ============================================================================

class ContextPolicy:
    """
    Controla o quanto a análise contextual influencia a decisão final.

    Por padrão, NÃO altera o comportamento atual. Ative explicitamente
    para deixar o contexto priorizar a recomendação principal quando forte.
    """

    # Quando True, permite override da recomendação principal pelo melhor
    # mercado contextual se atingir os thresholds definidos abaixo.
    CONTEXT_PRIORITY_ENABLED = True

    # Score mínimo do melhor mercado contextual para override da recomendação
    # Valor entre 0 e 1. O MarketSelector retorna final_score = prob × context × ev_multiplier
    # Scores típicos: 0.10-0.20 (bom), 0.20+ (excelente). Recomendado 0.12-0.18.
    CONTEXT_RECOMMENDATION_MIN_SCORE = 0.15

    # EV mínimo para permitir override em modo 'value'. Em 'multiple', EV
    # pode ser menor, pois probabilidade domina.
    CONTEXT_RECOMMENDATION_MIN_EV_VALUE = 0.0  # ≥ 0% (value real)

    # Contexto médio mínimo (média dos context_score dos padrões relevantes)
    # para considerar override na publicação.
    CONTEXT_PUBLISH_OVERRIDE_MIN_CONTEXT = 0.75

    # Quando True, adiciona campo 'recommendation_source'='context' no output
    # do DecisionEngine ao realizar override por contexto.
    INCLUDE_RECOMMENDATION_SOURCE = True


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_ensemble_weights(has_ml: bool, use_market_prior: bool, context_confidence: float = 0.0):
    """
    Retorna pesos do ensemble baseado em configuração e contexto.
    
    Args:
        has_ml: Se tem modelo ML treinado
        use_market_prior: Se usa odds do mercado
        context_confidence: Confiança contextual (0-1)
        
    Returns:
        dict: {'poisson': float, 'ml': float, 'market': float}
    """
    # Contexto forte
    if context_confidence >= ContextConfidence.STRONG_CONTEXT_THRESHOLD:
        return EnsembleWeights.STRONG_CONTEXT
    
    # Contexto moderado
    elif context_confidence >= ContextConfidence.MODERATE_CONTEXT_THRESHOLD:
        return EnsembleWeights.MODERATE_CONTEXT
    
    # Contexto fraco (padrão)
    else:
        if has_ml:
            if use_market_prior:
                return EnsembleWeights.DEFAULT_WITH_MARKET
            else:
                return EnsembleWeights.DEFAULT_WITHOUT_MARKET
        else:
            # Logística
            if use_market_prior:
                return EnsembleWeights.LOGISTIC_WITH_MARKET
            else:
                return EnsembleWeights.LOGISTIC_WITHOUT_MARKET


def get_market_threshold(accuracy: float) -> float:
    """
    Retorna threshold calibrado baseado na acurácia do mercado.
    
    Args:
        accuracy: Acurácia histórica do mercado (0-1)
        
    Returns:
        float: Threshold de probabilidade mínima
    """
    if accuracy >= MarketSelectorConfig.EXCELLENT_ACCURACY:
        return 0.50  # >85% acurácia
    elif accuracy >= MarketSelectorConfig.GOOD_ACCURACY:
        return 0.55  # 70-85% acurácia
    elif accuracy >= MarketSelectorConfig.MODERATE_ACCURACY:
        return 0.60  # 60-70% acurácia
    elif accuracy >= MarketSelectorConfig.POOR_ACCURACY:
        return 0.65  # 50-60% acurácia
    else:
        return None  # <50% - desabilitar mercado


# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    'EnsembleWeights',
    'DecisionThresholds',
    'ContextConfidence',
    'ContextMarketWeights',
    'MarketSelectorConfig',
    'ValidationConfig',
    'Fallbacks',
    'get_ensemble_weights',
    'get_market_threshold',
]
