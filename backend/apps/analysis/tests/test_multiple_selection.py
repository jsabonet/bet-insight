from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.analysis.services.ai_analyzer import AIAnalyzer
from apps.analysis.services.decision_engine import DecisionEngine
from apps.analysis.services.multiple_selection import (
    eligible_multiple_candidates,
    rank_multiple_candidates,
)


class MultipleSelectionTests(SimpleTestCase):
    def test_integrated_score_precedes_contextual_fit(self):
        high_score = {
            'market': 'under_2.5',
            'ranking_score': 0.82,
            'score': 0.82,
            'contextual_fit': 1.0,
            'probability': 0.72,
        }
        high_context = {
            'market': 'home_win',
            'ranking_score': 0.71,
            'score': 0.71,
            'contextual_fit': 1.4,
            'probability': 0.80,
        }

        ranked = rank_multiple_candidates([high_context, high_score])

        self.assertEqual(ranked, [high_score, high_context])

    def test_context_and_probability_break_score_ties(self):
        lower_probability = {
            'market': 'under_3.5',
            'score': 0.8,
            'contextual_fit': 1.1,
            'probability': 0.70,
        }
        higher_probability = {
            'market': 'double_chance_1x',
            'score': 0.8,
            'contextual_fit': 1.1,
            'probability': 0.75,
        }
        higher_context = {
            'market': 'btts_no',
            'score': 0.8,
            'contextual_fit': 1.2,
            'probability': 0.65,
        }

        ranked = rank_multiple_candidates(
            [lower_probability, higher_probability, higher_context]
        )

        self.assertEqual(
            ranked,
            [higher_context, higher_probability, lower_probability],
        )

    def test_ranking_does_not_mutate_candidates(self):
        candidates = [
            {'market': 'under_2.5', 'score': 0.5},
            {'market': 'home_win', 'score': 0.8},
        ]

        ranked = rank_multiple_candidates(candidates)

        self.assertEqual(candidates[0]['market'], 'under_2.5')
        self.assertEqual(ranked[0]['market'], 'home_win')
        self.assertEqual(rank_multiple_candidates([]), [])

    def test_existing_multiple_eligibility_thresholds_are_preserved(self):
        candidates = [
            {'market': 'under_3.5', 'probability': 0.65, 'market_odd': 1.30},
            {'market': 'over_2.5', 'probability': 0.80, 'market_odd': 1.51},
            {'market': 'btts_yes', 'probability': 0.64, 'market_odd': 1.40},
        ]

        eligible = eligible_multiple_candidates(candidates)

        self.assertEqual([bet['market'] for bet in eligible], ['under_3.5'])

    def test_supergiant_protective_market_keeps_existing_lower_odd_floor(self):
        match = SimpleNamespace(
            home_team=SimpleNamespace(id=42),
            away_team=SimpleNamespace(id=157),
        )
        candidates = [
            {'market': 'double_chance_x2', 'probability': 0.80, 'market_odd': 1.15},
            {'market': 'home_over_0.5', 'probability': 0.90, 'market_odd': 1.40},
        ]

        eligible = eligible_multiple_candidates(candidates, match=match)

        self.assertEqual([bet['market'] for bet in eligible], ['double_chance_x2'])

    def test_multiple_recommendation_uses_integrated_score_without_reordering_top_bets(self):
        high_context = {
            'rank': 1,
            'market': 'home_win',
            'market_display': 'Vitória Casa',
            'pick': 'Casa',
            'probability': 0.80,
            'market_odd': 1.40,
            'fair_odd': 1.25,
            'ev_pct': 12.0,
            'stake_units': 1.0,
            'score': 0.70,
            'ranking_score': 0.70,
            'contextual_fit': 1.40,
            'reason': 'Contexto favorável',
        }
        high_score = {
            'rank': 2,
            'market': 'under_2.5',
            'market_display': 'Under 2.5',
            'pick': 'Under',
            'probability': 0.72,
            'market_odd': 1.45,
            'fair_odd': 1.39,
            'ev_pct': 4.0,
            'stake_units': 1.0,
            'score': 0.82,
            'ranking_score': 0.82,
            'contextual_fit': 1.05,
            'reason': 'Score integrado superior',
        }
        engine = DecisionEngine()
        match = SimpleNamespace(
            home_team=SimpleNamespace(id=1, name='Casa'),
            away_team=SimpleNamespace(id=2, name='Fora'),
        )

        with (
            patch.object(engine, '_calculate_fair_odds', return_value={}),
            patch.object(engine, '_find_value_bets', return_value=[]),
            patch.object(
                engine,
                '_calculate_confidence',
                return_value={'score': 0.8, 'stars': 4, 'level': 'high'},
            ),
            patch.object(engine, '_assess_risk', return_value='medium'),
            patch.object(
                engine,
                '_generate_recommendation',
                return_value={
                    'market': 'home_win',
                    'market_display': 'Vitória Casa',
                    'pick': 'Casa',
                    'probability': 0.70,
                    'odd': 1.40,
                },
            ),
            patch.object(
                engine,
                '_select_contextual_bets',
                return_value=[high_context, high_score],
            ),
        ):
            result = engine.make_decision(
                model_predictions={
                    'consensus': {'home_win': 0.70, 'draw': 0.10, 'away_win': 0.20},
                    'poisson': {'expected_goals': {}},
                },
                features={},
                market_odds={},
                strategy='multiple',
                context_analysis={'patterns': []},
                match=match,
            )

        self.assertEqual(result['recommendation']['market'], 'under_2.5')
        self.assertEqual(result['multiple_selection']['market'], 'under_2.5')
        self.assertTrue(result['multiple_selection']['selection_eligible'])
        self.assertEqual(result['top_bets'], [high_context, high_score])

    def test_multiple_fallback_explains_decision_engine_selection(self):
        high_context = {
            'market': 'home_win',
            'market_display': 'Vitória Casa',
            'pick': 'Casa',
            'probability': 0.80,
            'market_odd': 1.40,
            'fair_odd': 1.25,
            'ev_pct': 12.0,
            'stake_units': 1.0,
            'score': 0.70,
            'ranking_score': 0.70,
            'contextual_fit': 1.40,
            'reason': 'Contexto favorável',
        }
        selected = {
            'market': 'under_2.5',
            'market_display': 'Under 2.5',
            'pick': 'Under',
            'probability': 0.72,
            'market_odd': 1.45,
            'fair_odd': 1.39,
            'ev_pct': 4.0,
            'stake_units': 1.0,
            'score': 0.82,
            'ranking_score': 0.82,
            'contextual_fit': 1.05,
            'reason': 'Score integrado superior',
            'selection_eligible': True,
        }
        analyzer = AIAnalyzer.__new__(AIAnalyzer)
        decision_data = {
            'top_bets': [high_context, selected],
            'multiple_selection': selected,
            'confidence': {'stars': 4},
            'risk': 'medium',
            'model_probabilities': {'consensus': {}},
        }
        enriched_data = {'context_analysis': {}, 'model_probabilities': {}}

        with patch.object(analyzer, '_get_context_explanation', return_value='Jogo padrão'):
            result = analyzer._fallback_explanation(
                decision_data,
                enriched_data,
                strategy='multiple',
            )

        self.assertIn('Aposta: Under 2.5', result['analysis'])
        self.assertIn('Score integrado: 0.820', result['analysis'])