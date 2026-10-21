# 📋 Sistema de Planos e Assinaturas
## Bet Insight Mozambique

## 🎯 Planos Disponíveis

### 1. **Freemium** (Gratuito)
- **Preço**: 0 MZN
- **Análises diárias**: 5
- **Duração**: Permanente
- **Recursos**:
  - 5 análises por dia
  - Acesso básico a estatísticas
  - Previsões com IA
  - Notificações básicas

### 2. **Premium Mensal**
- **Preço**: 499 MZN/mês
- **Análises diárias**: 50
- **Duração**: 30 dias
- **Recursos**:
  - 50 análises por dia
  - Acesso completo a estatísticas
  - Análises detalhadas com IA
  - Notificações em tempo real
  - Histórico completo de análises
  - Suporte prioritário

### 3. **Premium Trimestral** ⭐ (Mais Popular)
- **Preço**: 1.299 MZN (3 meses)
- **Análises diárias**: 100
- **Duração**: 90 dias
- **Economia**: 198 MZN (13% de desconto vs mensal)
- **Recursos**:
  - 100 análises por dia
  - Todos os recursos do mensal
  - Insights exclusivos
  - Melhor custo-benefício

### 4. **Premium Anual**
- **Preço**: 4.499 MZN (12 meses)
- **Análises diárias**: 150
- **Duração**: 365 dias
- **Economia**: 1.489 MZN (25% de desconto vs mensal)
- **Recursos**:
  - 150 análises por dia
  - Todos os recursos do mensal
  - Insights exclusivos
  - Acesso antecipado a novos recursos
  - Suporte prioritário 24/7

---

## 🛠️ Arquitetura Implementada

### Arquivos Criados/Modificados

#### 1. **`apps/subscriptions/plan_config.py`** (NOVO)
Configuração centralizada de planos:
- Definição de todos os planos (PLANS dict)
- Funções auxiliares: `get_plan()`, `get_active_plans()`, `get_premium_plans()`
- Limites de análises por plano
- Features e descrições

#### 2. **`apps/subscriptions/models.py`** (MODIFICADO)
- Adicionado campo `plan_slug` ao modelo Subscription
- Atualizado `PLAN_CHOICES` com freemium
- Métodos: `get_daily_limit()`, `is_premium()`
- Suporte para planos sem expiração (freemium)

#### 3. **`apps/users/models.py`** (MODIFICADO)
- Método `can_analyze()` agora busca assinatura ativa
- Usa limite do plano da assinatura ao invés de constantes
- Fallback para freemium (5 análises) se sem assinatura

#### 4. **`apps/subscriptions/serializers.py`** (MODIFICADO)
- Novo `PlanSerializer` para retornar configuração de planos
- `SubscriptionSerializer` com `daily_limit` e `plan_details`

#### 5. **`apps/subscriptions/plan_views.py`** (NOVO)
Views para gerenciar planos:
- `list_plans()` - Lista todos os planos (público)
- `list_premium_plans()` - Lista apenas planos pagos (público)
- `get_plan_details()` - Detalhes de um plano específico (público)
- `my_subscription()` - Assinatura ativa do usuário (autenticado)
- `cancel_subscription()` - Cancelar assinatura (autenticado)
- `subscription_history()` - Histórico (autenticado)

#### 6. **`apps/subscriptions/urls.py`** (NOVO)
Rotas para endpoints de planos:
```
GET /api/subscriptions/plans/
GET /api/subscriptions/plans/premium/
GET /api/subscriptions/plans/<slug>/
GET /api/subscriptions/my-subscription/
POST /api/subscriptions/cancel/
GET /api/subscriptions/history/
```

#### 7. **Migração**: `0002_subscription_plan_slug_*.py`
- Adiciona campo `plan_slug` ao modelo Subscription
- Atualiza choices de plan e status

---

## 🔌 Endpoints API

### Públicos (sem autenticação)

#### `GET /api/subscriptions/plans/`
Lista todos os planos disponíveis
```json
[
  {
    "slug": "freemium",
    "name": "Freemium",
    "price": 0,
    "daily_analysis_limit": 5,
    "duration_days": null,
    "features": ["5 análises por dia", ...],
    "description": "Plano gratuito...",
    "color": "gray",
    "popular": false
  },
  ...
]
```

#### `GET /api/subscriptions/plans/premium/`
Lista apenas planos premium (pagos)

#### `GET /api/subscriptions/plans/{slug}/`
Detalhes de um plano específico

### Autenticados

#### `GET /api/subscriptions/my-subscription/`
Retorna assinatura ativa do usuário
```json
{
  "id": 1,
  "plan": "monthly",
  "plan_slug": "monthly",
  "status": "active",
  "daily_limit": 50,
  "is_active": true,
  "plan_details": {
    "name": "Premium Mensal",
    "price": 499,
    "features": [...],
    "color": "primary"
  }
}
```

#### `POST /api/subscriptions/cancel/`
Cancela assinatura ativa

#### `GET /api/subscriptions/history/`
Histórico de assinaturas do usuário

---

## 📊 Lógica de Limites

### Como funciona:

1. **Usuário sem assinatura**: Automaticamente freemium (5 análises/dia)
2. **Usuário com assinatura ativa**: Usa limite do plano da assinatura
3. **Reset diário**: Contador zerado todo dia às 00:00
4. **Verificação**: Método `User.can_analyze()` verifica se pode fazer análise

### Código exemplo:
```python
# Verificar se pode analisar
if request.user.can_analyze():
    # Fazer análise
    request.user.increment_analysis_count()
else:
    return Response({'error': 'Limite diário atingido'})
```

---

## 🎨 Frontend Integration

### Endpoints para tela de planos:
```javascript
// Listar planos
const plans = await api.get('/subscriptions/plans/');

// Verificar assinatura atual
const subscription = await api.get('/subscriptions/my-subscription/');

// Cancelar assinatura
await api.post('/subscriptions/cancel/');
```

### Dados retornados incluem:
- Limites diários
- Preços
- Features/benefícios
- Economia (desconto)
- Cores para UI
- Badge "popular"

---

## 🚀 Próximos Passos

### 1. Integração VPay
- [x] Criar pedido no checkout hospedado
- [x] Confirmar pagamento via webhook assinado ou polling
- [x] Criar assinatura após pagamento confirmado
- [x] Atualizar status do usuário

### 2. Frontend
- [ ] Tela de seleção de planos (PricingPage)
- [ ] Modal de checkout
- [ ] Tela de gerenciamento de assinatura
- [ ] Badge premium no perfil
- [ ] Indicador de limite diário

### 3. Notificações
- [ ] Email de boas-vindas ao premium
- [ ] Notificação de expiração (7 dias antes)
- [ ] Email de cancelamento
- [ ] Lembrete de renovação

---

## 🔐 Segurança

- ✅ Planos configurados no backend (não no frontend)
- ✅ Validação de limites no servidor
- ✅ Endpoints de planos públicos (para mostrar preços)
- ✅ Endpoints de assinatura protegidos (autenticação obrigatória)
- ✅ Usuário só pode gerenciar própria assinatura
- ✅ Freemium não pode ser "cancelado" (é o padrão)

---

## 📝 Notas Técnicas

### Diferença: `plan` vs `plan_slug`
- `plan`: Campo com choices do Django (display)
- `plan_slug`: Referência ao plano em `plan_config.py` (lógica)

### Freemium
- Não tem registro na tabela Subscription
- É o comportamento padrão quando usuário não tem assinatura ativa
- Endpoint `my-subscription/` retorna dados simulados de freemium

### Expiração
- Assinaturas premium têm `end_date`
- Task cron deve marcar como `expired` quando `end_date` passar
- Freemium tem `end_date` muito distante (100 anos)
