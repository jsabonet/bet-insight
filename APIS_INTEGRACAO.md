# 🔑 GUIA DE INTEGRAÇÃO - APIs NECESSÁRIAS
## Bet Insight Mozambique - Cadastro e Chaves de API

---

## 📋 VISÃO GERAL

Este documento lista todas as APIs necessárias para o funcionamento completo da plataforma, com links diretos para cadastro e instruções para obter as chaves de API.

---

## 🎯 APIS ESSENCIAIS (MVP)

### 1. 🤖 Google Gemini AI (Análise Inteligente)

**Função:** Gerar análises preditivas e recomendações de apostas usando IA

**Plano Recomendado:** Gratuito (60 requisições/minuto)

**Links:**
- 🌐 Site: https://ai.google.dev/
- 📚 Documentação: https://ai.google.dev/gemini-api/docs
- 🔑 Console API: https://aistudio.google.com/app/apikey

**Passo a Passo:**
1. Acesse https://aistudio.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Selecione ou crie um projeto do Google Cloud
5. Copie a chave gerada (formato: `AIza...`)

**Variável de Ambiente:**
```bash
GOOGLE_GEMINI_API_KEY=sua_chave_aqui
```

**Limites do Plano Gratuito:**
- 60 requisições por minuto
- 1,500 requisições por dia
- Suficiente para MVP e testes

**Custo Após Limites:**
- $0.00025 por 1,000 caracteres de input
- $0.0005 por 1,000 caracteres de output

---

### 2. ⚽ API-Football via RapidAPI (Dados de Futebol)

**Função:** Obter dados em tempo real de partidas, estatísticas, odds, etc.

**Plano Recomendado:** Basic ($0/mês) para testes ou Pro ($24.99/mês) para produção

**Links:**
- 🌐 RapidAPI Hub: https://rapidapi.com/hub
- ⚽ API-Football: https://rapidapi.com/api-sports/api/api-football
- 📚 Documentação: https://www.api-football.com/documentation-v3
- 🔑 Dashboard: https://rapidapi.com/developer/apps

**Passo a Passo:**
1. Acesse https://rapidapi.com/ e crie uma conta
2. Confirme seu email
3. Vá para https://rapidapi.com/api-sports/api/api-football
4. Clique em "Subscribe to Test"
5. Escolha o plano (Basic para testes, Pro para produção)
6. Após subscrever, vá em "Endpoints" → "Code Snippets"
7. Copie o `X-RapidAPI-Key` do header

**Variáveis de Ambiente:**
```bash
RAPIDAPI_KEY=sua_chave_rapidapi_aqui
RAPIDAPI_HOST=api-football-v1.p.rapidapi.com
```

**Limites por Plano:**

| Plano | Requisições/Dia | Custo/Mês |
|-------|-----------------|-----------|
| Basic (Teste) | 100 | $0 |
| Pro | 3,000 | $24.99 |
| Ultra | 10,000 | $49.99 |
| Mega | 50,000 | $199.99 |

**Endpoints Principais:**
- `/fixtures` - Partidas (passadas e futuras)
- `/predictions` - Previsões (odds, probabilidades)
- `/teams/statistics` - Estatísticas de times
- `/players` - Estatísticas de jogadores
- `/standings` - Classificação de ligas
- `/odds` - Odds de casas de apostas

---

### 3. ⚽ Football-Data.org (Alternativa/Backup)

**Função:** Dados históricos e estatísticas de futebol (backup da API-Football)

**Plano Recomendado:** Free Tier (10 requisições/minuto)

**Links:**
- 🌐 Site: https://www.football-data.org/
- 📚 Documentação: https://www.football-data.org/documentation/quickstart
- 🔑 Cadastro: https://www.football-data.org/client/register

**Passo a Passo:**
1. Acesse https://www.football-data.org/client/register
2. Preencha o formulário de cadastro
3. Confirme seu email
4. Faça login em https://www.football-data.org/client/login
5. Acesse "API Token" no menu
6. Copie sua chave de API

**Variável de Ambiente:**
```bash
FOOTBALL_DATA_API_KEY=sua_chave_aqui
```

**Limites do Plano Gratuito:**
- 10 requisições por minuto
- Acesso limitado a ligas principais
- Sem dados de odds

**Custo do Plano Pago:**
- Não disponível para indivíduos (apenas organizações)
- Usar como backup/complemento da API-Football

---

## 💳 APIS DE PAGAMENTO (MOÇAMBIQUE)

### 4. 💰 PaySuite API (Pagamento Mobile) ✅ CONFIGURADO

**Função:** Processar pagamentos e assinaturas via M-Pesa, E-Mola e outros métodos de pagamento em Moçambique

**Plano Recomendado:** Produção

**Links:**
- 🌐 Site: https://paysuite.co.mz/
- 📚 Documentação: https://docs.paysuite.co.mz/
- 🔑 API Docs: https://paysuite.co.mz/api/documentation
- 🏪 Dashboard: https://paysuite.co.mz/

**Vantagens do PaySuite:**
- ✅ Suporta M-Pesa, E-Mola e outros métodos
- ✅ API unificada para todos os métodos de pagamento
- ✅ Webhook automático para confirmação de pagamentos
- ✅ Dashboard para gerenciar transações
- ✅ Sem necessidade de conta empresarial inicialmente
- ✅ Suporte local em Moçambique

**Passo a Passo:**
1. Acesse https://paysuite.co.mz/ e crie uma conta
2. Complete o perfil no dashboard
3. Acesse "Developers" ou "API"
4. Copie o API Token (formato: `ID|token`)
5. Configure a URL do webhook no dashboard
6. Copie o Webhook Secret para validação

**Variáveis de Ambiente:**
```bash
# PaySuite API
PAYSUITE_API_TOKEN=1193|4iu77r4TUkd0nsB3MP8Qjr1uYVvM7d0Y0lpOgwETc153d048
PAYSUITE_WEBHOOK_SECRET=whsec_cd0a9e1a17e2d5d2a7cc49e9b431721f88d19b95d018f2ac
PAYSUITE_API_URL=https://paysuite.co.mz/api

# Webhook Configuration
PAYSUITE_WEBHOOK_URL=https://seu-dominio.com/api/webhooks/paysuite/
```

**Métodos de Pagamento Suportados:**
- M-Pesa (Vodacom)
- E-Mola (Movitel)
- Cartões de crédito/débito
- Transferência bancária

**Fluxo de Integração:**
1. Criar requisição de pagamento via API
2. Cliente recebe prompt no celular (M-Pesa/E-Mola)
3. Cliente confirma pagamento
4. PaySuite envia webhook para sua aplicação
5. Validar webhook usando o secret
6. Ativar assinatura do usuário

**Endpoints Principais:**
- `POST /v1/payment` - Criar pagamento
- `GET /v1/payment/{id}` - Consultar status
- `POST /webhook` - Receber confirmações (seu servidor)

**Taxas:**
- Taxa de transação: Variável por método
- Tempo de processamento: Instantâneo
- Reconciliação: Dashboard online

**Status:** ✅ Chaves configuradas e prontas para uso

---

### 5. 💰 M-Pesa API Direto (Alternativa - Não Recomendado)

**Função:** Alternativa ao M-Pesa para pagamentos mobile

**Plano Recomendado:** Produção

**Links:**
- 🌐 Site: https://www.e-mola.com/
- 📧 Contato: suporte@e-mola.com
- 📚 Documentação: Disponível após cadastro

**Passo a Passo:**
1. Entre em contato via suporte@e-mola.com
2. Solicite documentação de integração
3. Preencha formulário de cadastro de parceiro
4. Aguarde análise e aprovação
5. Receba credenciais de API

**Variáveis de Ambiente:**
```bash
EMOLA_API_KEY=sua_chave_emola
EMOLA_MERCHANT_ID=seu_merchant_id
EMOLA_SECRET=seu_secret
```

**Nota:** E-Mola tem menos documentação pública. Recomendado como fallback.

---

## 📱 APIS OPCIONAIS (FEATURES AVANÇADAS)

### 6. 📧 SendGrid (Email Transacional)

**Função:** Enviar emails de confirmação, recuperação de senha, relatórios

**Plano Recomendado:** Free (100 emails/dia)

**Links:**
- 🌐 Site: https://sendgrid.com/
- 🔑 Signup: https://signup.sendgrid.com/
- 📚 Docs: https://docs.sendgrid.com/

**Passo a Passo:**
1. Crie conta em https://signup.sendgrid.com/
2. Confirme seu email
3. Complete o onboarding
4. Vá em Settings → API Keys
5. Create API Key (Full Access)
6. Copie a chave (só aparece uma vez!)

**Variável de Ambiente:**
```bash
SENDGRID_API_KEY=SG.sua_chave_aqui
SENDGRID_FROM_EMAIL=noreply@betinsight.co.mz
```

**Limites:**
- Free: 100 emails/dia
- Essentials ($19.95/mês): 50,000 emails/mês
- Pro ($89.95/mês): 100,000 emails/mês

---

### 7. 💬 Twilio (SMS e WhatsApp)

**Função:** Notificações via SMS e WhatsApp Business

**Plano Recomendado:** Pay as you go ($20 crédito inicial)

**Links:**
- 🌐 Site: https://www.twilio.com/
- 🔑 Console: https://www.twilio.com/console
- 📚 Docs: https://www.twilio.com/docs

**Passo a Passo:**
1. Crie conta em https://www.twilio.com/try-twilio
2. Verifique seu número de telefone
3. No Console, copie:
   - Account SID
   - Auth Token
4. Compre um número Twilio para Moçambique
5. Para WhatsApp, solicite acesso ao WhatsApp Business API

**Variáveis de Ambiente:**
```bash
TWILIO_ACCOUNT_SID=sua_account_sid
TWILIO_AUTH_TOKEN=sua_auth_token
TWILIO_PHONE_NUMBER=+258_seu_numero_twilio
TWILIO_WHATSAPP_NUMBER=whatsapp:+258_seu_numero
```

**Custos Estimados (Moçambique):**
- SMS: ~$0.05 por mensagem
- WhatsApp: $0.0042 por conversa iniciada
- Número Twilio: $1/mês

---

### 8. 🔥 Firebase (Notificações Push)

**Função:** Push notifications para PWA e apps mobile

**Plano Recomendado:** Spark (Gratuito)

**Links:**
- 🌐 Console: https://console.firebase.google.com/
- 📚 Docs: https://firebase.google.com/docs

**Passo a Passo:**
1. Acesse https://console.firebase.google.com/
2. Clique em "Add project"
3. Dê um nome ao projeto
4. Ative Google Analytics (opcional)
5. No projeto, vá em Project Settings
6. Em "Cloud Messaging", gere uma nova chave de servidor
7. Copie o "Server Key" e "Sender ID"

**Variáveis de Ambiente:**
```bash
FIREBASE_SERVER_KEY=sua_firebase_server_key
FIREBASE_SENDER_ID=seu_sender_id
FIREBASE_API_KEY=sua_api_key
FIREBASE_PROJECT_ID=seu_project_id
```

**Limites do Plano Gratuito:**
- Push notifications: Ilimitadas
- Storage: 1 GB
- Hosting: 10 GB/mês

---

## 🗂️ ARMAZENAMENTO E INFRAESTRUTURA

### 9. ☁️ AWS S3 (Armazenamento)

**Função:** Armazenar relatórios PDF, imagens, backups

**Plano Recomendado:** Pay as you go (Free tier: 5GB/12 meses)

**Links:**
- 🌐 Console: https://console.aws.amazon.com/
- 📚 S3 Docs: https://docs.aws.amazon.com/s3/

**Passo a Passo:**
1. Crie conta AWS em https://aws.amazon.com/
2. Vá para IAM → Users → Add User
3. Ative "Programmatic access"
4. Anexe política "AmazonS3FullAccess"
5. Copie Access Key ID e Secret Access Key
6. Crie um bucket S3 em https://s3.console.aws.amazon.com/

**Variáveis de Ambiente:**
```bash
AWS_ACCESS_KEY_ID=sua_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
AWS_REGION=eu-west-1
AWS_S3_BUCKET_NAME=bet-insight-storage
```

**Free Tier (12 meses):**
- 5 GB de armazenamento
- 20,000 requisições GET
- 2,000 requisições PUT

---

### 10. 🐘 ElephantSQL (PostgreSQL Cloud)

**Função:** Banco de dados PostgreSQL gerenciado

**Plano Recomendado:** Tiny Turtle (Gratuito) para testes, Little Lemur ($5/mês) para produção

**Links:**
- 🌐 Site: https://www.elephantsql.com/
- 🔑 Signup: https://customer.elephantsql.com/signup

**Passo a Passo:**
1. Crie conta em https://customer.elephantsql.com/signup
2. Crie uma nova instância
3. Escolha o plano
4. Selecione a região (escolher próxima a Moçambique)
5. Copie a URL de conexão

**Variável de Ambiente:**
```bash
DATABASE_URL=postgres://usuario:senha@servidor.db.elephantsql.com/database
```

**Planos:**
- Tiny Turtle: 20MB (grátis) - apenas testes
- Little Lemur: 5GB ($5/mês) - MVP
- Pretty Panda: 25GB ($19/mês) - produção
- Enormous Elephant: 100GB ($49/mês) - escala

---

### 11. ⚡ Redis Cloud (Cache)

**Função:** Cache para melhorar performance

**Plano Recomendado:** Free (30MB)

**Links:**
- 🌐 Site: https://redis.com/try-free/
- 🔑 Console: https://app.redislabs.com/

**Passo a Passo:**
1. Crie conta em https://redis.com/try-free/
2. Crie um banco de dados
3. Escolha a região
4. Copie o endpoint e senha

**Variável de Ambiente:**
```bash
REDIS_URL=redis://default:senha@endpoint:porta
```

**Free Tier:**
- 30 MB de RAM
- 30 conexões simultâneas
- Suficiente para MVP

---

## 📊 MONITORAMENTO E ANALYTICS

### 12. 📈 Google Analytics 4

**Função:** Análise de tráfego e comportamento de usuários

**Plano:** Gratuito

**Links:**
- 🌐 Console: https://analytics.google.com/
- 📚 Docs: https://developers.google.com/analytics

**Passo a Passo:**
1. Acesse https://analytics.google.com/
2. Crie uma conta e propriedade
3. Configure um Web Stream
4. Copie o Measurement ID (formato: G-XXXXXXXXXX)

**Variável de Ambiente:**
```bash
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

---

### 13. 🐛 Sentry (Error Tracking)

**Função:** Monitoramento e tracking de erros

**Plano Recomendado:** Developer (Gratuito - 5,000 eventos/mês)

**Links:**
- 🌐 Site: https://sentry.io/
- 🔑 Signup: https://sentry.io/signup/

**Passo a Passo:**
1. Crie conta em https://sentry.io/signup/
2. Crie um novo projeto (escolha Django/React)
3. Copie o DSN fornecido

**Variável de Ambiente:**
```bash
SENTRY_DSN=https://chave@sentry.io/projeto
```

---

## 🔒 CHECKLIST DE SEGURANÇA

Antes de colocar em produção, certifique-se de:

- [ ] Todas as chaves API estão em variáveis de ambiente (`.env`)
- [ ] `.env` está no `.gitignore`
- [ ] Usar HTTPS em produção
- [ ] Implementar rate limiting nas APIs
- [ ] Monitorar uso de cada API
- [ ] Configurar alertas de limite de requisições
- [ ] Ter backup das chaves em local seguro (LastPass, 1Password)
- [ ] Rotacionar chaves periodicamente
- [ ] Usar diferentes chaves para staging/production

---

## 📋 RESUMO DE CUSTOS MENSAIS

### Cenário MVP (Primeiros 3 meses)

| Serviço | Plano | Custo/Mês |
|---------|-------|-----------|
| Google Gemini AI | Free | $0 |
| API-Football (RapidAPI) | Basic | $0 |
| Football-Data.org | Free | $0 |
| M-Pesa | Taxas por transação | Variável |
| SendGrid | Free | $0 |
| Firebase | Spark | $0 |
| ElephantSQL | Tiny Turtle | $0 |
| Redis Cloud | Free | $0 |
| Sentry | Developer | $0 |
| **TOTAL MVP** | | **$0 + taxas M-Pesa** |

### Cenário Produção (100+ usuários)

| Serviço | Plano | Custo/Mês |
|---------|-------|-----------|
| Google Gemini AI | Pay-as-go | ~$20 |
| API-Football (RapidAPI) | Pro | $24.99 |
| ElephantSQL | Little Lemur | $5 |
| AWS S3 | Pay-as-go | ~$5 |
| SendGrid | Essentials | $19.95 |
| Twilio (opcional) | Pay-as-go | ~$20 |
| **TOTAL PRODUÇÃO** | | **~$95/mês** |

### Cenário Escala (1000+ usuários)

| Serviço | Plano | Custo/Mês |
|---------|-------|-----------|
| Google Gemini AI | Pay-as-go | ~$100 |
| API-Football (RapidAPI) | Ultra | $49.99 |
| ElephantSQL | Pretty Panda | $19 |
| AWS S3 | Pay-as-go | ~$20 |
| SendGrid | Pro | $89.95 |
| Twilio | Pay-as-go | ~$50 |
| Redis Cloud | Standard | $7 |
| Hosting (VPS/Cloud) | | ~$50 |
| **TOTAL ESCALA** | | **~$385/mês** |

---

## 🚀 ORDEM DE PRIORIDADE PARA CADASTRO

### Essencial (Semana 1)
1. ✅ Google Gemini AI
2. ✅ API-Football (RapidAPI)
3. ✅ ElephantSQL (ou PostgreSQL local)

### Importante (Semana 2)
4. ✅ M-Pesa (iniciar processo de cadastro - demora!)
5. ✅ SendGrid
6. ✅ Firebase

### Opcional (Semana 3+)
7. ⭕ Twilio (quando implementar SMS/WhatsApp)
8. ⭕ AWS S3 (quando implementar relatórios)
9. ⭕ Sentry (quando deploy em produção)

---

## 📝 TEMPLATE DE ARQUIVO .env

Copie e preencha com suas chaves:

```bash
# ============================================
# BET INSIGHT MOZAMBIQUE - ENVIRONMENT VARIABLES
# ============================================

# Django Settings
SECRET_KEY=sua_django_secret_key_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgres://user:password@localhost:5432/betinsight

# Google Gemini AI
GOOGLE_GEMINI_API_KEY=AIza...

# Football APIs
RAPIDAPI_KEY=sua_rapidapi_key
RAPIDAPI_HOST=api-football-v1.p.rapidapi.com
FOOTBALL_DATA_API_KEY=sua_football_data_key

# M-Pesa
MPESA_ENV=sandbox
MPESA_CONSUMER_KEY=sua_consumer_key
MPESA_CONSUMER_SECRET=sua_consumer_secret
MPESA_API_KEY=sua_api_key
MPESA_PUBLIC_KEY=sua_public_key
MPESA_SERVICE_PROVIDER_CODE=171717
MPESA_SHORTCODE=seu_shortcode

# Email
SENDGRID_API_KEY=SG.sua_key
SENDGRID_FROM_EMAIL=noreply@betinsight.co.mz

# SMS/WhatsApp (Opcional)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# Firebase (Opcional)
FIREBASE_SERVER_KEY=
FIREBASE_SENDER_ID=

# Storage (Opcional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=eu-west-1
AWS_S3_BUCKET_NAME=

# Cache
REDIS_URL=redis://localhost:6379

# Analytics
GOOGLE_ANALYTICS_ID=
SENTRY_DSN=

# Frontend
VITE_API_URL=http://localhost:8000/api
VITE_GOOGLE_ANALYTICS_ID=
```

---

## 📞 SUPORTE E CONTATOS

### Em caso de dúvidas:

- **Google Gemini:** https://ai.google.dev/support
- **RapidAPI:** support@rapidapi.com
- **M-Pesa:** suporte.mpesa@vm.co.mz
- **SendGrid:** https://support.sendgrid.com/
- **Twilio:** https://www.twilio.com/help

---

## ✅ PRÓXIMOS PASSOS

1. **Cadastre-se nas APIs essenciais** (Google Gemini + API-Football)
2. **Teste as APIs** com Postman/Insomnia
3. **Configure o arquivo .env** no backend
4. **Implemente os serviços** um por um
5. **Teste cada integração** antes de avançar
6. **Monitore o uso** para não exceder limites

---

*Última atualização: 29 de Dezembro de 2025*  
*Versão: 1.0*
