"""
Valida modelo ML com TODAS as partidas: DB + Dataset Copa
"""
import os
import sys
import django
from collections import defaultdict
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from ml_predictor import get_ml_predictor

print("="*80)
print("VALIDAÇÃO COMPLETA ML - BANCO + DATASET COPA")
print("="*80)
print()

# Carregar preditor
predictor = get_ml_predictor()

if not predictor:
    print("ERRO: Não foi possível carregar o modelo ML")
    sys.exit(1)

print(f"Modelo carregado: {predictor.get_model_info()}")
print()

# ============================================================================
# PARTE 1: VALIDAR PARTIDAS DO BANCO DE DADOS
# ============================================================================
print("="*80)
print("PARTE 1: PARTIDAS DO BANCO DE DADOS")
print("="*80)
print()

db_matches = Match.objects.filter(
    status='finished',
    home_score__isnull=False,
    away_score__isnull=False
).select_related('home_team', 'away_team', 'league')

total_db = db_matches.count()
print(f"Validando {total_db} partidas do banco...")
print()

# Contadores DB
db_correct = 0
db_total = 0
db_by_outcome = defaultdict(lambda: {'total': 0, 'correct': 0})
db_by_confidence = defaultdict(lambda: {'total': 0, 'correct': 0})

# Processar partidas do DB
for i, match in enumerate(db_matches):
    if i % 200 == 0:
        print(f"  Processando DB {i}/{total_db}...")
    
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
            db_correct += 1
        db_total += 1
        
        # Estatísticas por resultado
        db_by_outcome[prediction]['total'] += 1
        if is_correct:
            db_by_outcome[prediction]['correct'] += 1
        
        # Estatísticas por confiança
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
        
        db_by_confidence[bucket]['total'] += 1
        if is_correct:
            db_by_confidence[bucket]['correct'] += 1
    
    except Exception as e:
        print(f"  ERRO na partida {match.id}: {e}")
        continue

print()
print("RESULTADOS - BANCO DE DADOS:")
print("-" * 80)
db_accuracy = db_correct / db_total if db_total > 0 else 0
print(f"Acurácia: {db_accuracy*100:.2f}% ({db_correct}/{db_total})")
print()

# ============================================================================
# PARTE 2: VALIDAR DATASET DE COPA
# ============================================================================
print("="*80)
print("PARTE 2: DATASET DE COPA (FA CUP)")
print("="*80)
print()

# Carregar dataset da Copa
cup_dataset_path = 'ml_training/cup_training_dataset.json'
with open(cup_dataset_path, 'r', encoding='utf-8') as f:
    cup_data = json.load(f)

cup_matches = cup_data['matches']
total_cup = len(cup_matches)
print(f"Validando {total_cup} partidas do dataset Copa...")
print()

# Contadores Copa
cup_correct = 0
cup_total = 0
cup_by_outcome = defaultdict(lambda: {'total': 0, 'correct': 0})
cup_by_confidence = defaultdict(lambda: {'total': 0, 'correct': 0})

# Processar partidas da Copa
# NOTA: Dataset Copa já tem features pré-calculadas, então vamos usar diretamente
from calculate_real_features import TeamStatsCalculator
import numpy as np

calculator = TeamStatsCalculator()

for i, cup_match in enumerate(cup_matches):
    if i % 50 == 0:
        print(f"  Processando Copa {i}/{total_cup}...")
    
    try:
        # O dataset já tem o label
        real_result = cup_match['label']
        
        # Normalizar label (pode estar como 0/1/2 ou texto)
        label_map = {
            'Empate': 'Empate', 'X': 'Empate', 'Draw': 'Empate', '0': 'Empate', 0: 'Empate',
            'Casa': 'Casa', 'Home': 'Casa', '1': 'Casa', 1: 'Casa',
            'Fora': 'Fora', 'Away': 'Fora', '2': 'Fora', 2: 'Fora'
        }
        real_result = label_map.get(real_result, real_result)
        
        # Extrair features (já estão no dataset)
        features = cup_match['features']
        feature_names = predictor.feature_names
        
        # Converter para array
        feature_vector = []
        for feature_name in feature_names:
            value = features.get(feature_name, 0)
            
            if isinstance(value, bool):
                value = 1 if value else 0
            elif isinstance(value, str):
                value = hash(value) % 100 / 100.0
            
            feature_vector.append(float(value))
        
        X = np.array([feature_vector])
        
        # Predição
        prediction_numeric = predictor.model.predict(X)[0]
        probabilities_array = predictor.model.predict_proba(X)[0]
        
        label_map_numeric = {0: 'Empate', 1: 'Casa', 2: 'Fora'}
        prediction = label_map_numeric[prediction_numeric]
        
        probabilities = {
            'Empate': float(probabilities_array[0]),
            'Casa': float(probabilities_array[1]),
            'Fora': float(probabilities_array[2])
        }
        
        confidence = probabilities[prediction]
        
        # Verificar se acertou
        is_correct = prediction == real_result
        
        if is_correct:
            cup_correct += 1
        cup_total += 1
        
        # Estatísticas por resultado
        cup_by_outcome[prediction]['total'] += 1
        if is_correct:
            cup_by_outcome[prediction]['correct'] += 1
        
        # Estatísticas por confiança
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
        
        cup_by_confidence[bucket]['total'] += 1
        if is_correct:
            cup_by_confidence[bucket]['correct'] += 1
    
    except Exception as e:
        print(f"  ERRO na partida Copa {i}: {e}")
        continue

print()
print("RESULTADOS - DATASET COPA:")
print("-" * 80)
cup_accuracy = cup_correct / cup_total if cup_total > 0 else 0
print(f"Acurácia: {cup_accuracy*100:.2f}% ({cup_correct}/{cup_total})")
print()

# ============================================================================
# RESULTADOS CONSOLIDADOS
# ============================================================================
print("="*80)
print("RESULTADOS CONSOLIDADOS - TODAS AS 3,400 PARTIDAS")
print("="*80)
print()

total_all = db_total + cup_total
total_correct = db_correct + cup_correct
overall_accuracy = total_correct / total_all if total_all > 0 else 0

print(f"ACURÁCIA GERAL: {overall_accuracy*100:.2f}%")
print(f"  Total corretas: {total_correct}/{total_all}")
print()

print("DETALHAMENTO POR FONTE:")
print("-" * 80)
print(f"  Banco de dados:  {db_accuracy*100:.2f}% ({db_correct:4d}/{db_total:4d} partidas)")
print(f"  Dataset Copa:    {cup_accuracy*100:.2f}% ({cup_correct:4d}/{cup_total:4d} partidas)")
print()

# Acurácia por tipo - consolidado
print("ACURÁCIA POR TIPO DE PREDIÇÃO (CONSOLIDADO):")
print("-" * 80)

all_by_outcome = defaultdict(lambda: {'total': 0, 'correct': 0})
for outcome in ['Casa', 'Empate', 'Fora']:
    all_by_outcome[outcome]['total'] = db_by_outcome[outcome]['total'] + cup_by_outcome[outcome]['total']
    all_by_outcome[outcome]['correct'] = db_by_outcome[outcome]['correct'] + cup_by_outcome[outcome]['correct']

for outcome in ['Casa', 'Empate', 'Fora']:
    stats = all_by_outcome[outcome]
    if stats['total'] > 0:
        acc = stats['correct'] / stats['total']
        print(f"  {outcome:10s}: {acc*100:5.1f}% ({stats['correct']:4d}/{stats['total']:4d} predições)")

print()

# Acurácia por confiança - consolidado
print("ACURÁCIA POR NÍVEL DE CONFIANÇA (CONSOLIDADO):")
print("-" * 80)

all_by_confidence = defaultdict(lambda: {'total': 0, 'correct': 0})
buckets_order = ['< 40%', '40-50%', '50-60%', '60-70%', '70-80%', '> 80%']
for bucket in buckets_order:
    all_by_confidence[bucket]['total'] = db_by_confidence[bucket]['total'] + cup_by_confidence[bucket]['total']
    all_by_confidence[bucket]['correct'] = db_by_confidence[bucket]['correct'] + cup_by_confidence[bucket]['correct']

for bucket in buckets_order:
    stats = all_by_confidence[bucket]
    if stats['total'] > 0:
        acc = stats['correct'] / stats['total']
        bar = '=' * int(acc * 50)
        print(f"  {bucket:10s}: {acc*100:5.1f}% ({stats['correct']:4d}/{stats['total']:4d}) {bar}")

print()
print("="*80)
print("COMPARAÇÃO COM BASELINE:")
print("-" * 80)
print(f"  Poisson Baseline:              46.01%")
print(f"  Modelo ML (3,400 partidas):    {overall_accuracy*100:.2f}%")
print(f"  Ganho:                         {(overall_accuracy - 0.4601)*100:+.2f} pontos")
print()
print("="*80)
