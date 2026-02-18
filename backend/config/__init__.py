"""
BetInsight Configuration Package
"""

# Tenta importar Celery, mas não falha se Redis não estiver disponível
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except Exception:
    # Celery/Redis não disponível - modo degradado (apenas execução síncrona)
    celery_app = None
    __all__ = tuple()

