"""Testes do sistema de afiliados."""
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.notifications.models import Notification
from .models import (
    Affiliate, AffiliateTermsAcceptance, AffiliateReferral, AffiliateCommission, AffiliateWithdrawal,
)
from .services import assign_referral, create_commission_if_applicable
from .services import (
    _update_affiliate_balances,
    assign_member_referral,
    reward_member_referral_for_first_analysis,
)
from .terms import AFFILIATE_TERMS_VERSION
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
        accepted_terms_version=AFFILIATE_TERMS_VERSION,
        terms_accepted_at=timezone.now(),
    )


class AffiliateTermsAcceptanceTests(TestCase):
    def setUp(self):
        self.user = make_user('affiliate-applicant', 'affiliate-applicant@example.com')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_application_requires_explicit_current_terms_acceptance(self):
        response = self.client.post(
            '/api/affiliates/apply/',
            {'payout_method': 'mpesa', 'payout_account': '841234567'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Affiliate.objects.filter(user=self.user).exists())

    @patch('apps.affiliates.emails.send_template_email')
    def test_application_records_accepted_terms_version_and_timestamp(self, _send_email):
        response = self.client.post(
            '/api/affiliates/apply/',
            {
                'payout_method': 'mpesa',
                'payout_account': '841234567',
                'terms_version': AFFILIATE_TERMS_VERSION,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        affiliate = Affiliate.objects.get(user=self.user)
        self.assertEqual(affiliate.accepted_terms_version, AFFILIATE_TERMS_VERSION)
        self.assertIsNotNone(affiliate.terms_accepted_at)
        self.assertTrue(AffiliateTermsAcceptance.objects.filter(
            affiliate=affiliate,
            terms_version=AFFILIATE_TERMS_VERSION,
            accepted_at=affiliate.terms_accepted_at,
        ).exists())

    def test_existing_affiliate_must_accept_current_terms_before_using_program(self):
        affiliate = make_affiliate(self.user)
        affiliate.accepted_terms_version = ''
        affiliate.terms_accepted_at = None
        affiliate.save(update_fields=['accepted_terms_version', 'terms_accepted_at'])

        blocked = self.client.get('/api/affiliates/me/stats/')
        self.assertEqual(blocked.status_code, 403)
        self.assertEqual(blocked.data['code'], 'affiliate_terms_required')

        accepted = self.client.post(
            '/api/affiliates/apply/',
            {'terms_version': AFFILIATE_TERMS_VERSION},
            format='json',
        )
        self.assertEqual(accepted.status_code, 200)
        affiliate.refresh_from_db()
        self.assertEqual(affiliate.accepted_terms_version, AFFILIATE_TERMS_VERSION)
        self.assertIsNotNone(affiliate.terms_accepted_at)


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
    def test_member_referral_summary_is_private_and_returns_share_code(self):
        user = make_user('summary-member', 'summary-member@example.com')
        client = APIClient()
        client.force_authenticate(user)

        response = client.get('/api/affiliates/member/referrals/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], user.member_referral_code)
        self.assertEqual(response.data['reward_per_member'], 5)

    def test_member_invite_grants_five_credits_to_both_once(self):
        inviter = make_user('member-inviter', 'member-inviter@example.com')
        invitee = make_user('member-invitee', 'member-invitee@example.com')
        inviter.signup_ip = '192.0.2.10'
        inviter.device_fingerprint = 'inviter-device'
        inviter.save(update_fields=['signup_ip', 'device_fingerprint'])
        invitee.signup_ip = '192.0.2.11'
        invitee.device_fingerprint = 'invitee-device'
        invitee.total_analyses = 1
        invitee.save(update_fields=['signup_ip', 'device_fingerprint', 'total_analyses'])
        referral = assign_member_referral(invitee, inviter.member_referral_code)

        self.assertIsNotNone(referral)
        self.assertTrue(reward_member_referral_for_first_analysis(invitee))
        self.assertFalse(reward_member_referral_for_first_analysis(invitee))

        inviter.refresh_from_db()
        invitee.refresh_from_db()
        referral.refresh_from_db()
        self.assertEqual(inviter.bonus_analysis_credits, 5)
        self.assertEqual(invitee.bonus_analysis_credits, 5)
        self.assertIsNotNone(referral.rewarded_at)
        self.assertEqual(referral.reward_status, 'rewarded')

    def test_member_referral_reward_is_blocked_for_shared_ip(self):
        inviter = make_user('shared-ip-inviter', 'shared-ip-inviter@example.com')
        invitee = make_user('shared-ip-invitee', 'shared-ip-invitee@example.com')
        inviter.signup_ip = '192.0.2.12'
        invitee.signup_ip = '192.0.2.12'
        invitee.total_analyses = 1
        inviter.save(update_fields=['signup_ip'])
        invitee.save(update_fields=['signup_ip', 'total_analyses'])
        referral = assign_member_referral(invitee, inviter.member_referral_code)

        self.assertFalse(reward_member_referral_for_first_analysis(invitee))

        inviter.refresh_from_db()
        invitee.refresh_from_db()
        referral.refresh_from_db()
        self.assertEqual(inviter.bonus_analysis_credits, 0)
        self.assertEqual(invitee.bonus_analysis_credits, 0)
        self.assertEqual(referral.reward_status, 'ineligible')

    def test_member_referral_reward_is_blocked_for_shared_device(self):
        inviter = make_user('shared-device-inviter', 'shared-device-inviter@example.com')
        invitee = make_user('shared-device-invitee', 'shared-device-invitee@example.com')
        inviter.signup_ip = '192.0.2.15'
        inviter.device_fingerprint = 'shared-device'
        invitee.signup_ip = '192.0.2.16'
        invitee.device_fingerprint = 'shared-device'
        invitee.total_analyses = 1
        inviter.save(update_fields=['signup_ip', 'device_fingerprint'])
        invitee.save(update_fields=['signup_ip', 'device_fingerprint', 'total_analyses'])
        referral = assign_member_referral(invitee, inviter.member_referral_code)

        self.assertFalse(reward_member_referral_for_first_analysis(invitee))

        referral.refresh_from_db()
        self.assertEqual(referral.reward_status, 'ineligible')

    def test_member_referral_reward_requires_first_analysis(self):
        inviter = make_user('late-inviter', 'late-inviter@example.com')
        invitee = make_user('late-invitee', 'late-invitee@example.com')
        inviter.signup_ip = '192.0.2.13'
        invitee.signup_ip = '192.0.2.14'
        invitee.total_analyses = 2
        inviter.save(update_fields=['signup_ip'])
        invitee.save(update_fields=['signup_ip', 'total_analyses'])
        assign_member_referral(invitee, inviter.member_referral_code)

        self.assertFalse(reward_member_referral_for_first_analysis(invitee))
        inviter.refresh_from_db()
        invitee.refresh_from_db()
        self.assertEqual(inviter.bonus_analysis_credits, 0)
        self.assertEqual(invitee.bonus_analysis_credits, 0)

    def test_affiliate_code_does_not_trigger_member_reward_program(self):
        inviter = make_user('affiliate-inviter', 'affiliate-inviter@example.com')
        affiliate = make_affiliate(inviter, code='MEMBERAFF')
        invitee = make_user('affiliate-invitee', 'affiliate-invitee@example.com')

        referral = assign_member_referral(invitee, affiliate.code)

        self.assertIsNone(referral)

    def test_member_cannot_invite_self(self):
        user = make_user('self-inviter', 'self-inviter@example.com')

        self.assertIsNone(assign_member_referral(user, user.member_referral_code))

    def test_bonus_credits_extend_daily_analysis_limit(self):
        user = make_user('bonus-user', 'bonus-user@example.com')
        from apps.subscriptions.plan_config import get_plan_limit
        daily_limit = get_plan_limit('freemium')
        user.daily_analysis_count = daily_limit
        user.last_analysis_date = timezone.now().date()
        user.bonus_analysis_credits = 2
        user.save()

        self.assertTrue(user.can_analyze())
        user.increment_analysis_count()
        user.refresh_from_db()
        self.assertEqual(user.daily_analysis_count, daily_limit + 1)
        self.assertEqual(user.bonus_analysis_credits, 1)


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
        self.assertEqual(commission.amount, Decimal('100.00'))
        self.assertEqual(commission.commission_type, 'fixed')

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

    def test_simulated_lifetime_plan_never_generates_commission(self):
        affiliate_user = make_user('test-plan-aff', 'test-plan-aff@example.com')
        make_affiliate(affiliate_user, code='TESTPLAN')
        buyer = make_user('test-plan-buyer', 'test-plan-buyer@example.com')
        payment = make_payment(
            buyer,
            amount='250.00',
            plan='premium_vitalicio_teste',
            metadata={'affiliate_code': 'TESTPLAN'},
        )

        self.assertIsNone(create_commission_if_applicable(payment))

    def test_no_affiliate_code(self):
        buyer = make_user('buyer4', 'buyer4@example.com')
        payment = make_payment(buyer)
        commission = create_commission_if_applicable(payment)
        self.assertIsNone(commission)

    def test_previously_converted_referral_does_not_receive_renewal_commission(self):
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

        self.assertIsNone(commission)

    def test_only_first_referred_purchase_receives_a_commission(self):
        affiliate_user = make_user('first-sale-affiliate', 'first-sale-affiliate@example.com')
        affiliate = make_affiliate(affiliate_user, code='FIRSTSALE')
        buyer = make_user('first-sale-buyer', 'first-sale-buyer@example.com')
        metadata = {'affiliate_code': 'FIRSTSALE', 'affiliate_id': affiliate.id}
        first_payment = make_payment(buyer, metadata=metadata)
        second_payment = Payment.objects.create(
            user=buyer,
            amount=Decimal('250.00'),
            currency='MZN',
            phone_number='',
            transaction_id='TX-SECOND-PURCHASE',
            gateway='vpay',
            payment_method='vpay',
            status='completed',
            metadata={'plan': 'premium_vitalicio', **metadata},
        )

        first_commission = create_commission_if_applicable(first_payment)
        second_commission = create_commission_if_applicable(second_payment)

        self.assertIsNotNone(first_commission)
        self.assertIsNone(second_commission)


class AffiliateWithdrawalTests(TestCase):
    def setUp(self):
        self.affiliate_user = make_user('withdraw-aff', 'withdraw-aff@example.com')
        self.affiliate = make_affiliate(self.affiliate_user, code='WITHDRAW')
        buyer = make_user('withdraw-buyer', 'withdraw-buyer@example.com')
        payment = make_payment(buyer)
        self.commission = AffiliateCommission.objects.create(
            affiliate=self.affiliate,
            payment=payment,
            amount=Decimal('500.00'),
            rate=Decimal('0.40'),
            status='available',
        )
        self.affiliate.payout_account = '841234567'
        self.affiliate.save(update_fields=['payout_account'])
        _update_affiliate_balances(self.affiliate)
        self.client = APIClient()
        self.client.force_authenticate(self.affiliate_user)

    @patch('apps.affiliates.emails.send_mail')
    @patch('apps.affiliates.emails.send_withdrawal_requested_email')
    def test_request_persists_and_reserves_balance(self, send_email, admin_send_mail):
        admin = make_user('withdraw-notice-admin', 'withdraw-notice@example.com')
        admin.is_staff = True
        admin.save(update_fields=['is_staff'])

        response = self.client.post(
            '/api/affiliates/me/withdraw/',
            {'amount': '200.00'},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(AffiliateWithdrawal.objects.count(), 1)
        self.assertEqual(response.data['status'], 'requested')
        self.assertEqual(response.data['fee_rate'], Decimal('6'))
        self.assertEqual(response.data['fee_amount'], Decimal('12.00'))
        self.assertEqual(response.data['payout_amount'], Decimal('188.00'))
        withdrawal = AffiliateWithdrawal.objects.get()
        self.assertEqual(withdrawal.payout_amount, Decimal('188.00'))
        self.affiliate.refresh_from_db()
        self.assertEqual(self.affiliate.available_balance, Decimal('300.00'))
        send_email.assert_called_once()
        admin_send_mail.assert_called_once()

    @patch('apps.affiliates.emails.send_mail')
    @patch('apps.affiliates.emails.send_withdrawal_requested_email')
    def test_reserved_balance_cannot_be_requested_twice(self, _send_email, _admin_send_mail):
        first = self.client.post(
            '/api/affiliates/me/withdraw/', {'amount': '300.00'}, format='json',
        )
        second = self.client.post(
            '/api/affiliates/me/withdraw/', {'amount': '300.00'}, format='json',
        )

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(AffiliateWithdrawal.objects.count(), 1)

    @patch('apps.affiliates.emails.send_mail')
    @patch('apps.affiliates.emails.send_withdrawal_requested_email')
    def test_admin_can_process_and_record_payment(self, _send_email, _admin_send_mail):
        response = self.client.post(
            '/api/affiliates/me/withdraw/', {'amount': '200.00'}, format='json',
        )
        withdrawal_id = response.data['id']
        admin = make_user('withdraw-admin', 'withdraw-admin@example.com')
        admin.is_staff = True
        admin.save(update_fields=['is_staff'])
        self.client.force_authenticate(admin)

        processing = self.client.post(
            f'/api/affiliates/admin/withdrawals/{withdrawal_id}/process/',
            format='json',
        )
        paid = self.client.post(
            f'/api/affiliates/admin/withdrawals/{withdrawal_id}/complete/',
            {'transaction_reference': 'MPESA-TX-123'},
            format='json',
        )

        self.assertEqual(processing.status_code, 200)
        self.assertEqual(paid.status_code, 200)
        withdrawal = AffiliateWithdrawal.objects.get(pk=withdrawal_id)
        self.assertEqual(withdrawal.status, 'paid')
        self.assertEqual(withdrawal.transaction_reference, 'MPESA-TX-123')
        self.assertTrue(Notification.objects.filter(
            user=self.affiliate_user,
            event_key=f'affiliate_withdrawal_paid_{withdrawal.pk}',
        ).exists())
        self.affiliate.refresh_from_db()
        self.assertEqual(self.affiliate.available_balance, Decimal('300.00'))

    @patch('apps.affiliates.emails.send_mail')
    @patch('apps.affiliates.emails.send_withdrawal_requested_email')
    def test_rejection_releases_reserved_balance(self, _send_email, _admin_send_mail):
        response = self.client.post(
            '/api/affiliates/me/withdraw/', {'amount': '200.00'}, format='json',
        )
        admin = make_user('withdraw-reject-admin', 'withdraw-reject@example.com')
        admin.is_staff = True
        admin.save(update_fields=['is_staff'])
        self.client.force_authenticate(admin)

        rejected = self.client.post(
            f"/api/affiliates/admin/withdrawals/{response.data['id']}/reject/",
            {'reason': 'Dados de pagamento inválidos.'},
            format='json',
        )

        self.assertEqual(rejected.status_code, 200)
        self.affiliate.refresh_from_db()
        self.assertEqual(self.affiliate.available_balance, Decimal('500.00'))

    @patch('apps.affiliates.emails.send_mail')
    @patch('apps.affiliates.emails.send_withdrawal_requested_email')
    def test_commission_cannot_be_paid_while_allocated_to_withdrawal(self, _send_email, _admin_send_mail):
        self.client.post(
            '/api/affiliates/me/withdraw/', {'amount': '200.00'}, format='json',
        )
        admin = make_user('withdraw-commission-admin', 'withdraw-commission@example.com')
        admin.is_staff = True
        admin.save(update_fields=['is_staff'])
        self.client.force_authenticate(admin)

        response = self.client.post(
            f'/api/affiliates/admin/commissions/{self.commission.pk}/mark-paid/',
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.commission.refresh_from_db()
        self.assertEqual(self.commission.status, 'available')
