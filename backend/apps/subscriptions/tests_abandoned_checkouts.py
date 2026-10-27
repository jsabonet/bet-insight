from datetime import timedelta
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.notifications.models import Notification, PushSubscription
from apps.users.models import User

from .models import Payment
from .emails import send_abandoned_checkout_email
from .tasks import (
    reconcile_admin_payment_notifications,
    send_abandoned_checkout_emails,
    send_admin_payment_notification,
)
from .payment_helpers import apply_vpay_status


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


class AdminPaymentNotificationTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='admin-notification-customer',
            email='customer@example.com',
            password='test-password',
        )
        self.admin = User.objects.create_user(
            username='payment-admin',
            email='admin@example.com',
            password='test-password',
            is_staff=True,
            push_enabled=True,
        )
        self.push_subscription = PushSubscription.objects.create(
            user=self.admin,
            endpoint='https://fcm.googleapis.com/admin-device',
            p256dh_key='public-key',
            auth_key='auth-key',
        )
        self.payment = Payment.objects.create(
            user=self.customer,
            amount='250.00',
            currency='MZN',
            phone_number='',
            gateway='vpay',
            transaction_id='BET-ADMIN-NOTIFICATION-1',
            vpay_order_id='admin-notification-order',
            status='completed',
            metadata={'plan_name': 'Premium Vitalício'},
        )

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='public', WEBPUSH_VAPID_PRIVATE_KEY='private')
    @patch('apps.subscriptions.tasks.deliver_push_once', return_value=True)
    @patch('apps.subscriptions.tasks.send_template_email', return_value=1)
    def test_confirmed_sale_notifies_admin_once_by_email_and_push(self, send_email, send_push):
        result = send_admin_payment_notification.run(self.payment.pk, 'sale')
        repeated_result = send_admin_payment_notification.run(self.payment.pk, 'sale')

        self.payment.refresh_from_db()
        self.assertEqual(result, {'email_sent': True, 'push_sent': True})
        self.assertEqual(repeated_result, {'email_sent': True, 'push_sent': True})
        self.assertIsNotNone(self.payment.admin_sale_email_sent_at)
        self.assertIsNotNone(self.payment.admin_sale_push_sent_at)
        send_email.assert_called_once()
        self.assertEqual(send_email.call_args.kwargs['to'], ['admin@example.com'])
        send_push.assert_called_once()
        self.assertEqual(
            send_push.call_args.args[1],
            f'admin-payment-sale:{self.payment.pk}',
        )
        self.assertTrue(
            Notification.objects.filter(
                user=self.admin,
                event_key=f'admin-payment-sale:{self.payment.pk}',
            ).exists()
        )

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='public', WEBPUSH_VAPID_PRIVATE_KEY='private')
    @patch('apps.subscriptions.tasks.deliver_push_once', side_effect=[False, True])
    @patch('apps.subscriptions.tasks.send_template_email', return_value=1)
    def test_failed_push_retries_without_resending_successful_email(self, send_email, send_push):
        first_result = reconcile_admin_payment_notifications.run()
        second_result = reconcile_admin_payment_notifications.run()

        self.payment.refresh_from_db()
        self.assertEqual(first_result, {'sales': 1, 'abandoned': 0, 'incomplete': 1})
        self.assertEqual(second_result, {'sales': 1, 'abandoned': 0, 'incomplete': 0})
        self.assertIsNotNone(self.payment.admin_sale_email_sent_at)
        self.assertIsNotNone(self.payment.admin_sale_push_sent_at)
        send_email.assert_called_once()
        self.assertEqual(send_push.call_count, 2)

    @patch('apps.subscriptions.tasks.send_admin_payment_notification.delay')
    @patch('apps.subscriptions.emails.send_subscription_activated_email')
    @patch('apps.subscriptions.emails.send_payment_confirmed_email')
    def test_confirming_payment_enqueues_admin_sale_notification(
        self,
        send_payment_email,
        send_activation_email,
        enqueue_notification,
    ):
        self.payment.status = 'pending'
        self.payment.save(update_fields=['status'])

        with self.captureOnCommitCallbacks(execute=True):
            apply_vpay_status(self.payment, 'paid', activate=True)

        enqueue_notification.assert_called_once_with(self.payment.pk, 'sale')

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='public', WEBPUSH_VAPID_PRIVATE_KEY='private')
    @patch('apps.subscriptions.tasks.deliver_push_once', return_value=True)
    @patch('apps.subscriptions.tasks.send_template_email', return_value=1)
    def test_reconciliation_notifies_for_abandoned_checkout(self, send_email, send_push):
        Payment.objects.filter(pk=self.payment.pk).update(
            status='pending',
            created_at=timezone.now() - timedelta(hours=2),
        )

        result = reconcile_admin_payment_notifications.run()

        self.payment.refresh_from_db()
        self.assertEqual(result, {'sales': 0, 'abandoned': 1, 'incomplete': 0})
        self.assertIsNotNone(self.payment.admin_abandoned_email_sent_at)
        self.assertIsNotNone(self.payment.admin_abandoned_push_sent_at)
        self.assertEqual(send_email.call_args.kwargs['subject'], 'Carrinho abandonado - PlacarCerto')
        self.assertEqual(
            send_push.call_args.args[1],
            f'admin-payment-abandoned:{self.payment.pk}',
        )
