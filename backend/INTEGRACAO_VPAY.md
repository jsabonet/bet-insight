# 💳 Integração VPay Moçambique

Gateway de pagamentos VPay via **checkout hospedado** para processar assinaturas
premium. O cliente é redirecionado para o checkout da VPay e escolhe o método
(carteira móvel, cartão, PayPal ou QR Code), e a confirmação é feita sempre do
lado do servidor (polling + webhook verificado).

Documentação oficial:

- Referência da API: https://vpay.co.mz/docs/api-reference
- Autenticação: https://vpay.co.mz/docs/authentication
- Polling: https://vpay.co.mz/docs/api-reference/polling

---

## 🔐 Configuração (variáveis de ambiente)

Nenhum segredo deve estar no código, logs ou controlo de versão. Configure no
`backend/.env` (desenvolvimento) ou no gestor de segredos do servidor:

```text
VPAY_ENABLED=True
VPAY_BASE_URL=https://api.vpay.co.mz
VPAY_CLIENT_ID=app_e7fd19f9678ce3f793eb2d9efaa46f84
VPAY_CLIENT_SECRET=<configurar localmente, fora do código>
VPAY_APPLICATION_ID=3dd54636-bf2e-413f-b137-3f1d0e555365
VPAY_CHECKOUT_BASE_URL=https://checkout.vpay.co.mz
VPAY_WEBHOOK_SECRET=<configurar localmente, fora do código>
VPAY_TIMEOUT=30
```

- `VPAY_CLIENT_ID` e `VPAY_APPLICATION_ID` são identificadores públicos.
- `VPAY_CLIENT_SECRET` e `VPAY_WEBHOOK_SECRET` são segredos; **nunca** os cole
  no chat, em commits, fixtures, testes ou logs.
- Para gerar um segredo forte (webhook/secret), use por exemplo:
  `python -c "import secrets; print(secrets.token_urlsafe(48))"`.

---

## 🔌 Fluxo implementado

1. **Autenticação** — `POST /v1/auth/token` com `client_id` + `client_secret`. A página de autenticação também mostra `/api/auth/token`, mas essa rota respondeu 404 no teste de conectividade; o caminho `/v1/auth/token` foi confirmado com resposta de autenticação bem-sucedida.
   O `access_token` é mantido apenas em memória (cache com lock, renovado antes
   de expirar) e nunca é registado.
2. **Criar pedido** — `POST /v1/orders` com `source`, `customer` e `items`. Embora a API Collection atual liste `/api/orders`, essa rota respondeu 404; `/v1/orders` existe e devolveu validação do payload.
   O total é calculado no servidor (`quantidade × preço`) e os dados são
   validados antes do envio. O `orderId` da VPay é guardado para reconciliação.
3. **Checkout** — o cliente é redirecionado para o URL hospedado retornado pela
   API, ou para `https://checkout.vpay.co.mz/{orderId}` quando a resposta não o
   inclui.
4. **Confirmação** — nunca se considera pago apenas pelo regresso ao site. O
   estado é confirmado via:
   - Polling: `GET /v1/orders/{order_id}/status`
   - Webhook verificado: assinatura HMAC-SHA256 (`X-Voidpay-Signature: sha256=<hex>`)
     calculada sobre o corpo bruto, validada antes de interpretar o JSON.

---

## 🔌 Endpoints locais

### `POST /api/subscriptions/payments/vpay/create/` (autenticado)

Cria o pedido na VPay e devolve o URL de checkout.

**Body**:

```json
{ "plan_slug": "starter|pro|vip|teste" }
```

**Resposta (201)**:

```json
{
  "success": true,
  "checkout_url": "https://checkout.vpay.co.mz/<orderId>",
  "payment": { "transaction_id": "BET...", "gateway": "vpay", "vpay_order_id": "..." }
}
```

### `POST /api/subscriptions/payments/vpay/webhook/` (público, assinado)

Recebe a confirmação da VPay. A assinatura é validada antes de processar.

### `GET /api/subscriptions/payments/check/<transaction_id>/` (autenticado)

Polling já existente, agora ciente do gateway: para pagamentos `vpay` consulta
`GET /v1/orders/{id}/status`. Registos históricos de gateways desativados são
mantidos para auditoria, mas não podem ser reconciliados por esta integração.

---

## 🧭 Mapeamento de status

| VPay        | Local       |
|-------------|-------------|
| `paid`      | `completed` (ativa a assinatura) |
| `pending`   | `pending`   |
| `failed`    | `failed`    |
| `cancelled` | `cancelled` |
| `expired`   | `expired`   |

---

## 🛡️ Resiliência e segurança

- Timeouts e falhas de rede são tratados explicitamente.
- Um timeout na criação é marcado como `ambiguous` e **não** é repetido
  automaticamente sem antes consultar o estado (evita cobranças duplicadas).
- Criação de pedido é idempotente: um pedido `pending` do mesmo utilizador +
  plano é reutilizado após consulta do estado.
- Não guarda dados de cartão, PIN, tokens ou segredos.
- O fluxo usa apenas o checkout hospedado; não chama endpoints internos não
  documentados nem copia chaves de encriptação do JavaScript do checkout.

---

## 🧪 Testes

Os testes em `apps/subscriptions/tests.py` usam mocks e nunca chamam a API real:

```bash
cd backend
.venv\Scripts\python.exe manage.py test apps.subscriptions --noinput
```

> Para ambientes com console Windows cp1252, execute com
> `$env:PYTHONIOENCODING = "utf-8"` antes do comando.

---

## ⚠️ Ambiente de teste / sandbox

A disponibilidade de um ambiente sandbox da VPay **não foi confirmada** neste
projeto. Qualquer pedido que avance até ao checkout deve ser tratado como uma
transação real. Não crie cobranças reais durante desenvolvimento sem aprovação
explícita.
