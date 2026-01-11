#!/usr/bin/env python
"""Teste completo de geração do prompt e chamada da IA"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.ai_analyzer import AIAnalyzer

# Dados de teste
decision_data = {
    'recommendation': {
        'market': 'Match Winner',
        'market_display': 'Match Winner (1X2)',
        'pick': 'Vitória Fora',
        'probability': 0.504,
        'odd': 1.90
    },
    'confidence': {
        'level': 'high',
        'level_pt': 'Alta',
        'stars': 4
    },
    'risk': 'medium',
    'value_bets': [
        {
            'market': 'Match Winner',
            'value_pct': 5.3,
            'fair_odd': 1.98,
            'market_odd': 1.90
        }
    ],
    'model_probabilities': {
        'poisson': {
            'expected_goals_home': 1.2,
            'expected_goals_away': 1.8,
            'most_likely_score': '1-2'
        },
        'consensus': {
            'home_win': 0.32,
            'draw': 0.17,
            'away_win': 0.504
        }
    }
}

enriched_data = {
    'fixture_details': {
        'home_team': {'name': 'Rayo Vallecano'},
        'away_team': {'name': 'Mallorca'},
        'league': {'name': 'La Liga'},
        'date': '2026-01-11T13:00:00+00:00'
    },
    'table_context': {
        'home': {'position': 15, 'points': 19},
        'away': {'position': 17, 'points': 18}
    },
    'motivation': {'context': 'Normal'},
    'trends': {}
}

print("TESTE COMPLETO DA IA DECISORIA")
print("="*80)

try:
    analyzer = AIAnalyzer()
    print("✅ AIAnalyzer inicializado")
    
    print("\n📝 Chamando explain_decision()...")
    result = analyzer.explain_decision(decision_data, enriched_data)
    
    print(f"\n✅ Resultado recebido!")
    print(f"   Success: {result.get('success')}")
    print(f"   Cached: {result.get('cached', False)}")
    print(f"   Tamanho reasoning: {len(result.get('reasoning', ''))} chars")
    
    print("\n" + "="*80)
    print("📄 REASONING COMPLETO:")
    print("="*80)
    print(result.get('reasoning', 'NULL'))
    print("="*80)
    
    # Verificar formato
    reasoning = result.get('reasoning', '')
    checks = {
        'Tem HTML?': '<h3>' in reasoning or '<p>' in reasoning,
        'Tem DECISÃO?': '➡️ DECISÃO' in reasoning or 'DECISÃO:' in reasoning,
        'Tem Fair odd?': 'Fair odd' in reasoning,
        'Tem Odd mínima?': 'Odd mínima' in reasoning,
        'Formato decisório?': '📌' in reasoning
    }
    
    print("\n✅ VERIFICAÇÕES:")
    for check, status in checks.items():
        icon = '❌' if ('HTML' in check and status) else ('✅' if status else '❌')
        print(f"   {icon} {check}: {status}")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
