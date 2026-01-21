"""
Teste do decision_engine refatorado com múltiplas partidas REAIS
Valida acurácia da decisão objetiva vs resultados reais
"""
import os
import sys
import django
import json

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
django.setup()

from apps.analysis.services.decision_engine import DecisionEngine

# Carregar dados de validação
with open('validation_orchestrator_20260117_030739.json', 'r', encoding='utf-8') as f:
    validation_data = json.load(f)

# Selecionar 50 partidas para teste
test_matches = validation_data['detailed_results'][:50]

print("="*80)
print("TESTE: DECISION ENGINE REFATORADO - MULTIPLAS PARTIDAS")
print("="*80)
print(f"\nTestando com {len(test_matches)} partidas reais")
print()

engine = DecisionEngine()
correct_predictions = 0
total_predictions = 0

for i, match in enumerate(test_matches, 1):
    home = match['home']
    away = match['away']
    score = match['score']
    consensus = match['consensus']
    
    # Determinar resultado real
    h, a = map(int, score.split('-'))
    if h > a:
        actual_result = 'home_win'
    elif a > h:
        actual_result = 'away_win'
    else:
        actual_result = 'draw'
    
    # Mock predictions
    model_predictions = {
        'consensus': consensus,
        'poisson': {
            'expected_goals': {
                'home': consensus['home_win'] * 2.5,
                'away': consensus['away_win'] * 2.5
            },
            'most_likely_score': '1-1',
            'probabilities': {
                'over_1_5': 0.70,
                'under_1_5': 0.30,
                'over_2_5': 0.45,
                'under_2_5': 0.55,
                'over_3_5': 0.25,
                'under_3_5': 0.75,
                'btts': 0.50,
                'home_over_05': 0.85,
                'away_over_05': 0.85
            }
        }
    }
    
    # Mock market odds (usar fair odds como proxy)
    fair_odds = match.get('fair_odds', {})
    market_odds = {
        'odds_home': fair_odds.get('home_win', 2.5),
        'odds_draw': fair_odds.get('draw', 3.0),
        'odds_away': fair_odds.get('away_win', 2.8),
        'odds_over25': fair_odds.get('over_2_5', 2.0),
        'odds_under25': 1.9,
        'odds_btts': fair_odds.get('btts', 2.0)
    }
    
    # Mock features
    features = {
        'strength': {'strength_differential': 0.3},
        'form': {'form_differential': 0.2}
    }
    
    # Calcular confiança e risco
    confidence = engine._calculate_confidence(model_predictions, features)
    risk = engine._assess_risk(model_predictions, features, market_odds)
    
    # Selecionar top bets
    top_bets = engine.select_top_bets(model_predictions, market_odds, confidence, risk)
    
    if not top_bets:
        print(f"\n{i}. {home} vs {away}")
        print(f"   Resultado: {score}")
        print(f"   ERRO: Nenhuma aposta selecionada!")
        continue
    
    # Aposta #1 (mais provável)
    bet1 = top_bets[0]
    predicted_result = bet1['market']
    
    # Verificar acerto
    is_correct = predicted_result == actual_result
    if is_correct:
        correct_predictions += 1
    total_predictions += 1
    
    # Exibir
    prob_home = consensus['home_win'] * 100
    prob_draw = consensus['draw'] * 100
    prob_away = consensus['away_win'] * 100
    
    print(f"\n{i}. {home} vs {away}")
    print(f"   Resultado: {score} ({'Casa' if h > a else 'Fora' if a > h else 'Empate'})")
    print(f"   Probabilidades: Casa {prob_home:.1f}% | Empate {prob_draw:.1f}% | Fora {prob_away:.1f}%")
    print(f"   Predicao #1: {bet1['pick']} ({bet1['probability']*100:.1f}%) - EV: {bet1['ev_pct']:+.1f}%")
    print(f"   {'ACERTOU' if is_correct else 'ERROU'}")

# Estatísticas finais
print("\n" + "="*80)
print("RESULTADOS FINAIS")
print("="*80)
print(f"\nTotal de partidas: {total_predictions}")
print(f"Acertos: {correct_predictions}")
print(f"Erros: {total_predictions - correct_predictions}")
print(f"Acuracia: {(correct_predictions/total_predictions*100):.1f}%")

# Comparar com validação original
original_accuracy = validation_data['summary']['accuracy']
print(f"\nComparacao:")
print(f"  Acuracia ORIGINAL (IA decidindo): {original_accuracy:.1f}%")
print(f"  Acuracia NOVA (decisao objetiva): {(correct_predictions/total_predictions*100):.1f}%")
print(f"  Diferenca: {(correct_predictions/total_predictions*100) - original_accuracy:+.1f}%")

if (correct_predictions/total_predictions*100) > original_accuracy:
    print("\nMELHORIA! Decisao objetiva superou IA")
elif (correct_predictions/total_predictions*100) < original_accuracy:
    print("\nPIORA! Decisao objetiva abaixo da IA")
else:
    print("\nEMPATE! Mesma performance")

print()
