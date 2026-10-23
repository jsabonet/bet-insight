"""Testes da app de notificações.

Garante que todos os templates HTML/texto renderizam sem erros com um contexto
de exemplo, e que o serviço de envio funciona com o backend console (default).
"""
from django.core import mail
from django.test import TestCase, override_settings

from apps.notifications.service import render_template, send_template_email

# Conjunto de templates com o contexto mínimo necessário a cada um.
TEMPLATES = [
    "welcome",
    "email_verification",
    "password_reset",
    "password_changed",
    "subscription_activated",
    "payment_confirmed",
    "payment_failed",
    "subscription_expired",
    "subscription_cancelled",
    "affiliate_approved",
    "affiliate_commission_earned",
    "affiliate_commission_available",
    "affiliate_commission_paid",
    "affiliate_withdrawal_requested",
]

SAMPLE_CONTEXT = {
    "user_name": "Utilizador Teste",
    "plan_name": "Pro",
    "daily_limit": 40,
    "end_date": "22/10/2026",
    "amount": "599",
    "currency": "MZN",
    "transaction_id": "TX123",
    "verification_url": "https://placarcerto.digital/verify-email?uid=x&token=y",
    "reset_url": "https://placarcerto.digital/reset-password?uid=x&token=y",
    "affiliate_code": "TESTE1",
    "commission_rate": "40",
    "renewal_rate": "10",
    "affiliate_link": "https://placarcerto.digital/?ref=TESTE1",
    "rate": "40",
    "available_balance": "100",
    "payout_method": "M-Pesa",
}


class TemplateRenderingTests(TestCase):
    def test_all_templates_render_html(self):
        for name in TEMPLATES:
            with self.subTest(template=name):
                html, text = render_template(name, SAMPLE_CONTEXT)
                self.assertIn("PlacarCerto", html)
                self.assertGreater(len(html), 0)
                self.assertGreater(len(text), 0)


class EmailServiceTests(TestCase):
    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    )
    def test_send_template_email_dispatches(self):
        sent = send_template_email(
            to="destino@example.com",
            subject="Teste",
            template_name="welcome",
            context=SAMPLE_CONTEXT,
            tags=["welcome"],
        )
        self.assertEqual(sent, 1)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.subject, "Teste")
        self.assertIn("PlacarCerto", message.body)
        # A alternativa HTML deve estar anexada.
        html_alternatives = [alt for alt, mime in message.alternatives if mime == "text/html"]
        self.assertEqual(len(html_alternatives), 1)
