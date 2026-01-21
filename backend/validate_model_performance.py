"""
Validação com partidas finalizadas conhecidas para medir acertividade real
Usa IDs de partidas específicas que sabemos ter dados completos
"""
import os
import sys
import django

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
print("VALIDAÇÃO COM PARTIDAS FINALIZADAS")
print("="*80)

# Partidas finalizadas conhecidas de diferentes ligas
# Vamos buscar partidas recentes de ligas ativas
print("\nBuscando partidas finalizadas recentes de ligas ativas...")

# Ligas ativas (América do Sul, Copa do Mundo de Clubes, etc.)
leagues_active = [
    71,   # Brasileirão Serie A
    73,   # Copa do Brasil
    128,  # Liga Argentina
    283,  # Copa Libertadores
]

api = FootballAPIService()

fixtures_data = []
for league_id in leagues_active:
    print(f"  Liga {league_id}...", end=" ")
    try:
        from datetime import datetime, timedelta
        end = datetime.now()
        start = end - timedelta(days=30)  # Últimas 4 semanas
        
        result = api.get_fixtures_by_league(
            league_id=league_id,
            from_date=start.strftime('%Y-%m-%d'),
            to_date=end.strftime('%Y-%m-%d')
        )
        
        if result.get('success') and result.get('fixtures'):
            # Filtrar apenas finalizadas
            finished = [f for f in result['fixtures'] if f['fixture']['status']['short'] == 'FT']
            if finished:
                # Pegar apenas 3 mais recentes de cada liga
                fixtures_data.extend(finished[-3:])
                print(f"✓ {len(finished)} partidas FT (usando 3 mais recentes)")
            else:
                print("✓ 0 partidas FT")
        else:
            print("✓ 0 partidas")
    except Exception as e:
        print(f"✗ Erro: {str(e)}")

print(f"\nTotal de partidas coletadas: {len(fixtures_data)}")

if len(fixtures_data) == 0:
    print("\nTentando buscar partidas ao vivo recém-finalizadas...")
    # Buscar partidas de hoje
    today_result = api.get_fixtures_by_date()
    if today_result.get('success') and today_result.get('fixtures'):
        finished_today = [f for f in today_result['fixtures'] if f['fixture']['status']['short'] == 'FT']
        if finished_today:
            fixtures_data.extend(finished_today[:10])  # Primeiras 10
            print(f"✓ Encontradas {len(finished_today)} partidas finalizadas hoje")

print(f"\nTotal final: {len(fixtures_data)} partidas\n")

orchestrator = HybridAnalysisOrchestrator()

if len(fixtures_data) == 0:
    print("\nERRO: Nenhuma partida finalizada válida encontrada")
    print("\nSugestão: Atualize os fixture_ids no script com partidas recentes")
    print("Você pode encontrar IDs em: https://www.api-football.com/documentation-v3")
    sys.exit(1)

# Inicializar métricas
results = []
successful_analyses = 0
failed_analyses = 0

print("\n" + "="*80)
print("EXECUTANDO ANÁLISES")
print("="*80)

for i, fixture in enumerate(fixtures_data, 1):
    try:
        fixture_id = fixture['fixture']['id']
        home_team = fixture['teams']['home']['name']
        away_team = fixture['teams']['away']['name']
        home_score = fixture['goals']['home']
        away_score = fixture['goals']['away']
        league_name = fixture['league']['name']
        
        print(f"\n[{i}/{len(fixtures_data)}] {home_team} {home_score}-{away_score} {away_team}")
        print(f"    Liga: {league_name} | ID: {fixture_id}")
        
        # Buscar ou criar partida no banco
        from apps.matches.models import Match, League, Team
        from django.utils import timezone as tz
        
        # Tentar buscar partida existente
        match = Match.objects.filter(api_football_id=fixture_id).first()
        
        if not match:
            # Criar partida temporária para análise
            try:
                league, _ = League.objects.get_or_create(
                    api_football_id=fixture['league']['id'],
                    defaults={'name': league_name}
                )
                
                home_team_obj, _ = Team.objects.get_or_create(
                    api_football_id=fixture['teams']['home']['id'],
                    defaults={'name': home_team}
                )
                
                away_team_obj, _ = Team.objects.get_or_create(
                    api_football_id=fixture['teams']['away']['id'],
                    defaults={'name': away_team}
                )
                
                match = Match.objects.create(
                    api_football_id=fixture_id,
                    home_team=home_team_obj,
                    away_team=away_team_obj,
                    league=league,
                    match_date=tz.now(),
                    home_score=home_score,
                    away_score=away_score,
                    status='FT'
                )
            except Exception as e:
                print(f"    ⚠️  Erro ao criar partida no banco: {str(e)}")
                failed_analyses += 1
                continue
        
        # Executar análise
        result = orchestrator.run(match)
        
        if not result or 'model_probabilities' not in result:
            print("    ⚠️  Análise retornou dados incompletos")
            failed_analyses += 1
            continue
        
        # Extrair probabilidades
        if 'model_probabilities' in result:
            consensus = result.get('model_probabilities', {}).get('consensus', {})
        elif 'probabilities' in result:
            consensus = result['probabilities']
        else:
            print("    ⚠️  Probabilidades não encontradas no resultado")
            failed_analyses += 1
            continue
        
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
        
        # Obter odds do mercado se disponível
        if 'enriched_data' in result:
            enriched = result.get('enriched_data', {})
            market_odds = enriched.get('odds', {})
        elif 'market_odds' in result:
            market_odds = result.get('market_odds', {})
        else:
            market_odds = {}
        
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
            'league': league_name,
            'market_odds': market_odds
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
        
        # Comparar com odds do mercado se disponível
        if all(k in market_odds for k in ['home_win', 'draw', 'away_win']):
            print(f"    Odds: Casa {market_odds['home_win']:.2f} | Empate {market_odds['draw']:.2f} | Fora {market_odds['away_win']:.2f}")
        
    except Exception as e:
        print(f"    ❌ Erro na análise: {str(e)}")
        import traceback
        traceback.print_exc()
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

print(f"\nPartidas analisadas: {successful_analyses}/{len(fixtures_data)}")
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

# Comparação com mercado
print("\n" + "-"*80)
print("COMPARAÇÃO COM MERCADO:")
print("-"*80)

results_with_odds = [r for r in results if all(k in r['market_odds'] for k in ['home_win', 'draw', 'away_win'])]

if results_with_odds:
    market_correct = 0
    model_better = 0
    
    for r in results_with_odds:
        # Converter odds para probabilidades
        prob_home = 1 / r['market_odds']['home_win']
        prob_draw = 1 / r['market_odds']['draw']
        prob_away = 1 / r['market_odds']['away_win']
        total = prob_home + prob_draw + prob_away
        
        market_probs = {
            'home_win': prob_home / total,
            'draw': prob_draw / total,
            'away_win': prob_away / total
        }
        
        # Verificar se mercado acertou
        if validate_prediction(market_probs, r['actual_outcome']):
            market_correct += 1
        
        # Comparar Brier Score
        market_brier = calculate_brier_score(market_probs, r['actual_outcome'])
        if r['brier_score'] < market_brier:
            model_better += 1
    
    market_accuracy = market_correct / len(results_with_odds)
    print(f"Mercado (odds):          {market_accuracy*100:.1f}% accuracy")
    print(f"Modelo melhor que odds:  {model_better}/{len(results_with_odds)} casos ({model_better/len(results_with_odds)*100:.1f}%)")
else:
    print("Sem dados de odds para comparação")

# Benchmark
random_accuracy = 1/3
improvement = (accuracy - random_accuracy) / random_accuracy * 100

print("\n" + "-"*80)
print("BENCHMARK:")
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
warnings = []

if accuracy >= 0.45:
    recommendations.append("✅ Accuracy acima de 45% - Aceitável para lançamento")
elif accuracy >= 0.40:
    warnings.append(f"⚠️  Accuracy de {accuracy*100:.1f}% está no limite (mínimo: 45%)")
else:
    issues.append(f"❌ Accuracy de {accuracy*100:.1f}% está abaixo do mínimo (45%)")

if avg_brier <= 0.25:
    recommendations.append("✅ Brier Score ≤ 0.25 - Boa calibração")
elif avg_brier <= 0.30:
    warnings.append(f"⚠️  Brier Score de {avg_brier:.4f} - Calibração aceitável")
else:
    issues.append(f"❌ Brier Score de {avg_brier:.4f} - Necessita calibração")

if avg_log_loss <= 1.00:
    recommendations.append("✅ Log Loss ≤ 1.00 - Previsões razoavelmente confiantes")
elif avg_log_loss <= 1.20:
    warnings.append(f"⚠️  Log Loss de {avg_log_loss:.4f} - Confiança aceitável")
else:
    issues.append(f"❌ Log Loss de {avg_log_loss:.4f} - Excesso de confiança")

if improvement >= 20:
    recommendations.append(f"✅ Melhoria de {improvement:.1f}% sobre baseline aleatório")
elif improvement >= 10:
    warnings.append(f"⚠️  Melhoria de {improvement:.1f}% sobre baseline (esperado: 20%+)")
else:
    issues.append(f"❌ Melhoria de apenas {improvement:.1f}% sobre baseline")

# Amostra
if successful_analyses >= 20:
    recommendations.append(f"✅ Amostra adequada: {successful_analyses} partidas")
elif successful_analyses >= 10:
    warnings.append(f"⚠️  Amostra limitada: {successful_analyses} partidas")
else:
    issues.append(f"❌ Amostra insuficiente: apenas {successful_analyses} partidas")

print("\nPontos Positivos:")
for rec in recommendations:
    print(f"  {rec}")

if warnings:
    print("\nPontos de Atenção:")
    for warn in warnings:
        print(f"  {warn}")

if issues:
    print("\nProblemas Críticos:")
    for issue in issues:
        print(f"  {issue}")

print("\n" + "-"*80)
if len(recommendations) >= 4 and len(issues) == 0:
    print("CONCLUSÃO: ✅ APROVADO PARA LANÇAMENTO")
    print("O modelo demonstra métricas adequadas para uso comercial.")
    print("Recomenda-se monitoramento contínuo e ajustes incrementais.")
elif len(recommendations) >= 2 and len(issues) <= 1:
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
print("1. Expandir validação para 50-100 partidas de ligas diversas")
print("2. Testar em diferentes períodos da temporada")
print("3. Implementar monitoramento contínuo de performance em produção")
print("4. Avaliar performance por tipo de partida (favorito vs zebra)")
print("5. Criar dashboard de métricas em tempo real")
print("6. Realizar A/B testing com usuários beta")
print("="*80 + "\n")

print("\nOBSERVAÇÃO IMPORTANTE:")
print("Esta validação usa uma amostra limitada de partidas.")
print("Para uma validação robusta, recomenda-se:")
print("- Mínimo 100 partidas de diferentes ligas")
print("- Validação em diferentes períodos (início, meio, fim de temporada)")
print("- Validação cruzada para evitar overfitting")
print("- Monitoramento contínuo pós-lançamento\n")
