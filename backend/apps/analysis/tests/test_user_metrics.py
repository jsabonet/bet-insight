from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from apps.analysis.models import Analysis
from apps.analysis.services.match_result_sync import sync_results_for_date
from apps.matches.models import League, Match, Team
from apps.users.models import User


class UserProfileMetricsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='metrics-user',
            email='metrics-user@example.com',
            password='test-password',
        )
        self.league = League.objects.create(name='Metrics League', country='Test')
        self.home = Team.objects.create(name='Metrics Home')
        self.away = Team.objects.create(name='Metrics Away')

    def create_match(self, api_id=None, status='scheduled', home_score=None, away_score=None):
        return Match.objects.create(
            league=self.league,
            home_team=self.home,
            away_team=self.away,
            match_date=timezone.now(),
            api_football_id=api_id,
            status=status,
            home_score=home_score,
            away_score=away_score,
        )

    def create_analysis(self, match, is_correct=None, prediction='home'):
        return Analysis.objects.create(
            user=self.user,
            match=match,
            prediction=prediction,
            confidence=3,
            home_probability=45,
            draw_probability=30,
            away_probability=25,
            home_xg=1.5,
            away_xg=1.2,
            analysis_data={},
            reasoning='Test analysis',
            key_factors=[],
            is_correct=is_correct,
        )

    def test_stats_reflect_saved_analyses_and_only_resolved_results(self):
        self.create_analysis(self.create_match(), is_correct=True)
        self.create_analysis(
            self.create_match(),
            is_correct=False,
            prediction='away',
        )
        self.create_analysis(self.create_match(), is_correct=None)
        self.user.total_analyses = 99
        self.user.successful_predictions = 20
        self.user.daily_analysis_count = 2
        self.user.last_analysis_date = timezone.localdate()
        self.user.save(update_fields=[
            'total_analyses',
            'successful_predictions',
            'daily_analysis_count',
            'last_analysis_date',
        ])

        client = APIClient()
        client.force_authenticate(self.user)
        response = client.get('/api/users/stats/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_analyses'], 3)
        self.assertEqual(response.data['resolved_analyses'], 2)
        self.assertEqual(response.data['successful_predictions'], 1)
        self.assertEqual(response.data['success_rate'], 50)
        self.assertEqual(response.data['analyses_count_today'], 2)
        self.assertEqual(self.user.get_success_rate(), 50)

    def test_analysis_counter_is_synchronized_with_persisted_history(self):
        self.create_analysis(self.create_match())
        self.user.total_analyses = 99
        self.user.save(update_fields=['total_analyses'])

        self.user.increment_analysis_count()

        self.user.refresh_from_db()
        self.assertEqual(self.user.total_analyses, self.user.analyses.count())
        self.assertEqual(self.user.total_analyses, 1)

    def test_result_validation_updates_success_count_idempotently(self):
        match = self.create_match(status='finished', home_score=2, away_score=1)
        analysis = self.create_analysis(match, prediction='home')

        analysis.validate_result()
        analysis.validate_result()

        self.user.refresh_from_db()
        analysis.refresh_from_db()
        self.assertTrue(analysis.is_correct)
        self.assertEqual(self.user.successful_predictions, 1)

        match.home_score = 0
        match.away_score = 1
        match.save(update_fields=['home_score', 'away_score'])
        analysis.match.refresh_from_db()
        analysis.validate_result()

        self.user.refresh_from_db()
        analysis.refresh_from_db()
        self.assertFalse(analysis.is_correct)
        self.assertEqual(self.user.successful_predictions, 0)

    @patch('apps.analysis.services.match_result_sync.FootballAPIService')
    def test_result_sync_validates_analysis_and_persists_success_count(self, api_service):
        match = self.create_match(api_id=1234)
        analysis = self.create_analysis(match)
        api_service.return_value.get_fixtures_by_date.return_value = {
            'success': True,
            'fixtures': [{
                'fixture': {
                    'id': 1234,
                    'date': timezone.now().isoformat(),
                    'status': {'short': 'FT'},
                },
                'goals': {'home': 2, 'away': 1},
                'teams': {
                    'home': {'name': self.home.name},
                    'away': {'name': self.away.name},
                },
                'league': {'name': self.league.name},
            }],
        }

        sync_results_for_date(timezone.localdate())

        match.refresh_from_db()
        analysis.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(match.get_result(), 'home')
        self.assertTrue(analysis.is_correct)
        self.assertEqual(self.user.successful_predictions, 1)
