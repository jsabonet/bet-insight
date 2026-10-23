"""Emails transacionais do programa de afiliados.

Funções de domínio que montam o contexto e delegam o envio para o serviço
central (``apps.notifications.service``).
"""
import logging

from django.conf import settings

from apps.notifications.service import send_template_email

logger = logging.getLogger(__name__)


def _frontend_url(path=""):
    base = getattr(settings, "FRONTEND_URL", "https://placarcerto.digital").rstrip("/")
    return f"{base}/{path.lstrip('/')}" if path else base


def _affiliate_link(affiliate):
    return _frontend_url(f"?ref={affiliate.code}")


def send_affiliate_approved_email(affiliate):
    """Email quando a conta de afiliado é criada/aprovada."""
    try:
        user = affiliate.user
        send_template_email(
            to=user.email,
            subject="Conta de afiliado aprovada 🎉 - PlacarCerto",
            template_name="affiliate_approved",
            context={
                "user_name": user.username,
                "affiliate_code": affiliate.code,
                "commission_rate": f"{affiliate.commission_rate:g}",
                "renewal_rate": f"{affiliate.renewal_rate:g}",
                "affiliate_link": _affiliate_link(affiliate),
            },
            tags=["affiliate", "approved"],
        )
        logger.info("Email de afiliado aprovado enviado para %s", user.email)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de afiliado aprovado: %s", exc)
        return False


def send_commission_earned_email(commission):
    """Email quando uma nova comissão (pending) é criada."""
    try:
        affiliate = commission.affiliate
        user = affiliate.user
        send_template_email(
            to=user.email,
            subject="Nova comissão ganha 💰 - PlacarCerto",
            template_name="affiliate_commission_earned",
            context={
                "user_name": user.username,
                "amount": f"{commission.amount:g}",
                "rate": f"{commission.rate:g}",
                "currency": "MZN",
            },
            tags=["affiliate", "commission"],
        )
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de comissão ganha: %s", exc)
        return False


def send_commission_available_email(commission):
    """Email quando uma comissão fica disponível para levantamento."""
    try:
        affiliate = commission.affiliate
        user = affiliate.user
        send_template_email(
            to=user.email,
            subject="Comissão disponível ✅ - PlacarCerto",
            template_name="affiliate_commission_available",
            context={
                "user_name": user.username,
                "amount": f"{commission.amount:g}",
                "available_balance": f"{affiliate.available_balance:g}",
                "currency": "MZN",
            },
            tags=["affiliate", "commission", "available"],
        )
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de comissão disponível: %s", exc)
        return False


def send_commission_paid_email(commission):
    """Email quando uma comissão é marcada como paga."""
    try:
        affiliate = commission.affiliate
        user = affiliate.user
        send_template_email(
            to=user.email,
            subject="Comissão paga 💸 - PlacarCerto",
            template_name="affiliate_commission_paid",
            context={
                "user_name": user.username,
                "amount": f"{commission.amount:g}",
                "payout_method": affiliate.get_payout_method_display(),
                "currency": "MZN",
            },
            tags=["affiliate", "commission", "paid"],
        )
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de comissão paga: %s", exc)
        return False


def send_withdrawal_requested_email(affiliate, amount):
    """Email de confirmação quando um pedido de levantamento é registado."""
    try:
        user = affiliate.user
        send_template_email(
            to=user.email,
            subject="Pedido de levantamento recebido - PlacarCerto",
            template_name="affiliate_withdrawal_requested",
            context={
                "user_name": user.username,
                "amount": f"{amount:g}",
                "payout_method": affiliate.get_payout_method_display(),
                "currency": "MZN",
            },
            tags=["affiliate", "withdrawal"],
        )
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de levantamento: %s", exc)
        return False
