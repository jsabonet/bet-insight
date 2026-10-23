"""Geradores de token e helpers de codificação para links por email."""
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

# Token de ativação/verificação de email.
account_activation_token = PasswordResetTokenGenerator()

# Token de redefinição de senha.
password_reset_token = PasswordResetTokenGenerator()


def encode_uid(user):
    """Codifica o pk do utilizador para uso em URL (uidb64)."""
    return urlsafe_base64_encode(force_bytes(user.pk))


def decode_uid(uidb64):
    """Decodifica o uidb64 de volta para o pk (string) ou ``None`` se inválido."""
    try:
        return force_str(urlsafe_base64_decode(uidb64))
    except Exception:
        return None
