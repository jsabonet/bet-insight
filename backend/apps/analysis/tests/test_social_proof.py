"""Testes do fluxo de prova social (admin) e da validação estrita de bilhetes."""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.analysis.models import DailyBet, SocialProofTicket
from apps.users.models import User

BASE_URL = '/api/daily-bets/admin/social-proof/'


def _selection(fixture_id, kickoff, market='home_win', odd=1.5, probability=0.62):
    return {
        'api_fixture_id': fixture_id,
        'match': f'Equipa A{fixture_id} vs. Equipa B{fixture_id}',
        'league': 'Liga Teste',
        'date': kickoff.isoformat(),
        'market': market,
        'pick': 'Casa',
        'probability': probability,
        'odd': odd,
        'result': 'won',
        'final_score': '2-0',
    }


class SocialProofTestBase(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_sp', email='admin_sp@example.com', password='x', is_staff=True
        )
        self.regular = User.objects.create_user(
            username='user_sp', email='user_sp@example.com', password='x'
        )
        self.client = APIClient()

    def _auth(self, user):
        self.client.force_authenticate(user=user)

    def _won_bet(self, target_date, fixture_ids=(101, 102), kickoff=None, bet_type='multiple'):
        kickoff = kickoff or timezone.now() - timedelta(days=1)
        selections = [_selection(fid, kickoff) for fid in fixture_ids]
        total_odd = Decimal('1.00')
        for selection in selections:
            total_odd *= Decimal(str(selection['odd']))

        bet = DailyBet.objects.create(
            date=target_date,
            bet_type=bet_type,
            selections=selections,
            total_odd=total_odd,
            fair_odd=total_odd,
            combined_probability=0.4,
            expected_value=5.0,
            suggested_stake=10.0,
            status='won',
            is_validated=True,
        )
        # created_at é auto_now_add: recua para garantir "gerado antes do kickoff".
        DailyBet.objects.filter(pk=bet.pk).update(
            created_at=kickoff - timedelta(hours=6)
        )
        bet.refresh_from_db()
        return bet


class SocialProofPermissionTests(SocialProofTestBase):
    def test_anonymous_is_rejected(self):
        response = self.client.get(f'{BASE_URL}candidates/')
        self.assertIn(response.status_code, (401, 403))

    def test_non_admin_is_forbidden(self):
        self._auth(self.regular)
        response = self.client.get(f'{BASE_URL}candidates/')
        self.assertEqual(response.status_code, 403)

    def test_generate_requires_admin(self):
        self._auth(self.regular)
        response = self.client.post(f'{BASE_URL}generate/', {'kind': 'verified_ticket'}, format='json')
        self.assertEqual(response.status_code, 403)


class SocialProofCandidateTests(SocialProofTestBase):
    def setUp(self):
        super().setUp()
        self._auth(self.admin)
        self.today = timezone.localdate()
        self.yesterday = self.today - timedelta(days=1)

    def test_invalid_kind_is_rejected(self):
        response = self.client.get(f'{BASE_URL}candidates/', {'date': self.yesterday.isoformat(), 'kind': 'nope'})
        self.assertEqual(response.status_code, 400)

    def test_verified_candidates_include_won_bet_before_kickoff(self):
        self._won_bet(self.yesterday)
        response = self.client.get(
            f'{BASE_URL}candidates/',
            {'date': self.yesterday.isoformat(), 'kind': 'verified_ticket'},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['count'], 1)
        candidate = payload['candidates'][0]
        self.assertEqual(candidate['legs_count'], 2)
        self.assertFalse(candidate['watermark_required'])

    def test_bet_created_after_kickoff_is_excluded(self):
        bet = self._won_bet(self.yesterday)
        DailyBet.objects.filter(pk=bet.pk).update(created_at=timezone.now())
        response = self.client.get(
            f'{BASE_URL}candidates/',
            {'date': self.yesterday.isoformat(), 'kind': 'verified_ticket'},
        )
        self.assertEqual(response.json()['count'], 0)

    def test_simulation_requires_explicit_confirmation(self):
        self._won_bet(self.yesterday)
        response = self.client.post(
            f'{BASE_URL}generate/',
            {'date': self.yesterday.isoformat(), 'kind': 'simulation'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('simulação', response.json()['error'].lower())

    def test_simulation_ticket_is_watermarked(self):
        self._won_bet(self.yesterday, fixture_ids=(201, 202, 203))
        response = self.client.post(
            f'{BASE_URL}generate/',
            {
                'date': self.yesterday.isoformat(),
                'kind': 'simulation',
                'confirm_simulation': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201, response.content)
        body = response.json()
        self.assertTrue(body['watermark_required'])
        self.assertTrue(body['disclosure'])


class SocialProofSimulationFallbackTests(SocialProofTestBase):
    """Simulação deve funcionar sem bilhetes verificados (usando resultados)."""

    def setUp(self):
        super().setUp()
        self._auth(self.admin)
        self.yesterday = timezone.localdate() - timedelta(days=1)

    def _finished_fixture(self, fixture_id, home_score, away_score, kickoff=None):
        return {
            'fixture_id': fixture_id,
            'status': 'finished',
            'short_status': 'FT',
            'home_score': home_score,
            'away_score': away_score,
            'kickoff': (kickoff or (timezone.now() - timedelta(days=1))).isoformat(),
            'league': 'Liga Teste',
            'match': f'Equipa A{fixture_id} vs Equipa B{fixture_id}',
        }

    def _finished_results(self):
        fixtures = [
            self._finished_fixture(301, 2, 0),
            self._finished_fixture(302, 1, 3),
            self._finished_fixture(303, 1, 1),
        ]
        return {str(f['fixture_id']): f for f in fixtures}

    @patch('apps.analysis.services.social_proof_builder.sync_results_for_date')
    def test_simulation_generates_without_daily_bets(self, mock_sync):
        mock_sync.return_value = self._finished_results()

        response = self.client.post(
            f'{BASE_URL}generate/',
            {
                'date': self.yesterday.isoformat(),
                'kind': 'simulation',
                'confirm_simulation': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201, response.content)
        body = response.json()
        self.assertTrue(body['watermark_required'])
        self.assertTrue(body['disclosure'])
        self.assertGreaterEqual(body['legs_count'], 2)
        self.assertEqual(body['source_bet_ids'], [])
        for leg in body['legs']:
            self.assertIsNotNone(leg['fixture_id'])
            self.assertGreater(leg['odd'], 1.0)
            self.assertEqual(leg['result'], 'won')
            self.assertTrue(leg['final_score'])

    @patch('apps.analysis.services.social_proof_builder.sync_results_for_date')
    def test_simulation_fallback_still_requires_confirmation(self, mock_sync):
        mock_sync.return_value = self._finished_results()

        response = self.client.post(
            f'{BASE_URL}generate/',
            {'date': self.yesterday.isoformat(), 'kind': 'simulation'},
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('simulação', response.json()['error'].lower())

    @patch('apps.analysis.services.social_proof_builder.sync_results_for_date')
    def test_simulation_fallback_no_finished_matches_returns_400(self, mock_sync):
        mock_sync.return_value = {}

        response = self.client.post(
            f'{BASE_URL}generate/',
            {
                'date': self.yesterday.isoformat(),
                'kind': 'simulation',
                'confirm_simulation': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)


class SocialProofLifecycleTests(SocialProofTestBase):
    def setUp(self):
        super().setUp()
        self._auth(self.admin)
        self.yesterday = timezone.localdate() - timedelta(days=1)
        self._won_bet(self.yesterday)
        self.ticket = SocialProofTicket.objects.create(
            date=self.yesterday,
            kind='verified_ticket',
            ticket_code='SP-TEST-0001',
            reserve_code='BW7A',
            legs=[
                {
                    'fixture_id': 101,
                    'match': 'Equipa A vs. Equipa B',
                    'market': 'home_win',
                    'market_label': 'Casa Vence',
                    'odd': 1.5,
                    'probability': 0.62,
                }
            ],
            total_odd=Decimal('1.50'),
            combined_probability=0.62,
            snapshot_hash='hash-teste',
        )

    def test_generate_is_idempotent(self):
        url = f'{BASE_URL}generate/'
        body = {'date': self.yesterday.isoformat(), 'kind': 'verified_ticket'}

        first = self.client.post(url, body, format='json')
        self.assertEqual(first.status_code, 201)
        self.assertTrue(first.json()['created'])

        second = self.client.post(url, body, format='json')
        self.assertEqual(second.status_code, 200)
        self.assertFalse(second.json()['created'])
        self.assertEqual(
            SocialProofTicket.objects.filter(kind='verified_ticket').count(), 2
        )

    def test_export_before_approve_is_blocked(self):
        response = self.client.post(f'{BASE_URL}tickets/{self.ticket.id}/export/')
        self.assertEqual(response.status_code, 400)

    def test_approve_then_export(self):
        approve = self.client.post(f'{BASE_URL}tickets/{self.ticket.id}/approve/')
        self.assertEqual(approve.status_code, 200)
        self.assertEqual(approve.json()['status'], 'approved')

        export = self.client.post(f'{BASE_URL}tickets/{self.ticket.id}/export/')
        self.assertEqual(export.status_code, 200)
        body = export.json()
        self.assertEqual(body['status'], 'exported')
        self.assertEqual(body['export_count'], 1)

    def test_discarded_ticket_cannot_be_approved(self):
        discard = self.client.post(f'{BASE_URL}tickets/{self.ticket.id}/discard/')
        self.assertEqual(discard.status_code, 200)

        approve = self.client.post(f'{BASE_URL}tickets/{self.ticket.id}/approve/')
        self.assertEqual(approve.status_code, 400)

    def test_unknown_and_non_numeric_ids_return_404(self):
        self.assertEqual(self.client.get(f'{BASE_URL}tickets/999999/').status_code, 404)
        self.assertEqual(self.client.get(f'{BASE_URL}tickets/abc/').status_code, 404)

    def test_history_lists_tickets(self):
        response = self.client.get(f'{BASE_URL}tickets/', {'date': self.yesterday.isoformat()})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)


class DailyBetValidationStrictnessTests(SocialProofTestBase):
    def setUp(self):
        super().setUp()
        self.bet = DailyBet.objects.create(
            date=timezone.localdate(),
            bet_type='multiple',
            selections=[_selection(101, timezone.now() - timedelta(days=1))],
            total_odd=Decimal('1.50'),
            fair_odd=Decimal('1.50'),
            combined_probability=0.62,
            expected_value=5.0,
            suggested_stake=10.0,
        )

    def test_missing_result_keeps_bet_pending(self):
        self.assertFalse(self.bet.validate_result(results_map={}))
        self.bet.refresh_from_db()
        self.assertFalse(self.bet.is_validated)
        self.assertEqual(self.bet.status, 'pending')

    def test_unfinished_match_keeps_bet_pending(self):
        results = {'101': {'status': 'in_play', 'home_score': 1, 'away_score': 0}}
        self.assertFalse(self.bet.validate_result(results_map=results))
        self.bet.refresh_from_db()
        self.assertFalse(self.bet.is_validated)

    def test_finished_match_settles_bet(self):
        results = {'101': {'status': 'finished', 'home_score': 2, 'away_score': 0}}
        self.assertTrue(self.bet.validate_result(results_map=results))
        self.bet.refresh_from_db()
        self.assertTrue(self.bet.is_validated)
        self.assertEqual(self.bet.status, 'won')
        self.assertEqual(self.bet.selections[0]['result'], 'won')
        self.assertEqual(self.bet.selections[0]['final_score'], '2-0')

    def test_unsupported_market_keeps_bet_pending(self):
        self.bet.selections = [dict(self.bet.selections[0], market='corner_race_unknown')]
        self.bet.save(update_fields=['selections'])
        results = {'101': {'status': 'finished', 'home_score': 2, 'away_score': 0}}
        self.assertFalse(self.bet.validate_result(results_map=results))
        self.bet.refresh_from_db()
        self.assertFalse(self.bet.is_validated)
