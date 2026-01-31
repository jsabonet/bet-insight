# 🎯 Guia de Implementação - Sistema de Bilhetes Automáticos

## ✅ IMPLEMENTAÇÃO CONCLUÍDA

Data: 30/01/2026

### Componentes Implementados

1. ✅ **Modelo `DailyBet`** ([models.py](backend/apps/analysis/models.py))
   - Campos para bilhetes múltiplos e value bets
   - Sistema de validação automática de resultados
   - Cálculo de ROI
   - Status tracking (pending, won, lost, partial, cancelled)

2. ✅ **Service `DailyBetGenerator`** ([daily_bet_generator.py](backend/apps/analysis/services/daily_bet_generator.py))
   - Integração com HybridAnalysisOrchestrator existente
   - Geração de bilhetes 3x, 5x, 7x
   - Seleção de top 10 value bets
   - Filtros configuráveis (EV, probabilidade, odds)
   - Cálculo de stake (Kelly Criterion simplificado)

3. ✅ **Celery Tasks** ([tasks.py](backend/apps/analysis/tasks.py))
   - `generate_daily_bets` - Gera apostas diariamente às 06:00 UTC
   - `validate_daily_bets` - Valida resultados a cada 1 hora
   - `cleanup_old_daily_bets` - Remove apostas antigas (semanal)

4. ✅ **Serializers** ([serializers.py](backend/apps/analysis/serializers.py))
   - `DailyBetSerializer` - Completo (retrieve)
   - `DailyBetListSerializer` - Simplificado (list)

5. ✅ **API ViewSet** ([views.py](backend/apps/analysis/views.py))
   - Endpoints públicos (AllowAny)
   - `/api/daily-bets/today/` - Apostas de hoje
   - `/api/daily-bets/history/` - Histórico com stats
   - `/api/daily-bets/stats/` - Estatísticas agregadas
   - Cálculo automático de ROI, win rate, etc.

6. ✅ **Celery Config** ([config/celery.py](backend/config/celery.py))
   - Beat schedule configurado
   - Timeouts e limits definidos
   - Auto-discovery de tasks

7. ✅ **Admin Interface** ([admin.py](backend/apps/analysis/admin.py))
   - Admin customizado com badges coloridos
   - Visualização de seleções em tabela
   - Estatísticas inline (ROI, EV, etc.)
   - Proteção contra deleção de apostas validadas

8. ✅ **URLs** ([urls.py](backend/config/urls.py))
   - Router registrado: `daily-bets`

9. ✅ **Migration**
   - `0003_add_daily_bet_model.py` criada

---

## 🚀 Como Usar

### 1. Aplicar Migration

```bash
cd backend
python manage.py migrate analysis
```

### 2. Iniciar Celery Worker (Terminal 1)

```bash
cd backend
celery -A config worker --loglevel=info --pool=solo
```

### 3. Iniciar Celery Beat (Terminal 2)

```bash
cd backend
celery -A config beat --loglevel=info
```

### 4. Testar Geração Manual (Opcional)

```python
# Django shell
python manage.py shell

from apps.analysis.tasks import generate_daily_bets
result = generate_daily_bets.delay()  # Assíncrono
# ou
result = generate_daily_bets()  # Síncrono (para teste)
```

### 5. Verificar Apostas Geradas

#### Via Admin:
- Acesse: `http://localhost:8000/admin/analysis/dailybet/`

#### Via API:
```bash
# Apostas de hoje
curl http://localhost:8000/api/daily-bets/today/

# Histórico (últimos 30 dias)
curl http://localhost:8000/api/daily-bets/history/?days=30

# Estatísticas públicas
curl http://localhost:8000/api/daily-bets/stats/
```

---

## 📅 Schedule Automático

### Tasks Configuradas (Celery Beat)

1. **Gerar Bilhetes Diários**
   - Task: `analysis.generate_daily_bets`
   - Schedule: Diário às **06:00 UTC** (09:00 Maputo)
   - Função: Analisa todas partidas do dia, gera bilhetes e value bets

2. **Validar Resultados**
   - Task: `analysis.validate_daily_bets`
   - Schedule: **A cada 1 hora**
   - Função: Verifica jogos finalizados, atualiza status das apostas

3. **Cleanup**
   - Task: `analysis.cleanup_old_daily_bets`
   - Schedule: **Domingo às 03:00 UTC** (semanal)
   - Função: Remove apostas validadas com mais de 90 dias

---

## 🎨 Endpoints da API

### GET `/api/daily-bets/today/`

**Resposta:**
```json
{
  "date": "2026-01-30",
  "multiple_tickets": [
    {
      "id": 1,
      "bet_type": "multiple",
      "selections": [
        {
          "match": "Man Utd vs Liverpool",
          "pick": "Man Utd",
          "market": "home_win",
          "probability": 0.65,
          "odd": 1.45,
          "ev_pct": 6.2
        },
        // ... mais 2-6 apostas
      ],
      "total_odd": 5.6,
      "combined_probability": 0.18,
      "expected_value": -3.2,
      "suggested_stake": 1.5,
      "status": "pending"
    }
  ],
  "value_bets": [
    {
      "id": 2,
      "bet_type": "value",
      "selections": [
        {
          "match": "Barcelona vs Real Madrid",
          "pick": "Under 2.5",
          "market": "under_2.5",
          "probability": 0.52,
          "odd": 2.10,
          "fair_odd": 1.92,
          "ev_pct": 9.4
        }
      ],
      "total_odd": 2.10,
      "expected_value": 9.4,
      "suggested_stake": 2.0,
      "status": "pending"
    }
  ],
  "stats": {
    "total_matches": 45,
    "total_bets": 13,
    "multiple_count": 3,
    "value_count": 10,
    "avg_multiple_odd": 5.6,
    "avg_value_ev": 12.3
  }
}
```

### GET `/api/daily-bets/history/?days=30`

**Resposta:**
```json
{
  "period": "Últimos 30 dias",
  "overall": {
    "total": 150,
    "won": 68,
    "lost": 72,
    "win_rate": 45.3,
    "roi": -5.2,
    "avg_odd": 2.8
  },
  "multiple_tickets": {
    "total": 90,
    "won": 18,
    "win_rate": 20.0,
    "roi": -8.5
  },
  "value_bets": {
    "total": 60,
    "won": 32,
    "win_rate": 53.3,
    "roi": 8.7
  },
  "recent_bets": [...]
}
```

### GET `/api/daily-bets/stats/`

Estatísticas agregadas (all-time, 7 dias, 30 dias, por tipo de bilhete).

---

## ⚙️ Configurações

### Filtros do DailyBetGenerator

Edite `backend/apps/analysis/services/daily_bet_generator.py`:

```python
class DailyBetGenerator:
    # Value Bets
    MIN_VALUE_EV = 5.0  # EV mínimo +5%
    MIN_VALUE_PROBABILITY = 0.25  # Prob mínima 25%
    MAX_VALUE_BETS = 10  # Máximo de value bets por dia
    
    # Bilhetes Múltiplos
    MIN_MULTIPLE_PROBABILITY = 0.50  # Cada aposta min 50%
    MIN_COMBINED_PROBABILITY_3X = 0.15  # Bilhete 3x: 15%
    MIN_COMBINED_PROBABILITY_5X = 0.08  # Bilhete 5x: 8%
    MIN_COMBINED_PROBABILITY_7X = 0.04  # Bilhete 7x: 4%
    
    MIN_TICKET_ODD = 2.0
    MAX_TICKET_ODD = 20.0
```

### Horários do Celery Beat

Edite `backend/config/celery.py`:

```python
app.conf.beat_schedule = {
    'generate-daily-bets': {
        'task': 'analysis.generate_daily_bets',
        'schedule': crontab(hour=6, minute=0),  # Altere aqui
    },
    # ...
}
```

---

## 🧪 Testes

### 1. Testar Geração Manual

```python
from apps.analysis.services.daily_bet_generator import DailyBetGenerator

generator = DailyBetGenerator()
results = generator.generate_for_today()

print(f"Partidas analisadas: {results['matches_analyzed']}")
print(f"Bilhetes criados: {results['multiple_count']}")
print(f"Value bets criadas: {results['value_count']}")
```

### 2. Testar Validação

```python
from apps.analysis.models import DailyBet

# Simular validação de uma aposta
bet = DailyBet.objects.first()
bet.validate_result()

print(f"Status: {bet.get_status_display()}")
print(f"ROI: {bet.get_roi():.1f}%")
```

### 3. Verificar Logs do Celery

```bash
# Logs detalhados estão em stdout do worker
tail -f celery_worker.log
```

---

## 📊 Consumo de API

### Estimativa de Requisições

**Por partida analisada:**
- Sem cache: 11 requisições
- Com cache (90% hit): ~1.1 requisições

**Exemplo real (120 partidas/dia):**
- Requisições: 120 × 1.1 = **132 requisições**
- % do limite: 132 / 7500 = **1.76%**

**Margem de segurança: 98.24%** ✅

---

## 🐛 Troubleshooting

### Problema: Tasks não executam

**Solução:**
1. Verificar se Redis está rodando:
   ```bash
   redis-cli ping  # Deve retornar PONG
   ```

2. Verificar se Celery Worker e Beat estão ativos:
   ```bash
   ps aux | grep celery
   ```

3. Verificar logs:
   ```bash
   celery -A config inspect active
   ```

### Problema: Apostas não validam

**Solução:**
1. Verificar se jogos têm status 'finished' no banco
2. Verificar se `match.home_score` e `away_score` estão populados
3. Executar validação manual:
   ```python
   from apps.analysis.tasks import validate_daily_bets
   validate_daily_bets()
   ```

### Problema: Migration falha

**Solução:**
```bash
# Reverter migration
python manage.py migrate analysis 0002

# Deletar migration file
rm apps/analysis/migrations/0003_add_daily_bet_model.py

# Recriar
python manage.py makemigrations analysis --name add_daily_bet_model
python manage.py migrate
```

---

## 🎯 Próximos Passos (Opcional)

### Frontend (React)

Criar componente `DailyBetsPage.jsx`:

```jsx
import { useEffect, useState } from 'react';
import api from '../services/api';

function DailyBetsPage() {
  const [bets, setBets] = useState(null);
  
  useEffect(() => {
    api.get('/daily-bets/today/').then(res => setBets(res.data));
  }, []);
  
  return (
    <div>
      <h1>Bilhetes do Dia</h1>
      {bets?.multiple_tickets.map(ticket => (
        <TicketCard key={ticket.id} ticket={ticket} />
      ))}
      
      <h2>Value Bets</h2>
      {bets?.value_bets.map(bet => (
        <ValueBetCard key={bet.id} bet={bet} />
      ))}
    </div>
  );
}
```

### Notificações Push

Enviar notificação quando novos bilhetes são gerados:

```python
# Em tasks.py, após geração
from apps.notifications.service import NotificationService

NotificationService.send_push(
    title="Novos Bilhetes Disponíveis!",
    body=f"{results['multiple_count']} bilhetes e {results['value_count']} value bets",
    data={'url': '/daily-bets'}
)
```

### Compartilhamento Social

Gerar imagem com bilhetes para compartilhar:

```python
# apps/analysis/utils/image_generator.py
from PIL import Image, ImageDraw

def generate_ticket_image(daily_bet):
    # Criar imagem com apostas do bilhete
    # Retornar URL da imagem
    pass
```

---

## 📝 Checklist de Deploy

- [ ] Migration aplicada: `python manage.py migrate`
- [ ] Redis configurado e rodando
- [ ] Celery Worker iniciado: `celery -A config worker`
- [ ] Celery Beat iniciado: `celery -A config beat`
- [ ] Verificar timezone correto: `Africa/Maputo`
- [ ] Testar geração manual (1 dia)
- [ ] Monitorar logs por 48h
- [ ] Ajustar filtros baseado em resultados
- [ ] Criar documentação de usuário
- [ ] Lançar em produção

---

## 📞 Suporte

Em caso de dúvidas:
1. Verificar logs do Celery
2. Consultar [IMPLEMENTACAO_BILHETES_AUTOMATICOS.md](IMPLEMENTACAO_BILHETES_AUTOMATICOS.md)
3. Revisar código fonte nos links acima

**Sistema implementado com sucesso! 🎉**
