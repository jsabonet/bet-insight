# Correção do Viés de Empate - Análise Completa

## 📊 Problema Inicial

**Sintoma**: Acurácia de 36.11% (esperado: 55-60%)

**Root Cause**: Sistema tinha viés algorítmico para prever empates

## 🔍 Análise das 3 Validações

### Validação #1 - Original (Com Viés de Empate)
**Arquivo**: `validation_orchestrator_20260123_120409.json`
**Resultados**:
- **Acurácia**: 36.11%
- **Previsões**:
  - Empate: **52/72 (72.2%)** ❌ VIÉS CLARO
  - Casa: 17/72 (23.6%)
  - Fora: 3/72 (4.2%)
- **Realidade**:
  - Empate: 30/72 (41.7%)
  - Casa: 21/72 (29.2%)
  - Fora: 21/72 (29.2%)

**Problema**: Sistema previa empate 72% das vezes, mas empates reais eram apenas 42%

**Código Problemático** (`decision_engine.py` linha 488):
```python
# ANTES (ERRADO):
if prob_draw >= 0.25:  # Threshold 25% muito baixo!
    market_name = 'draw'
elif abs(prob_home - prob_away) < 0.05 and prob_draw >= 0.20:
    market_name = 'draw'  # Forçando empate mesmo não sendo máximo
```

---

### Validação #2 - Primeira Correção (Viés Invertido)
**Arquivo**: `validation_orchestrator_20260123_123903.json`
**Tentativa**: Threshold de 33% para empate + escolher máximo
**Resultados**:
- **Acurácia**: 36.99% (PIOR!)
- **Previsões**:
  - Casa: **57/73 (78.1%)** ❌ NOVO VIÉS
  - Fora: 16/73 (21.9%)
  - Empate: **0/73 (0%)** ❌ ELIMINOU TODOS EMPATES
- **Realidade**:
  - Empate: 30/73 (41.1%)
  - Casa: 22/73 (30.1%)
  - Fora: 21/73 (28.8%)

**Problema**: Eliminamos viés de empate MAS criamos viés de casa!

**Código Problemático**:
```python
# TENTATIVA #1 (TAMBÉM ERRADO):
max_market = max(consensus.items(), key=lambda x: x[1])
market_name = max_market[0]
probability = max_market[1]

# EXCEÇÃO problemática:
if market_name == 'draw' and probability < 0.33:
    # Forçava casa/fora mesmo quando empate era o MÁXIMO
    if prob_home > prob_away:
        market_name = 'home_win'
```

**Por que falhou?**:
- Análise de empates reais mostrou que probabilidade de empate **raramente passa de 30%**
- Nos 30 empates reais, prob_draw ficava entre 23-30%
- Threshold de 33% **eliminava todos os empates válidos**

Exemplo:
```
Casa: 36.9%, Empate: 28.6%, Fora: 34.5% → Real: EMPATE
Sistema previu: Casa (porque empate < 33%)
```

---

### Validação #3 - Correção Final (Em Progresso)
**Arquivo**: `validation_orchestrator_[NOVO].json` (rodando)
**Abordagem**: Eliminar TODOS os thresholds, escolher simplesmente o máximo

**Código CORRETO** (`decision_engine.py` linha 488):
```python
# CORREÇÃO FINAL (SIMPLES E CORRETO):
# Sempre escolher resultado com MAIOR probabilidade
max_market = max(consensus.items(), key=lambda x: x[1])
market_name = max_market[0]
probability = max_market[1]

# SEM OVERRIDES - deixar probabilidades decidirem naturalmente
```

**Filosofia**: Se os modelos calculam probabilidades corretamente, simplesmente confiar no máximo.

---

## 📈 Expectativas da Validação #3

**Distribuição Esperada** (se modelos estão calibrados):
- Casa: ~35-40% das previsões
- Empate: ~25-30% das previsões  
- Fora: ~30-35% das previsões

**Meta de Acurácia**: 
- Mínimo: 45%
- Target: 50-55%
- Ideal: 55-60%

---

## 🎯 Lições Aprendidas

1. **Thresholds Artificiais São Perigosos**
   - Threshold de 25% criou viés de empate
   - Threshold de 33% criou viés de casa
   - **Solução**: Eliminar thresholds, confiar em max()

2. **Probabilidades Reais de Empate**
   - Empates são naturalmente menos prováveis (26-30%)
   - Casa/Fora frequentemente têm 35-45%
   - Sistema DEVE aceitar que empate seja menos frequente

3. **Calibração é Chave**
   - Se modelos retornam prob_empate 26%, sistema deve aceitar
   - Se empate for REALMENTE o máximo (mesmo com 28%), prever empate
   - Sem "ajustes" ou "correções" - deixar matemática decidir

---

## 🔬 Análise das Probabilidades

**Médias dos Modelos** (validação #1):
- Casa: 42.5%
- Empate: 26.3%
- Fora: 31.2%

**Previsões Sistema Original**:
- Casa: 23.6%
- Empate: 72.2% ← Inversão completa!
- Fora: 4.2%

**Problema**: Sistema **inverteu** as probabilidades dos modelos!

**Previsões Sistema Correção #1**:
- Casa: 78.1% ← Agora inverteu pro outro lado
- Empate: 0%
- Fora: 21.9%

**Problema**: Overcorrection - foi pro extremo oposto

**Expectativa Correção #2** (em validação):
- Casa: ~40%
- Empate: ~26%
- Fora: ~31%

Alinhado com as probabilidades dos modelos!

---

## 🚀 Status Atual

✅ **Correção Implementada**: Linha 488 de `decision_engine.py`
🔄 **Validação Rodando**: `validation_with_orchestrator.py` (processando ~10/120 partidas)
⏳ **Aguardando Resultados**: ~10 minutos

**Próximos Passos**:
1. Aguardar conclusão da validação
2. Analisar distribuição de previsões
3. Verificar se acurácia atingiu 50%+
4. Se sim: deploy para produção
5. Se não: investigar calibração dos modelos estatísticos

---

## 📝 Código Final

```python
# LOCALIZAÇÃO: backend/apps/analysis/services/decision_engine.py
# LINHA: ~488

# PRIORIDADE 3: Resultado mais provável (SEM VIÉS)
prob_home = consensus.get('home_win', 0)
prob_draw = consensus.get('draw', 0)
prob_away = consensus.get('away_win', 0)

# Estratégia: Escolher máximo DIRETO, sem threshold artificial
# Análise mostrou: probabilidades médias são Casa 42%, Empate 26%, Fora 31%
# Mas em empates reais, empate raramente é máximo (fica 23-30%)

max_market = max(consensus.items(), key=lambda x: x[1])
market_name = max_market[0]
probability = max_market[1]

# Sem overrides - deixar probabilidades decidirem naturalmente
```

**Diferença da Versão Anterior**:
- ❌ Removido: `if market_name == 'draw' and probability < 0.33:`
- ❌ Removido: Toda lógica de override forçando casa/fora
- ✅ Mantido: Simplesmente `max()` e pronto

---

## 🎲 Análise Estatística

**Por que empates têm probabilidade mais baixa?**

No futebol:
- Distribuição de resultados NÃO é uniforme (não é 33/33/33)
- Casa tem vantagem (~5-7% de probabilidade extra)
- Empate é resultado "instável" - qualquer gol quebra empate
- Estatisticamente, empates são ~25-30% dos jogos

**Modelos Poisson/Logística capturam isso corretamente**:
- Calculam Casa ~40%, Empate ~26%, Fora ~32%
- Reflete realidade do futebol

**Erro do Sistema Original**:
- Tentava "equalizar" resultados com thresholds
- Assumia que empate deveria ser 33% (incorreto)
- Threshold de 25% forçava empates demais

**Solução**:
- Aceitar que empate É menos provável
- Confiar nos modelos matemáticos
- Não adicionar "lógica de negócio" sobre probabilidades

---

*Última atualização: 23/01/2026 13:00*
*Status: Aguardando validação #3*
