import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.analysis.models import Analysis

logger = logging.getLogger(__name__)


def _enqueue_analysis_ready(analysis_id):
    try:
        from .tasks import send_analysis_ready_push
        send_analysis_ready_push.delay(analysis_id)
    except Exception:
        logger.exception('Não foi possível agendar push da análise %s', analysis_id)


@receiver(post_save, sender=Analysis, dispatch_uid='notifications.analysis_ready_push')
def queue_analysis_ready_push(sender, instance, created, **kwargs):
    if created:
        analysis_id = instance.pk
        transaction.on_commit(lambda: _enqueue_analysis_ready(analysis_id))