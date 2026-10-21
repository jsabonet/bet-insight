"""Helpers for applying VPay payment results and activating subscriptions."""
import logging
from django.utils import timezone

from .models import Subscription

logger = logging.getLogger(__name__)

# Status VPay -> status local do Payment.
VPAY_STATUS_MAP = {
    'paid': 'completed',
    'pending': 'pending',
    'failed': 'failed',
    'cancelled': 'cancelled',
    'expired': 'expired',
}

# Mapeia o slug configurado (plan_config.PLANS) para uma escolha válida do
# campo Subscription.plan (monthly/quarterly/yearly). O slug original fica em
# Subscription.plan_slug e a duração é derivada de plan_config.get_plan_duration.
PLAN_CHOICE_MAP = {
    'monthly': 'monthly',
    'quarterly': 'quarterly',
    'yearly': 'yearly',
    'starter': 'monthly',
    'pro': 'monthly',
    'vip': 'monthly',
    'teste': 'monthly',
}


def mark_payment_completed(payment, paid_at=None):
    """Marca um pagamento como completo (idempotente)."""
    if payment.status == 'completed':
        return
    payment.status = 'completed'
    payment.completed_at = paid_at or timezone.now()
    payment.save(update_fields=['status', 'completed_at', 'updated_at'])


def activate_subscription_for_payment(payment):
    """
    Cria ou ativa a assinatura associada a um pagamento concluído.

    O cálculo da data de fim é delegado a Subscription.save(), que usa
    plan_config.get_plan_duration(plan_slug) e cai nas durações legadas
    (monthly/quarterly/yearly) quando o slug não está configurado.
    """
    plan_slug = (payment.metadata or {}).get('plan') or 'monthly'
    plan_choice = PLAN_CHOICE_MAP.get(plan_slug, 'monthly')

    if not payment.subscription:
        subscription = Subscription.objects.create(
            user=payment.user,
            plan=plan_choice,
            plan_slug=plan_slug,
            status='active',
            auto_renew=True,
            amount_paid=payment.amount,
        )
        payment.subscription = subscription
        payment.save(update_fields=['subscription', 'updated_at'])
        logger.info(
            'Assinatura criada via pagamento %s (plano %s)',
            payment.transaction_id, plan_slug,
        )
    else:
        subscription = payment.subscription
        subscription.status = 'active'
        subscription.plan = plan_choice
        subscription.plan_slug = plan_slug
        subscription.auto_renew = True
        subscription.save()
        logger.info(
            'Assinatura %s ativada via pagamento %s (plano %s)',
            subscription.id, payment.transaction_id, plan_slug,
        )

    return subscription


def apply_vpay_status(payment, vpay_status, *, activate=False):
    """
    Mapeia e persiste o estado VPay no Payment local.

    Quando `activate` é True e o estado é `paid`, conclui o pagamento e ativa a
    assinatura (idempotente). Devolve o status local resultante.
    """
    from .emails import (
        send_payment_confirmed_email,
        send_subscription_activated_email,
    )

    local_status = VPAY_STATUS_MAP.get(vpay_status, 'pending')
    if local_status == 'completed':
        if payment.status != 'completed':
            mark_payment_completed(payment)
            if activate:
                subscription = activate_subscription_for_payment(payment)
                send_payment_confirmed_email(payment.user, payment, subscription)
                send_subscription_activated_email(payment.user, subscription)
    else:
        payment.status = local_status
        payment.save(update_fields=['status', 'updated_at'])
    return payment.status
