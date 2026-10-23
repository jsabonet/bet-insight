"""Camada de serviço para envio de emails transacionais.

Centraliza a renderização de templates HTML (com fallback de texto), a montagem
da mensagem e o envio através do backend configurado (Resend em produção, console
em desenvolvimento). As funções de domínio (welcome, pagamento, comissão, etc.)
vivem nos apps respetivos e delegam para cá.
"""
import logging
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

TEMPLATE_DIR = "emails"


def _global_context(context):
    ctx = dict(context or {})
    ctx.setdefault("site_name", "PlacarCerto")
    ctx.setdefault(
        "site_url",
        getattr(settings, "FRONTEND_URL", "https://placarcerto.digital").rstrip("/"),
    )
    ctx.setdefault(
        "support_email",
        getattr(settings, "SUPPORT_EMAIL", "suporte@placarcerto.digital"),
    )
    ctx.setdefault("current_year", datetime.now().year)
    return ctx


def render_template(template_name, context):
    """Devolve ``(html, text)`` para um template, com contexto global injetado."""
    ctx = _global_context(context)
    html = render_to_string(f"{TEMPLATE_DIR}/{template_name}.html", ctx)
    try:
        text = render_to_string(f"{TEMPLATE_DIR}/{template_name}.txt", ctx)
    except Exception:
        text = _fallback_text(ctx)
    return html, text


def _fallback_text(ctx):
    lines = [str(ctx.get("title") or ctx.get("site_name")), ""]
    if ctx.get("message"):
        lines.append(str(ctx["message"]))
    lines.append("")
    lines.append(f"Aceda: {ctx.get('site_url')}")
    return "\n".join(lines)


def send_template_email(
    to,
    subject,
    template_name,
    context=None,
    from_email=None,
    tags=None,
    reply_to=None,
    fail_silently=True,
):
    """Envia um email transacional baseado em template HTML.

    Parâmetros:
        to: string ou lista de endereços de destino.
        subject: assunto do email.
        template_name: nome do template (sem extensão), dentro de ``emails/``.
        context: dict com o contexto do template.
        tags: lista de tags Resend (segmentação/analítica).
    """
    if isinstance(to, str):
        to = [to]
    to = [t for t in to if t]
    if not to:
        logger.warning("Envio ignorado: sem destinatários para '%s'.", template_name)
        return 0

    ctx = _global_context(context)
    ctx["subject"] = subject
    html, text = render_template(template_name, ctx)

    message = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=(
            from_email
            or getattr(settings, "RESEND_FROM_EMAIL", None)
            or settings.DEFAULT_FROM_EMAIL
        ),
        to=to,
    )
    message.attach_alternative(html, "text/html")

    support_email = ctx.get("support_email")
    if reply_to:
        message.reply_to = list(reply_to)
    elif support_email:
        message.reply_to = [support_email]

    if tags:
        message.tags = list(tags)
        message.extra_headers = {"X-Entity-Ref-ID": f"{template_name}:{':'.join(tags)}"}

    try:
        return message.send(fail_silently=fail_silently)
    except Exception as exc:
        logger.exception("Erro ao enviar email '%s': %s", template_name, exc)
        return 0
