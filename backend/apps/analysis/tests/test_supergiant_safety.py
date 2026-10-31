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
                'multiple_result': {
                    'analysis_data': {
                        'top_bets': [{
                            'market': 'under_3.5',
                            'pick': 'Under 3.5',
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
            })

        created = []

        def create_bet(**kwargs):
            created.append(kwargs)
            return SimpleNamespace(suggested_stake=1.0)

        with patch.object(DailyBet.objects, 'create', side_effect=create_bet):
            tickets = generator._generate_multiple_tickets(analyses, date(2026, 6, 1))

        self.assertEqual(len(tickets), 3)
        self.assertTrue(all(
            selection['market'] == 'under_3.5'
            for ticket in created
            for selection in ticket['selections']
        ))
        fixture_sets = [
            {selection['fixture_id'] for selection in ticket['selections']}
            for ticket in created
        ]
        self.assertEqual([len(fixtures) for fixtures in fixture_sets], [3, 5, 7])
        self.assertFalse(fixture_sets[0] & fixture_sets[1])
        self.assertFalse(fixture_sets[0] & fixture_sets[2])
        self.assertFalse(fixture_sets[1] & fixture_sets[2])

    def test_multiple_tickets_do_not_fall_back_to_value_analysis(self):
        generator = DailyBetGenerator.__new__(DailyBetGenerator)
        analyses = [{
            'match': SimpleNamespace(
                home_team=SimpleNamespace(id=100),
                away_team=SimpleNamespace(id=101),
            ),
            'fixture_id': 12345,
            'home_team': 'Home',
            'away_team': 'Away',
            'league_name': 'League',
            'league_id': 1,
            'match_date': '2026-06-01T12:00:00+00:00',
            'value_result': {
                'analysis_data': {
                    'top_bets': [{
                        'market': 'under_3.5',
                        'pick': 'Under 3.5',
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
            },
            'multiple_result': None,
        }]

        tickets = generator._generate_multiple_tickets(analyses, date(2026, 6, 1))

        self.assertEqual(tickets, [])

    def test_multiple_tickets_reuse_fixture_only_with_a_different_market(self):
        generator = DailyBetGenerator.__new__(DailyBetGenerator)
        analyses = []

        for index in range(6):
            fixture_id = 20000 + index
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
                'multiple_result': {
                    'analysis_data': {
                        'top_bets': [
                            {
                                'market': 'under_3.5',
                                'pick': 'Under 3.5',
                                'probability': 0.90,
                                'market_odd': 1.40,
                                'score': 0.70,
                                'ranking_score': 0.70,
                                'contextual_fit': 1.4,
                            },
                            {
                                'market': 'under_2.5',
                                'pick': 'Under 2.5',
                                'probability': 0.89,
                                'market_odd': 1.45,
                                'score': 0.88,
                                'contextual_fit': 1.1,
                            },
                            {
                                'market': 'double_chance_1x',
                                'pick': '1X',
                                'probability': 0.88,
                                'market_odd': 1.45,
                                'score': 0.85,
                                'contextual_fit': 1.0,
                            },
                        ],
                        'consensus': {'draw': 0.10},
                        'confidence': {'stars': 5},
                        'risk': 'low',
                    },
                },
            })

        created = []

        def create_bet(**kwargs):
            created.append(kwargs)
            return SimpleNamespace(suggested_stake=1.0)

        with patch.object(DailyBet.objects, 'create', side_effect=create_bet):
            tickets = generator._generate_multiple_tickets(analyses, date(2026, 6, 1))

        self.assertEqual([len(ticket['selections']) for ticket in created], [3, 5])
        first_fixture_pick = next(
            selection
            for selection in created[0]['selections']
            if selection['fixture_id'] == 20000
        )
        self.assertEqual(first_fixture_pick['market'], 'under_2.5')
        fixture_sets = [
            [selection['fixture_id'] for selection in ticket['selections']]
            for ticket in created
        ]
        self.assertTrue(all(len(fixtures) == len(set(fixtures)) for fixtures in fixture_sets))

        all_selections = [
            selection
            for ticket in created
            for selection in ticket['selections']
        ]
        fixture_appearances = {}
        fixture_markets = {}
        for selection in all_selections:
            fixture_id = selection['fixture_id']
            fixture_appearances[fixture_id] = fixture_appearances.get(fixture_id, 0) + 1
            fixture_markets.setdefault(fixture_id, set()).add(selection['market'])
            self.assertNotIn('_candidate_rank', selection)

        self.assertTrue(all(
            appearances <= generator.MAX_FIXTURE_TICKET_APPEARANCES
            for appearances in fixture_appearances.values()
        ))
        self.assertLessEqual(
            sum(ticket['suggested_stake'] for ticket in created),
            generator.MAX_DAILY_MULTIPLE_STAKE_UNITS,
        )
        repeated_fixtures = {
            fixture_id
            for fixture_id, appearances in fixture_appearances.items()
            if appearances > 1
        }
        self.assertTrue(repeated_fixtures)
        self.assertTrue(all(len(fixture_markets[fixture_id]) == 2 for fixture_id in repeated_fixtures))
        self.assertTrue(all(
            len({
                generator._market_group(market)
                for market in fixture_markets[fixture_id]
            }) == 2
            for fixture_id in repeated_fixtures
        ))

        created.clear()
        with patch.object(
            generator,
            'MAX_DAILY_MULTIPLE_STAKE_UNITS',
            2.5,
            create=True,
        ), patch.object(DailyBet.objects, 'create', side_effect=create_bet):
            generator._generate_multiple_tickets(analyses, date(2026, 6, 1))

        self.assertEqual(len(created), 1)
        self.assertEqual(created[0]['suggested_stake'], 2.5)

    def test_multiple_tickets_use_form_from_orchestrator_analysis_data(self):
        generator = DailyBetGenerator.__new__(DailyBetGenerator)
        analyses = [{
            'match': SimpleNamespace(
                home_team=SimpleNamespace(id=100),
                away_team=SimpleNamespace(id=101),
            ),
            'fixture_id': 12345,
            'home_team': 'Home',
            'away_team': 'Away',
            'league_name': 'League',
            'league_id': 1,
            'match_date': '2026-06-01T12:00:00+00:00',
            'multiple_result': {
                'analysis_data': {
                    'top_bets': [{
                        'market': 'under_3.5',
                        'pick': 'Under 3.5',
                        'probability': 0.90,
                        'market_odd': 1.40,
                        'score': 0.90,
                    }],
                    'consensus': {'draw': 0.10},
                    'confidence': {'stars': 5},
                    'risk': 'low',
                    'features_summary': {
                        'form': {
                            'home_weighted_form': 1.0,
                            'away_weighted_form': 1.2,
                        },
                    },
                },
            },
        }]

        tickets = generator._generate_multiple_tickets(analyses, date(2026, 6, 1))

        self.assertEqual(tickets, [])

    def test_confidence_consensus_uses_ml_and_legacy_logistic_outputs(self):
        engine = DecisionEngine()
        poisson = {'home_win': 0.70, 'draw': 0.20, 'away_win': 0.10}
        features = {'strength': {}, 'form': {}}
        consensus = {'home_win': 0.40, 'draw': 0.30, 'away_win': 0.30}

        for model_key in ('ml', 'logistic'):
            with self.subTest(model_key=model_key):
                result = engine._calculate_confidence(
                    {
                        'poisson': {'probabilities': poisson},
                        model_key: dict(poisson),
                        'consensus': consensus,
                    },
                    features,
                )

                self.assertEqual(result['factors']['consensus'], 1.0)

    def test_confidence_consensus_measures_all_1x2_outcomes(self):
        engine = DecisionEngine()
        result = engine._calculate_confidence(
            {
                'poisson': {
                    'probabilities': {
                        'home_win': 1.0,
                        'draw': 0.0,
                        'away_win': 0.0,
                    },
                },
                'ml': {
                    'home_win': 0.0,
                    'draw': 1.0,
                    'away_win': 0.0,
                },
                'consensus': {
                    'home_win': 0.34,
                    'draw': 0.33,
                    'away_win': 0.33,
                },
            },
            {'strength': {}, 'form': {}},
        )

        self.assertEqual(result['factors']['consensus'], 0.0)

    def test_medium_confidence_does_not_receive_four_stars(self):
        engine = DecisionEngine()
        result = engine._calculate_confidence(
            {
                'consensus': {
                    'home_win': 0.40,
                    'draw': 0.35,
                    'away_win': 0.25,
                },
            },
            {
                'strength': {'strength_differential': 0.4},
                'form': {},
            },
        )

        self.assertEqual(result['score'], 0.63)
        self.assertEqual(result['level'], 'medium')
        self.assertEqual(result['stars'], 3)
