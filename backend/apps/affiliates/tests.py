"""Testes do sistema de afiliados."""
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .models import Affiliate, AffiliateReferral, AffiliateCommission
from .services import assign_referral, create_commission_if_applicable
from apps.subscriptions.models import Payment

User = get_user_model()


def make_user(username='buyer', email='buyer@example.com'):
    return User.objects.create_user(username=username, email=email, password='x')


def make_affiliate(user, code='AFFTEST', rate='0.40'):
    return Affiliate.objects.create(
        user=user,
        code=code,
        status='active',
        tier='standard',
        commission_rate=Decimal(rate),
        renewal_rate=Decimal('0.10'),
    )


def make_payment(user, amount='599.00', plan='pro', metadata=None):
    meta = {'plan': plan, 'plan_name': 'Pro', 'gateway': 'vpay'}
    if metadata:
        meta.update(metadata)
    return Payment.objects.create(
        user=user,
        amount=Decimal(amount),
        currency='MZN',
        phone_number='',
        transaction_id=f'TX{user.id}',
        gateway='vpay',
        payment_method='vpay',
        status='completed',
        metadata=meta,
    )


class CommissionTests(TestCase):
    def test_commission_created_for_valid_payment(self):
        affiliate_user = make_user('aff', 'aff@example.com')
        affiliate = make_affiliate(affiliate_user)
        buyer = make_user('buyer', 'buyer@example.com')
        payment = make_payment(
            buyer, metadata={'affiliate_code': 'AFFTEST', 'affiliate_id': affiliate.id}
        )
        commission = create_commission_if_applicable(payment)
        self.assertIsNotNone(commission)
        self.assertEqual(commission.status, 'pending')
        self.assertEqual(commission.amount, Decimal('239.60'))  # 599 * 0.40

    @patch('apps.notifications.tasks.send_affiliate_push.delay')
    def test_new_referral_enqueues_push_after_commit(self, enqueue):
        affiliate_user = make_user('ref-affiliate', 'ref-affiliate@example.com')
        affiliate = make_affiliate(affiliate_user, code='REFTEST')
        referred_user = make_user('referred-user', 'referred@example.com')

        with self.captureOnCommitCallbacks(execute=True):
            referral = assign_referral(referred_user, affiliate.code)

        enqueue.assert_called_once()
        self.assertEqual(enqueue.call_args.args[:3], (
            affiliate_user.id,
            'referral_registered',
            str(referral.pk),
        ))

    @patch('apps.notifications.tasks.send_affiliate_push.delay')
    def test_new_commission_enqueues_push_after_commit(self, enqueue):
        affiliate_user = make_user('commission-affiliate', 'commission-affiliate@example.com')
        affiliate = make_affiliate(affiliate_user, code='COMTEST')
        buyer = make_user('commission-buyer', 'commission-buyer@example.com')
        payment = make_payment(
            buyer,
            metadata={'affiliate_code': 'COMTEST', 'affiliate_id': affiliate.id},
        )

        with self.captureOnCommitCallbacks(execute=True):
            commission = create_commission_if_applicable(payment)

        enqueue.assert_called_once()
        self.assertEqual(enqueue.call_args.args[:3], (
            affiliate_user.id,
            'commission_created',
            str(commission.pk),
        ))

    def test_idempotent(self):
        affiliate_user = make_user('aff2', 'aff2@example.com')
        affiliate = make_affiliate(affiliate_user, code='AFF2')
        buyer = make_user('buyer2', 'buyer2@example.com')
        payment = make_payment(buyer, metadata={'affiliate_code': 'AFF2'})
        first = create_commission_if_applicable(payment)
        second = create_commission_if_applicable(payment)
        self.assertEqual(first.id, second.id)
        self.assertEqual(AffiliateCommission.objects.count(), 1)

    def test_self_purchase_no_commission(self):
        user = make_user('self', 'self@example.com')
        affiliate = make_affiliate(user, code='SELF')
        payment = make_payment(user, metadata={'affiliate_code': 'SELF', 'affiliate_id': affiliate.id})
        commission = create_commission_if_applicable(payment)
        self.assertIsNone(commission)

    def test_excluded_plan_no_commission(self):
        affiliate_user = make_user('aff3', 'aff3@example.com')
        affiliate = make_affiliate(affiliate_user, code='AFF3')
        buyer = make_user('buyer3', 'buyer3@example.com')
        payment = make_payment(buyer, plan='teste', amount='1.00', metadata={'affiliate_code': 'AFF3'})
        commission = create_commission_if_applicable(payment)
        self.assertIsNone(commission)

    def test_no_affiliate_code(self):
        buyer = make_user('buyer4', 'buyer4@example.com')
        payment = make_payment(buyer)
        commission = create_commission_if_applicable(payment)
        self.assertIsNone(commission)

    def test_renewal_uses_renewal_rate(self):
        affiliate_user = make_user('aff5', 'aff5@example.com')
        affiliate = make_affiliate(affiliate_user, code='AFF5')
        buyer = make_user('buyer5', 'buyer5@example.com')

        # Indicação já convertida numa compra anterior (renovação).
        AffiliateReferral.objects.create(
            affiliate=affiliate,
            user=buyer,
            code='AFF5',
            source='link',
            converted_at=timezone.now(),
        )

        payment = make_payment(buyer, metadata={'affiliate_code': 'AFF5', 'affiliate_id': affiliate.id})
        commission = create_commission_if_applicable(payment)

        self.assertIsNotNone(commission)
        self.assertEqual(commission.rate, Decimal('0.10'))  # renewal_rate
        self.assertEqual(commission.amount, Decimal('59.90'))  # 599 * 0.10
