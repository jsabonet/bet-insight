# GUIA: Como Aplicar SMOTE em Produção

> **Status**: ✅ Demonstração validada | ⏸️ Aguardando dados reais  
> **Data**: 12/02/2026  
> **Ganho esperado**: +1-3% acurácia | -8.5 pts viés empates

---

## 🎯 Pré-requisitos

### 1. ✅ Bibliotecas Instaladas

```bash
pip install imbalanced-learn  # ✅ JÁ INSTALADO (v0.14.1)
```

### 2. ⏸️ Dataset de Treino (PENDENTE)

**Necessário**: Mínimo **500 jogos** com resultados conhecidos

**Opções para obter dados**:

#### Opção A: Usar collect_historical_matches.py (Django)
```bash
cd bet-insight/backend
python collect_historical_matches.py
```

**Prós**: Usa infraestrutura existente  
**Contras**: Requer Django configurado

#### Opção B: Aguardar acúmulo natural
- Sistema já está operando
- Aguardar 2-3 semanas
- Acumular 500+ validações reais

**Prós**: Dados reais do sistema  
**Contras**: Demora 2-3 semanas

#### Opção C: Dataset público (Kaggle/GitHub)
- Procurar "football match results dataset"
- Converter para formato compatível

**Prós**: Dados imediatos  
**Contras**: Pode não ter features específicas

---

## 📝 Passo a Passo

### FASE 1: Coletar Dados ⏸️

**Se Django funcional**:
```bash
cd bet-insight/backend
python collect_historical_matches.py
```

**Validar arquivo gerado**:
```bash
# Verificar tamanho
Get-Item ml_training/training_dataset.json | Select-Object Length, LastWriteTime

# Ver primeiros jogos
Get-Content ml_training/training_dataset.json | ConvertFrom-Json | Select-Object -First 5
```

**Mínimo aceitável**: 500 jogos (ideal: 1000+)

---

### FASE 2: Aplicar SMOTE ✅ PRONTO

**Script criado**: `balance_dataset_smote.py`

**Executar**:
```bash
python balance_dataset_smote.py --input ml_training/training_dataset.json
```

**Opções avançadas**:
```bash
# Usar BorderlineSMOTE (foca em exemplos difíceis)
python balance_dataset_smote.py --method borderline

# Usar ADASYN (adaptativo)
python balance_dataset_smote.py --method adasyn

# Estratégia customizada (balancear apenas empates)
python balance_dataset_smote.py --strategy minority
```

**Saída esperada**:
- `ml_training/trained_models/xgboost_1x2_smote.pkl` (modelo balanceado)
- `smote_balancing_results_YYYYMMDD_HHMMSS.json` (métricas)

---

### FASE 3: Validar Modelo

**Comparar com baseline**:
```bash
# Testar modelo balanceado
python test_ml_integration.py

# Verificar métricas
Get-Content smote_balancing_results_*.json | ConvertFrom-Json | Select-Object improvement
```

**O que verificar**:
- ✅ Acurácia melhorou? (mínimo +1%)
- ✅ Empates mais realistas? (target: 25-30%)
- ✅ Distribuição equilibrada? (32-34% cada classe)

---

### FASE 4: Teste A/B em Produção

**Configurar teste**:

1. **Backup do modelo atual**:
```bash
Copy-Item ml_training/trained_models/xgboost_1x2.pkl ml_training/trained_models/xgboost_1x2_backup.pkl
```

2. **Ativar modelo SMOTE** (APENAS se aprovado):
```bash
Copy-Item ml_training/trained_models/xgboost_1x2_smote.pkl ml_training/trained_models/xgboost_1x2.pkl
```

3. **Monitorar por 2 semanas**:
```bash
# Executar validação diária
python validate_ml_model.py > validation_smote_$(Get-Date -Format 'yyyyMMdd').txt
```

4. **Comparar resultados**:
```python
# Calcular acurácia média 2 semanas
baseline_accuracy = 0.56  # Atual
smote_accuracy = ?  # Medir

if smote_accuracy > baseline_accuracy + 0.01:
    print("✅ SMOTE aprovado - manter em produção")
else:
    print("❌ SMOTE não melhorou - reverter")
```

---

### FASE 5: Reverter se Necessário

**Se SMOTE piorou desempenho**:
```bash
# Restaurar modelo original
Copy-Item ml_training/trained_models/xgboost_1x2_backup.pkl ml_training/trained_models/xgboost_1x2.pkl -Force

# Validar restauração
python test_ml_integration.py
```

---

## 🔍 Critérios de Aprovação

**SMOTE é aprovado SE**:
- ✅ Acurácia > baseline + 1%
- ✅ Viés de empates < 5%
- ✅ Distribuição equilibrada (±5% por classe)
- ✅ Sem degradação em ligas específicas
- ✅ ROI melhora em pelo menos 10%

**SMOTE é rejeitado SE**:
- ❌ Acurácia < baseline
- ❌ Viés de empates aumenta
- ❌ Overfitting detectado (train >> test)
- ❌ Predições muito voláteis

---

## 📊 Resultados Esperados

### Demonstração (Dataset Sintético 1000 jogos)
- Acurácia: +1.0% ✅
- Viés empates: -8.5 pts ✅
- Recall empates: +15.4 pts ✅

### Produção (Dataset Real 500+ jogos)
Baseado em literatura e demonstração:

**Cenário Conservador**:
- Acurácia: +1-2%
- Viés empates: -5 pts
- ROI: +15-25%

**Cenário Otimista**:
- Acurácia: +2-3%
- Viés empates: -8 pts
- ROI: +30-40%

**Cenário Realista** (mais provável):
- Acurácia: +1.5%
- Viés empates: -6 pts
- ROI: +20%

---

## ⚠️ Cuidados e Limitações

### 1. Dataset Pequeno
**Problema**: < 500 jogos pode causar overfitting  
**Solução**: Aguardar mais dados ou usar cross-validation

### 2. Overfitting em Empates
**Problema**: SMOTE pode sobrepredizer empates  
**Solução**: Ajustar `sampling_strategy` (ex: 0.8 em vez de 1.0)

### 3. Features Irrelevantes
**Problema**: SMOTE cria exemplos baseados em features ruins  
**Solução**: Feature engineering ANTES de aplicar SMOTE

### 4. Dependência de Hiperparâmetros
**Problema**: k_neighbors=5 pode não ser ideal  
**Solução**: Testar k=3,5,7 e comparar

---

## 🛠️ Troubleshooting

### Problema: "ValueError: Expected n_neighbors <= n_samples"
**Causa**: Dataset muito pequeno  
**Solução**:
```python
# Reduzir k_neighbors
python balance_dataset_smote.py --k-neighbors 3
```

### Problema: Acurácia piorou após SMOTE
**Causa**: Overfitting ou features ruins  
**Soluções**:
1. Reduzir taxa de oversample:
```python
# Em vez de 'auto', usar dict customizado
sampling_strategy = {1: int(max_count * 0.8)}  # 80% ao invés de 100%
```

2. Usar BorderlineSMOTE (mais conservador):
```bash
python balance_dataset_smote.py --method borderline
```

3. Feature engineering primeiro:
```bash
python feature_engineering.py
python balance_dataset_smote.py
```

### Problema: Predições muito voláteis
**Causa**: Exemplos sintéticos de baixa qualidade  
**Solução**: Aumentar k_neighbors ou usar ADASYN

---

## 📈 Monitoramento Pós-Deploy

### Métricas Diárias
```bash
# Log de validação
python validate_ml_model.py 2>&1 | Tee-Object validation_daily_$(Get-Date -Format 'yyyyMMdd').txt

# Extrair acurácia
Select-String -Path validation_daily_*.txt -Pattern "accuracy" | Select-Object -Last 7
```

### Dashboard Semanal
```python
import json
from pathlib import Path

# Carregar últimos 7 dias
results = []
for f in Path('.').glob('validation_daily_*.txt'):
    # Parse accuracy
    pass

# Calcular média, desvio, tendência
avg_accuracy = mean(results)
print(f"Acurácia média 7 dias: {avg_accuracy:.2%}")
```

### Alerta Automático
```python
# Se acurácia < threshold por 3 dias consecutivos
if consecutive_days_below_threshold >= 3:
    send_alert("⚠️ Acurácia degradou - considere re-treino")
```

---

## 🎯 Próximos Passos Após SMOTE

**Se SMOTE aprovado**:
1. ✅ Manter modelo em produção
2. ⏸️ Implementar **FASE 5: Platt Scaling** (+3-5%)
3. ⏸️ Feature Engineering (+1-3%)
4. ⏸️ Monitoramento contínuo

**Se SMOTE rejeitado**:
1. ❌ Reverter para modelo baseline
2. ⏸️ Focar em **Platt Scaling** (maior ganho)
3. ⏸️ Coletar mais dados (1000+ jogos)
4. ⏸️ Re-testar SMOTE com dataset maior

---

## 📚 Referências

- [FASE_3_SMOTE_RESULTS.md](FASE_3_SMOTE_RESULTS.md) - Resultados da demonstração
- [PLANO_CALIBRACAO_ACURACIA.md](PLANO_CALIBRACAO_ACURACIA.md) - Roadmap completo
- [PROGRESSAO_MELHORIAS.md](PROGRESSAO_MELHORIAS.md) - Tracking de todas melhorias
- `test_smote_concept.py` - Código da demonstração
- `balance_dataset_smote.py` - Script de produção

---

**Última atualização**: 12/02/2026 04:15  
**Status**: Aguardando coleta de 500+ jogos reais  
**Responsável**: Sistema de Calibração Automática
