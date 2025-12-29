# 🤖 MVP BOT - BET INSIGHT MOZAMBIQUE
## Validação através de WhatsApp Bot

---

## 💡 POR QUE UM BOT É MELHOR PARA O MVP?

### ✅ Vantagens do Bot
1. **Desenvolvimento 3x mais rápido** (2 semanas vs 6 semanas)
2. **Custo 70% menor** ($1,200 vs $4,400)
3. **Zero fricção** - Cliente já usa WhatsApp diariamente
4. **Mais natural** - Conversação vs navegação web
5. **Viral orgânico** - Fácil compartilhar com amigos
6. **Notificações nativas** - WhatsApp já tem push
7. **Pagamento integrado** - M-Pesa via WhatsApp Business
8. **Mercado-alvo usa WhatsApp** - 90%+ penetração em Moçambique

### ⚠️ Desvantagens do Bot
1. Limitações de interface (sem gráficos complexos)
2. Depende da API do WhatsApp
3. Menos "profissional" que site
4. Dificultar monetização inicial (sem paywall tradicional)

---

## 🎯 ESCOPO DO BOT MVP

### Como Funciona (Fluxo do Usuário)

```
USUÁRIO                           BOT
   │                              │
   │  "Oi"                        │
   │──────────────────────────────>│
   │                              │
   │  Bem-vindo! Sou o Bet Insight │
   │  Seu assistente de apostas    │
   │                              │
   │  Comandos:                   │
   │  /jogos - Ver jogos hoje     │
   │  /analisar - Analisar jogo   │
   │  /ajuda - Ver todos comandos │
   │<──────────────────────────────│
   │                              │
   │  /jogos                      │
   │──────────────────────────────>│
   │                              │
   │  🎯 Jogos de Hoje:           │
   │                              │
   │  1️⃣ Man United vs Liverpool   │
   │     Premier | 20:00          │
   │                              │
   │  2️⃣ Benfica vs Porto          │
   │     Liga PT | 21:30          │
   │                              │
   │  Envie o número para analisar│
   │<──────────────────────────────│
   │                              │
   │  1                           │
   │──────────────────────────────>│
   │                              │
   │  ⚙️ Analisando com IA...      │
   │<──────────────────────────────│
   │                              │
   │  ⚽ Man United vs Liverpool   │
   │                              │
   │  📊 PREVISÃO:                │
   │  🏠 Casa: 35%                │
   │  ⚖️ Empate: 25%              │
   │  ✈️ Fora: 40%                │
   │                              │
   │  ⭐⭐⭐⭐ Confiança Alta        │
   │                              │
   │  💡 RECOMENDAÇÃO:            │
   │  Apostar em Liverpool (2)    │
   │                              │
   │  📈 RAZÃO:                   │
   │  Liverpool em melhor forma   │
   │  e vantagem histórica        │
   │                              │
   │  [Ver Detalhes]              │
   │<──────────────────────────────│
```

---

## 🤖 FUNCIONALIDADES DO BOT

### Comandos Disponíveis

#### 1. `/start` ou "Oi"
- Mensagem de boas-vindas
- Instruções básicas
- Menu de comandos

#### 2. `/jogos` ou `/hoje`
- Lista jogos das próximas 24h
- Top 5 ligas principais
- Formato numerado para fácil seleção

#### 3. `/analisar [número]` ou apenas `1`
- Analisa o jogo escolhido
- Retorna previsão da IA
- Inclui recomendação

#### 4. `/premium` ou `/assinar`
- Informações sobre plano pago
- Instruções de pagamento M-Pesa
- Benefícios do plano

#### 5. `/historico`
- Últimas 10 análises do usuário
- Taxa de acerto das previsões
- Estatísticas pessoais

#### 6. `/ajuda`
- Lista todos comandos
- FAQ
- Suporte

#### 7. `/ligas`
- Escolher ligas específicas
- Filtrar jogos

#### 8. `/alerta [time]`
- Criar alerta para jogo de time específico
- Notificação 2h antes do jogo

---

## 🔓 MODELO FREEMIUM

### ⚪ Plano Grátis (Sempre)
- **3 análises por dia**
- Jogos das 5 principais ligas
- Previsões básicas
- Sem histórico detalhado

### 💚 Plano Premium (399 MZN/mês)
- **Análises ilimitadas**
- Todas as ligas (30+)
- Previsões detalhadas com estatísticas completas
- Histórico completo (30 dias)
- Alertas personalizados
- Suporte prioritário
- Análise de odds value (comparação casas apostas)

### Conversão
```
3 análises grátis/dia → Usuário testa → Vê valor → 
→ Quer mais análises → Clica /premium → Paga M-Pesa → Premium ativado
```

---

## 💻 ARQUITETURA TÉCNICA

### Stack Ultra-Simplificado

```
┌─────────────────────────────────────┐
│         WHATSAPP USER               │
└──────────┬──────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│    WhatsApp Business API            │
│    (Twilio / 360dialog)             │
└──────────┬──────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│      WEBHOOK (API Routes)           │
│      Node.js + Express              │
├─────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐ │
│  │   Bot Logic │  │  IA Handler  │ │
│  │  (Commands) │  │   (Gemini)   │ │
│  └─────────────┘  └──────────────┘ │
│                                     │
│  ┌─────────────┐  ┌──────────────┐ │
│  │  Football   │  │   Payment    │ │
│  │     API     │  │   (M-Pesa)   │ │
│  └─────────────┘  └──────────────┘ │
└──────────┬──────────────────────────┘
           │
           ↓
┌─────────────────────────────────────┐
│     DATABASE (SQLite/PostgreSQL)    │
│  - Users                            │
│  - Subscriptions                    │
│  - Analyses                         │
│  - Matches                          │
└─────────────────────────────────────┘
```

### Tecnologias

#### Backend
```yaml
Runtime: Node.js 20+
Framework: Express.js
Linguagem: TypeScript
WhatsApp: Twilio WhatsApp API
Database: PostgreSQL (Supabase)
ORM: Prisma
IA: Google Gemini
Football API: Football-Data.org
Deploy: Railway / Render (grátis)
```

#### Dependências Principais
```json
{
  "dependencies": {
    "express": "^4.18.2",
    "twilio": "^4.19.0",
    "@google/generative-ai": "^0.1.3",
    "@prisma/client": "^5.7.0",
    "axios": "^1.6.2",
    "node-cron": "^3.0.3"
  }
}
```

---

## 📱 EXEMPLO DE CÓDIGO

### Estrutura de Pastas
```
bet-insight-bot/
├── src/
│   ├── bot/
│   │   ├── handlers/
│   │   │   ├── startHandler.ts
│   │   │   ├── matchesHandler.ts
│   │   │   ├── analyzeHandler.ts
│   │   │   └── premiumHandler.ts
│   │   ├── commands.ts
│   │   └── messageRouter.ts
│   ├── services/
│   │   ├── gemini.service.ts
│   │   ├── football.service.ts
│   │   ├── payment.service.ts
│   │   └── user.service.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   └── validators.ts
│   ├── db/
│   │   └── prisma.ts
│   ├── index.ts
│   └── webhook.ts
├── prisma/
│   └── schema.prisma
├── .env
├── package.json
└── README.md
```

### Código Principal (Webhook)

```typescript
// src/webhook.ts
import express from 'express';
import { MessagingResponse } from 'twilio/lib/twiml/MessagingResponse';
import { handleMessage } from './bot/messageRouter';

const app = express();
app.use(express.urlencoded({ extended: false }));

app.post('/webhook/whatsapp', async (req, res) => {
  const { From, Body } = req.body;
  const userPhone = From.replace('whatsapp:', '');
  const message = Body.trim();

  try {
    const reply = await handleMessage(userPhone, message);
    
    const twiml = new MessagingResponse();
    twiml.message(reply);
    
    res.writeHead(200, { 'Content-Type': 'text/xml' });
    res.end(twiml.toString());
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).send('Error processing message');
  }
});

app.listen(3000, () => {
  console.log('🤖 Bot running on port 3000');
});
```

### Router de Mensagens

```typescript
// src/bot/messageRouter.ts
import { db } from '../db/prisma';
import * as handlers from './handlers';

export async function handleMessage(phone: string, message: string): Promise<string> {
  // Buscar ou criar usuário
  let user = await db.user.findUnique({ where: { phone } });
  
  if (!user) {
    user = await db.user.create({
      data: { phone, freeAnalysisCount: 3 }
    });
    return handlers.startHandler(user);
  }

  // Roteamento de comandos
  const command = message.toLowerCase();

  if (command === '/start' || command === 'oi' || command === 'olá') {
    return handlers.startHandler(user);
  }

  if (command === '/jogos' || command === '/hoje') {
    return await handlers.matchesHandler(user);
  }

  if (command.startsWith('/analisar') || /^\d+$/.test(command)) {
    const matchNumber = command.match(/\d+/)?.[0];
    return await handlers.analyzeHandler(user, matchNumber);
  }

  if (command === '/premium' || command === '/assinar') {
    return handlers.premiumHandler(user);
  }

  if (command === '/historico') {
    return await handlers.historyHandler(user);
  }

  if (command === '/ajuda') {
    return handlers.helpHandler();
  }

  // Comando desconhecido
  return `❓ Comando não reconhecido.\n\nEnvie /ajuda para ver os comandos disponíveis.`;
}
```

### Handler de Análise

```typescript
// src/bot/handlers/analyzeHandler.ts
import { User } from '@prisma/client';
import { db } from '../../db/prisma';
import { geminiService } from '../../services/gemini.service';
import { footballService } from '../../services/football.service';

export async function analyzeHandler(user: User, matchNumber?: string): Promise<string> {
  if (!matchNumber) {
    return '❌ Por favor, especifique o número do jogo.\n\nExemplo: /analisar 1';
  }

  // Verificar limite de análises
  if (!user.isPremium && user.dailyAnalysisCount >= 3) {
    return `⛔ Você atingiu o limite de 3 análises gratuitas hoje.\n\n💎 Assine o plano Premium para análises ilimitadas!\n\nEnvie /premium para saber mais.`;
  }

  // Buscar jogo
  const matches = await footballService.getTodayMatches();
  const match = matches[parseInt(matchNumber) - 1];

  if (!match) {
    return '❌ Jogo não encontrado. Use /jogos para ver os jogos disponíveis.';
  }

  // Enviar mensagem de "carregando"
  await sendWhatsAppMessage(user.phone, '⚙️ Analisando com IA... Aguarde 10 segundos...');

  // Gerar análise com IA
  const analysis = await geminiService.generateAnalysis(match);

  // Salvar análise
  await db.analysis.create({
    data: {
      userId: user.id,
      matchId: match.id,
      prediction: analysis.prediction,
      recommendation: analysis.recommendation,
      confidence: analysis.confidence,
      reasoning: analysis.reasoning
    }
  });

  // Atualizar contador de análises
  await db.user.update({
    where: { id: user.id },
    data: { dailyAnalysisCount: { increment: 1 } }
  });

  // Formatar resposta
  return formatAnalysisResponse(match, analysis, user);
}

function formatAnalysisResponse(match: any, analysis: any, user: User): string {
  const { prediction, recommendation, confidence, reasoning } = analysis;

  const stars = '⭐'.repeat(confidence);
  const remaining = user.isPremium ? '∞' : (3 - user.dailyAnalysisCount);

  return `
⚽ *${match.homeTeam} vs ${match.awayTeam}*
🏆 ${match.league} | 🕐 ${match.time}

📊 *PREVISÃO DA IA:*
🏠 Casa: ${prediction.home}%
⚖️ Empate: ${prediction.draw}%
✈️ Fora: ${prediction.away}%

${stars} *Confiança ${confidence}/5*

💡 *RECOMENDAÇÃO:*
${recommendation}

📈 *RAZÃO:*
${reasoning}

---
Análises restantes hoje: ${remaining}

${!user.isPremium ? '\n💎 Quer análises ilimitadas? /premium' : ''}
`.trim();
}
```

### Serviço de IA (Gemini)

```typescript
// src/services/gemini.service.ts
import { GoogleGenerativeAI } from "@google/generative-ai";

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY!);

export const geminiService = {
  async generateAnalysis(match: any) {
    const model = genAI.getGenerativeModel({ model: "gemini-pro" });

    const prompt = `
Você é um especialista em análise de apostas de futebol para apostadores moçambicanos.

JOGO: ${match.homeTeam} vs ${match.awayTeam}
LIGA: ${match.league}
DATA: ${match.date}

DADOS:
${JSON.stringify(match.stats, null, 2)}

FORNEÇA ANÁLISE EM JSON:
{
  "prediction": {"home": 35, "draw": 25, "away": 40},
  "recommendation": "Apostar em Liverpool (2)",
  "confidence": 4,
  "reasoning": "Liverpool está em melhor forma..."
}

Seja conciso (máximo 3 linhas no reasoning) e direto.
`;

    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();

    // Extrair JSON da resposta
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error('Invalid AI response');

    return JSON.parse(jsonMatch[0]);
  }
};
```

---

## 💰 ORÇAMENTO BOT MVP

### Custos de Desenvolvimento
```
Desenvolvedor Backend (2 semanas):      $1,000 USD
Bot Logic + Integrações:                  $500 USD
Testing e QA:                             $200 USD
---------------------------------------------------
TOTAL DESENVOLVIMENTO:                  $1,700 USD
```

### Custos Operacionais (Mensais)
```
WhatsApp Business API (Twilio):           $20 USD
  └─ 1000 mensagens/mês incluídas
  └─ $0.005 por mensagem adicional

Hospedagem (Railway/Render):              $5 USD
  └─ Free tier para começar

Database (Supabase):                      $0 USD
  └─ Free tier (500MB)

Football API:                             $0 USD
  └─ Free tier (10 req/min)

Gemini API:                               $0 USD
  └─ Free tier (60 req/min)

M-Pesa Integration:                       5% receita
---------------------------------------------------
TOTAL MENSAL FIXO:                       $25 USD
```

### INVESTIMENTO TOTAL: $1,700 USD
**Economia vs Web: $2,700 USD (61% mais barato)**

---

## 📅 CRONOGRAMA BOT MVP

### Semana 1: Setup e Core
- **Dia 1-2:** Setup projeto + Twilio WhatsApp API
- **Dia 3-4:** Sistema de comandos e router
- **Dia 5-7:** Integração Gemini + Football API

### Semana 2: Features e Deploy
- **Dia 8-9:** Sistema de análises e limites
- **Dia 10-11:** Integração M-Pesa (manual)
- **Dia 12-13:** Testes com beta testers
- **Dia 14:** Deploy e lançamento

**PRONTO EM 2 SEMANAS! 🚀**

---

## 🎯 ESTRATÉGIA DE LANÇAMENTO BOT

### Fase 1: Viral Orgânico (Dias 1-7)
1. Criar 10 grupos de WhatsApp de apostadores
2. Adicionar bot aos grupos
3. Fazer 2-3 análises grátis por dia no grupo
4. Membros começam a usar privadamente
5. Boca-a-boca natural

### Fase 2: Referência (Dias 8-14)
1. Implementar comando `/indicar`
2. Quem indicar 3 amigos ganha 1 semana Premium grátis
3. Crescimento exponencial

### Fase 3: Ads Direcionados (Dias 15-30)
1. Facebook Ads para WhatsApp
2. Click-to-WhatsApp ads
3. Budget: 30 MZN/dia

### Aquisição Esperada
```
Semana 1: 50 usuários (orgânico)
Semana 2: 150 usuários (referência)
Semana 3-4: 300 usuários (ads)

Total em 30 dias: 500 usuários
Taxa de conversão (5%): 25 pagantes
Receita: 25 × 399 MZN = 9,975 MZN (~$155 USD)
```

---

## 📊 VANTAGENS DO BOT vs SITE

| Aspecto | Bot WhatsApp | Site/App |
|---------|--------------|----------|
| **Tempo de Dev** | 2 semanas | 6 semanas |
| **Custo** | $1,700 | $4,400 |
| **Fricção** | Zero | Média |
| **Notificações** | Nativas | Push (requer setup) |
| **Viralização** | Fácil (forward) | Difícil (compartilhar link) |
| **Onboarding** | Instantâneo | Cadastro obrigatório |
| **Pagamento** | M-Pesa via chat | Integração complexa |
| **Manutenção** | Simples | Complexa |
| **Escalabilidade** | Alta | Média |
| **Interface** | Limitada | Completa |
| **Profissionalismo** | Médio | Alto |

---

## ⚠️ LIMITAÇÕES DO BOT

### Técnicas
- Mensagens limitadas a texto (emojis OK)
- Sem gráficos interativos
- Dependência da API do WhatsApp
- Limite de mensagens (Twilio cobra após 1000/mês)

### Negócio
- Menos "premium" que um site
- Difícil mostrar múltiplas análises simultaneamente
- Usuário pode esquecer de interagir

### Soluções
1. **Gráficos:** Gerar imagens simples com estatísticas
2. **Interface:** Usar botões do WhatsApp (quick replies)
3. **Engajamento:** Notificações diárias automáticas
4. **Premium feel:** Design cuidadoso das mensagens

---

## 🔄 EVOLUÇÃO: BOT → PLATAFORMA

### Fase 1: Bot MVP (Meses 1-2)
- Validar demanda
- Coletar feedback
- Gerar receita inicial

### Fase 2: Bot + Landing Page (Mês 3)
- Site simples para explicar o serviço
- SEO e credibilidade
- Bot continua sendo principal canal

### Fase 3: Plataforma Completa (Meses 4-6)
- Desenvolver web app
- Bot se torna complemento
- Integração perfeita bot ↔ plataforma

---

## ✅ DECISÃO: BOT OU SITE?

### 🤖 Escolha BOT se:
- ✅ Quer validar rápido (2 semanas)
- ✅ Orçamento limitado ($1,700)
- ✅ Público-alvo usa WhatsApp diariamente
- ✅ Quer crescimento viral orgânico
- ✅ Prioriza MVP mínimo e iteração

### 🌐 Escolha SITE se:
- ✅ Tem orçamento maior ($4,400+)
- ✅ Quer posicionamento premium
- ✅ Precisa de interface rica (gráficos)
- ✅ Vai levantar investimento (site impressiona mais)
- ✅ Tem 6+ semanas para desenvolver

---

## 🎯 RECOMENDAÇÃO FINAL

### 🏆 ESTRATÉGIA IDEAL: HÍBRIDA

**1. Começar com Bot (Mês 1-2)**
- Desenvolvimento: 2 semanas
- Validação: 6 semanas
- Investimento: $1,700
- Meta: 50 usuários pagantes

**2. Se validado, adicionar Site (Mês 3-4)**
- Usar receita do bot para financiar
- Site complementa bot (não substitui)
- Aumenta credibilidade
- Facilita onboarding

**3. Resultado: Melhor dos 2 Mundos**
- Bot para engajamento diário
- Site para análises profundas
- Crescimento sustentável

---

## 📞 PRÓXIMOS PASSOS (BOT)

### Esta Semana
1. [ ] Criar conta Twilio (WhatsApp API)
2. [ ] Obter número WhatsApp Business
3. [ ] Setup projeto Node.js + TypeScript
4. [ ] Testar webhook básico
5. [ ] Implementar comando /start

### Próxima Semana
1. [ ] Integrar Gemini API
2. [ ] Integrar Football-Data API
3. [ ] Implementar análises
4. [ ] Sistema de limites (3/dia)
5. [ ] Testar com 10 amigos

### Semana 3
1. [ ] Integração M-Pesa manual
2. [ ] Sistema de assinaturas
3. [ ] Deploy em produção
4. [ ] Lançamento em grupos

---

## 🚀 CÓDIGO PARA COMEÇAR AGORA

```bash
# 1. Criar projeto
mkdir bet-insight-bot
cd bet-insight-bot
npm init -y

# 2. Instalar dependências
npm install express twilio @google/generative-ai @prisma/client axios dotenv
npm install -D typescript @types/express @types/node ts-node nodemon

# 3. Setup TypeScript
npx tsc --init

# 4. Criar estrutura
mkdir -p src/{bot,services,utils,db}
touch src/index.ts src/webhook.ts

# 5. Configurar .env
echo "TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
GEMINI_API_KEY=your_key
FOOTBALL_API_KEY=your_key
DATABASE_URL=your_db_url" > .env

# 6. Rodar
npm run dev
```

---

**DECISÃO: Você prefere começar com Bot ou Site? 🤔**

*Documento Bot MVP preparado por: GitHub Copilot*  
*Recomendação: Começar com Bot → Adicionar Site depois*  
*ROI: 3x mais rápido e 61% mais barato*
