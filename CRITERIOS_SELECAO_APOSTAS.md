# Critérios de Seleção de Apostas - IA

## Visão Geral

O sistema possui **2 modos de operação** com critérios diferentes:

### 🎯 **Modo "VALUE" (Apostas Simples)**
- **Objetivo**: Maximizar Expected Value (EV)
- **Estratégia**: Aceita qualquer probabilidade se o EV for favorável
- **Uso**: Apostas individuais para bankroll management agressivo

### 📋 **Modo "MULTIPLE" (Bilhetes/Acumuladores)**
- **Objetivo**: Maximizar probabilidade de acerto
- **Estratégia**: Prioriza alta probabilidade, aceita perda moderada de value
- **Uso**: Bilhetes combinados onde a segurança é mais importante

---

## 1. Modo VALUE (Apostas Simples) ⚡

### Fórmula de Score
```python
prob_weight = probabilidade  # Linear, sem penalização

# EV negativo: penalização severa (5x mais impacto)
if EV < 0:
    ev_weight = max(0.3, 1 + EV/20)
# EV positivo: amplificação forte (3x mais impacto)  
else:
    ev_weight = 1 + EV/30

score = prob_weight × ev_weight × confiança × fator_risco
```

**Exemplos de Cálculo** (conf=1.0, risk=1.0):
- **Under 2.5**: prob=52.3%, EV=+23%
  - `ev_weight = 1 + 23/30 = 1.767`
  - `score = 0.523 × 1.767 = 0.924` ✅ **VENCEDOR**
  
- **1X (Dupla Chance)**: prob=86.6%, EV=-2%
  - `ev_weight = 1 + (-2)/20 = 0.9`
  - `score = 0.866 × 0.9 = 0.779`
  
- **Casa Over 0.5**: prob=83.2%, EV=-3%
  - `ev_weight = 1 + (-3)/20 = 0.85`
  - `score = 0.832 × 0.85 = 0.707`

**Resultado**: Aposta com EV +23% supera favoritos com EV negativo!

### Critérios de Seleção

#### 1.1 Filtros Mínimos
- **Probabilidade mínima**: 15% (muito permissivo)
- **EV mínimo (prioridade)**:
  1. **IDEAL**: EV ≥ 0% (value real - prioriza estas)
  2. **ACEITÁVEL**: EV ≥ -2% (neutro - só se não houver EV positivo)
  3. **ÚLTIMO RECURSO**: EV ≥ -5% (só se não houver EV positivo/neutro)
- **Market odds**: Deve existir e ser > 0

**Lógica de Seleção**:
- Se existir **pelo menos 1 aposta com EV ≥ 0%**: usa **APENAS** apostas com EV positivo
- Se **não existir EV positivo**: aceita EV neutro (-2% a 0%)
- Se **não existir EV positivo nem neutro**: aceita EV até -5% como último recurso
- **NUNCA** mistura apostas de diferentes níveis de EV (não combina EV +10% com EV -3%)

#### 1.2 Priorização (ordem de preferência)
1. **BTTS (Ambos Marcam)** com probabilidade ≥ 65%
   - Histórico comprovado: 61.67% de acurácia
   - Melhor mercado do sistema
   
2. **Value Bet** com confiança ≥ 65% E probabilidade ≥ 30%
   - Odds de mercado > odds justas × 1.05 (5% margem de segurança)
   - Value % = ((market_odd / fair_odd) - 1) × 100
   
3. **Resultado mais provável** (1X2)
   - Sem threshold artificial
   - Escolhe diretamente o resultado com maior probabilidade

#### 1.3 Mercados Avaliados
- **1X2**: Casa, Empate, Fora (threshold 15%)
- **Over/Under 2.5**: Mais/Menos 2.5 gols (threshold 30%)
- **Over/Under 1.5**: Mais/Menos 1.5 gols (threshold 25%)
- **Over/Under 3.5**: Mais/Menos 3.5 gols (threshold 25%)
- **BTTS**: Ambos marcam Sim/Não (threshold 30%)
- **Dupla Chance**: 1X, 12, X2 (threshold 60%)
- **Team Goals**: Gols do time Casa/Fora (threshold 25%)

#### 1.4 Cálculo de Stake
Base: 1.0 unidade

**Ajustes**:
- EV ≥ 10%: +0.5u
- EV ≥ 5%: +0.3u
- EV < -5%: -0.3u
- Confiança ≥ 0.8: +0.3u
- Confiança < 0.5: -0.3u

**Limites por risco**:
- Risco BAIXO: máx 2.0u
- Risco MÉDIO: máx 1.5u
- Risco ALTO: máx 0.5u

#### 1.5 Top 3 Apostas VALUE
- Ordena TODOS os candidatos válidos por **score** (EV domina)
- Seleciona top 3 com maior score
- Evita duplicatas de mercado
- Prefere categorias diferentes quando possível

---

## 2. Modo MULTIPLE (Bilhetes) 📋

### Fórmula de Score
```python
prob_weight = probabilidade^1.5  # Penaliza probabilidades baixas
ev_weight = max(0.5, 1 + EV/200)  # EV com metade do peso

score = prob_weight × ev_weight × confiança × fator_risco
```

**Diferenças vs VALUE**:
- Probabilidade **elevada a 1.5** (penaliza baixas probabilidades)
  - 90% → 85.3%
  - 70% → 58.7%
  - 60% → 46.5%
  - 50% → 35.4%
  - 40% → 25.3%
  - 30% → 16.4%
- EV tem **metade do peso** (dividido por 200 em vez de 30)
  - EV +20% impacta apenas +10% no score
  - EV -10% impacta apenas -5% no score

### Critérios de Seleção

#### 2.1 Filtro Progressivo por Probabilidade

**Sistema de "favoritos"** com tolerância de EV negativo:

| Probabilidade | Classificação | EV Mínimo | Lógica |
|--------------|---------------|-----------|--------|
| ≥ 70% | Favorito Absoluto | -15% | Aceita grande perda de value |
| ≥ 60% | Favorito Forte | -10% | Aceita perda moderada |
| ≥ 50% | Provável | -5% | Aceita perda mínima |
| ≥ 40% | Razoável | -3% | Aceita perda pequena |
| ≥ 30% | Possível | 0% | Só aceita EV neutro ou positivo |
| < 30% | **REJEITADO** | N/A | Muito arriscado para bilhetes |

#### 2.2 Exemplo Prático

**Candidato A**: Real Madrid 70% prob, EV -12%
- ✅ **ACEITO** (favorito absoluto: -12% > -15%)

**Candidato B**: Barcelona 55% prob, EV -8%
- ❌ **REJEITADO** (provável: -8% < -5%)

**Candidato C**: Over 2.5 com 45% prob, EV +2%
- ❌ **REJEITADO** (razoável: +2% ≥ -3%, mas score será baixo devido a prob^1.5 = 30%)

**Candidato D**: BTTS 65% prob, EV -6%
- ✅ **ACEITO** (favorito forte: -6% > -10%)

#### 2.3 Mercados Avaliados (mesmos do VALUE)
- 1X2, Over/Under (1.5, 2.5, 3.5)
- BTTS, Dupla Chance, Team Goals

#### 2.4 Top 3 Apostas MULTIPLE
- Ordena candidatos por **score** (probabilidade^1.5 domina)
- Seleciona top 3 com maior score
- Evita duplicatas de mercado
- Prefere categorias diferentes quando possível

---

## 3. Value Bets (Comum a Ambos Modos)

### Definição
**Value bet** = Aposta onde a probabilidade do modelo é maior que a probabilidade implícita do mercado

### Cálculo
```python
fair_odd = 1 / probabilidade_modelo
market_odd = odd_da_casa_de_apostas

# Margem de segurança: 5%
if market_odd >= fair_odd × 1.05:
    value_pct = ((market_odd / fair_odd) - 1) × 100
    edge = value_pct / 100
```

### Exemplo
- Modelo prevê: Vitória Fora 40% → Fair Odd = 2.50
- Mercado oferece: 2.80
- Value: 2.80 / 2.50 = 1.12 → **12% de value**
- Edge: 0.12 (12%)

### Lista de Value Bets
Sistema retorna **todas as apostas** que atendem:
1. market_odd ≥ fair_odd × 1.05
2. Odds válidas (> 0)

Ordenadas por:
- **value_pct** decrescente (maior value primeiro)

---

## 4. Recomendação Principal (Única)

### Prioridade de Seleção

#### 1ª Prioridade: BTTS ≥ 65%
```python
if btts_prob >= 0.65 and btts_odd > 0:
    return {
        'market': 'btts',
        'pick': 'Sim',
        'reason': 'BTTS com 61.67% acurácia histórica'
    }
```

#### 2ª Prioridade: Value Bet com Confiança ≥ 65%
```python
if value_bets and confidence >= 0.65 and best_value['prob'] >= 0.30:
    return {
        'market': best_value['market'],
        'pick': best_value['pick'],
        'reason': f'Value bet com {value_pct}% de edge'
    }
```

#### 3ª Prioridade: Resultado Mais Provável
```python
# Escolhe o máximo de 1X2 (Casa, Empate, Fora)
max_result = max([prob_home, prob_draw, prob_away])
return {
    'market': max_market,
    'pick': team_name,
    'reason': 'Resultado mais provável segundo modelos'
}
```

---

## 5. Fatores de Ajuste

### 5.1 Confiança (Confidence)
Calculada com base em:
- **Concordância entre modelos** (Poisson vs Logística)
- **Qualidade dos dados** (features disponíveis)
- **Histórico de performance** (accuracy recente)

Score: 0.0 a 1.0
- ≥ 0.8: Confiança ALTA (5 estrelas)
- 0.6 - 0.8: Confiança MÉDIA (3-4 estrelas)
- < 0.6: Confiança BAIXA (1-2 estrelas)

### 5.2 Risco (Risk Assessment)
Avaliado com base em:
- **Volatilidade do modelo** (consenso entre previsões)
- **Qualidade das odds** (spread do mercado)
- **Histórico dos times** (forma recente)

Níveis:
- **LOW**: Times estáveis, consenso alto → fator 1.2
- **MEDIUM**: Variação normal → fator 1.0
- **HIGH**: Alta incerteza, dados limitados → fator 0.7

---

## 6. Estrutura de Retorno

### make_decision() retorna:
```python
{
    'recommendation': {  # Recomendação única
        'market': 'btts',
        'market_display': 'Ambos Marcam',
        'pick': 'Sim',
        'probability': 0.67,
        'odd': 1.85,
        'reason': 'btts_priority',
        'reason_pt': 'BTTS com 67% probabilidade (histórico: 61.67% acurácia)'
    },
    
    'value_bets': [  # Lista de todas as value bets
        {
            'market': 'away_win',
            'market_display': 'Vitória Fora',
            'model_probability': 0.40,
            'fair_odd': 2.50,
            'market_odd': 2.80,
            'value_pct': 12.0,
            'edge': 0.12,
            'stake_suggestion': '2-3% do bankroll'
        },
        # ... mais value bets
    ],
    
    'top_bets': [  # Top 3 apostas (modo VALUE ou MULTIPLE)
        {
            'rank': 1,
            'market': 'away_win',
            'market_display': 'Vitória Fora',
            'pick': 'Tottenham',
            'probability': 0.406,
            'market_odd': 2.46,
            'fair_odd': 2.46,
            'ev_pct': 0.0,
            'stake_units': 1.0,
            'score': 0.85,
            'reason': 'Resultado mais provável com boa confiança'
        },
        # ... rank 2 e 3
    ],
    
    'confidence': {
        'score': 0.75,
        'level': 'MEDIUM',
        'stars': 4
    },
    
    'risk': 'medium',
    
    'strategy': 'value'  # ou 'multiple'
}
```

---

## 7. Comparação Rápida: VALUE vs MULTIPLE

| Critério | VALUE (Apostas Simples) | MULTIPLE (Bilhetes) |
|----------|-------------------------|---------------------|
| **Objetivo** | Maximizar EV | Maximizar probabilidade |
| **Fórmula Prob** | Linear (sem penalização) | ^1.5 (penaliza baixas) |
| **Fórmula EV** | Amplificado (÷30 positivo, ÷20 negativo) | Reduzido (÷200) |
| **Prob mínima** | 15% (muito permissivo) | 30% (conservador) |
| **EV mínimo** | Prioriza EV ≥ 0%, aceita -2% se necessário | Progressivo (ver tabela) |
| **Peso do EV** | DOMINANTE (3-5x amplificado) | REDUZIDO (metade do normal) |
| **EV +20%** | +67% impacto no score | +10% impacto no score |
| **EV -2%** | -10% impacto no score | -1% impacto no score |
| **Favoritos 85%, EV -2%** | score ≈ 0.78 | score ≈ 0.80 |
| **Underdog 50%, EV +23%** | score ≈ 0.92 ✅ VENCE | score ≈ 0.40 |
| **Uso ideal** | Value betting puro | Bilhetes seguros |

**DIFERENÇA CHAVE**: 
- **MODE VALUE**: EV **domina completamente**. Apostas com +20% EV superam favoritos 85% com EV -2%.
- **MODE MULTIPLE**: Probabilidade **domina**. Favoritos 85% superam underdogs 50% mesmo com EV +20%.

---

## 8. Exemplo Completo: Barça vs Real Madrid

### Previsões do Modelo
- **Casa (Barça)**: 42%
- **Empate**: 26%
- **Fora (Real)**: 32%
- **Over 2.5**: 58%
- **BTTS**: 67%

### Odds do Mercado
- Casa: 2.20
- Empate: 3.30
- Fora: 3.10
- Over 2.5: 1.75
- BTTS: 1.85

### Análise MODE VALUE

**Fair Odds**:
- Casa: 1/0.42 = 2.38
- Empate: 1/0.26 = 3.85
- Fora: 1/0.32 = 3.13
- Over 2.5: 1/0.58 = 1.72
- BTTS: 1/0.67 = 1.49

**Value Bets**:
1. **Empate**: 3.30 vs 3.85 → -14% (REJEITADO)
2. **BTTS**: 1.85 vs 1.49 → **+24% VALUE** ✅
3. **Fora**: 3.10 vs 3.13 → -1% (REJEITADO - não atinge 5%)
4. **Over 2.5**: 1.75 vs 1.72 → +2% (REJEITADO - não atinge 5%)

**Recomendação Principal**:
- ✅ **BTTS SIM** (prioridade 1: ≥65% prob)
- Probabilidade: 67%
- Odd: 1.85
- Razão: "BTTS com 67% probabilidade (histórico: 61.67% acurácia)"

**Top 3 Apostas VALUE** (ordenado por score):
1. **BTTS SIM** - Prob: 67%, EV: +24%, Score: 0.92
2. **Casa (Barça)** - Prob: 42%, EV: -8%, Score: 0.38
3. **Over 2.5** - Prob: 58%, EV: +2%, Score: 0.59

### Análise MODE MULTIPLE

**Filtro Progressivo**:
- **BTTS 67%**: Favorito forte (-10% OK) → EV +24% ✅ **ACEITO**
- **Over 2.5 58%**: Provável (-5% OK) → EV +2% ✅ **ACEITO**
- **Casa 42%**: Razoável (-3% OK) → EV -8% ❌ **REJEITADO**
- **Fora 32%**: Possível (0% mín) → EV -1% ❌ **REJEITADO**
- **Empate 26%**: < 30% ❌ **REJEITADO**

**Scores** (prob^1.5 × EV/200):
- BTTS: 0.67^1.5 × 1.12 = 0.61
- Over 2.5: 0.58^1.5 × 1.01 = 0.44

**Top 3 Apostas MULTIPLE**:
1. **BTTS SIM** - Prob: 67%, EV: +24%, Score: 0.61
2. **Over 2.5** - Prob: 58%, EV: +2%, Score: 0.44
3. *(Nenhuma outra aposta passa no filtro)*

---

## 9. Conclusão

### Quando usar VALUE
- Bankroll management com value betting
- Apostas individuais
- Aceita risco maior para EV superior
- Diversificação de apostas

### Quando usar MULTIPLE
- Bilhetes combinados (acumuladores)
- Precisa de alta probabilidade de acerto
- Aceita perda de value para mais segurança
- Apostas conservadoras

### Notas Importantes
1. Sistema **NUNCA** força 1X2 no top 3 - pode ter 3 apostas de mercados alternativos
2. Modo MULTIPLE rejeita **qualquer aposta < 30%** independente do EV
3. BTTS é **sempre priorizado** se ≥65% (melhor mercado histórico)
4. Value bets são **calculados igualmente** em ambos modos
5. Diferença está no **critério de seleção** e **fórmula de score**
