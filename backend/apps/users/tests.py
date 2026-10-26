"""Testes dos fluxos de autenticação, verificação de email e recuperação de senha."""
from django.core import mail
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from .ip_utils import get_client_ip

from .models import User


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
class AuthEmailFlowTests(TestCase):
    def setUp(self):
        self.register_url = reverse("register")

    def _register(self, email="novo@example.com", username="novo"):
        payload = {
            "email": email,
            "username": username,
            "password": "SenhaForte123!",
            "password2": "SenhaForte123!",
            "age_confirmation": True,
        }
        return self.client.post(self.register_url, payload, format="json")

    def test_register_sends_welcome_and_verification_emails(self):
        response = self._register()
        self.assertEqual(response.status_code, 201)
        # Boas-vindas + verificação.
        self.assertEqual(len(mail.outbox), 2)

    def test_verify_email_endpoint(self):
        self._register()
        user = User.objects.get(email="novo@example.com")
        self.assertFalse(user.email_verified)

        from .tokens import account_activation_token, encode_uid
        uid = encode_uid(user)
        token = account_activation_token.make_token(user)

        response = self.client.post(
            reverse("verify-email"),
            {"uid": uid, "token": token},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.email_verified)

    def test_password_reset_flow(self):
        self._register()
        user = User.objects.get(email="novo@example.com")

        # 1) Pedir redefinição (envia email).
        response = self.client.post(
            reverse("password-reset"), {"email": "novo@example.com"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 3)  # +1 email de reset

        # 2) Confirmar com token válido.
        from .tokens import password_reset_token, encode_uid
        uid = encode_uid(user)
        token = password_reset_token.make_token(user)

        response = self.client.post(
            reverse("password-reset-confirm"),
            {"uid": uid, "token": token, "new_password": "NovaSenha123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.check_password("NovaSenha123!"))


class ClientIpResolutionTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(TRUSTED_PROXY_IPS=())
    def test_ignores_forwarded_ip_from_untrusted_remote(self):
        request = self.factory.get(
            '/',
            HTTP_X_FORWARDED_FOR='198.51.100.7',
            REMOTE_ADDR='203.0.113.8',
        )

        self.assertEqual(get_client_ip(request), '203.0.113.8')

    @override_settings(TRUSTED_PROXY_IPS=('10.0.0.0/8',))
    def test_resolves_forwarded_chain_from_trusted_proxy(self):
        request = self.factory.get(
            '/',
            HTTP_X_FORWARDED_FOR='198.51.100.7, 10.1.0.3',
            REMOTE_ADDR='10.1.0.2',
        )

        self.assertEqual(get_client_ip(request), '198.51.100.7')

    @override_settings(TRUSTED_PROXY_IPS=('10.0.0.0/8',))
    def test_ignores_malformed_forwarded_chain(self):
        request = self.factory.get(
            '/',
            HTTP_X_FORWARDED_FOR='spoofed',
            REMOTE_ADDR='10.1.0.2',
        )

        self.assertEqual(get_client_ip(request), '10.1.0.2')
