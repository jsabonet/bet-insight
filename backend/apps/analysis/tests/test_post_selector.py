import unittest

from apps.analysis.services.post_decision_selector import PostDecisionSelector


class TestPostDecisionSelector(unittest.TestCase):
    def test_select_best_for_ticket_prefers_high_prob_and_stable_odds(self):
        selector = PostDecisionSelector()
        top_bets = [
            {
                'market': 'home_win',
                'pick': 'Casa',
                'probability': 0.52,
                'market_odd': 1.90,
                'ev_pct': -3.0,
                'score': 0.45,
            },
            {
                'market': 'double_chance_x2',
                'pick': 'Empate ou Fora (X2)',
                'probability': 0.68,
                'market_odd': 1.55,
                'ev_pct': -4.0,
                'score': 0.50,
            },
            {
                'market': 'over_2_5',
                'pick': 'Over',
                'probability': 0.49,
                'market_odd': 2.00,
                'ev_pct': 1.0,
                'score': 0.40,
            }
        ]

        consensus = {'home_win': 0.30, 'draw': 0.20, 'away_win': 0.50}

        best = selector.select_best(top_bets, strategy='multiple', consensus=consensus)
        self.assertIsNotNone(best)
        # Deve preferir X2 com prob alta e odd na faixa ideal
        self.assertEqual(best['market'], 'double_chance_x2')


if __name__ == '__main__':
    unittest.main()
