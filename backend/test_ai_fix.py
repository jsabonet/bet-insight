"""Teste rápido das correções no AI Analyzer"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.ai_analyzer import AIAnalyzer

# Mock data
decision_data = {
    'recommendation': {'pick': 'home_win', 'odd': 2.31, 'probability': 0.433, 'market': '1X2'},
    'confidence': {'stars': 4, 'score': 0.85},
    'risk': 'medium',
    'model_probabilities': {
        'consensus': {'home_win': 0.433, 'draw': 0.260, 'away_win': 0.306},
        'poisson': {
            'expected_goals': {'home': 1.45, 'away': 1.12},
            'most_likely_score': '1-1',
            'probabilities': {'over_2_5': 0.55, 'under_2_5': 0.45, 'btts': 0.62}
        }
    },
    'fair_odds': {'home_win': 2.31, 'draw': 3.85, 'away_win': 3.27},
    'value_bets': [
        {'market': '1X2 Casa', 'fair_odd': 2.31, 'market_odd': 2.50, 'value': 0.082}
    ]
}

enriched_data = {
    'fixture_details': {
        'teams': {'home': {'name': 'Fulham'}, 'away': {'name': 'Brighton'}},
        'league': {'name': 'Premier League'},
        'fixture': {'date': '2026-01-24T15:00:00Z'}
    }
}

analyzer = AIAnalyzer()
print('\n🔍 Testando fallback com dados corrigidos...\n')
result = analyzer._fallback_explanation(decision_data, enriched_data)

print(f'📊 Resultado:')
print(f'   Success: {result.get("success")}')
print(f'   Fallback: {result.get("fallback")}')
print(f'\n📝 Análise completa:')
print('='*80)
print(result.get('analysis', ''))
print('='*80)
