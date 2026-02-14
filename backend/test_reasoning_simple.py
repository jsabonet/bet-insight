#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste simples de reasoning - Match 1388498
"""
import os
import sys
import django

sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.market_selector import MarketSelector

# Test reasoning generation with neutral context (1.0)
selector = MarketSelector()

print("="*80)
print("TESTE DE REASONING - Context Score vs Output")
print("="*80)

# Test 1: Neutral context (1.0) + Alta probabilidade (84%)
reasoning1 = selector._generate_reasoning(
    market='1x',
    context_score=1.0,
    probability=0.84,
    supporting_patterns=[],
    all_patterns=[]
)
print(f"\n1. Context 1.0 (NEUTRO) + Prob 84%:")
print(f"   {reasoning1}")

# Test 2: Strong context (0.85) + Alta probabilidade (79%)
reasoning2 = selector._generate_reasoning(
    market='over_2.5',
    context_score=0.85,
    probability=0.79,
    supporting_patterns=[],
    all_patterns=[]
)
print(f"\n2. Context 0.85 (FORTE) + Prob 79%:")
print(f"   {reasoning2}")

# Test 3: Neutral context (1.0) + Boa probabilidade (63%)
reasoning3 = selector._generate_reasoning(
    market='btts',
    context_score=1.0,
    probability=0.63,
    supporting_patterns=[],
    all_patterns=[]
)
print(f"\n3. Context 1.0 (NEUTRO) + Prob 63%:")
print(f"   {reasoning3}")

# Test 4: Context 0.75 (limiar) + Probabilidade 52%
reasoning4 = selector._generate_reasoning(
    market='12',
    context_score=0.75,
    probability=0.52,
    supporting_patterns=[],
    all_patterns=[]
)
print(f"\n4. Context 0.75 (FORTE limiar) + Prob 52%:")
print(f"   {reasoning4}")

# Test 5: Context 0.99 (quase 1.0, deve ser NEUTRO) + Prob 78%
reasoning5 = selector._generate_reasoning(
    market='over_1.5',
    context_score=0.99,
    probability=0.78,
    supporting_patterns=[],
    all_patterns=[]
)
print(f"\n5. Context 0.99 (NEUTRO) + Prob 78%:")
print(f"   {reasoning5}")

print("\n" + "="*80)
print("RESULTADO ESPERADO:")
print("- Contexts 1.0 e 0.99: Foco em probabilidade, SEM mencionar contexto")
print("- Context 0.85 e 0.75: Menciona contexto forte + probabilidade")
print("="*80)
