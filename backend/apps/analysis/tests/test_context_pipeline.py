from django.test import SimpleTestCase
from unittest.mock import Mock, patch

from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.ai_analyzer import AIAnalyzer
from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.analysis.services.context_pipeline import analyze_match_context
from apps.analysis.services.decision_engine import DecisionEngine
from apps.analysis.services.hybrid_strategy import HybridStrategy
from apps.analysis.services.ml_integration import MLModel, ModelEnsembleML
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.parallel_enricher import ParallelMatchEnricher
from apps.analysis.services.statistical_models import PoissonBivariateModel
from apps.analysis.config.analysis_config import EnsembleWeights


class HybridStrategyEvidenceTests(SimpleTestCase):
    def setUp(self):
        self.strategy = HybridStrategy()
        self.detected = {
            'patterns': [{
                'name': 'bogey_team_effect',
                'confidence': 0.95,
                'favorable_markets': ['double_chance_1x'],
                'market_weights': {'double_chance_1x': 0.9},
            }],
            'top_markets': [],
        }

    def test_rejects_high_rule_confidence_without_required_source_data(self):
        features = {
            '_metadata': {
                'data_availability': {
                    'h2h': False,
                    'weather': True,
                },
            },
        }

        result = self.strategy.apply_context(self.detected, features)

        self.assertFalse(result['context_decision']['use_context'])
        self.assertEqual(result['patterns'], [])
        self.assertFalse(result['confidence_is_calibrated'])

    def test_accepts_strong_pattern_when_its_source_data_is_available(self):
        features = {
            '_metadata': {
                'data_availability': {'h2h': True},
                'sample_sizes': {'h2h_games': 3},
            },
        }

        result = self.strategy.apply_context(self.detected, features)

        self.assertTrue(result['context_decision']['use_context'])
        self.assertEqual(
            [pattern['name'] for pattern in result['patterns']],
            ['bogey_team_effect'],
        )
        self.assertIn('double_chance_1x', {
            market['market'] for market in result['top_markets']
        })

    def test_rejects_pattern_below_strong_context_threshold(self):
        self.detected['patterns'][0]['confidence'] = 0.79
        features = {
            '_metadata': {
                'data_availability': {'h2h': True},
                'sample_sizes': {'h2h_games': 3},
            },
        }

        result = self.strategy.apply_context(self.detected, features)

        self.assertFalse(result['context_decision']['use_context'])
        self.assertEqual(result['patterns'], [])

    def test_quality_warning_does_not_count_as_predictive_context(self):
        context = {
            'patterns': [{
                'name': 'bookmaker_margin_high',
                'confidence': 0.80,
                'favorable_markets': ['1x'],
                'market_weights': {'1x': 0.75},
            }],
            'top_markets': [],
        }

        result = self.strategy.apply_context(
            context,
            {'_metadata': {'data_availability': {'market': True}}},
        )

        self.assertFalse(result['context_decision']['use_context'])
        self.assertEqual(result['patterns'], [])
        self.assertEqual(
            [pattern['name'] for pattern in result['detected_patterns']],
            ['bookmaker_margin_high'],
        )

    def test_open_game_does_not_require_h2h_when_recent_form_and_statistics_are_sufficient(self):
        context = {
            'patterns': [{
                'name': 'open_game',
                'confidence': 0.80,
            }],
        }
        features = {
            '_metadata': {
                'data_availability': {
                    'recent_form': True,
                    'team_statistics': True,
                    'h2h': False,
                },
                'sample_sizes': {
                    'home_recent_form_games': 5,
                    'away_recent_form_games': 4,
                    'home_team_statistics_games': 20,
                    'away_team_statistics_games': 19,
                },
            },
        }

        result = self.strategy.apply_context(context, features)

        self.assertEqual(
            result['context_decision']['approved_patterns'],
            ['open_game'],
        )

    def test_open_game_gate_rejects_insufficient_recent_form_or_team_samples(self):
        context = {
            'patterns': [{'name': 'open_game', 'confidence': 0.90}],
        }
        features = {
            '_metadata': {
                'data_availability': {
                    'recent_form': True,
                    'team_statistics': True,
                },
                'sample_sizes': {
                    'home_recent_form_games': 2,
                    'away_recent_form_games': 5,
                    'home_team_statistics_games': 20,
                    'away_team_statistics_games': 19,
                },
            },
        }

        result = self.strategy.apply_context(context, features)

        self.assertFalse(result['context_decision']['use_context'])

        features['_metadata']['sample_sizes'].update({
            'home_recent_form_games': 5,
            'home_team_statistics_games': 4,
        })
        result = self.strategy.apply_context(context, features)

        self.assertFalse(result['context_decision']['use_context'])

    def test_h2h_patterns_require_three_valid_sampled_matches(self):
        features = {
            '_metadata': {
                'data_availability': {'h2h': True},
                'sample_sizes': {'h2h_games': 2},
            },
        }

        result = self.strategy.apply_context(self.detected, features)

        self.assertFalse(result['context_decision']['use_context'])


class ContextFeatureInputTests(SimpleTestCase):
    def setUp(self):
        self.engineer = FeatureEngineer()

    def test_importance_features_read_provider_fixture_shape_and_both_positions(self):
        features = self.engineer._calculate_match_importance_features(
            {
                'fixture_details': {
                    'home_team': {'name': 'Home'},
                    'away_team': {'name': 'Away'},
                    'league': {'round': 'Regular Season - 20'},
                },
            },
            {
                'home': {'position': 3, 'points': 40},
                'away': {'position': 17, 'points': 12},
            },
        )

        self.assertEqual(features['away_distance_to_relegation'], 1)
        self.assertFalse(features['is_derby'])
        self.assertEqual(features['season_progress'], round(20 / 38, 2))

    def test_injury_features_read_enricher_home_away_payload(self):
        features = self.engineer._calculate_injuries_suspensions_features({
            'fixture_details': {
                'home_team': {'name': 'Home'},
                'away_team': {'name': 'Away'},
            },
            'injuries': {
                'home': [{'player': 'Player H', 'reason': 'Suspended', 'type': 'Missing'}],
                'away': [],
            },
        })

        self.assertEqual(features['home_injured_count'], 1)
        self.assertEqual(features['away_injured_count'], 0)

    def test_rest_context_accepts_enricher_aliases_and_exposes_ai_aliases(self):
        rest_context = {'home_days_rest': 6, 'away_days_rest': 7}

        features = self.engineer._calculate_context_features(rest_context)

        self.assertTrue(self.engineer._has_rest_context(rest_context))
        self.assertEqual(features['home_rest_days'], 6)
        self.assertEqual(features['away_rest_days'], 7)
        self.assertEqual(features['home_days_rest'], 6)
        self.assertEqual(features['away_days_rest'], 7)

    def test_recent_goal_averages_are_exposed_to_context_analyzer(self):
        form = self.engineer._calculate_form_features(
            {},
            {
                'home': {
                    'games': [
                        {'goals_scored': 2, 'goals_conceded': 1},
                        {'goals_scored': 1, 'goals_conceded': 2},
                        {'goals_scored': 3, 'goals_conceded': 0},
                    ],
                    'summary': {'strength_of_schedule': 0},
                },
                'away': {
                    'games': [
                        {'goals_scored': 2, 'goals_conceded': 0},
                        {'goals_scored': 2, 'goals_conceded': 2},
                    ],
                    'summary': {'strength_of_schedule': 0},
                },
            },
        )

        self.assertEqual(form['home_goals_scored_avg_l5'], 2.0)
        self.assertEqual(form['away_goals_scored_avg_l5'], 2.0)
        self.assertEqual(form['home_goal_samples_l5'], 3)

    def test_league_scoring_context_requires_minimum_sample(self):
        insufficient = self.engineer._calculate_league_context_features({
            'matches_sampled': 29,
            'avg_goals_per_match': 3.2,
            'avg_goals_per_team_game': 1.6,
        })
        sufficient = self.engineer._calculate_league_context_features({
            'matches_sampled': 30,
            'avg_goals_per_match': 3.2,
            'avg_goals_per_team_game': 1.6,
        })

        self.assertFalse(insufficient['available'])
        self.assertTrue(sufficient['available'])
        self.assertEqual(sufficient['avg_goals_per_team_game'], 1.6)

    def test_league_goal_average_is_shared_by_sequential_and_parallel_enrichers(self):
        standings = {
            1: {'games_played': 10, 'goals_for': 18},
            2: {'games_played': 10, 'goals_for': 22},
        }

        result = MatchDataEnricher._calculate_league_goal_context(standings)
        parallel = ParallelMatchEnricher.__new__(ParallelMatchEnricher)
        parallel_result = parallel._process_standings(standings, 1, 2)

        self.assertEqual(result['matches_sampled'], 10)
        self.assertEqual(result['avg_goals_per_match'], 4.0)
        self.assertEqual(
            parallel_result['league']['avg_goals_per_team_game'],
            result['avg_goals_per_team_game'],
        )

    def test_poisson_uses_available_league_average_for_defense_normalization(self):
        calibrator = Mock()
        calibrator.is_available.return_value = False

        with patch(
            'apps.analysis.services.statistical_models.get_xg_calibrator',
            return_value=calibrator,
        ):
            result = PoissonBivariateModel().predict(
                home_strength=1.2,
                away_strength=1.4,
                home_defense=1.1,
                away_defense=1.5,
                league_avg_goals_per_team=1.6,
            )

        self.assertAlmostEqual(
            result['expected_goals']['home'],
            1.2 * 1.07 * 1.5 / 1.6,
        )
        self.assertAlmostEqual(
            result['expected_goals']['away'],
            1.4 * 1.1 / 1.6,
        )

    def test_form_and_actual_h2h_features_enable_open_game_context(self):
        features = {
            'form': {
                'home_goals_scored_avg_l5': 2.0,
                'away_goals_scored_avg_l5': 2.1,
                'home_goal_samples_l5': 5,
                'away_goal_samples_l5': 5,
            },
            'h2h': {
                'h2h_games': 0,
                'h2h_avg_goals': 0,
                'h2h_btts_rate': 0,
            },
            '_metadata': {
                'data_availability': {
                    'recent_form': True,
                    'team_statistics': True,
                    'h2h': False,
                },
                'sample_sizes': {
                    'home_recent_form_games': 5,
                    'away_recent_form_games': 5,
                    'home_team_statistics_games': 10,
                    'away_team_statistics_games': 10,
                    'h2h_games': 0,
                },
            },
        }

        result = analyze_match_context(features)

        self.assertIn('open_game', result['context_decision']['approved_patterns'])

    def test_open_game_detection_requires_three_valid_recent_matches_per_team(self):
        context = ContextAnalyzer().analyze({
            'form': {
                'home_goals_scored_avg_l5': 2.2,
                'away_goals_scored_avg_l5': 2.1,
                'home_goal_samples_l5': 2,
                'away_goal_samples_l5': 5,
            },
            'h2h': {'h2h_games': 0},
        })

        self.assertNotIn(
            'open_game',
            [pattern['name'] for pattern in context['patterns']],
        )

    def test_h2h_features_exclude_matches_without_finished_scores(self):
        result = self.engineer._calculate_h2h_features([
            {
                'homeTeam': {'score': 2},
                'awayTeam': {'score': 1},
            },
            {
                'homeTeam': {'score': None},
                'awayTeam': {'score': None},
            },
            {
                'homeTeam': {'score': 0},
                'awayTeam': {'score': 0},
            },
        ])

        self.assertEqual(result['h2h_games'], 2)
        self.assertEqual(result['h2h_avg_goals'], 1.5)

    def test_h2h_wins_are_counted_for_current_teams_not_historical_venue(self):
        result = self.engineer._calculate_h2h_features(
            [
                {
                    'homeTeam': {'id': 20, 'score': 0},
                    'awayTeam': {'id': 10, 'score': 4},
                },
                {
                    'homeTeam': {'id': 10, 'score': 1},
                    'awayTeam': {'id': 20, 'score': 1},
                },
                {
                    'homeTeam': {'id': 10, 'score': 0},
                    'awayTeam': {'id': 20, 'score': 2},
                },
                {
                    'homeTeam': {'id': 30, 'score': 3},
                    'awayTeam': {'id': 40, 'score': 0},
                },
            ],
            {
                'home_team': {'id': 10},
                'away_team': {'id': 20},
            },
        )

        self.assertEqual(result['h2h_games'], 3)
        self.assertEqual(result['h2h_home_wins'], 1)
        self.assertEqual(result['h2h_draws'], 1)
        self.assertEqual(result['h2h_away_wins'], 1)
        self.assertEqual(result['h2h_home_win_rate'], 0.33)
        self.assertEqual(result['h2h_away_win_rate'], 0.33)
        self.assertEqual(result['h2h_draw_rate'], 0.33)

    def test_salzburg_fixture_h2h_sample_becomes_six_home_wins(self):
        salzburg_id = 10
        lustenau_id = 20
        results = [(7, 0), (0, 4), (4, 0), (0, 6), (5, 0), (0, 1)]
        h2h_data = []
        for index, (home_goals, away_goals) in enumerate(results):
            reversed_venue = index in {1, 3, 5}
            h2h_data.append({
                'homeTeam': {
                    'id': lustenau_id if reversed_venue else salzburg_id,
                    'score': home_goals,
                },
                'awayTeam': {
                    'id': salzburg_id if reversed_venue else lustenau_id,
                    'score': away_goals,
                },
            })

        result = self.engineer._calculate_h2h_features(
            h2h_data,
            {
                'home_team': {'id': salzburg_id},
                'away_team': {'id': lustenau_id},
            },
        )

        self.assertEqual(result['h2h_home_wins'], 6)
        self.assertEqual(result['h2h_away_wins'], 0)
        self.assertEqual(result['h2h_home_win_rate'], 1.0)
        self.assertEqual(result['h2h_avg_goals'], 4.5)
        self.assertEqual(result['h2h_btts_rate'], 0.0)

    def test_h2h_fetch_excludes_exact_fixture_future_and_undated_matches(self):
        enricher = MatchDataEnricher.__new__(MatchDataEnricher)
        enricher.api_service = Mock()
        enricher.api_service.fetch_h2h.return_value = [
            {'fixture_id': 10, 'date': '2026-10-25T12:00:00Z'},
            {'fixture_id': 1561958, 'date': '2026-11-01T13:30:00Z'},
            {'fixture_id': 12, 'date': '2026-11-02T12:00:00Z'},
            {'fixture_id': 13},
        ]

        with patch('apps.analysis.services.match_enricher.time.sleep'):
            result = enricher._get_h2h(
                1,
                2,
                {
                    'fixture_id': 1561958,
                    'date': '2026-11-01T13:30:00Z',
                },
            )

        self.assertEqual([match['fixture_id'] for match in result], [10])


class MLFeatureSchemaTests(SimpleTestCase):
    def test_features_are_ordered_by_training_schema_and_missing_names_are_zero(self):
        model = MLModel.__new__(MLModel)

        matrix = model._prepare_features(
            {'form.away': 2.5, 'form.home': 1.25, 'extra': 99},
            ['form.home', 'form.missing', 'form.away'],
            'test_market',
        )

        self.assertEqual(matrix.tolist(), [[1.25, 0.0, 2.5]])

    def test_feature_preparation_rejects_missing_schema(self):
        model = MLModel.__new__(MLModel)

        with self.assertRaisesRegex(ValueError, 'Esquema de features'):
            model._prepare_features({'form.home': 1.0}, None, 'test_market')

    def test_feature_flattening_preserves_categorical_names_as_training_zeros(self):
        model = MLModel.__new__(MLModel)

        flattened = model._flatten_features({
            'weather': {'condition': 'Clear', 'goal_impact': -0.2},
        })

        self.assertEqual(flattened, {
            'weather.condition': 0,
            'weather.goal_impact': -0.2,
        })


class AIAnalyzerFeatureMappingTests(SimpleTestCase):
    def test_decision_context_reads_feature_engineer_names_and_scales(self):
        analyzer = AIAnalyzer.__new__(AIAnalyzer)
        enriched_data = {
            'model_probabilities': {
                'poisson': {
                    'expected_goals': {'home': 2.2, 'away': 1.0},
                    'probabilities': {},
                },
                'consensus': {'home_win': 0.7, 'away_win': 0.1},
            },
            'features_summary': {
                'form': {'home_momentum': 1.2, 'away_momentum': -2.0},
                'injuries_suspensions': {
                    'home_key_players_out': 2,
                    'away_key_players_out': 1,
                },
                'motivation': {'home_motivation': 10, 'away_motivation': 4},
                'context': {'home_days_rest': 6, 'away_days_rest': 7},
                'h2h': {
                    'h2h_avg_goals': 4.5,
                    'h2h_home_win_rate': 1.0,
                    'h2h_away_win_rate': 0.0,
                    'h2h_draw_rate': 0.0,
                },
                'statistics': {
                    'home_corners_per_game': 5,
                    'away_corners_per_game': 2,
                    'home_cards_per_game': 2,
                    'away_cards_per_game': 2.5,
                },
                'elo': {'elo_differential': 250},
            },
            'context_analysis': {'patterns': []},
        }
        captured_context = {}

        def capture_context(_bet, context, _data, _strategy):
            captured_context.update(context)
            return 1.0

        with patch.object(
            analyzer,
            '_calculate_contextual_fit_score',
            side_effect=capture_context,
        ):
            analyzer._select_best_bet_by_context(
                [{'market_display': 'Vitória Casa'}],
                enriched_data,
            )

        self.assertTrue(captured_context['home_hot_streak'])
        self.assertTrue(captured_context['away_cold_streak'])
        self.assertTrue(captured_context['home_critical_injuries'])
        self.assertTrue(captured_context['both_weakened'])
        self.assertTrue(captured_context['home_must_win'])
        self.assertTrue(captured_context['both_rested'])
        self.assertTrue(captured_context['h2h_home_dominance'])
        self.assertTrue(captured_context['h2h_high_scoring'])
        self.assertTrue(captured_context['home_set_pieces_strong'])
        self.assertTrue(captured_context['high_cards_expected'])
        self.assertTrue(captured_context['elo_gap_large'])

        explanation = analyzer._get_context_explanation(enriched_data)
        self.assertIn('Casa em ÓTIMA forma', explanation)
        self.assertIn('Casa com 2 lesões CRÍTICAS', explanation)


class ContextOverrideEvidenceTests(SimpleTestCase):
    def test_contextual_fit_is_neutral_when_context_gate_rejects_all_patterns(self):
        decision_engine = DecisionEngine.__new__(DecisionEngine)

        fit = decision_engine._calculate_contextual_fit(
            'under_2.5',
            {'patterns': []},
            {
                'consensus': {'under_2.5': 0.84},
                'poisson': {'probabilities': {'under_2.5': 0.84}},
            },
            'multiple',
        )

        self.assertEqual(fit, 1.0)

    def test_open_game_context_favors_overs_and_penalizes_unders(self):
        decision_engine = DecisionEngine.__new__(DecisionEngine)
        context = {
            'patterns': [{
                'name': 'open_game',
                'confidence': 0.9,
                'favorable_markets': ['over_2.5', 'over_1.5'],
                'market_weights': {
                    'over_2.5': 0.70,
                    'over_1.5': 0.65,
                },
            }],
        }
        predictions = {
            'consensus': {'under_3.5': 0.80, 'over_2.5': 0.55},
            'poisson': {
                'probabilities': {'under_3.5': 0.80, 'over_2.5': 0.55},
            },
        }

        under_fit = decision_engine._calculate_contextual_fit(
            'under_3.5', context, predictions, 'multiple'
        )
        over_fit = decision_engine._calculate_contextual_fit(
            'over_2.5', context, predictions, 'multiple'
        )

        self.assertLess(under_fit, 1.0)
        self.assertGreater(over_fit, 1.0)

    def test_low_scoring_context_only_boosts_the_goal_lines_it_supports(self):
        decision_engine = DecisionEngine.__new__(DecisionEngine)
        context = {
            'patterns': [{
                'name': 'congested_schedule_both',
                'confidence': 0.85,
                'favorable_markets': ['under_2.5', 'under_3.5'],
                'market_weights': {
                    'under_2.5': 0.80,
                    'under_3.5': 0.75,
                },
            }],
        }

        under_35_fit = decision_engine._calculate_contextual_fit(
            'under_3.5', context, {}, 'multiple'
        )
        under_45_fit = decision_engine._calculate_contextual_fit(
            'under_4.5', context, {}, 'multiple'
        )

        self.assertGreater(under_35_fit, 1.0)
        self.assertEqual(under_45_fit, 1.0)

    def test_contextual_fit_explanation_identifies_offensive_pattern_conflict(self):
        decision_engine = DecisionEngine.__new__(DecisionEngine)

        explanation = decision_engine._explain_contextual_fit(
            'under_3.5',
            0.82,
            {
                'patterns': [{
                    'name': 'open_game',
                    'confidence': 0.9,
                    'favorable_markets': ['over_2.5', 'over_1.5'],
                    'market_weights': {
                        'over_2.5': 0.70,
                        'over_1.5': 0.65,
                    },
                }],
            },
        )

        self.assertIn('conflito com Under', explanation)

    def test_contextual_fit_explanation_does_not_generalize_under_support_to_other_lines(self):
        decision_engine = DecisionEngine.__new__(DecisionEngine)
        explanation = decision_engine._explain_contextual_fit(
            'under_4.5',
            1.0,
            {
                'patterns': [{
                    'name': 'congested_schedule_both',
                    'confidence': 0.85,
                    'favorable_markets': ['under_2.5', 'under_3.5'],
                    'market_weights': {
                        'under_2.5': 0.80,
                        'under_3.5': 0.75,
                    },
                }],
            },
        )

        self.assertEqual(explanation, 'Contexto neutro')

    def test_high_model_probability_does_not_masquerade_as_contextual_fit(self):
        decision_engine = DecisionEngine.__new__(DecisionEngine)

        fit = decision_engine._calculate_contextual_fit(
            'under_1.5',
            {'patterns': []},
            {
                'consensus': {'under_1.5': 0.90},
                'poisson': {'probabilities': {'under_1.5': 0.90}},
            },
            'multiple',
        )

        self.assertEqual(fit, 1.0)

    def test_no_context_override_when_context_gate_rejected_all_patterns(self):
        bet = {
            'context_score': 1.0,
            'supporting_patterns': [],
        }

        self.assertFalse(
            DecisionEngine._has_approved_context_support(
                bet,
                {'patterns': [], 'detected_patterns': [{'name': 'bogey_team_effect'}]},
            )
        )

    def test_context_override_requires_approved_pattern_supporting_the_market(self):
        context = {
            'patterns': [{'name': 'open_game'}],
        }
        supported_bet = {
            'context_score': 0.80,
            'supporting_patterns': ['open_game'],
        }
        unrelated_bet = {
            'context_score': 0.90,
            'supporting_patterns': ['bogey_team_effect'],
        }

        self.assertTrue(
            DecisionEngine._has_approved_context_support(supported_bet, context)
        )
        self.assertFalse(
            DecisionEngine._has_approved_context_support(unrelated_bet, context)
        )


class EnsembleContextPropagationTests(SimpleTestCase):
    def setUp(self):
        self.ensemble = ModelEnsembleML.__new__(ModelEnsembleML)
        self.ensemble.poisson = Mock()
        self.ensemble.poisson.predict.return_value = {
            'probabilities': {
                'home_win': 0.3,
                'draw': 0.3,
                'away_win': 0.4,
            },
            'expected_goals': {'home': 1.7, 'away': 1.5},
        }
        self.ensemble.ml = Mock()
        self.ensemble.ml.predict_1x2.return_value = {
            'home_win': 0.3,
            'draw': 0.3,
            'away_win': 0.4,
        }
        self.ensemble.has_ml = True
        self.ensemble.use_market_prior = True

    def test_cup_feature_key_selects_cup_model(self):
        self.ensemble.predict(
            {'competition': {'is_cup_competition': True}, 'market': {}},
            1.7,
            1.5,
        )

        self.ensemble.ml.predict_1x2.assert_called_once()
        self.assertTrue(
            self.ensemble.ml.predict_1x2.call_args.kwargs['is_cup']
        )

    def test_approved_open_game_context_applies_even_with_clear_market_favorite(self):
        result = self.ensemble.predict(
            {
                'competition': {'is_cup_competition': False},
                'market': {
                    'market_home_prob': 0.2,
                    'market_draw_prob': 0.2,
                    'market_away_prob': 0.6,
                },
            },
            1.7,
            1.5,
            context_analysis={
                'patterns': [{'name': 'open_game', 'confidence': 0.9}],
                'context_decision': {'use_context': True},
            },
        )

        self.assertEqual(result['weights'], EnsembleWeights.STRONG_CONTEXT)
