"""
Validação com partidas finalizadas para medir acertividade real
Calcula métricas de performance antes do lançamento comercial
"""
import os
import sys
import django
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
import numpy as np

def calculate_brier_score(predicted_probs, actual_outcome):
    """
    Calcula Brier Score (quanto menor, melhor)
    actual_outcome: [1,0,0] para vitória casa, [0,1,0] para empate, [0,0,1] para vitória fora
    """
    probs = [predicted_probs.get('home_win', 0), 
             predicted_probs.get('draw', 0), 
             predicted_probs.get('away_win', 0)]
    return np.mean([(p - a)**2 for p, a in zip(probs, actual_outcome)])

def calculate_log_loss(predicted_probs, actual_outcome):
    """
    Calcula Log Loss (quanto menor, melhor)
    Penaliza previsões muito confiantes que estão erradas
    """
    probs = [predicted_probs.get('home_win', 0), 
             predicted_probs.get('draw', 0), 
             predicted_probs.get('away_win', 0)]
    
    # Evitar log(0)
    probs = [max(min(p, 0.9999), 0.0001) for p in probs]
    
    # Log loss para a classe correta
    for i, actual in enumerate(actual_outcome):
        if actual == 1:
            return -np.log(probs[i])
    return 0

def get_actual_outcome(match):
    """Retorna vetor one-hot do resultado real"""
    if match.home_score > match.away_score:
        return [1, 0, 0]  # Vitória casa
    elif match.home_score < match.away_score:
        return [0, 0, 1]  # Vitória fora
    else:
        return [0, 1, 0]  # Empate

def get_prediction_label(probs):
    """Retorna label da previsão (maior probabilidade)"""
    max_prob = max(probs.get('home_win', 0), probs.get('draw', 0), probs.get('away_win', 0))
    if probs.get('home_win', 0) == max_prob:
        return 'home_win'
    elif probs.get('draw', 0) == max_prob:
        return 'draw'
    else:
        return 'away_win'

def validate_prediction(probs, actual_outcome):
    """Verifica se a previsão estava correta"""
    prediction = get_prediction_label(probs)
    
    if prediction == 'home_win' and actual_outcome == [1, 0, 0]:
        return True
    elif prediction == 'draw' and actual_outcome == [0, 1, 0]:
        return True
    elif prediction == 'away_win' and actual_outcome == [0, 0, 1]:
        return True
    return False

print("\n" + "="*80)
print("VALIDAÇÃO COM PARTIDAS FINALIZADAS")
print("="*80)

# Buscar partidas finalizadas dos últimos 7 dias
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

print(f"\nBuscando partidas finalizadas entre {start_date.date()} e {end_date.date()}...")

matches = Match.objects.filter(
    match_date__gte=start_date,
    match_date__lte=end_date,
    status='FT',  # Full Time
    home_score__isnull=False,
    away_score__isnull=False
).select_related('home_team', 'away_team', 'league').order_by('-match_date')[:50]  # Limitar a 50 partidas

total_matches = matches.count()
print(f"Encontradas {total_matches} partidas finalizadas\n")

if total_matches == 0:
    print("ERRO: Nenhuma partida finalizada encontrada no período")
    sys.exit(1)

# Inicializar métricas
results = []
successful_analyses = 0
failed_analyses = 0

orchestrator = HybridAnalysisOrchestrator()

print("Executando análises...")
print("-" * 80)

for i, match in enumerate(matches, 1):
    print(f"\n[{i}/{total_matches}] {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name}")
    print(f"    Liga: {match.league.name} | Data: {match.match_date.strftime('%d/%m/%Y')}")
    
    try:
        # Executar análise
        result = orchestrator.analyze(match.api_football_id)
        
        if not result or 'model_probabilities' not in result:
            print("    ⚠️  Análise retornou dados incompletos")
            failed_analyses += 1
            continue
        
        # Extrair probabilidades
        consensus = result.get('model_probabilities', {}).get('consensus', {})
        
        if not consensus or not all(k in consensus for k in ['home_win', 'draw', 'away_win']):
            print("    ⚠️  Probabilidades incompletas")
            failed_analyses += 1
            continue
        
        # Obter resultado real
        actual_outcome = get_actual_outcome(match)
        
        # Calcular métricas
        brier = calculate_brier_score(consensus, actual_outcome)
        log_loss = calculate_log_loss(consensus, actual_outcome)
        correct = validate_prediction(consensus, actual_outcome)
        
        # Armazenar resultado
        results.append({
            'match': match,
            'predicted_probs': consensus,
            'actual_outcome': actual_outcome,
            'brier_score': brier,
            'log_loss': log_loss,
            'correct': correct
        })
        
        successful_analyses += 1
        
        # Mostrar previsão vs realidade
        outcome_labels = {
            '[1, 0, 0]': '1 (Casa)',
            '[0, 1, 0]': 'X (Empate)',
            '[0, 0, 1]': '2 (Fora)'
        }
        
        prediction = get_prediction_label(consensus)
        pred_labels = {
            'home_win': '1 (Casa)',
            'draw': 'X (Empate)',
            'away_win': '2 (Fora)'
        }
        
        print(f"    Previsão: {pred_labels[prediction]} "
              f"[Casa:{consensus['home_win']*100:.1f}% | "
              f"Empate:{consensus['draw']*100:.1f}% | "
              f"Fora:{consensus['away_win']*100:.1f}%]")
        print(f"    Resultado: {outcome_labels[str(actual_outcome)]}")
        print(f"    Status: {'✅ ACERTOU' if correct else '❌ ERROU'} | Brier: {brier:.4f} | Log Loss: {log_loss:.4f}")
        
    except Exception as e:
        print(f"    ❌ Erro na análise: {str(e)}")
        failed_analyses += 1
        continue

# Calcular métricas agregadas
print("\n" + "="*80)
print("RELATÓRIO DE MÉTRICAS")
print("="*80)

if not results:
    print("\nERRO: Nenhuma análise bem-sucedida")
    sys.exit(1)

accuracy = sum(1 for r in results if r['correct']) / len(results)
avg_brier = np.mean([r['brier_score'] for r in results])
avg_log_loss = np.mean([r['log_loss'] for r in results])

print(f"\nPartidas analisadas: {successful_analyses}/{total_matches}")
print(f"Análises falhadas: {failed_analyses}")

print("\n" + "-"*80)
print("MÉTRICAS DE ACERTIVIDADE:")
print("-"*80)
print(f"Accuracy (acertos diretos):  {accuracy*100:.1f}%")
print(f"Brier Score (média):         {avg_brier:.4f}  (ótimo: < 0.20, bom: < 0.25)")
print(f"Log Loss (média):            {avg_log_loss:.4f}  (ótimo: < 0.70, bom: < 1.00)")

# Análise por tipo de resultado
home_wins = [r for r in results if r['actual_outcome'] == [1, 0, 0]]
draws = [r for r in results if r['actual_outcome'] == [0, 1, 0]]
away_wins = [r for r in results if r['actual_outcome'] == [0, 0, 1]]

print("\n" + "-"*80)
print("ACERTIVIDADE POR TIPO DE RESULTADO:")
print("-"*80)

if home_wins:
    home_acc = sum(1 for r in home_wins if r['correct']) / len(home_wins)
    print(f"Vitórias Casa: {home_acc*100:.1f}% ({sum(1 for r in home_wins if r['correct'])}/{len(home_wins)})")

if draws:
    draw_acc = sum(1 for r in draws if r['correct']) / len(draws)
    print(f"Empates:       {draw_acc*100:.1f}% ({sum(1 for r in draws if r['correct'])}/{len(draws)})")

if away_wins:
    away_acc = sum(1 for r in away_wins if r['correct']) / len(away_wins)
    print(f"Vitórias Fora: {away_acc*100:.1f}% ({sum(1 for r in away_wins if r['correct'])}/{len(away_wins)})")

# Calibração (confiança vs acertividade)
print("\n" + "-"*80)
print("CALIBRAÇÃO (confiança da previsão vs acertividade):")
print("-"*80)

confidence_ranges = [
    (0.33, 0.45, "Baixa (33-45%)"),
    (0.45, 0.55, "Média (45-55%)"),
    (0.55, 0.70, "Alta (55-70%)"),
    (0.70, 1.00, "Muito Alta (70%+)")
]

for min_conf, max_conf, label in confidence_ranges:
    # Encontrar previsões nesse range de confiança
    in_range = []
    for r in results:
        max_prob = max(r['predicted_probs']['home_win'], 
                      r['predicted_probs']['draw'], 
                      r['predicted_probs']['away_win'])
        if min_conf <= max_prob < max_conf:
            in_range.append(r)
    
    if in_range:
        acc_in_range = sum(1 for r in in_range if r['correct']) / len(in_range)
        print(f"{label}: {acc_in_range*100:.1f}% acertividade ({len(in_range)} partidas)")

# Benchmark contra apostas aleatórias
random_accuracy = 1/3  # 33.3% para 3 resultados possíveis
improvement = (accuracy - random_accuracy) / random_accuracy * 100

print("\n" + "-"*80)
print("COMPARAÇÃO:")
print("-"*80)
print(f"Baseline (aleatório):    {random_accuracy*100:.1f}%")
print(f"Modelo atual:            {accuracy*100:.1f}%")
print(f"Melhoria:                {improvement:+.1f}%")

# Benchmark contra mercado (odds)
market_comparisons = []
for r in results:
    match = r['match']
    enriched = orchestrator.analyze(match.api_football_id).get('enriched_data', {})
    odds = enriched.get('odds', {})
    
    if all(k in odds for k in ['home_win', 'draw', 'away_win']):
        # Converter odds para probabilidades
        prob_home = 1 / odds['home_win']
        prob_draw = 1 / odds['draw']
        prob_away = 1 / odds['away_win']
        total = prob_home + prob_draw + prob_away
        
        # Normalizar
        market_probs = {
            'home_win': prob_home / total,
            'draw': prob_draw / total,
            'away_win': prob_away / total
        }
        
        # Verificar se mercado acertou
        market_correct = validate_prediction(market_probs, r['actual_outcome'])
        market_comparisons.append({
            'model_correct': r['correct'],
            'market_correct': market_correct
        })

if market_comparisons:
    market_accuracy = sum(1 for c in market_comparisons if c['market_correct']) / len(market_comparisons)
    print(f"\nMercado (odds):          {market_accuracy*100:.1f}%")
    
    # Casos onde modelo acerta e mercado erra
    model_wins = sum(1 for c in market_comparisons if c['model_correct'] and not c['market_correct'])
    print(f"Modelo acerta / Mercado erra: {model_wins} casos")

# Recomendação final
print("\n" + "="*80)
print("AVALIAÇÃO PARA LANÇAMENTO COMERCIAL:")
print("="*80)

recommendations = []
issues = []

if accuracy >= 0.45:
    recommendations.append("✅ Accuracy acima de 45% - Aceitável para lançamento")
else:
    issues.append(f"❌ Accuracy de {accuracy*100:.1f}% está abaixo do mínimo (45%)")

if avg_brier <= 0.25:
    recommendations.append("✅ Brier Score ≤ 0.25 - Boa calibração")
else:
    issues.append(f"⚠️  Brier Score de {avg_brier:.4f} indica necessidade de calibração")

if avg_log_loss <= 1.00:
    recommendations.append("✅ Log Loss ≤ 1.00 - Previsões razoavelmente confiantes")
else:
    issues.append(f"⚠️  Log Loss de {avg_log_loss:.4f} indica excesso de confiança")

if improvement >= 20:
    recommendations.append(f"✅ Melhoria de {improvement:.1f}% sobre baseline aleatório")
else:
    issues.append(f"⚠️  Melhoria de apenas {improvement:.1f}% sobre baseline")

print("\nPontos Positivos:")
for rec in recommendations:
    print(f"  {rec}")

if issues:
    print("\nPontos de Atenção:")
    for issue in issues:
        print(f"  {issue}")

print("\n" + "-"*80)
if len(recommendations) >= 3 and len(issues) <= 1:
    print("CONCLUSÃO: ✅ APROVADO PARA LANÇAMENTO")
    print("O modelo demonstra métricas adequadas para uso comercial.")
    print("Recomenda-se monitoramento contínuo e ajustes incrementais.")
elif len(recommendations) >= 2:
    print("CONCLUSÃO: ⚠️  LANÇAMENTO CONDICIONAL")
    print("O modelo apresenta resultados promissores mas necessita melhorias.")
    print("Sugestão: lançar em fase beta com disclaimers claros.")
else:
    print("CONCLUSÃO: ❌ REQUER MAIS DESENVOLVIMENTO")
    print("O modelo ainda não atingiu métricas mínimas para lançamento comercial.")
    print("Recomenda-se aprimoramento antes de promover comercialmente.")
print("="*80 + "\n")
