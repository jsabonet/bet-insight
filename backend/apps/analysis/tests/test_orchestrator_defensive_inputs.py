from types import SimpleNamespace
from unittest.mock import Mock

from django.test import SimpleTestCase

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator


class StopAfterEnsemble(Exception):
    pass


class OrchestratorDefensiveInputTests(SimpleTestCase):
    def test_passes_goals_conceded_per_game_to_ensemble(self):
        orchestrator = HybridAnalysisOrchestrator.__new__(HybridAnalysisOrchestrator)
        orchestrator.enable_cup_adjustment = True
        orchestrator.enricher = Mock()
        orchestrator.enricher.enrich.return_value = {'api_id': 123}
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
        orchestrator.context_analyzer = Mock()
        orchestrator.context_analyzer.analyze.return_value = {'patterns': []}
        orchestrator.hybrid_strategy = Mock()
        orchestrator.hybrid_strategy.should_use_context.return_value = {'use_context': False}
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
