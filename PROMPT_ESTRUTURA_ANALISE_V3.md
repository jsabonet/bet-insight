# 📋 PROMPT: Estrutura, Layout e Design das Análises de IA v3.0

## 🎯 OBJETIVO PRINCIPAL

Criar um **motor de decisão profissional** para apostas esportivas, onde o usuário entende **a melhor aposta em até 3 segundos**, com:

- **Clareza visual máxima**
- **Confiança baseada em dados**
- **Hierarquia de informação clara**
- **Experiência premium (desktop + mobile)**

A análise não deve parecer texto de chatbot, e sim **conteúdo editorial de plataforma de análise esportiva profissional**.

---

## 🧠 FILOSOFIA DO PRODUTO (OBRIGATÓRIO)

✅ **A decisão vem antes da explicação**  
✅ **Texto longo só para quem quiser ler**  
✅ **Tudo responde: "Em que apostar e por quê?"**  
✅ **Clareza > criatividade**  
✅ **Linguagem profissional, não promocional**  
✅ **Orientação baseada em dados, não imposição**

---

## 🎨 MELHORIAS DE PRODUCT DESIGN APLICADAS

### 🔥 Decisão em 3 Segundos
- Hero section com previsão + probabilidade + placar
- **Micro-alerta de risco discreto mas visível** ⚠️ NOVO
- Leitura instantânea em menos de 5 segundos
- Otimização total para mobile (empilhamento vertical)

### ⚡ Escaneabilidade Máxima
- Bullets curtos e persuasivos (1 linha cada)
- **Fatores-chave destacados em negrito** (`**Forma:**`, `**H2H:**`) ⚡ NOVO
- Números em badges visuais (automático)
- Hierarquia visual forte com emojis estruturais

### 📊 Visualização Profissional
- Probabilidades com números grandes e comparáveis
- **Interpretação rápida incluída** 💡 NOVO
- Cores neutras e profissionais
- Preparado para barras visuais (implementação futura)

### 📚 Profundidade Opcional
- **Resumo executivo sempre visível** 📋 NOVO
- Análise detalhada preparada para collapse (implementação futura)
- Fluxo de leitura otimizado para mobile
- Zero redundância entre seções

### 💰 Recomendação Acionável
- **Tipo de aposta identificado** (Conservadora/Equilibrada/Agressiva) 🆕 NOVO
- **Gestão de risco** sem quebrar confiança ⚠️ NOVO
- **Alternativa** para usuários avançados 💡 NOVO
- Linguagem orientadora, não impositiva

---

## 🧱 ESTRUTURA FINAL OBRIGATÓRIA (ORDEM NÃO PODE MUDAR)

### 🔥 BLOCO 1 — DECISÃO IMEDIATA (HERO)

**Este é o DESTAQUE PRINCIPAL. Leitura em menos de 5 segundos.**

```markdown
🎯 PREVISÃO DA IA

**{RESULTADO MAIS PROVÁVEL}**

📊 Probabilidade: {XX}%
⚽ Placar esperado: {X:X}

⭐ Confiança: {1-5 estrelas} ({Alta | Média | Baixa})
⚠️ Risco: {Baixo | Médio | Alto}
```

**Melhorias aplicadas:**
- ✅ Micro-alerta de risco adicionado
- ✅ Probabilidade em destaque (número grande)
- ✅ Estrelas de confiança padronizadas com tooltip
- ✅ ZERO introduções ou enrolação
- ✅ Otimizado para leitura rápida em mobile

**Regras:**
- Uma única previsão clara e direta
- Sem texto explicativo neste bloco
- NÃO comece com introdução genérica

---

### ⚡ BLOCO 2 — FATORES-CHAVE DA DECISÃO

**Máximo 3-4 bullets. Cada um persuasivo e escaneável.**

```markdown
⚡ POR QUE ESSA PREVISÃO?

✓ **Forma recente:** {Insight objetivo com dado numérico}
✓ **Confronto direto:** {Padrão histórico relevante}
✓ **Análise tática:** {Vantagem competitiva clara}
✓ **Modelo estatístico:** {Resultado Poisson/xG se disponível}
```

**Melhorias aplicadas:**
- ✅ Fatores destacados em negrito antes da explicação
- ✅ Formato padronizado: **Fator:** Explicação
- ✅ Máximo 1 linha por bullet
- ✅ Evita números excessivos em uma frase
- ✅ Linguagem persuasiva mas profissional

**Regras:**
- Cada bullet: 1 linha máxima
- Dados concretos sempre que possível
- Nada de introduções genéricas

---

### 📊 BLOCO 3 — PROBABILIDADES VISUAIS

**Priorize entendimento instantâneo. Números grandes e comparáveis.**

```markdown
📊 PROBABILIDADES

🏠 **{TIME_CASA}:** {XX}%
🤝 **Empate:** {XX}%
✈️ **{TIME_FORA}:** {XX}%

---
💡 **Interpretação rápida:** {Uma frase explicando o cenário mais provável}
```

**Melhorias aplicadas:**
- ✅ Percentuais grandes e destacados
- ✅ Linha de interpretação rápida adicionada
- ✅ Facilita comparação visual entre cenários
- ✅ Mobile: empilhamento vertical automático
- ✅ Preparado para barras gráficas (implementação futura)

**Regras:**
- Percentuais obrigatórios
- Soma DEVE ser 100%
- Sem explicações longas (apenas interpretação de 1 linha)

**Implementação futura (frontend):**
- Barras horizontais com cores neutras
- Indicadores visuais de probabilidade
- Hover tooltips com detalhes

---

### 📚 BLOCO 4 — ANÁLISE DETALHADA (SECUNDÁRIO)

**Profundidade analítica para quem quer aprofundar. Estrutura colapsável.**

```markdown
**📋 RESUMO EXECUTIVO**
{2-3 frases com contexto essencial do jogo. Sempre visível, não colapsa.}

---

**1️⃣ ANÁLISE DE FORMA**

🏠 **Casa – {TIME_CASA}**
• Últimos 5 jogos: {Resumo com W-D-L}
• Desempenho em casa: {Estatística relevante}
• Momento atual: {Tendência clara}

✈️ **Fora – {TIME_FORA}**
• Últimos 5 jogos: {Resumo com W-D-L}
• Desempenho fora: {Estatística relevante}
• Momento atual: {Tendência clara}

---

**2️⃣ CONFRONTOS DIRETOS (H2H)**
• Histórico: {X vitórias casa, Y empates, Z vitórias fora}
• Padrão identificado: {Tendência relevante}
• Contexto: {Informação que muda a leitura dos números}

---

**3️⃣ ANÁLISE TÁTICA E ESTATÍSTICA**
• **Ataque vs Defesa:** {Comparação de médias de gols}
• **Estilo de jogo:** {Como os estilos se complementam/conflitam}
• **Fator decisivo:** {O que pode definir o jogo}
• **xG e Poisson:** {Resultado de modelos estatísticos}
```

**Melhorias aplicadas:**
- ✅ Resumo executivo separado e sempre visível
- ✅ Restante preparado para accordion/collapse (implementação futura)
- ✅ Evita redundância entre seções
- ✅ Fluxo de leitura otimizado para mobile
- ✅ Mantém profundidade sem perder clareza

**Regras:**
- Resumo executivo: 2-3 frases máximo
- Cada subseção: máximo 3-4 bullets
- Linguagem técnica mas acessível

**Implementação futura (frontend):**
- Accordion/collapse para seções 1️⃣ 2️⃣ 3️⃣
- Primeira seção aberta por padrão
- Animação suave de expansão/colapso
- Ícone de expandir/colapsar (chevron)

---

### 💰 BLOCO 5 — RECOMENDAÇÃO FINAL

**Acionável, coerente com os dados, sem imposição.**

```markdown
💰 RECOMENDAÇÃO

**Aposta sugerida:** {Mercado específico + seleção}
**Tipo:** {Conservadora | Equilibrada | Agressiva}

✅ **Justificativa:** {Por que esta aposta faz sentido}
⚠️ **Gestão de risco:** {Como minimizar perdas ou maximizar value}

💡 **Alternativa:** {Segunda melhor opção, se houver}
```

**Melhorias aplicadas:**
- ✅ Tipo de aposta identificado (perfil de risco)
- ✅ Gestão de risco sem quebrar confiança
- ✅ Alternativa para usuários avançados
- ✅ Linguagem orientadora, não impositiva
- ✅ Justificativa alinhada com análise apresentada

**Regras:**
- Recomendação clara e específica
- Indicar perfil: Conservadora (odds baixas), Equilibrada (odds médias), Agressiva (odds altas)
- Alternativa opcional
- Sem promessas irreais

---

## ✍️ REGRAS DE FORMATAÇÃO (MUITO IMPORTANTE)

### ✔ Negrito (**texto**)

**Use para:**
- Nomes dos times
- Fatores-chave (**Forma recente:**, **Ataque vs Defesa:**)
- Resultados finais e recomendações
- Subtítulos importantes

**Não use para:**
- Palavras aleatórias no meio do texto
- Ênfase excessiva

### ✔ Números e Percentuais

**Sempre inclua:**
- Percentuais (65%)
- Sequências (8 vitórias, 3-2-1 W-D-L)
- Médias (2.4 gols/jogo)
- Placares (3:1)

**Renderização automática:**
- Sistema converte em badges visuais
- Cor: azul claro (`bg-primary-50`)
- Destaque automático no frontend

### ✔ Bullets (•)

**Quando usar:**
- Listas de pontos escaneáveis
- Máximo 4-5 bullets por seção
- Cada bullet: idealmente 1 linha

**NUNCA:**
- Parágrafo corrido para múltiplos pontos
- Bullets com 3+ linhas

### ✔ Emojis

**Apenas estruturais:**
- 🎯 Previsão/Objetivo
- ⚡ Fatores-chave/Rápido
- 📊 Probabilidades/Dados
- 📚 📋 Análise/Resumo
- 1️⃣ 2️⃣ 3️⃣ Numeração
- 🏠 Casa | ✈️ Fora
- 💰 Recomendação/Aposta
- ⚠️ Risco/Alerta
- ✅ Justificativa/Check
- 💡 Insight/Alternativa

**❌ NÃO use:**
- Emojis decorativos (🔥 💪 🏆 exceto se estruturais)
- Excesso de emojis no texto corrido

### ✔ Logos dos Times (Inline)

**Funcionamento:**
- Sistema detecta automaticamente nomes dos times
- Renderiza logos inline automaticamente
- Não precisa de formatação especial

**Exemplo:**
```
Manchester City teve 65% de posse contra Arsenal
```
**Renderiza:**
```
[Logo] Manchester City teve 65% de posse contra [Logo] Arsenal
```

---

## 🚫 O QUE NÃO FAZER (PROIBIDO)

❌ NÃO comece com "Olá" ou introduções genéricas  
❌ NÃO use linguagem promocional ou exagerada  
❌ NÃO prometa resultados garantidos  
❌ NÃO invente estatísticas ou dados  
❌ NÃO escreva parágrafos longos no Bloco 1 ou 2  
❌ NÃO pule blocos ou mude a ordem  
❌ NÃO use `*` sozinho (sempre `**`)  
❌ NÃO escreva como especialista explicando  
❌ NÃO misture análise com recomendação  
❌ NÃO use jargão excessivo sem explicação

---

## ⭐ ESCALAS PADRONIZADAS

### Confiança (Estrelas)

| Estrelas | Label | Probabilidade | Descrição | Quando usar |
|----------|-------|---------------|-----------|-------------|
| **5** ⭐⭐⭐⭐⭐ | Alta | 70%+ | Dados completos, favorito claro | Óbvio favorito com histórico consistente |
| **4** ⭐⭐⭐⭐ | Alta | 60-69% | Bons dados, leve favorito | Favorito com algumas incertezas |
| **3** ⭐⭐⭐ | Média | 50-59% | Dados moderados, equilibrado | Jogo competitivo, dados razoáveis |
| **2** ⭐⭐ | Baixa | 40-49% | Dados limitados, incerteza | Poucos dados ou jogo muito aberto |
| **1** ⭐ | Baixa | <40% | Dados insuficientes | Evitar aposta, informação incompleta |

### Risco

| Nível | Descrição | Características | Exemplo |
|-------|-----------|-----------------|---------|
| **Baixo** | Favorito óbvio, odds conservadoras | Alta probabilidade, retorno menor | Casa forte vs visitante fraco |
| **Médio** | Jogo competitivo, odds razoáveis | Probabilidades equilibradas | Clássico entre times de nível similar |
| **Alto** | Jogo imprevisível, odds arriscadas | Muita incerteza, retorno alto | Zebra potencial, dados limitados |

### Tipo de Aposta

| Tipo | Perfil | Odds típicas | Para quem |
|------|--------|--------------|-----------|
| **Conservadora** | Segurança | 1.20 - 1.60 | Iniciantes, bankroll pequeno |
| **Equilibrada** | Balanced | 1.60 - 2.50 | Maioria dos apostadores |
| **Agressiva** | Alto risco | 2.50+ | Experientes, busca value |

---

## 🎯 CHECKLIST DE QUALIDADE FINAL

Antes de enviar, confirme:

✓ Bloco 1 pode ser lido em menos de 5 segundos  
✓ Bloco 1 inclui micro-alerta de risco (⚠️ Risco:)  
✓ Bloco 2 tem máximo 4 bullets, cada um com 1 linha  
✓ Bloco 2 usa formato **Fator:** Explicação  
✓ Bloco 3 tem percentuais somando 100%  
✓ Bloco 3 inclui interpretação rápida (💡)  
✓ Bloco 4 tem resumo executivo separado do restante  
✓ Bloco 5 identifica tipo de aposta (Conservadora/Equilibrada/Agressiva)  
✓ Bloco 5 inclui gestão de risco  
✓ Nenhuma promessa irreal ou linguagem promocional  
✓ Números em destaque (serão badges visuais)  
✓ Linguagem profissional e clara  
✓ Otimizado para mobile (leitura vertical)  
✓ Hierarquia visual forte (títulos, bullets, destaques)

---

## 📐 LAYOUT E ESPAÇAMENTO NO FRONTEND

### Estrutura do Modal (Atualizada)

```
┌──────────────────────────────────────────────┐
│  Header (scrollável)                          │
│  • Gradiente azul-roxo                       │
│  • Logo dos times + placar                   │
│  • Estrelas de confiança (1-5) + tooltip    │
│  • Data e hora da partida                    │
├──────────────────────────────────────────────┤
│  Metadados                                   │
│  • "DADOS ANALISADOS"                        │
│  • Checkmarks: Previsões, Stats, H2H, etc    │
├──────────────────────────────────────────────┤
│  🔥 BLOCO 1 - Hero (destaque visual)        │
│  • Fundo levemente diferenciado              │
│  • Fonte maior para probabilidade            │
│  • Micro-alerta de risco discreto            │
├──────────────────────────────────────────────┤
│  ⚡ BLOCO 2 - Fatores-chave                 │
│  • Bullets com check verde                   │
│  • Fatores em negrito destacado              │
├──────────────────────────────────────────────┤
│  📊 BLOCO 3 - Probabilidades                │
│  • Números grandes (text-2xl)               │
│  • Preparado para barras visuais (futuro)   │
│  • Interpretação em texto menor              │
├──────────────────────────────────────────────┤
│  📚 BLOCO 4 - Análise Detalhada             │
│  • Resumo executivo sempre visível           │
│  • Seções 1️⃣ 2️⃣ 3️⃣ (futuro: colapsáveis)    │
├──────────────────────────────────────────────┤
│  💰 BLOCO 5 - Recomendação                  │
│  • Tipo de aposta em badge colorido          │
│  • Alternativa em fonte menor (opcional)     │
└──────────────────────────────────────────────┘
```

### Espaçamento Vertical

**Entre Blocos principais (1-5):**
- `space-y-6` (24px entre blocos)
- Separadores visuais discretos (`border-t`)

**Entre Parágrafos:**
- `space-y-4` (16px entre parágrafos)
- Cria separação visual clara

**Entre Linhas:**
- `mb-1` (4px entre linhas dentro do mesmo parágrafo)
- Mantém coesão dentro do parágrafo

**Títulos de Seções:**
- Detectados automaticamente (começam com emoji)
- `text-base sm:text-lg` (maior que texto normal)
- `font-bold` (negrito)
- Animação: `fade-in` com delay progressivo

### Espaçamento Horizontal

**Padding do Container:**
- Mobile: `p-4` (16px)
- Desktop: `sm:p-6` (24px)
- Consistente em todo o modal

**Indentação de Bullets:**
- `ml-4` (16px de margem esquerda)
- `gap-2` (8px entre bullet e texto)

---

## 🎨 DESIGN VISUAL

### Cores

**Texto Principal:**
- Claro: `text-gray-700`
- Escuro: `text-gray-200`

**Texto em Destaque (Negrito):**
- Claro: `text-gray-900`
- Escuro: `text-white`

**Badges de Números:**
- Background: `bg-primary-50` / `dark:bg-primary-900/30`
- Texto: `text-primary-600` / `dark:text-primary-400`

**Bullets:**
- Cor: `text-primary-500`
- Check (✓): `text-green-500`

**Nomes de Times:**
- `text-gray-900` / `dark:text-white`
- `font-semibold`

**Micro-alerta de Risco:**
- Baixo: `text-green-600` / `bg-green-50`
- Médio: `text-yellow-600` / `bg-yellow-50`
- Alto: `text-red-600` / `bg-red-50`

### Tipografia

**Tamanhos:**
- Texto normal: `text-sm sm:text-base` (14px → 16px)
- Títulos de blocos: `text-lg sm:text-xl` (18px → 20px)
- Probabilidades: `text-2xl sm:text-3xl` (24px → 30px)
- Subtítulos: `text-base sm:text-lg` (16px → 18px)
- Leading: `leading-relaxed` (1.625)

**Pesos:**
- Normal: `font-normal` (400)
- Semibold: `font-semibold` (600) - nomes de times, fatores-chave
- Bold: `font-bold` (700) - destaques e títulos

### Animações

**Fade In dos Parágrafos:**
```css
@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```
- Delay progressivo: `animationDelay: ${idx * 0.05}s`
- Cria efeito de "digitação"

**Accordion (Implementação Futura):**
```css
@keyframes accordion-down {
  from { height: 0; opacity: 0; }
  to { height: var(--radix-accordion-content-height); opacity: 1; }
}
```

### Responsividade

**Breakpoints:**
- Mobile first: classes base
- Desktop: classes com prefixo `sm:` (640px+)

**Ajustes por Tamanho:**
- Padding: `p-4` → `sm:p-6`
- Font: `text-sm` → `sm:text-base`
- Logos: `w-4 h-4` → `sm:w-5 sm:h-5`
- Probabilidades: `text-2xl` → `sm:text-3xl`

---

## 🔧 PROCESSAMENTO TÉCNICO

### Pipeline de Renderização

1. **Backend (Python - AI Analyzer)**
   ```python
   # Gera texto estruturado com markdown
   texto = """
   🎯 PREVISÃO DA IA
   
   **Vitória do Manchester City**
   
   📊 Probabilidade: 60%
   ⚽ Placar esperado: 2:1
   
   ⭐ Confiança: 4 estrelas (Alta)
   ⚠️ Risco: Médio
   
   ⚡ POR QUE ESSA PREVISÃO?
   
   ✓ **Forma recente:** City está invicto há 10 jogos
   ✓ **Confronto direto:** 65% de aproveitamento contra Arsenal
   """
   ```

2. **Frontend - Etapa 1: Agrupar em Parágrafos**
   ```javascript
   formatAnalysisText(texto)
   // Divide por linhas vazias
   // Resultado: Array de parágrafos
   ```

3. **Frontend - Etapa 2: Processar Formatação Inline**
   ```javascript
   formatInlineText(linha, homeTeam, awayTeam)
   // Detecta: **bold**, números, %, times
   // Resultado: Array de {type, content}
   ```

4. **Frontend - Etapa 3: Renderizar JSX**
   ```jsx
   {parts.map(part => {
     if (part.type === 'home_team') {
       return <TeamLogo /> + Nome
     }
     if (part.type === 'bold') {
       return <strong>{content}</strong>
     }
     // etc...
   })}
   ```

### Regex Patterns Usados

```javascript
/\*\*([^*]+)\*\*/g          // **negrito**
/\*([^*]+)\*/g               // *bullet*
/(\d+%)/g                    // percentuais
/(\d+\.\d+|\d+:\d+)/g        // decimais/placares
/(\d+\s+gol(?:s)?)/gi        // "X gols"
/(Nome do Time)/gi           // detecção de times (dinâmica)
```

---

## 🆕 IMPLEMENTAÇÕES FUTURAS (ROADMAP)

### Fase 1 - Imediato (já implementado no backend)
- ✅ Micro-alerta de risco no Bloco 1
- ✅ Fatores-chave destacados no Bloco 2
- ✅ Interpretação rápida no Bloco 3
- ✅ Resumo executivo separado no Bloco 4
- ✅ Tipo de aposta + gestão de risco no Bloco 5

### Fase 2 - Frontend (próximos passos)
- ⏳ Accordion/collapse para Bloco 4 (seções 1️⃣ 2️⃣ 3️⃣)
- ⏳ Barras visuais de probabilidade no Bloco 3
- ⏳ Tooltip para escala de confiança (hover nas estrelas)
- ⏳ Badge colorido para tipo de aposta no Bloco 5
- ⏳ Separadores visuais entre blocos principais

### Fase 3 - Avançado (futuro)
- 💡 Gráfico de pizza para probabilidades
- 💡 Animação de barras progressivas
- 💡 Comparação visual de estatísticas (radar chart)
- 💡 Histórico de acurácia da IA
- 💡 Botão "Copiar análise" para compartilhamento

---

## 📚 REFERÊNCIAS

**Arquivos-Chave:**
- Backend: `backend/apps/analysis/services/ai_analyzer.py` - Geração do prompt (v3.0)
- Frontend: `frontend/src/components/AnalysisModal.jsx` - Renderização
- Frontend: `frontend/src/components/TeamLogo.jsx` - Logos dos times

**Bibliotecas:**
- Tailwind CSS 3 - Estilização
- Lucide React - Ícones (estrelas, close, chevron)
- React 18 - Componentes
- (Futuro) Radix UI - Accordion component

**Design System:**
- Border-radius: `rounded-2xl` (16px) - padrão do projeto
- Padding: `p-4` mobile, `p-6` desktop
- Shadow: `shadow-lg` para depth
- Primary color: Azul (#3B82F6)
- Success: Verde (#10B981)
- Warning: Amarelo (#F59E0B)
- Danger: Vermelho (#EF4444)

---

**Última Atualização:** 31 de Dezembro de 2025  
**Versão:** 3.0 (Product Design + UX/UI Improvements)  
**Mudanças principais:**
- Micro-alerta de risco adicionado
- Fatores-chave destacados
- Interpretação rápida de probabilidades
- Tipo de aposta identificado
- Gestão de risco incluída
- Preparado para accordion/collapse
- Escalas padronizadas
- Checklist de qualidade expandido
