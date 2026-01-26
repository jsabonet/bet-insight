import json
from pathlib import Path

# Carregar resultado do orchestrator
orch_path = Path(__file__).parent.parent.parent / 'validation_orchestrator_20260125_141448.json'
with open(orch_path, encoding='utf-8') as f:
    orch_data = json.load(f)

# Primeira partida
r = orch_data['detailed_results'][0]

print(f"Orchestrator consensus para match {r['id']}:")
print(f"HOME: {r['consensus']['home_win']:.4f}")
print(f"DRAW: {r['consensus']['draw']:.4f}")
print(f"AWAY: {r['consensus']['away_win']:.4f}")
print(f"\nPredicted: {r['predicted']}")
print(f"Predicted vector: {r['predicted_vector']}")
print(f"Actual: {r['actual']}")
print(f"Score: {r['score']}")
print(f"Correct: {r['correct']}")
print(f"\nConfidence: {r['confidence']}")

# Carregar resultado do decision_engine_analysis para comparação
dec_path = Path(__file__).parent.parent.parent / 'decision_engine_analysis.json'
with open(dec_path, encoding='utf-8') as f:
    dec_data = json.load(f)

# Encontrar a mesma partida
match_id = r['id']
match_found = False
for detail in dec_data['detailed_comparisons']:
    if detail['match_id'] == match_id:
        match_found = True
        print(f"\n{'='*60}")
        print("Decision Engine Analysis para MESMA partida:")
        print(f"Ensemble probs: {detail['ensemble_probs']}")
        print(f"Decision probs: {detail['decision_probs']}")
        print(f"Ensemble pred: {detail['ensemble_pred']}")
        print(f"Decision pred: {detail['decision_pred']}")
        print(f"Actual: {detail['actual']}")
        print(f"Ensemble correct: {detail['ensemble_correct']}")
        print(f"Decision correct: {detail['decision_correct']}")
        break

if not match_found:
    print(f"\n❌ Match {match_id} NÃO encontrado no decision_engine_analysis.json")
