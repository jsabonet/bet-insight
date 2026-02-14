# 🚨 CORREÇÃO URGENTE: Restaurar Acurácia Após Sistema de Contextualização

**Data:** 10 de Fevereiro de 2026  
**Problema:** Acurácia caiu drasticamente em produção após implementação do sistema de contextualização  
**Causa Raiz:** Thresholds muito baixos permitindo apostas de baixa qualidade

---

## 📊 DIAGNÓSTICO

### **Problema Identificado:**

O sistema de contextualização (`market_selector.py` + `context_analyzer.py`) foi implementado CORRETAMENTE, mas os **thresholds foram reduzidos demais** na tentativa de detectar mais padrões:

```python
# market_selector.py linha 275-285 (ATUAL - PROBLEMÁTICO)
if strategy == 'multiple':
    min_probability = 0.40  # 40% - MUITO BAIXO!
    min_context_score = 0.30  # 30% - MUITO BAIXO!
    min_final_score = 0.28  # 28% - MUITO BAIXO!
else:  # 'value'
    min_probability = 0.28  # 28% - ABSURDAMENTE BAIXO!
    min_context_score = 0.40  # 40% - MUITO BAIXO!  
    min_final_score = 0.28  # 28% - MUITO BAIXO!
```

### **Impacto:**

✅ **Positivo:**
- Sistema detecta padrões contextuais
- Identifica mercados favorecidos pelo contexto

❌ **Negativo (CRÍTICO):**
- **Apostas com 28% de probabilidade** → 72% de chance de perder!
- **Context score de 30%** → Contexto fraco, pouca fundamentação
- **Final score de 28%** → Apostas de qualidade terrível
- **Resultado:** Acurácia em produção caiu drasticamente

---

## 📈 HISTÓRICO DE ACURÁCIA

| Período | Sistema | Acurácia | Status |
|---------|---------|----------|--------|
| **Baseline** | Decision Engine original | **60.8%** | ✅ BOM |
| **Correção 3** | Threshold 27% | **23.08%** | ❌ DESASTRE |
| **Correção 4** | Threshold 23% | **42.11%** | ❌ RUIM |
| **Revert** | Volta ao baseline | **44.35%** | ⚠️ ACEITÁVEL |
| **Sistema Contextual** | Thresholds 28-40% | **~35-40%** (estimado) | ❌ QUEDA DRÁSTICA |

---

## ✅ SOLUÇÃO IMEDIATA

### **CORREÇÃO 1: Restaurar Thresholds Realistas**

#### Arquivo: `market_selector.py` linha 275-285

**SUBSTITUIR:**
```python
# Thresholds baseados em estratégia
if strategy == 'multiple':
    min_probability = 0.40  # Bilhetes: apostas >= 40%
    min_context_score = 0.30  # Contexto flexível (aceita qualquer contexto >= 30%)
    min_final_score = 0.28  # Score final flexível
else:
    min_probability = 0.28  # Value: aceita menor prob se EV bom
    min_context_score = 0.40  # Contexto flexível (reduzido de 45%)
    min_final_score = 0.28  # Score final baixo
```

**POR (THRESHOLDS REALISTAS):**
```python
# Thresholds baseados em estratégia - CORRIGIDOS para produção
if strategy == 'multiple':
    min_probability = 0.55  # Bilhetes: apostas SEGURAS >= 55%
    min_context_score = 0.65  # Contexto FORTE >= 65%
    min_final_score = 0.50  # Score final MIN 50%
else:  # 'value'
    min_probability = 0.45  # Value: apostas com pelo menos 45% de chance
    min_context_score = 0.60  # Contexto razoável >= 60%
    min_final_score = 0.45  # Score final MIN 45%
```

**Justificativa:**
- **55% prob (múltiplo)** → Apostas com >50% de chance (verdadeiras apostas seguras)
- **45% prob (value)** → Permite value bets mas ainda com fundamentação sólida
- **65% context (múltiplo)** → Contexto REALMENTE favorece o mercado
- **60% context (value)** → Contexto razoável, não fraco
- **50% final score** → Apostas de qualidade mínima aceitável

---

### **CORREÇÃO 2: Adicionar Validação de Qualidade**

#### Arquivo: `market_selector.py` após linha 370

**ADICIONAR NOVO MÉTODO:**
```python
def _validate_bet_quality(self, probability, context_score, final_score, strategy):
    """
    Validação EXTRA de qualidade para evitar apostas ruins.
    
    Critérios de segurança (além dos thresholds):
    1. Probabilidade + Context devem ser consistentes
    2. Evitar apostas com probabilidade OK mas contexto fraco
    3. Evitar apostas com contexto OK mas probabilidade fraca
    """
    # Regra 1: Probabilidade e contexto devem estar alinhados
    if probability >= 0.60 and context_score < 0.50:
        logger.warning(f"   ⚠️ Prob alta ({probability:.0%}) mas contexto fraco ({context_score:.0%}) - REJEITADA")
        return False
    
    if context_score >= 0.80 and probability < 0.35:
        logger.warning(f"   ⚠️ Contexto forte ({context_score:.0%}) mas prob fraca ({probability:.0%}) - REJEITADA")
        return False
    
    # Regra 2: Para bilhetes múltiplos, ser ainda mais conservador
    if strategy == 'multiple':
        # Exigir que prob OU context sejam excelentes
        if probability < 0.65 and context_score < 0.75:
            logger.warning(f"   ⚠️ Bilhete: nem prob ({probability:.0%}) nem context ({context_score:.0%}) são excelentes - REJEITADA")
            return False
    
    # Regra 3: Score final deve refletir qualidade mínima
    min_acceptable = 0.50 if strategy == 'multiple' else 0.45
    if final_score < min_acceptable:
        logger.warning(f"   ⚠️ Score final ({final_score:.2f}) abaixo do aceitável ({min_acceptable}) - REJEITADA")
        return False
    
    return True
```

**E USAR NA SELEÇÃO (linha ~350):**
```python
# Filtrar mercados que atendem thresholds E validação de qualidade
qualified_markets = []
for market_data in context_top_markets:
    # ... código existente ...
    
    # NOVO: Validação extra de qualidade
    if not self._validate_bet_quality(probability, context_score, final_score, strategy):
        continue  # Pular esta aposta
    
    qualified_markets.append(market_data)
```

---

### **CORREÇÃO 3: Ajustar Context Analyzer - Patterns Menos Agressivos**

#### Arquivo: `context_analyzer.py` linha 160-180

**PROBLEMA:** Padrões estão detectando cenários com pesos muito altos mesmo sem fundamento forte.

**SOLUÇÃO:** Reduzir pesos dos mercados favorecidos e aumentar confidence threshold.

**EXEMPLO - Pattern `balanced_tight_game` (linha ~400):**

**ANTES:**
```python
'market_weights': {
    'draw': 0.75,  # MUITO ALTO
    'draw_ht': 0.70,  # MUITO ALTO
    'under_2.5': 0.65,  # MUITO ALTO
    # ...
}
```

**DEPOIS:**
```python
'market_weights': {
    'draw': 0.55,  # REALISTA para draw
    'draw_ht': 0.50,  # REALISTA para HT
    'under_2.5': 0.50,  # REALISTA para under
    # ...
}
```

**Aplicar em TODOS os padrões:**
- low_motivation_both: weights de 0.95 → 0.70
- asymmetric_motivation: weights de 0.90 → 0.65
- defensive_fatigue: weights de 0.85 → 0.60
- etc.

---

## 🎯 RESULTADOS ESPERADOS

### ANTES (Atual - Problemático)
```
Arsenal vs Chelsea
→ 20 mercados passam threshold de 28%
→ Top 3: Under 1.5 (31% prob, contexto 42%)  ❌
→ Top 3: Draw (35% prob, contexto 38%)  ❌
→ Top 3: Away Over 0.5 (40% prob, contexto 35%)  ❌
Resultado: 3 apostas ruins → PERDA
```

### DEPOIS (Corrigido)
```
Arsenal vs Chelsea  
→ 5 mercados passam threshold de 45%+
→ Top 3: Under 2.5 (72% prob, contexto 68%, score 0.70)  ✅
→ Top 3: Draw HT (65% prob, contexto 73%, score 0.65)  ✅
→ Top 3: BTTS No (58% prob, contexto 62%, score 0.58)  ✅
Resultado: 3 apostas sólidas → GANHO
```

### Métricas Esperadas

| Métrica | Atual (P problemático) | Meta (Corrigido) |
|---------|---------|---------|
| **Acurácia** | ~35-40% | **55-65%** |
| **Apostas/Dia** | 15-20 | 5-10 |
| **Qualidade Média** | Baixa (28-40% prob) | Alta (55-70% prob) |
| **ROI** | Negativo | Positivo |

**Filosofia:** Menos apostas, MAS MUITO MELHORES.

---

## 🔧 IMPLEMENTAÇÃO

### Passo 1: Backup
```bash
cd D:\Projectos\Football\bet-insight\backend\apps\analysis\services
cp market_selector.py market_selector.py.backup_20260210
cp context_analyzer.py context_analyzer.py.backup_20260210
```

### Passo 2: Aplicar Correções
1. Editar `market_selector.py` - Correção 1 (thresholds) e Correção 2 (validação)
2. Editar `context_analyzer.py` - Correção 3 (reduzir pesos)

### Passo 3: Testar
```bash
python test_market_selector_celta.py
```

**Verificar:**
- Poucas apostas são retornadas (5-10 mercados passam threshold)
- Todas com prob ≥ 45% e context ≥ 60%
- Final scores ≥ 0.45

### Passo 4: Validar em Produção
```bash
python validate_accuracy_with_real_matches.py
```

**Meta:** Acurácia ≥ 55%

---

## 🚨 ROLLBACK SE NECESSÁRIO

Se acurácia não melhorar após 48h:

```bash
cd D:\Projectos\Football\bet-insight\backend\apps\analysis\services
mv market_selector.py market_selector.py.failed
mv market_selector.py.backup_20260210 market_selector.py
mv context_analyzer.py context_analyzer.py.failed  
mv context_analyzer.py.backup_20260210 context_analyzer.py
```

---

## 📝 LIÇÕES APRENDIDAS

1. **Thresholds baixos = Acurácia DESTRUÍDA**
   - 28% de probabilidade não é "value bet", é aposta ruim
   - 30% de context score não é "flexível", é fraco

2. **Sistema de contextualização É BOM, thresholds RUINS**
   - A ideia de analisar contexto está correta
   - Mas precisa de filtros de qualidade rigorosos

3. **Qualidade > Quantidade**
   - Melhor 5 apostas com 70% de chance
   - Do que 20 apostas com 35% de chance

4. **Validação em produção é ESSENCIAL**
   - Testes locais podem parecer ok
   - Produção revela problemas reais

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Backup dos arquivos originais
- [ ] Aplicar Correção 1 (thresholds realistas)
- [ ] Aplicar Correção 2 (validação de qualidade)
- [ ] Aplicar Correção 3 (reduzir pesos dos patterns)
- [ ] Testar com `test_market_selector_celta.py`
- [ ] Validar com `validate_accuracy_with_real_matches.py`
- [ ] Monitorar acurácia em produção por 48h
- [ ] Documentar resultados

---

**PRIORIDADE: 🔴 CRÍTICA - IMPLEMENTAR IMEDIATAMENTE**
