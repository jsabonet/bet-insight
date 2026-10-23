"""Backend de email para a Resend (https://resend.com).

Implementa a interface `django.core.mail.backends.base.BaseEmailBackend` para que
todo o ecossistema de email do Django (``send_mail``, ``EmailMultiAlternatives``,
redefinição de senha, etc.) seja encaminhado para a API REST da Resend.

Usa apenas ``requests`` (já presente nas dependências do projeto), sem necessidade
do SDK oficial ``resend``. Suporta HTML, texto alternativo, cc/bcc, reply_to,
anexos, tags e headers customizados.
"""
import base64
import logging
from email.utils import parseaddr

import requests
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def _extract_email(address):
    """Devolve apenas o endereço (sem 'Nome <...>') ou ``None``."""
    if not address:
        return None
    _, email = parseaddr(address)
    return email or None


class ResendBackend(BaseEmailBackend):
    """Envia emails transacionais através da API REST da Resend."""

    def __init__(self, api_key=None, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.api_key = api_key or getattr(settings, "RESEND_API_KEY", "")
        self.timeout = int(getattr(settings, "RESEND_TIMEOUT", 20))

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        if not self.api_key:
            if not self.fail_silently:
                raise RuntimeError(
                    "RESEND_API_KEY não configurado. Defina a variável de ambiente."
                )
            logger.error("RESEND_API_KEY não configurado; email não enviado.")
            return 0

        sent = 0
        for message in email_messages:
            if self._send_single(message):
                sent += 1
        return sent

    # ------------------------------------------------------------------
    # Envio individual
    # ------------------------------------------------------------------
    def _send_single(self, message):
        payload = self._build_payload(message)
        try:
            response = requests.post(
                RESEND_API_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=self.timeout,
            )
            if response.status_code in (200, 201, 202):
                return True

            logger.error(
                "Resend retornou %s: %s",
                response.status_code,
                (response.text or "")[:500],
            )
            if not self.fail_silently:
                response.raise_for_status()
            return False
        except requests.RequestException as exc:
            if not self.fail_silently:
                raise
            logger.exception("Falha ao enviar email via Resend: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Construção do payload
    # ------------------------------------------------------------------
    def _build_payload(self, message):
        to = [e for e in (_extract_email(a) for a in message.to) if e]
        cc = [e for e in (_extract_email(a) for a in message.cc) if e] if message.cc else []
        bcc = [e for e in (_extract_email(a) for a in message.bcc) if e] if message.bcc else []
        reply_to = (
            [e for e in (_extract_email(a) for a in message.reply_to) if e]
            if message.reply_to else []
        )

        from_email = (
            message.from_email
            or getattr(settings, "RESEND_FROM_EMAIL", None)
            or settings.DEFAULT_FROM_EMAIL
        )

        payload = {
            "from": from_email,
            "to": to,
            "subject": message.subject,
        }
        if cc:
            payload["cc"] = cc
        if bcc:
            payload["bcc"] = bcc
        if reply_to:
            payload["reply_to"] = reply_to

        html = None
        text = message.body or ""
        for alternative, mimetype in getattr(message, "alternatives", []):
            if mimetype == "text/html":
                html = alternative
                break
        if html:
            payload["html"] = html
            if text:
                payload["text"] = text

        attachments = self._build_attachments(message)
        if attachments:
            payload["attachments"] = attachments

        tags = getattr(message, "tags", None)
        if tags:
            payload["tags"] = [{"name": t} for t in tags]

        headers = getattr(message, "extra_headers", None)
        if headers:
            payload["headers"] = dict(headers)

        return payload

    @staticmethod
    def _build_attachments(message):
        result = []
        for att in getattr(message, "attachments", []) or []:
            try:
                if isinstance(att, tuple) and len(att) >= 2:
                    filename = att[0]
                    content = att[1]
                    mimetype = att[2] if len(att) >= 3 else "application/octet-stream"
                else:
                    # EmailAttachment (Django >= 5.x)
                    filename = att.get_filename() or "attachment"
                    content = att.get_payload() or b""
                    mimetype = att.get_content_type() or "application/octet-stream"
                if isinstance(content, str):
                    content = content.encode("utf-8")
                result.append(
                    {
                        "filename": filename,
                        "content": base64.b64encode(content).decode("ascii"),
                        "content_type": mimetype,
                    }
                )
            except Exception as exc:  # pragma: no cover - melhor esforço
                logger.warning("Anexo ignorado no email: %s", exc)
        return result
