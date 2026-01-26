"""
Validação REAL do modelo ML usando features já coletadas no dataset
Não recorre à API - usa os dados históricos que já temos
"""
import os
import sys
import django
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.ml_integration import ModelEnsembleML

def validate_ml_with_collected_data():
    """Valida modelo ML com o dataset coletado (880 partidas)"""
    
    print("="*80)
    print("VALIDACAO DO MODELO ML COM DADOS COLETADOS")
    print("="*80)
    
    # Carregar dataset completo
    dataset_path = Path(__file__).parent / 'ml_training' / 'training_dataset.json'
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    data = dataset['data']
    print(f"\nDataset: {len(data)} partidas")
    print(f"Distribuicao real:")
    print(f"  Casa: {sum(1 for x in data if x['label']==0)} (44.5%)")
    print(f"  Empate: {sum(1 for x in data if x['label']==1)} (25.2%)")
    print(f"  Fora: {sum(1 for x in data if x['label']==2)} (30.2%)")
    
    # Carregar modelo ML
    ensemble = ModelEnsembleML()
    
    # Validar com TODAS as partidas do dataset
    print(f"\nValidando com {len(data)} partidas...\n")
    
    correct_ml = 0
    correct_poisson_only = 0
    correct_consensus = 0
    
    predictions = []
    
    for i, match_data in enumerate(data):
        try:
            # Features JÁ ENGINEERED (não precisa API!)
            features = match_data['features']
            actual_label = match_data['label']
            
            # 1. Predição Ensemble Completo (Poisson + ML + Market)
            strength = features.get('strength', {})
            prediction = ensemble.predict(
                features=features,
                home_strength=strength.get('home_goals_per_game', 1.2),
                away_strength=strength.get('away_goals_per_game', 1.2),
                weather_impact=0.0
            )
            
            # Consensus (ensemble completo)
            consensus = prediction['consensus']
            consensus_pred = max(
                [(0, consensus['home_win']), (1, consensus['draw']), (2, consensus['away_win'])],
                key=lambda x: x[1]
            )[0]
            
            # 2. ML puro
            ml = prediction['ml']
            ml_pred = max(
                [(0, ml['home_win']), (1, ml['draw']), (2, ml['away_win'])],
                key=lambda x: x[1]
            )[0]
            
            # 3. Poisson puro
            poisson = prediction['poisson']['probabilities']
            poisson_pred = max(
                [(0, poisson['home_win']), (1, poisson['draw']), (2, poisson['away_win'])],
                key=lambda x: x[1]
            )[0]
            
            # Contar acertos
            if consensus_pred == actual_label:
                correct_consensus += 1
            if ml_pred == actual_label:
                correct_ml += 1
            if poisson_pred == actual_label:
                correct_poisson_only += 1
            
            predictions.append({
                'match': f"{match_data['teams']['home']} vs {match_data['teams']['away']}",
                'actual': actual_label,
                'consensus': consensus_pred,
                'ml': ml_pred,
                'poisson': poisson_pred,
                'consensus_probs': consensus,
                'ml_probs': ml
            })
            
            if (i+1) % 100 == 0:
                print(f"Processadas: {i+1}/{len(data)}")
        
        except Exception as e:
            print(f"Erro na partida {i+1}: {e}")
            continue
    
    # Resultados
    print(f"\n{'='*80}")
    print("RESULTADOS DA VALIDACAO")
    print(f"{'='*80}")
    
    total = len(predictions)
    
    print(f"\n1. ENSEMBLE COMPLETO (Poisson 20% + ML 50% + Market 30%):")
    print(f"   Acertos: {correct_consensus}/{total}")
    print(f"   Acuracia: {correct_consensus/total*100:.1f}%")
    
    print(f"\n2. ML PURO (XGBoost):")
    print(f"   Acertos: {correct_ml}/{total}")
    print(f"   Acuracia: {correct_ml/total*100:.1f}%")
    
    print(f"\n3. POISSON PURO (Baseline):")
    print(f"   Acertos: {correct_poisson_only}/{total}")
    print(f"   Acuracia: {correct_poisson_only/total*100:.1f}%")
    
    print(f"\n{'='*80}")
    print("MELHORIA VS BASELINE")
    print(f"{'='*80}")
    print(f"Ensemble vs Poisson: +{(correct_consensus-correct_poisson_only)/total*100:.1f}pp")
    print(f"ML vs Poisson: +{(correct_ml-correct_poisson_only)/total*100:.1f}pp")
    
    # Análise por tipo de resultado
    print(f"\n{'='*80}")
    print("ANALISE POR TIPO DE RESULTADO")
    print(f"{'='*80}")
    
    for label, label_name in [(0, 'Casa'), (1, 'Empate'), (2, 'Fora')]:
        actual_count = sum(1 for p in predictions if p['actual'] == label)
        consensus_correct = sum(1 for p in predictions if p['actual'] == label and p['consensus'] == label)
        ml_correct = sum(1 for p in predictions if p['actual'] == label and p['ml'] == label)
        
        print(f"\n{label_name} ({actual_count} partidas):")
        print(f"  Ensemble: {consensus_correct}/{actual_count} ({consensus_correct/actual_count*100 if actual_count else 0:.1f}%)")
        print(f"  ML Puro: {ml_correct}/{actual_count} ({ml_correct/actual_count*100 if actual_count else 0:.1f}%)")
    
    # Exemplos de acertos
    print(f"\n{'='*80}")
    print("EXEMPLOS DE PREVISOES CORRETAS DO ML")
    print(f"{'='*80}")
    
    correct_samples = [p for p in predictions if p['ml'] == p['actual']][:5]
    for sample in correct_samples:
        label_names = ['Casa', 'Empate', 'Fora']
        print(f"\n{sample['match']}")
        print(f"  Resultado: {label_names[sample['actual']]}")
        print(f"  ML previu: Casa={sample['ml_probs']['home_win']*100:.1f}%, Empate={sample['ml_probs']['draw']*100:.1f}%, Fora={sample['ml_probs']['away_win']*100:.1f}%")
    
    print(f"\n{'='*80}")

if __name__ == '__main__':
    validate_ml_with_collected_data()
