# 📱 MVP PWA - BET INSIGHT MOZAMBIQUE
## Progressive Web App para Apostadores

---

## 💡 POR QUE PWA É A ESCOLHA PERFEITA?

### ✅ Vantagens do PWA

**Melhor dos 2 Mundos: Web + App Nativo**

1. **Instalável** - Funciona como app no celular (sem Google Play/App Store)
2. **Offline First** - Funciona sem internet (análises salvas)
3. **Push Notifications** - Alertas nativos como app
4. **Leve** - ~2MB vs 50MB+ de app nativo
5. **Zero Fricção** - Basta acessar URL e "Adicionar à tela inicial"
6. **Update Automático** - Sem precisar baixar update
7. **Cross-Platform** - Android + iOS + Desktop com 1 código
8. **SEO** - Google indexa (diferente de app)
9. **Custo Baixo** - Desenvolve 1 vez, roda em todos dispositivos
10. **Performance** - Rápido como app nativo

### 📊 PWA vs Alternativas

| Aspecto | PWA | App Nativo | Site Tradicional | Bot WhatsApp |
|---------|-----|------------|------------------|--------------|
| **Tempo Dev** | 4 semanas | 12 semanas | 6 semanas | 2 semanas |
| **Custo** | $2,500 | $15,000 | $4,400 | $1,700 |
| **Instalação** | 1 click | App Store/Play | N/A | N/A |
| **Offline** | ✅ Sim | ✅ Sim | ❌ Não | ❌ Não |
| **Push Notif** | ✅ Sim | ✅ Sim | ⚠️ Limitado | ✅ Sim |
| **Performance** | ⚡ Alta | ⚡ Alta | ⚠️ Média | ⚡ Alta |
| **Atualização** | Automática | Manual | Automática | Automática |
| **SEO** | ✅ Sim | ❌ Não | ✅ Sim | ❌ Não |
| **Interface** | 🎨 Rica | 🎨 Rica | 🎨 Rica | ⚠️ Limitada |
| **Cross-Platform** | ✅ 1 código | ❌ 2 códigos | ✅ 1 código | ✅ 1 código |

---

## 🎯 ESCOPO DO PWA MVP

### ✅ Funcionalidades Core

#### 1. Landing Page + PWA Install Prompt
- Hero section com proposta de valor
- Banner "Instalar App" (aparece ao visitar)
- Demonstração em vídeo/GIF
- Depoimentos sociais
- Call-to-action claro

#### 2. Autenticação Simples
- Cadastro: Email + Senha (ou Google OAuth)
- Login rápido (salva sessão offline)
- Recuperação de senha
- Perfil básico

#### 3. Dashboard Responsivo
- Jogos de hoje (card-based)
- Filtros por liga
- Status: Analisado / Não analisado
- Skeleton loading (UX premium)

#### 4. Análise com IA (Core)
```
┌─────────────────────────────────┐
│  ⚽ Man United vs Liverpool     │
│  🏆 Premier League | 🕐 20:00   │
├─────────────────────────────────┤
│                                 │
│  📊 PREVISÃO DA IA              │
│                                 │
│  ┌───────────────────────────┐ │
│  │     35%   25%   40%       │ │
│  │    [■■■] [■■] [■■■■]      │ │
│  │     🏠    ⚖️    ✈️        │ │
│  └───────────────────────────┘ │
│                                 │
│  ⭐⭐⭐⭐ Confiança Alta          │
│                                 │
│  💡 RECOMENDAÇÃO                │
│  Apostar em Liverpool (2)       │
│                                 │
│  📈 RAZÃO                       │
│  • Melhor forma recente         │
│  • 3 vitórias nos últimos 5 H2H │
│  • Defesa sólida                │
│                                 │
│  [Ver Estatísticas Completas]   │
│                                 │
└─────────────────────────────────┘
```

#### 5. Sistema de Créditos (Freemium)
- **Grátis:** 5 análises por dia
- **Premium:** Análises ilimitadas (499 MZN/mês)
- Contador visual de créditos
- CTA para upgrade

#### 6. Modo Offline Inteligente
- Análises recentes salvas localmente
- Sync automático quando online
- Indicador de status (online/offline)
- Fila de requests pendentes

#### 7. Push Notifications
- Alertas de jogos importantes (2h antes)
- Novas análises disponíveis
- Lembretes de renovação
- Resultados de apostas sugeridas

#### 8. Pagamento M-Pesa Simplificado
- QR Code para pagamento
- Instruções claras passo-a-passo
- Upload de comprovante
- Ativação automática (webhook M-Pesa)

#### 9. Histórico e Stats
- Últimas 20 análises
- Taxa de acerto (análises vs resultados reais)
- Gráfico de performance
- Filtros por liga/data

#### 10. Instalação PWA
- Prompt automático após 2 visitas
- Tutorial de instalação (Android/iOS)
- Ícone e splash screen customizados
- Standalone mode (sem barra de navegação)

---

## 🛠️ STACK TÉCNICO PWA

### Frontend (PWA)
```yaml
Framework: Next.js 14 (App Router + PWA)
PWA Plugin: next-pwa
UI Framework: Tailwind CSS + Shadcn/ui
Componentes: Radix UI (acessibilidade)
Animações: Framer Motion
Gráficos: Recharts + Chart.js
Estado Global: Zustand (mais leve que Redux)
Offline Storage: IndexedDB (via Dexie.js)
HTTP Client: Axios + SWR (cache automático)
Forms: React Hook Form + Zod
Auth: NextAuth.js
```

### Backend
```yaml
API: Next.js API Routes (serverless)
Database: PostgreSQL (Supabase/Neon)
ORM: Prisma
Autenticação: NextAuth.js + JWT
Cache: Redis (Upstash - serverless)
File Upload: Cloudinary (comprovantes)
```

### Integrações
```yaml
IA: Google Gemini API 1.5 Pro
Football Data: Football-Data.org + API-Football
Pagamentos: M-Pesa API (Vodacom Moçambique)
Notificações: Firebase Cloud Messaging (FCM)
Analytics: Vercel Analytics + Plausible
Monitoring: Sentry (error tracking)
```

### Hospedagem
```yaml
Frontend + API: Vercel (Edge Functions)
Database: Supabase (PostgreSQL + Auth)
Cache: Upstash Redis (serverless)
CDN: Vercel Edge Network
Domínio: betinsight.co.mz
SSL: Automático (Vercel)
```

### PWA Requirements
```yaml
Service Worker: Workbox (next-pwa)
Manifest: Web App Manifest
Icons: 192x192, 512x512 (PNG)
Splash Screens: iOS + Android
Offline Strategy: Cache-First para assets
Background Sync: Análises pendentes
Push API: Service Worker + FCM
Install Prompt: Custom A2HS banner
```

---

## 📱 CARACTERÍSTICAS PWA

### 1. Manifest (manifest.json)
```json
{
  "name": "Bet Insight Mozambique",
  "short_name": "Bet Insight",
  "description": "Análises inteligentes de apostas com IA",
  "start_url": "/dashboard",
  "display": "standalone",
  "background_color": "#10B981",
  "theme_color": "#10B981",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "screenshots": [
    {
      "src": "/screenshots/dashboard.png",
      "sizes": "540x720",
      "type": "image/png"
    }
  ],
  "shortcuts": [
    {
      "name": "Ver Jogos Hoje",
      "url": "/dashboard",
      "icons": [{"src": "/icons/matches.png", "sizes": "96x96"}]
    },
    {
      "name": "Meu Histórico",
      "url": "/historico",
      "icons": [{"src": "/icons/history.png", "sizes": "96x96"}]
    }
  ]
}
```

### 2. Service Worker Strategy
```javascript
// Estratégias de Cache

// 1. App Shell (Cache First)
// HTML, CSS, JS principais
cache.addAll([
  '/',
  '/dashboard',
  '/styles.css',
  '/app.js',
  '/icons/*'
]);

// 2. Análises (Network First + Cache Fallback)
// Sempre tenta buscar novo, fallback para cache
if (online) {
  fetchFromNetwork();
} else {
  returnFromCache();
}

// 3. Assets (Cache First)
// Imagens, logos, fontes
if (inCache) {
  returnFromCache();
} else {
  fetchAndCache();
}

// 4. API Calls (Network Only + Background Sync)
// Sempre online, enfileira se offline
if (offline) {
  queueForBackgroundSync();
}
```

### 3. Offline Capabilities
```typescript
// O que funciona OFFLINE:

✅ Ver análises já carregadas (últimas 20)
✅ Navegar entre páginas do app
✅ Ver histórico pessoal
✅ Ler estatísticas salvas
✅ Interface completa funcional

❌ Gerar novas análises (precisa IA online)
❌ Ver jogos em tempo real
❌ Fazer pagamentos
❌ Atualizar dados
```

### 4. Background Sync
```typescript
// Quando usuário fica offline e tenta fazer ação:

1. Request é salvo em IndexedDB
2. Service Worker monitora conectividade
3. Quando volta online → executa automaticamente
4. Usuário recebe notificação de sucesso

// Exemplo: Tentar analisar jogo offline
userClicksAnalyze() → saveToQueue() → 
→ [OFFLINE] → connectivityRestored() → 
→ processQueue() → generateAnalysis() → 
→ notify("Análise pronta!")
```

### 5. Install Experience
```typescript
// Fluxo de Instalação PWA

// Desktop (Chrome/Edge)
1. Usuário visita site
2. Ícone "+" aparece na barra de URL
3. Click → "Instalar Bet Insight"
4. App abre em janela dedicada

// Mobile Android
1. Usuário visita site
2. Banner aparece: "Adicionar à tela inicial"
3. Click → "Adicionar"
4. Ícone aparece na home screen
5. Abre fullscreen (sem browser)

// Mobile iOS (Safari)
1. Usuário visita site
2. Click no botão "Compartilhar"
3. "Adicionar à Tela de Início"
4. Ícone aparece na home screen
```

---

## 💻 ESTRUTURA DO PROJETO

```
bet-insight-pwa/
├── app/
│   ├── (landing)/
│   │   ├── page.tsx                 # Landing page
│   │   └── layout.tsx
│   ├── (auth)/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── register/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── (app)/
│   │   ├── dashboard/
│   │   │   └── page.tsx             # Lista de jogos
│   │   ├── analise/
│   │   │   └── [id]/
│   │   │       └── page.tsx         # Análise detalhada
│   │   ├── historico/
│   │   │   └── page.tsx
│   │   ├── perfil/
│   │   │   └── page.tsx
│   │   ├── assinatura/
│   │   │   └── page.tsx
│   │   └── layout.tsx               # Layout app (header, nav)
│   ├── api/
│   │   ├── auth/
│   │   │   └── [...nextauth]/
│   │   │       └── route.ts
│   │   ├── matches/
│   │   │   ├── route.ts             # GET jogos
│   │   │   └── [id]/
│   │   │       └── route.ts
│   │   ├── analyze/
│   │   │   └── [matchId]/
│   │   │       └── route.ts         # POST análise
│   │   ├── subscription/
│   │   │   └── route.ts
│   │   └── webhook/
│   │       └── mpesa/
│   │           └── route.ts
│   ├── manifest.ts                  # Web App Manifest
│   ├── layout.tsx                   # Root layout
│   └── globals.css
├── components/
│   ├── ui/                          # Shadcn components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   └── ...
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Navigation.tsx
│   │   └── Footer.tsx
│   ├── dashboard/
│   │   ├── MatchCard.tsx
│   │   ├── FilterBar.tsx
│   │   └── MatchList.tsx
│   ├── analysis/
│   │   ├── PredictionChart.tsx
│   │   ├── StatsDisplay.tsx
│   │   ├── RecommendationCard.tsx
│   │   └── ShareButton.tsx
│   ├── subscription/
│   │   ├── PricingCard.tsx
│   │   ├── PaymentInstructions.tsx
│   │   └── CreditCounter.tsx
│   └── pwa/
│       ├── InstallPrompt.tsx        # A2HS banner
│       ├── OfflineIndicator.tsx
│       └── UpdatePrompt.tsx
├── lib/
│   ├── db/
│   │   └── prisma.ts
│   ├── api/
│   │   ├── gemini.ts
│   │   ├── football.ts
│   │   └── mpesa.ts
│   ├── hooks/
│   │   ├── useOnline.ts
│   │   ├── useInstallPrompt.ts
│   │   ├── usePushNotification.ts
│   │   └── useOfflineQueue.ts
│   ├── store/
│   │   └── store.ts                 # Zustand
│   ├── offline/
│   │   ├── db.ts                    # IndexedDB (Dexie)
│   │   └── sync.ts
│   └── utils.ts
├── public/
│   ├── icons/
│   │   ├── icon-192x192.png
│   │   ├── icon-512x512.png
│   │   └── maskable-icon.png
│   ├── screenshots/
│   │   ├── dashboard.png
│   │   └── analysis.png
│   └── sw.js                        # Service Worker
├── prisma/
│   └── schema.prisma
├── next.config.js                   # PWA config
├── .env.local
├── package.json
└── README.md
```

---

## 🎨 DESIGN E UX

### Princípios de Design PWA

1. **Mobile-First** - Projetado para celular, funciona em desktop
2. **Thumb-Friendly** - Botões grandes, fáceis de tocar
3. **Fast & Smooth** - Animações suaves, loading mínimo
4. **Progressive Enhancement** - Funciona sem JS, melhor com JS
5. **Accessible** - WCAG 2.1 AA compliant

### Paleta de Cores
```css
/* Modern & Trustworthy */
--primary: #10B981;      /* Verde - Sucesso */
--secondary: #3B82F6;    /* Azul - Confiança */
--accent: #F59E0B;       /* Laranja - Ação */
--success: #22C55E;
--warning: #EAB308;
--error: #EF4444;
--background: #FFFFFF;
--surface: #F9FAFB;
--text: #111827;
--text-muted: #6B7280;
```

### Typography
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
```

### Componentes-Chave

#### Match Card
```tsx
<MatchCard>
  <Badge>Premier League</Badge>
  <Teams>
    <Team logo={home.logo}>{home.name}</Team>
    <vs>VS</vs>
    <Team logo={away.logo}>{away.name}</Team>
  </Teams>
  <DateTime>Hoje • 20:00</DateTime>
  <Button>Analisar com IA</Button>
  {analyzed && <Badge variant="success">✓ Analisado</Badge>}
</MatchCard>
```

#### Install Banner
```tsx
<InstallBanner>
  <Icon>📱</Icon>
  <Text>
    Instale o app para acesso rápido e notificações
  </Text>
  <Button onClick={promptInstall}>Instalar</Button>
  <CloseButton />
</InstallBanner>
```

---

## 💰 ORÇAMENTO PWA MVP

### Custos de Desenvolvimento
```
Full-Stack Developer (4 semanas):      $2,000 USD
UI/UX Design (PWA específico):           $400 USD
PWA Setup (Service Worker, etc):         $300 USD
Testing (devices reais):                 $200 USD
---------------------------------------------------
TOTAL DESENVOLVIMENTO:                 $2,900 USD
```

### Custos Operacionais (Mensais)
```
Vercel Pro (melhor performance):          $20 USD
Supabase (Database + Auth):               $25 USD
Upstash Redis (Cache):                    $10 USD
Firebase (Push Notifications):            $10 USD
APIs:
  ├─ Football-Data (free tier):           $0 USD
  ├─ Gemini (free → $20 após scale):      $0 USD
  └─ M-Pesa (5% receita):                 variável
Cloudinary (upload de imagens):           $0 USD (free)
Domínio (.co.mz):                         $3 USD
---------------------------------------------------
TOTAL MENSAL FIXO:                       $68 USD
```

### INVESTIMENTO TOTAL: $2,900 USD

---

## 📅 CRONOGRAMA PWA MVP

### Semana 1: Fundação
- **Dias 1-2:** Setup Next.js + PWA config
- **Dias 3-4:** Design system (Tailwind + Shadcn)
- **Dias 5-7:** Autenticação + Database schema

### Semana 2: Core Features
- **Dias 8-9:** Dashboard + lista de jogos
- **Dias 10-11:** Integração APIs (Football + Gemini)
- **Dias 12-14:** Página de análise completa

### Semana 3: PWA Features
- **Dias 15-16:** Service Worker + Offline mode
- **Dias 17-18:** Install prompt + Manifest
- **Dias 19-21:** Push notifications + Background sync

### Semana 4: Payment & Polish
- **Dias 22-23:** Integração M-Pesa
- **Dias 24-25:** Sistema de créditos/assinatura
- **Dias 26-27:** Testing em devices reais
- **Dia 28:** Deploy produção + soft launch

---

## 🚀 ESTRATÉGIA DE LANÇAMENTO

### Fase 1: Soft Launch (Dias 1-7)
**Objetivo:** 50 usuários beta

**Táticas:**
- Compartilhar link em grupos WhatsApp
- Posts no Facebook (grupos de apostadores)
- Amigos e família testam
- Coletar feedback intensivo

**Oferta:**
- 30 dias grátis de Premium
- Acesso antecipado

### Fase 2: Public Launch (Dias 8-30)
**Objetivo:** 200 usuários / 20 pagantes

**Táticas:**
- **Facebook Ads:** 100 MZN/dia
  - Target: Homens 18-45, Maputo/Matola
  - Interesse: Futebol, Apostas, Premier League
- **Instagram Stories:** Demonstração do PWA
- **Google Ads:** Keywords "apostas futebol moçambique"
- **Influencers:** 2-3 micro-influencers locais

**Mensagens-chave:**
- "Como um app, mas sem precisar baixar"
- "Análises de IA em segundos"
- "Primeiro mês 50% desconto"

### Fase 3: Growth (Mês 2-3)
**Objetivo:** 1000 usuários / 100 pagantes

**Táticas:**
- Sistema de referência (indica amigo → 1 semana grátis)
- Content marketing (blog com dicas)
- Parcerias com sites de futebol
- Remarketing ads

---

## 📊 MÉTRICAS DE VALIDAÇÃO

### Métricas Técnicas (PWA)
- **Install Rate:** > 30% após 3 visitas
- **Offline Usage:** > 10% das sessões
- **Push Opt-in:** > 40% dos usuários
- **Load Time:** < 2 segundos (4G)
- **Lighthouse Score:** > 90/100 (todas categorias)

### Métricas de Negócio
- **DAU/MAU:** > 40%
- **Session Duration:** > 8 minutos
- **Analyses per User:** > 5/dia (premium)
- **Conversion Rate:** > 8% (free → paid)
- **Churn Rate:** < 20% mensal

### Metas de Crescimento (60 dias)
```
Semana 1-2: 50 usuários (beta)
Semana 3-4: 150 usuários (+100)
Semana 5-6: 350 usuários (+200)
Semana 7-8: 600 usuários (+250)

Total 60 dias: 600 usuários
Conversão (10%): 60 pagantes
Receita Mensal: 60 × 499 MZN = 29,940 MZN (~$470 USD)
```

---

## 🔧 CÓDIGO EXEMPLO

### Next.js PWA Config
```javascript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
  runtimeCaching: [
    {
      urlPattern: /^https:\/\/api\.betinsight\.co\.mz\/.*$/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'api-cache',
        expiration: {
          maxEntries: 100,
          maxAgeSeconds: 60 * 60 // 1 hora
        }
      }
    },
    {
      urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp)$/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'images-cache',
        expiration: {
          maxEntries: 50,
          maxAgeSeconds: 30 * 24 * 60 * 60 // 30 dias
        }
      }
    }
  ]
});

module.exports = withPWA({
  reactStrictMode: true,
  // ... outras configs
});
```

### Install Prompt Component
```tsx
// components/pwa/InstallPrompt.tsx
'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { X } from 'lucide-react';

export function InstallPrompt() {
  const [showPrompt, setShowPrompt] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      
      // Mostrar após 2 visitas
      const visitCount = parseInt(localStorage.getItem('visitCount') || '0');
      if (visitCount >= 2) {
        setShowPrompt(true);
      }
      localStorage.setItem('visitCount', String(visitCount + 1));
    };

    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      console.log('PWA instalado!');
    }
    
    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  if (!showPrompt) return null;

  return (
    <div className="fixed bottom-4 left-4 right-4 bg-white rounded-lg shadow-xl p-4 z-50 border-2 border-primary">
      <button 
        onClick={() => setShowPrompt(false)}
        className="absolute top-2 right-2"
      >
        <X className="w-5 h-5" />
      </button>
      
      <div className="flex items-start gap-3">
        <span className="text-3xl">📱</span>
        <div className="flex-1">
          <h3 className="font-bold text-lg">Instalar Bet Insight</h3>
          <p className="text-sm text-gray-600 mt-1">
            Acesso rápido, notificações e funciona offline!
          </p>
          <Button 
            onClick={handleInstall}
            className="mt-3 w-full"
          >
            Instalar App
          </Button>
        </div>
      </div>
    </div>
  );
}
```

### Offline Hook
```tsx
// lib/hooks/useOnline.ts
'use client';

import { useState, useEffect } from 'react';

export function useOnline() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    setIsOnline(navigator.onLine);

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}
```

### Offline Indicator Component
```tsx
// components/pwa/OfflineIndicator.tsx
'use client';

import { useOnline } from '@/lib/hooks/useOnline';
import { WifiOff, Wifi } from 'lucide-react';

export function OfflineIndicator() {
  const isOnline = useOnline();

  if (isOnline) return null;

  return (
    <div className="fixed top-0 left-0 right-0 bg-yellow-500 text-white px-4 py-2 text-center text-sm font-medium z-50">
      <WifiOff className="inline w-4 h-4 mr-2" />
      Você está offline. Algumas funcionalidades estão limitadas.
    </div>
  );
}
```

---

## ✅ CHECKLIST PWA

### Requisitos Técnicos
- [ ] HTTPS obrigatório
- [ ] Service Worker registrado
- [ ] Manifest.json configurado
- [ ] Ícones (192x192, 512x512)
- [ ] Splash screens (iOS)
- [ ] Funciona offline (pelo menos shell)
- [ ] Responsivo (mobile + desktop)
- [ ] Install prompt implementado
- [ ] Background sync
- [ ] Push notifications
- [ ] Fast (< 3s load)
- [ ] Lighthouse score > 90

### Testes Necessários
- [ ] Testar instalação (Chrome Android)
- [ ] Testar instalação (Safari iOS)
- [ ] Testar offline mode
- [ ] Testar push notifications
- [ ] Testar background sync
- [ ] Testar em 4G lento
- [ ] Testar em diversos devices
- [ ] Validar manifest (Chrome DevTools)

---

## 🎯 VANTAGENS DO PWA vs SITE TRADICIONAL

### Para o Usuário
✅ Instala com 1 click (sem App Store)
✅ Ícone na tela inicial
✅ Abre fullscreen (parece app nativo)
✅ Funciona offline
✅ Recebe notificações
✅ Mais rápido (cache inteligente)
✅ Usa menos dados

### Para o Negócio
✅ 1 código = Android + iOS + Desktop
✅ Update instantâneo (sem aprovação de store)
✅ SEO (Google indexa)
✅ Menor custo de desenvolvimento
✅ Menor custo de manutenção
✅ Analytics mais fácil
✅ Conversion rate maior (sem fricção de install)

---

## 📞 PRÓXIMOS PASSOS

### Esta Semana
1. [ ] Registrar domínio betinsight.co.mz
2. [ ] Criar contas (Vercel, Supabase, Firebase)
3. [ ] Obter API keys (Gemini, Football-Data)
4. [ ] Setup projeto Next.js + PWA
5. [ ] Design de ícones e logos

### Próxima Semana
1. [ ] Implementar autenticação
2. [ ] Criar dashboard básico
3. [ ] Integrar APIs (Football + IA)
4. [ ] Primeira análise funcional
5. [ ] Deploy em staging

### Semana 3
1. [ ] Configurar Service Worker
2. [ ] Implementar offline mode
3. [ ] Install prompt
4. [ ] Push notifications
5. [ ] Testes em devices reais

### Semana 4
1. [ ] Integração M-Pesa
2. [ ] Sistema de créditos
3. [ ] Polimento UI/UX
4. [ ] Deploy produção
5. [ ] Soft launch

---

## 🚀 COMANDO PARA COMEÇAR

```bash
# 1. Criar projeto Next.js com PWA
npx create-next-app@latest bet-insight-pwa --typescript --tailwind --app
cd bet-insight-pwa

# 2. Instalar dependências PWA
npm install next-pwa
npm install @prisma/client prisma
npm install next-auth
npm install zustand
npm install dexie
npm install @google/generative-ai axios swr
npm install framer-motion
npm install recharts
npm install react-hook-form @hookform/resolvers zod

# 3. Instalar Shadcn UI
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input label dialog

# 4. Setup Prisma
npx prisma init

# 5. Rodar desenvolvimento
npm run dev

# 6. Acessar https://localhost:3000
```

---

**DECISÃO CONFIRMADA: PWA é a melhor escolha! 🎯**

- ✅ Funciona como app (instalável)
- ✅ Custo moderado ($2,900)
- ✅ 4 semanas de desenvolvimento
- ✅ Offline + Push notifications
- ✅ Cross-platform (1 código)
- ✅ SEO + Performance

*Pronto para começar o desenvolvimento?* 🚀

---

*Documento PWA MVP preparado por: GitHub Copilot*  
*Tecnologia: Next.js 14 + PWA + Vercel*  
*Timeline: 4 semanas*  
*Status: Pronto para implementar*
