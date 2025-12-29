# 🎯 MVP - BET INSIGHT MOZAMBIQUE
## Produto Mínimo Viável para Validação de Mercado

---

## 📊 OBJETIVO DO MVP

**Validar 3 Hipóteses Principais:**
1. ✅ Apostadores em Moçambique pagam por análises com IA?
2. ✅ As previsões da IA geram valor real (taxa de acerto > 60%)?
3. ✅ O modelo de assinatura mensal é sustentável?

**Meta:** 50 usuários pagantes em 60 dias

---

## 🎯 ESCOPO DO MVP

### ✅ O QUE INCLUIR (Essencial)

#### 1. Landing Page Simples
- Hero section com proposta de valor clara
- 3 exemplos de análises (mockups)
- Preços transparentes
- Formulário de cadastro
- Depoimentos (podem ser genéricos inicialmente)

#### 2. Sistema de Autenticação Básico
- Cadastro com email + senha
- Login/Logout
- Recuperação de senha
- Dashboard simples pós-login

#### 3. Análise de Jogos com IA (Core Feature)
```
Input: Manchester United vs Liverpool
Output:
├── Probabilidade de Vitória (Home/Draw/Away)
├── Análise de Forma (últimos 5 jogos)
├── Confronto Direto (últimos 3 H2H)
├── Estatística-Chave (gols, posse, etc)
├── Recomendação (Apostar em X)
└── Nível de Confiança (1-5 estrelas)
```

#### 4. Lista de Jogos Disponíveis
- Jogos das próximas 48h
- Filtro por liga (5 principais ligas)
- Status: Não analisado / Análise disponível
- Click para ver análise completa

#### 5. Sistema de Pagamento Simples
- **APENAS M-Pesa** (manual inicialmente)
- Usuário envia pagamento e compartilha comprovante
- Ativação manual da conta (admin aprova)
- 1 plano único: 499 MZN/mês

#### 6. Dashboard do Usuário
- Análises disponíveis hoje
- Histórico de análises visualizadas
- Status da assinatura
- Botão de renovação

#### 7. Painel Admin Básico
- Ver usuários cadastrados
- Aprovar pagamentos
- Gerar análises manualmente (trigger IA)
- Métricas básicas (usuários, conversão)

### ❌ O QUE NÃO INCLUIR (Fase 2)

- ❌ App Mobile (apenas web responsivo)
- ❌ Múltiplos planos de assinatura
- ❌ Alertas WhatsApp/SMS automatizados
- ❌ Sistema de comunidade/social
- ❌ Histórico avançado e gráficos
- ❌ API pública
- ❌ Análise de odds value
- ❌ Live betting
- ❌ Pagamentos automáticos
- ❌ Sistema de afiliados
- ❌ Relatórios em PDF

---

## 🛠️ STACK TÉCNICO SIMPLIFICADO

### Frontend
```
Framework: Next.js 14 (App Router)
UI: Tailwind CSS + Shadcn/ui
Autenticação: NextAuth.js
Deploy: Vercel (grátis)
```

### Backend
```
API Routes: Next.js API Routes
Banco de Dados: Supabase (grátis até 500MB)
ORM: Prisma
Autenticação: Supabase Auth
```

### IA e Dados
```
IA: Google Gemini API (grátis até 60 req/min)
Dados de Futebol: Football-Data.org (grátis, 10 req/min)
Alternativa: API-Football (tier grátis)
```

### Hospedagem
```
Frontend: Vercel (grátis)
Banco de Dados: Supabase (grátis)
Domínio: Namecheap (~$10/ano)
```

**Custo Mensal Total: ~$50 USD** (domínio + buffer APIs)

---

## 📱 FLUXO DO USUÁRIO (MVP)

### Jornada do Apostador

```
1. DESCOBERTA
   └─> Chega via Facebook/Google Ads
       └─> Landing page betinsight.co.mz

2. INTERESSE
   └─> Vê exemplos de análises
       └─> Entende o valor (previsões com IA)
           └─> Clica "Começar Agora"

3. CADASTRO
   └─> Preenche: Nome, Email, WhatsApp, Senha
       └─> Recebe email de confirmação
           └─> Acessa dashboard (modo trial limitado)

4. TRIAL (3 Análises Grátis)
   └─> Vê lista de jogos disponíveis
       └─> Escolhe 1 jogo para analisar
           └─> IA gera análise em 10 segundos
               └─> Visualiza previsão completa
                   └─> Após 3 análises: "Assine para continuar"

5. PAGAMENTO
   └─> Clica "Assinar - 499 MZN/mês"
       └─> Vê instruções de pagamento M-Pesa:
           • Número: 84XXXXXXX
           • Valor: 499 MZN
           • Referência: [USER_ID]
       └─> Faz pagamento no M-Pesa
           └─> Envia comprovante via WhatsApp ou upload
               └─> Aguarda aprovação (1-24h)

6. USO ATIVO
   └─> Conta ativada
       └─> Análises ilimitadas
           └─> Verifica diariamente
               └─> Testa recomendações
                   └─> (espera-se) Vê resultados positivos

7. RENOVAÇÃO
   └─> Recebe lembrete 3 dias antes de expirar
       └─> Renova se satisfeito
           └─> (ou) Cancela e churn
```

---

## 🎨 WIREFRAMES E TELAS

### 1. Landing Page
```
┌─────────────────────────────────────┐
│  LOGO        [Entrar] [Começar]     │
├─────────────────────────────────────┤
│                                     │
│    APOSTE COM INTELIGÊNCIA          │
│    Análises de IA para Apostadores  │
│                                     │
│    [Começar Grátis - 3 Análises]   │
│                                     │
├─────────────────────────────────────┤
│  Como Funciona:                     │
│  1. Escolha um jogo                 │
│  2. IA analisa em segundos          │
│  3. Receba recomendação             │
│                                     │
├─────────────────────────────────────┤
│  Exemplo de Análise:                │
│  [Screenshot mockup]                │
│                                     │
├─────────────────────────────────────┤
│  Preço: 499 MZN/mês                │
│  [Ver Planos]                       │
│                                     │
└─────────────────────────────────────┘
```

### 2. Dashboard do Usuário
```
┌─────────────────────────────────────┐
│  Bem-vindo, João!                   │
│  Plano: Premium (expira 28/01)      │
├─────────────────────────────────────┤
│                                     │
│  JOGOS DE HOJE (15)                 │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ⚽ Man United vs Liverpool  │   │
│  │ Premier League | 20:00      │   │
│  │ [Ver Análise com IA]        │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ⚽ Benfica vs Porto          │   │
│  │ Liga Portugal | 21:30       │   │
│  │ [Ver Análise com IA]        │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Carregar mais...]                 │
│                                     │
└─────────────────────────────────────┘
```

### 3. Página de Análise
```
┌─────────────────────────────────────┐
│  ⚽ Manchester United vs Liverpool   │
│  Premier League | Hoje 20:00        │
├─────────────────────────────────────┤
│                                     │
│  📊 PREVISÃO DA IA                  │
│                                     │
│  ┌────┬────┬────┐                   │
│  │ 1  │ X  │ 2  │                   │
│  ├────┼────┼────┤                   │
│  │35% │25% │40% │                   │
│  └────┴────┴────┘                   │
│                                     │
│  ⭐⭐⭐⭐ Confiança Alta              │
│                                     │
│  💡 RECOMENDAÇÃO                    │
│  Apostar em: Liverpool Vence (2)    │
│  Razão: Melhor forma recente e      │
│  histórico positivo contra Man Utd  │
│                                     │
├─────────────────────────────────────┤
│  📈 FORMA RECENTE                   │
│                                     │
│  Man United: D-V-E-D-D              │
│  Liverpool:  V-V-V-E-V              │
│                                     │
├─────────────────────────────────────┤
│  🔄 CONFRONTOS DIRETOS (H2H)        │
│                                     │
│  Últimos 5 jogos:                   │
│  Liverpool 3 vitórias               │
│  Empates 1                          │
│  Man United 1 vitória               │
│                                     │
├─────────────────────────────────────┤
│  📊 ESTATÍSTICAS-CHAVE              │
│                                     │
│  Gols marcados (média):             │
│  Man United: 1.2 | Liverpool: 2.1   │
│                                     │
│  Gols sofridos:                     │
│  Man United: 1.8 | Liverpool: 0.9   │
│                                     │
└─────────────────────────────────────┘
```

---

## 💻 ESTRUTURA DO CÓDIGO

### Estrutura de Pastas
```
bet-insight-mvp/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── analysis/
│   │   │   └── [matchId]/
│   │   │       └── page.tsx
│   │   ├── subscription/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── (admin)/
│   │   └── admin/
│   │       └── page.tsx
│   ├── api/
│   │   ├── auth/
│   │   │   └── [...nextauth]/
│   │   │       └── route.ts
│   │   ├── matches/
│   │   │   └── route.ts
│   │   ├── analysis/
│   │   │   └── [matchId]/
│   │   │       └── route.ts
│   │   └── payments/
│   │       └── route.ts
│   ├── layout.tsx
│   └── page.tsx (Landing)
├── components/
│   ├── ui/
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── input.tsx
│   ├── MatchCard.tsx
│   ├── AnalysisResult.tsx
│   └── PaymentInstructions.tsx
├── lib/
│   ├── db.ts (Prisma client)
│   ├── gemini.ts (IA integration)
│   ├── football-api.ts
│   └── utils.ts
├── prisma/
│   └── schema.prisma
├── public/
│   └── images/
├── .env.local
├── package.json
└── README.md
```

### Schema do Banco de Dados (Prisma)
```prisma
// prisma/schema.prisma

model User {
  id            String    @id @default(cuid())
  email         String    @unique
  name          String
  phone         String
  password      String
  createdAt     DateTime  @default(now())
  subscription  Subscription?
  analyses      Analysis[]
  freeAnalysisCount Int @default(3)
}

model Subscription {
  id            String    @id @default(cuid())
  userId        String    @unique
  user          User      @relation(fields: [userId], references: [id])
  status        String    // active, pending, expired
  startDate     DateTime
  endDate       DateTime
  amount        Float
  paymentProof  String?
  createdAt     DateTime  @default(now())
}

model Match {
  id            String    @id @default(cuid())
  apiId         String    @unique
  homeTeam      String
  awayTeam      String
  league        String
  date          DateTime
  status        String    // scheduled, live, finished
  createdAt     DateTime  @default(now())
  analyses      Analysis[]
}

model Analysis {
  id            String    @id @default(cuid())
  matchId       String
  match         Match     @relation(fields: [matchId], references: [id])
  userId        String
  user          User      @relation(fields: [userId], references: [id])
  prediction    Json      // {home: 35, draw: 25, away: 40}
  recommendation String
  confidence    Int       // 1-5
  reasoning     String
  stats         Json
  createdAt     DateTime  @default(now())
}
```

---

## 🤖 LÓGICA DA IA (Gemini)

### Prompt Template para Análise
```javascript
const analysisPrompt = `
Você é um especialista em análise de apostas de futebol. Analise a partida e forneça uma previsão estruturada.

JOGO: ${homeTeam} vs ${awayTeam}
LIGA: ${league}
DATA: ${matchDate}

DADOS DISPONÍVEIS:
- Forma recente Home: ${homeForm}
- Forma recente Away: ${awayForm}
- Últimos confrontos H2H: ${h2hHistory}
- Estatísticas: ${stats}

FORNEÇA A ANÁLISE NO SEGUINTE FORMATO JSON:
{
  "prediction": {
    "home": 35,    // probabilidade %
    "draw": 25,
    "away": 40
  },
  "recommendation": "Apostar em Liverpool Vence (2)",
  "confidence": 4,  // 1-5 estrelas
  "reasoning": "Liverpool está em melhor forma e tem vantagem histórica",
  "keyPoints": [
    "Liverpool venceu 3 dos últimos 5 confrontos",
    "Man United sofreu 7 gols nos últimos 3 jogos",
    "Liverpool tem a melhor defesa da liga"
  ]
}

Seja conciso, objetivo e baseie-se nos dados fornecidos.
`;
```

### Código de Integração
```typescript
// lib/gemini.ts

import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

export async function generateAnalysis(matchData: any) {
  const model = genAI.getGenerativeModel({ model: "gemini-pro" });
  
  const prompt = buildPrompt(matchData);
  const result = await model.generateContent(prompt);
  const response = await result.response;
  const text = response.text();
  
  // Parse JSON from response
  const analysis = JSON.parse(text);
  
  return analysis;
}

function buildPrompt(data: any): string {
  // Construir prompt com dados do jogo
  return `...`;
}
```

---

## 📈 MÉTRICAS DE VALIDAÇÃO

### Semana 1-2: Validação de Interesse
- [ ] 100 visitas na landing page
- [ ] 20% taxa de cadastro (20 usuários)
- [ ] 10 usuários usam as 3 análises grátis

### Semana 3-4: Validação de Conversão
- [ ] 10% convertem para pagantes (2 de 20)
- [ ] Taxa de acerto das previsões > 55%
- [ ] Tempo médio na plataforma > 5 min

### Semana 5-8: Validação de Retenção
- [ ] 50 usuários pagantes totais
- [ ] 70% renovam no segundo mês
- [ ] NPS > 40 (satisfação)
- [ ] 5+ depoimentos positivos

### Métricas de IA
- **Acurácia:** > 60% das previsões corretas
- **Confiança:** Correlação entre estrelas e acerto
- **Tempo de resposta:** < 15 segundos por análise

---

## 💰 ORÇAMENTO MVP

### Custos de Desenvolvimento
```
Desenvolvedor Full-Stack (6 semanas):  $3,000 USD
Designer UI/UX (freelancer):            $500 USD
Testing e QA:                           $300 USD
---------------------------------------------------
TOTAL DESENVOLVIMENTO:                 $3,800 USD
```

### Custos Operacionais (Primeiros 3 Meses)
```
Domínio (.co.mz):                       $30 USD
Hospedagem (Vercel/Supabase - free):    $0 USD
APIs (Football-Data free tier):         $0 USD
Gemini API (free tier):                 $0 USD
M-Pesa fees (5% receita):               ~$75 USD
Marketing Digital:                      $500 USD
---------------------------------------------------
TOTAL OPERACIONAL (3 meses):           $605 USD
```

### INVESTIMENTO TOTAL MVP: $4,405 USD

### Projeção de Receita (60 dias)
```
Meta: 50 usuários × 499 MZN = 24,950 MZN
Conversão USD (1 USD = 64 MZN): ~$390 USD

Break-even: Mês 12 (acumulado)
```

---

## 🚀 CRONOGRAMA DE DESENVOLVIMENTO

### Semana 1: Fundação
- [ ] Setup Next.js + Supabase
- [ ] Configurar Prisma e schema
- [ ] Autenticação básica (registro/login)
- [ ] Landing page
- [ ] Deploy inicial na Vercel

### Semana 2: Core Features
- [ ] Integração Football-Data API
- [ ] Integração Google Gemini
- [ ] Endpoint de análise de jogos
- [ ] Dashboard com lista de jogos

### Semana 3: Análise e UI
- [ ] Página de análise completa
- [ ] Lógica de "3 análises grátis"
- [ ] UI/UX refinamento
- [ ] Página de assinatura

### Semana 4: Pagamentos e Admin
- [ ] Sistema de pagamento M-Pesa (manual)
- [ ] Painel admin básico
- [ ] Gestão de assinaturas
- [ ] Email notifications (transacional)

### Semana 5: Testes e Refinamento
- [ ] Testes com 10 beta testers
- [ ] Correção de bugs
- [ ] Otimização de prompts IA
- [ ] Melhoria de performance

### Semana 6: Lançamento
- [ ] Campanha de marketing
- [ ] Lançamento oficial
- [ ] Suporte ativo
- [ ] Coleta de feedback

---

## 🎯 ESTRATÉGIA DE LANÇAMENTO

### Fase 1: Beta Fechado (Dias 1-14)
- **Objetivo:** 20 usuários beta
- **Tática:** Grupos de WhatsApp de apostadores
- **Oferta:** Grátis por 30 dias
- **Meta:** Coletar feedback e ajustar

### Fase 2: Soft Launch (Dias 15-30)
- **Objetivo:** 50 usuários pagantes
- **Tática:** 
  - Facebook Ads (50 MZN/dia)
  - Posts em grupos de futebol
  - Influencers locais (micro)
- **Oferta:** 50% desconto no primeiro mês
- **Meta:** Validar conversão

### Fase 3: Ajustes e Scale (Dias 31-60)
- **Objetivo:** Otimizar e crescer
- **Tática:**
  - Dobrar budget de marketing
  - Implementar feedback
  - Melhorar taxa de acerto da IA
- **Meta:** Confirmar product-market fit

---

## ✅ CRITÉRIOS DE SUCESSO DO MVP

### ✅ SUCESSO (Próximos Passos: Escalar)
- 50+ usuários pagantes
- Churn < 30%
- Taxa de acerto IA > 60%
- NPS > 50
- 10+ depoimentos positivos

### ⚠️ SUCESSO PARCIAL (Ajustar e Iterar)
- 20-49 usuários pagantes
- Churn 30-50%
- Taxa de acerto 55-60%
- Feedback misto

### ❌ FALHA (Pivotar ou Abandonar)
- < 20 usuários pagantes
- Churn > 50%
- Taxa de acerto < 55%
- Feedback negativo consistente
- Problemas legais/regulatórios

---

## 🔄 PLANO DE ITERAÇÃO PÓS-MVP

Se o MVP for bem-sucedido, próximas features por prioridade:

### Iteração 1 (Mês 2)
1. Pagamentos M-Pesa automáticos (API)
2. App mobile (React Native)
3. Notificações push

### Iteração 2 (Mês 3)
4. Mais ligas (adicionar 10+ ligas)
5. Histórico avançado com gráficos
6. Sistema de referência (afiliados)

### Iteração 3 (Mês 4-6)
7. Análise de odds value
8. Sistema de comunidade básico
9. Alertas WhatsApp automatizados
10. Planos de assinatura múltiplos

---

## 📞 PRÓXIMAS AÇÕES IMEDIATAS

### Esta Semana
1. [ ] Registrar domínio betinsight.co.mz
2. [ ] Criar conta Vercel + Supabase
3. [ ] Obter API keys (Football-Data + Gemini)
4. [ ] Criar repositório GitHub
5. [ ] Começar desenvolvimento (Semana 1)

### Semana que Vem
1. [ ] Finalizar landing page
2. [ ] Implementar autenticação
3. [ ] Primeira integração com APIs
4. [ ] Preparar grupos de beta testers

---

## 📊 DASHBOARD DE PROGRESSO

```
┌─────────────────────────────────────┐
│  MVP PROGRESS TRACKER               │
├─────────────────────────────────────┤
│  Desenvolvimento:    [██░░░░] 30%   │
│  Design:             [████░░] 60%   │
│  Integrações:        [█░░░░░] 15%   │
│  Marketing:          [███░░░] 45%   │
│                                     │
│  Beta Testers:       0/20           │
│  Usuários Pagantes:  0/50           │
│  Dias até Launch:    42             │
└─────────────────────────────────────┘
```

---

## 💡 LIÇÕES APRENDIDAS (Atualizar)

> Esta seção será preenchida durante o desenvolvimento

- **O que funcionou:**
  - TBD

- **O que não funcionou:**
  - TBD

- **Surpresas:**
  - TBD

- **Próximas decisões:**
  - TBD

---

*Documento MVP preparado por: GitHub Copilot*  
*Status: Pronto para Desenvolvimento*  
*Início Previsto: Janeiro 2026*  
*Launch Target: Fevereiro 2026*

---

**VAMOS CONSTRUIR! 🚀**
