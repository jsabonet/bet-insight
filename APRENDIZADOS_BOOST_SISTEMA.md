# Aprendizados: Sistema de Boost Transferencial

**Data:** 24 de Janeiro de 2026  
**Contexto:** Implementação e otimização do sistema de boost para calibração de probabilidades

---

## 🎯 Objetivo Inicial

Melhorar acurácia de **54.12% (filtered)** para **60%+** usando todas as features disponíveis no sistema.

---

## ✅ Sistema Baseline (Funcional)

### Arquitetura
- **10 layers** de boost para empate (casa → empate)
- **8 boosts** para fora (casa → fora)
- **Transferência direta** de probabilidade (não multiplicativa)

### Resultados Baseline
```
Total: 118 partidas
Casa:   28.0% pred vs 40.7% real (-12.7pp)
Empate: 33.1% pred vs 33.1% real (0.0pp) ✅ CALIBRAÇÃO PERFEITA
Fora:   39.0% pred vs 26.3% real (+12.7pp)

Accuracy:
- Casa: 45.8% (22/48)
- Empate: 33.3% (13/39)  
- Fora: 67.7% (21/31)
- Overall: 47.46%
- Filtered (4/5+ confidence): 54.12% ✅
```

### Layers do Baseline

**Empate (10 layers):**
1. ⚖️ Jogo equilibrado (prob_diff < 0.20) → 10-25% transfer
2. ⚽ xG equilibrado (diff < 0.3) → 8% transfer
3. 💪 Força similar (diff < 0.15) → 6% transfer
4. 🛡️ Jogo defensivo (avg_xG < 2.2) → 5% transfer
5. 📜 H2H draw rate ≥35% → 3-13% transfer
6. 📅 Season progress ≥75% → 4% transfer
7. 🔥 Derby → 6% transfer
8. 😴 Fadiga bilateral → 5% transfer
9. 😐 Motivação equilibrada/baixa → 4% transfer
10. 🏥 Lesões bilaterais graves → 5% transfer

**Fora (8 boosts):**
1. 🚀 Visitante favorito (odd casa > 2.5) → 20% transfer
2. 💪 Força muito superior (diff < -0.25) → 18% transfer
3. ⚽ xG superior (diff > 0.4) → 12% transfer
4. 📈 Forma superior (diff < -0.8) → 10% transfer
5. 🔥 Motivação muito superior (diff > 3.0) → 15% transfer
6. 🏥 Casa lesões graves vs fora ok → 14% transfer
7. 😴 Fora descansado (diff < -3 dias) → 8% transfer
8. 📊 Momentum divergente → 10% transfer

---

## ❌ Tentativa: Sistema Completo (16+12 layers)

### Features Adicionadas
Tentamos usar **100% das features disponíveis**, adicionando:

**Empate (+6 layers):**
11. 🌧️ Clima adverso (severity ≥6/10)
12. 🛡️ Defesas sólidas bilaterais (40%+ clean sheets)
13. 📐 Baixa pressão ofensiva (<8 corners)
14. ⚡ ELO equilibrado (diff <30)
15. 🏆 Jogo decisivo (importance ≥8.5)
16. ⛔ Baixo BTTS H2H (<30%)

**Fora (+4 boosts):**
9. ⚡ ELO muito superior (>50 pontos)
10. 📐 Pressão ofensiva superior (3+ corners)
11. 🛡️❌ Casa defesa fraca (<25% CS)
12. 🟨 Disciplina superior

### Resultados DESASTROSOS
```
Total: 120 partidas
Casa:   14.2% pred vs 40.8% real (-26.7pp) ❌❌❌ COLAPSO!
Empate: 37.5% pred vs 32.5% real (+5.0pp)
Fora:   48.3% pred vs 26.7% real (+21.7pp) ❌❌

Accuracy:
- Casa: 26.5% (13/49) ❌ -19.3pp vs baseline
- Empate: 35.9% (14/39) ✅ +2.6pp
- Fora: 68.8% (22/32) ✅ +1.1pp
- Overall: 40.83% ❌ -6.63pp
- Filtered: 42.86% ❌ -11.26pp vs baseline!
```

---

## 🔍 Análise do Problema

### Por que piorou tanto?

#### 1. **Overtuning / Overfitting**
- 16 layers transferindo de casa criaram **efeito cascata**
- Previsões de casa colapsaram: 28% → 14.2% (-13.8pp)
- Sistema ficou extremamente conservador para casa

#### 2. **Conflito de Features**
- Múltiplas condições ativando **simultaneamente**
- Exemplo: Jogo pode ter:
  - ELO equilibrado → -7% casa
  - Defesas sólidas → -4-10% casa
  - Baixa pressão → -4% casa
  - **Total: -15-21% casa em UM único jogo!**

#### 3. **Features Fracas Diluindo Sinal**
- Nem todas as features têm poder preditivo forte
- Corners, discipline, BTTS H2H são **proxies fracos**
- Diluem o sinal das features fortes (ELO, xG, força)

#### 4. **Normalização Excessiva**
- Transfer total chegou a **40-50%** em alguns jogos
- Casa ficou com probabilidade residual
- Empate/Fora inflados artificialmente

---

## 📊 Comparação Visual

```
BASELINE (10+8):
Casa  ████████████████████████████ 28.0%
Empate ████████████████████████████████ 33.1% ✅ PERFEITO
Fora  ███████████████████████████████████████ 39.0%

COMPLETO (16+12):
Casa  ██████████████ 14.2% ❌ COLAPSO
Empate ██████████████████████████████████████ 37.5%
Fora  ████████████████████████████████████████████████ 48.3%

REALIDADE:
Casa  ████████████████████████████████████████ 40.8%
Empate █████████████████████████████████ 32.5%
Fora  ██████████████████████████ 26.7%
```

---

## 💡 Lições Aprendidas

### ✅ Boas Práticas

1. **Menos é Mais**
   - 10 layers bem calibrados > 16 layers sobrepostos
   - Foco em features **fortes e independentes**

2. **Validação Incremental**
   - Adicionar **1 layer por vez**
   - Validar com 120 partidas após cada adição
   - Manter apenas se ganho ≥ +0.5pp

3. **Monitorar Distribuição**
   - Viés por outcome (casa/empate/fora)
   - Accuracy individual por outcome
   - Coverage (% partidas filtradas)

4. **Transfer Limits**
   - Limitar transfer total < 20-25% por jogo
   - Evitar colapso de casa/fora
   - Manter probabilidade mínima ~15% por outcome

### ❌ Armadilhas

1. **Feature Bloat**
   - Adicionar todas as features ≠ melhor resultado
   - Features fracas diluem sinal
   - Overfitting para dataset específico

2. **Efeito Cascata**
   - Múltiplos transfers simultâneos = exponencial
   - Casa perde 5% × 8 layers = -40% total ❌

3. **Correlation Blindness**
   - Features correlacionadas somam efeito
   - Ex: ELO ↔ Força ↔ xG (redundantes)
   - Um já captura a informação

4. **Complexidade vs Performance**
   - Sistema complexo (16 layers) ≠ melhor accuracy
   - Dificulta debug e manutenção
   - Trade-off não vale a pena

---

## 🎯 Estratégia Corrigida

### Fase 1: Restaurar Baseline ✅
- Reverter para 10+8 layers
- Validar retorno a 54.12% filtered
- Confirmar estabilidade

### Fase 2: Teste Incremental Individual
Testar **1 layer por vez** das candidatas:

**Priority 1 - Features Fortes:**
1. ⚡ **ELO equilibrado** (diff < 30) → +7% empate
   - ELO é indicador técnico muito preciso
   - Correlação baixa com xG/força
   - Esperado: +1-2pp accuracy

2. 🛡️ **Defesas sólidas bilateral** (40%+ CS) → +4-10% empate
   - Clean sheets = métrica objetiva
   - Independente de xG/força
   - Esperado: +1-1.5pp accuracy

**Priority 2 - Contextuais:**
3. 🌧️ **Weather severity** (≥6/10) → +3-9% empate
   - Dados objetivos (API)
   - Impacto claro em gols
   - Esperado: +0.5-1pp accuracy

4. 🏆 **Match importance** (≥8.5) → +6% empate
   - Jogos decisivos = comportamento diferente
   - Moderadamente independente
   - Esperado: +0.3-0.8pp accuracy

**Descartar:**
- ❌ Corners (proxy fraco de pressão)
- ❌ Discipline (correlação baixa com resultado)
- ❌ BTTS H2H (ruidoso, poucos jogos)

### Fase 3: Ajuste Fino
- Se layer adiciona ≥+0.5pp → **manter**
- Se layer adiciona <+0.5pp → **descartar**
- Se layer piora accuracy → **descartar imediatamente**

### Fase 4: Calibração de Pesos
- Ajustar % de transfer de cada layer
- Otimizar com grid search pequeno
- Target: minimizar viés casa/fora

---

## 📈 Expectativas Realistas

### Baseline (Atual)
```
Filtered: 54.12%
Coverage: 72%
```

### Com ELO Layer (Otimista)
```
Filtered: 55-56%
Coverage: 70-72%
Ganho: +1-2pp
```

### Com ELO + Clean Sheets (Realista)
```
Filtered: 56-57%
Coverage: 68-70%
Ganho: +2-3pp
```

### Ceiling Teórico
```
Filtered: 57-60% (máximo alcançável)
Coverage: 65-70%
Nota: Requer features externas (lineup confirmado, árbitro, etc)
```

---

## 🚀 Próximos Passos

1. ✅ **Validar baseline restaurado** (aguardando)
2. 🔄 **Testar ELO layer individualmente**
3. 🔄 **Testar Clean Sheets layer**
4. 🔄 **Comparar resultados**
5. 📊 **Documentar ganhos reais**
6. 🎯 **Decidir manter ou descartar**

---

## 🧠 Insights-Chave

> **"Mais features NÃO significa melhor acurácia. Foco em features fortes e independentes > feature bloat."**

> **"Validação incremental (1 por vez) >>> implementação em massa."**

> **"Monitorar distribuição (casa/empate/fora) é tão importante quanto accuracy geral."**

> **"Transfer limits evitam colapso de outcomes. Sempre manter probabilidade mínima ~15%."**

---

## 📚 Referências Técnicas

- Baseline: validation_orchestrator_20260124_135231.json (54.12%)
- Completo: validation_orchestrator_20260124_154727.json (42.86%)
- Código: apps/analysis/services/statistical_models.py (linhas 658-885)

---

**Conclusão:** Sistema de boost é **sensível a overtuning**. Abordagem incremental e conservadora é essencial para manter estabilidade e evitar regressão de accuracy.
