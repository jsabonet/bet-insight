from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.users.models import User

from .models import Payment
from .emails import send_abandoned_checkout_email
from .tasks import send_abandoned_checkout_emails


class AbandonedCheckoutAdminTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='checkout-customer',
            email='checkout@example.com',
            password='test-password',
            first_name='Cliente',
            last_name='Teste',
            phone='+258841234567',
        )
        self.client = APIClient()

    def create_payment(self, **overrides):
        fields = {
            'user': self.user,
            'amount': '250.00',
            'currency': 'MZN',
            'phone_number': '',
            'gateway': 'vpay',
            'transaction_id': 'BET-CHECKOUT-1',
            'vpay_order_id': 'vpay-order-1',
            'status': 'pending',
            'metadata': {
                'plan': 'premium_vitalicio',
                'plan_name': 'Premium Vitalício',
                'checkout_url': 'https://checkout.vpay.co.mz/vpay-order-1',
            },
        }
        fields.update(overrides)
        return Payment.objects.create(**fields)

    def test_abandoned_checkout_endpoint_is_admin_only(self):
        response = self.client.get('/api/subscriptions/admin/abandoned-checkouts/')
        self.assertEqual(response.status_code, 401)

        self.client.force_authenticate(self.user)
        response = self.client.get('/api/subscriptions/admin/abandoned-checkouts/')
        self.assertEqual(response.status_code, 403)

    def test_admin_sees_stale_pending_checkout_and_contact_details_only(self):
        stale = self.create_payment()
        Payment.objects.filter(pk=stale.pk).update(
            created_at=timezone.now() - timedelta(hours=2),
        )
        self.create_payment(
            transaction_id='BET-CHECKOUT-2',
            vpay_order_id='vpay-order-2',
        )
        self.create_payment(
            transaction_id='BET-CHECKOUT-3',
            vpay_order_id='vpay-order-3',
            status='completed',
        )

        self.user.is_staff = True
        self.user.save(update_fields=['is_staff'])
        self.client.force_authenticate(self.user)
        response = self.client.get('/api/subscriptions/admin/abandoned-checkouts/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['abandonment_delay_minutes'], 60)
        checkout = response.data['results'][0]
        self.assertEqual(checkout['payment_id'], stale.pk)
        self.assertEqual(checkout['name'], 'Cliente Teste')
        self.assertEqual(checkout['phone'], '+258841234567')
        self.assertEqual(checkout['email'], self.user.email)
        self.assertEqual(checkout['plan_name'], 'Premium Vitalício')
        self.assertEqual(checkout['transaction_id'], stale.transaction_id)
        self.assertGreaterEqual(checkout['minutes_abandoned'], 120)


class AbandonedCheckoutEmailTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='recovery-customer',
            email='recovery@example.com',
            password='test-password',
            phone='+258841234567',
        )

    def create_payment(self, transaction_id='BET-RECOVERY-1', status='pending'):
        payment = Payment.objects.create(
            user=self.user,
            amount='250.00',
            currency='MZN',
            phone_number=self.user.phone,
            gateway='vpay',
            transaction_id=transaction_id,
            vpay_order_id=f'order-{transaction_id}',
            status=status,
            metadata={
                'plan': 'premium_vitalicio',
                'plan_name': 'Premium Vitalício',
                'checkout_url': 'https://checkout.vpay.co.mz/order',
            },
        )
        Payment.objects.filter(pk=payment.pk).update(
            created_at=timezone.now() - timedelta(hours=2),
        )
        return payment

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_recovery_email_contains_order_details_and_resume_link(self):
        payment = self.create_payment()

        sent = send_abandoned_checkout_email(payment)

        self.assertTrue(sent)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Premium Vitalício', mail.outbox[0].body)
        self.assertIn(payment.transaction_id, mail.outbox[0].body)
        self.assertIn('https://checkout.vpay.co.mz/order', mail.outbox[0].body)

    @patch('apps.subscriptions.tasks.send_abandoned_checkout_email', return_value=True)
    def test_sends_recovery_email_once_for_old_pending_vpay_checkout(self, send_email):
        payment = self.create_payment()

        result = send_abandoned_checkout_emails.run()
        second_result = send_abandoned_checkout_emails.run()

        payment.refresh_from_db()
        self.assertEqual(result, {'sent': 1, 'failed': 0})
        self.assertEqual(second_result, {'sent': 0, 'failed': 0})
        self.assertIsNotNone(payment.recovery_email_sent_at)
        send_email.assert_called_once()

    @patch('apps.subscriptions.tasks.send_abandoned_checkout_email', return_value=False)
    def test_failed_email_is_left_retryable(self, send_email):
        payment = self.create_payment()

        result = send_abandoned_checkout_emails.run()

        payment.refresh_from_db()
        self.assertEqual(result, {'sent': 0, 'failed': 1})
        self.assertIsNone(payment.recovery_email_sent_at)
        send_email.assert_called_once()

    @patch('apps.subscriptions.tasks.send_abandoned_checkout_email', return_value=True)
    def test_does_not_send_for_recent_or_completed_checkout(self, send_email):
        self.create_payment(transaction_id='BET-RECENT-1')
        recent = Payment.objects.get(transaction_id='BET-RECENT-1')
        Payment.objects.filter(pk=recent.pk).update(created_at=timezone.now())
        self.create_payment(transaction_id='BET-COMPLETED-1', status='completed')

        result = send_abandoned_checkout_emails.run()

        self.assertEqual(result, {'sent': 0, 'failed': 0})
        send_email.assert_not_called()
