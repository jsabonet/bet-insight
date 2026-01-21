"""
Validação com partidas finalizadas da API para medir acertividade real
Busca partidas recentes finalizadas e calcula métricas de performance
"""
import os
import sys
import django
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
import numpy as np

def calculate_brier_score(predicted_probs, actual_outcome):
    """Calcula Brier Score (quanto menor, melhor)"""
    probs = [predicted_probs.get('home_win', 0), 
             predicted_probs.get('draw', 0), 
             predicted_probs.get('away_win', 0)]
    return np.mean([(p - a)**2 for p, a in zip(probs, actual_outcome)])

def calculate_log_loss(predicted_probs, actual_outcome):
    """Calcula Log Loss (quanto menor, melhor)"""
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

def get_actual_outcome(home_score, away_score):
    """Retorna vetor one-hot do resultado real"""
    if home_score > away_score:
        return [1, 0, 0]  # Vitória casa
    elif home_score < away_score:
        return [0, 0, 1]  # Vitória fora
    else:
        return [0, 1, 0]  # Empate

def get_prediction_label(probs):
    """Retorna label da previsão"""
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
print("VALIDAÇÃO COM PARTIDAS FINALIZADAS (API)")
print("="*80)

# Ligas principais para teste
leagues = [
    39,   # Premier League
    140,  # La Liga
    78,   # Bundesliga
    135,  # Serie A
    61,   # Ligue 1
]

api = FootballAPIService()
orchestrator = HybridAnalysisOrchestrator()

# Data range: últimos 3 dias
end_date = datetime.now()
start_date = end_date - timedelta(days=3)

print(f"\nBuscando partidas finalizadas entre {start_date.date()} e {end_date.date()}...")
print("Ligas: Premier League, La Liga, Bundesliga, Serie A, Ligue 1\n")

all_fixtures = []
for league_id in leagues:
    print(f"  Consultando liga {league_id}...", end=" ")
    try:
        result = api.get_fixtures_by_league(
            league_id=league_id,
            from_date=start_date.strftime('%Y-%m-%d'),
            to_date=end_date.strftime('%Y-%m-%d')
        )
        if result.get('success') and result.get('fixtures'):
            # Filtrar apenas partidas finalizadas
            finished = [f for f in result['fixtures'] if f['fixture']['status']['short'] == 'FT']
            if finished:
                all_fixtures.extend(finished)
                print(f"✓ {len(finished)} partidas")
            else:
                print("✓ 0 partidas FT")
        else:
            print("✓ 0 partidas")
    except Exception as e:
        print(f"✗ Erro: {str(e)}")

print(f"\nTotal encontrado: {len(all_fixtures)} partidas finalizadas")

if len(all_fixtures) == 0:
    print("\nERRO: Nenhuma partida finalizada encontrada")
    print("Tentando com período maior (últimos 7 dias)...\n")
    
    start_date = end_date - timedelta(days=7)
    for league_id in leagues:
        print(f"  Consultando liga {league_id}...", end=" ")
        try:
            result = api.get_fixtures_by_league(
                league_id=league_id,
                from_date=start_date.strftime('%Y-%m-%d'),
                to_date=end_date.strftime('%Y-%m-%d')
            )
            if result.get('success') and result.get('fixtures'):
                finished = [f for f in result['fixtures'] if f['fixture']['status']['short'] == 'FT']
                if finished:
                    all_fixtures.extend(finished)
                    print(f"✓ {len(finished)} partidas")
                else:
                    print("✓ 0 partidas FT")
            else:
                print("✓ 0 partidas")
        except Exception as e:
            print(f"✗ Erro: {str(e)}")
    
    print(f"\nTotal encontrado: {len(all_fixtures)} partidas finalizadas")
    
    if len(all_fixtures) == 0:
        print("\nERRO: Ainda assim nenhuma partida encontrada. Abortando.")
        sys.exit(1)

# Limitar a 30 partidas para não gastar muitas requisições
all_fixtures = all_fixtures[:30]
print(f"Processando {len(all_fixtures)} partidas...\n")

# Inicializar métricas
results = []
successful_analyses = 0
failed_analyses = 0

print("Executando análises...")
print("-" * 80)

for i, fixture in enumerate(all_fixtures, 1):
    try:
        fixture_id = fixture['fixture']['id']
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']
        home_score = fixture['goals']['home']
        away_score = fixture['goals']['away']
        league_name = fixture['league']['name']
        match_date = fixture['fixture']['date']
        
        print(f"\n[{i}/{len(all_fixtures)}] {home_team} {home_score}-{away_score} {away_team}")
        print(f"    Liga: {league_name} | ID: {fixture_id}")
        
        # Executar análise
        result = orchestrator.analyze(fixture_id)
        
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
        actual_outcome = get_actual_outcome(home_score, away_score)
        
        # Calcular métricas
        brier = calculate_brier_score(consensus, actual_outcome)
        log_loss = calculate_log_loss(consensus, actual_outcome)
        correct = validate_prediction(consensus, actual_outcome)
        
        # Armazenar resultado
        results.append({
            'fixture_id': fixture_id,
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score,
            'predicted_probs': consensus,
            'actual_outcome': actual_outcome,
            'brier_score': brier,
            'log_loss': log_loss,
            'correct': correct,
            'league': league_name
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

print(f"\nPartidas analisadas: {successful_analyses}/{len(all_fixtures)}")
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

# Distribuição de resultados
print("\n" + "-"*80)
print("DISTRIBUIÇÃO DE RESULTADOS:")
print("-"*80)
print(f"Vitórias Casa: {len(home_wins)} ({len(home_wins)/len(results)*100:.1f}%)")
print(f"Empates:       {len(draws)} ({len(draws)/len(results)*100:.1f}%)")
print(f"Vitórias Fora: {len(away_wins)} ({len(away_wins)/len(results)*100:.1f}%)")

# Calibração
print("\n" + "-"*80)
print("CALIBRAÇÃO (confiança vs acertividade):")
print("-"*80)

confidence_ranges = [
    (0.33, 0.40, "Baixa (33-40%)"),
    (0.40, 0.50, "Média-Baixa (40-50%)"),
    (0.50, 0.60, "Média (50-60%)"),
    (0.60, 0.70, "Alta (60-70%)"),
    (0.70, 1.00, "Muito Alta (70%+)")
]

for min_conf, max_conf, label in confidence_ranges:
    in_range = []
    for r in results:
        max_prob = max(r['predicted_probs']['home_win'], 
                      r['predicted_probs']['draw'], 
                      r['predicted_probs']['away_win'])
        if min_conf <= max_prob < max_conf:
            in_range.append(r)
    
    if in_range:
        acc_in_range = sum(1 for r in in_range if r['correct']) / len(in_range)
        avg_conf = np.mean([max(r['predicted_probs']['home_win'], 
                               r['predicted_probs']['draw'], 
                               r['predicted_probs']['away_win']) for r in in_range])
        print(f"{label}: {acc_in_range*100:.1f}% acertividade | Confiança média: {avg_conf*100:.1f}% | {len(in_range)} partidas")

# Benchmark
random_accuracy = 1/3
improvement = (accuracy - random_accuracy) / random_accuracy * 100

print("\n" + "-"*80)
print("COMPARAÇÃO:")
print("-"*80)
print(f"Baseline (aleatório):    {random_accuracy*100:.1f}%")
print(f"Modelo atual:            {accuracy*100:.1f}%")
print(f"Melhoria:                {improvement:+.1f}%")

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

# Verificar se tem amostra suficiente
if successful_analyses >= 20:
    recommendations.append(f"✅ Amostra adequada: {successful_analyses} partidas analisadas")
else:
    issues.append(f"⚠️  Amostra pequena: apenas {successful_analyses} partidas")

print("\nPontos Positivos:")
for rec in recommendations:
    print(f"  {rec}")

if issues:
    print("\nPontos de Atenção:")
    for issue in issues:
        print(f"  {issue}")

print("\n" + "-"*80)
if len(recommendations) >= 4 and len(issues) <= 1:
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

print("\n" + "-"*80)
print("PRÓXIMOS PASSOS RECOMENDADOS:")
print("-"*80)
print("1. Expandir validação para 100+ partidas")
print("2. Testar em diferentes ligas e níveis de competição")
print("3. Implementar monitoramento contínuo de performance")
print("4. Avaliar performance em subconjuntos (favoritos, zebras, etc.)")
print("5. Comparar sistematicamente com odds do mercado")
print("="*80 + "\n")
