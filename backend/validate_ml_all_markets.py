"""
Validação ML em TODOS os 49 mercados do sistema
Combina predições ML (1X2) com Poisson para gerar todos os mercados
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.statistical_models import PoissonBivariateModel
from ml_predictor import get_ml_predictor
from collections import defaultdict
import json
from datetime import datetime

print("="*80)
print("VALIDAÇÃO ML - TODOS OS 49 MERCADOS")
print("="*80)
print()

# Carregar preditor ML
predictor = get_ml_predictor()

if not predictor:
    print("ERRO: Não foi possível carregar o modelo ML")
    sys.exit(1)

print(f"Modelo ML carregado: {predictor.get_model_info()}")
print()

# Carregar partidas
matches = Match.objects.filter(
    status='finished',
    home_score__isnull=False,
    away_score__isnull=False
).select_related('home_team', 'away_team', 'league')

total = matches.count()
print(f"Validando {total} partidas em todos os mercados...")
print()

# Modelo Poisson para gerar mercados
poisson_model = PoissonBivariateModel()

# Estrutura para armazenar resultados
market_results = defaultdict(lambda: {'correct': 0, 'total': 0, 'predictions': []})

# Processar cada partida
for i, match in enumerate(matches):
    if i % 200 == 0:
        print(f"  Processando {i}/{total}...")
    
    try:
        # 1. PREDIÇÃO ML para resultado 1X2
        try:
            ml_result = predictor.predict(match)
            ml_probabilities = ml_result['probabilities']
        except Exception as e:
            # Se ML falhar, pular esta partida
            if i % 200 == 0:
                print(f"   ERRO ML na partida {match.id}: {e}")
            continue
        
        # 2. Usar Poisson para gerar todos os mercados
        # predict() já retorna TODOS os mercados no dict 'probabilities'
        poisson_model = PoissonBivariateModel()
        
        # Calcular lambdas esperados baseado nas probabilidades ML
        prob_home = ml_probabilities['Casa']
        prob_draw = ml_probabilities['Empate']
        prob_away = ml_probabilities['Fora']
        
        # Estimar lambdas que dariam essas probabilidades (heurística simples)
        # Média de gols por jogo ≈ 2.7, distribuir conforme probabilidades
        total_lambda = 2.7
        if prob_home > prob_away:
            home_lambda = total_lambda * (0.5 + (prob_home - 0.33))
            away_lambda = total_lambda - home_lambda
        elif prob_away > prob_home:
            away_lambda = total_lambda * (0.5 + (prob_away - 0.33))
            home_lambda = total_lambda - away_lambda
        else:
            home_lambda = total_lambda / 2
            away_lambda = total_lambda / 2
        
        # Garantir valores mínimos
        home_lambda = max(0.5, min(3.5, home_lambda))
        away_lambda = max(0.5, min(3.5, away_lambda))
        
        # Chamar predict() que retorna TODOS os mercados
        try:
            prediction = poisson_model.predict(
                home_strength=home_lambda,
                away_strength=away_lambda,
                league_id=match.league.id if match.league else None
            )
            all_probs = prediction['probabilities']
        except Exception as e:
            print(f"   ERRO ao gerar mercados: {e}")
            continue
        
        # 3. Mapear probabilidades para os 49 mercados do sistema
        # Formato: {market_name: probabilidade}
        markets = {
            # 1X2 (3 mercados)
            'home_win': all_probs['home_win'],
            'draw': all_probs['draw'],
            'away_win': all_probs['away_win'],
            
            # Double Chance (3 mercados)
            '1X': all_probs['1X'],
            '12': all_probs['12'],
            'X2': all_probs['X2'],
            
            # Over/Under Standard (10 mercados)
            'over_0.5': all_probs['over_0_5'],
            'under_0.5': all_probs['under_0_5'],
            'over_1.5': all_probs['over_1_5'],
            'under_1.5': all_probs['under_1_5'],
            'over_2.5': all_probs['over_2_5'],
            'under_2.5': all_probs['under_2_5'],
            'over_3.5': all_probs['over_3_5'],
            'under_3.5': all_probs['under_3_5'],
            'over_4.5': all_probs['over_4_5'],
            'under_4.5': all_probs['under_4_5'],
            
            # Asian Lines (8 mercados)
            'over_1.75': all_probs['over_1_75'],
            'under_1.75': all_probs['under_1_75'],
            'over_2.25': all_probs['over_2_25'],
            'under_2.25': all_probs['under_2_25'],
            'over_2.75': all_probs['over_2_75'],
            'under_2.75': all_probs['under_2_75'],
            'over_3.25': all_probs['over_3_25'],
            'under_3.25': all_probs['under_3_25'],
            
            # BTTS (2 mercados)
            'btts_yes': all_probs['btts_yes'],
            'btts_no': all_probs['btts_no'],
            
            # Clean Sheets (2 mercados)
            'home_clean_sheet': all_probs['home_clean_sheet'],
            'away_clean_sheet': all_probs['away_clean_sheet'],
            
            # Team Total Goals (12 mercados)
            'home_over_0.5': all_probs['home_over_0.5'],
            'home_under_0.5': all_probs['home_under_0.5'],
            'home_over_1.5': all_probs['home_over_1.5'],
            'home_under_1.5': all_probs['home_under_1.5'],
            'home_over_2.5': all_probs['home_over_2.5'],
            'home_under_2.5': all_probs['home_under_2.5'],
            'away_over_0.5': all_probs['away_over_0.5'],
            'away_under_0.5': all_probs['away_under_0.5'],
            'away_over_1.5': all_probs['away_over_1.5'],
            'away_under_1.5': all_probs['away_under_1.5'],
            'away_over_2.5': all_probs['away_over_2.5'],
            'away_under_2.5': all_probs['away_under_2.5'],
            
            # Winning Margins (6 mercados)
            'home_by_1': all_probs['home_by_1'],
            'home_by_2+': all_probs['home_by_2plus'],
            'away_by_1': all_probs['away_by_1'],
            'away_by_2+': all_probs['away_by_2plus'],
            
            # Odd/Even (2 mercados)
            'odd_goals': all_probs['odd_goals'],
            'even_goals': all_probs['even_goals'],
        }
        
        # 4. Validar cada mercado
        home_score = match.home_score
        away_score = match.away_score
        
        # Tratamento especial para 1X2 (escolher máximo das 3 opções)
        probs_1x2 = {
            'home_win': markets['home_win'],
            'draw': markets['draw'],
            'away_win': markets['away_win']
        }
        predicted_1x2 = max(probs_1x2, key=probs_1x2.get)
        
        for market_name, probability in markets.items():
            # Determinar resultado real para este mercado
            actual_result = None
            
            # 1X2 - Tratamento especial (máximo das 3 opções)
            if market_name in ['home_win', 'draw', 'away_win']:
                if market_name == 'home_win':
                    actual_result = home_score > away_score
                elif market_name == 'draw':
                    actual_result = home_score == away_score
                elif market_name == 'away_win':
                    actual_result = home_score < away_score
                
                # Predição = mercado com maior probabilidade
                prediction = (predicted_1x2 == market_name)
                is_correct = prediction == actual_result
                
                market_results[market_name]['total'] += 1
                if is_correct:
                    market_results[market_name]['correct'] += 1
                continue  # Próximo mercado
            
            # Double Chance
            elif market_name == '1X':
                actual_result = home_score >= away_score
                actual_result = home_score >= away_score
            elif market_name == '12':
                actual_result = home_score != away_score
            elif market_name == 'X2':
                actual_result = home_score <= away_score
            
            # Over/Under Standard
            elif market_name.startswith('over_'):
                line = float(market_name.split('_')[1])
                actual_result = (home_score + away_score) > line
            elif market_name.startswith('under_'):
                line = float(market_name.split('_')[1])
                actual_result = (home_score + away_score) < line
            
            # BTTS
            elif market_name == 'btts_yes':
                actual_result = home_score > 0 and away_score > 0
            elif market_name == 'btts_no':
                actual_result = home_score == 0 or away_score == 0
            
            # Clean Sheets
            elif market_name == 'home_clean_sheet':
                actual_result = away_score == 0
            elif market_name == 'away_clean_sheet':
                actual_result = home_score == 0
            
            # Team Totals
            elif market_name.startswith('home_over_'):
                line = float(market_name.split('_')[2])
                actual_result = home_score > line
            elif market_name.startswith('home_under_'):
                line = float(market_name.split('_')[2])
                actual_result = home_score < line
            elif market_name.startswith('away_over_'):
                line = float(market_name.split('_')[2])
                actual_result = away_score > line
            elif market_name.startswith('away_under_'):
                line = float(market_name.split('_')[2])
                actual_result = away_score < line
            
            # Margins
            elif market_name == 'home_by_1':
                actual_result = (home_score - away_score) == 1
            elif market_name == 'home_by_2+':
                actual_result = (home_score - away_score) >= 2
            elif market_name == 'away_by_1':
                actual_result = (away_score - home_score) == 1
            elif market_name == 'away_by_2+':
                actual_result = (away_score - home_score) >= 2
            
            # Odd/Even
            elif market_name == 'odd_goals':
                actual_result = (home_score + away_score) % 2 == 1
            elif market_name == 'even_goals':
                actual_result = (home_score + away_score) % 2 == 0
            
            # Validar predição (prob > 0.5 = prever True)
            if actual_result is not None:
                prediction = probability > 0.5
                is_correct = prediction == actual_result
                
                market_results[market_name]['total'] += 1
                if is_correct:
                    market_results[market_name]['correct'] += 1
    
    except Exception as e:
        print(f"  ERRO na partida {match.id}: {e}")
        continue

print()
print("="*80)
print("RESULTADOS POR MERCADO (ML + POISSON)")
print("="*80)
print()

# Agrupar por categoria (nomes ajustados para bater com Poisson)
market_categories = {
    '1X2': ['home_win', 'draw', 'away_win'],
    'Double Chance': ['1X', '12', 'X2'],
    'Over/Under Standard': [
        'over_0.5', 'under_0.5',
        'over_1.5', 'under_1.5',
        'over_2.5', 'under_2.5',
        'over_3.5', 'under_3.5',
        'over_4.5', 'under_4.5'
    ],
    'Over/Under Asian': [
        'over_1.75', 'under_1.75',
        'over_2.25', 'under_2.25',
        'over_2.75', 'under_2.75',
        'over_3.25', 'under_3.25'
    ],
    'BTTS': ['btts_yes', 'btts_no'],
    'Clean Sheets': ['home_clean_sheet', 'away_clean_sheet'],
    'Team Totals': [
        'home_over_0.5', 'home_under_0.5',
        'home_over_1.5', 'home_under_1.5',
        'home_over_2.5', 'home_under_2.5',
        'away_over_0.5', 'away_under_0.5',
        'away_over_1.5', 'away_under_1.5',
        'away_over_2.5', 'away_under_2.5'
    ],
    'Margins': [
        'home_by_1', 'home_by_2+',
        'away_by_1', 'away_by_2+'
    ],
    'Odd/Even': ['odd_goals', 'even_goals']
}

# Calcular acurácia geral
total_predictions = sum(m['total'] for m in market_results.values())
total_correct = sum(m['correct'] for m in market_results.values())
overall_accuracy = total_correct / total_predictions if total_predictions > 0 else 0

print(f"ACURÁCIA GERAL (TODOS OS MERCADOS): {overall_accuracy*100:.2f}%")
print(f"  Corretas: {total_correct:,}/{total_predictions:,}")
print()

# Mostrar por categoria
all_accuracies = []

for category, markets in market_categories.items():
    print(f"\n{category}:")
    print("-" * 80)
    
    category_total = 0
    category_correct = 0
    
    for market in markets:
        if market in market_results:
            stats = market_results[market]
            if stats['total'] > 0:
                acc = stats['correct'] / stats['total']
                all_accuracies.append(acc)
                category_total += stats['total']
                category_correct += stats['correct']
                
                bar = '=' * int(acc * 50)
                print(f"  {market:25s}: {acc*100:5.1f}% ({stats['correct']:4d}/{stats['total']:4d}) {bar}")
    
    if category_total > 0:
        category_acc = category_correct / category_total
        print(f"\n  Média da categoria: {category_acc*100:.2f}%")

print()
print("="*80)
print("COMPARAÇÃO: ML+POISSON vs POISSON PURO")
print("="*80)
print()

print(f"  Poisson Puro (baseline):       46.01%")
print(f"  ML + Poisson (híbrido):        {overall_accuracy*100:.2f}%")
print(f"  Ganho:                         {(overall_accuracy - 0.4601)*100:+.2f} pontos")
print()

# TOP 10 e BOTTOM 10 mercados
print("="*80)
print("TOP 10 MERCADOS (MAIOR ACURÁCIA)")
print("="*80)

market_accuracies = []
for market, stats in market_results.items():
    if stats['total'] > 0:
        accuracy = stats['correct'] / stats['total']
        market_accuracies.append({
            'market': market,
            'accuracy': accuracy,
            'correct': stats['correct'],
            'total': stats['total']
        })

market_accuracies.sort(key=lambda x: x['accuracy'], reverse=True)

for i, item in enumerate(market_accuracies[:10], 1):
    print(f"{i:2d}. {item['market']:30s} {item['accuracy']*100:5.1f}% ({item['correct']:4d}/{item['total']:4d})")

print()
print("="*80)
print("BOTTOM 10 MERCADOS (MENOR ACURÁCIA)")
print("="*80)

for i, item in enumerate(market_accuracies[-10:], 1):
    print(f"{i:2d}. {item['market']:30s} {item['accuracy']*100:5.1f}% ({item['correct']:4d}/{item['total']:4d})")

print()

# Salvar resultados
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
results_file = f'validation_ml_all_markets_{timestamp}.json'

results_data = {
    'timestamp': timestamp,
    'total_matches': total,
    'overall_accuracy': overall_accuracy,
    'total_predictions': total_predictions,
    'total_correct': total_correct,
    'market_results': {
        market: {
            'accuracy': stats['correct'] / stats['total'] if stats['total'] > 0 else 0,
            'correct': stats['correct'],
            'total': stats['total']
        }
        for market, stats in market_results.items()
    },
    'top_10': market_accuracies[:10],
    'bottom_10': market_accuracies[-10:]
}

with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results_data, f, indent=2, ensure_ascii=False)

print(f"Resultados salvos em: {results_file}")
print()
print("="*80)
