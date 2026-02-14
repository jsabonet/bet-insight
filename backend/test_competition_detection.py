#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste de detecção de competições - Champions League
"""
import sys
import os
import django

sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.feature_engineer import FeatureEngineer

print("="*80)
print("TESTE DE DETECCAO DE COMPETICOES")
print("="*80)

engineer = FeatureEngineer()

# Casos de teste
competitions = [
    "CAF Champions League",
    "UEFA Champions League",
    "Copa Libertadores",
    "Copa Sudamericana",
    "FA Cup",
    "Copa del Rey",
    "Premier League",  # Liga (não copa)
    "La Liga",  # Liga (não copa)
    "Serie A",  # Liga (não copa)
    "UEFA Super Cup",
    "Supercopa de España",
]

print("\nTESTES DE DETECCAO:")
print("-" * 80)

for comp_name in competitions:
    # Simular dados enriquecidos
    enriched = {
        'fixture_details': {
            'league': {
                'name': comp_name,
                'round': 'Round of 16'
            }
        }
    }
    
    result = engineer._calculate_competition_features(enriched)
    
    is_cup = result['is_cup_competition']
    is_knockout = result['is_knockout_stage']
    stage = result['round_stage']
    factor = result['knockout_adjustment_factor']
    
    symbol = "✅" if is_cup else "❌"
    comp_type = "COPA" if is_cup else "LIGA"
    
    print(f"{symbol} {comp_name:30s} = {comp_type}")
    print(f"   Knockout stage: {is_knockout}, Round: {stage}, Factor: {factor}")

print("\n" + "="*80)
print("RESULTADO ESPERADO:")
print("- Champions, Libertadores, Copa: Detectadas como COPA")
print("- Premier League, La Liga, Serie A: Detectadas como LIGA")
print("="*80)
