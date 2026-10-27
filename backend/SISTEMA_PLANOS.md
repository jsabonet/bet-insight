# Planos e limites atuais

## Planos disponíveis

| Plano | Preço | Limite diário | Duração |
|---|---:|---:|---|
| Freemium | 0 MZN | 3 análises | Permanente |
| Premium Vitalício | 250 MZN, pagamento único | 60 análises | Vitalícia |

O plano `premium_vitalicio_teste` também usa o limite de 60 análises por dia,
mas é exclusivo para staff/admin e não representa uma oferta comercial.
Planos pagos antigos permanecem identificados como legados e não são oferecidos
no endpoint público de planos.

## Fonte de configuração e aplicação do limite

Os preços, limites e funcionalidades apresentados pela API vêm de
`apps/subscriptions/plan_config.py`. A página Premium e o checkout carregam
essa configuração, em vez de manter um catálogo de preços separado.

O método `User.get_daily_analysis_limit()` usa o limite do plano da assinatura
ativa. `PREMIUM_ANALYSIS_LIMIT` é apenas o fallback para contas Premium sem uma
assinatura associada e também deve permanecer em 60 no ambiente de produção.

```env
PREMIUM_ANALYSIS_LIMIT=60
```

O endpoint público dos planos é `GET /api/subscriptions/plans/`. O limite
retornado nessa resposta é o valor aplicado ao consumo diário de análises.
Use `python manage.py test apps.subscriptions` para validar pagamentos,
assinaturas e limites.
