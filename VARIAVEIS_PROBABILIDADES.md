# 📊 VARIÁVEIS ANALISADAS PARA CÁLCULO DE PROBABILIDADES

## 🎯 SISTEMA HÍBRIDO DE PROBABILIDADES

O sistema usa **2 modelos estatísticos** que geram probabilidades independentes, depois combinadas por **consenso ponderado**:

```
┌─────────────────────────┐
│ MODELO POISSON (60%)    │ ──┐
└─────────────────────────┘   │
                              ├──► CONSENSO ──► Probabilidades Finais
┌─────────────────────────┐   │
│ MODELO LOGÍSTICO (40%)  │ ──┘
└─────────────────────────┘
```

---

## 🔢 1. MODELO POISSON BIVARIADO

**Arquivo**: `statistical_models.py` (linha 15-220)

### Entrada Principal:
- **home_strength** (float): Força ofensiva casa (gols/jogo médios)
- **away_strength** (float): Força ofensiva fora (gols/jogo médios)
- **weather_impact** (float): Ajuste climático (-0.5 a +0.5 gols)

### Parâmetros do Modelo:
- **HOME_ADVANTAGE** = 1.3 (casa marca ~30% mais gols)
- **RHO** = -0.13 (correlação Dixon-Coles para baixos placares)

### Cálculo:
1. **λ_home** = home_strength × 1.3 + weather_impact
2. **λ_away** = away_strength + weather_impact
3. Distribui probabilidades em matriz 7×7 (0-6 gols cada time)
4. Aplica **correção Dixon-Coles** para placares 0-0, 0-1, 1-0, 1-1
5. Normaliza para somar 100%

### Saída:
```python
{
  'expected_goals': {'home': 2.1, 'away': 1.4},
  'most_likely_score': '2-1',
  'probabilities': {
    'home_win': 0.52,    # 52% vitória casa
    'draw': 0.28,        # 28% empate
    'away_win': 0.20,    # 20% vitória fora
    'over_2_5': 0.61,
    'under_2_5': 0.39,
    'btts': 0.58,
    'home_clean_sheet': 0.25,
    'away_clean_sheet': 0.18
  },
  'score_distribution': [
    {'score': '2-1', 'probability': 0.18},
    {'score': '1-0', 'probability': 0.14},
    ...
  ]
}
```

---

## 📈 2. MODELO LOGÍSTICO (Regressão)

**Arquivo**: `statistical_models.py` (linha 221-360)

### Features Utilizadas (40+ variáveis):

#### A. FORÇA OFENSIVA/DEFENSIVA (3 vars)
- `home_offensive_strength`: Gols/jogo casa vs média da liga
- `away_offensive_strength`: Gols/jogo fora vs média da liga
- `defensive_delta`: (Defesa casa - Defesa fora) normalizado

#### B. FORMA RECENTE (3 vars)
- `home_weighted_form`: Últimos 5 jogos com peso temporal
- `away_weighted_form`: Últimos 5 jogos com peso temporal
- `form_delta`: Diferença de forma

#### C. ESTATÍSTICAS AVANÇADAS (8 vars)
- `corners_per_game_delta`: Diferença de escanteios
- `cards_per_game_delta`: Diferença de cartões
- `shots_on_target_ratio`: Finalizações no alvo
- `possession_avg_delta`: Diferença de posse de bola
- `pass_accuracy_delta`: Precisão de passes
- `home_goals_temporal_pattern`: Padrão de gols (1H vs 2H)
- `away_goals_temporal_pattern`
- `form_variance_delta`: Consistência de resultados

#### D. CONTEXTO (2 vars)
- `rest_days_delta`: Diferença de descanso (fadiga)
- `fatigue_index_delta`: Índice de fadiga (jogos/14 dias)

#### E. MERCADO (3 vars)
- `market_home_prob`: Probabilidade implícita nas odds casa
- `market_draw_prob`: Probabilidade implícita empate
- `market_away_prob`: Probabilidade implícita fora

#### F. CLIMA (1 var)
- `weather_impact`: -0.5 a +0.5 gols (chuva/vento reduz gols)

#### G. HEAD-TO-HEAD (4 vars)
- `h2h_home_win_rate`: Taxa de vitórias casa nos últimos confrontos
- `h2h_btts_rate`: Taxa de ambas marcam
- `h2h_avg_goals`: Média de gols totais
- `h2h_recent_trend`: Tendência últimos 3 H2H

#### H. IMPORTÂNCIA DO JOGO (3 vars)
- `match_importance_home`: 0-1 (título, Champions, rebaixamento)
- `match_importance_away`: 0-1
- `importance_delta`: Diferença de motivação

#### I. LESÕES/SUSPENSÕES (2 vars)
- `home_key_players_missing`: % jogadores importantes ausentes
- `away_key_players_missing`: % jogadores importantes ausentes

#### J. MOTIVAÇÃO (3 vars)
- `home_motivation_index`: Luta por título/Europa/sobrevivência
- `away_motivation_index`
- `motivation_delta`: Diferença

### Cálculo:
1. Normaliza todas features para escala 0-1
2. Aplica **regressão logística** multinomial (3 classes: H/D/A)
3. Usa **softmax** para converter em probabilidades

### Saída:
```python
{
  'home_win': 0.48,
  'draw': 0.31,
  'away_win': 0.21
}
```

---

## ⚖️ 3. CONSENSO (ENSEMBLE)

**Arquivo**: `statistical_models.py` (linha 431-470)

### Pesos:
- **Poisson**: 60% (mais confiável para mercados de gols)
- **Logística**: 40% (captura fatores contextuais)

### Cálculo:
```python
consensus = {
  'home_win': poisson_home × 0.6 + logistic_home × 0.4,
  'draw': poisson_draw × 0.6 + logistic_draw × 0.4,
  'away_win': poisson_away × 0.6 + logistic_away × 0.4
}
```

### Exemplo Real:
```
Poisson:    Casa 52% | Empate 28% | Fora 20%
Logística:  Casa 48% | Empate 31% | Fora 21%
─────────────────────────────────────────────
CONSENSO:   Casa 50.4% | Empate 29.2% | Fora 20.4%
```

---

## 📥 ORIGEM DOS DADOS (API-Football)

### 1. Classificação da Liga (`/standings`)
```json
{
  "position": 2,
  "points": 45,
  "goals_for": 58,
  "goals_against": 22,
  "games_played": 20,
  "goal_difference": 36,
  "form": "WWDWW"
}
```

### 2. Estatísticas do Time (`/teams/statistics`)
```json
{
  "goals": {"for": {"total": 58, "average": "2.9"}},
  "lineups": [{"formation": "4-3-3", "played": 15}],
  "cards": {"yellow": 35, "red": 2},
  "fixtures": {"wins": {"total": 14}}
}
```

### 3. Odds (`/odds`)
```json
{
  "bookmakers": [{
    "bets": [{
      "name": "Match Winner",
      "values": [
        {"value": "Home", "odd": "1.85"},
        {"value": "Draw", "odd": "3.40"},
        {"value": "Away", "odd": "4.20"}
      ]
    }]
  }]
}
```

### 4. Confrontos Diretos (`/fixtures/headtohead`)
```json
[
  {
    "fixture": {"date": "2025-09-15"},
    "goals": {"home": 2, "away": 1},
    "score": {"fulltime": {"home": 2, "away": 1}}
  }
]
```

### 5. Clima (WeatherAPI)
```json
{
  "condition": {"text": "Moderate rain"},
  "temp_c": 8,
  "wind_kph": 25,
  "precip_mm": 5.2
}
```

---

## 🧮 EXEMPLO COMPLETO: Barcelona vs Real Madrid

### Entrada:
```python
# Poisson
home_strength = 2.8  # Barça marca 2.8 gols/jogo em casa
away_strength = 2.3  # Real marca 2.3 gols/jogo fora
weather_impact = 0.0

# Logística (40 features)
features = {
  'home_offensive_strength': 1.23,  # 23% acima da média
  'away_offensive_strength': 1.15,
  'defensive_delta': 0.08,
  'home_weighted_form': 0.82,       # 82% dos pontos
  'away_weighted_form': 0.78,
  'market_home_prob': 0.48,         # Odds 2.08
  'match_importance_home': 0.9,     # Jogo crucial
  'h2h_btts_rate': 0.75,            # 75% ambas marcam
  ...
}
```

### Saída Poisson:
```
λ_home = 2.8 × 1.3 = 3.64 gols
λ_away = 2.3 gols

Probabilidades:
- Casa: 58%
- Empate: 22%
- Fora: 20%
- Over 2.5: 78%
- BTTS: 72%
```

### Saída Logística:
```
Probabilidades:
- Casa: 52%
- Empate: 26%
- Fora: 22%
```

### Consenso Final:
```
Casa:   58% × 0.6 + 52% × 0.4 = 55.6%
Empate: 22% × 0.6 + 26% × 0.4 = 23.6%
Fora:   20% × 0.6 + 22% × 0.4 = 20.8%
```

---

## 🎯 CONFIANÇA DA PREVISÃO

**Arquivo**: `decision_engine.py` (linha 180-250)

### Fatores Considerados:

1. **Consenso entre modelos** (0-1)
   - Se Poisson e Logística concordam → +confiança
   - Exemplo: Ambos dão 55% casa → score 0.95

2. **Qualidade dos dados** (0-1)
   - Tem classificação? +0.2
   - Tem estatísticas? +0.2
   - Tem H2H? +0.2
   - Tem odds? +0.2
   - Tem forma recente? +0.2

3. **Força das features** (0-1)
   - Diferença clara de força? +confiança
   - Forma consistente? +confiança
   - Diferença de motivação? +confiança

### Conversão para Estrelas:
```python
if confidence_score >= 0.85: stars = 5  # ⭐⭐⭐⭐⭐
elif confidence_score >= 0.70: stars = 4  # ⭐⭐⭐⭐
elif confidence_score >= 0.55: stars = 3  # ⭐⭐⭐
elif confidence_score >= 0.40: stars = 2  # ⭐⭐
else: stars = 1                           # ⭐
```

---

## 🔍 RESUMO EXECUTIVO

### Variáveis Analisadas (Total: 50+)

| Categoria | Variáveis | Peso no Modelo |
|-----------|-----------|----------------|
| **Força ofensiva/defensiva** | Gols/jogo normalizado | 🟢🟢🟢 Alta |
| **Forma recente** | Últimos 5 jogos ponderados | 🟢🟢🟢 Alta |
| **xG esperado** | Lambda Poisson ajustado | 🟢🟢🟢 Alta |
| **Home advantage** | +30% gols casa | 🟢🟢 Média |
| **Estatísticas avançadas** | Corners, cartões, posse | 🟢 Baixa |
| **Contexto** | Fadiga, descanso | 🟢 Baixa |
| **Mercado** | Odds implícitas | 🟢🟢 Média |
| **Clima** | Impacto -0.5/+0.5 gols | 🟡 Condicional |
| **H2H** | Últimos 5 confrontos | 🟢 Baixa |
| **Motivação** | Importância do jogo | 🟢🟢 Média |
| **Lesões** | Jogadores-chave ausentes | 🟢 Baixa |

### O que **NÃO** é analisado:
❌ Confronto direto histórico completo (apenas últimos 5)
❌ Forma recente de jogadores individuais
❌ Sentimento de torcida/redes sociais
❌ Histórico de treinadores
❌ Detalhes táticos (formações são usadas apenas parcialmente)

---

## 📖 Arquivos Relevantes

1. **feature_engineer.py** (1061 linhas) - Extrai 40+ features
2. **statistical_models.py** (470 linhas) - Poisson + Logística + Ensemble
3. **decision_engine.py** (250 linhas) - Cálculo de confiança e decisão
4. **match_enricher.py** - Coleta dados da API-Football
5. **analysis_orchestrator.py** - Coordena todo o fluxo

---

**Última atualização**: 11/01/2026 20:45
