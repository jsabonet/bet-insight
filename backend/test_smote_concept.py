"""
Demonstração de SMOTE - Conceito e Benefícios
Mostra como SMOTE reduz viés de empates no ML

Este script:
1. Gera dataset sintético com distribuição realista
2. Treina modelo com dados desbalanceados
3. Aplica SMOTE e retreina
4. Compara resultados
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import xgboost as xgb
from imblearn.over_sampling import SMOTE
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def generate_realistic_dataset(n_samples=1000):
    """
    Gera dataset sintético com distribuição realista de resultados.
    
    Distribuição esperada:
    - Casa: ~45% (favoritos em casa)
    - Empate: ~25% (menos comum)
    - Fora: ~30% (visitante vence ocasionalmente)
    """
    np.random.seed(42)
    
    features = []
    labels = []
    
    for _ in range(n_samples):
        # Features simuladas (ex: força times, histórico, etc)
        home_strength = np.random.uniform(0.3, 0.9)
        away_strength = np.random.uniform(0.3, 0.9)
        home_form = np.random.uniform(0, 1)
        away_form = np.random.uniform(0, 1)
        historical_h2h = np.random.uniform(0, 1)
        
        # Calcular probabilidades realistas
        diff = home_strength - away_strength + (home_form - away_form) * 0.3
        
        # Probabilidades ajustadas
        if diff > 0.3:
            probs = [0.60, 0.20, 0.20]  # Casa favorita
        elif diff > 0.1:
            probs = [0.50, 0.25, 0.25]  # Casa leve favorita
        elif diff > -0.1:
            probs = [0.35, 0.35, 0.30]  # Equilibrado
        elif diff > -0.3:
            probs = [0.25, 0.25, 0.50]  # Fora leve favorito
        else:
            probs = [0.20, 0.20, 0.60]  # Fora favorito
        
        # Resultado baseado em probabilidades
        result = np.random.choice([0, 1, 2], p=probs)
        
        features.append([
            home_strength,
            away_strength,
            home_form,
            away_form,
            historical_h2h,
            diff,
            probs[0],  # prob_home calculada
            probs[1],  # prob_draw calculada
            probs[2]   # prob_away calculada
        ])
        
        labels.append(result)
    
    X = np.array(features)
    y = np.array(labels)
    
    return X, y


def train_model(X_train, y_train, X_test, y_test, name="Modelo"):
    """
    Treina modelo XGBoost e retorna métricas.
    """
    model = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=3,
        n_estimators=100,
        max_depth=4,
        learning_rate=0.05,
        random_state=42,
        eval_metric='mlogloss'
    )
    
    model.fit(X_train, y_train, verbose=False)
    
    # Predições
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Métricas
    accuracy = accuracy_score(y_test, y_pred)
    
    return {
        'model': model,
        'predictions': y_pred,
        'probabilities': y_pred_proba,
        'accuracy': accuracy,
        'distribution': Counter(y_pred),
        'confusion_matrix': confusion_matrix(y_test, y_pred)
    }


def main():
    logger.info("="*80)
    logger.info("🧪 DEMONSTRAÇÃO: SMOTE PARA REDUÇÃO DE VIÉS DE EMPATES")
    logger.info("="*80)
    
    # 1. Gerar dataset realista
    logger.info("\n📊 Gerando dataset sintético realista...")
    X, y = generate_realistic_dataset(n_samples=1000)
    
    dist_original = Counter(y)
    total = len(y)
    
    logger.info("\n✅ Dataset gerado:")
    logger.info(f"   Total: {total} jogos")
    logger.info(f"   Casa (0): {dist_original[0]} ({dist_original[0]/total*100:.1f}%)")
    logger.info(f"   Empate (1): {dist_original[1]} ({dist_original[1]/total*100:.1f}%)")
    logger.info(f"   Fora (2): {dist_original[2]} ({dist_original[2]/total*100:.1f}%)")
    
    # 2. Split dados
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"\n📈 Conjunto de treino: {len(X_train)} exemplos")
    logger.info(f"   Conjunto de teste: {len(X_test)} exemplos")
    
    # 3. Treinar com dados ORIGINAIS (desbalanceados)
    logger.info("\n" + "="*80)
    logger.info("🔵 MODELO 1: DADOS ORIGINAIS (Desbalanceados)")
    logger.info("="*80)
    
    results_original = train_model(X_train, y_train, X_test, y_test, "Original")
    
    logger.info(f"\n🎯 Acurácia: {results_original['accuracy']*100:.2f}%")
    logger.info("\n📊 Predições realizadas:")
    for label, count in sorted(results_original['distribution'].items()):
        pct = count/len(X_test)*100
        logger.info(f"   Classe {label}: {count} ({pct:.1f}%)")
    
    logger.info("\n🎯 Matriz de Confusão:")
    logger.info(f"\n{results_original['confusion_matrix']}")
    logger.info("\n     Real→  [Home, Draw, Away]")
    logger.info("     Pred↓")
    
    # 4. Aplicar SMOTE
    logger.info("\n" + "="*80)
    logger.info("🔄 APLICANDO SMOTE...")
    logger.info("="*80)
    
    smote = SMOTE(sampling_strategy='auto', random_state=42, k_neighbors=5)
    X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
    
    dist_balanced = Counter(y_train_balanced)
    
    logger.info("\n✅ Balanceamento concluído:")
    logger.info(f"   Antes: {len(X_train)} exemplos")
    logger.info(f"   Depois: {len(X_train_balanced)} exemplos")
    logger.info(f"   Criados: {len(X_train_balanced) - len(X_train)} exemplos sintéticos")
    
    logger.info("\n📊 Nova distribuição (treino):")
    for label, count in sorted(dist_balanced.items()):
        pct = count/len(y_train_balanced)*100
        logger.info(f"   Classe {label}: {count} ({pct:.1f}%)")
    
    # 5. Treinar com dados BALANCEADOS
    logger.info("\n" + "="*80)
    logger.info("🟢 MODELO 2: DADOS BALANCEADOS (com SMOTE)")
    logger.info("="*80)
    
    results_balanced = train_model(X_train_balanced, y_train_balanced, X_test, y_test, "SMOTE")
    
    logger.info(f"\n🎯 Acurácia: {results_balanced['accuracy']*100:.2f}%")
    logger.info("\n📊 Predições realizadas:")
    for label, count in sorted(results_balanced['distribution'].items()):
        pct = count/len(X_test)*100
        logger.info(f"   Classe {label}: {count} ({pct:.1f}%)")
    
    logger.info("\n🎯 Matriz de Confusão:")
    logger.info(f"\n{results_balanced['confusion_matrix']}")
    logger.info("\n     Real→  [Home, Draw, Away]")
    logger.info("     Pred↓")
    
    # 6. COMPARAÇÃO DETALHADA
    logger.info("\n" + "="*80)
    logger.info("📊 COMPARAÇÃO: ORIGINAL vs SMOTE")
    logger.info("="*80)
    
    logger.info("\n🎯 ACURÁCIA:")
    acc_diff = results_balanced['accuracy'] - results_original['accuracy']
    logger.info(f"   Original:   {results_original['accuracy']*100:.2f}%")
    logger.info(f"   SMOTE:      {results_balanced['accuracy']*100:.2f}%")
    logger.info(f"   Diferença:  {acc_diff*100:+.2f}%  {'✅' if acc_diff > 0 else '❌'}")
    
    logger.info("\n📈 DISTRIBUIÇÃO DE PREDIÇÕES:")
    logger.info(f"\n   {'Classe':<12} {'Original':<12} {'SMOTE':<12} {'Diferença'}")
    logger.info(f"   {'-'*12} {'-'*12} {'-'*12} {'-'*10}")
    
    classes = {0: 'Casa', 1: 'Empate', 2: 'Fora'}
    for label in [0, 1, 2]:
        orig_count = results_original['distribution'].get(label, 0)
        bal_count = results_balanced['distribution'].get(label, 0)
        orig_pct = orig_count/len(X_test)*100
        bal_pct = bal_count/len(X_test)*100
        diff = bal_pct - orig_pct
        
        symbol = "✅" if abs(diff) < 5 else "⚠️"
        
        logger.info(
            f"   {classes[label]:<12} "
            f"{orig_pct:>6.1f}%      "
            f"{bal_pct:>6.1f}%      "
            f"{symbol} {diff:+.1f}%"
        )
    
    # 7. ANÁLISE ESPECÍFICA: VIÉS DE EMPATES
    logger.info("\n" + "="*80)
    logger.info("🎯 ANÁLISE DE VIÉS DE EMPATES")
    logger.info("="*80)
    
    real_draw_pct = Counter(y_test)[1] / len(y_test) * 100
    orig_draw_pct = results_original['distribution'].get(1, 0) / len(X_test) * 100
    smote_draw_pct = results_balanced['distribution'].get(1, 0) / len(X_test) * 100
    
    logger.info(f"\n📊 Percentual de Empates:")
    logger.info(f"   Real (teste):    {real_draw_pct:.1f}%")
    logger.info(f"   Original (pred): {orig_draw_pct:.1f}%  (viés: {orig_draw_pct - real_draw_pct:+.1f}%)")
    logger.info(f"   SMOTE (pred):    {smote_draw_pct:.1f}%  (viés: {smote_draw_pct - real_draw_pct:+.1f}%)")
    
    orig_bias = abs(orig_draw_pct - real_draw_pct)
    smote_bias = abs(smote_draw_pct - real_draw_pct)
    bias_reduction = orig_bias - smote_bias
    
    logger.info(f"\n✅ Redução de viés: {bias_reduction:.1f} pontos percentuais")
    
    if smote_bias < orig_bias:
        logger.info("   🎉 SMOTE reduziu o viés de empates!")
    elif smote_bias == orig_bias:
        logger.info("   ➖ SMOTE manteve o viés igual")
    else:
        logger.info("   ⚠️ SMOTE aumentou o viés (não recomendado)")
    
    # 8. RECOMENDAÇÕES
    logger.info("\n" + "="*80)
    logger.info("💡 RECOMENDAÇÕES")
    logger.info("="*80)
    
    if acc_diff > 0.02 and smote_bias < orig_bias:
        logger.info("\n✅ SMOTE É ALTAMENTE RECOMENDADO!")
        logger.info(f"   • Melhora acurácia: +{acc_diff*100:.2f}%")
        logger.info(f"   • Reduz viés de empates: -{bias_reduction:.1f}%")
        logger.info("\n📝 Próximos passos:")
        logger.info("   1. Coletar dataset real (500+ jogos)")
        logger.info("   2. python balance_dataset_smote.py --input training_dataset.json")
        logger.info("   3. Substituir modelo atual por modelo balanceado")
        logger.info("   4. Validar em produção")
    
    elif acc_diff > 0:
        logger.info("\n⚠️ SMOTE OFERECE MELHORA MODERADA")
        logger.info(f"   • Melhora acurácia: +{acc_diff*100:.2f}%")
        logger.info("   • Considere testar em produção A/B")
    
    else:
        logger.info("\n❌ SMOTE NÃO RECOMENDADO NESTE CASO")
        logger.info(f"   • Piora acurácia: {acc_diff*100:.2f}%")
        logger.info("   • Considere outros métodos de balanceamento")
    
    logger.info("\n" + "="*80)
    logger.info("✅ DEMONSTRAÇÃO CONCLUÍDA")
    logger.info("="*80)


if __name__ == '__main__':
    main()
