from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class AnalysisConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analysis"
    verbose_name = "Análises"
    
    def ready(self):
        """Verifica valores carregados no startup do Django"""
        from apps.analysis.config.analysis_config import EnsembleWeights
        
        logger.warning("=" * 80)
        logger.warning("🔍 VERIFICAÇÃO STARTUP DJANGO - Valores Carregados:")
        logger.warning(f"   DEFAULT_WITH_MARKET poisson: {EnsembleWeights.DEFAULT_WITH_MARKET['poisson']}")
        logger.warning(f"   CLEAR_FAVORITE poisson: {EnsembleWeights.CLEAR_FAVORITE['poisson']}")
        
        if EnsembleWeights.DEFAULT_WITH_MARKET['poisson'] == 0.60:
            logger.warning("   ✅ DJANGO CARREGOU CÓDIGO NOVO!")
        else:
            logger.error(f"   ❌ DJANGO CARREGOU CÓDIGO ERRADO: {EnsembleWeights.DEFAULT_WITH_MARKET['poisson']}")
        logger.warning("=" * 80)
