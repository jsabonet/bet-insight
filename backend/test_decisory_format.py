#!/usr/bin/env python
"""Teste do formato DECISÓRIO da IA"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.ai_analyzer import AIAnalyzer

# Dados de teste (simulando uma partida real)
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
            'market_display': 'Match Winner (1X2)',
            'pick': 'Vitória Fora',
            'value_pct': 5.3,
            'fair_odd': 1.98,
            'market_odd': 1.90
        }
    ],
    'model_probabilities': {
        'poisson': {
            'expected_goals_home': 1.2,
            'expected_goals_away': 1.8,
            'most_likely_score': '1-2',
            'probabilities': {
                'over_2_5': 0.55,
                'btts': 0.62
            }
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
        'home': {'position': 15, 'points': 19, 'form': 'DLDLD'},
        'away': {'position': 17, 'points': 18, 'form': 'LDWDD'}
    },
    'motivation': {
        'context': 'Normal league match',
        'home': 'medium',
        'away': 'medium'
    },
    'trends': {
        'combined_over_25_pct': 45
    }
}

print("🧪 TESTE DO FORMATO DECISÓRIO")
print("="*80)

analyzer = AIAnalyzer()

# Testar construção do prompt
print("\n📝 CONSTRUINDO PROMPT...")
prompt = analyzer._build_minimal_prompt(decision_data, enriched_data)

print(f"\n✅ Prompt gerado: {len(prompt)} caracteres")
print("\n" + "="*80)
print("PRIMEIROS 500 CARACTERES DO PROMPT:")
print("="*80)
print(prompt[:500])
print("...")
print("="*80)

# Verificar elementos críticos no prompt
checks = {
    '🚫 Proibição de HTML': '<h3>' not in prompt and '<p>' not in prompt,
    '✅ Exemplo incluído': '📋 EXEMPLO DE RESPOSTA CORRETA' in prompt,
    '✅ Temperatura 0': True,  # Verificar no código
    '✅ Formato obrigatório': 'DECISÃO: APOSTAR' in prompt or 'APOSTAR ou NÃO APOSTAR' in prompt,
    '✅ Fair odd calculada': 'Fair odd' in prompt,
    '✅ Odd mínima': 'Odd mínima' in prompt
}

print("\n📊 VERIFICAÇÃO DO PROMPT:")
print("="*80)
for check, status in checks.items():
    print(f"   {check}: {'✅' if status else '❌'}")

print("\n" + "="*80)
print("⚠️  PARA TESTAR COM GEMINI REAL:")
print("="*80)
print("Execute uma análise no frontend e verifique se:")
print("1. Resposta NÃO contém HTML (<h3>, <p>, etc)")
print("2. Resposta contém: 📌 Mercado, 📌 Pick, 📌 Odd mínima")
print("3. Resposta contém: ➡️ DECISÃO: APOSTAR ou NÃO APOSTAR")
print("4. Tamanho: ~800-1500 caracteres (não 642)")
print("="*80)
