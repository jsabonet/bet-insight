"""
Teste do decision_engine refatorado - decisão OBJETIVA
"""
import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
django.setup()

from apps.analysis.services.decision_engine import DecisionEngine

# Mock data: Burnley vs Tottenham
model_predictions = {
    'consensus': {
        'home_win': 0.322,  # Burnley
        'draw': 0.272,
        'away_win': 0.406   # Tottenham (MAIOR)
    },
    'poisson': {
        'expected_goals': {
            'home': 1.2,
            'away': 1.5
        },
        'most_likely_score': '1-2',
        'probabilities': {
            'over_1_5': 0.746,
            'under_1_5': 0.254,
            'over_2_5': 0.478,
            'under_2_5': 0.522,
            'over_3_5': 0.261,
            'under_3_5': 0.739,
            'btts': 0.51,
            'home_over_05': 0.879,
            'away_over_05': 0.923
        }
    }
}

market_odds = {
    'odds_home': 3.70,  # Burnley
    'odds_draw': 3.50,
    'odds_away': 2.46,  # Tottenham
    'odds_over25': 2.10,
    'odds_under25': 1.85,
    'odds_btts': 2.00
}

# Mock features
features = {
    'strength': {'strength_differential': 0.4},
    'form': {'form_differential': 0.3}
}

engine = DecisionEngine()

# 1. Calcular confiança e risco
confidence = engine._calculate_confidence(model_predictions, features)
risk = engine._assess_risk(model_predictions, features, market_odds)

print("="*80)
print("TESTE: DECISION ENGINE REFATORADO")
print("="*80)
print(f"\nProbabilidades:")
print(f"   Burnley (Casa): {model_predictions['consensus']['home_win']*100:.1f}%")
print(f"   Empate: {model_predictions['consensus']['draw']*100:.1f}%")
print(f"   Tottenham (Fora): {model_predictions['consensus']['away_win']*100:.1f}%")

print(f"\nOdds do Mercado:")
print(f"   Burnley: {market_odds['odds_home']}")
print(f"   Tottenham: {market_odds['odds_away']}")

print(f"\nConfianca: {confidence['stars']}/5 ({confidence['level']})")
print(f"Risco: {risk.upper()}")

# 2. Selecionar top 3 apostas (DECISÃO OBJETIVA)
print(f"\n{'='*80}")
print("TOP 3 APOSTAS (DECISAO OBJETIVA - SEM IA)")
print("="*80)

top_bets = engine.select_top_bets(model_predictions, market_odds, confidence, risk)

for bet in top_bets:
    print(f"\n#{bet['rank']}: {bet['market_display']} - {bet['pick']}")
    print(f"   Probabilidade: {bet['probability']*100:.1f}%")
    print(f"   Odd mercado: {bet['market_odd']:.2f} | Fair: {bet['fair_odd']:.2f}")
    print(f"   EV: {bet['ev_pct']:+.1f}%")
    print(f"   Stake: {bet['stake_units']} unidades")
    print(f"   Score: {bet['score']:.3f}")
    print(f"   Razao: {bet['reason']}")

print(f"\n{'='*80}")
print("VERIFICACOES:")
print("="*80)

# Verificações
bet1 = top_bets[0] if top_bets else None

if bet1:
    if bet1['pick'] == 'Fora':  # Tottenham
        print("✅ Aposta #1 é o FAVORITO (Tottenham 40.6%)")
    elif bet1['pick'] == 'Casa':  # Burnley
        if bet1['ev_pct'] > 10:
            print("✅ Aposta #1 é UNDERDOG mas com ÓTIMO VALUE (+19% EV)")
        else:
            print("❌ ERRO: Aposta #1 é underdog sem value suficiente")
    
    # Verificar stake
    if risk == 'medium' and bet1['stake_units'] > 1.5:
        print(f"❌ ERRO: Stake {bet1['stake_units']}u excede máximo 1.5u para MEDIUM risk")
    else:
        print(f"✅ Stake {bet1['stake_units']}u está dentro do limite")
    
    # Verificar diversificação
    categories = [b.get('pick') for b in top_bets]
    if len(set([b['market'] for b in top_bets])) == len(top_bets):
        print(f"✅ Top 3 apostas são DIVERSIFICADAS (mercados diferentes)")
    else:
        print(f"⚠️ Top 3 apostas têm mercados repetidos")

print()
