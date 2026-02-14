# 🎯 Plano de Calibração e Melhoria de Acurácia

**Data**: 12 de Fevereiro de 2026  
**Objetivo**: Calibrar sistema para máxima acurácia mantendo alto ROI

---

## 📊 Estado Atual

### Métricas Conhecidas
- **XGBoost Otimizado**: 51.47% acurácia (DESABILITADO - overfitting severo)
  - Treino: 93.93% | Teste: 49.56%
  - Problema: Exagera empates (48% vs 25% real)
  
- **Ensemble Atual**: 
  - Poisson: 50% | ML: 30% | Market: 20%
  - Empates previstos: 36.6% (melhorou de 44.4%)
  
- **Publicação**:
  - Threshold probabilidade: 52%
  - Threshold confiança: 75%

### Problemas Identificados
1. ❌ XGBoost tem viés severo de empates
2. ❌ Overfitting em modelos ML (94% treino vs 50% teste)
3. ⚠️ Pesos do ensemble ajustados manualmente (não otimizados)
4. ⚠️ Sem calibração de probabilidades (podem estar enviesadas)
5. ⚠️ Thresholds de publicação não validados estatisticamente

---

## 🎯 Estratégia de Calibração (7 Etapas)

### **FASE 1: Calibração de Probabilidades** (Alta Prioridade)

#### 1.1 Implementar Platt Scaling
```python
from sklearn.calibration import CalibratedClassifierCV

# Calibrar probabilidades do XGBoost
calibrated_model = CalibratedClassifierCV(
    xgboost_model, 
    method='sigmoid',  # Platt scaling
    cv=5
)
```

**Objetivo**: Corrigir probabilidades enviesadas  
**Ganho esperado**: +3-5% acurácia  
**Tempo**: 2-3 horas

#### 1.2 Isotonic Regression (alternativa)
```python
calibrated_model = CalibratedClassifierCV(
    xgboost_model,
    method='isotonic',  # Mais flexível que sigmoid
    cv=5
)
```

**Quando usar**: Se Platt scaling não melhorar suficiente  
**Tempo**: +1 hora

---

### **FASE 2: Otimização de Pesos do Ensemble** (Alta Prioridade)

#### 2.1 Grid Search para Pesos Ótimos
```python
def optimize_ensemble_weights(poisson_preds, ml_preds, market_preds, true_labels):
    """
    Encontra pesos ótimos via grid search.
    """
    best_accuracy = 0
    best_weights = None
    
    # Grid de busca
    for w_poisson in np.arange(0.2, 0.8, 0.05):
        for w_ml in np.arange(0.1, 0.6, 0.05):
            w_market = 1.0 - w_poisson - w_ml
            
            if w_market < 0 or w_market > 0.5:
                continue
            
            # Calcular consensus
            consensus = (
                poisson_preds * w_poisson +
                ml_preds * w_ml +
                market_preds * w_market
            )
            
            # Calcular acurácia
            predictions = np.argmax(consensus, axis=1)
            accuracy = np.mean(predictions == true_labels)
            
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_weights = {
                    'poisson': w_poisson,
                    'ml': w_ml,
                    'market': w_market
                }
    
    return best_weights, best_accuracy
```

**Objetivo**: Encontrar pesos ideais data-driven  
**Ganho esperado**: +2-4% acurácia  
**Tempo**: 1-2 horas

#### 2.2 Validação Cruzada dos Pesos
```python
from sklearn.model_selection import KFold

kf = KFold(n_splits=5, shuffle=True, random_state=42)
fold_weights = []

for train_idx, val_idx in kf.split(data):
    # Otimizar pesos em cada fold
    weights, acc = optimize_ensemble_weights(
        poisson_preds[train_idx],
        ml_preds[train_idx],
        market_preds[train_idx],
        labels[train_idx]
    )
    fold_weights.append(weights)

# Média dos pesos de todos os folds
final_weights = {
    'poisson': np.mean([w['poisson'] for w in fold_weights]),
    'ml': np.mean([w['ml'] for w in fold_weights]),
    'market': np.mean([w['market'] for w in fold_weights])
}
```

**Objetivo**: Evitar overfitting nos pesos  
**Tempo**: +1 hora

---

### **FASE 3: Otimização de Thresholds** (Média Prioridade)

#### 3.1 Curva ROC para Threshold de Confiança
```python
from sklearn.metrics import roc_curve, auc

def find_optimal_confidence_threshold(predictions, confidences, labels):
    """
    Encontra threshold de confiança que maximiza F1-score.
    """
    from sklearn.metrics import f1_score
    
    best_f1 = 0
    best_threshold = 0.5
    
    for threshold in np.arange(0.5, 0.95, 0.05):
        # Filtrar apenas predições acima do threshold
        mask = confidences >= threshold
        filtered_preds = predictions[mask]
        filtered_labels = labels[mask]
        
        if len(filtered_preds) < 10:
            continue
        
        f1 = f1_score(filtered_labels, filtered_preds, average='weighted')
        
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    
    return best_threshold, best_f1
```

**Objetivo**: Threshold ótimo entre acurácia e cobertura  
**Ganho esperado**: +1-2% acurácia (com menor volume)  
**Tempo**: 1 hora

#### 3.2 Precision-Recall Trade-off
```python
def analyze_precision_recall_tradeoff(predictions, confidences, labels):
    """
    Mostra trade-off entre precisão e recall para diferentes thresholds.
    """
    results = []
    
    for threshold in np.arange(0.5, 0.95, 0.05):
        mask = confidences >= threshold
        
        if mask.sum() == 0:
            continue
        
        precision = precision_score(labels[mask], predictions[mask], average='weighted')
        recall = recall_score(labels[mask], predictions[mask], average='weighted')
        coverage = mask.sum() / len(mask)
        
        results.append({
            'threshold': threshold,
            'precision': precision,
            'recall': recall,
            'coverage': coverage,
            'f1': 2 * precision * recall / (precision + recall)
        })
    
    return pd.DataFrame(results)
```

**Objetivo**: Entender impacto de threshold na qualidade  
**Tempo**: 30 minutos

---

### **FASE 4: Feature Engineering Avançado** (Média Prioridade)

#### 4.1 Features de Interação
```python
def add_interaction_features(df):
    """
    Adiciona features de interação entre variáveis.
    """
    # Interações de força × forma
    df['strength_form_home'] = df['home_strength'] * df['home_form']
    df['strength_form_away'] = df['away_strength'] * df['away_form']
    
    # Diferencial combinado
    df['combined_differential'] = (
        df['strength_differential'] * 0.6 +
        df['form_differential'] * 0.4
    )
    
    # Motivação × performance
    df['motivation_performance_home'] = df['home_motivation'] * df['home_attack_strength']
    df['motivation_performance_away'] = df['away_motivation'] * df['away_attack_strength']
    
    # Contexto temporal (dia da semana × fadiga)
    df['midweek_fatigue'] = (df['is_midweek'] * df['days_since_last_match']).apply(
        lambda x: 1 if x < 3 else 0
    )
    
    return df
```

**Objetivo**: Capturar relações não-lineares  
**Ganho esperado**: +1-3% acurácia  
**Tempo**: 2-3 horas

#### 4.2 Features Temporais
```python
def add_temporal_features(df):
    """
    Features baseadas em tendências temporais.
    """
    # Momentum (últimos 3 vs últimos 6 jogos)
    df['momentum_home'] = df['home_points_l3'] / 9 - df['home_points_l6'] / 18
    df['momentum_away'] = df['away_points_l3'] / 9 - df['away_points_l6'] / 18
    
    # Volatilidade de performance
    df['volatility_home'] = df['home_goals_std_l5']
    df['volatility_away'] = df['away_goals_std_l5']
    
    # Sequência de resultados
    df['winning_streak_home'] = df['home_wins_in_row']
    df['winless_streak_away'] = df['away_games_without_win']
    
    return df
```

**Tempo**: 1-2 horas

---

### **FASE 5: Balanceamento de Classes** (Alta Prioridade para XGBoost)

#### 5.1 SMOTE para Balanceamento
```python
from imblearn.over_sampling import SMOTE

def balance_dataset(X_train, y_train):
    """
    Balanceia classes usando SMOTE (Synthetic Minority Over-sampling).
    """
    smote = SMOTE(
        sampling_strategy='auto',  # Balanceia todas as classes
        random_state=42,
        k_neighbors=5
    )
    
    X_balanced, y_balanced = smote.fit_resample(X_train, y_train)
    
    print(f"Original: {Counter(y_train)}")
    print(f"Balanceado: {Counter(y_balanced)}")
    
    return X_balanced, y_balanced
```

**Objetivo**: Reduzir viés de empates  
**Ganho esperado**: +3-5% acurácia  
**Tempo**: 1 hora

#### 5.2 Class Weights Dinâmicos
```python
from sklearn.utils.class_weight import compute_class_weight

# Calcular pesos baseados na distribuição real
class_weights = compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)

# Aplicar no XGBoost
scale_pos_weight = class_weights[1] / class_weights[0]  # Para binário
# Para multi-classe, usar sample_weight no fit
```

**Tempo**: 30 minutos

---

### **FASE 6: Ensembling Avançado** (Baixa Prioridade - Longo Prazo)

#### 6.1 Stacking com Meta-Learner
```python
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression

# Base models
base_models = [
    ('poisson', PoissonModel()),
    ('xgboost', XGBoostModel()),
    ('random_forest', RandomForestClassifier(n_estimators=100))
]

# Meta-learner
stacking_model = StackingClassifier(
    estimators=base_models,
    final_estimator=LogisticRegression(multi_class='multinomial'),
    cv=5
)
```

**Objetivo**: Combinar modelos de forma ótima  
**Ganho esperado**: +2-4% acurácia  
**Tempo**: 4-6 horas

---

### **FASE 7: Validação e Monitoramento Contínuo** (Alta Prioridade)

#### 7.1 Validação Temporal Sliding Window
```python
def temporal_validation(df, window_size=100, step=20):
    """
    Valida modelo em janelas temporais progressivas.
    """
    results = []
    
    for i in range(0, len(df) - window_size, step):
        train_df = df[:i]
        test_df = df[i:i+window_size]
        
        if len(train_df) < 200:  # Mínimo para treino
            continue
        
        # Treinar e avaliar
        model.fit(train_df[features], train_df['result'])
        accuracy = model.score(test_df[features], test_df['result'])
        
        results.append({
            'window': i,
            'accuracy': accuracy,
            'train_size': len(train_df),
            'test_size': len(test_df)
        })
    
    return pd.DataFrame(results)
```

**Objetivo**: Detectar degradação ao longo do tempo  
**Tempo**: 2 horas

#### 7.2 Dashboard de Monitoramento
```python
# Métricas a monitorar:
metrics_to_track = {
    'accuracy': accuracy_score,
    'precision_home': lambda y_true, y_pred: precision_score(y_true, y_pred, labels=[0], average='macro'),
    'precision_draw': lambda y_true, y_pred: precision_score(y_true, y_pred, labels=[1], average='macro'),
    'precision_away': lambda y_true, y_pred: precision_score(y_true, y_pred, labels=[2], average='macro'),
    'distribution_bias': lambda y_true, y_pred: np.abs(np.bincount(y_pred) / len(y_pred) - np.bincount(y_true) / len(y_true)).mean()
}
```

**Tempo**: 3-4 horas

---

## 📅 Cronograma de Implementação

### **Sprints Sugeridos**

#### **SPRINT 1 (Semana 1)** - Calibração Rápida
- [ ] Implementar Platt Scaling (3h)
- [ ] Otimizar pesos do ensemble via grid search (2h)
- [ ] Validação cruzada dos pesos (1h)
- [ ] **Ganho esperado**: +5-9% acurácia

#### **SPRINT 2 (Semana 2)** - Balanceamento e Features
- [ ] Implementar SMOTE para balanceamento (1h)
- [ ] Retreinar XGBoost com dados balanceados (2h)
- [ ] Adicionar features de interação (3h)
- [ ] **Ganho esperado**: +4-8% acurácia

#### **SPRINT 3 (Semana 3)** - Otimização de Thresholds
- [ ] Encontrar threshold ótimo de confiança (1h)
- [ ] Análise precision-recall (30min)
- [ ] Ajustar thresholds na configuração (30min)
- [ ] **Ganho esperado**: +1-2% acurácia

#### **SPRINT 4 (Semana 4)** - Validação e Monitoramento
- [ ] Implementar validação temporal (2h)
- [ ] Criar dashboard de métricas (4h)
- [ ] Documentar resultados (2h)
- [ ] **Ganho esperado**: Estabilidade longo prazo

---

## 🎯 Metas Realistas

### Acurácia Esperada por Fase

| Fase | Baseline | Após Implementação | Ganho |
|------|----------|-------------------|-------|
| Atual | 51% | - | - |
| + Calibração | 51% | **56-60%** | +5-9% |
| + Balanceamento | 56% | **60-64%** | +4-8% |
| + Features | 60% | **62-66%** | +2-4% |
| + Thresholds | 62% | **63-68%** | +1-2% |
| **Meta Final** | **51%** | **63-68%** | **+12-17%** |

### Trade-offs a Considerar

1. **Acurácia vs Cobertura**
   - Threshold alto → Acurácia +5% mas cobertura -30%
   - Decisão: Priorizar acurácia se ROI compensa

2. **Complexidade vs Manutenibilidade**
   - Stacking aumenta acurácia mas dificulta debug
   - Decisão: Implementar apenas se ganho > 3%

3. **Overfitting vs Generalização**
   - Validação temporal é essencial
   - Sempre testar em dados futuros

---

## 🔧 Código Base para Começar

### Arquivo: `calibrate_system.py`
```python
"""
Sistema de calibração automática.
Uso: python calibrate_system.py --phase 1
"""

import argparse
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import KFold
import joblib

def calibrate_probabilities(model_path, data_path, output_path):
    """FASE 1: Calibrar probabilidades."""
    model = joblib.load(model_path)
    data = pd.read_pickle(data_path)
    
    X = data.drop('result', axis=1)
    y = data['result']
    
    # Calibrar com Platt Scaling
    calibrated = CalibratedClassifierCV(model, method='sigmoid', cv=5)
    calibrated.fit(X, y)
    
    # Salvar modelo calibrado
    joblib.dump(calibrated, output_path)
    print(f"✅ Modelo calibrado salvo em {output_path}")

def optimize_weights(poisson_preds, ml_preds, market_preds, labels):
    """FASE 2: Otimizar pesos do ensemble."""
    best_accuracy = 0
    best_weights = None
    
    for w_p in np.arange(0.3, 0.7, 0.05):
        for w_m in np.arange(0.2, 0.5, 0.05):
            w_mk = round(1.0 - w_p - w_m, 2)
            
            if w_mk < 0.1 or w_mk > 0.4:
                continue
            
            consensus = (
                poisson_preds * w_p +
                ml_preds * w_m +
                market_preds * w_mk
            )
            
            preds = np.argmax(consensus, axis=1)
            acc = np.mean(preds == labels)
            
            if acc > best_accuracy:
                best_accuracy = acc
                best_weights = {'poisson': w_p, 'ml': w_m, 'market': w_mk}
    
    return best_weights, best_accuracy

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', type=int, required=True)
    args = parser.parse_args()
    
    if args.phase == 1:
        calibrate_probabilities(
            'models/xgboost_1x2.pkl',
            'data/validation_data.pkl',
            'models/xgboost_1x2_calibrated.pkl'
        )
    elif args.phase == 2:
        # Implementar otimização de pesos
        pass
```

---

## 📊 Métricas de Sucesso

### KPIs Principais
1. **Acurácia Geral**: Target ≥ 65%
2. **Acurácia por Classe**:
   - Home Win: ≥ 70%
   - Draw: ≥ 50% (mais difícil)
   - Away Win: ≥ 70%
3. **Calibration Error**: < 0.05 (probabilidades bem calibradas)
4. **ROI em Apostas**: ≥ 10% (lucro sobre investimento)
5. **Cobertura**: ≥ 40% dos jogos (threshold não muito alto)

### Alertas de Degradação
- Acurácia cai > 5% em 100 jogos consecutivos → Re-calibrar
- Viés de classe > 15% → Re-balancear
- ROI < 5% por 50 jogos → Revisar thresholds

---

## 💡 Recomendações Finais

### O Que Fazer AGORA (Próximas 24h)
1. ✅ **Implementar Platt Scaling** - Maior impacto rápido
2. ✅ **Otimizar pesos via grid search** - Data-driven
3. ✅ **Balancear dataset com SMOTE** - Reduzir viés empates

### O Que Fazer Esta Semana
4. ⚠️ Adicionar features de interação
5. ⚠️ Validar thresholds de confiança  
6. ⚠️ Implementar validação temporal

### O Que Deixar para Depois
7. ⏸️ Stacking ensemble (complexo)
8. ⏸️ Dashboard completo
9. ⏸️ A/B testing framework

---

## 🚀 Quick Start

```bash
# 1. Calibrar probabilidades
python calibrate_system.py --phase 1

# 2. Otimizar pesos
python calibrate_system.py --phase 2

# 3. Validar resultados
python validate_calibration.py

# 4. Atualizar configuração
# Editar apps/analysis/config/analysis_config.py com novos valores

# 5. Testar end-to-end
python test_ml_integration.py
```

**Tempo total estimado para implementação completa**: 3-4 semanas  
**Ganho de acurácia esperado**: +12-17 pontos percentuais  
**ROI estimado**: 20-30% após calibração
