#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CALIBRACAO DE THRESHOLD PARA CORRIGIR VIES DE DRAW
Ajusta o threshold de decisao para corrigir o vies de empate (52.7% -> 25.2%)
"""
import os
import sys
import json
import numpy as np
from pathlib import Path
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))

from apps.analysis.services.ml_integration import ModelEnsembleML

def load_dataset():
    """Carrega dataset de 880 partidas"""
    dataset_path = Path(__file__).parent / 'ml_training' / 'training_dataset.json'
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset_json = json.load(f)
    
    return dataset_json["data"]

def apply_threshold_calibration(probs, threshold_draw):
    """
    Aplica threshold calibrado para decisao
    
    Args:
        probs: dict com home_win, draw, away_win
        threshold_draw: threshold minimo para aceitar draw (ex: 0.40)
    
    Returns:
        label predito (0=HOME, 1=DRAW, 2=AWAY)
    """
    p_home = probs['home_win']
    p_draw = probs['draw']
    p_away = probs['away_win']
    
    # Se draw nao atingir threshold, escolher entre home/away
    if p_draw < threshold_draw:
        # Escolher entre home e away (ignorar draw)
        if p_home > p_away:
            return 0  # HOME
        else:
            return 2  # AWAY
    else:
        # Draw atingiu threshold, aplicar logica normal
        max_prob = max(p_home, p_draw, p_away)
        if max_prob == p_home:
            return 0
        elif max_prob == p_draw:
            return 1
        else:
            return 2

def test_threshold(data, threshold_draw):
    """
    Testa um threshold especifico
    
    Returns:
        dict com accuracy, distribuicao, etc
    """
    ensemble = ModelEnsembleML()
    
    predictions = []
    actuals = []
    pred_distribution = Counter()
    
    for match in data:
        try:
            features = match['features']
            actual_label = match.get('label')
            
            home_strength = features.get('strength.home_goals_per_game', 1.2)
            away_strength = features.get('strength.away_goals_per_game', 1.2)
            
            prediction = ensemble.predict(
                features=features,
                home_strength=home_strength,
                away_strength=away_strength,
                weather_impact=0.0
            )
            
            consensus = prediction['consensus']
            
            # Aplicar threshold calibrado
            predicted_label = apply_threshold_calibration(consensus, threshold_draw)
            
            predictions.append(predicted_label)
            actuals.append(actual_label)
            pred_distribution[predicted_label] += 1
            
        except Exception as e:
            continue
    
    # Calcular acuracia
    correct = sum(1 for p, a in zip(predictions, actuals) if p == a)
    accuracy = (correct / len(actuals)) * 100 if actuals else 0
    
    # Calcular acuracia por classe
    accuracy_by_class = {}
    for label in [0, 1, 2]:
        label_correct = sum(1 for p, a in zip(predictions, actuals) if p == label and a == label)
        label_total = sum(1 for a in actuals if a == label)
        accuracy_by_class[label] = (label_correct / label_total * 100) if label_total > 0 else 0
    
    return {
        'threshold': threshold_draw,
        'accuracy': accuracy,
        'correct': correct,
        'total': len(actuals),
        'distribution': {
            'HOME': pred_distribution[0],
            'DRAW': pred_distribution[1],
            'AWAY': pred_distribution[2]
        },
        'distribution_pct': {
            'HOME': (pred_distribution[0] / len(actuals)) * 100,
            'DRAW': (pred_distribution[1] / len(actuals)) * 100,
            'AWAY': (pred_distribution[2] / len(actuals)) * 100
        },
        'accuracy_by_class': {
            'HOME': accuracy_by_class[0],
            'DRAW': accuracy_by_class[1],
            'AWAY': accuracy_by_class[2]
        }
    }

def calibrate_threshold():
    """
    Calibra threshold de draw para maximizar acuracia
    """
    print("\n" + "="*80)
    print("CALIBRACAO DE THRESHOLD DE DRAW")
    print("="*80)
    
    # Carregar dataset
    print("\n[1/3] Carregando dataset...")
    data = load_dataset()
    print(f"      Dataset: {len(data)} partidas")
    
    # Distribuicao real
    actual_distribution = Counter()
    for match in data:
        actual_distribution[match['label']] += 1
    
    print(f"\nDistribuicao REAL:")
    print(f"  HOME: {actual_distribution[0]} ({100*actual_distribution[0]/len(data):.1f}%)")
    print(f"  DRAW: {actual_distribution[1]} ({100*actual_distribution[1]/len(data):.1f}%)")
    print(f"  AWAY: {actual_distribution[2]} ({100*actual_distribution[2]/len(data):.1f}%)")
    
    # Testar diferentes thresholds
    print("\n[2/3] Testando thresholds...")
    
    thresholds = np.arange(0.25, 0.75, 0.05)  # De 25% a 75% em steps de 5%
    results = []
    
    best_accuracy = 0
    best_result = None
    
    for threshold in thresholds:
        result = test_threshold(data, threshold)
        results.append(result)
        
        print(f"\nThreshold {threshold:.2f}:")
        print(f"  Acuracia: {result['accuracy']:.2f}%")
        print(f"  Distribuicao: HOME {result['distribution_pct']['HOME']:.1f}% | "
              f"DRAW {result['distribution_pct']['DRAW']:.1f}% | "
              f"AWAY {result['distribution_pct']['AWAY']:.1f}%")
        
        if result['accuracy'] > best_accuracy:
            best_accuracy = result['accuracy']
            best_result = result
            print(f"  >>> MELHOR ATE AGORA!")
    
    # Resultados
    print("\n" + "="*80)
    print("RESULTADOS DA CALIBRACAO")
    print("="*80)
    
    print(f"\nMELHOR THRESHOLD: {best_result['threshold']:.2f}")
    print(f"Acuracia: {best_result['accuracy']:.2f}%")
    
    print(f"\nDistribuicao de Predicoes:")
    print(f"  HOME: {best_result['distribution']['HOME']} ({best_result['distribution_pct']['HOME']:.1f}%)")
    print(f"  DRAW: {best_result['distribution']['DRAW']} ({best_result['distribution_pct']['DRAW']:.1f}%)")
    print(f"  AWAY: {best_result['distribution']['AWAY']} ({best_result['distribution_pct']['AWAY']:.1f}%)")
    
    print(f"\nAcuracia por Classe:")
    print(f"  HOME: {best_result['accuracy_by_class']['HOME']:.1f}%")
    print(f"  DRAW: {best_result['accuracy_by_class']['DRAW']:.1f}%")
    print(f"  AWAY: {best_result['accuracy_by_class']['AWAY']:.1f}%")
    
    # Comparar com baseline (sem threshold)
    baseline = test_threshold(data, 0.0)  # threshold 0 = logica normal
    
    print(f"\nCOMPARACAO:")
    print(f"  Baseline (sem threshold): {baseline['accuracy']:.2f}%")
    print(f"  Com threshold {best_result['threshold']:.2f}: {best_result['accuracy']:.2f}%")
    print(f"  Melhoria: {best_result['accuracy'] - baseline['accuracy']:+.2f}% pontos")
    
    # Salvar resultados
    print("\n[3/3] Salvando resultados...")
    
    best_config = {
        'threshold_draw': best_result['threshold'],
        'accuracy': best_result['accuracy'],
        'distribution': best_result['distribution'],
        'distribution_pct': best_result['distribution_pct'],
        'accuracy_by_class': best_result['accuracy_by_class'],
        'improvement_over_baseline': best_result['accuracy'] - baseline['accuracy']
    }
    
    config_file = Path("calibration_threshold.json")
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(best_config, f, indent=2)
    
    all_results_file = Path("calibration_threshold_all_results.json")
    with open(all_results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'best': best_config,
            'all_results': results
        }, f, indent=2)
    
    print(f"      Melhor config: {config_file}")
    print(f"      Todos resultados: {all_results_file}")
    
    print("\n" + "="*80)
    print("CALIBRACAO CONCLUIDA!")
    print("="*80)
    print(f"\nProximos passos:")
    print(f"1. Revise {config_file}")
    print(f"2. Implemente threshold em ml_integration.py")
    print(f"3. Valide com validation_with_orchestrator.py")
    print()

if __name__ == "__main__":
    calibrate_threshold()
