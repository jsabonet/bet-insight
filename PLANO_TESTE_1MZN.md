# Plano de Teste - 1 MZN

## ✅ Implementação Concluída

Foi criado um novo plano de assinatura chamado **"Teste"** com valor de apenas **1 MZN** para facilitar testes de pagamento.

---

## 📋 Configuração do Plano

### Detalhes do Plano:
- **Nome**: Teste (1 MZN)
- **Slug**: `teste`
- **Preço**: 1 MZN
- **Duração**: 1 dia
- **Limite de análises**: 3 por dia
- **Status**: Ativo

### Features:
- 3 análises por dia
- Análise de IA básica
- Válido por 1 dia
- 🧪 Apenas para testes de pagamento

---

## 🗂️ Arquivos Modificados

### 1. **Backend - Configuração de Planos**
**Arquivo**: `backend/apps/subscriptions/plan_config.py`

Adicionado o plano 'teste' ao dicionário `PLANS`:

```python
'teste': {
    'name': 'Teste (1 MZN)',
    'slug': 'teste',
    'price': 1,
    'daily_analysis_limit': 3,
    'duration_days': 1,  # 1 dia apenas
    'features': [
        '3 análises por dia',
        'Análise de IA básica',
        'Válido por 1 dia',
        '🧪 Apenas para testes de pagamento',
    ],
    'description': 'Plano de teste - 1 MZN',
    'is_active': True,
    'color': 'green',
    'popular': False,
},
```

### 2. **Backend - Modelo de Assinatura**
**Arquivo**: `backend/apps/subscriptions/models.py`

Adicionado 'teste' às escolhas do campo `plan`:

```python
PLAN_CHOICES = [
    ('freemium', 'Freemium - Grátis'),
    ('teste', 'Teste - 1 MZN'),  # ← NOVO
    ('starter', 'Starter - 299 MZN'),
    ('pro', 'Pro - 599 MZN'),
    ('vip', 'VIP - 1499 MZN'),
]
```

### 3. **Migração de Banco de Dados**
**Arquivo**: `backend/apps/subscriptions/migrations/0006_alter_subscription_plan.py`

Migração criada e aplicada com sucesso:
```
✅ Applying subscriptions.0006_alter_subscription_plan... OK
```

---

## 🧪 Script de Teste

**Arquivo**: `backend/test_payment_1_metical.py`

Script criado para testar pagamentos de 1 MZN via PaySuite:

```python
payload = {
    'amount': 1,  # 1 metical
    'reference': 'TESTE001',
    'description': 'Plano Teste - 1 MZN - Bet Insight',
    'return_url': 'http://localhost:5173/payment/confirmation/TESTE001',
    'method': 'emola',  # ou 'mpesa'
}
```

### Resultado do Teste:
```
✅ PAGAMENTO CRIADO COM SUCESSO!
💳 ID do Pagamento: cc7c3561-d93b-40bc-940d-1f60c21dbed4
💰 Valor: 1.00 MZN
🔗 Checkout URL: https://paysuite.tech/checkout/cc7c3561-d93b-40bc-940d-1f60c21dbed4
```

---

## 🚀 Como Usar

### 1. **No Frontend** (Página de Planos)
O plano aparecerá automaticamente na página de planos (`/pricing`) porque:
- A API `/subscriptions/plans/` retorna todos os planos ativos
- O plano 'teste' tem `is_active: True`
- É ordenado por preço (aparecerá entre freemium e starter)

### 2. **Testar Pagamento de 1 MZN**

**Opção A - Via Script:**
```bash
cd backend
python test_payment_1_metical.py
```

**Opção B - Via Frontend:**
1. Acesse http://localhost:5173/pricing
2. Selecione o plano "Teste (1 MZN)"
3. Escolha método de pagamento (M-Pesa ou e-Mola)
4. Clique em "Criar Pagamento"
5. Acesse o checkout URL gerado
6. Complete o pagamento de 1 MZN

**Opção C - Via API Direta:**
```bash
curl -X POST http://localhost:8000/api/subscriptions/payments/ \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_slug": "teste",
    "payment_method": "emola"
  }'
```

### 3. **Verificar Assinatura**
Após pagamento confirmado:
```bash
curl http://localhost:8000/api/subscriptions/my-subscription/ \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## 🎯 Objetivo

Este plano de 1 MZN foi criado especificamente para:

✅ **Testar o fluxo completo de pagamento** sem gastar muito dinheiro  
✅ **Validar integração com PaySuite** (M-Pesa e e-Mola)  
✅ **Testar o sistema de timeout** (2 minutos)  
✅ **Validar o modal de checkout** com countdown  
✅ **Verificar webhooks** e polling de status  
✅ **Confirmar criação de assinatura** após pagamento  

---

## 📊 Comparação de Planos

| Plano | Preço | Duração | Análises/Dia | Uso |
|-------|-------|---------|--------------|-----|
| Freemium | Grátis | ∞ | 3 | Padrão |
| **Teste** | **1 MZN** | **1 dia** | **3** | **🧪 Testes** |
| Starter | 299 MZN | 30 dias | 15 | Casual |
| Pro | 599 MZN | 30 dias | 40 | Regular |
| VIP | 1499 MZN | 90 dias | 80 | Avançado |

---

## ⚠️ Observações Importantes

1. **Validade de 1 Dia**: O plano expira automaticamente após 24 horas
2. **Não Renovável**: `auto_renew` é false por padrão
3. **Apenas Teste**: Identificado com emoji 🧪 nas features
4. **Ambiente de Teste**: Funciona tanto em desenvolvimento quanto produção
5. **Cor Verde**: Para distinguir visualmente dos outros planos

---

## 🔧 Comandos Úteis

### Executar Teste de Pagamento:
```bash
cd D:\Projectos\Football\bet-insight\backend
python test_payment_1_metical.py
```

### Ver Migrações:
```bash
python manage.py showmigrations subscriptions
```

### Reverter Migração (se necessário):
```bash
python manage.py migrate subscriptions 0005
```

### Desativar Plano de Teste:
Em `plan_config.py`, altere:
```python
'teste': {
    ...
    'is_active': False,  # ← Desativa o plano
}
```

---

## ✅ Status Final

- ✅ Plano criado e configurado
- ✅ Migração aplicada ao banco de dados
- ✅ API retornando o plano automaticamente
- ✅ Script de teste funcionando
- ✅ PaySuite confirmando criação de pagamento
- ✅ Checkout URL gerado com sucesso
- ✅ Pronto para testes end-to-end

**🎉 O sistema está pronto para testar pagamentos de 1 MZN!**
