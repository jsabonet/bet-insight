#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste específico: ES Tunis vs Petro de Luanda - CAF Champions League
Verifica se contexto de Champions League é detectado
"""
import sys
import os
import django

sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.context_analyzer import ContextAnalyzer

print("="*80)
print("TESTE: ES TUNIS vs PETRO DE LUANDA - CAF CHAMPIONS LEAGUE")
print("="*80)

# Simular dados enriquecidos
enriched_data = {
    'fixture_details': {
        'league': {
            'name': 'CAF Champions League',
            'round': 'Group Stage - 5',
            'season': 2025
        },
        'teams': {
            'home': {'name': 'ES Tunis'},
            'away': {'name': 'Petro de Luanda'}
        }
    },
    'home_stats': {
        'goals_per_game_avg': 1.4,
        'goals_conceded_avg': 0.9,
        'form_l5': 0.6
    },
    'away_stats': {
        'goals_per_game_avg': 1.1,
        'goals_conceded_avg': 1.2,
        'form_l5': 0.4
    },
    'context': {
        'home_rest_days': 5,
        'away_rest_days': 4
    },
    'motivation': {
        'home_motivation': 7,
        'away_motivation': 8
    },
    'injuries_suspensions': {
        'home_injury_impact': 0.1,
        'away_injury_impact': 0.15
    }
    # H2H removido para simplificar teste
}

# 1. Testar detecção de competição
print("\n1. DETECCAO DE COMPETICAO")
print("-" * 80)

engineer = FeatureEngineer()
comp_features = engineer._calculate_competition_features(enriched_data)

print(f"Nome: {comp_features['competition_name']}")
print(f"É Copa: {comp_features['is_cup_competition']}")
print(f"É Knockout: {comp_features['is_knockout_stage']}")
print(f"Fase: {comp_features['round_stage']}")
print(f"Fator de ajuste: {comp_features['knockout_adjustment_factor']}")

if comp_features['is_cup_competition']:
    print("\n✅ SUCESSO: CAF Champions League detectada como Copa!")
else:
    print("\n❌ ERRO: CAF Champions League NÃO foi detectada como Copa!")

# 2. Criar features completas
print("\n2. ENGINERING DE FEATURES")
print("-" * 80)

features = engineer.engineer_all_features(enriched_data)

print(f"Total de features criadas: {len(features)}")
print(f"Competition features: {features.get('competition', {})}")

# 3. Analisar contexto
print("\n3. CONTEXT ANALYZER")
print("-" * 80)

analyzer = ContextAnalyzer()
context_result = analyzer.analyze(features)

patterns = context_result.get('patterns', [])
top_markets = context_result.get('top_markets', [])

if patterns:
    print(f"\n✅ {len(patterns)} PADRAO(ES) DETECTADO(S):\n")
    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. {pattern['name'].upper()}")
        print(f"   Confianca: {pattern['confidence']:.0%}")
        print(f"   Mercados favorecidos: {', '.join(pattern['favorable_markets'][:5])}")
        print(f"   Reasoning: {pattern['reasoning']}")
        print()
else:
    print("\n❌ NENHUM PADRAO CONTEXTUAL DETECTADO")
    print("   Esperado: Padrões de Copa (must_win, knockout_upset, etc.)")

# 4. Top markets com contexto
print("\n4. TOP MARKETS COM CONTEXTO")
print("-" * 80)

if top_markets:
    print(f"\n✅ {len(top_markets)} mercados com contexto > 0:\n")
    for i, market in enumerate(top_markets[:10], 1):
        print(f"{i}. {market['market']:20s}: {market['context_score']:.0%}")
else:
    print("\n❌ Nenhum mercado com contexto detectado")

# 5. Resumo
print("\n" + "="*80)
print("RESUMO DO TESTE")
print("="*80)

if comp_features['is_cup_competition'] and patterns:
    print("✅ TESTE PASSOU:")
    print("   - CAF Champions League detectada como Copa")
    print(f"   - {len(patterns)} padrões contextuais detectados")
    print(f"   - {len(top_markets)} mercados com boost contextual")
    print("\n   Sistema agora considera contexto de Champions League!")
else:
    print("❌ TESTE FALHOU:")
    if not comp_features['is_cup_competition']:
        print("   - CAF Champions League NÃO detectada como Copa")
    if not patterns:
        print("   - Nenhum padrão contextual detectado")
    print("\n   Sistema ainda não reconhece contexto de Champions!")

print("="*80)
