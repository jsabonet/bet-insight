from unittest.mock import patch

from django.test import SimpleTestCase

from apps.analysis.services.api_football_service import APIFootballService
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.parallel_enricher import ParallelMatchEnricher


class RestContextTests(SimpleTestCase):
    match_date = '2026-10-31T21:00:00+00:00'

    def test_api_queries_team_fixtures_until_requested_date(self):
        service = APIFootballService()
        with patch.object(service, '_make_request', return_value=[]) as make_request:
            service.fetch_team_fixtures(
                team_id=9,
                league_id=253,
                season=2026,
                before='2026-10-31',
            )

        make_request.assert_called_once_with(
            'fixtures',
            {
                'team': 9,
                'status': 'FT',
                'to': '2026-10-31',
                'league': 253,
                'season': 2026,
            },
            cache_type='fixtures',
        )

    def test_sequential_rest_uses_latest_fixture_strictly_before_match(self):
        enricher = MatchDataEnricher()
        home_fixtures = [
            {'date': self.match_date},
            {'date': '2026-10-26T21:00:00+00:00'},
            {'date': '2026-10-20T21:00:00+00:00'},
        ]
        away_fixtures = [
            {'date': self.match_date},
            {'date': '2026-10-29T21:00:00+00:00'},
        ]

        with (
            patch('apps.analysis.services.match_enricher.time.sleep'),
            patch.object(
                enricher.api_service,
                'fetch_team_fixtures',
                side_effect=[home_fixtures, away_fixtures],
            ) as fetch_fixtures,
        ):
            result = enricher._calculate_rest_context(
                1, 2, 253, 2026, self.match_date
            )

        self.assertEqual(result['home_days_rest'], 5)
        self.assertEqual(result['away_days_rest'], 2)
        self.assertEqual(result['advantage'], 'home')
        self.assertEqual(fetch_fixtures.call_args_list[0].kwargs['before'], '2026-10-31')
        self.assertEqual(fetch_fixtures.call_args_list[1].kwargs['before'], '2026-10-31')

    def test_parallel_rest_ignores_current_and_future_fixtures(self):
        enricher = ParallelMatchEnricher.__new__(ParallelMatchEnricher)

        result = enricher._calculate_rest_parallel(
            [
                {'date': self.match_date},
                {'date': '2026-10-26T21:00:00+00:00'},
            ],
            [
                {'fixture': {'date': '2026-11-02T21:00:00+00:00'}},
                {'fixture': {'date': '2026-10-29T21:00:00+00:00'}},
            ],
            self.match_date,
        )

        self.assertEqual(result['home_days_rest'], 5)
        self.assertEqual(result['away_days_rest'], 2)
        self.assertEqual(result['advantage'], 'home')

    def test_missing_rest_data_uses_neutral_features_without_claiming_availability(self):
        engineer = FeatureEngineer()
        rest_context = {'home_days_rest': None, 'away_days_rest': None}

        features = engineer._calculate_context_features(rest_context)

        self.assertEqual(features['home_rest_days'], 7)
        self.assertEqual(features['away_rest_days'], 7)
        self.assertFalse(engineer._has_rest_context(rest_context))
