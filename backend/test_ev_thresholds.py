"""
Teste específico para validar EV thresholds e cálculo dinâmico de stake
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.ai_analyzer import AIAnalyzer

def test_scenario(name, decision_data, enriched_data):
    print(f"\n{'='*80}")
    print(f"CENÁRIO: {name}")
    print(f"{'='*80}")
    
    ai = AIAnalyzer()
    result = ai.explain_decision(decision_data, enriched_data)
    
    # Extrai informações-chave do resultado
    print(f"\n📊 DADOS DO TESTE:")
    print(f"   Confiança: {decision_data['confidence']['stars']}/5")
    print(f"   Risco: {decision_data['risk']}")
    
    # Value bets
    for vb in decision_data.get('value_bets', []):
        ev_pct = vb['value'] * 100
        print(f"   {vb['market_display']}: EV = +{ev_pct:.1f}%")
    
    print(f"\n📝 ANÁLISE DA IA:")
    reasoning = result.get('reasoning', '')
    
    # Verifica se contém warnings de EV marginal
    if '⚠️ MARGINAL' in reasoning:
        print("   ⚠️ AI identificou EV MARGINAL")
    if '✅ SÓLIDA' in reasoning or 'EV sólido' in reasoning.lower():
        print("   ✅ AI identificou EV SÓLIDO")
    
    # Mostra primeira aposta recomendada
    if '🥇 APOSTA #1' in reasoning:
        lines = reasoning.split('\n')
        in_bet1 = False
        bet1_lines = []
        for line in lines:
            if '🥇 APOSTA #1' in line:
                in_bet1 = True
            elif '🥈 APOSTA #2' in line or '⛔ NÃO APOSTE' in line:
                break
            elif in_bet1:
                bet1_lines.append(line)
        
        print("\n   APOSTA #1:")
        for line in bet1_lines[:15]:  # Primeiras 15 linhas
            if line.strip():
                print(f"   {line}")


# ============================================================
# CENÁRIO 1: MEDIUM risk com EV MARGINAL (+1.8%, abaixo de 4%)
# ============================================================
print("\n" + "="*80)
print("🧪 TESTE: EV THRESHOLDS E DYNAMIC STAKE")
print("="*80)

scenario1_decision = {
    'recommendation': {
        'market': 'double_chance_x2',
        'pick': 'X2',
        'probability': 0.67,
        'odd': 1.52,
        'fair_odd': 1.49,
        'expected_value': 0.018,  # +1.8% (abaixo de 4% = MARGINAL)
        'market_display': 'Dupla Chance X2'
    },
    'confidence': {
        'level': 'medium',
        'stars': 3,
        'score': 0.62,
        'explanation': 'Consenso entre modelos médio'
    },
    'risk': 'medium',
    'model_probabilities': {
        'poisson': {
            'expected_goals_home': 1.15,
            'expected_goals_away': 1.25,
            'most_likely_score': '1-1',
            'probabilities': {
                'home_win': 0.329,
                'draw': 0.306,
                'away_win': 0.364,
                'over_2_5': 0.42,
                'btts': 0.51
            }
        },
        'consensus': {
            'home_win': 0.329,
            'draw': 0.306,
            'away_win': 0.364
        }
    },
    'fair_odds': {
        'home_win': 3.04,
        'draw': 3.27,
        'away_win': 2.75,
        'double_chance_x2': 1.49,
        'over_2_5': 2.38,
        'btts': 1.96
    },
    'value_bets': [
        {
            'market': 'double_chance_x2',
            'market_display': 'Dupla Chance X2',
            'fair_odd': 1.49,
            'market_odd': 1.52,
            'value': 0.018,  # +1.8%
            'probability': 0.67
        }
    ]
}

scenario1_enriched = {
    'fixture_details': {
        'teams': {
            'home': {'name': 'Mallorca', 'id': 532},
            'away': {'name': 'Rayo Vallecano', 'id': 728}
        },
        'league': {'name': 'La Liga', 'country': 'Spain'},
        'fixture': {'date': '2026-01-12T15:00:00+00:00'}
    },
    'table_context': {
        'home': {'position': 8, 'form': 'LWDWL'},
        'away': {'position': 11, 'form': 'DWLLW'}
    },
    'odds': {
        'home_win': 2.20,
        'draw': 3.20,
        'away_win': 2.75,
        'double_chance_x2': 1.52,
        'over_2_5': 2.10,
        'btts': 1.80
    }
}

test_scenario("EV MARGINAL - MEDIUM risk (+1.8% < 4%)", scenario1_decision, scenario1_enriched)


# ============================================================
# CENÁRIO 2: MEDIUM risk com EV SÓLIDO (+5.2%, acima de 4%)
# ============================================================

scenario2_decision = {
    'recommendation': {
        'market': 'away_dnb',
        'pick': 'Barcelona',
        'probability': 0.632,
        'odd': 1.88,
        'fair_odd': 1.58,
        'expected_value': 0.052,  # +5.2% (acima de 4% = SÓLIDO)
        'market_display': 'Draw No Bet Barcelona'
    },
    'confidence': {
        'level': 'high',
        'stars': 4,
        'score': 0.78,
        'explanation': 'Consenso entre modelos alto, Barcelona favorito claro'
    },
    'risk': 'medium',
    'model_probabilities': {
        'poisson': {
            'expected_goals_home': 0.95,
            'expected_goals_away': 1.85,
            'most_likely_score': '1-2',
            'probabilities': {
                'home_win': 0.248,
                'draw': 0.120,
                'away_win': 0.632,
                'over_2_5': 0.58,
                'btts': 0.62
            }
        },
        'consensus': {
            'home_win': 0.248,
            'draw': 0.120,
            'away_win': 0.632
        }
    },
    'fair_odds': {
        'home_win': 4.03,
        'draw': 8.33,
        'away_win': 1.58,
        'away_dnb': 1.58,
        'over_2_5': 1.72,
        'btts': 1.61
    },
    'value_bets': [
        {
            'market': 'away_dnb',
            'market_display': 'Draw No Bet Barcelona',
            'fair_odd': 1.58,
            'market_odd': 1.88,
            'value': 0.052,  # +5.2%
            'probability': 0.632
        },
        {
            'market': 'away_win',
            'market_display': 'Vitória Fora',
            'fair_odd': 1.58,
            'market_odd': 1.65,
            'value': 0.024,  # +2.4%
            'probability': 0.632
        }
    ]
}

scenario2_enriched = {
    'fixture_details': {
        'teams': {
            'home': {'name': 'Getafe', 'id': 546},
            'away': {'name': 'Barcelona', 'id': 529}
        },
        'league': {'name': 'La Liga', 'country': 'Spain'},
        'fixture': {'date': '2026-01-13T20:00:00+00:00'}
    },
    'table_context': {
        'home': {'position': 17, 'form': 'LLLLD'},
        'away': {'position': 1, 'form': 'WWWWW'}
    },
    'odds': {
        'home_win': 5.50,
        'draw': 4.20,
        'away_win': 1.65,
        'away_dnb': 1.88,
        'over_2_5': 1.90,
        'btts': 1.75
    }
}

test_scenario("EV SÓLIDO - MEDIUM risk (+5.2% > 4%)", scenario2_decision, scenario2_enriched)


# ============================================================
# CENÁRIO 3: HIGH risk com EV alto (+8.5%, mas risco elevado)
# ============================================================

scenario3_decision = {
    'recommendation': {
        'market': 'home_win',
        'pick': 'Real Madrid',
        'probability': 0.458,
        'odd': 2.55,
        'fair_odd': 2.18,
        'expected_value': 0.085,  # +8.5% (acima de 6%)
        'market_display': 'Vitória Casa'
    },
    'confidence': {
        'level': 'medium',
        'stars': 3,
        'score': 0.65,
        'explanation': 'Jogo equilibrado com ligeira vantagem Real Madrid'
    },
    'risk': 'high',  # HIGH risk = precisa EV > 6%
    'model_probabilities': {
        'poisson': {
            'expected_goals_home': 1.65,
            'expected_goals_away': 1.45,
            'most_likely_score': '2-1',
            'probabilities': {
                'home_win': 0.458,
                'draw': 0.285,
                'away_win': 0.257,
                'over_2_5': 0.62,
                'btts': 0.68
            }
        },
        'consensus': {
            'home_win': 0.458,
            'draw': 0.285,
            'away_win': 0.257
        }
    },
    'fair_odds': {
        'home_win': 2.18,
        'draw': 3.51,
        'away_win': 3.89,
        'over_2_5': 1.61,
        'btts': 1.47
    },
    'value_bets': [
        {
            'market': 'home_win',
            'market_display': 'Vitória Casa',
            'fair_odd': 2.18,
            'market_odd': 2.55,
            'value': 0.085,  # +8.5%
            'probability': 0.458
        }
    ]
}

scenario3_enriched = {
    'fixture_details': {
        'teams': {
            'home': {'name': 'Real Madrid', 'id': 541},
            'away': {'name': 'Atlético Madrid', 'id': 530}
        },
        'league': {'name': 'La Liga', 'country': 'Spain'},
        'fixture': {'date': '2026-01-14T21:00:00+00:00'}
    },
    'table_context': {
        'home': {'position': 2, 'form': 'WWDWL'},
        'away': {'position': 3, 'form': 'WWLWD'}
    },
    'odds': {
        'home_win': 2.55,
        'draw': 3.40,
        'away_win': 3.00,
        'over_2_5': 1.70,
        'btts': 1.60
    }
}

test_scenario("EV ALTO - HIGH risk (+8.5% > 6%)", scenario3_decision, scenario3_enriched)

print("\n" + "="*80)
print("✅ TESTES CONCLUÍDOS")
print("="*80)
print("\nVERIFICAÇÕES:")
print("1. ⚠️ MARGINAL aparece quando EV < threshold?")
print("2. ✅ SÓLIDA aparece quando EV > threshold?")
print("3. Stake = 0 para EV marginal?")
print("4. Stake calculado para EV sólido?")
print("5. Fórmula do stake explicada?")
