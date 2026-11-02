from django.test import SimpleTestCase
from unittest.mock import Mock, patch
from scipy.stats import poisson

from apps.analysis.config.market_standards import get_market_category, normalize_market_name
from apps.analysis.services.api_football_service import APIFootballService
from apps.analysis.services.decision_engine import DecisionEngine
from apps.analysis.services.goal_line_safety import conservative_total_market
from apps.analysis.services.market_selector import MarketSelector
from apps.analysis.services.odds_calculator import OddsCalculator
from apps.analysis.services.statistical_models import PoissonBivariateModel


class ConservativeGoalLineTests(SimpleTestCase):
    def test_asian_goal_lines_are_not_supported_or_normalized(self):
        for line in ('1.75', '2.25', '2.75', '3.25'):
            for direction in ('over', 'under'):
                self.assertIsNone(normalize_market_name(f'{direction}_{line}'))
                self.assertIsNone(normalize_market_name(f'{direction}_{line.replace(".", "_")}'))
                self.assertIsNone(get_market_category(f'{direction}_{line}'))

    def test_odds_calculator_does_not_create_asian_goal_lines(self):
        odds = OddsCalculator().calculate_all_derived_odds({
            'home_win': 2.1,
            'draw': 3.2,
            'away_win': 3.4,
            'over_1.5': 1.5,
            'under_1.5': 2.5,
            'over_2.5': 2.0,
            'under_2.5': 1.8,
            'over_3.5': 3.0,
            'under_3.5': 1.3,
        })

        self.assertFalse(any(normalize_market_name(market) is None for market in odds))
        self.assertFalse(any(line in market for market in odds for line in ('1.75', '2.25', '2.75', '3.25')))

    def test_poisson_output_contains_only_supported_goal_total_lines(self):
        prediction = PoissonBivariateModel().predict(home_strength=1.4, away_strength=1.1)
        probabilities = prediction['probabilities']

        self.assertTrue({'over_0.5', 'under_0.5', 'over_2.5', 'under_2.5'}.issubset(probabilities))
        self.assertEqual(prediction['total_scenarios'], 49)
        self.assertFalse(any(
            line in market for market in probabilities for line in ('1.75', '2.25', '2.75', '3.25')
        ))

    def test_under_45_uses_full_poisson_tail(self):
        calibrator = Mock()
        calibrator.is_available.return_value = False

        with patch(
            'apps.analysis.services.statistical_models.get_xg_calibrator',
            return_value=calibrator,
        ):
            prediction = PoissonBivariateModel().predict(
                home_strength=3.2,
                away_strength=3.2,
            )

        expected_goals = prediction['expected_goals']
        total_lambda = expected_goals['home'] + expected_goals['away']
        probabilities = prediction['probabilities']
        self.assertAlmostEqual(
            probabilities['under_4.5'],
            poisson.cdf(4, total_lambda),
            places=10,
        )
        self.assertAlmostEqual(
            probabilities['under_4.5'] + probabilities['over_4.5'],
            1.0,
            places=10,
        )

    def test_most_likely_score_changes_with_expected_goals(self):
        calibrator = Mock()
        calibrator.is_available.return_value = False
        expectations = ((0.35, 1.9), (1.2, 1.1), (2.4, 0.8), (2.7, 2.1))

        with patch(
            'apps.analysis.services.statistical_models.get_xg_calibrator',
            return_value=calibrator,
        ):
            predictions = [
                PoissonBivariateModel().predict(home, away)
                for home, away in expectations
            ]

        self.assertEqual(
            [prediction['most_likely_score'] for prediction in predictions],
            ['0-1', '1-1', '2-0', '2-2'],
        )

    def test_odds_api_parser_ignores_asian_goal_lines_but_keeps_standard_lines(self):
        service = APIFootballService()
        response = [{
            'bookmakers': [{
                'name': 'Bookmaker',
                'bets': [{
                    'name': 'Goals Over/Under',
                    'values': [
                        {'value': 'Over 2.25', 'odd': '1.90'},
                        {'value': 'Under 2.75', 'odd': '1.95'},
                        {'value': 'Over 2.5', 'odd': '2.00'},
                        {'value': 'Under 2.5', 'odd': '1.80'},
                    ],
                }],
            }],
        }]

        with patch.object(service, '_make_request', return_value=response):
            odds = service.fetch_odds(123)

        self.assertEqual(odds['over_2.5'], 2.0)
        self.assertEqual(odds['under_2.5'], 1.8)
        self.assertFalse(any('2.25' in market or '2.75' in market for market in odds))

    @patch('apps.analysis.services.api_football_service.requests.get')
    @patch('apps.analysis.services.api_football_service.cache.delete')
    @patch('apps.analysis.services.api_football_service.cache.get', side_effect=[[], None])
    def test_fixture_details_retries_after_empty_cached_response(
        self,
        cache_get,
        cache_delete,
        requests_get,
    ):
        service = APIFootballService()
        fixture = {
            'fixture': {
                'id': 123,
                'date': '2026-11-01T18:00:00+00:00',
                'venue': {'name': 'Stadium'},
                'referee': None,
                'status': {'short': 'NS'},
            },
            'teams': {
                'home': {'id': 1, 'name': 'Home', 'logo': ''},
                'away': {'id': 2, 'name': 'Away', 'logo': ''},
            },
            'league': {
                'id': 39,
                'name': 'League',
                'season': 2026,
                'round': 'Regular Season - 1',
            },
            'goals': {'home': None, 'away': None},
            'score': {},
        }
        response = Mock()
        response.json.return_value = {'response': [fixture]}
        requests_get.return_value = response

        details = service.fetch_fixture_details(123)

        self.assertEqual(details['fixture_id'], 123)
        self.assertEqual(details['home_team']['id'], 1)
        cache_delete.assert_called_once_with(
            service._get_cache_key('fixtures', {'id': 123})
        )
        requests_get.assert_called_once()

    def test_only_over_lines_move_down(self):
        self.assertEqual(conservative_total_market('over_1_5'), 'over_0.5')
        self.assertEqual(conservative_total_market('over_2.5'), 'over_1.5')
        self.assertEqual(conservative_total_market('under_1.5'), 'under_1.5')
        self.assertEqual(conservative_total_market('under_3.5'), 'under_3.5')

    def test_boundaries_and_non_total_markets_are_unchanged_or_ignored(self):
        self.assertEqual(conservative_total_market('over_0.5'), 'over_0.5')
        self.assertEqual(conservative_total_market('under_4.5'), 'under_4.5')
        self.assertIsNone(conservative_total_market('home_over_1.5'))
        self.assertIsNone(conservative_total_market('btts_yes'))

    def test_market_selector_preserves_under_line_and_uses_its_probability_and_odd(self):
        selector = MarketSelector()
        probabilities = {
            'over_0.5': 0.90,
            'over_1.5': 0.70,
            'under_0.5': 0.10,
            'under_1.5': 0.60,
            'under_2.5': 0.70,
            'under_3.5': 0.50,
            'under_4.5': 0.40,
        }
        odds = {
            'over_0.5': 1.40,
            'over_1.5': 1.60,
            'under_1.5': 1.50,
            'under_2.5': 1.50,
            'under_3.5': 1.50,
            'under_4.5': 1.50,
        }

        selections = selector.select_top_markets(
            context_analysis={'patterns': [], 'top_markets': []},
            model_predictions={'consensus': {}, 'poisson': {'probabilities': probabilities}},
            market_odds=odds,
            strategy='multiple',
        )

        over = next(selection for selection in selections if selection['market'] == 'over_0.5')
        under = next(selection for selection in selections if selection['market'] == 'under_2.5')
        self.assertEqual(over['original_market'], 'over_1.5')
        self.assertEqual(over['probability'], 0.90)
        self.assertEqual(over['market_odd'], 1.40)
        self.assertIsNone(under['original_market'])
        self.assertEqual(under['probability'], 0.70)
        self.assertEqual(under['market_odd'], 1.50)

    def test_market_selector_does_not_reuse_original_line_odd(self):
        selector = MarketSelector()
        selections = selector.select_top_markets(
            context_analysis={'patterns': [], 'top_markets': []},
            model_predictions={
                'consensus': {},
                'poisson': {'probabilities': {'over_1.5': 0.90, 'over_0.5': 0.95}},
            },
            market_odds={'over_1.5': 1.50},
            strategy='multiple',
        )

        self.assertFalse(any(selection['market'] == 'over_0.5' for selection in selections))

    def test_market_selector_rejects_asian_goal_lines(self):
        selections = MarketSelector().select_top_markets(
            context_analysis={'patterns': [], 'top_markets': []},
            model_predictions={
                'consensus': {},
                'poisson': {'probabilities': {'over_2.25': 0.95, 'under_2.75': 0.95}},
            },
            market_odds={'over_2.25': 1.9, 'under_2.75': 1.9},
            strategy='multiple',
        )

        self.assertEqual(selections, [])

    def test_value_bet_engine_rejects_asian_goal_lines(self):
        value_bets = DecisionEngine()._find_value_bets(
            {'poisson': {'probabilities': {'over_2.25': 0.95, 'under_2.75': 0.95}}, 'consensus': {}},
            {'over_2.25': 2.0, 'under_2.75': 2.0},
        )

        self.assertFalse(any('2.25' in bet['market'] or '2.75' in bet['market'] for bet in value_bets))

    def test_value_bet_uses_adjusted_market_probability_and_odds(self):
        engine = DecisionEngine()
        probabilities = {
            'over_0.5': 0.90,
            'over_1.5': 0.70,
            'over_2.5': 0.50,
            'over_3.5': 0.30,
            'over_4.5': 0.15,
            'under_0.5': 0.10,
            'under_1.5': 0.30,
            'under_2.5': 0.50,
            'under_3.5': 0.70,
            'under_4.5': 0.85,
        }
        predictions = {'poisson': {'probabilities': probabilities}, 'consensus': {}}
        odds = {
            'over_0.5': 1.30,
            'over_1.5': 1.70,
            'over_2.5': 2.20,
            'over_3.5': 3.00,
            'over_4.5': 5.00,
            'under_1.5': 4.00,
            'under_2.5': 2.20,
            'under_3.5': 1.70,
            'under_4.5': 1.30,
        }

        value_bets = engine._find_value_bets(predictions, odds)
        by_market = {bet['market']: bet for bet in value_bets}

        self.assertIn('over_0.5', by_market)
        self.assertEqual(by_market['over_0.5']['model_probability'], 0.90)
        self.assertEqual(by_market['over_0.5']['market_odd'], 1.30)
        self.assertEqual(by_market['over_0.5']['original_market'], 'over_1.5')
        self.assertIn('under_1.5', by_market)
        self.assertEqual(by_market['under_1.5']['model_probability'], 0.30)
        self.assertIsNone(by_market['under_1.5']['original_market'])

        simulated_value_bets = engine._find_value_bets(
            predictions,
            {'over_0_5': {'value': 1.30, 'is_simulated': True}},
        )
        self.assertFalse(any(bet['market'] == 'over_0.5' for bet in simulated_value_bets))
