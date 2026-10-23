"""Emails transacionais de assinaturas e pagamentos.

Mantém as assinaturas originais das funções (para compatibilidade com os
testes) mas delega o envio para o serviço central de notificações com templates
HTML. As funções são idempotentes e nunca lançam exceções para o chamador.
"""
import logging

from apps.notifications.service import send_template_email

logger = logging.getLogger(__name__)


def _plan_name(subscription):
    """Nome amigável do plano a partir do plan_slug (fallback: choices)."""
    try:
        from .plan_config import get_plan
        plan = get_plan(subscription.plan_slug)
        if plan:
            return plan["name"]
    except Exception:
        pass
    return subscription.get_plan_display()


def _daily_limit(subscription):
    """Limite diário de análises do plano (fallback: None)."""
    try:
        from .plan_config import get_plan_limit
        return get_plan_limit(subscription.plan_slug)
    except Exception:
        return None


def send_subscription_activated_email(user, subscription):
    """Email de boas-vindas ao premium (assinatura ativada)."""
    try:
        end_date = subscription.end_date.strftime("%d/%m/%Y")
        send_template_email(
            to=user.email,
            subject="Bem-vindo ao PlacarCerto Premium! 🎉",
            template_name="subscription_activated",
            context={
                "user_name": user.username,
                "plan_name": _plan_name(subscription),
                "daily_limit": _daily_limit(subscription) or "ilimitadas",
                "end_date": end_date,
            },
            tags=["subscription", "activated"],
        )
        logger.info("Email de ativação enviado para %s", user.email)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de ativação: %s", exc)
        return False


def send_subscription_expired_email(user, subscription):
    """Email de expiração de assinatura."""
    try:
        send_template_email(
            to=user.email,
            subject="A sua assinatura PlacarCerto expirou",
            template_name="subscription_expired",
            context={
                "user_name": user.username,
                "plan_name": _plan_name(subscription),
            },
            tags=["subscription", "expired"],
        )
        logger.info("Email de expiração enviado para %s", user.email)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de expiração: %s", exc)
        return False


def send_subscription_cancelled_email(user, subscription):
    """Email de confirmação de cancelamento de assinatura."""
    try:
        send_template_email(
            to=user.email,
            subject="Assinatura cancelada - PlacarCerto",
            template_name="subscription_cancelled",
            context={
                "user_name": user.username,
                "plan_name": _plan_name(subscription),
            },
            tags=["subscription", "cancelled"],
        )
        logger.info("Email de cancelamento enviado para %s", user.email)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de cancelamento: %s", exc)
        return False


def send_payment_confirmed_email(user, payment, subscription):
    """Email de confirmação de pagamento (recibo)."""
    try:
        send_template_email(
            to=user.email,
            subject="Pagamento confirmado ✅ - PlacarCerto",
            template_name="payment_confirmed",
            context={
                "user_name": user.username,
                "plan_name": _plan_name(subscription),
                "amount": f"{payment.amount:g}",
                "currency": payment.currency or "MZN",
                "transaction_id": payment.transaction_id,
            },
            tags=["payment", "confirmed"],
        )
        logger.info("Email de confirmação de pagamento enviado para %s", user.email)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de confirmação de pagamento: %s", exc)
        return False


def send_payment_failed_email(user, payment):
    """Email de falha no pagamento."""
    try:
        send_template_email(
            to=user.email,
            subject="Falha no pagamento - PlacarCerto",
            template_name="payment_failed",
            context={
                "user_name": user.username,
                "transaction_id": payment.transaction_id,
            },
            tags=["payment", "failed"],
        )
        logger.info("Email de falha de pagamento enviado para %s", user.email)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de falha de pagamento: %s", exc)
        return False
