import logging

from celery import shared_task
from django.utils import timezone

from .abandoned_checkouts import abandoned_checkout_queryset
from .emails import send_abandoned_checkout_email
from .models import Payment

logger = logging.getLogger(__name__)


@shared_task(name='subscriptions.send_abandoned_checkout_emails')
def send_abandoned_checkout_emails():
    """Envia lembretes uma vez para checkouts VPay pendentes há pelo menos uma hora."""
    now = timezone.now()
    candidates = abandoned_checkout_queryset(now).filter(
        recovery_email_sent_at__isnull=True,
    ).exclude(user__email='')

    sent_count = 0
    failed_count = 0

    for payment in candidates.iterator():
        claimed = Payment.objects.filter(
            pk=payment.pk,
            gateway='vpay',
            status='pending',
            recovery_email_sent_at__isnull=True,
        ).update(recovery_email_sent_at=now)
        if not claimed:
            continue

        if send_abandoned_checkout_email(payment):
            sent_count += 1
            continue

        Payment.objects.filter(
            pk=payment.pk,
            recovery_email_sent_at=now,
        ).update(recovery_email_sent_at=None)
        failed_count += 1
        logger.error(
            'Email de recuperação não enviado para o pagamento pendente %s; será tentado novamente.',
            payment.pk,
        )

    return {'sent': sent_count, 'failed': failed_count}
