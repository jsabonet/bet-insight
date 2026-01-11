# 🤖 COMO A IA RECEBE OS DADOS E DEFINE A MELHOR APOSTA

## 📋 FLUXO COMPLETO: DOS DADOS ATÉ A RECOMENDAÇÃO FINAL

```
┌──────────────────┐
│ 1. API-Football │ → Dados brutos (estatísticas, odds, clima)
└────────┬─────────┘
         ↓
┌────────────────────┐
│ 2. Match Enricher  │ → Enriquece dados, adiciona contexto
└────────┬───────────┘
         ↓
┌────────────────────┐
│ 3. Feature Engineer│ → Extrai 50+ features numéricas
└────────┬───────────┘
         ↓
┌────────────────────┐
│ 4. Model Ensemble  │ → Poisson (60%) + Logística (40%)
│    (Statistical)   │ → Gera probabilidades matemáticas
└────────┬───────────┘
         ↓
┌────────────────────┐
│ 5. Decision Engine │ → Calcula odds justas, identifica value bets
│    (Deterministic) │ → Define recomendação, confiança, risco
└────────┬───────────┘
         ↓
┌────────────────────┐
│ 6. AI Analyzer     │ → Google Gemini explica em português
│    (Explicação)    │ → Gera análise multi-mercado
└────────────────────┘
```

---

## 🎯 ETAPA 6: O QUE A IA RECEBE (Inputs)

**Arquivo**: `ai_analyzer.py` → método `explain_decision(decision_data, enriched_data)`

### A. `decision_data` (do Decision Engine)

```python
decision_data = {
    # RECOMENDAÇÃO PRINCIPAL
    'recommendation': {
        'market': 'away_win',           # Mercado escolhido
        'pick': 'Rayo Vallecano',       # Pick específico
        'probability': 0.364,           # 36.4% probabilidade
        'odd': 2.75,                    # Odd disponível no mercado
        'fair_odd': 2.75,               # Odd justa calculada
        'expected_value': 0.001,        # +0.1% EV (value bet?)
        'market_display': 'Vitória Fora'
    },
    
    # CONFIANÇA
    'confidence': {
        'level': 'medium',              # low/medium/high
        'stars': 3,                     # 1-5 estrelas
        'score': 0.62,                  # 0-1 score interno
        'explanation': 'Consenso entre modelos médio, dados completos'
    },
    
    # RISCO
    'risk': 'medium',                   # low/medium/high
    
    # PROBABILIDADES DOS MODELOS
    'model_probabilities': {
        'poisson': {
            'expected_goals_home': 1.15,
            'expected_goals_away': 1.25,
            'most_likely_score': '1-1',
            'probabilities': {
                'home_win': 0.329,
                'draw': 0.306,
                'away_win': 0.364,
                'over_2_5': 0.42,
                'under_2_5': 0.58,
                'btts': 0.51
            }
        },
        'consensus': {              # Consenso Poisson 60% + Logística 40%
            'home_win': 0.329,      # 32.9%
            'draw': 0.306,          # 30.6%
            'away_win': 0.364       # 36.4%
        }
    },
    
    # ODDS JUSTAS
    'fair_odds': {
        'home_win': 3.04,
        'draw': 3.27,
        'away_win': 2.75,
        'over_2_5': 2.38,
        'btts': 1.96
    },
    
    # VALUE BETS (apostas com valor)
    'value_bets': [
        {
            'market': 'away_win',
            'market_display': 'Vitória Fora',
            'fair_odd': 2.75,
            'market_odd': 2.75,
            'value': 0.001,         # +0.1% esperado
            'probability': 0.364
        }
    ]
}
```

### B. `enriched_data` (do Match Enricher)

```python
enriched_data = {
    # DADOS DA PARTIDA
    'fixture_details': {
        'teams': {
            'home': {'name': 'Mallorca', 'id': 532, 'logo': 'url'},
            'away': {'name': 'Rayo Vallecano', 'id': 728, 'logo': 'url'}
        },
        'league': {
            'name': 'La Liga',
            'country': 'Spain',
            'logo': 'url'
        },
        'fixture': {
            'date': '2026-01-12T15:00:00+00:00',
            'venue': 'Estadio de Son Moix'
        }
    },
    
    # CLASSIFICAÇÃO
    'table_context': {
        'home': {
            'position': 8,
            'points': 28,
            'games_played': 20,
            'goals_for': 25,
            'goals_against': 23,
            'goal_difference': 2,
            'form': 'LWDWL'
        },
        'away': {
            'position': 11,
            'points': 24,
            'games_played': 20,
            'goals_for': 22,
            'goals_against': 26,
            'goal_difference': -4,
            'form': 'DWLLW'
        }
    },
    
    # ESTATÍSTICAS DOS TIMES
    'home_stats': {...},
    'away_stats': {...},
    
    # ODDS DO MERCADO
    'odds': {
        'home_win': 2.20,
        'draw': 3.20,
        'away_win': 2.75,
        'over_2_5': 2.10,
        'btts': 1.80
    },
    
    # HEAD-TO-HEAD (últimos 5)
    'h2h': [...],
    
    # CLIMA
    'weather': {
        'temperature': 15,
        'condition': 'Clear',
        'wind_kph': 12,
        'weather_impact': 0.0
    }
}
```

---

## 🧠 O QUE A IA FAZ COM ESSES DADOS

### 1. **Extrai Informações-Chave** (`_build_prompt`)

```python
# Da decision_data
prob_home = 32.9%
prob_draw = 30.6%
prob_away = 36.4%
xg_home = 1.15
xg_away = 1.25
most_likely = "1-1"
confidence_stars = 3
risk = "MEDIUM"

# Da enriched_data
home_team = "Mallorca"
away_team = "Rayo Vallecano"
league = "La Liga"
match_date = "12/01/2026 15:00"
```

### 2. **Aplica Validações Estatísticas**

```python
total_xg = 1.15 + 1.25 = 2.40 gols
max_prob = max(32.9%, 30.6%, 36.4%) = 36.4%
is_balanced = 36.4% < 45%  # TRUE → Jogo equilibrado!
```

### 3. **Constrói Prompt Estruturado para Gemini**

```python
prompt = f"""Você é um sistema profissional de apostas esportivas.

🔢 DADOS FORNECIDOS (NÃO INVENTE OUTROS):
• Mallorca vs Rayo Vallecano
• Liga: La Liga
• Data: 12/01/2026 15:00
• Confiança: 3/5 • Risco: MEDIUM
• Probabilidades: Casa 32.9% | Empate 30.6% | Fora 36.4%
• xG esperado: 1.15 x 1.25
• Placar provável: 1-1
• Predição: Fora

⚠️ REGRAS OBRIGATÓRIAS:
1. NÃO invente dados históricos
2. SE xG < 0.5: NÃO recomende Over/Under, BTTS
3. SE jogo equilibrado (todas prob < 45%): PRIORIZE Dupla Chance
4. JUSTIFIQUE por que mercados foram descartados

🎯 ANÁLISE OBRIGATÓRIA DE MERCADOS:
• 1X2: Volatilidade ALTA (use se prob > 50%)
• Dupla Chance: Reduz risco, ideal para equilibrados
• Draw No Bet: Remove empate
• Over/Under: Use apenas se xG total > 2.0
• BTTS: Use apenas se ambos xG > 0.8

Gere análise com esta estrutura:
[formato completo com cabeçalho, comparação de mercados, 3 apostas]
"""
```

### 4. **Envia para Google Gemini 2.0 Flash**

```python
response = model.generate_content(
    prompt,
    generation_config={
        'temperature': 0,        # Deterministico (sem criatividade)
        'max_output_tokens': 2500,
        'top_p': 0.95,
        'top_k': 40,
    }
)
```

**Configuração explica**:
- `temperature=0`: Sem variação, sempre a mesma resposta para mesmos dados
- `max_tokens=2500`: ~600 palavras (suficiente para análise completa)
- `top_p=0.95`: Usa apenas 95% dos tokens mais prováveis (alta qualidade)

### 5. **IA Gera Análise em Português**

```python
# Gemini recebe o prompt e retorna:
output = """
🏆 Mallorca vs Rayo Vallecano
🏅 La Liga
📅 12/01/2026 15:00
⭐⭐⭐ Confiança: 3/5

🎯 PREDIÇÃO: Fora

📊 PROBABILIDADES:
🏠 Mallorca: 32.9%
🤝 Empate: 30.6%
✈️ Rayo Vallecano: 36.4%

═══════════════════════════════════════
🔍 COMPARAÇÃO DE MERCADOS
═══════════════════════════════════════

✅ Dupla Chance X2: Prob 67%, risco MÉDIO, cobre empate
✅ Draw No Bet Rayo: Prob 53.4%, risco MÉDIO
❌ 1X2 Fora: Prob 36.4%, risco ALTO, favorito indefinido
❌ Over 2.5: xG total 2.40 insuficiente
❌ BTTS: xG Mallorca baixo (1.15)

═══════════════════════════════════════
💰 APOSTAS RECOMENDADAS
═══════════════════════════════════════

🥇 APOSTA #1 - MAIOR VALOR
───────────────────────────────────────
📊 Mercado: Dupla Chance
🎯 Aposte em: X2 (Empate ou Rayo)
💵 Odd disponível: 1.60
📈 Odd justa: 1.49
✅ Vantagem: +7.4%
💰 Stake: 1.2 unidades
🎲 Risco real: MÉDIO

➡️ O QUE FAZER:
✓ Aposte AGORA se odd ≥ 1.49
✗ NÃO aposte se odd < 1.49

📝 PORQUÊ ESTE MERCADO?
• Jogo equilibrado (nenhuma prob > 45%)
• Dupla Chance reduz risco vs 1X2 simples
• Cobre 67% dos cenários (empate + vitória Rayo)
• xG total 2.40 baixo para mercados de gols

[... mais 2 apostas ...]
"""
```

---

## 🎯 POR QUE A IA NÃO "DECIDE"?

### ❌ O que a IA **NÃO** faz:
1. **NÃO calcula probabilidades** (feito por Poisson + Logística)
2. **NÃO escolhe mercados** (DecisionEngine identifica value bets)
3. **NÃO define confiança** (DecisionEngine calcula baseado em consenso)
4. **NÃO inventa dados** (regras no prompt proíbem)

### ✅ O que a IA **FAZ**:
1. **Explica** decisões já tomadas pelos modelos
2. **Compara** mercados com base nos dados fornecidos
3. **Justifica** por que alguns mercados foram eliminados
4. **Formata** saída em português de Moçambique profissional
5. **Adapta** linguagem ao nível de confiança/risco

---

## 📊 EXEMPLO PRÁTICO COMPLETO

### Input (O que IA recebe):
```
Mallorca vs Rayo Vallecano
Probabilidades: 32.9% | 30.6% | 36.4%
xG: 1.15 x 1.25
Confiança: 3/5
Risco: MEDIUM
Jogo equilibrado: TRUE (max prob 36.4% < 45%)
```

### Lógica da IA:
```
1. Detecta jogo equilibrado → PRIORIZA Dupla Chance
2. xG total 2.40 < 2.0? NÃO → Pode considerar Over/Under
3. xG Mallorca 1.15 > 0.8? SIM → BTTS é válido
4. Compara 5 mercados:
   - ✅ Dupla Chance X2: 67% prob, MÉDIO risco
   - ✅ Draw No Bet: 53.4% prob, MÉDIO risco
   - ❌ 1X2 Fora: 36.4% prob, ALTO risco
   - ⚠️ Over 2.5: xG marginal (2.40)
   - ❌ BTTS: xG Mallorca baixo
5. Ordena por valor esperado (EV%)
6. Gera 3 recomendações
```

### Output (O que usuário vê):
```
🥇 Dupla Chance X2 - EV +7.4%
🥈 Draw No Bet Rayo - EV +1.2%
🥉 1X2 Fora - EV +0.1% (alto risco)
```

---

## 🔒 GARANTIAS DE COERÊNCIA

### 1. **Validações no Prompt**
```python
if xg_home < 0.5 or xg_away < 0.5:
    prompt += "NÃO recomende mercados de gols"

if max_prob < 45:
    prompt += "PRIORIZE Dupla Chance ou Draw No Bet"
```

### 2. **Regras Críticas (Linha 404-413)**
```
🚫 VIOLAÇÃO = RESPOSTA INVÁLIDA:
1. NÃO invente histórico de confrontos
2. NÃO recomende Over 2.5 se xG < 2.0
3. NÃO recomende BTTS se qualquer xG < 0.8
4. NÃO escolha 1X2 em equilibrado sem justificar
5. SEMPRE compare >= 4 mercados
```

### 3. **Fallback Determinístico**
Se Gemini falhar ou violar regras → Sistema usa análise pré-formatada sem IA

---

## 📂 ARQUIVOS ENVOLVIDOS

1. **analysis_orchestrator.py** (linha 87-98)
   - Coordena todo o fluxo
   - Chama `ai.explain_decision(decision_data, enriched_data)`

2. **ai_analyzer.py** (linha 48-115)
   - `explain_decision()`: Recebe dados e chama Gemini
   - `_build_prompt()`: Constrói prompt estruturado
   - `_fallback_explanation()`: Backup sem IA

3. **decision_engine.py**
   - Gera `decision_data` com recomendação, confiança, risco

4. **statistical_models.py**
   - Gera `model_probabilities` com Poisson + Logística

---

## 🎯 RESUMO EXECUTIVO

| Etapa | Responsável | Output |
|-------|-------------|--------|
| **Coleta dados** | API-Football | Estatísticas brutas |
| **Enriquece** | MatchEnricher | Contexto completo |
| **Extrai features** | FeatureEngineer | 50+ variáveis numéricas |
| **Calcula probabilidades** | ModelEnsemble | Poisson + Logística → Consenso |
| **Define recomendação** | DecisionEngine | Mercado, odds justas, value bets |
| **Explica em português** | AIAnalyzer (Gemini) | Análise multi-mercado formatada |

**A IA é o ÚLTIMO passo** - apenas traduz decisões matemáticas em linguagem natural profissional.

---

**Última atualização**: 11/01/2026 21:10
