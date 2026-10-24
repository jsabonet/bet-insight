"""Emails transacionais do programa de afiliados.

Funções de domínio que montam o contexto e delegam o envio para o serviço
central (``apps.notifications.service``).
"""
import logging

from django.conf import settings
from django.core.mail import send_mail

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


def send_new_referral_email(referral):
    """Email ao afiliado quando alguém cria conta com o seu link/código."""
    try:
        affiliate = referral.affiliate
        user = affiliate.user
        referred = referral.user
        send_template_email(
            to=user.email,
            subject="Nova indicação no seu link - PlacarCerto",
            template_name="affiliate_new_referral",
            context={
                "user_name": user.username,
                "referred_name": referred.username,
                "referred_email": referred.email,
                "affiliate_code": affiliate.code,
                "source_display": referral.get_source_display(),
                "first_touch_at": referral.first_touch_at.strftime("%d/%m/%Y"),
            },
            tags=["affiliate", "referral"],
        )
        logger.info("Email de nova indicação enviado para %s", user.email)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de nova indicação: %s", exc)
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
                "commission_type": commission.commission_type,
                "commission_type_display": commission.get_commission_type_display(),
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


def send_withdrawal_requested_email(affiliate, withdrawal):
    """Email de confirmação quando um pedido de levantamento é registado."""
    try:
        user = affiliate.user
        send_template_email(
            to=user.email,
            subject="Pedido de levantamento recebido - PlacarCerto",
            template_name="affiliate_withdrawal_requested",
            context={
                "user_name": user.username,
                "amount": f"{withdrawal.amount:g}",
                "fee_amount": f"{withdrawal.fee_amount:g}",
                "payout_amount": f"{withdrawal.payout_amount:g}",
                "payout_method": affiliate.get_payout_method_display(),
                "currency": "MZN",
            },
            tags=["affiliate", "withdrawal"],
        )
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de levantamento: %s", exc)
        return False


def send_withdrawal_admin_email(withdrawal):
    """Avisa os administradores com email configurado sobre um novo pedido."""
    from django.contrib.auth import get_user_model

    admin_emails = list(
        get_user_model().objects.filter(
            is_active=True,
            is_staff=True,
        ).exclude(email='').values_list('email', flat=True).distinct()
    )
    if not admin_emails:
        logger.warning(
            "Pedido de levantamento %s registado sem destinatário administrativo com email.",
            withdrawal.pk,
        )
        return False

    affiliate = withdrawal.affiliate
    subject = f"Novo pedido de levantamento de afiliado - {affiliate.code}"
    message = (
        f"Foi recebido um pedido de levantamento de {withdrawal.amount:g} MZN.\n"
        f"Taxa da plataforma ({withdrawal.fee_rate:g}%): {withdrawal.fee_amount:g} MZN.\n"
        f"Valor líquido a pagar: {withdrawal.payout_amount:g} MZN.\n\n"
        f"Afiliado: {affiliate.code} ({affiliate.user.username})\n"
        f"Email: {affiliate.user.email or 'não informado'}\n"
        f"Método: {withdrawal.get_payout_method_display()}\n"
        f"Conta: {withdrawal.payout_account}\n"
        f"Estado: {withdrawal.get_status_display()}\n\n"
        f"Abra o painel administrativo: {_frontend_url('/admin/affiliates')}"
    )
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=False,
        )
        return True
    except Exception as exc:
        logger.exception(
            "Erro ao notificar administradores do levantamento %s: %s",
            withdrawal.pk,
            exc,
        )
        return False
