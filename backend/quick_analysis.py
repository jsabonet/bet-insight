import json

data = json.load(open('validation_orchestrator_20260117_030739.json', 'r', encoding='utf-8'))  # BASELINE (44.35%)
matches = data['detailed_results']
total = len(matches)
correct = sum(1 for m in matches if m.get('correct', False))

# Converter actual array para string (home/draw/away)
def get_real_result(actual):
    if actual[0] == 1: return 'home'
    if actual[1] == 1: return 'draw'
    return 'away'

def get_prediction(predicted):
    if predicted == 'home': return 'home'
    if predicted == 'draw': return 'draw'
    return 'away'

acertos_casa = sum(1 for m in matches if m.get('correct', False) and get_real_result(m['actual']) == 'home')
acertos_empate = sum(1 for m in matches if m.get('correct', False) and get_real_result(m['actual']) == 'draw')
acertos_fora = sum(1 for m in matches if m.get('correct', False) and get_real_result(m['actual']) == 'away')

prev_casa = sum(1 for m in matches if get_prediction(m['predicted']) == 'home')
prev_empate = sum(1 for m in matches if get_prediction(m['predicted']) == 'draw')
prev_fora = sum(1 for m in matches if get_prediction(m['predicted']) == 'away')

real_casa = sum(1 for m in matches if get_real_result(m['actual']) == 'home')
real_empate = sum(1 for m in matches if get_real_result(m['actual']) == 'draw')
real_fora = sum(1 for m in matches if get_real_result(m['actual']) == 'away')

print(f"""
{"="*70}
VALIDAÇÃO COM PARÂMETROS CORRIGIDOS
{"="*70}
Total: {total} matches
Acurácia: {correct/total*100:.2f}% ({correct}/{total})

RESULTADOS REAIS:
  Casa: {real_casa} ({real_casa/total*100:.1f}%)
  Empate: {real_empate} ({real_empate/total*100:.1f}%)
  Fora: {real_fora} ({real_fora/total*100:.1f}%)

PREVISÕES DO MODELO:
  Casa: {prev_casa} ({prev_casa/total*100:.1f}%)
  Empate: {prev_empate} ({prev_empate/total*100:.1f}%)
  Fora: {prev_fora} ({prev_fora/total*100:.1f}%)

VIÉS (Modelo - Real):
  Casa: {(prev_casa-real_casa)/total*100:+.1f} pts
  Empate: {(prev_empate-real_empate)/total*100:+.1f} pts
  Fora: {(prev_fora-real_fora)/total*100:+.1f} pts

ACERTOS POR TIPO DE RESULTADO:
  Casa: {acertos_casa}/{real_casa} ({acertos_casa/real_casa*100 if real_casa > 0 else 0:.1f}%)
  Empate: {acertos_empate}/{real_empate} ({acertos_empate/real_empate*100 if real_empate > 0 else 0:.1f}%)
  Fora: {acertos_fora}/{real_fora} ({acertos_fora/real_fora*100 if real_fora > 0 else 0:.1f}%)
{"="*70}
""")

