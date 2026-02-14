"""
Balanceamento de Dataset com SMOTE - FASE 3
Synthetic Minority Over-sampling Technique para corrigir viés de classes

Uso:
    python balance_dataset_smote.py --input ml_training/training_dataset.json

Resultado:
    - Dataset balanceado salvo
    - Modelo retreinado com dados balanceados
    - Comparação de métricas antes/depois
"""

import numpy as np
import pandas as pd
import json
import logging
from pathlib import Path
from datetime import datetime
import argparse
from collections import Counter

# Verificar se imbalanced-learn está instalado
try:
    from imblearn.over_sampling import SMOTE
    from imblearn.over_sampling import ADASYN, BorderlineSMOTE
except ImportError:
    print("❌ Erro: imbalanced-learn não está instalado")
    print("\n💡 Instale com:")
    print("   pip install imbalanced-learn")
    exit(1)

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import xgboost as xgb
import joblib

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class DatasetBalancer:
    """
    Balanceia dataset usando SMOTE para reduzir viés de classes.
    """
    
    def __init__(self):
        self.original_data = None
        self.balanced_data = None
        self.feature_names = None
    
    def load_dataset(self, file_path):
        """
        Carrega dataset de treinamento.
        
        Suporta JSON ou CSV.
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"❌ Arquivo não encontrado: {file_path}")
            return None
        
        logger.info(f"📂 Carregando: {path.name}")
        
        try:
            if path.suffix == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Converter para DataFrame
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = pd.DataFrame([data])
                
            elif path.suffix == '.csv':
                df = pd.read_csv(path)
            
            else:
                logger.error(f"❌ Formato não suportado: {path.suffix}")
                return None
            
            logger.info(f"✅ Carregados {len(df)} exemplos")
            
            # Verificar distribuição de classes
            if 'result' in df.columns:
                dist = df['result'].value_counts().sort_index()
                logger.info(f"\n📊 Distribuição original:")
                logger.info(f"   Home (0): {dist.get(0, 0)} ({dist.get(0, 0)/len(df)*100:.1f}%)")
                logger.info(f"   Draw (1): {dist.get(1, 0)} ({dist.get(1, 0)/len(df)*100:.1f}%)")
                logger.info(f"   Away (2): {dist.get(2, 0)} ({dist.get(2, 0)/len(df)*100:.1f}%)")
            
            self.original_data = df
            return df
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar: {e}")
            return None
    
    def prepare_features(self, df):
        """
        Prepara features e labels para balanceamento.
        """
        if 'result' not in df.columns:
            logger.error("❌ Coluna 'result' não encontrada")
            return None, None
        
        # Separar features e labels
        y = df['result'].values
        
        # Identificar colunas numéricas (excluindo result)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if 'result' in numeric_cols:
            numeric_cols.remove('result')
        
        if len(numeric_cols) == 0:
            logger.error("❌ Nenhuma feature numérica encontrada")
            return None, None
        
        X = df[numeric_cols].values
        self.feature_names = numeric_cols
        
        logger.info(f"✅ Preparados {X.shape[0]} exemplos com {X.shape[1]} features")
        
        return X, y
    
    def balance_with_smote(self, X, y, method='smote', sampling_strategy='auto'):
        """
        Balanceia dataset usando SMOTE ou variações.
        
        Args:
            method: 'smote', 'borderline', ou 'adasyn'
            sampling_strategy: 'auto' (balanceia todas), dict customizado, ou 'minority'
        """
        logger.info(f"\n🔄 Balanceando com {method.upper()}...")
        logger.info(f"   Estratégia: {sampling_strategy}")
        
        # Verificar distribuição antes
        dist_before = Counter(y)
        logger.info(f"\n📊 Antes do balanceamento:")
        for label, count in sorted(dist_before.items()):
            logger.info(f"   Classe {label}: {count} ({count/len(y)*100:.1f}%)")
        
        # Escolher método
        if method == 'smote':
            sampler = SMOTE(
                sampling_strategy=sampling_strategy,
                random_state=42,
                k_neighbors=5
            )
        elif method == 'borderline':
            sampler = BorderlineSMOTE(
                sampling_strategy=sampling_strategy,
                random_state=42,
                k_neighbors=5
            )
        elif method == 'adasyn':
            sampler = ADASYN(
                sampling_strategy=sampling_strategy,
                random_state=42,
                n_neighbors=5
            )
        else:
            logger.error(f"❌ Método desconhecido: {method}")
            return None, None
        
        try:
            # Aplicar SMOTE
            X_balanced, y_balanced = sampler.fit_resample(X, y)
            
            # Verificar distribuição depois
            dist_after = Counter(y_balanced)
            logger.info(f"\n📊 Depois do balanceamento:")
            for label, count in sorted(dist_after.items()):
                logger.info(f"   Classe {label}: {count} ({count/len(y_balanced)*100:.1f}%)")
            
            # Mostrar novos exemplos criados
            new_samples = len(y_balanced) - len(y)
            logger.info(f"\n✨ Criados {new_samples} novos exemplos sintéticos")
            
            return X_balanced, y_balanced
            
        except Exception as e:
            logger.error(f"❌ Erro no balanceamento: {e}")
            return None, None
    
    def train_and_compare(self, X_original, y_original, X_balanced, y_balanced):
        """
        Treina modelos com dados originais e balanceados para comparar.
        """
        logger.info("\n" + "="*80)
        logger.info("🎯 COMPARAÇÃO: ORIGINAL vs BALANCEADO")
        logger.info("="*80)
        
        results = {}
        
        # Split original
        X_train_orig, X_test_orig, y_train_orig, y_test_orig = train_test_split(
            X_original, y_original, test_size=0.2, random_state=42, stratify=y_original
        )
        
        # Split balanceado
        X_train_bal, X_test_bal, y_train_bal, y_test_bal = train_test_split(
            X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced
        )
        
        # Treinar modelo ORIGINAL
        logger.info("\n🔵 Treinando com dados ORIGINAIS...")
        model_orig = xgb.XGBClassifier(
            objective='multi:softprob',
            num_class=3,
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
            eval_metric='mlogloss'
        )
        
        model_orig.fit(X_train_orig, y_train_orig, verbose=False)
        
        y_pred_orig = model_orig.predict(X_test_orig)
        
        results['original'] = {
            'accuracy': accuracy_score(y_test_orig, y_pred_orig),
            'precision': precision_score(y_test_orig, y_pred_orig, average='weighted', zero_division=0),
            'recall': recall_score(y_test_orig, y_pred_orig, average='weighted', zero_division=0),
            'f1': f1_score(y_test_orig, y_pred_orig, average='weighted', zero_division=0),
            'confusion_matrix': confusion_matrix(y_test_orig, y_pred_orig),
            'class_distribution': Counter(y_pred_orig)
        }
        
        # Treinar modelo BALANCEADO
        logger.info("\n🟢 Treinando com dados BALANCEADOS...")
        model_bal = xgb.XGBClassifier(
            objective='multi:softprob',
            num_class=3,
            n_estimators=100,
            max_depth=4,
            learning_rate=0.05,
            random_state=42,
            eval_metric='mlogloss'
        )
        
        model_bal.fit(X_train_bal, y_train_bal, verbose=False)
        
        # Testar no MESMO conjunto de teste original (importante!)
        y_pred_bal = model_bal.predict(X_test_orig)
        
        results['balanced'] = {
            'accuracy': accuracy_score(y_test_orig, y_pred_bal),
            'precision': precision_score(y_test_orig, y_pred_bal, average='weighted', zero_division=0),
            'recall': recall_score(y_test_orig, y_pred_bal, average='weighted', zero_division=0),
            'f1': f1_score(y_test_orig, y_pred_bal, average='weighted', zero_division=0),
            'confusion_matrix': confusion_matrix(y_test_orig, y_pred_bal),
            'class_distribution': Counter(y_pred_bal)
        }
        
        # Salvar modelo balanceado
        output_path = Path('ml_training/trained_models/xgboost_1x2_smote.pkl')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model_bal, output_path)
        logger.info(f"\n💾 Modelo balanceado salvo: {output_path}")
        
        return results, model_bal
    
    def print_comparison(self, results):
        """
        Imprime comparação detalhada.
        """
        logger.info("\n" + "="*80)
        logger.info("📊 RESULTADOS DA COMPARAÇÃO")
        logger.info("="*80)
        
        orig = results['original']
        bal = results['balanced']
        
        logger.info("\n🎯 MÉTRICAS GERAIS:")
        logger.info(f"\n   {'Métrica':<15} {'Original':<12} {'Balanceado':<12} {'Diferença'}")
        logger.info(f"   {'-'*15} {'-'*12} {'-'*12} {'-'*10}")
        
        metrics = ['accuracy', 'precision', 'recall', 'f1']
        for metric in metrics:
            orig_val = orig[metric]
            bal_val = bal[metric]
            diff = bal_val - orig_val
            symbol = "✅" if diff > 0 else "❌" if diff < 0 else "➖"
            
            logger.info(
                f"   {metric.capitalize():<15} "
                f"{orig_val*100:>6.2f}%     "
                f"{bal_val*100:>6.2f}%     "
                f"{symbol} {diff*100:+.2f}%"
            )
        
        logger.info("\n📈 PREDIÇÕES POR CLASSE:")
        logger.info(f"\n   {'Classe':<15} {'Original':<12} {'Balanceado':<12} {'Diferença'}")
        logger.info(f"   {'-'*15} {'-'*12} {'-'*12} {'-'*10}")
        
        classes = ['Home (0)', 'Draw (1)', 'Away (2)']
        for i, class_name in enumerate(classes):
            orig_count = orig['class_distribution'].get(i, 0)
            bal_count = bal['class_distribution'].get(i, 0)
            diff = bal_count - orig_count
            symbol = "✅" if abs(diff) < 10 else "⚠️"
            
            logger.info(
                f"   {class_name:<15} "
                f"{orig_count:>6}       "
                f"{bal_count:>6}       "
                f"{symbol} {diff:+4}"
            )
        
        logger.info("\n🎯 MATRIZ DE CONFUSÃO:")
        logger.info("\n   ORIGINAL:")
        logger.info(f"   {orig['confusion_matrix']}")
        logger.info("\n   BALANCEADO:")
        logger.info(f"   {bal['confusion_matrix']}")


def main():
    parser = argparse.ArgumentParser(description='Balanceamento de dataset com SMOTE')
    parser.add_argument('--input', type=str, default='ml_training/training_dataset.json',
                       help='Arquivo de entrada (JSON ou CSV)')
    parser.add_argument('--method', type=str, default='smote',
                       choices=['smote', 'borderline', 'adasyn'],
                       help='Método de balanceamento')
    parser.add_argument('--strategy', type=str, default='auto',
                       help='Estratégia de sampling')
    
    args = parser.parse_args()
    
    logger.info("="*80)
    logger.info("🔄 BALANCEAMENTO DE DATASET COM SMOTE")
    logger.info("="*80)
    
    balancer = DatasetBalancer()
    
    # 1. Carregar dados
    df = balancer.load_dataset(args.input)
    if df is None:
        logger.error("\n❌ Impossível continuar sem dados")
        logger.info("\n💡 Certifique-se que existe um arquivo válido em:")
        logger.info(f"   {args.input}")
        return
    
    # 2. Preparar features
    X, y = balancer.prepare_features(df)
    if X is None:
        return
    
    # 3. Verificar se precisa balancear
    dist = Counter(y)
    max_count = max(dist.values())
    min_count = min(dist.values())
    imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
    
    logger.info(f"\n📊 Razão de desbalanceamento: {imbalance_ratio:.2f}")
    
    if imbalance_ratio < 1.5:
        logger.info("✅ Dataset já está relativamente balanceado")
        logger.info("   Continuando com balanceamento para fins de teste...")
    
    # 4. Aplicar SMOTE
    X_balanced, y_balanced = balancer.balance_with_smote(X, y, method=args.method, sampling_strategy=args.strategy)
    
    if X_balanced is None:
        return
    
    # 5. Treinar e comparar
    results, model = balancer.train_and_compare(X, y, X_balanced, y_balanced)
    
    # 6. Imprimir comparação
    balancer.print_comparison(results)
    
    # 7. Salvar resultados
    output = {
        'timestamp': datetime.now().isoformat(),
        'method': args.method,
        'strategy': args.strategy,
        'original_size': len(y),
        'balanced_size': len(y_balanced),
        'original_distribution': {str(k): int(v) for k, v in Counter(y).items()},
        'balanced_distribution': {str(k): int(v) for k, v in Counter(y_balanced).items()},
        'metrics': {
            'original': {k: float(v) if not isinstance(v, (np.ndarray, Counter)) else str(v) 
                        for k, v in results['original'].items()},
            'balanced': {k: float(v) if not isinstance(v, (np.ndarray, Counter)) else str(v) 
                        for k, v in results['balanced'].items()}
        },
        'improvement': {
            'accuracy': float(results['balanced']['accuracy'] - results['original']['accuracy']),
            'f1': float(results['balanced']['f1'] - results['original']['f1'])
        }
    }
    
    output_file = f'smote_balancing_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n💾 Resultados salvos: {output_file}")
    
    # 8. Recomendações
    logger.info("\n" + "="*80)
    logger.info("💡 RECOMENDAÇÕES")
    logger.info("="*80)
    
    improvement = results['balanced']['accuracy'] - results['original']['accuracy']
    
    if improvement > 0.03:
        logger.info("\n✅ BALANCEAMENTO RECOMENDADO!")
        logger.info(f"   Melhora significativa: +{improvement*100:.2f}%")
        logger.info("\n📝 Próximos passos:")
        logger.info("   1. Substitua xgboost_1x2.pkl por xgboost_1x2_smote.pkl")
        logger.info("   2. Teste em produção por 50-100 jogos")
        logger.info("   3. Compare acurácia real com baseline")
    elif improvement > 0:
        logger.info("\n⚠️ MELHORA MODERADA")
        logger.info(f"   Ganho pequeno: +{improvement*100:.2f}%")
        logger.info("   Considere testar em produção A/B")
    else:
        logger.info("\n❌ BALANCEAMENTO NÃO RECOMENDADO")
        logger.info(f"   Piora no desempenho: {improvement*100:.2f}%")
        logger.info("   Manter modelo original")
    
    logger.info("\n" + "="*80)


if __name__ == '__main__':
    main()
