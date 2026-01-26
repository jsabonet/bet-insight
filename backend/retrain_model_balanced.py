#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RETREINAMENTO DO MODELO ML COM CLASS WEIGHTS BALANCEADOS
Corrige o vies de DRAW (52.7% predicoes vs 25.2% real)
"""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from xgboost import XGBClassifier
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))

def load_dataset():
    """Carrega dataset de 880 partidas"""
    dataset_path = Path(__file__).parent / 'ml_training' / 'training_dataset.json'
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset_json = json.load(f)
    
    return dataset_json["data"]

def prepare_features(data):
    """
    Prepara features e labels para treino (usando abordagem do train_ml_model.py)
    """
    import pandas as pd
    
    # Converter para DataFrame
    rows = []
    for match in data:
        row = {
            'fixture_id': match['fixture_id'],
            'label': match['label'],
            **match['features']  # Unpack todas as features
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Separar features e labels
    feature_cols = [col for col in df.columns 
                   if col not in ['fixture_id', 'label']]
    
    X = df[feature_cols].copy()
    y = df['label'].copy()
    
    # Converter para numeric
    X = X.apply(pd.to_numeric, errors='coerce')
    
    # Preencher missing com mediana
    X = X.fillna(X.median())
    
    # Remover features com variancia zero
    zero_var_cols = X.columns[X.var() == 0].tolist()
    if zero_var_cols:
        print(f"  Removendo {len(zero_var_cols)} features com variancia zero")
        X = X.drop(columns=zero_var_cols)
    
    print(f"  Features finais: {X.shape[1]}")
    
    return X.values, y.values, feature_cols

def retrain_model_with_balance():
    """
    Retreina modelo XGBoost com class weights balanceados
    """
    print("\n" + "="*80)
    print("RETREINAMENTO DO MODELO ML COM CLASS WEIGHTS")
    print("="*80)
    
    # Carregar dataset
    print("\n[1/6] Carregando dataset...")
    data = load_dataset()
    print(f"      Dataset: {len(data)} partidas")
    
    # Preparar features
    print("\n[2/6] Preparando features...")
    X, y, feature_cols = prepare_features(data)
    
    # Analise de distribuicao
    print("\n[3/6] Analisando distribuicao de classes...")
    class_dist = Counter(y)
    print(f"\nDistribuicao de labels:")
    print(f"  HOME (0): {class_dist[0]} ({100*class_dist[0]/len(y):.1f}%)")
    print(f"  DRAW (1): {class_dist[1]} ({100*class_dist[1]/len(y):.1f}%)")
    print(f"  AWAY (2): {class_dist[2]} ({100*class_dist[2]/len(y):.1f}%)")
    
    # Calcular class weights
    classes = np.unique(y)
    class_weights = compute_class_weight('balanced', classes=classes, y=y)
    class_weight_dict = {i: w for i, w in enumerate(class_weights)}
    
    print(f"\nClass Weights Calculados:")
    print(f"  HOME (0): {class_weight_dict[0]:.3f}")
    print(f"  DRAW (1): {class_weight_dict[1]:.3f}")
    print(f"  AWAY (2): {class_weight_dict[2]:.3f}")
    
    # Split train/test
    print("\n[4/6] Dividindo em treino/teste...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"  Treino: {len(X_train)} partidas")
    print(f"  Teste: {len(X_test)} partidas")
    
    # Treinar modelo COM class weights
    print("\n[5/6] Treinando XGBoost COM class weights...")
    
    # Converter class_weights para sample_weights
    sample_weights = np.array([class_weight_dict[label] for label in y_train])
    
    model_balanced = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='mlogloss',
        early_stopping_rounds=20
    )
    
    model_balanced.fit(
        X_train, y_train,
        sample_weight=sample_weights,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    # Avaliar modelo balanceado
    y_pred_balanced = model_balanced.predict(X_test)
    accuracy_balanced = (y_pred_balanced == y_test).mean() * 100
    
    pred_dist_balanced = Counter(y_pred_balanced)
    
    print(f"\n  Acuracia no teste: {accuracy_balanced:.2f}%")
    print(f"  Distribuicao de predicoes:")
    print(f"    HOME: {pred_dist_balanced[0]} ({100*pred_dist_balanced[0]/len(y_pred_balanced):.1f}%)")
    print(f"    DRAW: {pred_dist_balanced[1]} ({100*pred_dist_balanced[1]/len(y_pred_balanced):.1f}%)")
    print(f"    AWAY: {pred_dist_balanced[2]} ({100*pred_dist_balanced[2]/len(y_pred_balanced):.1f}%)")
    
    # Comparar com modelo original (sem weights)
    print("\n  Treinando modelo SEM class weights (baseline)...")
    model_baseline = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='mlogloss',
        early_stopping_rounds=20
    )
    
    model_baseline.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    y_pred_baseline = model_baseline.predict(X_test)
    accuracy_baseline = (y_pred_baseline == y_test).mean() * 100
    
    pred_dist_baseline = Counter(y_pred_baseline)
    
    print(f"\n  COMPARACAO:")
    print(f"    Baseline (sem weights): {accuracy_baseline:.2f}%")
    print(f"    Balanceado (com weights): {accuracy_balanced:.2f}%")
    print(f"    Diferenca: {accuracy_balanced - accuracy_baseline:+.2f}% pontos")
    
    print(f"\n  Distribuicao Baseline:")
    print(f"    HOME: {pred_dist_baseline[0]} ({100*pred_dist_baseline[0]/len(y_pred_baseline):.1f}%)")
    print(f"    DRAW: {pred_dist_baseline[1]} ({100*pred_dist_baseline[1]/len(y_pred_baseline):.1f}%)")
    print(f"    AWAY: {pred_dist_baseline[2]} ({100*pred_dist_baseline[2]/len(y_pred_baseline):.1f}%)")
    
    # Salvar modelo balanceado
    print("\n[6/6] Salvando modelo balanceado...")
    
    model_path = Path(__file__).parent / 'ml_training' / 'trained_models' / 'xgboost_1x2_balanced.pkl'
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    joblib.dump({
        'model': model_balanced,
        'feature_cols': feature_cols,
        'class_weights': class_weight_dict,
        'accuracy': accuracy_balanced,
        'distribution': pred_dist_balanced
    }, model_path)
    
    print(f"      Modelo salvo em: {model_path}")
    
    # Salvar relatorio
    report = {
        'model_path': str(model_path),
        'accuracy_balanced': float(accuracy_balanced),
        'accuracy_baseline': float(accuracy_baseline),
        'improvement': float(accuracy_balanced - accuracy_baseline),
        'class_weights': {int(k): float(v) for k, v in class_weight_dict.items()},
        'distribution_balanced': {int(k): int(v) for k, v in pred_dist_balanced.items()},
        'distribution_baseline': {int(k): int(v) for k, v in pred_dist_baseline.items()},
        'distribution_real': {int(k): int(v) for k, v in class_dist.items()}
    }
    
    report_file = Path("retrain_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"      Relatorio salvo em: {report_file}")
    
    print("\n" + "="*80)
    print("RETREINAMENTO CONCLUIDO!")
    print("="*80)
    print(f"\nProximos passos:")
    print(f"1. Revise {report_file}")
    print(f"2. Atualize ml_integration.py para usar: {model_path.name}")
    print(f"3. Execute validation_100_matches.py para validar")
    print(f"4. Execute validation_with_orchestrator.py para validar sistema completo")
    print()

if __name__ == "__main__":
    retrain_model_with_balance()
