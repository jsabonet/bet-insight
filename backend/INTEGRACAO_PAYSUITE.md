# 💳 Integração PaySuite - Sistema de Pagamentos
## Bet Insight Mozambique

## 🎯 Visão Geral

Sistema completo de pagamentos via PaySuite para processar assinaturas premium usando M-Pesa e e-Mola.

---

## 🏗️ Arquitetura Implementada

### Arquivos Criados

#### 1. **`apps/subscriptions/paysuite_service.py`** (NOVO)
Serviço de integração com API PaySuite:
- `create_payment()` - Inicia pagamento
- `check_payment_status()` - Consulta status
- `verify_webhook_signature()` - Valida webhooks
- `process_webhook()` - Processa callbacks

#### 2. **`apps/subscriptions/payment_views.py`** (NOVO)
Endpoints para processar pagamentos:
- `create_payment()` - POST para iniciar pagamento
- `paysuite_webhook()` - Recebe notificações do PaySuite
- `check_payment_status()` - Verifica status de pagamento
- `my_payments()` - Lista pagamentos do usuário

#### 3. **Migrações**
- `0003_payment_currency_payment_paysuite_reference.py`
  - Adiciona campo `currency` (MZN)
  - Adiciona campo `paysuite_reference`

---

## 🔌 Endpoints API

### `POST /api/subscriptions/payments/create/`
Inicia processo de pagamento

**Autenticação**: Requerida

**Body**:
```json
{
  "plan_slug": "monthly|quarterly|yearly",
  "phone_number": "+258840000000",
  "payment_method": "mpesa"
}
```

**Response Success (201)**:
```json
{
  "success": true,
  "message": "Pagamento iniciado. Verifique seu telefone para confirmar.",
  "payment": {
    "id": 1,
    "transaction_id": "BET-123-ABC12345",
    "amount": "499.00",
    "currency": "MZN",
    "phone_number": "+258840000000",
    "status": "pending",
    "payment_method": "mpesa",
    "paysuite_reference": "PST-XYZ789"
  },
  "subscription": {
    "id": 1,
    "plan": "monthly",
    "status": "pending",
    "daily_limit": 50
  },
  "instructions": "Você receberá uma notificação no +258840000000 para confirmar o pagamento de 499 MZN."
}
```

**Response Error (400)**:
```json
{
  "error": "Você já possui uma assinatura ativa",
  "subscription": {...}
}
```

---

### `POST /api/subscriptions/payments/webhook/`
Webhook para PaySuite (público, mas validado)

**Autenticação**: Não requerida (validação por assinatura)

**Headers**:
- `X-PaySuite-Signature`: Assinatura do webhook

**Body** (exemplo do PaySuite):
```json
{
  "transaction_id": "BET-123-ABC12345",
  "reference": "PST-XYZ789",
  "status": "completed",
  "amount": 499.00,
  "phone": "+258840000000",
  "paid_at": "2026-01-01T10:30:00Z"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Webhook processed"
}
```

**Ações executadas**:
1. Valida assinatura do webhook
2. Busca pagamento pelo `transaction_id`
3. Atualiza status do pagamento
4. Ativa assinatura se pagamento confirmado
5. Atualiza status premium do usuário

---

### `GET /api/subscriptions/payments/check/{transaction_id}/`
Verifica status de pagamento específico

**Autenticação**: Requerida

**Response**:
```json
{
  "status": "completed",
  "payment": {
    "id": 1,
    "transaction_id": "BET-123-ABC12345",
    "amount": "499.00",
    "status": "completed",
    "completed_at": "2026-01-01T10:30:00Z"
  },
  "subscription": {
    "id": 1,
    "plan": "monthly",
    "status": "active",
    "is_active": true
  }
}
```

**Uso**: Frontend pode fazer polling para verificar se pagamento foi confirmado.

---

### `GET /api/subscriptions/payments/my-payments/`
Lista todos os pagamentos do usuário

**Autenticação**: Requerida

**Response**:
```json
[
  {
    "id": 1,
    "transaction_id": "BET-123-ABC12345",
    "amount": "499.00",
    "currency": "MZN",
    "status": "completed",
    "payment_method": "mpesa",
    "subscription_plan": {
      "plan": "monthly",
      "plan_slug": "monthly"
    },
    "created_at": "2026-01-01T10:25:00Z",
    "completed_at": "2026-01-01T10:30:00Z"
  }
]
```

---

## 🔧 Configuração

### Variáveis de Ambiente (`.env`)

```env
# PaySuite API Credentials
PAYSUITE_API_KEY=your_api_key_here
PAYSUITE_API_SECRET=your_api_secret_here

# PaySuite Settings
PAYSUITE_BASE_URL=https://api.paysuite.co.mz/v1
PAYSUITE_WEBHOOK_URL=https://seu-dominio.com/api/subscriptions/payments/webhook/
PAYSUITE_ENVIRONMENT=sandbox  # ou production
```

### Settings Django (`config/settings.py`)

```python
PAYSUITE_API_KEY = os.getenv('PAYSUITE_API_KEY', '')
PAYSUITE_API_SECRET = os.getenv('PAYSUITE_API_SECRET', '')
PAYSUITE_BASE_URL = os.getenv('PAYSUITE_BASE_URL', 'https://api.paysuite.co.mz/v1')
PAYSUITE_WEBHOOK_URL = os.getenv('PAYSUITE_WEBHOOK_URL', 'http://localhost:8000/api/subscriptions/payments/webhook/')
PAYSUITE_ENVIRONMENT = os.getenv('PAYSUITE_ENVIRONMENT', 'sandbox')
```

---

## 📱 Fluxo de Pagamento

### 1. Usuário Seleciona Plano
```
Frontend → GET /api/subscriptions/plans/
         ← Lista de planos com preços
```

### 2. Usuário Inicia Pagamento
```
Frontend → POST /api/subscriptions/payments/create/
           {
             "plan_slug": "monthly",
             "phone_number": "+258840000000"
           }
         ← Transaction ID + Instructions
```

### 3. Backend → PaySuite
```
Backend → POST https://api.paysuite.co.mz/v1/payments
          {
            "phone": "+258840000000",
            "amount": 499,
            "reference": "BET-123-ABC12345",
            "callback_url": "webhook URL"
          }
        ← Transaction ID + Status: pending
```

### 4. PaySuite → Usuário (M-Pesa)
```
Usuário recebe USSD/SMS no telefone
Usuário confirma pagamento no M-Pesa
```

### 5. PaySuite → Backend (Webhook)
```
PaySuite → POST /webhook/
           {
             "transaction_id": "BET-123-ABC12345",
             "status": "completed"
           }
         ← 200 OK

Backend:
  1. Marca pagamento como completed
  2. Ativa assinatura
  3. Atualiza user.is_premium = True
  4. Define user.premium_until = hoje + 30 dias
```

### 6. Frontend Verifica Status (Polling)
```
Frontend → GET /payments/check/BET-123-ABC12345/
         ← Status: completed
         
Frontend → GET /my-subscription/
         ← Assinatura ativa com novos limites
```

---

## 🔒 Segurança

### Validação de Webhook
```python
# PaySuite envia assinatura no header
signature = request.headers.get('X-PaySuite-Signature')

# Backend valida usando API secret
is_valid = paysuite_service.verify_webhook_signature(
    payload=request.data,
    signature=signature
)

if not is_valid:
    return 400 Bad Request
```

### Prevenção de Duplicação
- `transaction_id` é único no banco de dados
- Webhook pode ser chamado múltiplas vezes
- Backend verifica se pagamento já foi processado

### Validações de Negócio
- ✅ Usuário não pode ter 2 assinaturas ativas
- ✅ Plano freemium não pode ser pago
- ✅ Telefone normalizado para formato +258...
- ✅ Apenas usuário autenticado pode criar pagamento
- ✅ Usuário só vê seus próprios pagamentos

---

## 🧪 Testando Localmente

### 1. Configurar Sandbox PaySuite
```bash
# No .env
PAYSUITE_ENVIRONMENT=sandbox
PAYSUITE_API_KEY=sandbox_key
PAYSUITE_API_SECRET=sandbox_secret
```

### 2. Expor Webhook (Ngrok ou similares)
```bash
ngrok http 8000
# URL: https://abc123.ngrok.io

# Atualizar .env
PAYSUITE_WEBHOOK_URL=https://abc123.ngrok.io/api/subscriptions/payments/webhook/
```

### 3. Testar Endpoint
```bash
curl -X POST http://localhost:8000/api/subscriptions/payments/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_slug": "monthly",
    "phone_number": "+258840000000"
  }'
```

### 4. Simular Webhook (Teste Manual)
```bash
curl -X POST http://localhost:8000/api/subscriptions/payments/webhook/ \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "BET-123-ABC12345",
    "status": "completed",
    "amount": 499,
    "paid_at": "2026-01-01T10:30:00Z"
  }'
```

---

## 📊 Modelos Atualizados

### Payment
```python
class Payment(models.Model):
    # Relacionamentos
    user = ForeignKey(User)
    subscription = ForeignKey(Subscription)
    
    # Valores
    amount = DecimalField()
    currency = CharField(default='MZN')  # NOVO
    phone_number = CharField()
    
    # Referências
    transaction_id = CharField(unique=True)
    paysuite_reference = CharField()  # NOVO
    mpesa_reference = CharField()
    
    # Status
    status = CharField()  # pending, completed, failed
    payment_method = CharField()  # mpesa, emola
    
    # Timestamps
    created_at = DateTimeField()
    completed_at = DateTimeField(null=True)
    
    # Métodos
    def mark_as_completed(paid_at=None):
        """Marca como completo e ativa assinatura"""
    
    def mark_as_failed(reason=''):
        """Marca como falho"""
```

### Subscription
```python
# Status possíveis
STATUS_CHOICES = [
    ('active', 'Ativa'),
    ('expired', 'Expirada'),
    ('cancelled', 'Cancelada'),
    ('pending', 'Pendente'),  # Aguardando pagamento
]
```

---

## 🎨 Frontend Integration

### Exemplo React
```javascript
// 1. Buscar planos
const plans = await api.get('/subscriptions/plans/premium/');

// 2. Iniciar pagamento
const response = await api.post('/subscriptions/payments/create/', {
  plan_slug: 'monthly',
  phone_number: '+258840000000',
  payment_method: 'mpesa'
});

const { transaction_id, instructions } = response.data;

// 3. Mostrar instruções ao usuário
alert(instructions);

// 4. Fazer polling para verificar status
const checkStatus = async () => {
  const status = await api.get(`/subscriptions/payments/check/${transaction_id}/`);
  
  if (status.data.status === 'completed') {
    // Pagamento confirmado!
    navigate('/subscription/success');
  } else if (status.data.status === 'failed') {
    // Pagamento falhou
    navigate('/subscription/error');
  } else {
    // Ainda pendente, verificar novamente em 5s
    setTimeout(checkStatus, 5000);
  }
};

setTimeout(checkStatus, 5000); // Primeiro check após 5s
```

---

## 📝 Próximos Passos

### Backend
- [ ] Criar task cron para expirar assinaturas
- [ ] Enviar emails de confirmação
- [ ] Implementar reembolsos
- [ ] Logs detalhados de pagamentos
- [ ] Dashboard admin de pagamentos

### Frontend
- [ ] Tela de seleção de planos
- [ ] Modal de checkout
- [ ] Indicador de progresso do pagamento
- [ ] Tela de sucesso/erro
- [ ] Histórico de pagamentos no perfil

### Produção
- [ ] Obter credenciais production PaySuite
- [ ] Configurar domínio real para webhook
- [ ] Configurar HTTPS
- [ ] Monitoramento de webhooks
- [ ] Alertas de falhas de pagamento

---

## 🐛 Troubleshooting

### Webhook não está sendo recebido
- Verificar se URL está acessível publicamente
- Confirmar que PaySuite tem URL correta configurada
- Checar logs do servidor web (nginx/gunicorn)
- Validar formato da URL (deve terminar com `/`)

### Pagamento não ativa assinatura
- Verificar se webhook foi recebido e processado
- Checar logs: `payment.mark_as_completed()` foi chamado?
- Verificar `subscription.status` está `active`
- Confirmar `user.is_premium` está `True`

### Erro ao criar pagamento
- Verificar credenciais PaySuite no `.env`
- Confirmar formato do telefone: `+258...`
- Checar se plano existe e está ativo
- Validar se usuário não tem assinatura ativa

---

## 📞 Suporte PaySuite

- **Website**: https://paysuite.co.mz
- **Documentação**: https://paysuite.co.mz/docs
- **Email**: suporte@paysuite.co.mz
- **Sandbox**: Usar números de teste fornecidos pela PaySuite
