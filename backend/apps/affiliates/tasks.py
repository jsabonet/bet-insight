"""Tarefas Celery do sistema de afiliados."""
import logging

from celery import shared_task
from django.utils import timezone

from .models import AffiliateCommission
from .services import _update_affiliate_balances

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='affiliates.release_pending_commissions')
def release_pending_commissions(self):
    """Move comissões `pending` vencidas para `available`, atualiza saldos e notifica."""
    now = timezone.now()
    commissions = list(
        AffiliateCommission.objects.filter(
            status='pending',
            available_at__isnull=False,
            available_at__lte=now,
        ).select_related('affiliate', 'affiliate__user')
    )
    if not commissions:
        return 0

    ids = [c.id for c in commissions]
    AffiliateCommission.objects.filter(id__in=ids).update(
        status='available', updated_at=now,
    )

    # Recálculo de saldos dos afiliados afetados.
    affiliate_ids = {c.affiliate_id for c in commissions}
    from .models import Affiliate
    for affiliate in Affiliate.objects.filter(id__in=affiliate_ids):
        _update_affiliate_balances(affiliate)

    # Notificar afiliados por email (melhor esforço, não bloqueia).
    from .emails import send_commission_available_email
    for commission in commissions:
        try:
            send_commission_available_email(commission)
        except Exception as exc:
            logger.warning('Falha ao enviar email de comissão disponível: %s', exc)
        from .services import _enqueue_commission_push
        _enqueue_commission_push(
            commission.pk,
            commission.affiliate.user_id,
            'commission_available',
        )

    logger.info('Comissões libertadas (pending->available): %s', len(commissions))
    return len(commissions)
