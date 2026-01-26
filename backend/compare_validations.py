"""
Comparar consensos: validation_100_matches vs validation_with_orchestrator
"""
import json
from pathlib import Path

# Carregar ambos resultados
backend_path = Path(__file__).parent
root_path = backend_path.parent.parent

# validation_100_matches (ensemble isolado)
val_100_path = backend_path / 'validation_results_100_matches.json'
with open(val_100_path, encoding='utf-8') as f:
    val_100 = json.load(f)

# validation_orchestrator (sistema completo)
val_orch_path = root_path / 'validation_orchestrator_20260125_141448.json'
with open(val_orch_path, encoding='utf-8') as f:
    val_orch = json.load(f)

# Comparar primeira partida
match1_100 = val_100['detailed_results'][0]
match1_orch = val_orch['detailed_results'][0]

print("="*80)
print("COMPARAÇÃO: validation_100_matches vs validation_orchestrator")
print("="*80)
print(f"\nPrimeira partida (ID {match1_100['match_id']}):")
print(f"  {match1_100['home_team']} {match1_100['score']} {match1_100['away_team']}")
print(f"  Resultado real: {match1_100['actual']}")

print(f"\nvalidation_100_matches (Ensemble isolado):")
print(f"  Consensus HOME: {match1_100['ensemble_probs']['home_win']:.4f}")
print(f"  Consensus DRAW: {match1_100['ensemble_probs']['draw']:.4f}")
print(f"  Consensus AWAY: {match1_100['ensemble_probs']['away_win']:.4f}")
print(f"  Previsão: {match1_100['predicted']}")
print(f"  Correto: {match1_100['correct']}")

print(f"\nvalidation_orchestrator (Sistema completo):")
print(f"  Consensus HOME: {match1_orch['consensus']['home_win']:.4f}")
print(f"  Consensus DRAW: {match1_orch['consensus']['draw']:.4f}")
print(f"  Consensus AWAY: {match1_orch['consensus']['away_win']:.4f}")
print(f"  Previsão: {match1_orch['predicted']}")
print(f"  Correto: {match1_orch['correct']}")

print(f"\n{'='*80}")
print("DIFERENÇAS:")
print("="*80)
print(f"HOME: {abs(match1_100['ensemble_probs']['home_win'] - match1_orch['consensus']['home_win']):.6f}")
print(f"DRAW: {abs(match1_100['ensemble_probs']['draw'] - match1_orch['consensus']['draw']):.6f}")
print(f"AWAY: {abs(match1_100['ensemble_probs']['away_win'] - match1_orch['consensus']['away_win']):.6f}")
print(f"\nPrevisões match: {match1_100['predicted'] == match1_orch['predicted']}")

# Estatísticas gerais
print(f"\n{'='*80}")
print("ESTATÍSTICAS GERAIS:")
print("="*80)
print(f"\nvalidation_100_matches:")
print(f"  Total: {len(val_100['detailed_results'])} partidas")
print(f"  Corretos: {sum(1 for r in val_100['detailed_results'] if r['correct'])}")
print(f"  Acurácia: {val_100['summary']['accuracy']:.2f}%")
print(f"  Distribuição previsões:")
print(f"    HOME: {sum(1 for r in val_100['detailed_results'] if r['predicted'] == 'HOME')}")
print(f"    DRAW: {sum(1 for r in val_100['detailed_results'] if r['predicted'] == 'DRAW')}")
print(f"    AWAY: {sum(1 for r in val_100['detailed_results'] if r['predicted'] == 'AWAY')}")

print(f"\nvalidation_orchestrator:")
print(f"  Total: {val_orch['metadata']['total_matches']} partidas")
print(f"  Corretos: {val_orch['summary']['by_confidence']['4']['correct']}")
print(f"  Acurácia: {val_orch['summary']['accuracy']:.2f}%")
print(f"  Distribuição previsões:")
predicted_counts = {}
for r in val_orch['detailed_results']:
    pred = r['predicted']
    predicted_counts[pred] = predicted_counts.get(pred, 0) + 1
print(f"    HOME: {predicted_counts.get('home', 0)}")
print(f"    DRAW: {predicted_counts.get('draw', 0)}")
print(f"    AWAY: {predicted_counts.get('away', 0)}")
