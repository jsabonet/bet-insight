"""
Testes para garantir que IA NÃO CONTRADIZ decisões
"""
import pytest
from apps.analysis.services.ai_analyzer import AIAnalyzer
from apps.analysis.services.ai_helpers import parse_and_validate_response


class TestAINoContradiction:
    """Testes anti-contradição"""
    
    def setup_method(self):
        self.analyzer = AIAnalyzer()
    
    def test_ai_never_returns_new_odds(self):
        """IA nunca deve sugerir odds diferentes"""
        decision_data = {
            'recommendation': {
                'pick': 'Home Win',
                'market_display': 'Match Winner',
                'probability': 0.65,
                'odd': 1.85
            },
            'confidence': {'stars': 4, 'level_pt': 'Alta'},
            'risk': 'low',
            'model_probabilities': {
                'poisson': {
                    'expected_goals_home': 2.1,
                    'expected_goals_away': 0.9,
                    'most_likely_score': '2-1'
                },
                'consensus': {
                    'home_win': 0.65,
                    'draw': 0.20,
                    'away_win': 0.15
                }
            }
        }
        
        enriched_data = {
            'fixture_details': {
                'home_team': {'name': 'Team A'},
                'away_team': {'name': 'Team B'},
                'date': '2026-01-11'
            },
            'table_context': {},
            'motivation': {},
            'trends': {}
        }
        
        result = self.analyzer.explain_decision(decision_data, enriched_data)
        
        assert result['success'] == True
        
        # IA NÃO PODE mencionar odds diferentes
        response_text = result.get('analysis', '') + result.get('reasoning', '')
        response_lower = response_text.lower()
        
        # Verificar que não sugere outras odds
        forbidden_phrases = ['odd de', 'deveria ser', 'melhor odd', 'considere', 'ou talvez']
        for phrase in forbidden_phrases:
            assert phrase not in response_lower, f"IA sugeriu odds alternativas: '{phrase}'"
    
    def test_ai_never_changes_probability(self):
        """IA nunca deve sugerir probabilidades diferentes"""
        decision_data = {
            'recommendation': {
                'pick': 'Over 2.5',
                'probability': 0.58
            },
            'confidence': {'stars': 3, 'level_pt': 'Média'},
            'risk': 'medium',
            'model_probabilities': {
                'poisson': {
                    'expected_goals_home': 1.5,
                    'expected_goals_away': 1.3
                },
                'consensus': {
                    'home_win': 0.35,
                    'draw': 0.28,
                    'away_win': 0.37
                }
            }
        }
        
        enriched_data = {
            'fixture_details': {
                'home_team': {'name': 'Team A'},
                'away_team': {'name': 'Team B'}
            }
        }
        
        result = self.analyzer.explain_decision(decision_data, enriched_data)
        
        # IA não pode mencionar probabilidades diferentes de 58%
        response_text = result.get('analysis', '') + result.get('reasoning', '')
        
        # Permitir apenas a probabilidade correta
        assert '58' in response_text or '58.0' in response_text
        
        # Proibir outras probabilidades altas
        forbidden_probs = ['70%', '75%', '80%', '85%', '90%']
        for prob in forbidden_probs:
            assert prob not in response_text, f"IA mencionou probabilidade errada: {prob}"
    
    def test_ai_never_suggests_different_market(self):
        """IA nunca deve sugerir mercados diferentes"""
        decision_data = {
            'recommendation': {
                'pick': 'Home Win',
                'market_display': 'Match Winner'
            },
            'confidence': {'stars': 4},
            'risk': 'low',
            'model_probabilities': {
                'poisson': {'expected_goals_home': 2.0, 'expected_goals_away': 1.0},
                'consensus': {'home_win': 0.60, 'draw': 0.25, 'away_win': 0.15}
            }
        }
        
        enriched_data = {
            'fixture_details': {
                'home_team': {'name': 'Team A'},
                'away_team': {'name': 'Team B'}
            }
        }
        
        result = self.analyzer.explain_decision(decision_data, enriched_data)
        
        response_text = result.get('analysis', '').lower()
        
        # Proibir sugestões de outros mercados
        forbidden = ['btts', 'over', 'under', 'alternativa', 'também', 'considere']
        for word in forbidden:
            assert word not in response_text, f"IA sugeriu mercado alternativo: '{word}'"
    
    def test_response_format_validation(self):
        """Valida que resposta tem formato fixo"""
        mock_response = """
RESUMO: Team A tem vantagem clara com 65% de probabilidade.

FATORES:
• Expected goals favorecem casa (2.1 vs 0.9)
• Time da casa em boa forma recente
• Histórico favorável em confrontos diretos

RISCO: Risco baixo - recomendado para apostadores conservadores.
"""
        
        parsed = parse_and_validate_response(mock_response)
        
        assert parsed['valid'] == True
        assert len(parsed['summary']) <= 200
        assert 3 <= len(parsed['bullets']) <= 5
        assert len(parsed['risk_warning']) <= 150
    
    def test_fallback_when_ai_fails(self):
        """Fallback determinístico quando IA falha"""
        decision_data = {
            'recommendation': {
                'pick': 'Away Win',
                'probability': 0.55
            },
            'confidence': {'stars': 3, 'level_pt': 'Média'},
            'risk': 'medium',
            'model_probabilities': {
                'poisson': {
                    'expected_goals_home': 1.2,
                    'expected_goals_away': 1.8,
                    'most_likely_score': '1-2'
                },
                'consensus': {
                    'home_win': 0.30,
                    'draw': 0.15,
                    'away_win': 0.55
                }
            }
        }
        
        enriched_data = {
            'fixture_details': {
                'home_team': {'name': 'Team A'},
                'away_team': {'name': 'Team B'}
            }
        }
        
        result = self.analyzer._fallback_explanation(decision_data, enriched_data)
        
        assert result['success'] == True
        assert result['fallback'] == True
        assert 'reasoning' in result
        assert result['generation_time'] == 0.0
