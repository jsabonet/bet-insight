"""
Calibração Automática de Pesos do Ensemble - FASE 2
Encontra pesos ótimos via grid search + validação cruzada

Uso:
    python calibrate_ensemble_weights.py

Resultado:
    - Pesos ótimos salvos em calibration_weights.json
    - Métricas de validação
    - Gráficos de performance
"""

import numpy as np
import pandas as pd
import json
import logging
from pathlib import Path
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnsembleWeightOptimizer:
    """
    Otimiza pesos do ensemble Poisson + ML + Market.
    """
    
    def __init__(self):
        self.best_weights = None
        self.best_accuracy = 0
        self.validation_results = []
    
    def load_predictions(self, data_path='ml_training/validation_predictions.pkl'):
        """
        Carrega predições dos 3 modelos para validação.
        
        Estrutura esperada:
        {
            'poisson': array([[p_home, p_draw, p_away], ...]),
            'ml': array([[p_home, p_draw, p_away], ...]),
            'market': array([[p_home, p_draw, p_away], ...]),
            'labels': array([0, 2, 1, ...])  # 0=home, 1=draw, 2=away
        }
        """
        if not Path(data_path).exists():
            logger.error(f"❌ Arquivo não encontrado: {data_path}")
            logger.info("💡 Execute primeiro: python generate_validation_predictions.py")
            return None
        
        data = joblib.load(data_path)
        logger.info(f"✅ Carregadas {len(data['labels'])} predições para calibração")
        return data
    
    def optimize_weights_grid_search(self, poisson_preds, ml_preds, market_preds, labels):
        """
        Grid search para encontrar pesos ótimos.
        
        Args:
            poisson_preds: array (n_samples, 3)
            ml_preds: array (n_samples, 3)
            market_preds: array (n_samples, 3)
            labels: array (n_samples,)
        
        Returns:
            dict: Melhores pesos e acurácia
        """
        logger.info("🔍 Iniciando grid search...")
        
        best_acc = 0
        best_weights = None
        all_results = []
        
        # Grid de busca (granularidade 0.05)
        step = 0.05
        
        for w_poisson in np.arange(0.20, 0.80, step):
            for w_ml in np.arange(0.10, 0.60, step):
                w_market = 1.0 - w_poisson - w_ml
                
                # Restrições
                if w_market < 0 or w_market > 0.50:
                    continue
                
                # Calcular consensus
                consensus = (
                    poisson_preds * w_poisson +
                    ml_preds * w_ml +
                    market_preds * w_market
                )
                
                # Predição (argmax)
                predictions = np.argmax(consensus, axis=1)
                
                # Métricas
                accuracy = accuracy_score(labels, predictions)
                precision = precision_score(labels, predictions, average='weighted', zero_division=0)
                recall = recall_score(labels, predictions, average='weighted', zero_division=0)
                f1 = f1_score(labels, predictions, average='weighted', zero_division=0)
                
                # Calcular distribuição de predições
                pred_dist = np.bincount(predictions, minlength=3) / len(predictions)
                true_dist = np.bincount(labels, minlength=3) / len(labels)
                
                # Viés de distribuição (queremos minimizar)
                dist_bias = np.abs(pred_dist - true_dist).mean()
                
                result = {
                    'weights': {
                        'poisson': round(w_poisson, 2),
                        'ml': round(w_ml, 2),
                        'market': round(w_market, 2)
                    },
                    'accuracy': accuracy,
                    'precision': precision,
                    'recall': recall,
                    'f1': f1,
                    'dist_bias': dist_bias,
                    'pred_dist': {
                        'home': float(pred_dist[0]),
                        'draw': float(pred_dist[1]),
                        'away': float(pred_dist[2])
                    }
                }
                
                all_results.append(result)
                
                # Atualizar melhor
                if accuracy > best_acc:
                    best_acc = accuracy
                    best_weights = result['weights'].copy()
                    logger.info(f"🎯 Novo melhor: {best_weights} → {best_acc*100:.2f}%")
        
        logger.info(f"✅ Grid search completo: {len(all_results)} combinações testadas")
        
        return {
            'best_weights': best_weights,
            'best_accuracy': best_acc,
            'all_results': all_results
        }
    
    def cross_validate_weights(self, poisson_preds, ml_preds, market_preds, labels, n_splits=5):
        """
        Valida pesos usando K-Fold cross-validation.
        
        Retorna média dos pesos ótimos em cada fold.
        """
        logger.info(f"🔄 Validação cruzada com {n_splits} folds...")
        
        kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
        fold_results = []
        
        for fold_idx, (train_idx, val_idx) in enumerate(kf.split(poisson_preds), 1):
            logger.info(f"\n📊 Fold {fold_idx}/{n_splits}")
            
            # Dados de treino/validação
            poisson_train = poisson_preds[train_idx]
            ml_train = ml_preds[train_idx]
            market_train = market_preds[train_idx]
            labels_train = labels[train_idx]
            
            poisson_val = poisson_preds[val_idx]
            ml_val = ml_preds[val_idx]
            market_val = market_preds[val_idx]
            labels_val = labels[val_idx]
            
            # Otimizar no treino
            result = self.optimize_weights_grid_search(
                poisson_train, ml_train, market_train, labels_train
            )
            
            fold_weights = result['best_weights']
            
            # Avaliar na validação
            consensus_val = (
                poisson_val * fold_weights['poisson'] +
                ml_val * fold_weights['ml'] +
                market_val * fold_weights['market']
            )
            
            preds_val = np.argmax(consensus_val, axis=1)
            val_accuracy = accuracy_score(labels_val, preds_val)
            
            fold_results.append({
                'fold': fold_idx,
                'weights': fold_weights,
                'train_accuracy': result['best_accuracy'],
                'val_accuracy': val_accuracy
            })
            
            logger.info(f"   Pesos: {fold_weights}")
            logger.info(f"   Treino: {result['best_accuracy']*100:.2f}%")
            logger.info(f"   Validação: {val_accuracy*100:.2f}%")
        
        # Média dos pesos
        avg_weights = {
            'poisson': np.mean([r['weights']['poisson'] for r in fold_results]),
            'ml': np.mean([r['weights']['ml'] for r in fold_results]),
            'market': np.mean([r['weights']['market'] for r in fold_results])
        }
        
        avg_train_acc = np.mean([r['train_accuracy'] for r in fold_results])
        avg_val_acc = np.mean([r['val_accuracy'] for r in fold_results])
        
        logger.info(f"\n✅ Validação Cruzada Completa:")
        logger.info(f"   Pesos médios: {avg_weights}")
        logger.info(f"   Acurácia treino: {avg_train_acc*100:.2f}%")
        logger.info(f"   Acurácia validação: {avg_val_acc*100:.2f}%")
        logger.info(f"   Overfitting: {(avg_train_acc - avg_val_acc)*100:.2f}%")
        
        return {
            'avg_weights': avg_weights,
            'avg_train_accuracy': avg_train_acc,
            'avg_val_accuracy': avg_val_acc,
            'fold_results': fold_results
        }
    
    def analyze_context_specific_weights(self, poisson_preds, ml_preds, market_preds, labels, context_confidences):
        """
        Analisa se pesos devem mudar baseado em confiança do contexto.
        
        Args:
            context_confidences: array (n_samples,) com valores 0.0-1.0
        """
        logger.info("\n🎯 Analisando pesos específicos por contexto...")
        
        # Dividir em 3 grupos: fraco, moderado, forte
        weak_mask = context_confidences < 0.65
        moderate_mask = (context_confidences >= 0.65) & (context_confidences < 0.80)
        strong_mask = context_confidences >= 0.80
        
        results = {}
        
        for name, mask in [('weak', weak_mask), ('moderate', moderate_mask), ('strong', strong_mask)]:
            if mask.sum() < 10:
                logger.info(f"   ⚠️ {name}: Poucos exemplos ({mask.sum()})")
                continue
            
            result = self.optimize_weights_grid_search(
                poisson_preds[mask],
                ml_preds[mask],
                market_preds[mask],
                labels[mask]
            )
            
            results[name] = result['best_weights']
            logger.info(f"   {name.upper()}: {result['best_weights']} → {result['best_accuracy']*100:.2f}%")
        
        return results
    
    def save_results(self, results, output_path='calibration_weights.json'):
        """
        Salva resultados da calibração.
        """
        results['timestamp'] = datetime.now().isoformat()
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n💾 Resultados salvos em: {output_path}")


def main():
    """
    Executa calibração completa.
    """
    logger.info("="*80)
    logger.info("🎯 CALIBRAÇÃO DE PESOS DO ENSEMBLE")
    logger.info("="*80)
    
    optimizer = EnsembleWeightOptimizer()
    
    # 1. Carregar predições
    data = optimizer.load_predictions()
    
    if data is None:
        logger.error("\n❌ Impossível continuar sem dados de validação")
        logger.info("\n💡 Como gerar dados de validação:")
        logger.info("   1. Execute: python generate_validation_predictions.py")
        logger.info("   2. Isso criará ml_training/validation_predictions.pkl")
        logger.info("   3. Execute este script novamente")
        return
    
    poisson_preds = data['poisson']
    ml_preds = data['ml']
    market_preds = data['market']
    labels = data['labels']
    
    # 2. Grid search simples
    logger.info("\n" + "="*80)
    logger.info("ETAPA 1: Grid Search")
    logger.info("="*80)
    
    grid_result = optimizer.optimize_weights_grid_search(
        poisson_preds, ml_preds, market_preds, labels
    )
    
    # 3. Validação cruzada
    logger.info("\n" + "="*80)
    logger.info("ETAPA 2: Validação Cruzada")
    logger.info("="*80)
    
    cv_result = optimizer.cross_validate_weights(
        poisson_preds, ml_preds, market_preds, labels, n_splits=5
    )
    
    # 4. Pesos por contexto (se disponível)
    context_weights = {}
    if 'context_confidences' in data:
        logger.info("\n" + "="*80)
        logger.info("ETAPA 3: Pesos por Contexto")
        logger.info("="*80)
        
        context_weights = optimizer.analyze_context_specific_weights(
            poisson_preds, ml_preds, market_preds, labels,
            data['context_confidences']
        )
    
    # 5. Salvar resultados
    final_results = {
        'method': 'cross_validation',
        'recommended_weights': cv_result['avg_weights'],
        'accuracy': cv_result['avg_val_accuracy'],
        'grid_search': {
            'best_weights': grid_result['best_weights'],
            'accuracy': grid_result['best_accuracy']
        },
        'cross_validation': cv_result,
        'context_specific': context_weights,
        'comparison_with_current': {
            'current': {
                'poisson': 0.50,
                'ml': 0.30,
                'market': 0.20
            },
            'improvement': cv_result['avg_val_accuracy'] - 0.51  # Baseline atual
        }
    }
    
    optimizer.save_results(final_results)
    
    # 6. Resumo final
    logger.info("\n" + "="*80)
    logger.info("📊 RESUMO FINAL")
    logger.info("="*80)
    logger.info(f"\n🎯 PESOS RECOMENDADOS:")
    logger.info(f"   Poisson: {cv_result['avg_weights']['poisson']*100:.0f}%")
    logger.info(f"   ML:      {cv_result['avg_weights']['ml']*100:.0f}%")
    logger.info(f"   Market:  {cv_result['avg_weights']['market']*100:.0f}%")
    logger.info(f"\n📈 ACURÁCIA:")
    logger.info(f"   Validação: {cv_result['avg_val_accuracy']*100:.2f}%")
    logger.info(f"   Melhora:   +{(cv_result['avg_val_accuracy'] - 0.51)*100:.2f}%")
    logger.info(f"\n💡 PRÓXIMOS PASSOS:")
    logger.info(f"   1. Atualizar apps/analysis/config/analysis_config.py")
    logger.info(f"   2. Testar com: python test_ml_integration.py")
    logger.info(f"   3. Validar em produção por 100 jogos")
    logger.info("="*80)


if __name__ == '__main__':
    main()
