# 🎯 Diferenciações Competitivas - Bet Insight

> **Documento:** Recomendações estratégicas para diferenciação no mercado de análise de apostas esportivas  
> **Data:** 30 Janeiro 2026  
> **Status:** Roadmap de Features

---

## 📋 Índice

1. [Transparência Total](#1-transparência-total)
2. [IA Explicável](#2-ia-explicável)
3. [Sistema de Bankroll Inteligente](#3-sistema-de-bankroll-inteligente)
4. [Notificações Inteligentes](#4-notificações-inteligentes)
5. [Social Proof & Community](#5-social-proof--community)
6. [Análise Preditiva de Odds](#6-análise-preditiva-de-odds)
7. [Modo Simulação](#7-modo-simulação)
8. [API Pública para Devs](#8-api-pública-para-devs)
9. [Insights Exclusivos por Liga](#9-insights-exclusivos-por-liga)
10. [Comparação com Bookmakers](#10-comparação-com-bookmakers)
11. [Resumo de Prioridades](#resumo-top-5-prioridades)

---

## 1. 📊 Transparência Total (Maior Diferenciador)

### **Status:** ✅ Tecnicamente Seguro | 🔥 Alto Impacto Competitivo

### **Conceito**
Rastreamento público e em tempo real da performance real do sistema. Nenhum competitor expõe dados reais de acurácia.

### **O Que Implementar**

#### **1.1 Live Accuracy Dashboard**
Página pública mostrando:
- Taxa de acerto dos últimos 7/30/90 dias
- ROI real por estratégia (VALUE vs MULTIPLE)
- Gráfico de performance diária
- Breakdown por liga (Championship: 72%, Ligue 1: 68%)
- Histórico completo de apostas validadas

#### **Implementação Técnica**

```python
# API Endpoint (já existe!)
GET /api/daily-bets/public-stats/

# Response:
{
  "all_time": {
    "total_bets": 347,
    "won": 238,
    "lost": 89,
    "pending": 20,
    "win_rate": "68.5%",
    "roi": "+14.2%"
  },
  "last_7_days": {
    "total_bets": 42,
    "win_rate": "71.4%",
    "roi": "+18.3%"
  },
  "by_league": {
    "Championship": {"win_rate": "72%", "roi": "+18%"},
    "Ligue 1": {"win_rate": "65%", "roi": "+11%"},
    "La Liga": {"win_rate": "70%", "roi": "+15%"}
  },
  "by_bet_type": {
    "multiple": {"win_rate": "64%", "roi": "+8.5%"},
    "value": {"win_rate": "72%", "roi": "+22.1%"}
  }
}
```

#### **Frontend Component**

```jsx
// components/PublicAccuracyDashboard.jsx
const PublicAccuracyDashboard = () => {
  return (
    <div className="accuracy-dashboard">
      <h1>📊 Nossa Performance Real</h1>
      <p>100% transparente. Todas as apostas validadas automaticamente.</p>
      
      <StatsGrid>
        <StatCard title="Taxa de Acerto (30d)" value="68.5%" trend="+2.1%" />
        <StatCard title="ROI Total" value="+14.2%" trend="+3.5%" />
        <StatCard title="Apostas Validadas" value="347" />
      </StatsGrid>
      
      <PerformanceChart data={last30Days} />
      
      <LeagueBreakdown leagues={stats.by_league} />
    </div>
  );
};
```

### **Por Que Funciona**
- 🎯 **Prova Social**: Usuários veem resultados reais, não promessas
- 💎 **Confiança**: Transparência total = credibilidade máxima
- 🚀 **Viral**: Bons resultados = compartilhamento orgânico
- 🏆 **Único**: Nenhum competitor faz isso publicamente

### **Esforço de Implementação**
- Backend: ✅ **Já implementado** (DailyBet model + API)
- Frontend: 4 horas (Dashboard + gráficos)
- **Total: 4 horas**

---

## 2. 🤖 IA Explicável (Explainable AI)

### **Status:** ✅ Tecnicamente Seguro | 🔥 Alto Impacto UX

### **Conceito**
Mostrar **por que** a IA escolheu cada aposta, não apenas o resultado final. Educação + transparência.

### **O Que Implementar**

#### **2.1 Feature Importance Breakdown**

```
┌────────────────────────────────────────────────────────┐
│ Por que "Casa Over 0.5" @ 1.29?                        │
├────────────────────────────────────────────────────────┤
│ ✅ FATORES POSITIVOS:                                  │
│                                                        │
│ 🎯 Força Ofensiva Casa: 9/10 (+15% probabilidade)     │
│    └─ 1.4 gols/jogo (média da liga: 1.1)              │
│                                                        │
│ 📈 Forma Recente: 7 pts em 3 jogos (+8%)              │
│    └─ 3V, 1E, 1D - Sequência invicta em casa          │
│                                                        │
│ ⚔️ H2H Favorável: 8/10 jogos com gol casa (+5%)       │
│    └─ Média 1.8 gols/jogo nos confrontos diretos      │
│                                                        │
│ 🏟️ Mando de Campo: +7% (liga com forte home adv.)     │
│                                                        │
│ ⚠️ FATORES DE RISCO:                                   │
│                                                        │
│ 🚑 Lesões: 2 atacantes fora (-3%)                     │
│    └─ Titular e reserva do ataque                     │
│                                                        │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                        │
│ 🎲 Probabilidade Final: 77.6%                         │
│ 💰 Odd Justa: 1.29 vs Mercado: 1.29                   │
│ 📊 Confidence Score: 4/5 (High)                        │
│ ⚡ Expected Value: 0.0% (Fair price)                   │
└────────────────────────────────────────────────────────┘
```

#### **Implementação Técnica**

```python
# backend/apps/analysis/models.py (DailyBet)
def get_reasoning_breakdown(self):
    """Extrai explicação detalhada das features"""
    
    # Parse do reasoning (já vem do AIAnalyzer)
    reasoning = self.reasoning or {}
    
    # Top features do FeatureEngineer (109 features disponíveis)
    top_factors = [
        {
            "name": "Força Ofensiva Casa",
            "value": 9,
            "max": 10,
            "impact": "+15%",
            "description": "1.4 gols/jogo (média da liga: 1.1)"
        },
        {
            "name": "Forma Recente",
            "value": 7,
            "max": 10,
            "impact": "+8%",
            "description": "7 pts em 3 jogos - Invicto em casa"
        },
        {
            "name": "H2H Favorável",
            "value": 8,
            "max": 10,
            "impact": "+5%",
            "description": "8/10 jogos com gol casa"
        }
    ]
    
    risk_factors = [
        {
            "name": "Lesões",
            "impact": "-3%",
            "description": "2 atacantes titulares fora"
        }
    ]
    
    return {
        "top_factors": top_factors,
        "risk_factors": risk_factors,
        "ensemble_weights": {
            "poisson": 25,
            "logistic": 40,
            "market_prior": 35
        },
        "confidence": {
            "score": 4,
            "max": 5,
            "level": "high"
        }
    }

# Novo endpoint
@action(detail=True, methods=['get'])
def reasoning(self, request, pk=None):
    """Retorna explicação detalhada da aposta"""
    bet = self.get_object()
    return Response(bet.get_reasoning_breakdown())
```

#### **Frontend Component**

```jsx
// components/ReasoningBreakdown.jsx
const ReasoningBreakdown = ({ betId }) => {
  const { data } = useFetch(`/api/daily-bets/${betId}/reasoning/`);
  
  return (
    <div className="reasoning-breakdown">
      <h3>🤖 Por que a IA escolheu essa aposta?</h3>
      
      {/* Fatores Positivos */}
      <section className="positive-factors">
        <h4>✅ Fatores Positivos</h4>
        {data.top_factors.map(factor => (
          <FactorCard 
            key={factor.name}
            name={factor.name}
            value={factor.value}
            max={factor.max}
            impact={factor.impact}
            description={factor.description}
          />
        ))}
      </section>
      
      {/* Fatores de Risco */}
      <section className="risk-factors">
        <h4>⚠️ Fatores de Risco</h4>
        {data.risk_factors.map(risk => (
          <RiskCard 
            key={risk.name}
            name={risk.name}
            impact={risk.impact}
            description={risk.description}
          />
        ))}
      </section>
      
      {/* Ensemble Breakdown */}
      <section className="ensemble-info">
        <h4>🎲 Como Chegamos Nessa Probabilidade?</h4>
        <EnsembleChart weights={data.ensemble_weights} />
      </section>
    </div>
  );
};
```

### **Dados Já Disponíveis**
- ✅ 109 features do FeatureEngineer
- ✅ Pesos do Ensemble (Poisson, Logística, Market Prior)
- ✅ Reasoning textual do AIAnalyzer
- ✅ Confidence score e risk level

### **Por Que Funciona**
- 🎓 **Educação**: Usuário aprende sobre análise de apostas
- 💪 **Confiança**: Entende o "porquê", não apenas "o quê"
- 🏆 **Diferenciação**: Competitors mostram só "Casa @ 2.0"
- 🧠 **Memorável**: Usuário lembra da lógica e volta

### **Esforço de Implementação**
- Backend: 3 horas (método get_reasoning_breakdown + endpoint)
- Frontend: 3 horas (componentes visuais)
- **Total: 6 horas**

---

## 3. 💰 Sistema de Bankroll Inteligente

### **Status:** ✅ Tecnicamente Seguro | 💰 Alto Valor Percebido

### **Conceito**
Gestão automática de banca usando **Kelly Criterion** (matematicamente ótimo para crescimento de longo prazo).

### **O Que Implementar**

#### **3.1 Rastreamento de Banca Pessoal**

```
┌──────────────────────────────────────────────────────┐
│ 💰 Sua Banca                                         │
├──────────────────────────────────────────────────────┤
│                                                      │
│ Atual: 127.5u (+27.5% em 30 dias) 📈                │
│ Inicial: 100u (01/Jan/2026)                         │
│                                                      │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│ 📊 Estatísticas:                                     │
│ • ROI: +27.5%                                        │
│ • Melhor Dia: +12.3u (15/Jan)                       │
│ • Pior Dia: -5.2u (08/Jan)                          │
│ • Drawdown Máximo: -8.2%                            │
│ • Apostas Realizadas: 47                            │
│                                                      │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│ 🎯 Alocação Sugerida Hoje:                          │
│                                                      │
│ Bilhete 3x (Odd 2.03, Prob 54.6%):                  │
│ └─ Kelly Stake: 2.5u (2.0% da banca) ✅             │
│                                                      │
│ Value Bet #1 (Odd 2.35, Prob 52%, EV +23%):         │
│ └─ Kelly Stake: 3.8u (3.0% da banca) ✅             │
│                                                      │
│ Value Bet #2 (Odd 2.10, Prob 53%, EV +11%):         │
│ └─ Kelly Stake: 2.5u (2.0% da banca) ✅             │
│                                                      │
│ 📊 Risco Total Hoje: 8% da banca (Baixo) ✅         │
│                                                      │
│ [Registrar Aposta] [Ver Histórico]                  │
└──────────────────────────────────────────────────────┘
```

#### **3.2 Kelly Criterion - Matemática**

```python
# Fórmula do Kelly
Kelly % = (probability × odd - 1) / (odd - 1)

# Exemplo:
# Odd: 2.10, Probabilidade: 53%
Kelly = (0.53 × 2.10 - 1) / (2.10 - 1)
Kelly = (1.113 - 1) / 1.10
Kelly = 0.113 / 1.10
Kelly = 10.3%

# Fractional Kelly (mais seguro)
Stake = Bankroll × Kelly × 0.25  # 25% do Kelly
Stake = 100u × 0.103 × 0.25
Stake = 2.6u
```

#### **Implementação Técnica**

```python
# backend/apps/users/models.py (novo model)
class UserBankroll(models.Model):
    """Rastreamento de banca do usuário"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    initial = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    current = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='MZN')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_kelly_stake(self, probability, odd, fractional=0.25):
        """
        Calcula stake ótimo usando Kelly Criterion
        
        Args:
            probability (float): 0.0 - 1.0
            odd (float): Decimal odd (ex: 2.10)
            fractional (float): Fração do Kelly a usar (0.25 = 25%)
        
        Returns:
            float: Stake recomendado em unidades
        """
        if probability <= 0 or odd <= 1:
            return 0
        
        # Kelly % = (p × b - 1) / (b - 1)
        # onde b = odd - 1
        kelly_pct = (probability * odd - 1) / (odd - 1)
        
        # Fractional Kelly para segurança
        kelly_pct = max(0, kelly_pct) * fractional
        
        # Stake máximo: 5% da banca (proteção)
        kelly_pct = min(kelly_pct, 0.05)
        
        return round(float(self.current) * kelly_pct, 2)
    
    def record_bet(self, amount, result):
        """Registra aposta e atualiza banca"""
        if result == 'won':
            self.current += amount
        elif result == 'lost':
            self.current -= amount
        self.save()
    
    def get_stats(self):
        """Retorna estatísticas da banca"""
        bets = self.user.bets.all()
        
        return {
            'current': float(self.current),
            'initial': float(self.initial),
            'roi': ((self.current - self.initial) / self.initial * 100),
            'total_bets': bets.count(),
            'won': bets.filter(result='won').count(),
            'lost': bets.filter(result='lost').count(),
            'max_drawdown': self._calculate_max_drawdown(),
            'best_day': self._get_best_day(),
            'worst_day': self._get_worst_day()
        }
    
    def _calculate_max_drawdown(self):
        """Calcula maior queda percentual"""
        # Implementar análise de histórico
        pass

# backend/apps/users/models.py (novo model)
class UserBet(models.Model):
    """Registro de apostas do usuário"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bets')
    daily_bet = models.ForeignKey('analysis.DailyBet', on_delete=models.SET_NULL, null=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    odd = models.DecimalField(max_digits=5, decimal_places=2)
    
    result = models.CharField(max_length=20, choices=[
        ('pending', 'Pendente'),
        ('won', 'Vencida'),
        ('lost', 'Perdida'),
        ('void', 'Anulada')
    ])
    
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    placed_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    
    def calculate_profit(self):
        """Calcula lucro/prejuízo"""
        if self.result == 'won':
            self.profit = self.amount * (self.odd - 1)
        elif self.result == 'lost':
            self.profit = -self.amount
        else:
            self.profit = 0
        self.save()
```

#### **API Endpoints**

```python
# backend/apps/users/views.py
class BankrollViewSet(viewsets.ModelViewSet):
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas da banca"""
        bankroll = request.user.bankroll
        return Response(bankroll.get_stats())
    
    @action(detail=False, methods=['post'])
    def calculate_stake(self, request):
        """Calcula stake Kelly para aposta"""
        probability = request.data['probability']  # 0.0 - 1.0
        odd = request.data['odd']
        
        bankroll = request.user.bankroll
        stake = bankroll.calculate_kelly_stake(probability, odd)
        
        return Response({
            'recommended_stake': stake,
            'percentage_of_bankroll': (stake / float(bankroll.current)) * 100,
            'kelly_full': stake / 0.25,  # Kelly completo
            'kelly_fractional': stake  # 25% do Kelly
        })
    
    @action(detail=False, methods=['post'])
    def record_bet(self, request):
        """Registra aposta do usuário"""
        amount = request.data['amount']
        odd = request.data['odd']
        daily_bet_id = request.data.get('daily_bet_id')
        
        UserBet.objects.create(
            user=request.user,
            daily_bet_id=daily_bet_id,
            amount=amount,
            odd=odd,
            result='pending'
        )
        
        return Response({'status': 'recorded'})
```

### **Por Que Funciona**
- 💰 **Gestão de Risco**: Evita apostas emocionais e overbet
- 📈 **Crescimento Sustentável**: Kelly otimiza crescimento de longo prazo
- 🎯 **Personalização**: Cada usuário tem estratégia única baseada em sua banca
- 🧠 **Educação**: Aprende sobre bankroll management

### **Esforço de Implementação**
- Backend: 6 horas (models, API, cálculos)
- Frontend: 2 horas (dashboard de banca)
- **Total: 8 horas**

---

## 4. 📱 Notificações Inteligentes

### **Status:** ⚠️ Requer Infraestrutura | 🔥 Alto Engagement

### **Conceito**
Push notifications quando eventos importantes acontecem (value excepcional, odd em movimento, etc).

### **O Que Implementar**

#### **4.1 Alertas de Value Bets**

```
┌─────────────────────────────────────────────┐
│ 🔔 VALUE ALERT!                             │
├─────────────────────────────────────────────┤
│                                             │
│ Lens vs Le Havre                            │
│ Under 2.5 @ 2.35                            │
│                                             │
│ ⚡ EV: +23% (EXCEPCIONAL!)                  │
│ 🎯 Prob: 52%                                │
│ 💰 Stake: 3.8u (Kelly)                      │
│                                             │
│ ⏰ Jogo em 4h30min                          │
│                                             │
│ [Ver Análise] [Apostar Agora]              │
└─────────────────────────────────────────────┘
```

#### **4.2 Tipos de Alertas**

1. **Value Excepcional** (EV > 15%)
2. **Odd em Movimento Favorável** (subiu >5%)
3. **Bilhete de Alta Probabilidade** (>80% combinada)
4. **Novo Bilhete Disponível** (gerado às 6h)
5. **Resultado Validado** ("Sua aposta ganhou! +5.2u")

#### **Implementação Técnica**

```python
# backend/apps/notifications/services.py
from firebase_admin import messaging

class NotificationService:
    
    @staticmethod
    def send_value_alert(bet, users):
        """Envia alerta de value excepcional"""
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title='🔔 VALUE ALERT!',
                body=f'{bet.match} - {bet.market} @ {bet.odd}\nEV: +{bet.expected_value}%'
            ),
            data={
                'type': 'value_alert',
                'bet_id': str(bet.id),
                'ev': str(bet.expected_value),
                'url': f'/daily-bets/{bet.id}'
            },
            tokens=[user.fcm_token for user in users]
        )
        
        response = messaging.send_multicast(message)
        return response

# backend/apps/analysis/tasks.py
@periodic_task(run_every=timedelta(hours=1))
def check_exceptional_value():
    """Verifica value bets excepcionais e notifica"""
    
    # Bets com EV > 15%
    exceptional_bets = DailyBet.objects.filter(
        expected_value__gte=15,
        date=date.today(),
        status='pending'
    )
    
    # Usuários com notificações ativadas
    users = User.objects.filter(
        notification_settings__value_alerts=True,
        fcm_token__isnull=False
    )
    
    for bet in exceptional_bets:
        # Verifica se já foi notificado
        if not Notification.objects.filter(bet=bet, type='value_alert').exists():
            NotificationService.send_value_alert(bet, users)
            
            # Registra notificação
            Notification.objects.create(
                bet=bet,
                type='value_alert',
                sent_to=users.count()
            )
            
            logger.info(f"🔔 Value alert sent for bet #{bet.id} (EV: {bet.expected_value}%)")

@periodic_task(run_every=timedelta(hours=2))
def check_odds_movement():
    """Verifica movimento de odds favorável"""
    
    for bet in DailyBet.objects.filter(date=date.today(), status='pending'):
        # Busca odd atual
        current_odd = fetch_current_odd(bet.match, bet.market)
        
        # Se odd subiu >5%
        if current_odd > bet.odd * 1.05:
            users = User.objects.filter(
                notification_settings__odds_movement=True,
                fcm_token__isnull=False
            )
            
            NotificationService.send_odds_movement_alert(bet, current_odd, users)
```

#### **Frontend - Configurações de Notificações**

```jsx
// components/NotificationSettings.jsx
const NotificationSettings = () => {
  const [settings, setSettings] = useState({
    value_alerts: true,
    odds_movement: true,
    new_tickets: true,
    results: true
  });
  
  return (
    <div className="notification-settings">
      <h3>🔔 Configurar Notificações</h3>
      
      <Toggle
        label="Alertas de Value (EV > 15%)"
        checked={settings.value_alerts}
        onChange={(v) => updateSetting('value_alerts', v)}
      />
      
      <Toggle
        label="Movimento de Odds (+5%)"
        checked={settings.odds_movement}
        onChange={(v) => updateSetting('odds_movement', v)}
      />
      
      <Toggle
        label="Novos Bilhetes Diários"
        checked={settings.new_tickets}
        onChange={(v) => updateSetting('new_tickets', v)}
      />
      
      <Toggle
        label="Resultados das Minhas Apostas"
        checked={settings.results}
        onChange={(v) => updateSetting('results', v)}
      />
    </div>
  );
};
```

### **Por Que Funciona**
- ⚡ **Urgência**: "Aposta agora antes que odd caia!"
- 📲 **Engagement**: Usuário volta ao app diariamente
- 🎯 **Personalizado**: Só notifica values realmente excepcionais
- 💰 **Conversão**: Notificações → Mais apostas → Mais engajamento

### **Esforço de Implementação**
- Backend: 8 horas (Firebase, Celery tasks, models)
- Frontend: 4 hours (permissions, settings)
- **Total: 12 horas**

---

## 5. 🏆 Social Proof & Community

### **Status:** ✅ Tecnicamente Seguro | 🎮 Gamificação

### **Conceito**
Leaderboard público de usuários com melhor performance. Gamificação + social learning.

### **O Que Implementar**

#### **5.1 Leaderboard Público**

```
┌─────────────────────────────────────────────────────┐
│ 🏆 Top Apostadores (Últimos 30 dias)                │
├─────────────────────────────────────────────────────┤
│                                                     │
│ #1  @João_Silva           ROI: +32.5% 🥇          │
│     47 apostas | 34 acertos (72%)                  │
│     [Ver Estratégia] [Seguir]                      │
│                                                     │
│ #2  @Maria_Costa          ROI: +28.1% 🥈          │
│     52 apostas | 36 acertos (69%)                  │
│     [Ver Estratégia] [Seguir]                      │
│                                                     │
│ #3  @Pedro_Alves          ROI: +24.7% 🥉          │
│     39 apostas | 28 acertos (72%)                  │
│     [Ver Estratégia] [Seguir]                      │
│                                                     │
│ ...                                                 │
│                                                     │
│ #47 🎯 Você               ROI: +12.3%              │
│     31 apostas | 22 acertos (71%)                  │
│     [Melhorar Ranking] [Compartilhar]              │
│                                                     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                     │
│ 💡 Dica: Siga os top 3 para copiar estratégias!    │
└─────────────────────────────────────────────────────┘
```

#### **5.2 Badges & Conquistas**

```
🏅 Badges Disponíveis:

✅ Streak Master     - 7 dias consecutivos apostando
✅ Sharp Bettor      - 90% accuracy em 20+ apostas
✅ Value Hunter      - 10 value bets com EV > 20%
✅ Early Adopter     - Cadastrou em Janeiro 2026
✅ Bankroll Builder  - +50% ROI em 30 dias
✅ Risk Manager      - Nunca apostou >5% da banca
```

#### **Implementação Técnica**

```python
# backend/apps/users/models.py
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Social
    username = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True)
    
    # Privacy
    is_public = models.BooleanField(default=False)
    show_on_leaderboard = models.BooleanField(default=False)
    
    # Stats
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')
    
    def get_leaderboard_stats(self, days=30):
        """Calcula stats para leaderboard"""
        cutoff = timezone.now() - timedelta(days=days)
        bets = self.user.bets.filter(placed_at__gte=cutoff, result__in=['won', 'lost'])
        
        total = bets.count()
        won = bets.filter(result='won').count()
        
        total_staked = sum(float(b.amount) for b in bets)
        total_profit = sum(float(b.profit) for b in bets)
        
        return {
            'username': self.username,
            'total_bets': total,
            'won': won,
            'win_rate': (won / total * 100) if total > 0 else 0,
            'roi': (total_profit / total_staked * 100) if total_staked > 0 else 0,
            'total_profit': total_profit
        }

# backend/apps/users/views.py
class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    
    def list(self, request):
        """Lista top 100 usuários"""
        days = int(request.query_params.get('days', 30))
        
        # Usuários públicos
        profiles = UserProfile.objects.filter(show_on_leaderboard=True)
        
        # Calcula stats
        leaderboard = []
        for profile in profiles:
            stats = profile.get_leaderboard_stats(days)
            if stats['total_bets'] >= 10:  # Mínimo 10 apostas
                leaderboard.append(stats)
        
        # Ordena por ROI
        leaderboard = sorted(leaderboard, key=lambda x: x['roi'], reverse=True)
        
        return Response({
            'top_100': leaderboard[:100],
            'current_user_rank': self._get_user_rank(request.user, leaderboard)
        })

# backend/apps/users/models.py (Badges)
class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)  # emoji
    condition = models.CharField(max_length=200)
    
class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

# Celery task para atribuir badges
@periodic_task(run_every=timedelta(hours=6))
def award_badges():
    """Verifica e atribui badges"""
    
    # Streak Master
    for user in User.objects.all():
        if user.has_7_day_streak():
            Badge.award_to_user(user, 'streak_master')
    
    # Sharp Bettor (90% accuracy)
    for user in User.objects.all():
        stats = user.profile.get_leaderboard_stats(days=30)
        if stats['total_bets'] >= 20 and stats['win_rate'] >= 90:
            Badge.award_to_user(user, 'sharp_bettor')
```

### **Por Que Funciona**
- 🎮 **Gamificação**: Usuários competem por ranking
- 👥 **Social Learning**: Iniciantes copiam estratégias de experts
- 🚀 **Viralidade**: "Compartilhar meu ranking no Twitter"
- 🏆 **Retenção**: Usuários voltam para melhorar posição

### **Esforço de Implementação**
- Backend: 6 horas (models, leaderboard API, badges)
- Frontend: 4 horas (leaderboard UI, profile pages)
- **Total: 10 horas**

---

## 6. 📈 Análise Preditiva de Odds

### **Status:** ✅ Tecnicamente Seguro | 💎 Diferenciação Única

### **Conceito**
Rastrear movimento de odds ao longo do dia e recomendar melhor momento para apostar.

### **O Que Implementar**

#### **6.1 Odds Timeline**

```
┌────────────────────────────────────────────────────┐
│ Bristol vs Derby - Over 2.5                        │
├────────────────────────────────────────────────────┤
│                                                    │
│ 📊 Movimento de Odd (Últimas 12h):                │
│                                                    │
│ 2.15 ┤                             ●              │
│ 2.10 ┤              ●──────●───────               │
│ 2.05 ┤        ●─────                              │
│ 2.00 ┤   ●────                                    │
│ 1.95 ┼●──                                         │
│      └─────────────────────────────────────────   │
│       6h    8h   10h   12h   14h   16h   18h      │
│                                                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                    │
│ Odd Atual: 2.10 ⬆️ (+7.7% desde manhã)            │
│ Odd Média (7d): 2.05                              │
│ Nossa Fair Odd: 1.89                              │
│                                                    │
│ 💡 RECOMENDAÇÃO: ✅ APOSTAR AGORA                 │
│                                                    │
│ Razão: Odd subiu 7.7% e pode cair novamente       │
│                                                    │
│ 📊 Padrão Histórico:                              │
│ Em 68% dos casos, odds caem nas últimas 2h        │
│ antes do jogo (média -3.2%)                       │
│                                                    │
│ [Apostar @2.10] [Esperar]                         │
└────────────────────────────────────────────────────┘
```

#### **Implementação Técnica**

```python
# backend/apps/odds/models.py (novo app)
class OddsHistory(models.Model):
    """Rastreamento histórico de odds"""
    
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE)
    market = models.CharField(max_length=50)  # 'over_25', 'home_win', etc
    bookmaker = models.CharField(max_length=50, default='average')
    
    odd = models.DecimalField(max_digits=5, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['match', 'market', 'timestamp']),
        ]

# backend/apps/odds/services.py
class OddsAnalyzer:
    
    @staticmethod
    def get_movement_analysis(match, market):
        """Analisa movimento de odd para um mercado"""
        
        # Histórico últimas 24h
        history = OddsHistory.objects.filter(
            match=match,
            market=market,
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).order_by('timestamp')
        
        if not history.exists():
            return None
        
        first_odd = float(history.first().odd)
        current_odd = float(history.last().odd)
        
        change_pct = ((current_odd - first_odd) / first_odd) * 100
        
        # Calcula média de 7 dias
        avg_7d = OddsHistory.objects.filter(
            match__league=match.league,
            market=market,
            timestamp__gte=timezone.now() - timedelta(days=7)
        ).aggregate(Avg('odd'))['odd__avg']
        
        # Padrão histórico (odds caem antes do jogo?)
        historical_pattern = cls._analyze_historical_pattern(match.league, market)
        
        return {
            'current_odd': current_odd,
            'first_odd': first_odd,
            'change_pct': round(change_pct, 1),
            'average_7d': float(avg_7d) if avg_7d else None,
            'trend': 'up' if change_pct > 2 else 'down' if change_pct < -2 else 'stable',
            'recommendation': cls._get_recommendation(change_pct, historical_pattern),
            'historical_pattern': historical_pattern,
            'timeline': [
                {'time': h.timestamp, 'odd': float(h.odd)}
                for h in history
            ]
        }
    
    @staticmethod
    def _get_recommendation(change_pct, pattern):
        """Recomenda quando apostar"""
        
        # Se odd subiu muito e historicamente cai antes do jogo
        if change_pct > 5 and pattern['usually_drops_before_match']:
            return {
                'action': 'bet_now',
                'confidence': 'high',
                'reason': f'Odd subiu {change_pct:.1f}% e tende a cair antes do jogo'
            }
        
        # Se odd caiu muito
        if change_pct < -5:
            return {
                'action': 'wait',
                'confidence': 'medium',
                'reason': 'Odd em queda, pode estabilizar em valor menor'
            }
        
        # Estável
        return {
            'action': 'bet_now',
            'confidence': 'medium',
            'reason': 'Odd estável, pode apostar'
        }

# backend/apps/analysis/tasks.py
@periodic_task(run_every=timedelta(hours=2))
def track_odds_movement():
    """Rastreia odds a cada 2 horas"""
    
    # Partidas de hoje e amanhã
    matches = Match.objects.filter(
        status='NS',
        fixture_date__gte=timezone.now(),
        fixture_date__lte=timezone.now() + timedelta(days=2)
    )
    
    for match in matches:
        try:
            # Busca odds atuais
            odds = api_football.fetch_odds(match.api_fixture_id)
            
            # Salva histórico
            for market, odd_value in odds.items():
                OddsHistory.objects.create(
                    match=match,
                    market=market,
                    odd=odd_value
                )
            
            logger.info(f"📊 Odds tracked for match #{match.id}")
            
        except Exception as e:
            logger.error(f"Error tracking odds: {e}")
```

### **Por Que Funciona**
- 💰 **Maximiza EV**: Aposta quando odd está no melhor momento
- 🎯 **Data-Driven**: Decisão baseada em padrões históricos reais
- 🏆 **Único no Mercado**: Nenhum competitor oferece isso
- 📊 **Educação**: Usuário aprende sobre timing de apostas

### **Esforço de Implementação**
- Backend: 8 horas (models, Celery tasks, análise)
- Frontend: 4 horas (gráficos, timeline UI)
- **Total: 12 horas**

---

## 7. 🎮 Modo Simulação (Paper Trading)

### **Status:** ✅ Tecnicamente Seguro | 🎓 Educacional

### **Conceito**
Usuários testam estratégias com dinheiro virtual antes de apostar de verdade. Zero risco, máximo aprendizado.

### **O Que Implementar**

#### **7.1 Banca Virtual**

```
┌────────────────────────────────────────────────────┐
│ 🎮 MODO SIMULAÇÃO                                  │
├────────────────────────────────────────────────────┤
│                                                    │
│ Banca Virtual: 1,247.50 MZN (+24.8% em 30d) 🎮   │
│ Inicial: 1,000 MZN                                │
│                                                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                    │
│ 📊 Sua Performance vs IA:                         │
│                                                    │
│ 👤 Você:                                          │
│    • ROI: +24.8% (47 apostas)                     │
│    • Win Rate: 68.1% (32/47)                      │
│    • Melhor Aposta: +127 MZN                      │
│                                                    │
│ 🤖 IA (Múltiplos):                                │
│    • ROI: +12.3% (24 bilhetes)                    │
│    • Win Rate: 66.7% (16/24)                      │
│                                                    │
│ 🤖 IA (Value):                                    │
│    • ROI: +18.5% (30 value bets)                  │
│    • Win Rate: 66.7% (20/30)                      │
│                                                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                    │
│ 💡 Insights Personalizados:                       │
│                                                    │
│ ✅ Você está indo bem!                            │
│    Superou a IA em +6.3% ROI                      │
│                                                    │
│ ⚠️ Pontos de Atenção:                             │
│    • 73% das suas apostas são em 1X2              │
│    • Tente diversificar em Over/Under e BTTS     │
│    • Seu stake médio: 4.2% (ideal: 2-3%)         │
│                                                    │
│ [Ver Histórico] [Apostar de Verdade]              │
└────────────────────────────────────────────────────┘
```

#### **Implementação Técnica**

```python
# backend/apps/users/models.py
class VirtualBankroll(models.Model):
    """Banca virtual para simulação"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    initial = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_reset = models.DateTimeField(auto_now_add=True)
    
    def reset(self):
        """Reseta banca virtual"""
        self.balance = self.initial
        self.last_reset = timezone.now()
        self.save()
        
        # Arquiva apostas antigas
        self.user.virtual_bets.update(archived=True)
    
    def get_performance_vs_ai(self):
        """Compara performance do usuário vs IA"""
        
        # Stats do usuário
        user_bets = self.user.virtual_bets.filter(archived=False, result__in=['won', 'lost'])
        user_stats = {
            'total': user_bets.count(),
            'won': user_bets.filter(result='won').count(),
            'roi': self._calculate_roi(user_bets)
        }
        
        # Stats da IA
        ai_multiple_stats = DailyBet.objects.filter(
            bet_type='multiple',
            status__in=['won', 'lost']
        ).aggregate(
            total=Count('id'),
            won=Count('id', filter=Q(status='won'))
        )
        
        ai_value_stats = DailyBet.objects.filter(
            bet_type='value',
            status__in=['won', 'lost']
        ).aggregate(
            total=Count('id'),
            won=Count('id', filter=Q(status='won'))
        )
        
        return {
            'user': user_stats,
            'ai_multiple': ai_multiple_stats,
            'ai_value': ai_value_stats,
            'insights': self._generate_insights(user_bets)
        }
    
    def _generate_insights(self, bets):
        """Gera insights personalizados"""
        
        # Análise de mercados mais apostados
        market_breakdown = bets.values('market').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Stake médio
        avg_stake = bets.aggregate(Avg('amount'))['amount__avg']
        avg_stake_pct = (float(avg_stake) / float(self.initial)) * 100
        
        insights = []
        
        # Diversificação
        if market_breakdown[0]['count'] / bets.count() > 0.7:
            insights.append({
                'type': 'warning',
                'message': f"{(market_breakdown[0]['count'] / bets.count() * 100):.0f}% das suas apostas são em {market_breakdown[0]['market']}",
                'suggestion': 'Tente diversificar em outros mercados'
            })
        
        # Stake management
        if avg_stake_pct > 4:
            insights.append({
                'type': 'warning',
                'message': f'Seu stake médio é {avg_stake_pct:.1f}% da banca',
                'suggestion': 'Ideal: 2-3% por aposta'
            })
        
        return insights

class VirtualBet(models.Model):
    """Aposta virtual (simulação)"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='virtual_bets')
    daily_bet = models.ForeignKey('analysis.DailyBet', on_delete=models.SET_NULL, null=True)
    
    market = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    odd = models.DecimalField(max_digits=5, decimal_places=2)
    
    result = models.CharField(max_length=20, choices=[
        ('pending', 'Pendente'),
        ('won', 'Vencida'),
        ('lost', 'Perdida')
    ])
    
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    archived = models.BooleanField(default=False)
    
    placed_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(null=True)
```

### **Por Que Funciona**
- 🎓 **Zero Risco**: Aprende sem perder dinheiro
- 📊 **Autoconhecimento**: Descobre vieses e erros
- 🎯 **Conversão**: Usuários que simulam → depois assinam PRO
- 🏆 **Gamificação**: Competir com IA é divertido

### **Esforço de Implementação**
- Backend: 6 horas (models, comparação com IA)
- Frontend: 4 horas (dashboard de simulação)
- **Total: 10 horas**

---

## 8. 🔬 API Pública para Devs

### **Status:** ⚠️ Complexidade Média | 🚀 Ecosistema

### **Conceito**
Disponibilizar API pública para desenvolvedores criarem apps/bots baseados nas análises.

### **O Que Implementar**

#### **8.1 Endpoints Públicos**

```python
# API Routes
GET /api/v1/matches/today/predictions
GET /api/v1/daily-bets/
GET /api/v1/stats/accuracy/
GET /api/v1/leagues/
GET /api/v1/odds/{match_id}/

# Rate Limiting
Free Tier:    100 calls/day
Pro Tier:     1,000 calls/day
Premium Tier: 10,000 calls/day
```

#### **8.2 Exemplo de Uso**

```javascript
// Bot do Telegram criado por dev externo
const axios = require('axios');

async function sendDailyBets() {
  const response = await axios.get('https://api.betinsight.com/v1/daily-bets/', {
    headers: {
      'Authorization': 'Bearer YOUR_API_KEY'
    }
  });
  
  const { multiple_tickets, value_bets } = response.data;
  
  // Envia para canal do Telegram
  telegram.sendMessage(`
    🎯 Bilhetes de Hoje - Bet Insight

    📋 Bilhete 3x (Odd ${multiple_tickets[0].total_odd}):
    ${multiple_tickets[0].selections.map(s => `• ${s.match} - ${s.pick}`).join('\n')}

    ⚡ Top Value Bet:
    ${value_bets[0].match} - ${value_bets[0].market}
    Odd: ${value_bets[0].odd} | EV: +${value_bets[0].expected_value}%
  `);
}
```

#### **8.3 Marketplace de Estratégias**

```
┌────────────────────────────────────────────────┐
│ 🛒 Marketplace de Estratégias                  │
├────────────────────────────────────────────────┤
│                                                │
│ 🔥 Mais Vendidas:                              │
│                                                │
│ 1. "Value Hunter Pro" by @JoãoSilva           │
│    ROI: +45% (últimos 90d)                    │
│    Preço: 50 MZN/mês                          │
│    [Testar Grátis] [Comprar]                  │
│                                                │
│ 2. "Under Master" by @MariaCosta              │
│    ROI: +38% (últimos 90d)                    │
│    Preço: 40 MZN/mês                          │
│    [Testar Grátis] [Comprar]                  │
│                                                │
│ 💡 Crie sua própria estratégia e venda!       │
│    [Criar Estratégia]                         │
└────────────────────────────────────────────────┘
```

### **Por Que Funciona**
- 🌐 **Ecosistema**: Comunidade cria features que você não pensou
- 💰 **Receita Adicional**: API Premium ($10-50/mês)
- 🚀 **Viralidade**: Bots/apps de terceiros divulgam seu produto
- 🏆 **Network Effect**: Mais apps → mais usuários → mais valor

### **Esforço de Implementação**
- Backend: 12 horas (API versioning, auth, rate limiting)
- Docs: 4 horas (documentação completa)
- **Total: 16 horas**

---

## 9. 📊 Insights Exclusivos por Liga

### **Status:** ✅ Tecnicamente Seguro | 📈 Conteúdo Premium

### **Conceito**
Relatórios semanais automáticos com tendências e padrões de cada liga.

### **O Que Implementar**

#### **9.1 Weekly Intelligence Report**

```markdown
# 📊 Championship Intelligence Report
**Semana 30** | 27 Jan - 2 Fev 2026

## 🔥 Tendências da Semana

### Resultados Gerais
- **Home Win**: 68% (vs média temporada: 58%)
- **Draw**: 18% (vs média: 24%)
- **Away Win**: 14% (vs média: 18%)

### Gols
- **Over 2.5**: 32% (liga muito defensiva!)
- **BTTS**: 48% (abaixo da média: 55%)
- **Média de gols**: 2.1/jogo

### Surpresas
- ⚡ **Derby County** 4 vitórias seguidas (de rebaixado a playoff!)
- 📉 **Leeds United** apenas 2 pontos em 5 jogos

---

## 💎 Value Spots Identificados

### 1. Under 2.5 em jogos mid-table
- **EV Médio**: +12%
- **Accuracy**: 74% (17/23 jogos)
- **Razão**: Times brigam por nada, jogos travados

### 2. Away wins em relegation battles
- **EV Médio**: +8%
- **Accuracy**: 67% (8/12 jogos)
- **Razão**: Desespero do visitante, casa pressionada

### 3. BTTS=No em jogos do Top 6
- **EV Médio**: +6%
- **Accuracy**: 71% (10/14 jogos)
- **Razão**: Defesas sólidas, ataque funcionando

---

## ⚠️ Evite

### ❌ Apostas em favoritos absolutos
- Odds muito baixas (média 1.35)
- Sem value mesmo com 75%+ probabilidade

### ❌ BTTS em jogos mid-table
- Apenas 38% accuracy (vs esperado 55%)
- Jogos muito travados

---

## 📅 Próxima Semana - Jogos Chave

### Sábado 1/Fev
- **Leeds vs Sheffield Wed** - Derby local, Over 2.5 @ 2.1 (value!)
- **Derby vs Burnley** - Derby em forma, 1X @ 1.45

### Domingo 2/Fev
- **Middlesbrough vs Sunderland** - BTTS @ 1.75 (valor!)

---

📧 Quer receber este relatório toda semana?  
[Assinar Newsletter PRO]
```

#### **Implementação Técnica**

```python
# backend/apps/reports/services.py
class LeagueReportGenerator:
    
    @staticmethod
    def generate_weekly_report(league_id, start_date, end_date):
        """Gera relatório semanal de uma liga"""
        
        matches = Match.objects.filter(
            league_id=league_id,
            fixture_date__gte=start_date,
            fixture_date__lte=end_date,
            status='FT'
        )
        
        # Análise geral
        stats = {
            'total_matches': matches.count(),
            'home_wins': matches.filter(winner='home').count(),
            'draws': matches.filter(winner='draw').count(),
            'away_wins': matches.filter(winner='away').count(),
        }
        
        # Análise de gols
        total_goals = sum(m.home_score + m.away_score for m in matches)
        over_25 = matches.filter(
            home_score__plus=F('away_score__gt=3')
        ).count()
        
        # Value spots (análise de DailyBets)
        value_analysis = cls._analyze_value_spots(league_id, start_date, end_date)
        
        # Tendências
        trends = cls._identify_trends(matches)
        
        # Gera markdown
        report = cls._generate_markdown({
            'league': League.objects.get(id=league_id),
            'period': f"{start_date} - {end_date}",
            'stats': stats,
            'trends': trends,
            'value_spots': value_analysis,
            'key_matches': cls._get_key_matches_next_week(league_id)
        })
        
        return report
    
    @staticmethod
    def _analyze_value_spots(league_id, start_date, end_date):
        """Identifica patterns de value"""
        
        bets = DailyBet.objects.filter(
            match__league_id=league_id,
            date__gte=start_date,
            date__lte=end_date,
            expected_value__gte=5
        )
        
        # Agrupa por mercado
        by_market = {}
        for bet in bets:
            market = bet.market
            if market not in by_market:
                by_market[market] = {'total': 0, 'won': 0, 'ev_sum': 0}
            
            by_market[market]['total'] += 1
            if bet.status == 'won':
                by_market[market]['won'] += 1
            by_market[market]['ev_sum'] += bet.expected_value
        
        # Calcula accuracy e EV médio
        value_spots = []
        for market, data in by_market.items():
            if data['total'] >= 5:  # Mínimo 5 apostas
                value_spots.append({
                    'market': market,
                    'accuracy': (data['won'] / data['total']) * 100,
                    'avg_ev': data['ev_sum'] / data['total'],
                    'count': data['total']
                })
        
        return sorted(value_spots, key=lambda x: x['avg_ev'], reverse=True)

# Celery task semanal
@periodic_task(crontab(day_of_week=1, hour=8))
def generate_weekly_reports():
    """Gera relatórios semanais para todas as ligas"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    leagues = [40, 39, 61, 78]  # Championship, Ligue 1, etc
    
    for league_id in leagues:
        report = LeagueReportGenerator.generate_weekly_report(
            league_id, start_date, end_date
        )
        
        # Salva relatório
        WeeklyReport.objects.create(
            league_id=league_id,
            start_date=start_date,
            end_date=end_date,
            content=report
        )
        
        # Envia por email para assinantes PRO
        subscribers = User.objects.filter(
            subscription__plan='pro',
            subscription__is_active=True
        )
        
        send_email_to_users(
            users=subscribers,
            subject=f"Championship Report - Semana {start_date.isocalendar()[1]}",
            html_content=markdown_to_html(report)
        )
        
        logger.info(f"📊 Weekly report generated for league {league_id}")
```

### **Por Que Funciona**
- 📧 **Email Marketing**: Usuários voltam semanalmente
- 🎓 **Educação**: Entendem padrões de cada liga
- 💎 **Premium**: Conteúdo exclusivo para PRO
- 🏆 **Autoridade**: Posiciona como expert em análise

### **Esforço de Implementação**
- Backend: 8 horas (análise, geração de report)
- Email: 2 horas (templates HTML)
- **Total: 10 horas**

---

## 10. 🏪 Comparação com Bookmakers

### **Status:** ⚠️ Requer Múltiplas APIs | 💰 Alto Valor

### **Conceito**
Integrar múltiplas casas de apostas e mostrar qual paga melhor odd para cada aposta.

### **O Que Implementar**

#### **10.1 Odds Comparison**

```
┌────────────────────────────────────────────────────┐
│ Bristol vs Derby - Over 2.5                        │
├────────────────────────────────────────────────────┤
│                                                    │
│ 🎯 Nossa Recomendação: ✅ APOSTAR                 │
│ Fair Odd: 1.89 | EV: +11%                         │
│                                                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                    │
│ 💰 Melhores Odds Disponíveis:                     │
│                                                    │
│ 🥇 Betano:     2.15 ⭐ (+2.4% vs média)           │
│    [Apostar na Betano]                            │
│                                                    │
│ 🥈 Bet365:     2.10 (+0.0% vs média)              │
│    [Apostar na Bet365]                            │
│                                                    │
│ 🥉 Betfair:    2.08 (-1.0% vs média)              │
│    [Apostar na Betfair]                           │
│                                                    │
│    1xBet:      2.05 (-2.4% vs média)              │
│                                                    │
│    22Bet:      2.03 (-3.3% vs média)              │
│                                                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                    │
│ 💡 Apostar na Betano maximiza seu lucro em 2.4%! │
│                                                    │
│ 📊 Se apostar 100 MZN:                            │
│ • Betano: 215 MZN (lucro: 115 MZN)                │
│ • 22Bet:  203 MZN (lucro: 103 MZN)                │
│ • Diferença: +12 MZN! 💰                          │
└────────────────────────────────────────────────────┘
```

#### **Implementação Técnica**

```python
# backend/apps/bookmakers/models.py
class Bookmaker(models.Model):
    name = models.CharField(max_length=100)
    logo = models.URLField()
    affiliate_link = models.URLField()
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2)  # %
    
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)

class BookmakerOdds(models.Model):
    bookmaker = models.ForeignKey(Bookmaker, on_delete=models.CASCADE)
    match = models.ForeignKey('matches.Match', on_delete=models.CASCADE)
    market = models.CharField(max_length=50)
    
    odd = models.DecimalField(max_digits=5, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

# backend/apps/bookmakers/services.py
class OddsComparator:
    
    @staticmethod
    def get_best_odds(match, market):
        """Retorna melhores odds de todos os bookmakers"""
        
        odds = BookmakerOdds.objects.filter(
            match=match,
            market=market,
            bookmaker__is_active=True
        ).select_related('bookmaker').order_by('-odd')
        
        if not odds.exists():
            return None
        
        # Calcula odd média
        avg_odd = odds.aggregate(Avg('odd'))['odd__avg']
        
        # Formata resultado
        comparison = []
        for i, odd in enumerate(odds):
            diff_pct = ((float(odd.odd) - avg_odd) / avg_odd) * 100
            
            comparison.append({
                'rank': i + 1,
                'bookmaker': odd.bookmaker.name,
                'logo': odd.bookmaker.logo,
                'odd': float(odd.odd),
                'diff_from_avg': round(diff_pct, 1),
                'affiliate_link': odd.bookmaker.affiliate_link,
                'is_best': i == 0
            })
        
        return {
            'best_odd': float(odds.first().odd),
            'average_odd': float(avg_odd),
            'comparison': comparison,
            'profit_difference': cls._calculate_profit_diff(comparison, stake=100)
        }
    
    @staticmethod
    def _calculate_profit_diff(comparison, stake=100):
        """Calcula diferença de lucro entre melhor e pior odd"""
        
        best = comparison[0]['odd']
        worst = comparison[-1]['odd']
        
        return {
            'stake': stake,
            'best_return': stake * best,
            'worst_return': stake * worst,
            'difference': stake * (best - worst)
        }

# Celery task para atualizar odds
@periodic_task(run_every=timedelta(hours=1))
def update_bookmaker_odds():
    """Atualiza odds de todos os bookmakers"""
    
    matches = Match.objects.filter(
        status='NS',
        fixture_date__gte=timezone.now(),
        fixture_date__lte=timezone.now() + timedelta(days=2)
    )
    
    for match in matches:
        for bookmaker in Bookmaker.objects.filter(is_active=True):
            try:
                # API específica de cada bookmaker
                odds = fetch_bookmaker_odds(bookmaker, match)
                
                for market, odd_value in odds.items():
                    BookmakerOdds.objects.update_or_create(
                        bookmaker=bookmaker,
                        match=match,
                        market=market,
                        defaults={'odd': odd_value}
                    )
                
            except Exception as e:
                logger.error(f"Error fetching odds from {bookmaker.name}: {e}")
```

### **Por Que Funciona**
- 💰 **Maximiza Lucro**: +2-5% por odd melhor acumula
- 🎯 **Receita de Afiliação**: Comissão de 20-40% das casas
- 🏆 **Diferenciação**: Competitors mostram só 1 bookmaker
- 📊 **Transparência**: Usuário vê todas as opções

### **Esforço de Implementação**
- Backend: 16 horas (integração múltiplas APIs)
- Frontend: 4 horas (UI de comparação)
- **Total: 20 horas**

---

## 📊 Resumo: Top 5 Prioridades

### **Implementar Nesta Ordem**

| # | Feature | Impacto | Esforço | ROI | Status |
|---|---------|---------|---------|-----|--------|
| **1** | **Transparência Total** | 🔥🔥🔥 | 4h | ⭐⭐⭐⭐⭐ 10/10 | ✅ Pronto backend |
| **2** | **IA Explicável** | 🔥🔥🔥 | 6h | ⭐⭐⭐⭐⭐ 9/10 | ✅ Dados disponíveis |
| **3** | **Bankroll Inteligente** | 🔥🔥 | 8h | ⭐⭐⭐⭐ 8/10 | 🟡 Requer models |
| **4** | **Notificações Push** | 🔥🔥 | 12h | ⭐⭐⭐⭐ 8/10 | 🔴 Requer Firebase |
| **5** | **Modo Simulação** | 🔥 | 10h | ⭐⭐⭐ 7/10 | 🟡 Médio |

---

## ⚡ Quick Wins (Implementar Hoje - 2 horas total)

### **1. Public Stats Dashboard** (30 minutos)

```python
# backend/apps/analysis/views.py
# APENAS MUDAR PERMISSION!

class DailyBetViewSet(viewsets.ReadOnlyModelViewSet):
    # Antes: permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  # ← Já é público!
    
    # Endpoint já existe e funciona!
    @action(detail=False, methods=['get'], url_path='stats')
    def public_stats(self, request):
        # Retorna accuracy real do sistema
        ...
```

**Frontend:**
```jsx
// Criar página /public-stats
const PublicStatsPage = () => {
  const { data } = useFetch('/api/daily-bets/stats/');
  
  return (
    <div>
      <h1>📊 Nossa Performance Real</h1>
      <StatCard title="Win Rate (30d)" value={data.last_7_days.win_rate} />
      <StatCard title="ROI Total" value={data.all_time.roi} />
    </div>
  );
};
```

---

### **2. Feature Importance Badge** (1 hora)

```python
# backend/apps/analysis/models.py (DailyBet)
def get_top_features(self):
    """Extrai top 3 features que influenciaram aposta"""
    
    # Parse do reasoning
    reasoning = self.reasoning or {}
    
    # Mock (implementação completa depois)
    return [
        "Força Ofensiva Casa: 9/10",
        "H2H Favorável: 8/10",
        "Forma Recente: 7/10"
    ]

# Admin
class DailyBetAdmin(admin.ModelAdmin):
    def features_summary(self, obj):
        return "<br>".join(obj.get_top_features())
```

---

### **3. Badge "Nova Feature"** (5 minutos)

```jsx
// frontend/components/Header.jsx
<Link to="/daily-bets">
  Bilhetes do Dia <span className="badge-new">🆕</span>
</Link>

// CSS
.badge-new {
  background: linear-gradient(45deg, #ff6b6b, #ff8e53);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  color: white;
  font-weight: bold;
  margin-left: 4px;
}
```

---

## 🎯 Roadmap de 30 Dias

### **Semana 1: Quick Wins + Transparência**
- ✅ Public Stats Dashboard
- ✅ Badge "Novo"
- ✅ Feature Importance (basic)

### **Semana 2: IA Explicável**
- Reasoning Breakdown completo
- Frontend componentes visuais
- Ensemble explanation

### **Semana 3: Bankroll + Simulação**
- Kelly Criterion implementação
- Virtual bankroll
- Comparação user vs IA

### **Semana 4: Notificações + Polish**
- Firebase setup
- Push notifications
- Testes e refinamentos

---

## 💡 Dicas de Implementação

### **1. Começe Pequeno**
- Implemente MVP de cada feature primeiro
- Refine baseado em feedback real

### **2. Meça Tudo**
- Adicione analytics em cada feature
- A/B teste quando possível

### **3. Comunique Valor**
- Cada feature precisa de tutorial/onboarding
- Mostre benefício claro para o usuário

### **4. Priorize Mobile**
- 70%+ dos usuários estão no celular
- Mobile-first em tudo

---

## 📚 Recursos Necessários

### **Backend**
- Firebase Admin SDK (notificações)
- Celery + Redis (já tem!)
- PostgreSQL (já tem!)

### **Frontend**
- Chart.js ou Recharts (gráficos)
- React Query (cache)
- PWA notifications API

### **Infraestrutura**
- Firebase Cloud Messaging (push)
- Email service (SendGrid/Mailgun)
- CDN para assets

---

## 🎉 Conclusão

Essas 10 diferenciações competitivas transformam o Bet Insight de "mais um sistema de análise" para **a plataforma de apostas mais transparente e educacional do mercado**.

**Único no mercado:**
- ✅ Transparência total (accuracy público)
- ✅ IA explicável (usuário entende o porquê)
- ✅ Bankroll management (Kelly Criterion)
- ✅ Timing de odds (quando apostar)
- ✅ Simulação vs IA (aprendizado zero risco)

**Próximos Passos:**
1. Implementar Quick Wins (2h)
2. Escolher 2-3 features para Fase 1
3. Medir impacto e iterar

---

**Criado em:** 30 Janeiro 2026  
**Última Atualização:** 30 Janeiro 2026  
**Versão:** 1.0
