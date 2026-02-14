"""
Valida acurácia do modelo ML treinado em todas as partidas do banco
"""
import os
import sys
import django
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from ml_predictor import get_ml_predictor

print("="*80)
print("VALIDAÇÃO ML - TODAS AS PARTIDAS DO BANCO")
print("="*80)
print()

# Carregar preditor
predictor = get_ml_predictor()

if not predictor:
    print("ERRO: Não foi possível carregar o modelo ML")
    sys.exit(1)

print(f"Modelo carregado: {predictor.get_model_info()}")
print()

# Carregar TODAS as partidas finalizadas
matches = Match.objects.filter(
    status='finished',
    home_score__isnull=False,
    away_score__isnull=False
).select_related('home_team', 'away_team', 'league')

total = matches.count()
print(f"Validando TODAS as {total} partidas do banco de dados...")
print()

# Contadores
correct_predictions = 0
total_predictions = 0
predictions_by_outcome = defaultdict(lambda: {'total': 0, 'correct': 0})
confidence_buckets = defaultdict(lambda: {'total': 0, 'correct': 0})

# Processar partidas
for i, match in enumerate(matches):
    if i % 100 == 0:
        print(f"  Processando {i}/{total}...")
    
    try:
        # Determinar resultado real
        if match.home_score > match.away_score:
            real_result = 'Casa'
        elif match.home_score < match.away_score:
            real_result = 'Fora'
        else:
            real_result = 'Empate'
        
        # Fazer predição
        result = predictor.predict(match)
        prediction = result['prediction']
        confidence = result['confidence']
        
        # Verificar se acertou
        is_correct = prediction == real_result
        
        if is_correct:
            correct_predictions += 1
        
        total_predictions += 1
        
        # Estatísticas por resultado
        predictions_by_outcome[prediction]['total'] += 1
        if is_correct:
            predictions_by_outcome[prediction]['correct'] += 1
        
        # Estatísticas por nível de confiança
        if confidence < 0.4:
            bucket = '< 40%'
        elif confidence < 0.5:
            bucket = '40-50%'
        elif confidence < 0.6:
            bucket = '50-60%'
        elif confidence < 0.7:
            bucket = '60-70%'
        elif confidence < 0.8:
            bucket = '70-80%'
        else:
            bucket = '> 80%'
        
        confidence_buckets[bucket]['total'] += 1
        if is_correct:
            confidence_buckets[bucket]['correct'] += 1
    
    except Exception as e:
        print(f"  ERRO na partida {match.id}: {e}")
        continue

print()
print("="*80)
print("RESULTADOS DA VALIDAÇÃO")
print("="*80)
print()

# Acurácia geral
accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
print(f"ACURÁCIA GERAL: {accuracy*100:.2f}%")
print(f"  Corretas: {correct_predictions}/{total_predictions}")
print()

# Acurácia por tipo de predição
print("ACURÁCIA POR TIPO DE PREDIÇÃO:")
print("-" * 60)
for outcome in ['Casa', 'Empate', 'Fora']:
    stats = predictions_by_outcome[outcome]
    if stats['total'] > 0:
        acc = stats['correct'] / stats['total']
        print(f"  {outcome:10s}: {acc*100:5.1f}% ({stats['correct']:4d}/{stats['total']:4d} predições)")
    else:
        print(f"  {outcome:10s}: N/A (sem predições)")
print()

# Acurácia por nível de confiança
print("ACURÁCIA POR NÍVEL DE CONFIANÇA:")
print("-" * 60)
buckets_order = ['< 40%', '40-50%', '50-60%', '60-70%', '70-80%', '> 80%']
for bucket in buckets_order:
    stats = confidence_buckets[bucket]
    if stats['total'] > 0:
        acc = stats['correct'] / stats['total']
        bar = '=' * int(acc * 50)
        print(f"  {bucket:10s}: {acc*100:5.1f}% ({stats['correct']:4d}/{stats['total']:4d}) {bar}")
print()

print("="*80)
print("COMPARAÇÃO COM OUTROS MODELOS:")
print("-" * 80)
print(f"  Poisson Baseline:       46.01%")
print(f"  Modelo genérico:        49.41%")
print(f"  Modelo balanceado (ML): {accuracy*100:.2f}%")
print()
print("="*80)
