"""
Análise detalhada: Por que a decisão objetiva não superou a IA?
"""
import json

with open('validation_orchestrator_20260117_030739.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Analisar primeiras 50 partidas
matches = data['detailed_results'][:50]

print("="*80)
print("ANALISE: DECISAO OBJETIVA vs IA ORIGINAL")
print("="*80)

# Contar casos onde:
# 1. Resultado mais provável != Predição original
# 2. Resultado mais provável acertou mas IA original errou
# 3. IA original acertou mas resultado mais provável errou

diff_predictions = 0
objective_right_ia_wrong = 0
ia_right_objective_wrong = 0

for match in matches:
    consensus = match['consensus']
    predicted_original = match['predicted']
    actual = match['actual']
    
    # Determinar resultado mais provável (nossa lógica objetiva)
    max_prob = max(consensus, key=consensus.get)
    
    # Converter para formato compatível
    result_map = {
        'home_win': 0,
        'draw': 1,
        'away_win': 2
    }
    
    predicted_objective_idx = result_map[max_prob]
    actual_idx = actual.index(1) if 1 in actual else -1
    
    # Converter predição original
    if predicted_original == 'home':
        predicted_original_idx = 0
    elif predicted_original == 'draw':
        predicted_original_idx = 1
    elif predicted_original == 'away':
        predicted_original_idx = 2
    else:
        predicted_original_idx = -1
    
    # Comparar
    if predicted_objective_idx != predicted_original_idx:
        diff_predictions += 1
        
        objective_correct = (predicted_objective_idx == actual_idx)
        ia_correct = (predicted_original_idx == actual_idx)
        
        if objective_correct and not ia_correct:
            objective_right_ia_wrong += 1
            print(f"\n{match['home']} vs {match['away']}")
            print(f"  Resultado: {match['score']}")
            print(f"  Prob: Casa {consensus['home_win']*100:.1f}% | Empate {consensus.get('draw', 0)*100:.1f}% | Fora {consensus['away_win']*100:.1f}%")
            print(f"  Objetivo: {max_prob} (ACERTOU)")
            print(f"  IA Original: {predicted_original} (ERROU)")
        
        elif ia_correct and not objective_correct:
            ia_right_objective_wrong += 1

print(f"\n{'='*80}")
print("RESUMO:")
print("="*80)
print(f"Total de partidas: {len(matches)}")
print(f"Predicoes diferentes: {diff_predictions}")
print(f"Objetivo acertou, IA errou: {objective_right_ia_wrong}")
print(f"IA acertou, Objetivo errou: {ia_right_objective_wrong}")

print(f"\nCONCLUSAO:")
if objective_right_ia_wrong > ia_right_objective_wrong:
    print("Decisao objetiva SERIA MELHOR se aplicada consistentemente")
elif ia_right_objective_wrong > objective_right_ia_wrong:
    print("IA original TEM INSIGHT além do resultado mais provável")
else:
    print("Ambas performam igualmente nos casos divergentes")
