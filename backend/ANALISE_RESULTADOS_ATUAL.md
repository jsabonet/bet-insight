# ANÁLISE RESULTADOS VALIDAÇÃO - 23/01/2026 15:51

## 📊 RESULTADOS OBTIDOS

### Métricas Gerais
```
Total: 120 partidas
Acurácia Pick Recomendado: 46.67% (56/120)
Acurácia Filtrada (high-quality): 52.27% (88/120 coverage)
Brier Score: 0.2061
```

### ✅ VITÓRIAS - O QUE FUNCIONOU

**1. EMPATES AGORA SÃO PREVISTOS!**
- **ANTES:** 0/79 (0%) empates previstos
- **DEPOIS:** 53/120 (44.2%) empates previstos
- **Acurácia de empates:** 21/45 (46.7%) ✅ EXCELENTE!

**2. ACURÁCIA DE CASA MELHOROU**
- Casa: 31/38 (81.6%) quando prevemos casa acertamos!
- Viés de casa: 49.2% vs 31.7% real (+17.5pp)
  - **ANTES:** 78% casa (viés +48pp)
  - **DEPOIS:** 49% casa (viés +17pp) ✅ REDUZIU 65%!

**3. ESTRATÉGIA DE FILTRO FUNCIONA**
- Sem filtro: 46.67% acurácia
- Com filtro (high-quality): 52.27% acurácia
- **Ganho:** +5.6pp (+12% relativo)

## ❌ PROBLEMAS IDENTIFICADOS

### PROBLEMA #1: VIÉS CONTRA FORA É CRÍTICO

```
DISTRIBUIÇÃO:
  Previsões Casa:   59/120 (49.2%)
  Previsões Empate: 53/120 (44.2%)
  Previsões Fora:    8/120 ( 6.7%) ❌ MUITO BAIXO!

REALIDADE:
  Casa:   38/120 (31.7%)
  Empate: 45/120 (37.5%)
  Fora:   37/120 (30.8%) ← 31% dos jogos!

VIÉS:
  Casa:   +17.5pp (sobre-previsto)
  Empate:  +6.7pp (sobre-previsto)
  Fora:   -24.2pp (sub-previsto) ❌ CRÍTICO!
```

**CAUSA RAIZ:**
O boost de empate está "roubando" probabilidade de FORA, não de CASA.

**Exemplo:**
```
ANTES DO BOOST:
Casa:   45% | Empate: 28% | Fora: 27%

APÓS BOOST (empate 1.5x):
Casa:   45% | Empate: 42% | Fora: 27%

APÓS NORMALIZAÇÃO:
Casa:   39% | Empate: 37% | Fora: 24% ← PENALIZADO!
```

### PROBLEMA #2: ACURÁCIA DE FORA PÉSSIMA

```
Acurácia por tipo:
  Casa:   31/38 (81.6%) ✅
  Empate: 21/45 (46.7%) ✅
  Fora:    4/37 (10.8%) ❌ CRÍTICO!
```

**37 jogos com vitória fora**, previmos apenas **8** (6.7%), acertamos **4** (10.8%).

Isso significa que **33 vitórias fora** (89%) não foram previstas!

## 🔍 ANÁLISE TÉCNICA

### Por que Fora está sendo penalizado?

**Teoria:** O boost de empate aumenta numerador de draw, mas na normalização:
```python
# Antes normalização:
total = 45 + 42 + 27 = 114  # > 100% devido ao boost!

# Normalização divide por total:
casa_final = 45 / 114 = 39.5%
draw_final = 42 / 114 = 36.8%  
fora_final = 27 / 114 = 23.7%  ← REDUZ FORA!
```

**Solução:** Boost deve transferir probabilidade de CASA para EMPATE, não aumentar total!

### Comparação Consensus vs Previsões

Script `analyze_consensus.py` mostra:
```
Consensus médio (ANTES dos boosts no orchestrator):
  Casa:   43.2%
  Empate: 26.1%
  Fora:   30.6%

Previsões finais (DEPOIS dos boosts):
  Casa:   49.2%  (+6pp)
  Empate: 44.2%  (+18.1pp) ✅ Boost funcionou!
  Fora:    6.7%  (-23.9pp) ❌ Penalizado demais!
```

## 🎯 PLANO DE AÇÃO

### PRIORIDADE 1: REBALANCEAR BOOST (URGENTE)

**Opção A - Boost Transferencial (RECOMENDADO):**
```python
# Antes do boost, calcular excesso de casa vs empate
prob_diff = abs(consensus['home_win'] - consensus['draw'])

if prob_diff < 0.20 and consensus['home_win'] > consensus['draw']:
    # Transferir probabilidade de CASA para EMPATE
    transfer_amount = consensus['home_win'] * 0.15  # 15% de casa
    consensus['home_win'] -= transfer_amount
    consensus['draw'] += transfer_amount
    # FORA não é afetado!
```

**Impacto esperado:**
- Empates mantêm: 44% → 40-45%
- Casa reduz: 49% → 35-40%
- Fora aumenta: 7% → 20-25%
- Acurácia geral: 47% → 50-55%

**Opção B - Boost Seletivo:**
```python
# Só boostar empate quando casa E fora são parecidos
home_away_diff = abs(consensus['home_win'] - consensus['away_win'])

if home_away_diff < 0.15:  # Times equivalentes
    # Aumentar empate, reduzir AMBOS proporcionalmente
    boost = 1.3
    consensus['draw'] *= boost
    consensus['home_win'] *= 0.85
    consensus['away_win'] *= 0.85
```

**Impacto esperado:**
- Menos boost total (mais seletivo)
- Empates: 44% → 35-40%
- Casa: 49% → 40-45%
- Fora: 7% → 15-20%

### PRIORIDADE 2: ADICIONAR BOOST PARA FORA

```python
# Detectar favoritos visitantes (odd casa > 2.5)
if market_odds and market_odds.get('home_win', 0) > 2.5:
    # Visitante é favorito!
    away_boost = 1.25
    consensus['away_win'] *= away_boost
    logger.info(f"🚀 [Calibração] Visitante favorito → Boost: {away_boost}x")

# Detectar força fora maior que casa
strength_diff = features.get('strength', {}).get('strength_diff', 0)
if strength_diff < -0.20:  # Fora muito mais forte
    away_boost = 1.15
    consensus['away_win'] *= away_boost
```

### PRIORIDADE 3: AJUSTAR ENSEMBLE WEIGHTS

Possível que Poisson/Logistic tenham viés contra fora:
```python
# Testar pesos alternativos:
# ATUAL:
#   Poisson: 40%, Logistic: 45%, Market: 15%

# TESTE:
#   Poisson: 35%, Logistic: 50%, Market: 15%
#   (Logistic melhor para away wins)
```

## 📋 CHECKLIST DE TESTES

Após implementar correções, validar:

**Distribuição de Previsões:**
- [ ] Casa: 35-42% (alvo: ~35%, realidade: 31.7%)
- [ ] Empate: 35-42% (alvo: ~38%, realidade: 37.5%)
- [ ] Fora: 20-30% (alvo: ~27%, realidade: 30.8%)

**Viés (Previsão - Realidade):**
- [ ] Casa: < 10pp (atual: +17.5pp)
- [ ] Empate: < 10pp (atual: +6.7pp)
- [ ] Fora: < 10pp (atual: -24.2pp) ← CRÍTICO

**Acurácia por Tipo:**
- [ ] Casa: > 70% (atual: 81.6% ✅)
- [ ] Empate: > 40% (atual: 46.7% ✅)
- [ ] Fora: > 30% (atual: 10.8% ❌)

**Métricas Gerais:**
- [ ] Acurácia geral: > 50% (atual: 46.67%)
- [ ] Pick recomendado: > 52% (atual: 46.67%)
- [ ] Brier Score: < 0.20 (atual: 0.2061)

## 🚀 NEXT STEPS

1. **Implementar Opção A (Boost Transferencial)**
   - Modificar `statistical_models.py` linha 660-700
   - Transferir de casa para empate (não aumentar total)

2. **Adicionar Boost Fora (Favorito Visitante)**
   - Detectar odd casa > 2.5 OR strength_diff < -0.20
   - Boost away_win em 15-25%

3. **Rodar Nova Validação**
   ```bash
   python validation_with_orchestrator.py
   python analyze_validation_final.py
   ```

4. **Verificar Melhorias**
   - Fora predictions: 7% → 20-25%
   - Fora accuracy: 10.8% → 30%+
   - Overall accuracy: 46.67% → 50-55%

## 💡 INSIGHTS

### O que aprendemos:

1. ✅ **Boost funcionou para empates** - 0% → 44% predictions, 46.7% accuracy
2. ✅ **Filtro high-quality funciona** - +5.6pp accuracy trade-off 27% volume
3. ❌ **Boost não pode apenas multiplicar** - penaliza outros outcomes na normalização
4. ❌ **Sistema tem viés estrutural contra fora** - precisa boost específico

### Comparação com objetivos:

**OBJETIVO ORIGINAL:** 55%+ acurácia
**RESULTADO ATUAL:** 46.67% (Pick), 52.27% (Filtrado)
**PROGRESSO:** 40.51% → 46.67% (+6.16pp em 1 iteração!)

**OBSTÁCULO:** Fora sub-previsto impede atingir 55%
- 37 jogos fora, só acertamos 4 (10.8%)
- Se acertássemos 30% (11 jogos): +7 acertos → 53% acurácia! ✅

---

**Conclusão:** Estamos a **1 correção** de atingir 50-55% acurácia. 
Foco total: **REBALANCEAR BOOST PARA NÃO PENALIZAR FORA**
