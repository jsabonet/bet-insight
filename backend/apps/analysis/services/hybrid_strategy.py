"""Evidence gate for rule-based match context signals."""

import logging
from typing import Dict
from apps.analysis.config import ContextConfidence

logger = logging.getLogger(__name__)

PATTERN_DATA_REQUIREMENTS = {
    'low_motivation_both': {'standings'},
    'knockout_upset': {'competition', 'team_statistics'},
    'motivated_favorite_vs_defensive_wall': {'standings', 'team_statistics', 'market'},
    'must_win_high_importance': {'standings'},
    'congested_schedule_both': {'rest'},
    'bogey_team_effect': {'h2h'},
    'bookmaker_margin_high': {'market'},
    'post_heavy_defeat_volatility': {'recent_form'},
    'set_pieces_advantage': {'team_statistics', 'match_statistics'},
    'asymmetric_motivation': {'standings', 'team_statistics'},
    'asymmetric_fatigue': {'rest'},
    'defensive_fatigue_game': {'rest', 'injuries'},
    'open_game': {'recent_form', 'team_statistics'},
    'derby_context': {'h2h'},
    'upset_potential': {'team_statistics', 'recent_form'},
    'critical_injuries': {'injuries'},
    'balanced_tight_game': {'standings', 'team_statistics'},
}

SOURCE_SAMPLE_REQUIREMENTS = {
    'standings': {
        'home_standings_games': 5,
        'away_standings_games': 5,
    },
    'team_statistics': {
        'home_team_statistics_games': 5,
        'away_team_statistics_games': 5,
    },
    'recent_form': {
        'home_recent_form_games': 3,
        'away_recent_form_games': 3,
    },
    'h2h': {
        'h2h_games': 3,
    },
}


class HybridStrategy:
    """
    Enables a detected pattern only when its required inputs are available and
    its rule score meets the strong-context threshold. The score is not a
    historically calibrated probability.
    """
    
    # Rule-based confidence is not a calibrated probability of correctness.
    MIN_CONFIDENCE_FOR_CONTEXT = ContextConfidence.STRONG_CONTEXT_THRESHOLD
    INVALIDATED_PATTERNS = frozenset()
    NON_PREDICTIVE_PATTERNS = frozenset({'bookmaker_margin_high'})
    
    def __init__(self):
        """Inicializa estrategia hibrida."""
        self.decisions_log = []
    
    def should_use_context(self, 
                          context_result: Dict,
                          match_features: Dict) -> Dict:
        """
        Decide quais padrões têm evidência suficiente para influenciar a análise.
        
        Args:
            context_result: Output do ContextAnalyzer
            match_features: Features and source-availability metadata from FeatureEngineer
            
        Returns:
            Dict: {
                'use_context': bool,
                'reason': str,
                'confidence': float,
                'approved_patterns': List[str]
            }
        """
        patterns = context_result.get('patterns', [])
        
        if not patterns:
            return self._reject_context("Nenhum padrao detectado")
        
        available_data = self._available_data(match_features)
        approved_patterns = []
        max_confidence = 0
        approved_confidences = []

        for pattern in patterns:
            pattern_name = pattern.get('name')
            confidence = pattern.get('confidence', 0)
            required_data = PATTERN_DATA_REQUIREMENTS.get(pattern_name)

            max_confidence = max(max_confidence, confidence)

            if pattern_name in self.INVALIDATED_PATTERNS:
                logger.info(f"   ❌ {pattern_name}: padrão desativado por validação histórica")
                continue
            if pattern_name in self.NON_PREDICTIVE_PATTERNS:
                logger.info(f"   ℹ️ {pattern_name}: sinal de qualidade/risco, não evidência preditiva")
                continue

            if required_data is None or not required_data.issubset(available_data):
                logger.info(
                    "   ⚠️ %s: dados insuficientes (%s)",
                    pattern_name,
                    sorted(required_data or ()),
                )
                continue
            insufficient_samples = self._insufficient_samples(
                required_data,
                match_features,
            )
            if insufficient_samples:
                logger.info(
                    "   ⚠️ %s: amostra insuficiente (%s)",
                    pattern_name,
                    ', '.join(insufficient_samples),
                )
                continue

            if confidence < self.MIN_CONFIDENCE_FOR_CONTEXT:
                logger.info(f"   ⚠️ {pattern_name}: Confianca {confidence:.0%} < {self.MIN_CONFIDENCE_FOR_CONTEXT:.0%}")
                continue
            
            approved_patterns.append(pattern_name)
            approved_confidences.append(confidence)
            logger.info(f"   ✅ {pattern_name}: APROVADO (confianca: {confidence:.0%})")
        
        if approved_patterns:
            decision = {
                'use_context': True,
                'reason': f"Padroes fortes detectados: {', '.join(approved_patterns)}",
                'confidence': max(approved_confidences),
                'approved_patterns': approved_patterns
            }
            logger.info(f"\n🎯 DECISAO: USAR CONTEXTO")
            logger.info(f"   Padroes: {', '.join(approved_patterns)}")
            logger.info(f"   Confianca: {max_confidence:.0%}")
        else:
            decision = self._reject_context(
                "Nenhum padrão tem simultaneamente dados de origem disponíveis e "
                f"score de regra >= {self.MIN_CONFIDENCE_FOR_CONTEXT:.0%} "
                f"(maior score detectado: {max_confidence:.0%})"
            )
        
        self.decisions_log.append(decision)
        return decision

    def apply_context(self, context_result: Dict, match_features: Dict) -> Dict:
        """Return one consistently gated context payload for every analysis path."""
        decision = self.should_use_context(context_result, match_features)
        detected_patterns = context_result.get('patterns', [])
        approved_names = set(decision['approved_patterns'])
        approved_patterns = [
            pattern for pattern in detected_patterns
            if pattern.get('name') in approved_names
        ]

        analyzer = self._market_consolidator(approved_patterns)
        return {
            'patterns': approved_patterns,
            'top_markets': analyzer,
            'context_decision': decision,
            'detected_patterns': detected_patterns,
            'confidence_is_calibrated': False,
        }

    @staticmethod
    def _market_consolidator(patterns):
        from .context_analyzer import ContextAnalyzer

        analyzer = ContextAnalyzer()
        analyzer.patterns_detected = patterns
        return analyzer._consolidate_favorable_markets()
    
    def _reject_context(self, reason: str) -> Dict:
        """Rejeita uso de contexto e retorna decisao."""
        logger.info(f"\n🔄 DECISAO: USAR MODELO BASE (Poisson)")
        logger.info(f"   Razao: {reason}")
        
        return {
            'use_context': False,
            'reason': reason,
            'confidence': 0,
            'approved_patterns': []
        }
    
    @staticmethod
    def _available_data(features: Dict):
        if not features:
            return set()

        metadata = features.get('_metadata', {}).get('data_availability')
        if isinstance(metadata, dict):
            return {key for key, available in metadata.items() if available}
        return set()

    @staticmethod
    def _insufficient_samples(required_data, features):
        metadata = features.get('_metadata', {})
        if not isinstance(metadata, dict):
            metadata = {}
        sample_sizes = metadata.get('sample_sizes', {})
        if not isinstance(sample_sizes, dict):
            sample_sizes = {}

        insufficient = []
        for source in required_data:
            for sample_key, minimum in SOURCE_SAMPLE_REQUIREMENTS.get(source, {}).items():
                observed = sample_sizes.get(sample_key, 0)
                if not isinstance(observed, (int, float)) or observed < minimum:
                    insufficient.append(
                        f'{sample_key}={observed} (mínimo {minimum})'
                    )
        return insufficient
    
    def get_stats(self) -> Dict:
        """Retorna estatisticas das decisoes."""
        total = len(self.decisions_log)
        if total == 0:
            return {
                'total_decisions': 0,
                'used_context': 0,
                'used_base': 0,
                'context_percentage': 0
            }
        
        used_context = sum(1 for d in self.decisions_log if d['use_context'])
        used_base = total - used_context
        
        return {
            'total_decisions': total,
            'used_context': used_context,
            'used_base': used_base,
            'context_percentage': used_context / total * 100
        }
