#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Validação de 880 Partidas com Ensemble ML
Analisa todas as 880 partidas do dataset completo
usando ModelEnsembleML para validar acurácia do modelo treinado
"""

import json
import os
import sys
from pathlib import Path

# Adicionar diretório do projeto ao path
sys.path.insert(0, os.path.dirname(__file__))

from apps.analysis.services.ml_integration import ModelEnsembleML

def validate_880_matches():
    """
    Carrega todas as 880 partidas do dataset e valida com o ensemble
    """
    # Caminhos
    backend_dir = Path(__file__).parent
    dataset_path = backend_dir / "ml_training" / "training_dataset.json"
    model_path = backend_dir / "ml_training" / "trained_models" / "xgboost_1x2.pkl"
    
    # Verificar arquivos
    if not dataset_path.exists():
        print(f"[ERRO] Dataset nao encontrado: {dataset_path}")
        return
    
    if not model_path.exists():
        print(f"[ERRO] Modelo nao encontrado: {model_path}")
        return
    
    # Carregar dataset
    print("\n[*] Carregando dataset...")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset_json = json.load(f)
    
    all_data = dataset_json["data"]  # Extrair a chave "data"
    
    print(f"[OK] Dataset carregado: {len(all_data)} partidas totais")
    
    # Usar todas as partidas do dataset
    test_data = all_data
    print(f"[>>] Usando TODAS as {len(test_data)} partidas para validacao completa\n")
    
    # Inicializar ensemble
    print("[*] Inicializando ModelEnsembleML...")
    try:
        ensemble = ModelEnsembleML()
        print("[OK] Ensemble inicializado\n")
    except Exception as e:
        print(f"[ERRO] Erro ao inicializar ensemble: {e}")
        return
    
    # Validar
    print("=" * 60)
    print("VALIDAÇÃO DE 880 PARTIDAS COMPLETAS")
    print("=" * 60)
    print()
    
    correct = 0
    total = len(test_data)
    results_by_outcome = {"HOME": {"correct": 0, "total": 0},
                          "DRAW": {"correct": 0, "total": 0},
                          "AWAY": {"correct": 0, "total": 0}}
    
    for i, match in enumerate(test_data, 1):
        try:
            # Extrair features e strength do match
            features = match['features']
            actual = match.get('label')  # label é o resultado real (0=HOME, 1=DRAW, 2=AWAY)
            
            # Extrair strength para os parâmetros obrigatórios
            home_strength = features.get('strength.home_goals_per_game', 1.2)
            away_strength = features.get('strength.away_goals_per_game', 1.2)
            
            # Fazer predição com ensemble
            prediction = ensemble.predict(
                features=features,
                home_strength=home_strength,
                away_strength=away_strength,
                weather_impact=0.0
            )
            
            # Extrair predição do consensus (ensemble completo)
            consensus = prediction['consensus']
            consensus_pred = max(
                [(0, consensus['home_win']), (1, consensus['draw']), (2, consensus['away_win'])],
                key=lambda x: x[1]
            )[0]
            
            predicted_result = consensus_pred
            
            # Verificar se acertou
            is_correct = (predicted_result == actual)
            
            if is_correct:
                correct += 1
            
            # Contar por tipo de resultado
            outcome_map = {0: "HOME", 1: "DRAW", 2: "AWAY"}
            actual_outcome = outcome_map.get(actual, "UNKNOWN")
            
            if actual_outcome in results_by_outcome:
                results_by_outcome[actual_outcome]["total"] += 1
                if is_correct:
                    results_by_outcome[actual_outcome]["correct"] += 1
            
            # Log a cada 50 partidas
            if i % 50 == 0:
                print(f"[{i:3d}/{total}] Processadas: {i} partidas | Acertos: {correct}/{i} ({100*correct/i:.1f}%)")
        
        except Exception as e:
            print(f"[ERRO] Erro na partida {i}: {e}")
            continue
    
    # Resultados finais
    print()
    print("=" * 60)
    print("RESULTADOS FINAIS")
    print("=" * 60)
    
    accuracy = (correct / total) * 100 if total > 0 else 0
    print(f"\n[RESULTADO] Acuracia Global: {correct}/{total} ({accuracy:.1f}%)\n")
    
    print("Detalhamento por resultado:")
    for outcome, data in results_by_outcome.items():
        if data["total"] > 0:
            outcome_accuracy = (data["correct"] / data["total"]) * 100
            print(f"  {outcome:5s}: {data['correct']:3d}/{data['total']:3d} ({outcome_accuracy:5.1f}%)")
    
    print()
    print("=" * 60)
    
    # Salvar resultado
    result_file = Path("validation_880_results.txt")
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(f"VALIDAÇÃO DE 880 PARTIDAS COMPLETAS\n")
        f.write(f"===================================\n\n")
        f.write(f"Acurácia Global: {correct}/{total} ({accuracy:.1f}%)\n\n")
        f.write(f"Resultados por tipo:\n")
        for outcome, data in results_by_outcome.items():
            if data["total"] > 0:
                outcome_accuracy = (data["correct"] / data["total"]) * 100
                f.write(f"  {outcome}: {data['correct']}/{data['total']} ({outcome_accuracy:.1f}%)\n")
    
    print(f"\n[OK] Resultados salvos em: {result_file}")

if __name__ == "__main__":
    validate_880_matches()
