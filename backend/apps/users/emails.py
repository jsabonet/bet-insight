"""Emails transacionais da app de utilizadores.

Inclui boas-vindas, verificação de email, redefinição de senha e confirmação
de alteração de senha. Todas as funções usam o serviço central de envio
(``apps.notifications.service``) e o backend configurado (Resend em produção).
"""
import logging

from django.conf import settings

from apps.notifications.service import send_template_email
from .tokens import account_activation_token, encode_uid, password_reset_token

logger = logging.getLogger(__name__)


def _frontend_url(path=""):
    base = getattr(settings, "FRONTEND_URL", "https://placarcerto.digital").rstrip("/")
    return f"{base}/{path.lstrip('/')}" if path else base


def send_welcome_email(user, verified=False):
    """Email de boas-vindas após o registo."""
    try:
        send_template_email(
            to=user.email,
            subject="Bem-vindo ao PlacarCerto 🎉",
            template_name="welcome",
            context={"user_name": user.username, "user_verified": verified},
            tags=["welcome", "onboarding"],
        )
        logger.info("Email de boas-vindas enviado para %s", user.email)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de boas-vindas: %s", exc)
        return False


def send_verification_email(user):
    """Email com link de confirmação de email."""
    try:
        uid = encode_uid(user)
        token = account_activation_token.make_token(user)
        verification_url = _frontend_url(f"verify-email?uid={uid}&token={token}")

        send_template_email(
            to=user.email,
            subject="Confirme o seu email - PlacarCerto",
            template_name="email_verification",
            context={"user_name": user.username, "verification_url": verification_url},
            tags=["verification"],
        )
        logger.info("Email de verificação enviado para %s", user.email)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de verificação: %s", exc)
        return False


def send_password_reset_email(user):
    """Email com link de redefinição de senha."""
    try:
        uid = encode_uid(user)
        token = password_reset_token.make_token(user)
        reset_url = _frontend_url(f"reset-password?uid={uid}&token={token}")

        send_template_email(
            to=user.email,
            subject="Redefina a sua senha - PlacarCerto",
            template_name="password_reset",
            context={"user_name": user.username, "reset_url": reset_url},
            tags=["password-reset"],
        )
        logger.info("Email de redefinição de senha enviado para %s", user.email)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de redefinição de senha: %s", exc)
        return False


def send_password_changed_email(user):
    """Email de confirmação de alteração de senha."""
    try:
        send_template_email(
            to=user.email,
            subject="A sua senha foi alterada - PlacarCerto",
            template_name="password_changed",
            context={"user_name": user.username},
            tags=["password-changed"],
        )
        logger.info("Email de alteração de senha enviado para %s", user.email)
        return True
    except Exception as exc:
        logger.error("Erro ao enviar email de alteração de senha: %s", exc)
        return False
