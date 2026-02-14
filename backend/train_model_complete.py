"""
Treinamento completo do modelo usando:
1. Dataset de copas (450 partidas FA Cup com 107 features)
2. Partidas do banco de dados (2.957 partidas finalizadas)

Total: ~3.400 partidas para treinamento
"""
import os
import sys
import json
import django
import numpy as np
from datetime import datetime
from collections import Counter

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match

print("="*80)
print("TREINAMENTO COMPLETO DO MODELO ML")
print("="*80)
print()

# ============================================================================
# ETAPA 1: Carregar dataset de copas
# ============================================================================
print("ETAPA 1: Carregando dataset de copas...")
print("-" * 80)

cup_dataset_path = "ml_training/cup_training_dataset.json"
with open(cup_dataset_path, 'r', encoding='utf-8') as f:
    cup_data = json.load(f)

cup_matches = cup_data['matches']
print(f"  Dataset de copas carregado: {len(cup_matches)} partidas")
print(f"  Features por partida: {len(cup_matches[0]['features'])}")
print()

# ============================================================================
# ETAPA 2: Carregar partidas do banco de dados
# ============================================================================
print("ETAPA 2: Carregando partidas do banco de dados...")
print("-" * 80)

db_matches = Match.objects.filter(
    status='finished',
    home_score__isnull=False,
    away_score__isnull=False
).select_related('home_team', 'away_team', 'league')

total_db_matches = db_matches.count()
print(f"  Partidas disponíveis no DB: {total_db_matches}")
print()

# ============================================================================
# ETAPA 3: Extrair features das partidas do DB
# ============================================================================
print("ETAPA 3: Extraindo features das partidas do DB...")
print("-" * 80)
print("  (Usando valores genéricos por enquanto - próxima etapa: calcular reais)")
print()

db_dataset = []
for idx, match in enumerate(db_matches, 1):
    if idx % 500 == 0:
        print(f"  Processadas {idx}/{total_db_matches} partidas...")
    
    # Determinar label (1X2)
    if match.home_score > match.away_score:
        label = 1  # Casa
    elif match.home_score < match.away_score:
        label = 2  # Fora
    else:
        label = 0  # Empate
    
    # Features básicas (expandir depois com cálculos reais)
    features = {
        # Strength (valores genéricos por agora)
        'strength.home_attack_strength': 1.4,
        'strength.away_attack_strength': 1.2,
        'strength.home_defense_strength': 1.1,
        'strength.away_defense_strength': 1.1,
        'strength.home_goals_per_game': 1.5,
        'strength.away_goals_per_game': 1.3,
        'strength.home_conceded_per_game': 1.2,
        'strength.away_conceded_per_game': 1.2,
        'strength.home_advantage_factor': 1.2,
        'strength.strength_differential': 0.2,
        
        # Competition
        'competition.is_cup_competition': 'cup' in match.league.name.lower() if match.league else False,
        'competition.is_knockout_stage': False,
        'competition.knockout_adjustment_factor': 1.0,
        
        # Market (probabilidades balanceadas)
        'market.market_home_prob': 0.40,
        'market.market_draw_prob': 0.30,
        'market.market_away_prob': 0.30,
        'market.bookmaker_margin': 0.05,
        
        # Context
        'context.home_rest_days': 7,
        'context.away_rest_days': 7,
        'context.rest_advantage': 0,
        'context.home_is_fatigued': False,
        'context.away_is_fatigued': False,
        'context.fatigue_impact': 0.0,
        
        # Form (valores neutros)
        'form.home_recent_points': 5,
        'form.away_recent_points': 5,
        'form.home_momentum': 0,
        'form.away_momentum': 0,
        'form.form_differential': 0.0,
        'form.home_weighted_form': 1.5,
        'form.away_weighted_form': 1.5,
        
        # ELO (valores médios)
        'elo.home_elo': 1500,
        'elo.away_elo': 1500,
        'elo.elo_differential': 0,
        
        # H2H (sem histórico)
        'h2h.h2h_games': 0,
        'h2h.h2h_home_wins': 0,
        'h2h.h2h_away_wins': 0,
        'h2h.h2h_draws': 0,
        'h2h.h2h_home_win_rate': 0.33,
        'h2h.h2h_avg_goals': 2.5,
        'h2h.h2h_btts_rate': 0.5,
        
        # Statistics
        'statistics.home_clean_sheet_rate': 0.3,
        'statistics.away_clean_sheet_rate': 0.25,
        'statistics.home_cards_per_game': 2.0,
        'statistics.away_cards_per_game': 2.0,
        
        # Weather
        'weather.temperature': 20.0,
        'weather.has_rain': False,
        'weather.has_snow': False,
        'weather.has_wind': False,
        'weather.weather_impact': 0.0,
        'weather.goal_impact': 0.0,
        
        # Match importance
        'match_importance.home_importance': 5,
        'match_importance.away_importance': 5,
        'match_importance.match_importance': 5.0,
        'match_importance.is_derby': False,
        
        # Motivation
        'motivation.home_motivation': 5.0,
        'motivation.away_motivation': 5.0,
        'motivation.motivation_differential': 0.0,
    }
    
    db_dataset.append({
        'features': features,
        'label': label,
        'result': {
            'home_goals': match.home_score,
            'away_goals': match.away_score,
            'total_goals': match.home_score + match.away_score,
            'winner': 'home' if label == 1 else ('away' if label == 2 else 'draw')
        },
        'teams': {
            'home': match.home_team.name,
            'away': match.away_team.name
        },
        'competition': match.league.name if match.league else 'Unknown',
        'source': 'database'
    })

print(f"  Features extraídas de {len(db_dataset)} partidas do DB")
print()

# ============================================================================
# ETAPA 4: Combinar datasets
# ============================================================================
print("ETAPA 4: Combinando datasets...")
print("-" * 80)

# Marcar fonte nos dados de copa
for match in cup_matches:
    match['source'] = 'cup_dataset'

# Combinar
all_matches = cup_matches + db_dataset
print(f"  Dataset de copas: {len(cup_matches)} partidas")
print(f"  Dataset do DB: {len(db_dataset)} partidas")
print(f"  Total combinado: {len(all_matches)} partidas")
print()

# Distribuição de labels
labels = Counter([m['label'] for m in all_matches])
print("  Distribuição de labels (1X2):")
label_names = {1: 'Casa (1)', 0: 'Empate (X)', 2: 'Fora (2)'}
for label, count in sorted(labels.items()):
    print(f"    {label_names[label]:15s}: {count:4d} ({count/len(all_matches)*100:.1f}%)")
print()

# ============================================================================
# ETAPA 5: Preparar dados para treinamento
# ============================================================================
print("ETAPA 5: Preparando dados para treinamento...")
print("-" * 80)

# Coletar todos os nomes de features
all_feature_names = set()
for match in all_matches:
    all_feature_names.update(match['features'].keys())

feature_names_list = sorted(all_feature_names)
print(f"  Total de features únicas: {len(feature_names_list)}")
print()

# Converter para matriz X e vetor y
X = []
y = []

for match in all_matches:
    # Criar vetor de features (preencher com 0 se feature não existir)
    feature_vector = []
    for feature_name in feature_names_list:
        value = match['features'].get(feature_name, 0)
        
        # Converter booleanos para numéricos
        if isinstance(value, bool):
            value = 1 if value else 0
        # Converter strings para numéricos (categóricos)
        elif isinstance(value, str):
            value = hash(value) % 1000 / 1000.0  # Simples encoding
        
        feature_vector.append(float(value))
    
    X.append(feature_vector)
    y.append(match['label'])

X = np.array(X)
y = np.array(y)

print(f"  Shape de X: {X.shape} (partidas x features)")
print(f"  Shape de y: {y.shape} (partidas)")
print(f"  Classes em y: {sorted(set(y))}")
print()

# ============================================================================
# ETAPA 6: Dividir em treino e teste
# ============================================================================
print("ETAPA 6: Dividindo em treino (80%) e teste (20%)...")
print("-" * 80)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"  Treino: {X_train.shape[0]} partidas")
print(f"  Teste: {X_test.shape[0]} partidas")
print()

# ============================================================================
# ETAPA 7: Treinar modelo XGBoost
# ============================================================================
print("ETAPA 7: Treinando modelo XGBoost...")
print("-" * 80)

try:
    import xgboost as xgb
    from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
    
    print("  Inicializando XGBoost Classifier...")
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='mlogloss',
        verbosity=0
    )
    
    print("  Treinando modelo...")
    model.fit(X_train, y_train)
    print("  Treinamento concluído!")
    print()
    
    # ============================================================================
    # ETAPA 8: Avaliar modelo
    # ============================================================================
    print("ETAPA 8: Avaliando modelo...")
    print("-" * 80)
    
    # Predições no conjunto de treino
    y_train_pred = model.predict(X_train)
    train_accuracy = accuracy_score(y_train, y_train_pred)
    
    # Predições no conjunto de teste
    y_test_pred = model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    
    print(f"  Acurácia no TREINO: {train_accuracy*100:.2f}%")
    print(f"  Acurácia no TESTE:  {test_accuracy*100:.2f}%")
    print()
    
    print("  Relatório de classificação (Teste):")
    print("-" * 80)
    print(classification_report(
        y_test, y_test_pred,
        target_names=['Empate (X)', 'Casa (1)', 'Fora (2)']
    ))
    
    print("  Matriz de confusão (Teste):")
    print("-" * 80)
    cm = confusion_matrix(y_test, y_test_pred)
    print("              Predito")
    print("             X    1    2")
    print(f"Real  X    {cm[0,0]:4d} {cm[0,1]:4d} {cm[0,2]:4d}")
    print(f"      1    {cm[1,0]:4d} {cm[1,1]:4d} {cm[1,2]:4d}")
    print(f"      2    {cm[2,0]:4d} {cm[2,1]:4d} {cm[2,2]:4d}")
    print()
    
    # ============================================================================
    # ETAPA 9: Feature Importance
    # ============================================================================
    print("ETAPA 9: Importância das features (Top 20)...")
    print("-" * 80)
    
    feature_importance = model.feature_importances_
    feature_importance_dict = {
        feature_names_list[i]: importance 
        for i, importance in enumerate(feature_importance)
    }
    
    sorted_features = sorted(
        feature_importance_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    for i, (feature, importance) in enumerate(sorted_features[:20], 1):
        print(f"  {i:2d}. {feature:50s}: {importance:.4f}")
    print()
    
    # ============================================================================
    # ETAPA 10: Salvar modelo
    # ============================================================================
    print("ETAPA 10: Salvando modelo...")
    print("-" * 80)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    model_path = f'ml_training/xgboost_model_{timestamp}.json'
    metadata_path = f'ml_training/model_metadata_{timestamp}.json'
    
    # Salvar modelo
    model.save_model(model_path)
    print(f"  Modelo salvo em: {model_path}")
    
    # Salvar metadados
    metadata = {
        'timestamp': timestamp,
        'total_matches': len(all_matches),
        'cup_matches': len(cup_matches),
        'db_matches': len(db_dataset),
        'features_count': len(feature_names_list),
        'feature_names': feature_names_list,
        'train_size': X_train.shape[0],
        'test_size': X_test.shape[0],
        'train_accuracy': float(train_accuracy),
        'test_accuracy': float(test_accuracy),
        'label_distribution': {
            label_names[k]: v for k, v in labels.items()
        },
        'top_20_features': [
            {'feature': f, 'importance': float(imp)}
            for f, imp in sorted_features[:20]
        ]
    }
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"  Metadados salvos em: {metadata_path}")
    print()
    
    print("="*80)
    print("TREINAMENTO CONCLUÍDO COM SUCESSO!")
    print("="*80)
    print()
    print(f"RESUMO:")
    print(f"  Dataset total: {len(all_matches)} partidas")
    print(f"  Features: {len(feature_names_list)}")
    print(f"  Acurácia treino: {train_accuracy*100:.2f}%")
    print(f"  Acurácia teste: {test_accuracy*100:.2f}%")
    print()
    print(f"Próximos passos:")
    print(f"  1. Integrar modelo no analysis_orchestrator.py")
    print(f"  2. Extrair features REAIS das equipes (força, forma, etc)")
    print(f"  3. Testar com partidas futuras")
    print()
    
except ImportError:
    print("  ERRO: xgboost não instalado")
    print("  Execute: pip install xgboost scikit-learn")
    print()
except Exception as e:
    print(f"  ERRO durante treinamento: {e}")
    import traceback
    traceback.print_exc()
