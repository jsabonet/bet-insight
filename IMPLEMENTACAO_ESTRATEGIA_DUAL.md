# 🎯 Implementação: Sistema de Estratégia Dual (Value vs Multiple)

**Data:** 19 Janeiro 2026  
**Status:** ✅ Completamente Implementado e Corrigido
**Prioridade:** Alta  

---

## ⚙️ CORREÇÃO CRÍTICA APLICADA (19/01/2026)

### 🐛 Problema Reportado
**"As recomendações para análises simples e bilhetes não estão diferenciando"**

### 🔍 Causa Raiz
1. **Backend forçava sempre o 1X2 mais provável como #1** - Mesmo no modo MULTIPLE
2. **Falta de diferenciação visual** - Modal não indicava qual estratégia estava ativa
3. **Logs insuficientes** - Difícil diagnosticar qual lógica estava sendo aplicada

### ✅ Correções Implementadas

#### 1. Backend - `decision_engine.py` (Lógica de Seleção)
**Antes:**
```python
# SEMPRE forçava 1X2 mais provável como #1
best_1x2 = max(only_1x2, key=lambda x: x['probability'])
selected.append(best_1x2)  # #1 fixo
```

**Depois:**
```python
if strategy == 'value':
    # #1 = 1X2 mais provável (mantém lógica original)
    best_1x2 = max(only_1x2, key=lambda x: x['probability'])
    selected.append(best_1x2)
    others = [c for c in valid_candidates if c != best_1x2]
    
else:  # multiple
    # Top 3 por score PURO (prob² domina), SEM forçar 1X2
    others = sorted(valid_candidates, key=lambda x: x['score'], reverse=True)
    # #1 pode ser Over 2.5, BTTS, ou qualquer mercado com prob ≥ 50%
```

**Impacto:**
- **VALUE**: Mantém #1 = resultado mais provável (ex: Casa 45%) + value bets
- **MULTIPLE**: Ranking puro por score - pode ter Over 2.5 65% como #1

#### 2. Frontend - `AnalysisModal.jsx` (Interface)
**Adicionado:**
- 📋 Badge "Análise para Bilhetes" (modo MULTIPLE)
- ⚡ Badge "Análise Simples (Value)" (modo VALUE)
- Formatação de probabilidades: `76.14974842268292%` → `76.1%`
- Removidas seções técnicas (odds justas, market odds, value bets)

#### 3. Logs Melhorados
```
📊 SELECT_TOP_BETS - Estratégia: MULTIPLE
   🎯 Modo: BILHETES (prob ≥ 50%, EV ≥ 0%)
   Top 5 candidatos por score:
      1. Over 2.5 - Prob: 65.2%, EV: +2.1%, Score: 0.437
      2. Vitória Casa - Prob: 70.3%, EV: -1.2%, Score: 0.489
      3. BTTS - Prob: 55.8%, EV: +0.5%, Score: 0.313
```

### 🎯 Resultado Final

**Modo VALUE (Apostas Simples):**
- #1: **SEMPRE** resultado 1X2 mais provável
- #2 e #3: Melhores value bets por score
- Aceita qualquer probabilidade (30-90%)
- Fórmula: `score = prob × (1 + EV/100) × conf × risk`

**Modo MULTIPLE (Para Bilhetes):**
- #1, #2, #3: Top 3 por score (prob² domina)
- **NÃO** força 1X2 como #1
- Filtro progressivo por probabilidade:
  - Prob ≥ 70%: aceita até EV **-15%** (favoritos absolutos)
  - Prob ≥ 60%: aceita até EV **-10%**
  - Prob ≥ 50%: aceita até EV **-5%**
- Fórmula: `score = prob² × (1 + EV/200) × conf × risk`

**Exemplo Real:**
- VALUE: #1 = Empate 35% (mais provável) + Value bets com EV positivo
- MULTIPLE: #1 = Casa 76% (EV -12%, aceito), #2 = Over 2.5 60%, #3 = Casa -1.5 55%

#### 4. Fluxo de Aplicação da Estratégia

**IMPORTANTE:** A estratégia é aplicada APENAS no `quick_analyze` (botão "Ver Análise"):

```
1. statistical_preview (carregamento inicial da página)
   ↓
   Strategy: 'value' (fixo, dados neutros)
   Retorna: Probabilidades, odds, features (SEM aplicar filtros de estratégia)

2. quick_analyze (quando clica "Ver Análise")
   ↓
   Strategy: Do contexto global (value ou multiple)
   Aplica: Filtros e lógica específica da estratégia escolhida
   Retorna: Análise da IA + top_bets filtrados pela estratégia
```

**Motivo:** O preview estatístico é neutro e rápido. A estratégia só é aplicada quando o usuário solicita análise completa com IA

---

## ⚠️ ARQUITETURA CORRETA IMPLEMENTADA

### ❌ Problema da Implementação Anterior
- Toggle na página de detalhes (usuário só via depois de clicar)
- Descartava botão "Ver Análise" dos cards
- UX confusa (repetitivo, não intuitivo)

### ✅ Solução Implementada (Estratégia Global)
```
┌─────────────────────────────────────┐
│  HEADER (TOPO)                      │
│  [⚡ Simples] [📋 Bilhete] ← TOGGLE │  ← Escolha GLOBAL
└─────────────────────────────────────┘
           ↓ (persiste em localStorage)
┌─────────────────────────────────────┐
│  CARDS DE PARTIDAS                  │
│  [Ver Análise] ← usa estratégia     │  ← Mantém navegação
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│  PÁGINA DETALHES                    │
│  (carrega com estratégia correta)   │  ← Sem toggle redundante
└─────────────────────────────────────┘
```

### 🎯 Benefícios
- ✅ Usuário escolhe UMA vez (persiste em todas páginas)
- ✅ Mantém botão dos cards intacto
- ✅ UX limpa e intuitiva
- ✅ Salva preferência (localStorage)

---

## 📖 Contexto e Motivação

### Problema Identificado
O sistema atual recomenda apostas com **EV máximo** (value betting), mas isso resulta em:
- Apostas com **30-40% probabilidade** (menos prováveis)
- **Usuários confusos**: "Por que apostar no time ruim?"
- **Incompatível com bilhetes múltiplos**: Probabilidade combinada muito baixa (4-10%)

### Solução Proposta
**Sistema Dual com duas estratégias:**

| Estratégia | Objetivo | Probabilidade | EV | Taxa Acerto | ROI | Uso |
|------------|----------|---------------|----|-----------|----|-----|
| **⚡ Value Betting** | Maximizar EV | 30-45% | +15-25% | 35-45% | +20-25% | Apostas simples |
| **📋 Multiple Safe** | Alta prob + EV não-negativo | 50-70% | 0-10% | 50-65% | +5-15% | Bilhetes múltiplos |

### Matemática
```
APOSTA SIMPLES (Value):
- 100 apostas × 10€
- Taxa acerto: 35%
- Odd média: 3.50
- Retorno: 35 × 3.50 × 10 = 1.225€
- Lucro: +225€ (+22.5%)

BILHETE 3x (Safe):
- Prob individual: 60% cada
- Prob combinada: 0.6³ = 21.6%
- Odd total: 5.20
- 10 bilhetes × 10€ = 100€
- Acertos: 2-3 bilhetes
- Retorno: 2.5 × 52€ = 130€
- Lucro: +30€ (+30%) mas menor consistência
```

---

## 🏗️ Arquitetura da Implementação

### Componentes Afetados

```
backend/
├── apps/analysis/
│   ├── services/
│   │   ├── decision_engine.py          ← MODIFICAR (strategy param)
│   │   ├── daily_curator.py            ← CRIAR (curadoria jogos do dia)
│   │   └── ai_analyzer.py              ← MODIFICAR (prompt por strategy)
│   └── views.py                        ← MODIFICAR (endpoint daily-picks)

frontend/
├── pages/
│   ├── DailyPicks.tsx                  ← CRIAR (página apostas do dia)
│   └── MatchDetail.tsx                 ← MODIFICAR (toggle strategy)
├── components/
│   ├── EducationalBanner.tsx           ← CRIAR
│   ├── BetCard.tsx                     ← CRIAR
│   ├── SuggestedParlays.tsx            ← CRIAR
│   └── StrategyToggle.tsx              ← CRIAR
```

---

## 📋 Plano de Implementação (3 Fases)

### **FASE 1: Backend Core** ✅ COMPLETO
Status: ✅ Implementado

#### 1.1 ✅ Modificar `decision_engine.py`
- ✅ `make_decision()` aceita `strategy='value'`
- ✅ `_calculate_bet_score()` com lógica dual (value vs multiple)
- ✅ `select_top_bets()` passa strategy através da cadeia
- ✅ 6 chamadas atualizadas via PowerShell

#### 1.2 ✅ Modificar `views.py`
- ✅ `statistical_preview` extrai strategy de request.data
- ✅ Validação (fallback para 'value')
- ✅ Passa strategy para DecisionEngine
- ✅ Logs configurados

#### 1.3 ✅ Modificar `ai_analyzer.py`
- ✅ `explain_decision()` aceita strategy param
- ✅ `_build_prompt()` adapta prompt por estratégia
- ✅ Cache inclui strategy na chave
- ✅ Prompts diferentes: VALUE (EV focus) vs MULTIPLE (prob focus)

#### 1.4 🔧 Ajuste de Filtros (19/01/2026)
**Problema:** Filtro MULTIPLE muito restritivo (EV ≥ +5%)
- ❌ Favoritos com 76% prob não qualificavam
- ❌ Impossível usar em bilhetes

**Solução:** Relaxar filtro para EV ≥ 0%
- ✅ Aceita favoritos com odds justas (EV próximo de 0%)
- ✅ Mantém filtro de prob ≥ 50%
- ✅ Favoritos absolutos (70%+) agora qualificam
- ✅ Exemplo: Inter 76% com odd 1.30 → OK para bilhete

---

### **FASE 2: Frontend Base** ✅ COMPLETO
Status: ✅ Implementado (Arquitetura Global)

#### 2.1 ✅ Criar Context React Global
**Arquivo:** `frontend/src/context/StrategyContext.jsx`
```javascript
- ✅ StrategyProvider com localStorage
- ✅ useStrategy() hook
- ✅ Persiste escolha do usuário
- ✅ Helpers: isValue, isMultiple
```

#### 2.2 ✅ Criar StrategySelector para Header
**Arquivo:** `frontend/src/components/StrategySelector.jsx`
```javascript
- ✅ Toggle com 2 botões (⚡ Simples | 📋 Bilhete)
- ✅ Design com gradientes (amarelo-laranja | azul-roxo)
- ✅ Responsivo (oculta texto em mobile)
- ✅ Animações suaves
```

#### 2.3 ✅ Integrar Provider no App
**Arquivo:** `frontend/src/App.jsx`
```javascript
- ✅ Import StrategyProvider
- ✅ Wraps Routes com <StrategyProvider>
- ✅ Disponível em toda aplicação
```

#### 2.4 ✅ Modificar Header
**Arquivo:** `frontend/src/components/Header.jsx`
```javascript
- ✅ Import StrategySelector
- ✅ Adicionado entre DailyLimitIndicator e Title
- ✅ Visível em todas páginas
```

#### 2.5 ✅ Atualizar MatchDetailPage
**Arquivo:** `frontend/src/pages/MatchDetailPage.jsx`
```javascript
- ✅ Import useStrategy() do context
- ✅ REMOVIDO useState local de strategy
- ✅ REMOVIDO <StrategyToggle> da página
- ✅ Usa const { strategy } = useStrategy()
- ✅ loadStatisticalData usa strategy global
- ✅ Payload API inclui strategy
```

---

### **FASE 3: Features Avançadas** ⏳ PENDENTE
Status: ⏳ Planejado

#### 3.1 ⏳ Daily Curator (`daily_curator.py`)
- ⏳ Análise automática de jogos do dia
- ⏳ Top 10 Value + Top 10 Multiple
- ⏳ Bilhetes sugeridos (3-4x)

#### 3.2 ⏳ Página Daily Picks
- ⏳ Duas colunas (Value | Multiple)
- ⏳ Filtros (data, liga, confiança)
- ⏳ Cards diferenciados por estratégia

#### 3.3 ⏳ AI Analyzer Adaptation
- ⏳ Prompt muda por estratégia
- ⏳ Explicações adaptadas

---

#### 1.1 Modificar `decision_engine.py`

**Método `make_decision()`**
```python
def make_decision(self, fixture_id, predictions, probabilities, 
                  market_odds, strategy='value'):
    """
    Args:
        strategy (str): 'value' ou 'multiple'
    """
    # ... código existente ...
    
    top_bets = self.select_top_bets(
        predictions, probabilities, market_odds, 
        strategy=strategy  # ← NOVO
    )
    
    return {
        'top_bets': top_bets,
        'strategy': strategy,  # ← NOVO
        # ... resto ...
    }
```

**Método `_calculate_bet_score()` - DUAL**
```python
def _calculate_bet_score(self, prob, ev_pct, confidence, risk_level, 
                         strategy='value'):
    """
    Score adaptado por estratégia:
    - value: prob × (1 + EV/100) × conf × risk
    - multiple: prob² × (1 + EV/200) × conf × risk
    """
    conf_factor = confidence.get('score', 0.5)
    risk_factor = {'low': 1.2, 'medium': 1.0, 'high': 0.7}[risk_level]
    
    if strategy == 'multiple':
        # MODO BILHETE: Prioriza MUITO mais probabilidade
        prob_weight = prob ** 2  # Quadrático (65%→42%, 30%→9%)
        ev_weight = max(0.5, 1 + (ev_pct / 200))  # EV com metade do peso
        
        # FILTRO RIGOROSO: Só retorna se atende critérios
        if prob < 0.50 or ev_pct < 5:
            return 0  # Não qualifica para bilhete
    else:
        # MODO VALUE: Código atual
        prob_weight = prob
        ev_weight = max(0.5, 1 + (ev_pct / 100))
    
    score = prob_weight * ev_weight * conf_factor * risk_factor
    return round(score, 3)
```

**Método `select_top_bets()` - Adicionar filtro**
```python
def select_top_bets(self, predictions, probabilities, market_odds, 
                    confidence, risk, strategy='value'):
    """
    Seleciona top 3 apostas baseado na estratégia.
    """
    # ... gerar candidatos (código existente) ...
    
    # Calcular score de cada candidato
    for candidate in candidates:
        score = self._calculate_bet_score(
            candidate['probability'],
            candidate['ev_pct'],
            confidence,
            risk,
            strategy=strategy  # ← NOVO
        )
        candidate['score'] = score
    
    # FILTRO por estratégia
    if strategy == 'multiple':
        # Remover apostas que não atendem critérios de bilhete
        candidates = [c for c in candidates if c['score'] > 0]
        logger.info(f"Modo BILHETE: {len(candidates)} apostas qualificadas")
    
    # Ordenar por score
    candidates.sort(key=lambda x: x['score'], reverse=True)
    
    # Regra #1: SEMPRE resultado mais provável 1X2 (se strategy=value)
    if strategy == 'value':
        best_1x2 = max([c for c in candidates if c['category']=='1x2'], 
                       key=lambda x: x['probability'])
        # ... lógica existente ...
    else:
        # Modo bilhete: pega top 3 por score (sem forçar 1X2)
        return candidates[:3]
```

#### 1.2 Modificar `views.py`

**Endpoint `statistical_preview`**
```python
def statistical_preview(request, fixture_id):
    """Adicionar suporte a strategy query param"""
    strategy = request.GET.get('strategy', 'value')  # ← NOVO
    
    # Validação
    if strategy not in ['value', 'multiple']:
        return JsonResponse({'error': 'Invalid strategy'}, status=400)
    
    # ... código existente de análise ...
    
    # Passar strategy para DecisionEngine
    decision = DecisionEngine.make_decision(
        fixture_id=fixture_id,
        predictions=predictions,
        probabilities=probabilities,
        market_odds=market_odds,
        strategy=strategy  # ← NOVO
    )
    
    return JsonResponse({
        'strategy': strategy,  # ← NOVO
        'top_bets': decision['top_bets'],
        # ... resto ...
    })
```

#### 1.3 Criar `daily_curator.py`

**Novo serviço de curadoria**
```python
"""
apps/analysis/services/daily_curator.py
Curadoria inteligente de apostas do dia
"""
import logging
from datetime import datetime, timedelta
from django.core.cache import cache
from .decision_engine import DecisionEngine
from .api_football_service import APIFootballService

logger = logging.getLogger(__name__)

class DailyCurator:
    """
    Analisa todos os jogos do dia e seleciona:
    - Top 10 apostas Value Betting
    - Top 10 apostas para Bilhetes
    - 2-3 bilhetes sugeridos
    """
    
    def __init__(self):
        self.decision_engine = DecisionEngine()
        self.api_service = APIFootballService()
    
    def get_daily_picks(self, date=None, leagues=None, min_confidence=70):
        """
        Retorna curadoria do dia.
        
        Args:
            date (str): YYYY-MM-DD (default: hoje)
            leagues (list): IDs de ligas ou None (todas)
            min_confidence (int): 0-100 (default: 70)
        
        Returns:
            {
                'date': '2026-01-19',
                'total_matches': 12,
                'value_bets': [...],      # Top 10 value
                'safe_bets': [...],       # Top 10 bilhetes
                'suggested_parlays': [...]  # 2-3 bilhetes prontos
            }
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Cache key
        cache_key = f'daily_picks_{date}_{leagues}_{min_confidence}'
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Cache HIT: {cache_key}")
            return cached
        
        logger.info(f"Curando apostas para {date}...")
        
        # 1. Buscar fixtures do dia
        fixtures = self._get_fixtures_by_date(date, leagues)
        logger.info(f"Encontrados {len(fixtures)} jogos")
        
        # 2. Analisar cada fixture (ambas estratégias)
        all_value_bets = []
        all_safe_bets = []
        
        for fixture in fixtures:
            try:
                # Análise VALUE
                value_analysis = self._analyze_fixture(
                    fixture['id'], 
                    strategy='value'
                )
                
                # Análise MULTIPLE
                safe_analysis = self._analyze_fixture(
                    fixture['id'],
                    strategy='multiple'
                )
                
                # Filtrar por confiança
                for bet in value_analysis['top_bets']:
                    if bet.get('confidence', 0) >= min_confidence:
                        bet['fixture'] = fixture
                        all_value_bets.append(bet)
                
                for bet in safe_analysis['top_bets']:
                    if bet.get('confidence', 0) >= min_confidence:
                        bet['fixture'] = fixture
                        all_safe_bets.append(bet)
                
            except Exception as e:
                logger.error(f"Erro ao analisar fixture {fixture['id']}: {e}")
                continue
        
        # 3. Ranquear globalmente
        top_value = sorted(all_value_bets, key=lambda x: x['score'], reverse=True)[:10]
        top_safe = sorted(all_safe_bets, key=lambda x: x['score'], reverse=True)[:10]
        
        # 4. Gerar bilhetes sugeridos
        parlays = self._suggest_parlays(top_safe)
        
        result = {
            'date': date,
            'total_matches': len(fixtures),
            'analyzed': len(fixtures),
            'value_bets': top_value,
            'safe_bets': top_safe,
            'suggested_parlays': parlays
        }
        
        # Cache por 12h
        cache.set(cache_key, result, 60*60*12)
        
        logger.info(f"✅ Curadoria completa: {len(top_value)} value, {len(top_safe)} safe")
        return result
    
    def _get_fixtures_by_date(self, date, leagues):
        """Busca fixtures da API"""
        # Implementar chamada à API Football
        # Retorna lista de fixtures
        pass
    
    def _analyze_fixture(self, fixture_id, strategy):
        """Analisa um fixture com estratégia específica"""
        # Chamar fluxo completo de análise
        # Retornar top_bets
        pass
    
    def _suggest_parlays(self, safe_bets):
        """
        Combina apostas seguras em bilhetes otimizados.
        
        Critérios:
        - 2-4 apostas por bilhete
        - Odd total: 3.0 - 8.0
        - Prob combinada >= 15%
        - Máximo 1 aposta por fixture
        """
        parlays = []
        
        # Bilhete conservador (3 apostas, prob ~20%)
        if len(safe_bets) >= 3:
            # Garantir fixtures diferentes
            used_fixtures = set()
            parlay_bets = []
            
            for bet in safe_bets:
                fixture_id = bet['fixture']['id']
                if fixture_id not in used_fixtures and len(parlay_bets) < 3:
                    parlay_bets.append(bet)
                    used_fixtures.add(fixture_id)
            
            if len(parlay_bets) == 3:
                parlay = self._create_parlay(parlay_bets, "Bilhete Seguro 3x")
                if parlay['combined_probability'] >= 15:
                    parlays.append(parlay)
        
        # Bilhete moderado (4 apostas)
        if len(safe_bets) >= 4:
            # ... similar ...
            pass
        
        return parlays
    
    def _create_parlay(self, bets, name):
        """Calcula estatísticas do bilhete"""
        total_odd = 1.0
        combined_prob = 1.0
        bet_ids = []
        
        for bet in bets:
            total_odd *= bet['market_odd']
            combined_prob *= bet['probability']
            bet_ids.append(bet['fixture']['id'])
        
        expected_roi = (combined_prob * total_odd - 1) * 100
        
        return {
            'name': name,
            'bets': bet_ids,
            'bet_details': bets,  # Para exibição
            'total_odd': round(total_odd, 2),
            'combined_probability': round(combined_prob * 100, 1),
            'expected_roi': round(expected_roi, 1),
            'expected_hit_rate': f"1 em {int(1/combined_prob)}"
        }
```

#### 1.4 Novo Endpoint `daily-picks`

**views.py**
```python
from .services.daily_curator import DailyCurator

@require_http_methods(["GET"])
def daily_picks(request):
    """
    Endpoint: /api/analysis/daily-picks/
    
    Query params:
        - date: YYYY-MM-DD (default: hoje)
        - leagues: 39,140,78 (comma-separated, optional)
        - min_confidence: 70-100 (default: 70)
    
    Returns:
        {
            'date': '2026-01-19',
            'value_bets': [...],
            'safe_bets': [...],
            'suggested_parlays': [...]
        }
    """
    try:
        date = request.GET.get('date')
        leagues_str = request.GET.get('leagues')
        min_confidence = int(request.GET.get('min_confidence', 70))
        
        leagues = None
        if leagues_str:
            leagues = [int(l) for l in leagues_str.split(',')]
        
        curator = DailyCurator()
        picks = curator.get_daily_picks(date, leagues, min_confidence)
        
        return JsonResponse(picks)
        
    except Exception as e:
        logger.error(f"Erro em daily_picks: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
```

**urls.py**
```python
urlpatterns = [
    # ... existentes ...
    path('daily-picks/', views.daily_picks, name='daily-picks'),
]
```

#### 1.5 Modificar `ai_analyzer.py`

**Prompt adaptado por estratégia**
```python
def _build_prompt(self, decision_data):
    """Prompt muda baseado na estratégia"""
    strategy = decision_data.get('strategy', 'value')
    top_bets = decision_data.get('top_bets', [])
    
    if strategy == 'multiple':
        # PROMPT PARA BILHETES
        return f"""
Você é um CONSULTOR DE BILHETES MÚLTIPLOS.

📋 APOSTAS SELECIONADAS PARA BILHETE

{self._format_bets_for_prompt(top_bets)}

🎯 SUA TAREFA:
Explique por que estas apostas SÃO IDEAIS PARA COMBINAR:
- Alta probabilidade individual (50-70%)
- Valor positivo (EV > +5%)
- Probabilidade combinada razoável (15-25%)

FORMATO OBRIGATÓRIO:

📋 APOSTAS PARA BILHETE

[Para cada top_bet:]

✅ [Nome aposta] - Odd [X.XX]
PORQUE INCLUIR:
• [Razão 1 - estatística de probabilidade]
• [Razão 2 - valor positivo]
• [Razão 3 - dados históricos]

💡 DICA BILHETE:
Combine 2-3 destas apostas para odd total entre 3.00-6.00.
Probabilidade razoável com retorno atrativo.

⚠️ LEMBRE-SE: Bilhetes são mais arriscados. Mesmo com alta probabilidade individual,
apenas ~20% dos bilhetes acertam todas as pernas.
"""
    else:
        # PROMPT VALUE (existente)
        return f"""
Você é um CONSULTOR DE VALUE BETTING.
... prompt atual ...
"""
```

---

### **FASE 2: Frontend Base** (2-3 dias)
Status: ⏳ Pendente

#### 2.1 Toggle de Estratégia (Análise Individual)

**components/StrategyToggle.tsx**
```typescript
interface StrategyToggleProps {
  strategy: 'value' | 'multiple';
  onChange: (strategy: 'value' | 'multiple') => void;
}

export function StrategyToggle({ strategy, onChange }: StrategyToggleProps) {
  return (
    <div className="strategy-toggle">
      <button
        className={strategy === 'value' ? 'active' : ''}
        onClick={() => onChange('value')}
      >
        <span className="icon">⚡</span>
        <span className="label">Aposta Simples</span>
        <span className="sublabel">Máximo valor</span>
      </button>
      
      <button
        className={strategy === 'multiple' ? 'active' : ''}
        onClick={() => onChange('multiple')}
      >
        <span className="icon">📋</span>
        <span className="label">Para Bilhete</span>
        <span className="sublabel">Alta probabilidade</span>
      </button>
    </div>
  );
}
```

**CSS**
```css
.strategy-toggle {
  display: flex;
  gap: 12px;
  margin: 20px 0;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 12px;
}

.strategy-toggle button {
  flex: 1;
  padding: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.strategy-toggle button.active {
  border-color: #00A86B;
  background: #e6f7f1;
}

.strategy-toggle .icon {
  font-size: 24px;
  display: block;
  margin-bottom: 8px;
}

.strategy-toggle .label {
  font-weight: 600;
  display: block;
  margin-bottom: 4px;
}

.strategy-toggle .sublabel {
  font-size: 12px;
  color: #666;
}
```

#### 2.2 Modificar Página de Detalhes

**pages/MatchDetail.tsx**
```typescript
import { useState } from 'react';
import { StrategyToggle } from '../components/StrategyToggle';

export function MatchDetail({ fixtureId }) {
  const [strategy, setStrategy] = useState<'value' | 'multiple'>('value');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // Recarregar análise quando strategy muda
  useEffect(() => {
    loadAnalysis();
  }, [strategy, fixtureId]);
  
  async function loadAnalysis() {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/analysis/preview/${fixtureId}/?strategy=${strategy}`
      );
      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Erro ao carregar análise:', error);
    } finally {
      setLoading(false);
    }
  }
  
  return (
    <div className="match-detail">
      <header>
        <h1>{analysis?.home_team} vs {analysis?.away_team}</h1>
      </header>
      
      {/* Toggle de Estratégia */}
      <StrategyToggle 
        strategy={strategy}
        onChange={setStrategy}
      />
      
      {/* Explicação da estratégia atual */}
      <InfoBox strategy={strategy} />
      
      {/* Recomendações (adaptadas por strategy) */}
      {loading ? (
        <Loader />
      ) : (
        <Recommendations 
          bets={analysis?.top_bets}
          strategy={strategy}
        />
      )}
    </div>
  );
}
```

**components/InfoBox.tsx**
```typescript
export function InfoBox({ strategy }) {
  const info = {
    value: {
      title: '⚡ Aposta Simples (Value Betting)',
      description: 'Maximiza lucro a longo prazo apostando em odds sobrevalorizadas.',
      stats: [
        { label: 'Taxa de acerto', value: '30-45%', note: 'Normal' },
        { label: 'ROI esperado', value: '+15-25%', note: 'Após 100+ apostas' },
        { label: 'Risco', value: 'Médio-Alto', note: 'Odds altas' }
      ],
      example: 'Aposta: Fora vence (30% prob, odd 3.90, EV +23%) - Lucro: +225€ em 100 apostas'
    },
    multiple: {
      title: '📋 Para Bilhete (Safe Bets)',
      description: 'Apostas com alta probabilidade e valor positivo, ideais para combinar.',
      stats: [
        { label: 'Taxa de acerto', value: '50-70%', note: 'Por aposta' },
        { label: 'Taxa bilhete 3x', value: '15-25%', note: '1 em 5 acerta' },
        { label: 'Risco', value: 'Baixo-Médio', note: 'Odds moderadas' }
      ],
      example: 'Bilhete 3x: Over 2.5 (65%) + Casa vence (60%) + BTTS (55%) = 21.6% chance total'
    }
  };
  
  const current = info[strategy];
  
  return (
    <div className="info-box">
      <h3>{current.title}</h3>
      <p>{current.description}</p>
      
      <div className="stats-grid">
        {current.stats.map(stat => (
          <div key={stat.label} className="stat">
            <span className="label">{stat.label}</span>
            <span className="value">{stat.value}</span>
            <span className="note">{stat.note}</span>
          </div>
        ))}
      </div>
      
      <div className="example">
        💡 <strong>Exemplo:</strong> {current.example}
      </div>
    </div>
  );
}
```

#### 2.3 Página Daily Picks (Estrutura Básica)

**pages/DailyPicks.tsx**
```typescript
import { useState, useEffect } from 'react';

export function DailyPicks() {
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [picks, setPicks] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadDailyPicks();
  }, [date]);
  
  async function loadDailyPicks() {
    setLoading(true);
    try {
      const response = await fetch(
        `/api/analysis/daily-picks/?date=${date}`
      );
      const data = await response.json();
      setPicks(data);
    } catch (error) {
      console.error('Erro:', error);
    } finally {
      setLoading(false);
    }
  }
  
  if (loading) return <Loader />;
  
  return (
    <div className="daily-picks-page">
      {/* Header */}
      <header>
        <h1>🎯 Apostas do Dia</h1>
        <DatePicker value={date} onChange={setDate} />
        <p>{picks.total_matches} jogos analisados</p>
      </header>
      
      {/* Banner Educativo */}
      <EducationalBanner />
      
      {/* Duas colunas */}
      <div className="picks-grid">
        <div className="column">
          <h2>⚡ Apostas Simples</h2>
          <p>Melhor valor esperado</p>
          <BetsList bets={picks.value_bets} type="value" />
        </div>
        
        <div className="column">
          <h2>📋 Para Bilhetes</h2>
          <p>Alta probabilidade + valor</p>
          <BetsList bets={picks.safe_bets} type="safe" />
          
          {/* Bilhetes sugeridos */}
          <h3>🎁 Bilhetes Prontos</h3>
          <ParlaysList parlays={picks.suggested_parlays} />
        </div>
      </div>
    </div>
  );
}
```

---

### **FASE 3: Polish & Features Avançadas** (2-3 dias)
Status: ⏳ Pendente

#### 3.1 Componentes Avançados
- `EducationalBanner` (explicação completa)
- `BetCard` (design diferenciado por strategy)
- `SuggestedParlays` (bilhetes prontos)
- `FiltersBar` (data, liga, confiança)

#### 3.2 Features
- Loading skeletons
- Animações de transição
- Mobile responsive
- Error boundaries

#### 3.3 Testes
- Testes E2E (Playwright)
- Testes unitários (pytest)
- Validação de dados

---

## 🧪 Testes e Validação

### Teste Manual Rápido

**1. Testar Toggle em Análise Individual**
```bash
# Backend já rodando
# Frontend: adicionar toggle

# Testar chamadas:
curl "http://localhost:8000/api/analysis/preview/12345/?strategy=value"
curl "http://localhost:8000/api/analysis/preview/12345/?strategy=multiple"

# Verificar:
# - strategy='value': top_bets com EV alto, prob média
# - strategy='multiple': top_bets com prob alta, EV moderado
```

**2. Testar Curadoria Diária**
```bash
curl "http://localhost:8000/api/analysis/daily-picks/?date=2026-01-19"

# Verificar:
# - value_bets: 10 apostas com EV alto
# - safe_bets: 10 apostas com prob >= 50%
# - suggested_parlays: 2-3 bilhetes
```

### Métricas de Sucesso

**Backend:**
- ✅ Strategy param funciona em `preview`
- ✅ Score muda baseado em strategy
- ✅ Filtro remove apostas prob < 50% no modo multiple
- ✅ Daily curator retorna top 10 de cada

**Frontend:**
- ✅ Toggle troca strategy e recarrega
- ✅ InfoBox explica diferença
- ✅ Top bets mudam visualmente
- ✅ Página Daily Picks lista ambas estratégias

---

## 📊 Comparação Antes vs Depois

### ANTES (Sistema Atual)
```
Análise Jogo:
✅ Recomendação principal (mais provável)
✅ Top 3 apostas (objetivas)
❌ Todas focadas em EV máximo
❌ Confunde usuários ("por que time ruim?")
❌ Incompatível com bilhetes
```

### DEPOIS (Sistema Dual)
```
Análise Jogo:
✅ Toggle ⚡ Value / 📋 Bilhete
✅ Explicação da estratégia
✅ Top 3 adaptadas ao objetivo
✅ Usuário escolhe: lucro LP vs acerto MP
✅ Bilhetes viáveis (prob 15-25%)

Daily Picks:
✅ Curadoria automática do dia
✅ 10 apostas Value + 10 Safe
✅ Bilhetes sugeridos (3-4x)
✅ Banner educativo
```

---

## 🔧 Configurações e Parâmetros

### Thresholds Configuráveis

**decision_engine.py**
```python
# Modo Value
VALUE_MIN_PROB = 0.15  # 15% mínimo
VALUE_MIN_EV = -5      # Aceita EV negativo se prob alta

# Modo Multiple
MULTIPLE_MIN_PROB = 0.50  # 50% mínimo (RÍGIDO)
MULTIPLE_MIN_EV = 5       # +5% mínimo (RÍGIDO)

# Bilhetes Sugeridos
PARLAY_MIN_COMBINED_PROB = 0.15  # 15% chance total
PARLAY_MAX_LEGS = 4              # Máximo 4 apostas
PARLAY_MIN_ODD = 3.0             # Odd mínima total
PARLAY_MAX_ODD = 8.0             # Odd máxima total
```

---

## 📝 Documentação para Usuários

### Incluir no Frontend

**FAQ Section**
```markdown
## ❓ Perguntas Frequentes

**Q: Qual estratégia devo usar?**
A: Depende do seu objetivo:
- Aposta Simples: Construir bankroll de forma consistente (100+ apostas)
- Bilhetes: Buscar retornos maiores ocasionalmente (aceita mais variância)

**Q: Por que apostar no "time mais fraco"?**
A: No modo Value, apostamos quando a odd paga MAIS que deveria.
   Exemplo: Time tem 30% chance, mas odd paga como se tivesse 25%.
   A longo prazo, isso gera lucro.

**Q: Quantas apostas devo fazer por dia?**
A: Apostas Simples: 3-10 por dia
   Bilhetes: 1-3 por semana (mais volátil)

**Q: Qual o bankroll mínimo?**
A: 100€ mínimo (stake de 1€-2€)
   Recomendado: 500€+ (stake de 5€-10€)
```

---

## 🚀 Deployment

### Checklist Pré-Deploy

**Backend:**
- [ ] Testes unitários `decision_engine.py`
- [ ] Teste integração `daily_curator.py`
- [ ] Validar cache (12h)
- [ ] Logs configurados
- [ ] Rate limiting (API Football)

**Frontend:**
- [ ] Build production (`npm run build`)
- [ ] Testes E2E passando
- [ ] Mobile responsivo
- [ ] Performance (Lighthouse > 90)

**Infraestrutura:**
- [ ] Celery worker (para background jobs)
- [ ] Redis configurado (cache)
- [ ] Monitoramento (Sentry)

---

## 📞 Suporte e Manutenção

### Monitoramento

**Métricas a Acompanhar:**
1. **Taxa de uso por estratégia**
   - Quantos % usam Value vs Multiple
   - Qual gera mais conversão

2. **Performance das recomendações**
   - Tracking real de ROI
   - Taxa de acerto por estratégia

3. **Engagement**
   - Tempo na página Daily Picks
   - Quantos bilhetes sugeridos são usados

### Ajustes Futuros

**Baseado em feedback:**
- Adicionar modo "Conservador" (prob >= 70%)
- Filtros avançados (horário, odds range)
- Notificações push
- Histórico de performance

---

## 🎯 Resumo Executivo

### O Que Muda
1. **Backend**: Parâmetro `strategy` em toda a cadeia de decisão
2. **Frontend**: Toggle na análise + página Daily Picks
3. **UX**: Usuário escolhe objetivo → Sistema adapta recomendações

### Benefícios
- ✅ Elimina confusão sobre "time fraco"
- ✅ Torna bilhetes múltiplos viáveis
- ✅ Educação embutida (usuário aprende value betting)
- ✅ Maior conversão (atendem ambos perfis)

### Riscos Mitigados
- ⚠️ Performance: Cache 12h + background jobs
- ⚠️ Complexidade: UI simples (toggle binário)
- ⚠️ Expectativas: Banner educativo + disclaimers

---

## ✅ Próximos Passos

### ✅ COMPLETO
1. ✅ Backend: decision_engine.py modificado
2. ✅ Backend: views.py aceita strategy
3. ✅ Frontend: StrategyContext global criado
4. ✅ Frontend: StrategySelector no Header
5. ✅ Frontend: MatchDetailPage usa context
6. ✅ Arquitetura global implementada

### 🧪 TESTAR AGORA
```bash
# 1. Iniciar backend
cd backend
python manage.py runserver --noreload

# 2. Iniciar frontend (outro terminal)
cd frontend
npm run dev

# 3. Testar fluxo:
#    - Abrir app no browser
#    - Clicar no toggle ⚡/📋 no topo
#    - Verificar que localStorage salva escolha
#    - Clicar em "Ver Análise" de um jogo
#    - Verificar console logs: "⚡ Estratégia: VALUE" ou "📋 MULTIPLE"
#    - Verificar que top_bets mudam (VALUE: EV alto | MULTIPLE: prob alta)
```

### ⏳ PRÓXIMA FASE (Opcional)
7. ⏳ Criar daily_curator.py
8. ⏳ Endpoint /api/analysis/daily-picks/
9. ⏳ Página Daily Picks no frontend
10. ⏳ Bilhetes sugeridos automaticamente

---

**Documento criado em:** 19/01/2026  
**Última atualização:** 19/01/2026  
**Responsável:** Sistema de IA + Desenvolvedor  
**Status:** 📋 Planejamento completo - pronto para implementar
