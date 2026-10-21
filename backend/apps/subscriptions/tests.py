"""
Testes para a integração VPay Moçambique.

Todos os testes usam mocks: nunca chamam a API real nem usam credenciais reais.
"""
import hashlib
import hmac
import json
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.users.models import User

from .models import Payment
from .payment_helpers import apply_vpay_status
from .vpay_service import VPayService, VPayServiceError, vpay_service


VPAY_SETTINGS = {
    'VPAY_ENABLED': True,
    'VPAY_BASE_URL': 'https://api.vpay.co.mz',
    'VPAY_CLIENT_ID': 'test-client-id',
    'VPAY_CLIENT_SECRET': 'test-client-secret',
    'VPAY_APPLICATION_ID': 'test-app-id',
    'VPAY_CHECKOUT_BASE_URL': 'https://checkout.vpay.co.mz',
    'VPAY_WEBHOOK_SECRET': 'webhook-secret',
    'VPAY_TIMEOUT': 5,
    'VPAY_AUTH_TOKEN_PATH': '/v1/auth/token',
}


def make_user(**kwargs):
    defaults = {
        'username': 'vpay_user',
        'email': 'vpay_user@example.com',
        'password': 'x' * 12,
    }
    defaults.update(kwargs)
    return User.objects.create_user(**defaults)


class VPayServiceAuthTests(TestCase):
    """Autenticação e cache de token (nunca chamam a API real)."""

    @override_settings(**VPAY_SETTINGS)
    def test_access_token_is_cached(self):
        service = VPayService()
        token_response = {'data': {'access_token': 'tok-abc', 'expires_in': 3600}}

        with patch.object(service, '_request_access_token', return_value=token_response) as request_token:
            first = service._get_access_token()
            second = service._get_access_token()

        self.assertEqual(first, 'tok-abc')
        self.assertEqual(second, 'tok-abc')
        request_token.assert_called_once()

    @override_settings(**VPAY_SETTINGS)
    def test_access_token_renewed_after_expiry(self):
        service = VPayService()
        token_response = {'data': {'access_token': 'tok-abc', 'expires_in': 3600}}

        with patch.object(service, '_request_access_token', return_value=token_response) as request_token:
            service._get_access_token()
            # Força expiração do token em memória.
            service._token_expires_at = 0
            service._get_access_token()

        self.assertEqual(request_token.call_count, 2)

    @override_settings(**VPAY_SETTINGS)
    def test_auth_missing_token_raises(self):
        service = VPayService()
        with patch.object(service, '_request_access_token', return_value={'data': {}}):
            with self.assertRaises(VPayServiceError):
                service._get_access_token()


class VPayServiceOrderTests(TestCase):
    """Criação de pedido: total calculado no servidor e URL de checkout."""

    @override_settings(**VPAY_SETTINGS)
    def test_create_order_computes_total_and_builds_checkout_url(self):
        service = VPayService()

        response = MagicMock(status_code=200)
        response.raise_for_status.return_value = None
        response.json.return_value = {'data': {'orderId': 'ord-123', 'status': 'pending'}}

        with patch.object(service, '_get_access_token', return_value='tok-abc'), \
                patch('apps.subscriptions.vpay_service.requests.post', return_value=response) as post:
            result = service.create_order(
                customer={'name': 'Teste', 'email': 'teste@example.com'},
                items=[{'originProductId': 'plan-starter', 'name': 'Starter', 'quantity': 1, 'price': '299'}],
                merchant_order_reference='BET1ABC',
                currency='MZN',
            )

        self.assertTrue(result['success'])
        self.assertEqual(result['order_id'], 'ord-123')
        # A API não devolveu URL de checkout -> constrói o hospedado documentado.
        self.assertEqual(result['checkout_url'], 'https://checkout.vpay.co.mz/ord-123')

        payload = post.call_args.kwargs['json']
        self.assertEqual(
            post.call_args.args[0],
            'https://api.vpay.co.mz/v1/orders',
        )
        self.assertEqual(payload['currency'], 'MZN')
        self.assertEqual(payload['items'][0]['quantity'], 1)
        self.assertEqual(payload['items'][0]['price'], 299.0)
        self.assertIsInstance(payload['items'][0]['price'], float)
        self.assertEqual(payload['metadata']['merchantOrderReference'], 'BET1ABC')
        self.assertEqual(payload['metadata']['applicationId'], 'test-app-id')
        self.assertTrue(payload['shippingAddressDisabled'])
        self.assertTrue(payload['deliveryInfoDisabled'])

    @override_settings(**VPAY_SETTINGS)
    def test_create_order_uses_checkout_url_from_response(self):
        service = VPayService()
        response = MagicMock(status_code=200)
        response.raise_for_status.return_value = None
        response.json.return_value = {
            'data': {'orderId': 'ord-456', 'checkout': 'https://checkout.vpay.co.mz/custom'}
        }

        with patch.object(service, '_get_access_token', return_value='tok-abc'), \
                patch('apps.subscriptions.vpay_service.requests.post', return_value=response):
            result = service.create_order(
                customer={},
                items=[{'originProductId': 'p', 'name': 'P', 'quantity': 1, 'price': '1'}],
                merchant_order_reference='REF',
            )

        self.assertEqual(result['checkout_url'], 'https://checkout.vpay.co.mz/custom')

    @override_settings(**VPAY_SETTINGS)
    def test_create_order_timeout_is_ambiguous(self):
        service = VPayService()

        with patch.object(service, '_get_access_token', return_value='tok-abc'), \
                patch('apps.subscriptions.vpay_service.requests.post',
                      side_effect=__import__('requests').exceptions.Timeout('x')):
            result = service.create_order(
                customer={},
                items=[{'originProductId': 'p', 'name': 'P', 'quantity': 1, 'price': '1'}],
                merchant_order_reference='REF',
            )

        self.assertFalse(result['success'])
        self.assertTrue(result['ambiguous'])

    @override_settings(**VPAY_SETTINGS)
    def test_get_order_status_parses_paid(self):
        service = VPayService()
        response = MagicMock(status_code=200)
        response.raise_for_status.return_value = None
        response.json.return_value = {
            'data': {'orderId': 'ord-1', 'status': 'paid', 'amount': '1.00', 'transactionId': 'tx-1'}
        }

        with patch.object(service, '_get_access_token', return_value='tok-abc'), \
                patch('apps.subscriptions.vpay_service.requests.get', return_value=response) as get:
            result = service.get_order_status('ord-1')

        self.assertTrue(result['success'])
        self.assertEqual(result['status'], 'paid')
        self.assertEqual(result['transaction_id'], 'tx-1')
        self.assertEqual(
            get.call_args.args[0],
            'https://api.vpay.co.mz/v1/orders/ord-1/status',
        )


class VPayWebhookSignatureTests(TestCase):
    """Verificação de assinatura HMAC-SHA256 do webhook."""

    @override_settings(**VPAY_SETTINGS)
    def test_valid_signature(self):
        service = VPayService()
        body = b'{"event":"payment.confirmed","orderId":"ord-1","status":"paid"}'
        signature = hmac.new(b'webhook-secret', body, hashlib.sha256).hexdigest()
        self.assertTrue(service.verify_webhook_signature(body, f'sha256={signature}'))

    @override_settings(**VPAY_SETTINGS)
    def test_invalid_signature(self):
        service = VPayService()
        body = b'{"event":"payment.confirmed"}'
        self.assertFalse(service.verify_webhook_signature(body, 'sha256=deadbeef'))
        self.assertFalse(service.verify_webhook_signature(body, ''))
        self.assertFalse(service.verify_webhook_signature(body, 'plain-not-sha256'))

    @override_settings(**VPAY_SETTINGS)
    def test_signature_does_not_match_tampered_body(self):
        service = VPayService()
        original = b'{"orderId":"ord-1"}'
        signature = hmac.new(b'webhook-secret', original, hashlib.sha256).hexdigest()
        self.assertFalse(service.verify_webhook_signature(b'{"orderId":"ord-2"}', f'sha256={signature}'))


class VPayStatusMappingTests(TestCase):
    """Mapeamento de status VPay -> status local."""

    def setUp(self):
        self.user = make_user()

    def _payment(self, status='pending'):
        return Payment.objects.create(
            user=self.user,
            amount=299,
            currency='MZN',
            phone_number='844720861',
            transaction_id=f'BET{self.user.id}{status}{Payment.objects.count()}',
            gateway='vpay',
            payment_method='vpay',
            status=status,
            metadata={'plan': 'starter'},
        )

    @patch('apps.subscriptions.emails.send_payment_confirmed_email')
    @patch('apps.subscriptions.emails.send_subscription_activated_email')
    def test_paid_activates_subscription(self, activated_email, confirmed_email):
        payment = self._payment()
        result = apply_vpay_status(payment, 'paid', activate=True)

        payment.refresh_from_db()
        self.assertEqual(result, 'completed')
        self.assertEqual(payment.status, 'completed')
        self.assertIsNotNone(payment.subscription)
        self.assertEqual(payment.subscription.status, 'active')
        self.assertEqual(payment.subscription.plan_slug, 'starter')
        confirmed_email.assert_called_once()
        activated_email.assert_called_once()

    def test_failed_cancelled_expired_are_persisted(self):
        for vpay_status, expected in [('failed', 'failed'), ('cancelled', 'cancelled'), ('expired', 'expired')]:
            payment = self._payment()
            apply_vpay_status(payment, vpay_status)
            payment.refresh_from_db()
            self.assertEqual(payment.status, expected, f'{vpay_status} -> {expected}')

    def test_unknown_status_keeps_pending(self):
        payment = self._payment()
        apply_vpay_status(payment, 'something-new')
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'pending')


class VPayViewTests(TestCase):
    """Endpoints create_vpay_payment e vpay_webhook."""

    def setUp(self):
        self.client = APIClient()
        self.user = make_user()
        self.client.force_authenticate(self.user)

    @override_settings(**VPAY_SETTINGS)
    def test_create_vpay_payment_success(self):
        with patch('apps.subscriptions.vpay_views.vpay_service.create_order', return_value={
            'success': True,
            'order_id': 'ord-999',
            'checkout_url': 'https://checkout.vpay.co.mz/ord-999',
            'status': 'pending',
        }):
            response = self.client.post('/api/subscriptions/payments/vpay/create/', {
                'plan_slug': 'starter',
            }, format='json')

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['checkout_url'], 'https://checkout.vpay.co.mz/ord-999')
        self.assertEqual(data['payment']['gateway'], 'vpay')
        self.assertEqual(data['payment']['vpay_order_id'], 'ord-999')

        payment = Payment.objects.get(transaction_id=data['payment']['transaction_id'])
        self.assertEqual(payment.amount, 299)
        self.assertEqual(payment.currency, 'MZN')
        self.assertEqual(payment.gateway, 'vpay')
        self.assertEqual(payment.vpay_order_id, 'ord-999')
        self.assertEqual(payment.metadata['plan'], 'starter')

    @override_settings(**VPAY_SETTINGS)
    def test_create_vpay_payment_idempotent_reuses_pending_order(self):
        with patch('apps.subscriptions.vpay_views.vpay_service.create_order', return_value={
            'success': True,
            'order_id': 'ord-100',
            'checkout_url': 'https://checkout.vpay.co.mz/ord-100',
            'status': 'pending',
        }):
            first = self.client.post('/api/subscriptions/payments/vpay/create/', {'plan_slug': 'starter'}, format='json')
            self.assertEqual(first.status_code, 201)

        with patch('apps.subscriptions.vpay_views.vpay_service.get_order_status', return_value={
            'success': True,
            'status': 'pending',
        }):
            second = self.client.post('/api/subscriptions/payments/vpay/create/', {'plan_slug': 'starter'}, format='json')

        self.assertEqual(second.status_code, 200)
        self.assertEqual(Payment.objects.filter(user=self.user, gateway='vpay').count(), 1)
        self.assertEqual(second.json()['payment']['vpay_order_id'], 'ord-100')

    @override_settings(**VPAY_SETTINGS)
    def test_create_vpay_payment_rejects_invalid_plan(self):
        response = self.client.post('/api/subscriptions/payments/vpay/create/', {'plan_slug': 'nope'}, format='json')
        self.assertEqual(response.status_code, 400)

    @override_settings(**VPAY_SETTINGS)
    def test_create_vpay_payment_failure_is_ambiguous(self):
        with patch('apps.subscriptions.vpay_views.vpay_service.create_order', return_value={
            'success': False,
            'error': 'Timeout ao contactar a VPay.',
            'ambiguous': True,
        }):
            response = self.client.post('/api/subscriptions/payments/vpay/create/', {'plan_slug': 'starter'}, format='json')

        self.assertEqual(response.status_code, 502)
        payment = Payment.objects.filter(user=self.user, gateway='vpay').first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, 'pending')
        self.assertTrue(payment.metadata['ambiguous'])

        with patch('apps.subscriptions.vpay_views.vpay_service.create_order') as create_order:
            retry = self.client.post(
                '/api/subscriptions/payments/vpay/create/',
                {'plan_slug': 'starter'},
                format='json',
            )

        self.assertEqual(retry.status_code, 409)
        create_order.assert_not_called()

    @override_settings(**VPAY_SETTINGS)
    def test_webhook_valid_signature_confirms_payment(self):
        payment = Payment.objects.create(
            user=self.user,
            amount=299,
            currency='MZN',
            phone_number='844720861',
            transaction_id='BETWH',
            gateway='vpay',
            payment_method='vpay',
            status='pending',
            vpay_order_id='ord-wh',
            metadata={'plan': 'starter'},
        )

        payload = {
            'event': 'payment.confirmed',
            'orderId': 'ord-wh',
            'status': 'paid',
            'transactionId': 'tx-wh',
        }
        body = json.dumps(payload)
        signature = hmac.new(b'webhook-secret', body.encode('utf-8'), hashlib.sha256).hexdigest()

        with patch.object(vpay_service, 'webhook_secret', 'webhook-secret'), \
                patch('apps.subscriptions.emails.send_payment_confirmed_email'), \
                patch('apps.subscriptions.emails.send_subscription_activated_email'):
            response = self.client.post(
                '/api/subscriptions/payments/vpay/webhook/',
                data=body.encode('utf-8'),
                content_type='application/json',
                HTTP_X_VOIDPAY_SIGNATURE=f'sha256={signature}',
            )

        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')
        self.assertIsNotNone(payment.subscription)

    @override_settings(**VPAY_SETTINGS)
    def test_webhook_invalid_signature_rejected(self):
        with patch.object(vpay_service, 'webhook_secret', 'webhook-secret'):
            response = self.client.post(
                '/api/subscriptions/payments/vpay/webhook/',
                data=json.dumps({'event': 'payment.confirmed', 'orderId': 'x', 'status': 'paid'}).encode('utf-8'),
                content_type='application/json',
                HTTP_X_VOIDPAY_SIGNATURE='sha256=deadbeef',
            )

        self.assertEqual(response.status_code, 400)


class VPayCheckStatusTests(TestCase):
    """Polling: check_payment_status encaminha para o VPay."""

    @override_settings(**VPAY_SETTINGS)
    def test_check_payment_status_marks_paid(self):
        client = APIClient()
        user = make_user()
        client.force_authenticate(user)

        payment = Payment.objects.create(
            user=user,
            amount=299,
            currency='MZN',
            phone_number='844720861',
            transaction_id='BETCHECK',
            gateway='vpay',
            payment_method='vpay',
            status='pending',
            vpay_order_id='ord-check',
            metadata={'plan': 'starter'},
        )

        with patch('apps.subscriptions.payment_views.vpay_service.get_order_status', return_value={
            'success': True,
            'status': 'paid',
            'transaction_id': 'tx-check',
        }), patch('apps.subscriptions.emails.send_payment_confirmed_email'), \
                patch('apps.subscriptions.emails.send_subscription_activated_email'):
            response = client.get(f'/api/subscriptions/payments/check/{payment.transaction_id}/')

        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')
        self.assertEqual(response.json()['status'], 'completed')
