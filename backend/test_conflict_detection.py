#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de detecção de conflitos entre mercados
"""
import sys
import os
import django

sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.market_selector import MarketSelector

print("="*80)
print("TESTE DE DETECAO DE CONFLITOS")
print("="*80)

selector = MarketSelector()

# Casos de teste
test_cases = [
    ('over_2.5', 'under_2.5', True, 'Over vs Under mesmo threshold'),
    ('over_1.5', 'under_2.5', False, 'Over vs Under threshold diferente'),
    ('home_win', 'away_win', True, 'Casa vs Fora'),
    ('home_win', 'draw', False, 'Casa vs Empate (nao conflita)'),
    ('btts_yes', 'btts_no', True, 'BTTS Yes vs No'),
    ('btts', 'btts_no', True, 'BTTS vs BTTS No'),
    ('12', 'draw', True, '12 vs Empate'),
    ('1x', '12', False, '1X vs 12 (nao conflita totalmente)'),
    ('home_clean_sheet', 'away_over_0.5', True, 'Clean sheet vs gols sofridos'),
    ('home_over_1.5', 'away_clean_sheet', True, 'Gols marcados vs clean sheet'),
    ('over_2.5', 'btts', False, 'Over 2.5 vs BTTS (nao conflita)'),
]

print("\nTESTES DE CONFLITO:")
print("-" * 80)

passed = 0
failed = 0

for market1, market2, expected, description in test_cases:
    result = selector._markets_conflict(market1, market2)
    status = "PASS" if result == expected else "FAIL"
    
    if result == expected:
        passed += 1
        symbol = "✅"
    else:
        failed += 1
        symbol = "❌"
    
    print(f"{symbol} {status}: {description}")
    print(f"   {market1} vs {market2} = {result} (esperado: {expected})")

print("\n" + "="*80)
print(f"RESULTADO: {passed} passed, {failed} failed")
print("="*80)

# Teste de remoção de conflitos
print("\n\nTESTE DE REMOCAO DE CONFLITOS:")
print("-" * 80)

candidates = [
    {'market': 'btts_yes', 'market_display': 'Ambos Marcam', 'probability': 0.542, 'selection_score': 0.542},
    {'market': 'under_2.5', 'market_display': 'Under 2.5', 'probability': 0.523, 'selection_score': 0.523},
    {'market': 'over_2.5', 'market_display': 'Over 2.5', 'probability': 0.477, 'selection_score': 0.477},
    {'market': 'home_win', 'market_display': 'Vitória Casa', 'probability': 0.324, 'selection_score': 0.324},
]

print("\nCandidatos originais:")
for c in candidates:
    print(f"  - {c['market_display']} ({c['probability']:.1%})")

conflict_free = selector._remove_conflicting_markets(candidates)

print("\nCandidatos sem conflitos:")
for c in conflict_free:
    print(f"  - {c['market_display']} ({c['probability']:.1%})")

print("\n" + "="*80)
