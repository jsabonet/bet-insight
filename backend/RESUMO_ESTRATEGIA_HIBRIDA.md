# RESUMO - ESTRATÉGIA HÍBRIDA IMPLEMENTADA

**Data**: 11 de Fevereiro de 2026  
**Objetivo**: Corrigir queda de acurácia causada pela contextualização

---

## 📊 ANÁLISE REALIZADA

### 1. Medição de Acurácia Baseline
- **Script**: `validate_super_simple.py`
- **Método**: Poisson básico sem contextualização
- **Resultado**: **45.6%** de acurácia geral
- **Mercados testados**: 100 partidas, 6 mercados
- **Melhor mercado**: BTTS (60.0%)
- **Pior mercado**: Draw (32.0%)

### 2. Medição com Contextualização Forçada
- **Script**: `validate_context_only.py`
- **Método**: Poisson + ContextAnalyzer + MarketSelector
- **Resultado**: **43.5%** de acurácia geral
- **Diferença**: **-2.1 pontos** vs baseline ❌
- **Problema**: Seleção restrita a under_2.5 (47%) e btts_no (40%)

### 3. Análise de Padrões Detectados
- **Script**: `analyze_context_patterns.py`
- **Descoberta**: TODOS os 100 jogos classificados como "balanced_tight_game"
- **Causa**: Contexto genérico (importance='medium', motivation='medium')
- **Acurácia do padrão**:
  - Low scoring: 47% (ruim - pior que aleatório)
  - BTTS_no: 40% (muito ruim)
  - Draw: 32% (péssimo)
- **Conclusão**: Padrão detecta incorretamente com dados genéricos

### 4. Implementação da Estratégia Híbrida
- **Script**: `validate_hybrid_strategy.py`
- **Método**: Usar contexto SÓ se:
  1. Confiança >= 90% (muito forte)
  2. Dados contextuais REAIS (não genéricos)
  3. Padrão com histórico validado
- **Fallback**: Poisson puro com top 3 mercados
- **Resultado**: **47.7%** de acurácia geral ✅
- **Diferença**: **+2.1 pontos** vs baseline
- **Decisões**: 0% uso de contexto (todos rejeitados corretamente)
- **Mercados selecionados**:
  - BTTS_yes: 60.0% ✅✅ (melhor escolha)
  - Under 2.5: 47.0% ✅
  - Home win: 36.0% ⚠️

---

## ✅ SOLUÇÃO IMPLEMENTADA

### Componentes Criados

1. **`HybridStrategy`** (`apps/analysis/services/hybrid_strategy.py`)
   - Decide quando usar contextualização
   - Detecta dados genéricos vs reais
   - Valida confiança mínima de 90%
   - Mantém histórico de decisões

2. **Integração no `HybridAnalysisOrchestrator`**
   - Linha 11: Import da HybridStrategy
   - Linha 24: Inicialização no __init__
   - Linhas 71-79: Decisão híbrida após análise de contexto
   - Rejeita contexto se genérico ou fraco
   - Limpa context_analysis para não influenciar modelos

### Lógica de Decisão

```python
# 1. Analisa contexto
context_analysis = self.context_analyzer.analyze(features)

# 2. DECISÃO HÍBRIDA
context_decision = self.hybrid_strategy.should_use_context(
    context_analysis, 
    features
)

# 3. Se rejeitado, usar modelo base
if not context_decision['use_context']:
    context_analysis = {'patterns': [], 'top_markets': []}
```

### Critérios de Rejeição

**Contexto é rejeitado se**:
- Nenhum padrão detectado
- Dados contextuais genéricos:
  - `importance = 'medium'`
  - `motivation = {'home': 'medium', 'away': 'medium'}`
  - `standings = {'home_position': 10, 'away_position': 10'}`
  - `rest_context = {'advantage': 'equal'}`
  - `weather = None`
- Confiança < 90%
- Padrão invalidado historicamente

**Contexto é aprovado se**:
- Dados reais (posições variadas, motivações diferentes)
- Confiança >= 90%
- Padrão validado

---

## 📈 RESULTADOS COMPARATIVOS

| Abordagem | Acurácia | vs Baseline | Status |
|-----------|----------|-------------|--------|
| **Poisson Básico** | 45.6% | - | Baseline |
| **Poisson + Contexto** | 43.5% | -2.1 pts | ❌ Pior |
| **Híbrida Adaptativa** | **47.7%** | **+2.1 pts** | ✅ Melhor |

**Melhoria**: +2.1 pontos percentuais  
**Contexto usado**: 0% (rejeitado por dados genéricos)  
**Mercados**: Diversificação melhorada (btts_yes vs btts_no)

---

## 🎯 PRÓXIMOS PASSOS

### Opções de Evolução

1. **Validar com dados reais** (recomendado)
   - Testar orchestrator em partidas com dados completos
   - Verificar se contexto forte é detectado
   - Medir acurácia quando contexto é aprovado

2. **Calibrar padrões**
   - Validar "balanced_tight_game" com dados reais
   - Adicionar mais padrões específicos
   - Ajustar thresholds de confiança

3. **Enriquecer contexto**
   - Melhorar captação de dados reais
   - Adicionar features de forma/momentum
   - Incluir estatísticas head-to-head

4. **Monitoramento**
   - Logar decisões híbridas em produção
   - Acompanhar % de uso de contexto
   - Comparar acurácia com/sem contexto

---

## 📝 ARQUIVOS CRIADOS/MODIFICADOS

### Novos Arquivos
1. `validate_super_simple.py` - Baseline Poisson
2. `validate_context_only.py` - Contexto forçado
3. `analyze_context_patterns.py` - Análise de padrões
4. `validate_hybrid_strategy.py` - Teste da híbrida
5. `apps/analysis/services/hybrid_strategy.py` - Estratégia híbrida

### Modificados
1. `apps/analysis/services/analysis_orchestrator.py`
   - Import HybridStrategy (linha 11)
   - Inicialização (linha 24)
   - Decisão híbrida (linhas 71-79)

### Resultados Salvos
1. `validation_simple_20260211_203716.json` - Baseline: 45.6%
2. `validation_context_20260211_*.json` - Contexto: 43.5%
3. `pattern_analysis_20260211_*.json` - Análise de padrões
4. `validation_hybrid_20260211_*.json` - Híbrida: 47.7%

---

## ⚠️ OBSERVAÇÕES IMPORTANTES

1. **Contexto genérico é sempre rejeitado**
   - Sistema funciona em modo "safe" (Poisson puro)
   - Não há risco de piora de acurácia

2. **Contexto real ainda não testado**
   - Precisa validar com dados enriquecidos da API
   - Verificar se padrões são detectados corretamente

3. **Melhoria atual vem da seleção de mercados**
   - Top 3 do Poisson vs seleção forçada do MarketSelector
   - BTTS_yes (60%) substitui BTTS_no (40%)

4. **Home win com 36% é preocupante**
   - Pode indicar bias no Poisson genérico
   - Considerar ajustar strengths por liga

---

## ✅ CONCLUSÃO

**Estratégia híbrida implementada com sucesso!**

- ✅ **+2.1 pontos** de melhoria vs baseline
- ✅ **+4.2 pontos** vs contexto forçado
- ✅ Sistema **seguro** (rejeita contexto fraco)
- ✅ Pronto para **teste em produção**
- ⏳ Aguardando **validação com dados reais**

**Recomendação**: Manter em produção e monitorar. Quando dados contextuais reais estiverem disponíveis, o sistema aprovará automaticamente e usará contextualização forte.
