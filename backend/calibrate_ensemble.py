#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CALIBRACAO AUTOMATICA DO ENSEMBLE
Encontra os melhores pesos para Poisson + ML + Market usando Grid Search
"""
import os
import sys
import json
import numpy as np
from pathlib import Path
from itertools import product
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from apps.analysis.services.ml_integration import ModelEnsembleML

def load_dataset():
    """Carrega dataset de 880 partidas"""
    dataset_path = Path(__file__).parent / 'ml_training' / 'training_dataset.json'
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset_json = json.load(f)
    
    return dataset_json["data"]

def calculate_accuracy(predictions, actuals):
    """Calcula acuracia"""
    correct = sum(1 for p, a in zip(predictions, actuals) if p == a)
    return (correct / len(actuals)) * 100 if actuals else 0

def evaluate_weights(data, weight_poisson, weight_ml, weight_market, max_samples=880):
    """
    Avalia uma combinacao de pesos testando contra o dataset
    
    Args:
        data: Dataset de partidas
        weight_poisson: Peso do modelo Poisson (0-100)
        weight_ml: Peso do modelo ML (0-100) 
        weight_market: Peso do Market Odds (0-100)
        max_samples: Numero maximo de partidas para testar (para velocidade)
    
    Returns:
        accuracy: Acuracia percentual
    """
    # Criar ensemble normal
    ensemble = ModelEnsembleML()
    
    # Converter pesos para decimais
    w_p = weight_poisson / 100
    w_m = weight_ml / 100
    w_k = weight_market / 100
    
    predictions = []
    actuals = []
    
    # Limitar amostras para velocidade
    test_data = data[:max_samples]
    
    for i, match in enumerate(test_data, 1):
        try:
            # Extrair features e label
            features = match['features']
            actual_label = match.get('label')  # 0=HOME, 1=DRAW, 2=AWAY
            
            # Extrair strength
            home_strength = features.get('strength.home_goals_per_game', 1.2)
            away_strength = features.get('strength.away_goals_per_game', 1.2)
            
            # Fazer predicao
            prediction = ensemble.predict(
                features=features,
                home_strength=home_strength,
                away_strength=away_strength,
                weather_impact=0.0
            )
            
            # Recalcular consensus com pesos customizados
            poisson_probs = prediction['poisson']['probabilities']
            ml_probs = prediction['ml']
            market_probs = {
                'home_win': features.get('market', {}).get('market_home_prob', 0.33),
                'draw': features.get('market', {}).get('market_draw_prob', 0.33),
                'away_win': features.get('market', {}).get('market_away_prob', 0.33)
            }
            
            # Aplicar pesos customizados
            custom_consensus = {
                'home_win': (
                    poisson_probs['home_win'] * w_p +
                    ml_probs['home_win'] * w_m +
                    market_probs['home_win'] * w_k
                ),
                'draw': (
                    poisson_probs['draw'] * w_p +
                    ml_probs['draw'] * w_m +
                    market_probs['draw'] * w_k
                ),
                'away_win': (
                    poisson_probs['away_win'] * w_p +
                    ml_probs['away_win'] * w_m +
                    market_probs['away_win'] * w_k
                )
            }
            
            # Extrair predicao do custom consensus
            predicted_label = max(
                [(0, custom_consensus['home_win']), (1, custom_consensus['draw']), (2, custom_consensus['away_win'])],
                key=lambda x: x[1]
            )[0]
            
            predictions.append(predicted_label)
            actuals.append(actual_label)
            
        except Exception as e:
            continue
    
    # Calcular acuracia
    accuracy = calculate_accuracy(predictions, actuals)
    return accuracy

def grid_search_weights(data, step=10):
    """
    Grid Search para encontrar os melhores pesos
    
    Args:
        data: Dataset de partidas
        step: Incremento dos pesos (default 10 = teste a cada 10%)
    
    Returns:
        best_weights: Dicionario com os melhores pesos e acuracia
    """
    print("\n" + "="*80)
    print("CALIBRACAO AUTOMATICA - GRID SEARCH")
    print("="*80)
    print(f"\nDataset: {len(data)} partidas")
    print(f"Step: {step}% (testara {int(100/step + 1)**3} combinacoes)")
    print("\nIniciando busca...\n")
    
    best_accuracy = 0
    best_weights = None
    all_results = []
    
    # Gerar todas as combinacoes de pesos que somam 100
    weights_range = range(0, 101, step)
    total_combinations = 0
    tested = 0
    
    # Contar total de combinacoes validas
    for w_poisson in weights_range:
        for w_ml in weights_range:
            w_market = 100 - w_poisson - w_ml
            if 0 <= w_market <= 100:
                total_combinations += 1
    
    print(f"Total de combinacoes validas: {total_combinations}\n")
    
    # Testar todas as combinacoes
    for w_poisson in weights_range:
        for w_ml in weights_range:
            w_market = 100 - w_poisson - w_ml
            
            # Pesos devem somar 100
            if w_market < 0 or w_market > 100:
                continue
            
            tested += 1
            
            # Avaliar esta combinacao
            accuracy = evaluate_weights(data, w_poisson, w_ml, w_market)
            
            result = {
                'poisson': w_poisson,
                'ml': w_ml,
                'market': w_market,
                'accuracy': accuracy
            }
            all_results.append(result)
            
            # Atualizar melhor resultado
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_weights = result
                print(f"\n>>> NOVA MELHOR CONFIGURACAO ENCONTRADA!")
                print(f"    Poisson: {w_poisson}% | ML: {w_ml}% | Market: {w_market}%")
                print(f"    Acuracia: {accuracy:.2f}%\n")
            
            # Progresso
            if tested % 10 == 0:
                print(f"[{tested}/{total_combinations}] Testado: P={w_poisson}% ML={w_ml}% M={w_market}% -> {accuracy:.2f}%")
    
    return best_weights, all_results

def save_results(best_weights, all_results):
    """Salva resultados da calibracao"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salvar melhor configuracao
    best_config_file = Path("calibration_best_weights.json")
    with open(best_config_file, 'w', encoding='utf-8') as f:
        json.dump(best_weights, f, indent=2)
    
    # Salvar todos os resultados
    all_results_file = Path(f"calibration_all_results_{timestamp}.json")
    with open(all_results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': timestamp,
            'best': best_weights,
            'all_results': sorted(all_results, key=lambda x: x['accuracy'], reverse=True)
        }, f, indent=2)
    
    return best_config_file, all_results_file

def main():
    """Funcao principal"""
    print("\n" + "="*80)
    print("SISTEMA DE CALIBRACAO AUTOMATICA")
    print("Otimizando pesos do Ensemble (Poisson + ML + Market)")
    print("="*80)
    
    # Carregar dataset
    print("\n[1/4] Carregando dataset...")
    data = load_dataset()
    print(f"      Dataset carregado: {len(data)} partidas")
    
    # Grid Search
    print("\n[2/4] Executando Grid Search...")
    best_weights, all_results = grid_search_weights(data, step=10)
    
    # Mostrar resultados
    print("\n" + "="*80)
    print("RESULTADOS DA CALIBRACAO")
    print("="*80)
    print(f"\nMELHOR CONFIGURACAO ENCONTRADA:")
    print(f"  Poisson: {best_weights['poisson']}%")
    print(f"  ML:      {best_weights['ml']}%")
    print(f"  Market:  {best_weights['market']}%")
    print(f"  Acuracia: {best_weights['accuracy']:.2f}%")
    
    # Comparar com configuracao atual
    print(f"\nCONFIGURACAO ATUAL (antes da calibracao):")
    print(f"  Poisson: 20%")
    print(f"  ML:      50%")
    print(f"  Market:  30%")
    current_accuracy = evaluate_weights(data, 20, 50, 30)
    print(f"  Acuracia: {current_accuracy:.2f}%")
    
    improvement = best_weights['accuracy'] - current_accuracy
    print(f"\nMELHORIA: {improvement:+.2f}% pontos percentuais")
    
    # Top 10 configuracoes
    print(f"\nTOP 10 CONFIGURACOES:")
    top_10 = sorted(all_results, key=lambda x: x['accuracy'], reverse=True)[:10]
    for i, config in enumerate(top_10, 1):
        print(f"  #{i}: P={config['poisson']:3d}% ML={config['ml']:3d}% M={config['market']:3d}% -> {config['accuracy']:.2f}%")
    
    # Salvar resultados
    print("\n[3/4] Salvando resultados...")
    best_file, all_file = save_results(best_weights, all_results)
    print(f"      Melhor configuracao: {best_file}")
    print(f"      Todos os resultados: {all_file}")
    
    # Teste final com melhor configuracao
    print("\n[4/4] Validacao final com melhor configuracao...")
    final_accuracy = evaluate_weights(data, best_weights['poisson'], best_weights['ml'], best_weights['market'])
    print(f"      Acuracia final: {final_accuracy:.2f}%")
    
    print("\n" + "="*80)
    print("CALIBRACAO CONCLUIDA!")
    print("="*80)
    print(f"\nProximos passos:")
    print(f"1. Revise os resultados em: {best_file}")
    print(f"2. Atualize ml_integration.py com os novos pesos")
    print(f"3. Execute validation_with_orchestrator.py para validar")
    print()

if __name__ == "__main__":
    main()
