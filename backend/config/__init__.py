"""
BetInsight Configuration Package
"""

# Isso garante que o app Celery é sempre importado quando o Django inicia
from .celery import app as celery_app

__all__ = ('celery_app',)
