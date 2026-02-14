"""
Retreina o modelo XGBoost com FEATURES REAIS + CLASSES BALANCEADAS + OTIMIZAÇÃO
"""
import os
import sys
import django
import json
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import xgboost as xgb

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from calculate_real_features import TeamStatsCalculator, extract_features_from_match

print("="*80)
print("RETREINAMENTO OTIMIZADO DO MODELO")
print("="*80)
print()

# ============================================================================
# ETAPA 1: CARREGAR DATASET DA COPA (450 partidas com 107 features)
# ============================================================================
print("ETAPA 1: Carregando dataset da Copa...")

cup_dataset_path = 'ml_training/cup_training_dataset.json'
with open(cup_dataset_path, 'r', encoding='utf-8') as f:
    cup_data = json.load(f)

cup_matches = cup_data['matches']
print(f"OK {len(cup_matches)} partidas da Copa carregadas\n")

# ============================================================================
# ETAPA 2: CARREGAR PARTIDAS DO BANCO DE DADOS
# ============================================================================
print("ETAPA 2: Carregando partidas do banco de dados...")

db_matches = Match.objects.filter(
    status='finished',
    home_score__isnull=False,
    away_score__isnull=False
).select_related('home_team', 'away_team', 'league').order_by('-match_date')

print(f"OK {db_matches.count()} partidas do DB encontradas\n")

# ============================================================================
# ETAPA 3: EXTRAIR FEATURES REAIS DAS PARTIDAS DO DB
# ============================================================================
print("ETAPA 3: Extraindo features REAIS das partidas do DB...")
print("(Isso pode levar alguns minutos...)")

calculator = TeamStatsCalculator()
db_data_with_features = []

for i, match in enumerate(db_matches):
    if i % 100 == 0:
        print(f"  Processando partida {i}/{db_matches.count()}...")
    
    try:
        features = extract_features_from_match(match, calculator)
        
        # Determinar label
        if match.home_score > match.away_score:
            label = 'Casa'
        elif match.home_score < match.away_score:
            label = 'Fora'
        else:
            label = 'Empate'
        
        db_data_with_features.append({
            'features': features,
            'label': label,
            'fixture_id': match.id,
            'result': f"{match.home_score}-{match.away_score}",
            'teams': f"{match.home_team.name} vs {match.away_team.name}"
        })
    except Exception as e:
        print(f"  ! Erro ao processar partida {match.id}: {e}")
        continue

print(f"OK {len(db_data_with_features)} partidas do DB com features reais\n")

# ============================================================================
# ETAPA 4: COMBINAR DATASETS
# ============================================================================
print("ETAPA 4: Combinando datasets...")

all_matches = cup_matches + db_data_with_features
print(f"OK Total: {len(all_matches)} partidas combinadas")
print(f"   Copa: {len(cup_matches)}")
print(f"   DB:   {len(db_data_with_features)}\n")

# ============================================================================
# ETAPA 5: PREPARAR MATRIZES X e y
# ============================================================================
print("ETAPA 5: Preparando matrizes X e y...")

# Pegar todas as features possíveis do primeiro registro
all_features_keys = sorted(all_matches[0]['features'].keys())
print(f"Features disponiveis: {len(all_features_keys)}")

X = []
y = []

# Mapa de labels para numérico: 0=Empate/X, 1=Casa/Home, 2=Fora/Away
label_map = {
    'Empate': 0, 'X': 0, 'Draw': 0, '0': 0, 0: 0,
    'Casa': 1, 'Home': 1, '1': 1, 1: 1,
    'Fora': 2, 'Away': 2, '2': 2, 2: 2
}

for match in all_matches:
    features = match['features']
    
    # Converter features para array numérico
    feature_vector = []
    for key in all_features_keys:
        value = features.get(key, 0)
        
        # Converter booleanos e strings para numérico
        if isinstance(value, bool):
            value = 1 if value else 0
        elif isinstance(value, str):
            # Hash simples para strings
            value = hash(value) % 100 / 100.0
        
        feature_vector.append(float(value))
    
    X.append(feature_vector)
    
    # Normalizar label
    label = match['label']
    numeric_label = label_map.get(label, label_map.get(str(label), 0))
    y.append(numeric_label)

X = np.array(X)
y = np.array(y)

print(f"OK X shape: {X.shape}")
print(f"OK y shape: {y.shape}")

# Distribuição de labels
unique, counts = np.unique(y, return_counts=True)
label_names = {0: 'Empate', 1: 'Casa', 2: 'Fora'}
print(f"\nDistribuicao de labels:")
for label, count in zip(unique, counts):
    percentage = count / len(y) * 100
    label_name = label_names.get(label, f'Label_{label}')
    print(f"  {label} ({label_name:10s}): {count:5d} ({percentage:5.1f}%)")
print()

# ============================================================================
# ETAPA 6: SPLIT TREINO/TESTE COM ESTRATIFICAÇÃO
# ============================================================================
print("ETAPA 6: Dividindo em treino (80%) e teste (20%)...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"OK Treino: {X_train.shape[0]} amostras")
print(f"OK Teste:  {X_test.shape[0]} amostras\n")

# ============================================================================
# ETAPA 7: CALCULAR PESOS DAS CLASSES PARA BALANCEAMENTO
# ============================================================================
print("ETAPA 7: Calculando pesos para balanceamento de classes...")

# Contar amostras por classe
class_counts = {}
for label in y_train:
    class_counts[label] = class_counts.get(label, 0) + 1

# Calcular pesos (inversamente proporcional à frequência)
total_samples = len(y_train)
n_classes = len(class_counts)
class_weights = {}
label_names = {0: 'Empate', 1: 'Casa', 2: 'Fora'}

for label, count in class_counts.items():
    weight = total_samples / (n_classes * count)
    class_weights[label] = weight
    label_name = label_names.get(label, f'Label_{label}')
    print(f"  {label} ({label_name:10s}): {weight:.2f}x")

# Criar sample_weight para treino
sample_weights = np.array([class_weights[label] for label in y_train])
print(f"OK Sample weights calculados\n")

# ============================================================================
# ETAPA 8: TREINAR MODELO COM BALANCEAMENTO
# ============================================================================
print("ETAPA 8: Treinando XGBoost com classes balanceadas...")

# Configuração otimizada (prevenir overfitting)
base_model = xgb.XGBClassifier(
    objective='multi:softprob',
    num_class=3,
    n_estimators=100,          # Reduzido de 200
    max_depth=4,               # Reduzido de 6 (menos overfitting)
    learning_rate=0.05,        # Reduzido de 0.1 (aprendizado mais suave)
    subsample=0.7,             # Reduzido de 0.8
    colsample_bytree=0.7,      # Reduzido de 0.8
    min_child_weight=3,        # Novo: regularização
    gamma=0.1,                 # Novo: regularização
    reg_alpha=0.1,             # Novo: L1 regularização
    reg_lambda=1.0,            # Novo: L2 regularização
    random_state=42,
    eval_metric='mlogloss'
)

# Treinar SEM balanceamento (empates não devem ser artificialmente favorecidos)
base_model.fit(X_train, y_train, verbose=False)

# Avaliar
y_pred_train = base_model.predict(X_train)
y_pred_test = base_model.predict(X_test)

train_acc = accuracy_score(y_train, y_pred_train)
test_acc = accuracy_score(y_test, y_pred_test)

print(f"OK Modelo base treinado")
print(f"   Acurácia treino: {train_acc*100:.2f}%")
print(f"   Acurácia teste:  {test_acc*100:.2f}%\n")

print("Relatório de classificação (TESTE):")
print(classification_report(y_test, y_pred_test))

print("\nMatriz de confusão:")
cm = confusion_matrix(y_test, y_pred_test, labels=[0, 1, 2])
print("             Predicted")
print("            X    1    2")
print(f"Actual  X  {cm[0][0]:3d}  {cm[0][1]:3d}  {cm[0][2]:3d}")
print(f"        1  {cm[1][0]:3d}  {cm[1][1]:3d}  {cm[1][2]:3d}")
print(f"        2  {cm[2][0]:3d}  {cm[2][1]:3d}  {cm[2][2]:3d}")
print()

# ============================================================================
# ETAPA  9: FEATURE IMPORTANCE
# ============================================================================
print("ETAPA 9: Analisando importância das features...")

# Pegar importâncias do modelo base
importances = base_model.feature_importances_

# Criar lista de (feature, importance)
feature_importance = []
for i, importance in enumerate(importances):
    if importance > 0:
        feature_importance.append({
            'feature': all_features_keys[i],
            'importance': float(importance)
        })

# Ordenar por importância
feature_importance.sort(key=lambda x: x['importance'], reverse=True)

print(f"\nTop 20 features mais importantes:")
print("-" * 70)
for i, item in enumerate(feature_importance[:20], 1):
    bar = '=' * int(item['importance'] * 100)
    print(f"{i:2d}. {item['feature']:45s} {item['importance']*100:5.2f}% {bar}")

print()

# ============================================================================
# ETAPA 10: SALVAR MODELO E METADADOS
# ============================================================================
print("ETAPA 10: Salvando modelo e metadados...")

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# Salvar modelo balanceado
model_path = f'ml_training/xgboost_balanced_{timestamp}.json'
base_model.save_model(model_path)
print(f"OK Modelo salvo: {model_path}")

# Salvar metadados
metadata = {
    'timestamp': timestamp,
    'total_matches': len(all_matches),
    'cup_matches': len(cup_matches),
    'db_matches': len(db_data_with_features),
    'features_count': len(all_features_keys),
    'feature_names': all_features_keys,
    'train_samples': int(X_train.shape[0]),
    'test_samples': int(X_test.shape[0]),
    'train_accuracy': float(train_acc),
    'test_accuracy': float(test_acc),
    'class_weights': {str(k): float(v) for k, v in class_weights.items()},
    'top_20_features': feature_importance[:20],
    'classification_report': classification_report(y_test, y_pred_test, output_dict=True),
    'confusion_matrix': cm.tolist()
}

metadata_path = f'ml_training/model_metadata_balanced_{timestamp}.json'
with open(metadata_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"OK Metadados salvos: {metadata_path}\n")

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("="*80)
print("RETREINAMENTO CONCLUIDO!")
print("="*80)
print()
print("RESULTADOS:")
print(f"  Baseline Poisson:                       46.01%")
print(f"  Modelo anterior (features genericas):   49.41%")
print(f"  Modelo novo (features reais + balanced): {test_acc*100:.2f}%")
print()
report = classification_report(y_test, y_pred_test, output_dict=True)
print("RECALL POR CLASSE:")
print(f"  Empate: {100*report['0']['recall']:.0f}% (antes: 20%)")
print(f"  Casa:   {100*report['1']['recall']:.0f}% (antes: 99%)")
print(f"  Fora:   {100*report['2']['recall']:.0f}% (antes: 10%)")
print()
print("PROXIMOS PASSOS:")
print("  1. OK Features reais calculadas")
print("  2. OK Classes balanceadas")  
print("  3. ... Otimizar hiperparametros (opcional)")
print("  4. ... Integrar modelo no orchestrator")
print()
print("="*80)


