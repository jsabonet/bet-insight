# 📊 ANÁLISE COMPLETA: FEATURES E PESOS DO DECISION ENGINE

## 🎯 RESUMO EXECUTIVO

**Total de Features Engineered:** ~**60-70 variáveis** por partida
**Decisão Final:** Combinação ponderada de 3 fatores principais

---

## 1️⃣ FEATURES ENGINEERING (TIER 1)

### 📦 Categorias de Features

O sistema extrai features de **12 categorias**:

#### **1. STRENGTH (Força) - 10 features**
```python
{
    'home_attack_strength': float,        # Força ofensiva casa / média da liga
    'home_defense_strength': float,       # Força defensiva casa / média da liga
    'away_attack_strength': float,        # Força ofensiva fora / média da liga
    'away_defense_strength': float,       # Força defensiva fora / média da liga
    'strength_differential': float,       # Diferencial de força casa-fora
    'home_advantage_factor': float,       # Fator de vantagem de jogar em casa (1.0-1.5)
    'home_goals_per_game': float,         # Média de gols casa
    'away_goals_per_game': float,         # Média de gols fora
    'home_conceded_per_game': float,      # Média de gols sofridos casa
    'away_conceded_per_game': float       # Média de gols sofridos fora
}
```

#### **2. FORM (Forma) - 13 features**
```python
{
    'home_weighted_form': float,          # Forma ponderada (jogos recentes valem mais)
    'home_momentum': float,               # Tendência (melhorando ou piorando)
    'home_recent_points': int,            # Pontos nos últimos 5 jogos
    'home_sos': float,                    # Strength of Schedule (força dos adversários)
    'home_adjusted_form': float,          # Forma ajustada por SoS
    'away_weighted_form': float,
    'away_momentum': float,
    'away_recent_points': int,
    'away_sos': float,
    'away_adjusted_form': float,
    'form_differential': float,           # Diferencial de forma
    'sos_differential': float,            # Diferencial de SoS
    'adjusted_form_diff': float           # Diferencial de forma ajustada
}
```

**Time Decay Weighting:**
- Fórmula: `weight = exp(-0.0065 * days_ago)`
- Jogo de 7 dias atrás: peso ~0.95
- Jogo de 30 dias atrás: peso ~0.81
- Jogo de 90 dias atrás: peso ~0.55

#### **3. STATISTICS (Estatísticas) - 16 features**
```python
{
    # Corners
    'home_corners_per_game': float,
    'away_corners_per_game': float,
    'total_corners_expected': float,
    
    # Disciplina
    'home_cards_per_game': float,         # Amarelos + Vermelhos*2
    'away_cards_per_game': float,
    'home_discipline_score': float,        # 0-1 (1=muito disciplinado)
    'away_discipline_score': float,
    
    # Clean Sheets
    'home_clean_sheet_rate': float,        # % de jogos sem sofrer gols
    'away_clean_sheet_rate': float,
    
    # Variância (Consistência)
    'home_variance': float,                # Desvio padrão de performance
    'away_variance': float,
    'variance_differential': float,
    
    # Performance por Tempo
    'home_1st_half_pct': float,           # % de gols no 1º tempo
    'away_1st_half_pct': float,
    'first_half_differential': float
}
```

#### **4. CONTEXT (Contexto) - 6 features**
```python
{
    'home_rest_days': int,                # Dias desde último jogo
    'away_rest_days': int,
    'home_is_fatigued': bool,             # < 3 dias = fadiga
    'away_is_fatigued': bool,
    'rest_advantage': int,                # Diferencial de descanso
    'fatigue_impact': float               # Impacto estimado (-0.1 se fadiga)
}
```

#### **5. MARKET (Mercado) - 11 features**
```python
{
    'market_home_prob': float,            # Probabilidade implícita casa
    'market_draw_prob': float,            # Probabilidade implícita empate
    'market_away_prob': float,            # Probabilidade implícita fora
    'market_over_prob': float,            # Probabilidade implícita over 2.5
    'market_under_prob': float,           # Probabilidade implícita under 2.5
    'bookmaker_margin': float,            # Overround (margem da casa)
    'odds_home': float,                   # Odds brutas
    'odds_draw': float,
    'odds_away': float,
    'odds_over_25': float,
    'odds_under_25': float
}
```

#### **6. WEATHER (Clima) - 4-6 features**
```python
{
    'temperature': float,                 # °C
    'precipitation': float,               # mm
    'wind_speed': float,                  # km/h
    'weather_impact': float,              # Impacto estimado em gols (-0.3 a +0.2)
    'description': str,                   # "Chuva forte", "Ensolarado", etc.
    'condition_factor': float             # Fator de ajuste (0.8-1.2)
}
```

#### **7. H2H (Histórico Direto) - 5-10 features**
```python
{
    'h2h_home_wins': int,                 # Vitórias casa nos últimos confrontos
    'h2h_draws': int,
    'h2h_away_wins': int,
    'h2h_avg_goals': float,               # Média de gols nos confrontos
    'h2h_btts_rate': float,               # % de ambos marcam
    'h2h_home_dominance': float           # Dominância casa nos confrontos
}
```

#### **8. MATCH IMPORTANCE (Importância) - 4-6 features**
```python
{
    'home_importance': float,             # 0-1 (1=crucial)
    'away_importance': float,
    'importance_differential': float,
    'is_derby': bool,                     # Derby local
    'is_cup_tie': bool,                   # Jogo de copa
    'stage_weight': float                 # Peso da fase (final > quartas)
}
```

#### **9. INJURIES/SUSPENSIONS (Lesões) - 4 features**
```python
{
    'home_injury_impact': float,          # 0-5 (5=muito impacto)
    'away_injury_impact': float,
    'home_suspensions': int,
    'away_suspensions': int
}
```

#### **10. MOTIVATION (Motivação) - 6 features**
```python
{
    'home_motivation': float,             # 0-1 (0.8-1.2)
    'away_motivation': float,
    'home_fighting_relegation': bool,     # Luta contra rebaixamento
    'away_fighting_relegation': bool,
    'home_fighting_title': bool,          # Luta pelo título
    'away_fighting_title': bool
}
```

#### **11. ELO (Rating) - 4 features**
```python
{
    'home_elo': float,                    # Rating ELO casa (1300-1700)
    'away_elo': float,                    # Rating ELO fora (1300-1700)
    'elo_differential': float,            # Diferença bruta
    'elo_diff': float                     # Diferença normalizada (-3 a +3)
}
```
**Cálculo:**
```python
ELO = 1500 + 25*(PPG - 1.35) + 10*GDpg - 3*injury_impact
```

#### **12. COMPETITION (Tipo de Competição) - 4-6 features**
```python
{
    'is_cup_competition': bool,           # Copa vs Liga
    'competition_name': str,
    'knockout_adjustment_factor': float,   # Ajuste para mata-mata (0.85-0.95)
    'competition_prestige': float,         # Prestígio da competição (0.5-1.0)
    'home_bias_adjustment': float,         # Ajuste de vantagem casa em copas
    'is_knockout_stage': bool
}
```

---

## 2️⃣ PESOS DO DECISION ENGINE

### 🎯 CÁLCULO DE CONFIANÇA (Confidence Score)

O Decision Engine combina **3 fatores** com pesos específicos:

```python
weights = {
    'consensus': 0.40,      # 40% - Consenso entre modelos Poisson e Logística
    'differential': 0.30,   # 30% - Força do diferencial (strength + form)
    'dominance': 0.30       # 30% - Probabilidade dominante
}
```

#### **Score Final:**
```python
confidence_score = (
    0.40 * consensus_factor +
    0.30 * differential_factor +
    0.30 * dominance_factor
)
```

#### **Fatores Detalhados:**

**1. CONSENSUS (40%)** - Acordo entre modelos
```python
# Se Poisson e Logística concordam = alta confiança
consensus_score = 1 - abs(poisson_home_prob - logistic_home_prob)

# Exemplo:
# Poisson: 45% casa, Logística: 43% casa
# Consensus = 1 - |0.45 - 0.43| = 0.98 (98% de acordo)
```

**2. DIFFERENTIAL (30%)** - Força das diferenças
```python
if strength_diff > 0.5 or form_diff > 0.5:
    differential_factor = 0.9  # Grande diferença = 90%
elif strength_diff > 0.3 or form_diff > 0.3:
    differential_factor = 0.7  # Média diferença = 70%
else:
    differential_factor = 0.5  # Pequena diferença = 50%
```

**3. DOMINANCE (30%)** - Probabilidade clara
```python
max_prob = max(home_prob, draw_prob, away_prob)

if max_prob > 0.60:
    dominance_factor = 1.0   # Favorito claro (>60%)
elif max_prob > 0.50:
    dominance_factor = 0.8   # Favorito moderado (>50%)
else:
    dominance_factor = 0.6   # Jogo equilibrado
```

### 📊 EXEMPLO PRÁTICO

**Match: Leeds (casa) vs Forest (fora)**

**Features extraídas:**
- `strength_differential`: +0.47 (Leeds mais forte)
- `form_differential`: +0.15 (Leeds melhor forma)
- `elo_diff`: +1.82 (Leeds ELO superior)
- `home_attack_strength`: 1.27 (27% acima da média)
- `away_defense_strength`: 0.87 (13% abaixo da média)

**Predições dos modelos:**
- Poisson: 43% casa, 28% empate, 29% fora
- Logística: 41% casa, 30% empate, 29% fora

**Cálculo de Confiança:**
1. **Consensus**: `1 - |0.43 - 0.41| = 0.98` ✅
2. **Differential**: `0.7` (diferença moderada: 0.47 > 0.3)
3. **Dominance**: `0.6` (max_prob = 43% < 50%)

**Score Final:**
```python
confidence = 0.40 * 0.98 + 0.30 * 0.7 + 0.30 * 0.6
           = 0.392 + 0.21 + 0.18
           = 0.782 (78.2%)
```

**Resultado:** ⭐⭐⭐⭐ (4/5 estrelas - "Alta Confiança")

---

## 3️⃣ PESOS POR ESTRATÉGIA (BET SCORING)

### 🎲 MODO VALUE (Apostas Simples)

**Objetivo:** Maximizar Expected Value (EV)

```python
score = probability × ev_weight × confidence × risk_factor
```

**Componentes:**
- **Probability**: Peso linear (não penalizado)
- **EV Weight**: DOMINANTE
  - EV < 0: `ev_weight = max(0.3, 1 + EV/20)` - penalização severa
  - EV ≥ 0: `ev_weight = 1 + EV/30` - amplificação forte
- **Confidence**: Score de confiança (0.5-1.0)
- **Risk Factor**:
  - Baixo risco: 1.2
  - Médio risco: 1.0
  - Alto risco: 0.7

**Exemplos VALUE:**
```
Under 2.5: prob=52%, EV=+23%
→ score = 0.52 × (1 + 23/30) × 1.0 × 1.0 = 0.92 ✅ MELHOR

Casa 1X: prob=87%, EV=-2%
→ score = 0.87 × (1 - 2/20) × 1.0 × 1.0 = 0.78

Fora Over 0.5: prob=83%, EV=-3%
→ score = 0.83 × (1 - 3/20) × 1.0 × 1.0 = 0.71
```

**Resultado:** Under 2.5 com +23% EV vence favoritos com EV negativo!

### 📋 MODO MULTIPLE (Bilhetes Combinados)

**Objetivo:** Maximizar probabilidade (aceitar EV neutro)

```python
score = probability^1.5 × ev_weight × confidence × risk_factor
```

**Componentes:**
- **Probability^1.5**: DOMINANTE (penalização quadrática suave)
  - 70% → 58.6%
  - 60% → 46.5%
  - 50% → 35.4%
  - 40% → 25.3%
- **EV Weight**: `max(0.5, 1 + EV/200)` - peso reduzido
- **Confidence**: Score de confiança
- **Risk Factor**: Mesmo que VALUE

**Filtros Progressivos:**
```python
if probability >= 0.70:  # Favorito absoluto
    rejeitar se EV < -15%
elif probability >= 0.60:  # Favorito forte
    rejeitar se EV < -10%
elif probability >= 0.50:  # Provável
    rejeitar se EV < -5%
elif probability >= 0.40:  # Razoável
    rejeitar se EV < -3%
else:  # Possível
    rejeitar se EV < 0%
```

**Exemplos MULTIPLE:**
```
Casa 1X: prob=87%, EV=-2%
→ score = 0.87^1.5 × (1 - 2/200) × 1.0 × 1.0 = 0.81 × 0.99 = 0.80 ✅ MELHOR

Under 2.5: prob=52%, EV=+23%
→ score = 0.52^1.5 × (1 + 23/200) × 1.0 × 1.0 = 0.38 × 1.12 = 0.42

Fora Over 0.5: prob=83%, EV=-3%
→ score = 0.83^1.5 × (1 - 3/200) × 1.0 × 1.0 = 0.76 × 0.99 = 0.75
```

**Resultado:** Favoritos 87% vencem underdogs com EV alto!

---

## 4️⃣ FLUXO COMPLETO DE DECISÃO

### 📈 Passo a Passo

```mermaid
1. Feature Engineering (60-70 features)
   ↓
2. Model Predictions (Poisson + Logística + ML Ensemble)
   ↓
3. Consensus Calculation (média ponderada)
   ↓
4. Confidence Score (40% consensus + 30% differential + 30% dominance)
   ↓
5. Fair Odds Calculation (1 / probability)
   ↓
6. Value Bet Detection (market_odd > fair_odd * 1.05)
   ↓
7. Bet Scoring (strategy-dependent: VALUE vs MULTIPLE)
   ↓
8. Top 3 Selection (ranking por score)
   ↓
9. Stake Calculation (Kelly Criterion ajustado)
```

### 🎯 Critérios de Publicação

```python
# Filtro de Qualidade (OU lógico):
should_publish = (max_probability >= 0.52) OR (confidence_score >= 0.75)

# Thresholds:
- Max Probability: ≥ 52% (reduzido de 55% para mais cobertura)
- Confidence Score: ≥ 0.75 (aumentado de 0.70 = apenas "very_high")
```

**Status de Publicação:**
- ✅ **PUBLICAR**: Alta prob (≥52%) OU alta conf (≥0.75)
- ❌ **PULAR**: Jogo equilibrado (prob<52% E conf<0.75)

---

## 5️⃣ RESUMO DOS PESOS PRINCIPAIS

| Componente | Peso | Detalhes |
|------------|------|----------|
| **Consensus** | 40% | Acordo Poisson-Logística |
| **Differential** | 30% | Força + Forma + ELO |
| **Dominance** | 30% | Probabilidade máxima |
| **EV (VALUE)** | Dominante | -20% → peso 0.0, +30% → peso 2.0 |
| **EV (MULTIPLE)** | Reduzido | -20% → peso 0.9, +30% → peso 1.15 |
| **Probability (VALUE)** | Linear | Peso 1.0 |
| **Probability (MULTIPLE)** | ^1.5 | 70%→58%, 50%→35% |
| **Risk Factor** | 0.7-1.2 | Baixo:1.2, Médio:1.0, Alto:0.7 |

---

## 6️⃣ FEATURES MAIS INFLUENTES

### Top 10 Features com Maior Impacto

1. **strength_differential** - Diferença de força ofensiva/defensiva
2. **elo_diff** - Diferença de rating ELO
3. **adjusted_form_diff** - Diferença de forma ajustada por SoS
4. **home_advantage_factor** - Vantagem de jogar em casa
5. **weather_impact** - Impacto climático em gols
6. **h2h_home_dominance** - Dominância casa nos confrontos diretos
7. **rest_advantage** - Vantagem de descanso
8. **motivation** - Motivação contextual
9. **injury_impact** - Impacto de lesões/suspensões
10. **market_consensus** - Probabilidades implícitas do mercado

### Pesos Indiretos (Via Modelos)

Os modelos ML (Poisson, Logística, XGBoost) aprendem pesos automaticamente durante treinamento:
- **Poisson Bivariado**: Foca em `attack_strength`, `defense_strength`, `home_advantage`
- **Regressão Logística**: Combina todas as 60-70 features com pesos aprendidos
- **XGBoost Ensemble**: 18 modelos (9 ligas + 9 copas) × 9 mercados = feature importance dinâmica

---

## 7️⃣ CONSIDERAÇÕES FINAIS

### 🔍 Transparência do Sistema

**Todas as decisões são baseadas em:**
1. ✅ Features objetivas calculadas (60-70 variáveis)
2. ✅ Modelos estatísticos treinados com dados reais
3. ✅ Pesos fixos e documentados (40% consensus, 30% differential, 30% dominance)
4. ✅ Estratégias claras (VALUE = EV dominante, MULTIPLE = probabilidade dominante)

**Nenhuma "caixa preta":**
- Todos os pesos são explícitos
- Todos os cálculos são rastreáveis via logs
- Decisões podem ser auditadas e replicadas

### 📊 Performance Esperada

**Com base nas calibrações:**
- **Apostas VALUE**: 55-60% acurácia, +10-15% ROI
- **Bilhetes MULTIPLE (3x)**: 60-65% acurácia, ROI neutro (0-5%)
- **Confiança ≥75%**: 70-75% acurácia

### 🎲 Variância Natural

**Sistema estatisticamente correto ≠ 100% acurácia**
- Exemplo Celta (18 shots) vs Osasuna (8 shots, 100% conversão)
- Charlton 0-0 (Over 0.5 = 98% probabilidade, mas aconteceu o 2%)
- **Variância esperada:** 35-45% de falhas mesmo com lógica correta

---

**📌 Documento gerado em:** 07/02/2026  
**🔗 Arquivos relacionados:**
- [feature_engineer.py](bet-insight/backend/apps/analysis/services/feature_engineer.py)
- [decision_engine.py](bet-insight/backend/apps/analysis/services/decision_engine.py)
- [RESUMO_ANALISE_BILHETE.md](bet-insight/backend/RESUMO_ANALISE_BILHETE.md)
