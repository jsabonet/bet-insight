# 🚀 Como Testar a Integração de Pagamento

## 📋 Pré-requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL rodando
- Conta PaySuite com credenciais (já configuradas)

---

## ⚡ Início Rápido (2 Terminais)

### Terminal 1: Backend Django

```bash
# Navegar para o backend
cd d:\Projectos\Football\bet-insight\backend

# Ativar ambiente virtual (se usar)
# .\venv\Scripts\activate  # Windows
# source venv/bin/activate # Linux/Mac

# Instalar dependências (se necessário)
pip install -r requirements.txt

# Rodar migrações (se necessário)
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

**Resultado esperado:**
```
Django version 5.0.1, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Terminal 2: Frontend React

```bash
# Navegar para o frontend
cd d:\Projectos\Football\bet-insight\frontend

# Instalar dependências (se necessário)
npm install

# Iniciar dev server
npm run dev
```

**Resultado esperado:**
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

---

## 🧪 Teste Passo a Passo

### 1. Acessar Frontend
```
http://localhost:5173
```

### 2. Fazer Login (se necessário)
- Criar conta ou usar existente
- Login: seu_email@exemplo.com
- Senha: sua_senha

### 3. Ir para Página Premium
```
http://localhost:5173/premium
```

**O que você deve ver:**
- ✅ 4 planos: Freemium, Starter, Pro, VIP
- ✅ Badge "🎁 7 dias grátis" no Starter
- ✅ Badge "⭐ Mais Popular" no Pro
- ✅ Lista de features com checkmarks
- ✅ Botões "Assinar Agora" / "Plano Atual"

### 4. Abrir Modal de Pagamento
- Clique em "Assinar Agora" em qualquer plano pago
- Recomendado: **Starter (299 MZN)** para teste inicial

**O que você deve ver:**
```
┌─────────────────────────────────────┐
│ Finalizar Assinatura          [X]   │
│ Starter                             │
├─────────────────────────────────────┤
│ Plano: Starter                      │
│ Análises: 15/dia                    │
│ Duração: 30 dias                    │
│ Total: 299 MZN                      │
├─────────────────────────────────────┤
│ Método de Pagamento                 │
│ ┌───────────────┬───────────────┐   │
│ │  [M-Pesa]     │  [e-Mola]     │   │
│ │   Vermelho    │   Verde       │   │
│ │   Vodacom     │   Movitel     │   │
│ └───────────────┴───────────────┘   │
│                                     │
│ Número de Telefone                  │
│ [📱] +258 84 ___ ____               │
│                                     │
│ [Confirmar Pagamento]               │
└─────────────────────────────────────┘
```

### 5. Verificar Logos Oficiais ⭐

**M-Pesa:**
- [ ] Logo vermelho (#E60000) visível
- [ ] Texto "M-Pesa" branco
- [ ] Label "Vodacom" abaixo
- [ ] Border vermelho quando selecionado
- [ ] Hover muda cor

**e-Mola:**
- [ ] Logo verde (#00A651) visível
- [ ] Texto "e-Mola" branco
- [ ] Label "Movitel" abaixo
- [ ] Border verde quando selecionado
- [ ] Hover muda cor

### 6. Selecionar Método
- Clique em **M-Pesa** ou **e-Mola**
- Veja o border mudar de cor
- Ring de destaque deve aparecer

### 7. Digitar Telefone

**Formatos aceitos:**
```
84 123 4567       → +258 84 123 4567 ✅
258 84 123 4567   → +258 84 123 4567 ✅
+258 84 123 4567  → +258 84 123 4567 ✅
```

**Operadoras:**
- 84, 85: Vodacom (M-Pesa)
- 86, 87: Movitel (e-Mola)

### 8. Confirmar Pagamento

**Clique em "Confirmar Pagamento"**

**Backend vai:**
1. Validar dados
2. Criar Payment (status: pending)
3. Criar Subscription (status: pending)
4. Chamar PaySuite API
5. Retornar transaction_id

**Frontend vai:**
1. Mostrar spinner "Processando..."
2. Mudar para "Aguardando confirmação..."
3. Mostrar logo do método escolhido
4. Iniciar polling (cada 5 segundos)

**Você deve ver:**
```
┌─────────────────────────────────────┐
│ ⟳ Aguardando confirmação...         │
│ Verifique seu telefone              │
│                                     │
│ [M-Pesa] Vodacom                    │
│                                     │
│ Uma notificação foi enviada para    │
│ +258 84 123 4567.                   │
│ Insira seu PIN no M-Pesa para       │
│ confirmar o pagamento de 299 MZN.   │
└─────────────────────────────────────┘
```

### 9. Confirmar no Telefone 📱

**No seu celular:**
1. Receba notificação do M-Pesa/e-Mola
2. Abra o app
3. Veja detalhes: "Bet Insight - 299 MZN"
4. Digite seu PIN
5. Confirme

### 10. Aguardar Confirmação

**PaySuite vai:**
1. Processar pagamento
2. Chamar webhook: `POST /api/subscriptions/payments/webhook/`
3. Backend atualiza Payment: pending → completed
4. Backend ativa Subscription
5. Backend envia email

**Frontend vai:**
1. Polling detecta mudança (máximo 5 segundos)
2. Mostra checkmark verde ✅
3. "Pagamento confirmado!"
4. Redireciona após 2 segundos
5. Fecha modal
6. Recarrega página

**Você deve ver:**
```
┌─────────────────────────────────────┐
│ ✅ Pagamento confirmado!             │
│                                     │
│ Sua assinatura Starter está ativa.  │
│ Redirecionando...                   │
└─────────────────────────────────────┘
```

### 11. Verificar Ativação

**Na página Premium:**
- Badge "✓ Plano Atual" no Starter
- Botão mudou para "Gerenciar"
- Limite de análises: 15/dia

**No perfil:**
- Subscription ativa
- Data de expiração: +30 dias
- Método de pagamento usado

---

## 🔍 Logs para Monitorar

### Backend Logs (Terminal 1)

**Requisição de criação:**
```
POST /api/subscriptions/payments/create/ 200
Creating payment for user: seu_usuario
Transaction ID: TXN_20260108_123456
Payment created successfully
```

**Polling:**
```
GET /api/subscriptions/payments/check/TXN_20260108_123456/ 200
Payment status: pending
```

**Webhook (quando confirmar):**
```
POST /api/subscriptions/payments/webhook/ 200
Webhook received: TXN_20260108_123456
Signature valid: True
Payment updated: pending → completed
Subscription activated: seu_usuario
Email sent to: seu_email@exemplo.com
```

**Polling detecta sucesso:**
```
GET /api/subscriptions/payments/check/TXN_20260108_123456/ 200
Payment status: completed
```

### Frontend Logs (DevTools Console)

**Abrir DevTools:** `F12` → Console

**Criação de pagamento:**
```javascript
POST http://localhost:8000/api/subscriptions/payments/create/
Status: 200 OK
Response: {
  transaction_id: "TXN_20260108_123456",
  instructions: "Verifique seu telefone...",
  status: "pending"
}
```

**Polling:**
```javascript
GET http://localhost:8000/api/subscriptions/payments/check/TXN_20260108_123456/
Status: 200 OK
Response: { status: "pending" }

// ... 5 segundos depois ...

GET http://localhost:8000/api/subscriptions/payments/check/TXN_20260108_123456/
Status: 200 OK
Response: { status: "completed" }
```

---

## ⚠️ Problemas Comuns

### Problema 1: Backend não inicia

**Erro:**
```
django.db.utils.OperationalError: could not connect to server
```

**Solução:**
```bash
# Verificar se PostgreSQL está rodando
# Windows: Serviços → PostgreSQL
# Linux: sudo systemctl status postgresql

# Verificar credenciais no .env
DATABASE_NAME=bet_insight
DATABASE_USER=postgres
DATABASE_PASSWORD=sua_senha
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### Problema 2: Frontend não conecta

**Erro:**
```javascript
Network Error
ERR_CONNECTION_REFUSED
```

**Solução:**
```bash
# Verificar se backend está rodando
curl http://localhost:8000/api/subscriptions/plans/

# Verificar CORS no settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
```

### Problema 3: Logos não aparecem

**Sintoma:** Botões mostram emojis 📱💳 em vez de logos

**Solução:**
```bash
# Limpar cache do navegador
Ctrl + Shift + R

# Verificar console por erros SVG
F12 → Console

# Forçar rebuild do frontend
cd frontend
npm run dev -- --force
```

### Problema 4: PaySuite retorna erro

**Erro:**
```json
{
  "error": "Invalid phone number",
  "code": 400
}
```

**Solução:**
- Verifique formato: +258 84 XXX XXXX
- Use operadora correta (84-87)
- Certifique-se que o número tem saldo

**Erro:**
```json
{
  "error": "Invalid API key",
  "code": 401
}
```

**Solução:**
```bash
# Verificar credenciais no .env
grep PAYSUITE backend/.env

# Deve retornar:
PAYSUITE_API_KEY=1193|4iu77r4TUkd0nsB3MP8Qjr1uYVvM7d0Y0lpOgwETc153d048
PAYSUITE_WEBHOOK_SECRET=whsec_cd0a9e1a17e2d5d2a7cc49e9b431721f88d19b95d018f2ac
```

### Problema 5: Webhook não funciona

**Sintoma:** Polling continua indefinidamente, nunca atualiza

**Causa:** Webhook não consegue chamar localhost

**Soluções:**

**A. Teste sem webhook (temporário):**
```bash
# No admin do Django: http://localhost:8000/admin
# Vá em Payments → Encontre seu pagamento
# Mude status: pending → completed
# Salve
# Polling vai detectar em até 5 segundos
```

**B. Usar ngrok (permanente):**
```bash
# Instalar ngrok: https://ngrok.com/download
ngrok http 8000

# Copiar URL: https://abc123.ngrok.io
# Configurar no painel PaySuite:
# Webhook URL: https://abc123.ngrok.io/api/subscriptions/payments/webhook/
```

### Problema 6: Timeout (5 minutos)

**Sintoma:**
```
Tempo limite excedido. Verifique o status na aba de pagamentos.
```

**Causas:**
- Usuário não confirmou no telefone
- Telefone sem saldo
- App M-Pesa/e-Mola não instalado
- Número incorreto

**Solução:**
- Verifique o telefone
- Tente novamente com número correto
- Consulte histórico em "Meus Pagamentos"

---

## 🎯 Checklist de Teste Completo

### Visual
- [ ] 4 planos visíveis na PremiumPage
- [ ] Badge "7 dias grátis" no Starter
- [ ] Badge "Mais Popular" no Pro
- [ ] Features com checkmarks
- [ ] Modal abre ao clicar "Assinar Agora"
- [ ] Logo M-Pesa vermelho (#E60000)
- [ ] Logo e-Mola verde (#00A651)
- [ ] Labels "Vodacom" e "Movitel"
- [ ] Border muda ao selecionar
- [ ] Ring de destaque aparece

### Funcional
- [ ] Validação de telefone funciona
- [ ] Formatação automática: +258 84 XXX XXXX
- [ ] Botão "Confirmar" desabilitado se telefone inválido
- [ ] Spinner aparece ao clicar
- [ ] Mensagem "Aguardando confirmação"
- [ ] Logo do método aparece no feedback
- [ ] Polling inicia automaticamente
- [ ] Webhook recebe callback
- [ ] Status atualiza: pending → completed
- [ ] Subscription ativa automaticamente
- [ ] Email de confirmação enviado
- [ ] Modal fecha após sucesso
- [ ] Página recarrega
- [ ] Badge "Plano Atual" aparece

### Backend
- [ ] Endpoint `/payments/create/` retorna 200
- [ ] Transaction ID é gerado
- [ ] Payment criado com status pending
- [ ] Subscription criado com status pending
- [ ] Endpoint `/payments/check/` retorna status
- [ ] Webhook valida assinatura HMAC
- [ ] Webhook atualiza Payment para completed
- [ ] Webhook ativa Subscription
- [ ] Email enviado corretamente
- [ ] Logs registrados

### Integração
- [ ] Frontend → Backend: create payment
- [ ] Backend → PaySuite: create transaction
- [ ] PaySuite → Usuário: push notification
- [ ] Usuário → PaySuite: confirm with PIN
- [ ] PaySuite → Backend: webhook callback
- [ ] Backend → Database: update records
- [ ] Backend → Frontend: polling returns completed
- [ ] Frontend → Usuário: success message

---

## 📊 Teste de Performance

### Tempo Esperado

**Fluxo normal:**
```
1. Usuário clica "Confirmar": < 1s
2. Backend cria pagamento: < 2s
3. PaySuite notifica usuário: < 5s
4. Usuário confirma PIN: 10-30s (variável)
5. Webhook recebido: < 2s
6. Frontend detecta via polling: < 5s
Total: ~25-50 segundos
```

**Casos extremos:**
```
Usuário demora: até 5 minutos (timeout)
Webhook falha: até 5 minutos (polling continua)
PaySuite lento: + 10-20 segundos
```

---

## 🚀 Próximo Passo: Deploy

Depois de testar localmente, veja:
- [INTEGRACAO_PAGAMENTO_COMPLETA.md](INTEGRACAO_PAGAMENTO_COMPLETA.md) - Seção "Para Produção"

**Requisitos mínimos:**
- Servidor com HTTPS (PaySuite exige SSL)
- Webhook URL pública
- CORS configurado
- Email funcionando
- Monitoramento ativo

---

## 📞 Precisa de Ajuda?

**Documentação do Projeto:**
1. [RESUMO_IMPLEMENTACAO.md](RESUMO_IMPLEMENTACAO.md) - Visão geral
2. [DESIGN_PAGAMENTOS.md](DESIGN_PAGAMENTOS.md) - Design system
3. [PAYSUITE_INTEGRADO.md](backend/PAYSUITE_INTEGRADO.md) - PaySuite API

**PaySuite Support:**
- Email: support@paysuite.co.mz
- Docs: https://docs.paysuite.co.mz
- Dashboard: https://paysuite.co.mz/dashboard

---

**Pronto para testar? Abra 2 terminais e siga os passos acima! 🎉**
