"""Teste com dados reais do Burnley vs Tottenham"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.ai_analyzer import AIAnalyzer

# Dados reais do jogo
decision_data = {
    'recommendation': {'pick': 'away_win', 'odd': 2.46, 'probability': 0.406, 'market': '1X2'},
    'confidence': {'stars': 4, 'score': 0.85},
    'risk': 'medium',
    'model_probabilities': {
        'consensus': {
            'home_win': 0.3224,  # 32.2%
            'draw': 0.2713,      # 27.1%
            'away_win': 0.4062   # 40.6% ← MAIOR
        },
        'poisson': {
            'expected_goals': {'home': 1.06, 'away': 1.40},
            'most_likely_score': '1-1',
            'probabilities': {
                'over_1_5': 0.68,
                'over_2_5': 0.42,
                'over_3_5': 0.22,
                'btts': 0.55,
                'home_over_05': 0.65,
                'away_over_05': 0.75
            }
        }
    },
    'fair_odds': {
        'home_win': 3.10,  # 1/0.3224
        'draw': 3.69,      # 1/0.2713
        'away_win': 2.46   # 1/0.4062
    },
    'value_bets': []  # Sem value bets
}

enriched_data = {
    'fixture_details': {
        'teams': {'home': {'name': 'Burnley'}, 'away': {'name': 'Tottenham'}},
        'league': {'name': 'Premier League'},
        'fixture': {'date': '2026-01-24T15:00:00Z'}
    }
}

analyzer = AIAnalyzer()

print('\n🔍 Testando correções...\n')

# Teste 1: Header
header = analyzer._generate_header(decision_data, enriched_data)
print('='*80)
print('TESTE 1: PREDIÇÃO NO HEADER')
print('='*80)
print(header)
print('='*80)

# Verificação
if 'PREDIÇÃO: Fora' in header:
    print('\n✅ CORRETO! Predição agora é "Fora" (40.6% > 32.2%)')
else:
    print('\n❌ ERRO! Predição ainda errada')

print('\n' + '='*80)
print('TESTE 2: DADOS NO PROMPT')
print('='*80)

# Teste 2: Prompt
from unittest.mock import MagicMock
mock_model = MagicMock()
analyzer.model = None  # Forçar fallback

result = analyzer._fallback_explanation(decision_data, enriched_data)
analysis = result['analysis']

# Verificações
print('\n✅ Verificações:')
if 'xG esperado: 1.06 x 1.40' in analysis:
    print('   ✅ xG correto')
else:
    print('   ❌ xG errado')

if 'Over 2.5:' in analysis or 'BTTS:' in analysis:
    print('   ✅ Mercados de gols presentes')
else:
    print('   ❌ Mercados de gols faltando')

if 'Fora' in header or 'Tottenham' in header:
    print('   ✅ Predição para Fora')
else:
    print('   ❌ Predição errada')

print('\n' + '='*80)
