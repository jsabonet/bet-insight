from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase

from apps.analysis.models import DailyBetCandidate
from apps.analysis.services.daily_bet_evidence import (
    MIN_EVIDENCE_SAMPLES,
    market_evidence,
    probability_bucket,
    record_shadow_candidates,
    settle_shadow_candidates,
    shadow_performance_report,
    wilson_lower_bound,
)


class DailyBetEvidenceTests(TestCase):
    def setUp(self):
        self.prediction_date = date(2026, 6, 1)

    def _create_candidate(self, index, outcome='won', eligible=True, **overrides):
        values = {
            'date': self.prediction_date - timedelta(days=1),
            'fixture_id': 100000 + index,
            'league_id': 39,
            'league_name': 'Premier League',
            'match_name': f'Team A {index} vs Team B {index}',
            'market': 'under_4.5',
            'pick': 'Under 4.5',
            'probability': 0.82,
            'probability_bucket': '0.80-0.85',
            'odd': 2.0,
            'ev_pct': 64.0,
            'selection_eligible': eligible,
            'outcome': outcome,
        }
        values.update(overrides)
        return DailyBetCandidate.objects.create(**values)

    def test_probability_buckets_cover_valid_values_without_rounding_up(self):
        self.assertEqual(probability_bucket(0.65), '0.65-0.70')
        self.assertEqual(probability_bucket(0.6999), '0.65-0.70')
        self.assertEqual(probability_bucket(0.70), '0.70-0.75')
        self.assertEqual(probability_bucket(1.0), '0.95-1.00')
        self.assertIsNone(probability_bucket(0))

    def test_requires_minimum_sample_and_positive_roi_and_wilson_lower_bound(self):
        for index in range(MIN_EVIDENCE_SAMPLES - 1):
            self._create_candidate(index)

        evidence = market_evidence('under_4.5', 0.82, self.prediction_date)

        self.assertEqual(evidence['sample_size'], MIN_EVIDENCE_SAMPLES - 1)
        self.assertFalse(evidence['sample_sufficient'])
        self.assertFalse(evidence['evidence_passed'])

        self._create_candidate(MIN_EVIDENCE_SAMPLES - 1)
        evidence = market_evidence('under_4.5', 0.82, self.prediction_date)

        self.assertEqual(evidence['sample_size'], MIN_EVIDENCE_SAMPLES)
        self.assertGreater(evidence['win_rate_lower_95'], evidence['break_even_probability'])
        self.assertGreater(evidence['roi_pct'], 0)
        self.assertTrue(evidence['evidence_passed'])

    def test_evidence_uses_only_prior_eligible_settled_predictions_in_same_bucket(self):
        self._create_candidate(1, eligible=False)
        self._create_candidate(
            2,
            date=self.prediction_date,
            fixture_id=100002,
        )
        self._create_candidate(
            3,
            probability=0.76,
            probability_bucket='0.75-0.80',
            fixture_id=100003,
        )

        evidence = market_evidence('under_4.5', 0.82, self.prediction_date)

        self.assertEqual(evidence['sample_size'], 0)
        self.assertFalse(evidence['evidence_passed'])

    def test_wilson_lower_bound_returns_none_without_observations(self):
        self.assertIsNone(wilson_lower_bound(0, 0))
        self.assertLess(wilson_lower_bound(50, 100), 0.5)

    def test_records_pre_match_candidates_with_input_snapshot_and_rejection_reason(self):
        analyses = [{
            'fixture_id': 7001,
            'match_date': '2026-06-01T20:00:00+00:00',
            'home_team': 'Home',
            'away_team': 'Away',
            'league_id': 39,
            'league_name': 'Premier League',
            'quality_score': 90,
            'data_completeness_pct': 80,
            'multiple_result': {
                'analysis_data': {
                    'top_bets': [{
                        'market': 'under_4.5',
                        'pick': 'Under 4.5',
                        'probability': 0.82,
                        'market_odd': 2.0,
                        'ev_pct': 64.0,
                        'ranking_score': 0.8,
                    }],
                    'consensus': {'draw': 0.20},
                    'confidence': {'stars': 5},
                    'risk': 'low',
                    'features_summary': {
                        'form': {
                            'home_weighted_form': 2.0,
                            'away_weighted_form': 2.0,
                        },
                        'complete': {
                            '_metadata': {
                                'data_availability': {
                                    'market': True,
                                    'rest': False,
                                },
                            },
                        },
                    },
                    'model_predictions': {'poisson': {'expected_goals': {'home': 1.4, 'away': 1.2}}},
                },
            },
        }]

        created = record_shadow_candidates(analyses)
        candidate = DailyBetCandidate.objects.get(fixture_id=7001)

        self.assertEqual(created, 1)
        self.assertTrue(candidate.selection_eligible)
        self.assertEqual(candidate.probability_bucket, '0.80-0.85')
        self.assertEqual(candidate.data_quality_score, 90)
        self.assertEqual(candidate.data_completeness_pct, 50)
        self.assertIn('model_predictions', candidate.source_snapshot['analysis'])
        self.assertEqual(
            record_shadow_candidates(analyses),
            0,
        )

    def test_missing_shadow_table_does_not_break_candidate_recording_or_evidence(self):
        with patch(
            'apps.analysis.services.daily_bet_evidence.shadow_table_available',
            return_value=False,
        ):
            created = record_shadow_candidates([{}])
            evidence = market_evidence(
                'under_4.5',
                0.82,
                self.prediction_date,
            )

        self.assertEqual(created, 0)
        self.assertEqual(evidence['sample_size'], 0)
        self.assertFalse(evidence['evidence_passed'])
        self.assertIn('migration pendente', evidence['reason'])

    def test_settles_shadow_prediction_against_official_market_result(self):
        candidate = self._create_candidate(
            20,
            outcome='pending',
            date=date.today(),
            fixture_id=100020,
        )
        results = {
            str(candidate.fixture_id): {
                'status': 'finished',
                'home_score': 4,
                'away_score': 1,
            },
        }

        with patch(
            'apps.analysis.services.daily_bet_evidence.build_results_map',
            return_value=results,
        ):
            settled = settle_shadow_candidates()

        candidate.refresh_from_db()
        self.assertEqual(settled, 1)
        self.assertEqual(candidate.outcome, 'lost')
        self.assertEqual(candidate.actual_result, 'home')
        self.assertEqual(candidate.home_score, 4)
        self.assertIsNotNone(candidate.settled_at)

    def test_report_compares_model_to_market_by_league_and_market(self):
        self._create_candidate(30, outcome='won')

        report = shadow_performance_report()

        self.assertEqual(len(report), 2)
        league_report = next(row for row in report if row['league_id'] is not None)
        aggregate_report = next(row for row in report if row['league_id'] is None)
        self.assertEqual(league_report['market'], 'under_4.5')
        self.assertEqual(league_report['league'], 'Premier League')
        self.assertEqual(league_report['sample_size'], 1)
        self.assertEqual(league_report['mean_model_probability'], 0.82)
        self.assertEqual(league_report['mean_market_implied_probability'], 0.5)
        self.assertEqual(league_report['roi_pct'], 100.0)
        self.assertFalse(league_report['evidence_sufficient'])
        self.assertEqual(aggregate_report['league'], 'Todas as ligas')
