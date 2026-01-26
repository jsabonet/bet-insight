#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ANALISE DO DECISION ENGINE
Investiga por que o Decision Engine esta errando tanto (25% vs 65% do Ensemble)
"""
import os
import sys
import json
import django
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.ml_integration import ModelEnsembleML
from apps.analysis.services.decision_engine import DecisionEngine
from apps.analysis.services.statistical_models import PoissonBivariateModel

def load_dataset():
    """Carrega dataset de 880 partidas"""
    dataset_path = Path(__file__).parent / 'ml_training' / 'training_dataset.json'
    
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset_json = json.load(f)
    
    return dataset_json["data"]

def analyze_decision_engine_behavior():
    """
    Analisa como o Decision Engine esta tomando decisoes
    e compara com o Ensemble puro
    """
    print("\n" + "="*80)
    print("ANALISE DO DECISION ENGINE")
    print("="*80)
    
    # Carregar dataset
    print("\n[1/5] Carregando dataset...")
    data = load_dataset()
    print(f"      Dataset: {len(data)} partidas")
    
    # Inicializar componentes
    print("\n[2/5] Inicializando componentes...")
    ensemble = ModelEnsembleML()
    decision_engine = DecisionEngine()
    poisson = PoissonBivariateModel()
    
    # Estatisticas
    stats = {
        'ensemble_correct': 0,
        'decision_correct': 0,
        'total': 0,
        'ensemble_predictions': Counter(),
        'decision_predictions': Counter(),
        'decision_markets': Counter(),
        'actual_results': Counter(),
        'disagreements': 0,
        'decision_reasons': Counter(),
        'confidence_distribution': Counter(),
        'errors_by_confidence': defaultdict(int),
        'errors_total_by_confidence': defaultdict(int)
    }
    
    # Mapear labels para nomes
    label_map = {0: 'HOME', 1: 'DRAW', 2: 'AWAY'}
    
    print("\n[3/5] Analisando decisoes em 880 partidas...")
    
    for i, match in enumerate(data, 1):
        try:
            # Features e resultado real
            features = match['features']
            actual_label = match.get('label')  # 0=HOME, 1=DRAW, 2=AWAY
            actual_name = label_map[actual_label]
            
            # Strength
            home_strength = features.get('strength.home_goals_per_game', 1.2)
            away_strength = features.get('strength.away_goals_per_game', 1.2)
            
            # 1. Predicao do Ensemble puro
            prediction = ensemble.predict(
                features=features,
                home_strength=home_strength,
                away_strength=away_strength,
                weather_impact=0.0
            )
            
            consensus = prediction['consensus']
            ensemble_pred = max(
                [(0, consensus['home_win']), (1, consensus['draw']), (2, consensus['away_win'])],
                key=lambda x: x[1]
            )[0]
            ensemble_correct = (ensemble_pred == actual_label)
            
            # 2. Decisao do Decision Engine
            # Criar model_predictions completo
            model_predictions = {
                'consensus': consensus,
                'poisson': prediction['poisson'],
                'ml': prediction['ml']
            }
            
            # Market odds vazios (como no validation_with_orchestrator quando nao ha odds)
            market_odds = {}
            
            # Fazer decisao
            decision_result = decision_engine.make_decision(
                model_predictions=model_predictions,
                features=features,
                market_odds=market_odds,
                strategy='value'
            )
            
            recommendation = decision_result['recommendation']
            confidence = decision_result['confidence']
            
            # Mapear recomendacao para label
            decision_market = recommendation['market']
            decision_map = {'home_win': 0, 'draw': 1, 'away_win': 2}
            
            # Se recomendacao nao e 1X2, usar consensus
            if decision_market not in decision_map:
                decision_pred = ensemble_pred  # Fallback
                decision_name = label_map[decision_pred]
            else:
                decision_pred = decision_map[decision_market]
                decision_name = label_map[decision_pred]
            
            decision_correct = (decision_pred == actual_label)
            
            # Estatisticas
            stats['total'] += 1
            if ensemble_correct:
                stats['ensemble_correct'] += 1
            if decision_correct:
                stats['decision_correct'] += 1
            
            stats['ensemble_predictions'][label_map[ensemble_pred]] += 1
            stats['decision_predictions'][decision_name] += 1
            stats['actual_results'][actual_name] += 1
            stats['decision_markets'][decision_market] += 1
            stats['decision_reasons'][recommendation.get('reason', 'unknown')] += 1
            stats['confidence_distribution'][confidence['level']] += 1
            
            # Contar erros por confianca
            conf_level = confidence['level']
            stats['errors_total_by_confidence'][conf_level] += 1
            if not decision_correct:
                stats['errors_by_confidence'][conf_level] += 1
            
            if ensemble_pred != decision_pred:
                stats['disagreements'] += 1
            
            # Progress
            if i % 100 == 0:
                ens_acc = (stats['ensemble_correct'] / stats['total']) * 100
                dec_acc = (stats['decision_correct'] / stats['total']) * 100
                print(f"[{i}/{len(data)}] Ensemble: {ens_acc:.1f}% | Decision: {dec_acc:.1f}%")
        
        except Exception as e:
            print(f"Erro na partida {i}: {e}")
            continue
    
    # Resultados
    print("\n" + "="*80)
    print("RESULTADOS DA ANALISE")
    print("="*80)
    
    ens_acc = (stats['ensemble_correct'] / stats['total']) * 100
    dec_acc = (stats['decision_correct'] / stats['total']) * 100
    
    print(f"\nACURACIA:")
    print(f"  Ensemble puro: {stats['ensemble_correct']}/{stats['total']} ({ens_acc:.2f}%)")
    print(f"  Decision Engine: {stats['decision_correct']}/{stats['total']} ({dec_acc:.2f}%)")
    print(f"  Diferenca: {ens_acc - dec_acc:+.2f}% pontos")
    
    print(f"\nDISCORDANCIAS:")
    print(f"  Ensemble e Decision discordaram em {stats['disagreements']}/{stats['total']} casos ({100*stats['disagreements']/stats['total']:.1f}%)")
    
    print(f"\nDISTRIBUICAO DE PREDICOES:")
    print(f"\n  Ensemble:")
    for outcome, count in stats['ensemble_predictions'].most_common():
        pct = (count / stats['total']) * 100
        print(f"    {outcome}: {count} ({pct:.1f}%)")
    
    print(f"\n  Decision Engine:")
    for outcome, count in stats['decision_predictions'].most_common():
        pct = (count / stats['total']) * 100
        print(f"    {outcome}: {count} ({pct:.1f}%)")
    
    print(f"\n  Real (Actual):")
    for outcome, count in stats['actual_results'].most_common():
        pct = (count / stats['total']) * 100
        print(f"    {outcome}: {count} ({pct:.1f}%)")
    
    print(f"\nMERCADOS RECOMENDADOS:")
    for market, count in stats['decision_markets'].most_common():
        pct = (count / stats['total']) * 100
        print(f"  {market}: {count} ({pct:.1f}%)")
    
    print(f"\nRAZOES DAS DECISOES:")
    for reason, count in stats['decision_reasons'].most_common():
        pct = (count / stats['total']) * 100
        print(f"  {reason}: {count} ({pct:.1f}%)")
    
    print(f"\nCONFIANCA:")
    for level, count in stats['confidence_distribution'].most_common():
        pct = (count / stats['total']) * 100
        errors = stats['errors_by_confidence'][level]
        total = stats['errors_total_by_confidence'][level]
        error_rate = (errors / total * 100) if total > 0 else 0
        accuracy = 100 - error_rate
        print(f"  {level}: {count} ({pct:.1f}%) - Acuracia: {accuracy:.1f}%")
    
    # Salvar analise
    print("\n[4/5] Salvando analise...")
    result_file = Path("decision_engine_analysis.json")
    with open(result_file, 'w', encoding='utf-8') as f:
        # Converter Counters para dicts
        json_stats = {
            'ensemble_accuracy': ens_acc,
            'decision_accuracy': dec_acc,
            'difference': ens_acc - dec_acc,
            'disagreements': stats['disagreements'],
            'total_matches': stats['total'],
            'ensemble_predictions': dict(stats['ensemble_predictions']),
            'decision_predictions': dict(stats['decision_predictions']),
            'actual_results': dict(stats['actual_results']),
            'decision_markets': dict(stats['decision_markets']),
            'decision_reasons': dict(stats['decision_reasons']),
            'confidence_distribution': dict(stats['confidence_distribution']),
            'accuracy_by_confidence': {
                level: 100 - (stats['errors_by_confidence'][level] / stats['errors_total_by_confidence'][level] * 100)
                for level in stats['errors_total_by_confidence'].keys()
            }
        }
        json.dump(json_stats, f, indent=2)
    
    print(f"      Analise salva em: {result_file}")
    
    # Diagnostico
    print("\n[5/5] DIAGNOSTICO:")
    print("="*80)
    
    if dec_acc < ens_acc:
        print(f"\nPROBLEMA: Decision Engine esta PIORANDO a acuracia em {ens_acc - dec_acc:.1f}% pontos!")
        print("\nPOSSIVEIS CAUSAS:")
        
        # Verificar se esta recomendando mercados nao-1X2
        non_1x2_count = sum(count for market, count in stats['decision_markets'].items() 
                           if market not in ['home_win', 'draw', 'away_win'])
        if non_1x2_count > stats['total'] * 0.1:
            print(f"  1. Recomendando mercados nao-1X2 em {100*non_1x2_count/stats['total']:.1f}% dos casos")
            print(f"     (BTTS, Over/Under, etc nao sao contabilizados na acuracia 1X2)")
        
        # Verificar vies
        most_predicted = stats['decision_predictions'].most_common(1)[0]
        if most_predicted[1] > stats['total'] * 0.5:
            print(f"  2. VIES: Prevendo '{most_predicted[0]}' em {100*most_predicted[1]/stats['total']:.1f}% dos casos")
            actual_freq = stats['actual_results'][most_predicted[0]]
            print(f"     (Frequencia real: {100*actual_freq/stats['total']:.1f}%)")
        
        # Verificar confianca vs acuracia
        print(f"  3. Confianca nao correlaciona com acuracia:")
        for level in ['very_high', 'high', 'medium', 'low', 'very_low']:
            if level in stats['errors_total_by_confidence']:
                total = stats['errors_total_by_confidence'][level]
                errors = stats['errors_by_confidence'][level]
                acc = 100 - (errors / total * 100) if total > 0 else 0
                print(f"     {level}: {acc:.1f}% acuracia")
    
    print("\n" + "="*80)
    print("ANALISE CONCLUIDA!")
    print("="*80)
    print(f"\nProximos passos:")
    print(f"1. Revisar decision_engine_analysis.json")
    print(f"2. Ajustar logica do _generate_recommendation")
    print(f"3. Calibrar parametros de confianca e risco")
    print()

if __name__ == "__main__":
    analyze_decision_engine_behavior()
