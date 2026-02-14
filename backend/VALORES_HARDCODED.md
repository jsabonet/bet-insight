# Valores Hardcoded no Sistema

## 📊 ml_integration.py - Pesos do Ensemble

### Contexto Fraco (Padrão)
**COM ML Treinado + Market Prior:**
- `weight_poisson = 0.50` (linha 409) - Ajustado para reduzir empates exagerados
- `weight_ml = 0.30` (linha 410) - Reduzido de 0.50 (ML exagera empates)
- `weight_market = 0.20` (linha 411) - Reduzido de 0.30

**COM ML Treinado SEM Market Prior:**
- `weight_poisson = 0.60` (linha 414)
- `weight_ml = 0.40` (linha 415)
- `weight_market = 0.0` (linha 416)

**SEM ML (Logística) + Market Prior:**
- `weight_poisson = 0.25` (linha 420)
- `weight_ml = 0.40` (linha 421)
- `weight_market = 0.35` (linha 422)

**SEM ML (Logística) SEM Market Prior:**
- `weight_poisson = 0.45` (linha 424)
- `weight_ml = 0.55` (linha 425)
- `weight_market = 0.0` (linha 426)

### Contexto Forte (≥80% confiança)
- `poisson: 0.30` (linha 521)
- `ml: 0.50` (linha 522)
- `market: 0.20` (linha 523)

### Contexto Moderado (≥65% confiança)
- `poisson: 0.40` (linha 542)
- `ml: 0.40` (linha 543)
- `market: 0.20` (linha 544)

### Thresholds de Confiança Contextual
- `max_context_confidence >= 0.80` (linha 514) - Contexto forte
- `max_context_confidence >= 0.65` (linha 537) - Contexto moderado

### Fallback
- `{'home_win': 0.33, 'draw': 0.33, 'away_win': 0.33}` (linhas 165, 183, 186) - Distribuição uniforme

---

## 🎯 decision_engine.py - Thresholds de Decisão

### Publicação de Previsões
- `threshold_prob = 0.52` (linha 26) - Probabilidade mínima para publicar (52%)
- `threshold_conf = 0.75` (linha 26) - Confiança mínima para publicar (75%)

### Odds e Probabilidades
- `prob > 0.01` (linhas 233, 258) - Probabilidade mínima 1% para evitar odds absurdas
- `fair_odds limite = 500.0` (linha 238) - Odd máxima

### Força e Forma
- `strength_diff > 0.5` (linha 357) - Diferença significativa de força
- `form_diff > 0.5` (linha 357) - Diferença significativa de forma

---

## 🔍 context_analyzer.py - Padrões Contextuais

### Motivação Assimétrica
- Base: `0.70 + (motivation_gap * 0.3)` (linha 166) - Range: 0.70-1.0

### Derby/Rivalidade
- Base: `0.70` (linha 252)
- Derby: `0.85` ou até `0.90` (linha 294)

### Upset Potential
- Base: `0.65 + (underdog_form - 0.65) * 0.5` (linha 334) - Max 0.825

### Lesões Críticas
- Base: `0.70 + (max_impact - 0.7) * 0.5` (linha 373) - Max 0.85

### Open Game (Jogo Aberto)
- Base: `0.50 + (balance_score * 0.30)` (linha 420) - Range: 0.50-0.80

---

## 📈 market_selector.py - Scores Finais

### Apostas Simples
- `min_final_score = 0.50` (linha 280) - Score mínimo 50% (antes era 28%)

### Bilhetes Combinados
- `min_final_score = 0.45` (linha 284) - Score mínimo 45% (antes era 28%)

---

## 🎲 market_thresholds.py - Thresholds por Mercado

### Thresholds Calibrados (49 mercados)
Baseado em validação de 2,950 partidas:

**Excelentes (>85% acurácia):**
- `over_0.5: 0.50` - 92.6% acurácia
- `under_0.5: 0.50` - 92.6% acurácia
- `away_over_2.5: 0.50` - 86.7% acurácia
- `over_4.5: 0.50` - 85.1% acurácia

**Bons (70-85% acurácia):**
- `home_win: 0.55` - 76.6% acurácia
- `1X: 0.55` - 83.1% acurácia
- `X2: 0.55` - 80.7% acurácia

**Moderados (60-70% acurácia):**
- Linhas Asiáticas: `0.58-0.60`

**Difíceis (<60% acurácia):**
- `over_2.5: 0.65` - 52.5% acurácia
- `btts_yes: 0.68` - 54.2% acurácia

**Desabilitados:**
- `odd_goals: None` - 51.5% acurácia (≈ aleatório)
- `even_goals: None` - 51.5% acurácia (≈ aleatório)

---

## ⚙️ hybrid_boost_system.py

### Qualidade de Mercados
Usa thresholds do `market_thresholds.py` + classificação:
- `'excellent'` - >85% acurácia
- `'good'` - 70-85% acurácia
- `'moderate'` - 60-70% acurácia
- `'poor'` - 50-60% acurácia
- `'disabled'` - <50% acurácia

---

## 🔧 Recomendações

### Valores que DEVEM permanecer hardcoded:
1. **Fallback uniforme** (0.33/0.33/0.33) - Padrão matemático
2. **Probabilidade mínima** (0.01) - Previne divisão por zero
3. **Thresholds calibrados** (market_thresholds.py) - Baseados em dados reais

### Valores que PODEM ser configuráveis:
1. **Pesos do ensemble** - Atualmente otimizados manualmente
2. **Thresholds de publicação** (0.52, 0.75) - Podem variar por estratégia
3. **Confiança contextual** (0.65, 0.80) - Ajuste fino por padrão
4. **Score mínimo** (0.45, 0.50) - Pode variar por modo de jogo

### Valores que PRECISAM ser configuráveis:
❌ Nenhum crítico no momento - sistema está balanceado

---

## 📌 Status Atual

**Data:** 12 de Fevereiro de 2026
**Sistema:** 100% funcional
**Acurácia validada:** 71.92% em 49 mercados
**Empates:** Calibrados (36.6% vs 44.4% anterior)
**Pesos ajustados:** Poisson 50% > ML 30% > Market 20%
