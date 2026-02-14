# Configuração do Sistema de Análise

## 📋 Visão Geral

Este diretório contém configurações centralizadas do sistema de análise de apostas. Os valores que antes estavam **hardcoded** no código agora estão organizados em classes de configuração.

## 📁 Arquivos

### `analysis_config.py`
Arquivo principal com todas as configurações:

- **`EnsembleWeights`** - Pesos Poisson/ML/Market
- **`DecisionThresholds`** - Limites de publicação e seleção
- **`ContextConfidence`** - Confiança para padrões contextuais
- **`MarketSelectorConfig`** - Scores e qualidade de mercados
- **`ValidationConfig`** - Configurações de validação
- **`Fallbacks`** - Valores padrão quando dados indisponíveis

## 🔧 Como Usar

### Importar Configurações

```python
from apps.analysis.config import (
    EnsembleWeights,
    DecisionThresholds,
    get_ensemble_weights,
)
```

### Exemplo 1: Pesos do Ensemble

```python
# Obter pesos automaticamente
weights = get_ensemble_weights(
    has_ml=True,
    use_market_prior=True,
    context_confidence=0.75
)
# Retorna: {'poisson': 0.40, 'ml': 0.40, 'market': 0.20}

# Ou acessar diretamente
weights = EnsembleWeights.DEFAULT_WITH_MARKET
# {'poisson': 0.50, 'ml': 0.30, 'market': 0.20}
```

### Exemplo 2: Thresholds

```python
from apps.analysis.config import DecisionThresholds

if probability >= DecisionThresholds.MIN_PROBABILITY:
    publish = True

if odd < DecisionThresholds.MAX_FAIR_ODD:
    accept_bet = True
```

### Exemplo 3: Threshold por Acurácia

```python
from apps.analysis.config import get_market_threshold

# Mercado com 87% acurácia
threshold = get_market_threshold(0.87)
# Retorna: 0.50 (excelente)

# Mercado com 55% acurácia
threshold = get_market_threshold(0.55)
# Retorna: 0.65 (difícil)
```

## 📊 Valores Atuais (12/02/2026)

### Pesos do Ensemble

**Contexto Fraco (Padrão):**
- Poisson: **50%** ← Aumentado (mais realista)
- ML: **30%** ← Reduzido (exagerava empates)
- Market: **20%** ← Reduzido

**Contexto Forte (≥80%):**
- Poisson: 30%
- ML: 50%
- Market: 20%

**Contexto Moderado (≥65%):**
- Poisson: 40%
- ML: 40%
- Market: 20%

### Thresholds de Publicação

- **Probabilidade mínima:** 52%
- **Confiança mínima:** 75%

### Thresholds por Mercado

| Acurácia | Threshold | Qualidade |
|----------|-----------|-----------|
| >85% | 0.50 | Excelente |
| 70-85% | 0.55 | Bom |
| 60-70% | 0.60 | Moderado |
| 50-60% | 0.65 | Difícil |
| <50% | `None` | Desabilitado |

## 🎯 Histórico de Ajustes

### 12/02/2026 - Correção Viés de Empates
**Problema:** ML previa empate em 44.4% vs 24.6% do Poisson (exagerado)

**Solução:**
- Poisson: 20% → **50%** (mais peso ao modelo realista)
- ML: 50% → **30%** (reduzir viés de empates)
- Market: 30% → **20%**

**Resultado:** Empates agora em 36.6% (muito mais realista!)

## 🔍 Debugging

### Ver Configuração Atual

```python
from apps.analysis.config import EnsembleWeights
import json

# Imprimir todas as configurações
print(json.dumps(EnsembleWeights.DEFAULT_WITH_MARKET, indent=2))
```

### Testar Diferentes Pesos

```python
# Temporariamente sobrescrever pesos
custom_weights = {
    'poisson': 0.40,
    'ml': 0.40,
    'market': 0.20
}

# Usar em predict()
result = ensemble.predict(
    ...,
    weights=custom_weights  # Se implementado
)
```

## ⚠️ Notas Importantes

1. **Não alterar valores sem validação** - Os pesos atuais foram calibrados com base em 2,950 partidas

2. **Thresholds de mercado** - Vêm de `market_thresholds.py` que usa validação real, não desta config

3. **Fallbacks** - Valores uniformes (0.33/0.33/0.33) são padrão matemático, não devem ser alterados

4. **Probabilidade mínima** - 0.01 previne divisão por zero, não alterar

## 📈 Próximos Passos

- [ ] Migrar código para usar `analysis_config.py`
- [ ] Adicionar validação de ranges (0-1 para probabilidades)
- [ ] Implementar A/B testing de diferentes configurações
- [ ] Dashboard para ajustar pesos em tempo real
- [ ] Auto-calibração baseada em performance

## 📝 Documentação Completa

Ver [VALORES_HARDCODED.md](../../VALORES_HARDCODED.md) para lista completa de todos os valores hardcoded no sistema.
