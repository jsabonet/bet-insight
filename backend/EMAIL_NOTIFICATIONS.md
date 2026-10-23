# Notificações por Email (Resend)

Arquitetura de emails transacionais do **PlacarCerto**, integrada com a
**Resend** (https://resend.com) como provedor de envio.

---

## 1. Arquitetura

```
apps/notifications/
├── backends.py   # ResendBackend (implementa BaseEmailBackend, usa `requests`)
├── service.py    # send_template_email() + render_template()
├── templates/emails/*.html + *.txt   # Templates HTML (base + 14 emails)
└── tests.py      # Testes de renderização + envio

apps/users/emails.py           # welcome, verification, password_reset, password_changed
apps/subscriptions/emails.py   # activated, expired, cancelled, payment_confirmed, payment_failed
apps/affiliates/emails.py      # approved, commission_earned/available/paid, withdrawal_requested
```

- `ResendBackend` é um backend Django padrão (`EMAIL_BACKEND`). Quando
  `RESEND_API_KEY` está definida, ele é selecionado automaticamente em
  `config/settings.py`; caso contrário, cai para o `console` (logs) em dev.
- Envio suporta HTML (via `EmailMultiAlternatives`), texto alternativo,
  `cc/bcc`, `reply_to`, anexos e **tags** (segmentação na Resend).
- Não requer o SDK `resend` — usa `requests`, já presente no projeto.

---

## 2. Mapeamento de fluxos → emails

| # | Fluxo / Rota | Disparador | Template |
|---|---|---|---|
| 1 | `POST /api/users/auth/register/` | Registo | `welcome` + `email_verification` |
| 2 | `POST /api/users/auth/verify-email/` | Confirmação | (marca `email_verified`) |
| 3 | `POST /api/users/auth/password-reset/` | Recuperar senha | `password_reset` |
| 4 | `POST /api/users/auth/password-reset/confirm/` | Senha alterada | `password_changed` |
| 5 | `POST /api/subscriptions/.../vpay/webhook/` (paid) | Pagamento confirmado | `payment_confirmed` |
| 6 | idem | Assinatura ativada | `subscription_activated` |
| 7 | idem (failed) | Pagamento falhou | `payment_failed` |
| 8 | `POST /api/subscriptions/cancel/` | Cancelamento | `subscription_cancelled` |
| 9 | `manage.py expire_subscriptions` | Assinatura expirada | `subscription_expired` |
| 10 | `POST /api/affiliates/apply/` | Afiliado aprovado | `affiliate_approved` |
| 11 | `create_commission_if_applicable` | Comissão ganha | `affiliate_commission_earned` |
| 12 | `affiliates.release_pending_commissions` (celery) | Comissão disponível | `affiliate_commission_available` |
| 13 | `admin_mark_paid` | Comissão paga | `affiliate_commission_paid` |
| 14 | `POST /api/affiliates/withdraw/` | Levantamento pedido | `affiliate_withdrawal_requested` |

---

## 3. Configuração do provedor (Resend)

1. Criar conta em **https://resend.com**.
2. Em *Domains*, **adicionar e verificar** o domínio de envio
   (ex.: `placarcerto.digital`). Isto adiciona os registos SPF e DKIM ao DNS.
3. Em *API Keys*, criar uma chave e copiá-la.
4. Preencher no `backend/.env` (fora do Git):

```env
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
RESEND_FROM_EMAIL=PlacarCerto <noreply@placarcerto.digital>
RESEND_TIMEOUT=20
SUPPORT_EMAIL=suporte@placarcerto.digital
FRONTEND_URL=https://placarcerto.digital
```

> **O remetente (`RESEND_FROM_EMAIL`) tem de usar o domínio verificado.**
> Sem `RESEND_API_KEY`, o backend usa o console (apenas logs) — útil em dev.

Variáveis relevantes em `config/settings.py`:
- `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `RESEND_TIMEOUT`
- `FRONTEND_URL` (base dos links nos emails)
- `SUPPORT_EMAIL`

---

## 4. Endpoints novos (users)

| Método | Rota | Body | Descrição |
|---|---|---|---|
| POST | `/api/users/auth/verify-email/` | `{uid, token}` | Confirma email |
| POST | `/api/users/auth/resend-verification/` | `{email}` | Reenvia verificação |
| POST | `/api/users/auth/password-reset/` | `{email}` | Envia link de reset |
| POST | `/api/users/auth/password-reset/confirm/` | `{uid, token, new_password}` | Redefine senha |

> Os links apontam para `FRONTEND_URL/verify-email?...` e
> `FRONTEND_URL/reset-password?...` — o frontend deve renderizar essas rotas.

---

## 5. Migração

Novo campo no modelo `User`:
```bash
python manage.py migrate apps.users
```
- `0004_user_email_verified.py` — adiciona `email_verified`.

---

## 6. Testes

```bash
python manage.py test apps.users apps.subscriptions apps.affiliates apps.notifications
```

Cobre: renderização de todos os templates, envio, fluxo de registo/verificação/
redefinição de senha, e emails de assinatura/afiliados.

---

## 7. Próximos passos sugeridos

- **Frontend**: páginas `verify-email` e `reset-password` (consumem os
  endpoints acima e os query params `uid`/`token`).
- **Lembretes**: email de "teste a terminar" / "renovação em N dias" via Celery
  Beat (novo task `notify_expiring_subscriptions`).
- **Async**: mover envios para Celery com `EMAIL_ASYNC=True` se o volume
  crescer (hoje o envio é síncrono, mas não bloqueia o fluxo — wrapped em
  try/except).
- **Webhooks**: consumir `email.sent`/`email.bounced` da Resend para tracking.
