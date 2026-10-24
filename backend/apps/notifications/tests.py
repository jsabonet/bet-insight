"""Testes da app de notificações.

Garante que todos os templates HTML/texto renderizam sem erros com um contexto
de exemplo, e que o serviço de envio funciona com o backend console (default).
"""
from unittest.mock import patch
from datetime import timedelta
import base64
from io import StringIO

from django.core import mail
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from cryptography.hazmat.primitives import serialization
from rest_framework.test import APIClient

from apps.analysis.models import Analysis
from apps.matches.models import League, Match, Team
from apps.notifications.delivery import deliver_push_once
from apps.notifications.models import PushDelivery, PushSubscription
from apps.notifications.service import render_template, send_template_email
from apps.notifications.tasks import (
    poll_analyzed_match_events,
    send_affiliate_push,
    send_analysis_ready_push,
    send_analyzed_match_reminders,
)
from py_vapid import Vapid

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


class WebPushAPITests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='push-user',
            email='push@example.com',
            password='Strong-test-pass-123',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='', WEBPUSH_VAPID_PRIVATE_KEY='')
    def test_status_reports_push_unavailable_without_vapid_keys(self):
        response = self.client.get('/api/users/push/status/')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['available'])
        self.assertEqual(response.data['public_key'], '')

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='', WEBPUSH_VAPID_PRIVATE_KEY='')
    def test_subscription_is_rejected_when_push_is_not_configured(self):
        response = self.client.post('/api/users/push/subscriptions/', {
            'subscription': {
                'endpoint': 'https://fcm.googleapis.com/subscription',
                'keys': {'p256dh': 'public-key', 'auth': 'auth-key'},
            },
        }, format='json')

        self.assertEqual(response.status_code, 503)
        self.assertEqual(PushSubscription.objects.count(), 0)

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='public', WEBPUSH_VAPID_PRIVATE_KEY='private')
    def test_subscription_registers_per_device_and_preferences(self):
        response = self.client.post('/api/users/push/subscriptions/', {
            'subscription': {
                'endpoint': 'https://fcm.googleapis.com/device-one',
                'keys': {'p256dh': 'public-key', 'auth': 'auth-key'},
            },
        }, format='json')
        self.assertEqual(response.status_code, 201)

        response = self.client.patch('/api/users/push/preferences/', {
            'push_enabled': True,
            'analysis_ready_enabled': False,
            'match_reminders_enabled': True,
            'match_events_enabled': False,
            'affiliate_notifications_enabled': False,
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['push_enabled'])
        self.assertFalse(response.data['analysis_ready_enabled'])
        self.assertTrue(response.data['match_reminders_enabled'])

        subscription = PushSubscription.objects.get(user=self.user)
        self.assertFalse(subscription.analysis_ready_enabled)
        self.assertFalse(subscription.match_events_enabled)
        self.assertFalse(subscription.affiliate_notifications_enabled)

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='public', WEBPUSH_VAPID_PRIVATE_KEY='private')
    def test_subscription_rejects_non_push_provider_endpoint(self):
        response = self.client.post('/api/users/push/subscriptions/', {
            'subscription': {
                'endpoint': 'https://attacker.example/subscription',
                'keys': {'p256dh': 'public-key', 'auth': 'auth-key'},
            },
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(PushSubscription.objects.count(), 0)

    def test_enabling_push_requires_a_registered_subscription(self):
        self.user.push_enabled = False
        self.user.save(update_fields=['push_enabled'])
        response = self.client.patch('/api/users/push/preferences/', {'push_enabled': True}, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.user.push_enabled)


class PushDeliveryTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='delivery-user',
            email='delivery@example.com',
            password='Strong-test-pass-123',
            push_enabled=True,
        )
        self.subscription = PushSubscription.objects.create(
            user=self.user,
            endpoint='https://fcm.googleapis.com/device-one',
            p256dh_key='public-key',
            auth_key='auth-key',
        )

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='public', WEBPUSH_VAPID_PRIVATE_KEY='private')
    @patch('apps.notifications.delivery.send_web_push', return_value=True)
    def test_event_is_delivered_only_once_per_subscription(self, send_push):
        payload = {'title': 'Análise pronta', 'body': 'Home vs Away', 'url': '/match/1'}

        self.assertTrue(deliver_push_once(self.subscription, 'analysis-ready:1', payload))
        self.assertTrue(deliver_push_once(self.subscription, 'analysis-ready:1', payload))

        send_push.assert_called_once_with(self.subscription, payload)
        self.assertEqual(PushDelivery.objects.filter(subscription=self.subscription).count(), 1)


class PushEventTaskTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='event-user',
            email='event@example.com',
            password='Strong-test-pass-123',
            push_enabled=True,
        )
        league = League.objects.create(name='Premier League', country='England')
        home_team = Team.objects.create(name='Home')
        away_team = Team.objects.create(name='Away')
        self.match = Match.objects.create(
            league=league,
            home_team=home_team,
            away_team=away_team,
            match_date=timezone.now() + timedelta(hours=1),
            status='scheduled',
        )
        self.subscription = PushSubscription.objects.create(
            user=self.user,
            endpoint='https://fcm.googleapis.com/event-device',
            p256dh_key='public-key',
            auth_key='auth-key',
        )

    def create_analysis(self):
        return Analysis.objects.create(
            user=self.user,
            match=self.match,
            prediction='home',
            confidence=3,
            home_probability=45,
            draw_probability=30,
            away_probability=25,
            analysis_data={},
            reasoning='Teste',
            key_factors=[],
        )

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='public', WEBPUSH_VAPID_PRIVATE_KEY='private')
    @patch('apps.notifications.tasks.deliver_push_once', return_value=True)
    def test_analysis_ready_task_sends_neutral_match_notification(self, deliver):
        analysis = self.create_analysis()

        result = send_analysis_ready_push.run(analysis.pk)

        self.assertEqual(result, {'sent': 1})
        self.assertEqual(deliver.call_args.args[1], f'analysis-ready:{analysis.pk}')
        self.assertEqual(deliver.call_args.args[2]['title'], 'Análise pronta')

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='public', WEBPUSH_VAPID_PRIVATE_KEY='private')
    @patch('apps.notifications.tasks.deliver_push_once', return_value=True)
    def test_match_reminder_targets_analyzed_upcoming_match(self, deliver):
        self.create_analysis()
        self.match.match_date = timezone.now() + timedelta(minutes=60)
        self.match.save(update_fields=['match_date'])

        result = send_analyzed_match_reminders.run()

        self.assertEqual(result, {'sent': 1})
        self.assertEqual(deliver.call_args.args[1], f'match-reminder:{self.match.pk}:60m')

    @patch('apps.notifications.tasks.send_analysis_ready_push.delay')
    def test_analysis_creation_enqueues_ready_notification_after_commit(self, enqueue):
        with self.captureOnCommitCallbacks(execute=True):
            analysis = self.create_analysis()

        enqueue.assert_called_once_with(analysis.pk)

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='public', WEBPUSH_VAPID_PRIVATE_KEY='private')
    @patch('apps.notifications.tasks.deliver_push_once', return_value=True)
    @patch('apps.notifications.tasks.FootballAPIService')
    def test_live_game_events_notify_only_analyzed_match_subscribers(self, api_class, deliver):
        self.create_analysis()
        self.match.api_football_id = 54321
        self.match.status = 'live'
        self.match.match_date = timezone.now()
        self.match.save(update_fields=['api_football_id', 'status', 'match_date'])
        api = api_class.return_value
        api.get_live_fixtures.return_value = {
            'success': True,
            'fixtures': [{'fixture': {'id': 54321}}],
        }
        api.get_fixture_events.return_value = {
            'success': True,
            'events': [{
                'time': {'elapsed': 31, 'extra': None},
                'team': {'id': 1, 'name': 'Home'},
                'player': {'id': 8, 'name': 'Player'},
                'assist': {'id': None, 'name': None},
                'type': 'Goal',
                'detail': 'Normal Goal',
            }],
        }

        result = poll_analyzed_match_events.run()

        self.assertEqual(result, {'sent': 1, 'matches': 1, 'failures': 0})
        api.get_fixture_events.assert_called_once_with(54321)
        self.assertEqual(deliver.call_args.args[2]['title'], 'Golo na partida analisada')

    def test_event_classifier_includes_selected_match_event_types(self):
        from apps.notifications.tasks import _classify_match_event

        self.assertEqual(_classify_match_event({'type': 'Goal', 'detail': 'Normal Goal'}), 'goal')
        self.assertEqual(_classify_match_event({'type': 'Goal', 'detail': 'Missed Penalty'}), 'penalty')
        self.assertEqual(_classify_match_event({'type': 'Card', 'detail': 'Red Card'}), 'red_card')
        self.assertEqual(_classify_match_event({'type': 'Card', 'detail': 'Yellow Card'}), 'yellow_card')
        self.assertEqual(_classify_match_event({'type': 'subst', 'detail': 'Substitution'}), 'substitution')
        self.assertEqual(_classify_match_event({'type': 'Var', 'detail': 'Goal cancelled'}), 'var')
        self.assertEqual(_classify_match_event({'type': 'Card', 'detail': 'Second Yellow Card'}), 'red_card')
        from apps.notifications.tasks import _match_event_payload
        payload = _match_event_payload(
            self.match,
            {
                'type': 'subst',
                'detail': 'Substitution',
                'comments': 'Injury',
                'team': {'name': 'Home'},
                'player': {'name': 'Player'},
                'assist': {'name': 'Replacement'},
            },
        )
        self.assertEqual(payload['title'], 'Substituição por lesão')

    @override_settings(WEBPUSH_VAPID_PUBLIC_KEY='public', WEBPUSH_VAPID_PRIVATE_KEY='private')
    @patch('apps.notifications.tasks.deliver_push_once', return_value=True)
    def test_affiliate_notification_is_sent_to_enabled_subscribers(self, deliver):
        result = send_affiliate_push.run(
            self.user.id,
            'commission_created',
            'commission-1',
            'Nova comissão gerada',
            'Uma venda foi confirmada.',
        )

        self.assertEqual(result, {'sent': 1})
        self.assertEqual(deliver.call_args.args[1], 'affiliate:commission_created:commission-1')
        self.assertEqual(deliver.call_args.args[2]['url'], '/affiliate')


class VapidKeyCommandTests(TestCase):
    def test_generated_keys_form_a_valid_vapid_pair(self):
        output = StringIO()
        call_command('generate_vapid_keys', stdout=output)
        values = dict(
            line.split('=', 1)
            for line in output.getvalue().splitlines()
            if '=' in line
        )

        public_key = values['WEBPUSH_VAPID_PUBLIC_KEY']
        vapid = Vapid.from_string(values['WEBPUSH_VAPID_PRIVATE_KEY'])
        encoded_public = base64.urlsafe_b64encode(
            vapid.public_key.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint,
            )
        ).rstrip(b'=').decode('ascii')

        self.assertEqual(encoded_public, public_key)
