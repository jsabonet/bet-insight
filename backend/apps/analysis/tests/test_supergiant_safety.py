from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.analysis.config.supergiants import (
    is_protective_supergiant_market,
    is_supergiant_away,
    is_supergiant_match,
)
from apps.analysis.models import DailyBet
from apps.analysis.services.daily_bet_generator import DailyBetGenerator
from apps.analysis.services.decision_engine import DecisionEngine
from apps.analysis.services.market_selector import MarketSelector


class SupergiantSafetyTests(SimpleTestCase):
    def setUp(self):
        self.match = SimpleNamespace(
            home_team=SimpleNamespace(id=42),
            away_team=SimpleNamespace(id=157),
        )

    def test_supergiant_ids_and_protective_markets(self):
        self.assertTrue(is_supergiant_match(self.match))
        self.assertTrue(is_supergiant_away(self.match))
        self.assertTrue(is_protective_supergiant_market('double_chance_x2'))
        self.assertTrue(is_protective_supergiant_market('under_4.5'))
        self.assertFalse(is_protective_supergiant_market('12'))
        self.assertFalse(is_protective_supergiant_market('home_over_0.5'))

    def test_market_selector_keeps_only_protective_markets_at_1_15_or_more(self):
        selector = MarketSelector()
        selections = selector.select_top_markets(
            context_analysis={'patterns': [], 'top_markets': []},
            model_predictions={
                'consensus': {
                    '1x': 0.85,
                    'x2': 0.80,
                    '12': 0.90,
                    'home_over_0.5': 0.90,
                },
                'poisson': {'probabilities': {}},
            },
            market_odds={
                '1x': 1.15,
                'x2': 1.14,
                '12': 1.20,
                'home_over_0.5': 1.40,
            },
            strategy='multiple',
            match=self.match,
        )

        markets = {selection['market'] for selection in selections}
        self.assertIn('1x', markets)
        self.assertNotIn('x2', markets)
        self.assertNotIn('12', markets)
        self.assertNotIn('home_over_0.5', markets)

    def test_decision_filter_vetoes_home_over_against_away_supergiant(self):
        engine = DecisionEngine()
        selections = [
            {'market': 'home_over_0.5'},
            {'market': 'over_2.5'},
            {'market': 'x2'},
            {'market': 'under_4.5'},
        ]

        filtered = engine._apply_tactical_safety_filters(
            selections, self.match, 'multiple'
        )

        self.assertEqual(
            {selection['market'] for selection in filtered},
            {'x2', 'under_4.5'},
        )

    def test_multiple_tickets_do_not_reuse_fixtures(self):
        generator = DailyBetGenerator.__new__(DailyBetGenerator)
        analyses = []

        for index in range(15):
            fixture_id = 10000 + index
            match = SimpleNamespace(
                home_team=SimpleNamespace(id=fixture_id * 2),
                away_team=SimpleNamespace(id=fixture_id * 2 + 1),
            )
            analyses.append({
                'match': match,
                'fixture_id': fixture_id,
                'home_team': f'Home {index}',
                'away_team': f'Away {index}',
                'league_name': f'League {index}',
                'league_id': index + 1,
                'match_date': '2026-06-01T12:00:00+00:00',
                'value_result': {
                    'analysis_data': {
                        'top_bets': [{
                            'market': 'under_4.5',
                            'pick': 'Under 4.5',
                            'probability': 0.90,
                            'market_odd': 1.40,
                            'score': 0.90,
                        }],
                        'consensus': {'draw': 0.10},
                        'decision': {
                            'confidence': {'stars': 5},
                            'risk': 'low',
                        },
                    },
                    'features': {
                        'form': {
                            'home_weighted_form': 2.0,
                            'away_weighted_form': 2.0,
                        },
                    },
                },
                'multiple_result': None,
            })

        created = []

        def create_bet(**kwargs):
            created.append(kwargs)
            return SimpleNamespace(suggested_stake=1.0)

        with patch.object(DailyBet.objects, 'create', side_effect=create_bet):
            tickets = generator._generate_multiple_tickets(analyses, date(2026, 6, 1))

        self.assertEqual(len(tickets), 3)
        fixture_sets = [
            {selection['fixture_id'] for selection in ticket['selections']}
            for ticket in created
        ]
        self.assertEqual([len(fixtures) for fixtures in fixture_sets], [3, 5, 7])
        self.assertFalse(fixture_sets[0] & fixture_sets[1])
        self.assertFalse(fixture_sets[0] & fixture_sets[2])
        self.assertFalse(fixture_sets[1] & fixture_sets[2])
