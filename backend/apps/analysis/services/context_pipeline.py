from .context_analyzer import ContextAnalyzer
from .hybrid_strategy import HybridStrategy


def analyze_match_context(features, context_analyzer=None, hybrid_strategy=None):
    """Run context detection and the shared evidence gate used by all analyses."""
    analyzer = context_analyzer or ContextAnalyzer()
    strategy = hybrid_strategy or HybridStrategy()
    detected_context = analyzer.analyze(features)
    return strategy.apply_context(detected_context, features)
