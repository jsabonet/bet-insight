from django.test import SimpleTestCase

from apps.analysis.services.decision_engine import DecisionEngine
from apps.analysis.services.goal_line_safety import conservative_total_market
from apps.analysis.services.market_selector import MarketSelector


class ConservativeGoalLineTests(SimpleTestCase):
    def test_over_moves_down_and_under_moves_up_one_line(self):
        self.assertEqual(conservative_total_market('over_1_5'), 'over_0.5')
        self.assertEqual(conservative_total_market('over_2.5'), 'over_1.5')
        self.assertEqual(conservative_total_market('under_1.5'), 'under_2.5')
        self.assertEqual(conservative_total_market('under_3.5'), 'under_4.5')

    def test_boundaries_and_non_total_markets_are_unchanged_or_ignored(self):
        self.assertEqual(conservative_total_market('over_0.5'), 'over_0.5')
        self.assertEqual(conservative_total_market('under_4.5'), 'under_4.5')
        self.assertIsNone(conservative_total_market('home_over_1.5'))
        self.assertIsNone(conservative_total_market('btts_yes'))

    def test_market_selector_uses_adjusted_line_probability_and_actual_odd(self):
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
        self.assertEqual(under['original_market'], 'under_1.5')
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
        self.assertEqual(by_market['under_1.5']['original_market'], 'under_0.5')

        simulated_value_bets = engine._find_value_bets(
            predictions,
            {'over_0_5': {'value': 1.30, 'is_simulated': True}},
        )
        self.assertFalse(any(bet['market'] == 'over_0.5' for bet in simulated_value_bets))
