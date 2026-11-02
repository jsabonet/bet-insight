from types import SimpleNamespace
from unittest.mock import Mock

from django.test import SimpleTestCase

from apps.analysis.services.analysis_orchestrator import (
    FixtureDetailsUnavailableError,
    HybridAnalysisOrchestrator,
)


class StopAfterEnsemble(Exception):
    pass


class OrchestratorDefensiveInputTests(SimpleTestCase):
    def test_missing_fixture_details_raise_specific_unavailable_error(self):
        orchestrator = HybridAnalysisOrchestrator.__new__(HybridAnalysisOrchestrator)
        orchestrator.enricher = Mock()
        orchestrator.enricher.enrich.return_value = {'api_id': 123}
        match = SimpleNamespace(api_football_id=123)

        with self.assertRaises(FixtureDetailsUnavailableError):
            orchestrator.run(match, include_ai=False)

    def test_returns_form_features_for_daily_bet_generator(self):
        orchestrator = HybridAnalysisOrchestrator.__new__(HybridAnalysisOrchestrator)
        form_features = {
            'home_weighted_form': 2.4,
            'away_weighted_form': 1.1,
        }
        orchestrator.enable_cup_adjustment = True
        orchestrator.enricher = Mock()
        orchestrator.enricher.enrich.return_value = {
            'api_id': 123,
            'odds': {},
            'fixture_details': {'league': {'id': 39}},
        }
        orchestrator.fe = Mock()
        orchestrator.fe.engineer_all_features.return_value = {
            'strength': {
                'home_goals_per_game': 1.6,
                'away_goals_per_game': 1.2,
                'home_conceded_per_game': 1.4,
                'away_conceded_per_game': 0.9,
            },
            'form': form_features,
            'weather': {'goal_impact': 0.0},
            'competition': {'is_cup_competition': False},
        }
        orchestrator.hybrid_strategy = Mock()
        orchestrator.hybrid_strategy.apply_context.return_value = {
            'patterns': [],
            'top_markets': [],
            'context_decision': {'use_context': False, 'approved_patterns': []},
        }
        orchestrator.ensemble = Mock()
        orchestrator.ensemble.predict.return_value = {
            'consensus': {'home_win': 0.5, 'draw': 0.3, 'away_win': 0.2},
            'poisson': {
                'expected_goals': {'home': 1.6, 'away': 1.2},
                'probabilities': {'home_win': 0.5, 'draw': 0.3, 'away_win': 0.2},
            },
            'logistic': {},
            'market': {},
        }
        orchestrator.decision = Mock()
        orchestrator.decision.make_decision.return_value = {
            'recommendation': {
                'market_display': 'Vitória Casa',
                'probability': 0.5,
                'fair_odd': 2.0,
            },
            'confidence': {'stars': 3},
            'risk': 'medium',
            'fair_odds': {},
            'value_bets': [],
            'top_bets': [],
            'publish_filter': {'should_publish': True},
        }
        orchestrator.ai = Mock()
        orchestrator.ai.explain_decision.return_value = {'success': False}

        match = SimpleNamespace(
            api_football_id=123,
            league=SimpleNamespace(api_football_id=39),
        )

        result = orchestrator.run(match, include_ai=False)

        self.assertEqual(
            result['analysis_data']['features_summary']['form'],
            form_features,
        )
        orchestrator.ai.explain_decision.assert_not_called()

    def test_passes_goals_conceded_per_game_to_ensemble(self):
        orchestrator = HybridAnalysisOrchestrator.__new__(HybridAnalysisOrchestrator)
        orchestrator.enable_cup_adjustment = True
        orchestrator.enricher = Mock()
        orchestrator.enricher.enrich.return_value = {
            'api_id': 123,
            'fixture_details': {'league': {'id': 39}},
        }
        orchestrator.fe = Mock()
        orchestrator.fe.engineer_all_features.return_value = {
            'strength': {
                'home_goals_per_game': 1.6,
                'away_goals_per_game': 1.2,
                'home_conceded_per_game': 1.4,
                'away_conceded_per_game': 0.9,
            },
            'weather': {'goal_impact': 0.0},
            'competition': {'is_cup_competition': False},
        }
        orchestrator.hybrid_strategy = Mock()
        orchestrator.hybrid_strategy.apply_context.return_value = {
            'patterns': [],
            'top_markets': [],
            'context_decision': {'use_context': False, 'approved_patterns': []},
        }
        orchestrator.ensemble = Mock()
        orchestrator.ensemble.predict.side_effect = StopAfterEnsemble

        match = SimpleNamespace(
            api_football_id=123,
            league=SimpleNamespace(api_football_id=39),
        )

        with self.assertRaises(StopAfterEnsemble):
            orchestrator.run(match)

        self.assertEqual(
            orchestrator.ensemble.predict.call_args.args[1:5],
            (1.6, 1.2, 0.0, 39),
        )
        self.assertEqual(orchestrator.ensemble.predict.call_args.kwargs['home_defense'], 1.4)
        self.assertEqual(orchestrator.ensemble.predict.call_args.kwargs['away_defense'], 0.9)
