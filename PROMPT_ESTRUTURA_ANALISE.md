# 📋 PROMPT: Estrutura, Layout e Design das Análises de IA

## 🎯 OBJETIVO PRINCIPAL

Gerar uma análise de apostas de futebol profissional para exibição em modal web premium, onde o usuário deve entender **a melhor aposta em até 3 segundos**, com clareza, confiança e hierarquia visual forte.

A análise não deve parecer texto de chatbot, e sim **conteúdo editorial de alto nível, orientado à decisão**.

---

## 🧠 FILOSOFIA DO PRODUTO (OBRIGATÓRIO)

✅ **A decisão vem antes da explicação**  
✅ **Texto longo só para quem quiser ler**  
✅ **Tudo deve responder à pergunta: "Em que apostar e por quê?"**  
✅ **Clareza > criatividade**  
✅ **Menos texto, mais sinal**

---

## 🧱 ESTRUTURA FINAL OBRIGATÓRIA (ORDEM NÃO PODE MUDAR)

### 🔥 BLOCO 1 — DECISÃO IMEDIATA (MAIS IMPORTANTE)

**Comece SEMPRE com este bloco.**

```markdown
🎯 PREVISÃO DA IA

**{RESULTADO MAIS PROVÁVEL}**

📊 Probabilidade: {XX}%
⚽ Placar esperado: {X:X}

⭐ Confiança: {1 a 5 estrelas} ({Baixa | Média | Alta})
```

**Regras:**
- Seja direto
- Uma única previsão clara
- Nada de texto explicativo aqui
- NÃO comece com introdução genérica

---

### ⚡ BLOCO 2 — POR QUE CONFIAR? (PONTOS-CHAVE)

Liste **no máximo 3 pontos**, objetivos e curtos:

```markdown
⚡ POR QUE ESSA APOSTA?

✓ {Insight objetivo baseado em dados}
✓ {Insight objetivo baseado em forma / histórico}
✓ {Insight objetivo baseado em matchup ou tendência}
```

**Regras:**
- Frases curtas (1 linha cada)
- Dados concretos
- Nada de introduções genéricas

---

### 📊 BLOCO 3 — PROBABILIDADES VISUAIS

```markdown
📊 PROBABILIDADES

🏠 {TIME_CASA}: {XX}%
🤝 Empate: {XX}%
✈️ {TIME_FORA}: {XX}%
```

**Regras:**
- Percentuais obrigatórios
- Soma deve ser 100%
- Sem explicações longas

---

### 📚 BLOCO 4 — ANÁLISE DETALHADA (SECUNDÁRIO)

Este bloco é para **leitura aprofundada**.  
Escreva bem estruturado, mas lembre-se: **não é o foco principal**.

```markdown
� RESUMO EXECUTIVO

• Contexto do jogo
• Situação atual dos times
• 1–2 parágrafos curtos

1️⃣ ANÁLISE DE FORMA

🏠 Casa – {TIME_CASA}
• Estatísticas recentes
• Tendências claras

✈️ Fora – {TIME_FORA}
• Estatísticas recentes
• Tendências claras

2️⃣ CONFRONTOS DIRETOS (H2H)

• Resultados recentes
• Padrões importantes

3️⃣ ANÁLISE TÁTICA

• Ataque vs Defesa
• Onde o jogo pode ser decidido
```

---

### 💰 BLOCO 5 — RECOMENDAÇÃO FINAL

```markdown
💰 RECOMENDAÇÃO

**Aposta sugerida:** {Mercado + seleção}

✅ Justificativa objetiva
⚠️ Risco: {Baixo | Médio | Alto}
```

**Regras:**
- Uma recomendação principal
- Nada de listas longas
- Clareza máxima

---

## ✍️ REGRAS DE FORMATAÇÃO (MUITO IMPORTANTE)

### ✔ Negrito (**texto**)

Use para:
- Nomes dos times
- Resultados finais
- Recomendações
- Subtítulos importantes

### ✔ Números e Percentuais

Sempre inclua:
- Percentuais (%)
- Sequências (ex: 8 vitórias)
- Médias (ex: 2.4 gols)
- Placares (ex: 2:1)

**Esses números serão renderizados como badges visuais no frontend.**

### ✔ Bullets

Use `•` para listas  
**Nunca escreva listas em parágrafo corrido.**

### ✔ Emojis

Use apenas quando:
- Estruturam seções
- Ajudam na leitura

❌ **Não use emojis decorativos.**

### ✔ Logos dos Times (Inline)

Quando o nome do time for mencionado no texto, **o sistema automaticamente detecta e exibe o logo ao lado**.

**Exemplo:**
```
Manchester City teve 65% de posse contra Arsenal
```

**Renderiza como:**
```
[⚽ Logo City] Manchester City teve 65% de posse contra [⚽ Logo Arsenal] Arsenal
```

---

## 🚫 O QUE NÃO FAZER (PROIBIDO)

❌ Não comece com introdução genérica  
❌ Não escreva texto longo antes da previsão  
❌ Não pule blocos  
❌ Não misture análise com recomendação  
❌ Não use linguagem informal excessiva  
❌ Não escreva como "especialista explicando"  
❌ Não invente estatísticas  
❌ Não use `*` sozinho (sempre use `**`)

---

## ⭐ ESCALA DE CONFIANÇA

| Estrelas | Confiança | Probabilidade | Descrição |
|----------|-----------|---------------|-----------|
| **5** ⭐⭐⭐⭐⭐ | Alta | 70%+ | Favorito ÓBVIO |
| **4** ⭐⭐⭐⭐ | Alta | 60-69% | Favorito CLARO |
| **3** ⭐⭐⭐ | Média | 50-59% | Leve favorito |
| **2** ⭐⭐ | Baixa | 45-55% | Muito equilibrado |
| **1** ⭐ | Baixa | <45% | Total incerteza |

---

## 🏁 RESULTADO ESPERADO

Ao final, o texto deve:

✓ Permitir decisão em até 3 segundos  
✓ Ser altamente escaneável  
✓ Funcionar perfeitamente em mobile  
✓ Transmitir confiança e profissionalismo  
✓ Estar pronto para renderização direta em um modal premium

---

## 🔥 Observação Final (IMPORTANTE)

**Se houver conflito entre:**
- Texto bonito
- Texto claro

👉 **Priorize sempre o texto claro.**

---

## 📐 LAYOUT E ESPAÇAMENTO NO FRONTEND

### Estrutura do Modal

```
┌─────────────────────────────────────────────┐
│  Header (scrollável com conteúdo)           │
│  • Gradiente azul-roxo                      │
│  • Logo dos times + placar                  │
│  • Estrelas de confiança (1-5)              │
│  • Data e hora da partida                   │
├─────────────────────────────────────────────┤
│  Metadados                                  │
│  • "DADOS ANALISADOS"                       │
│  • Checkmarks: Previsões, Stats, H2H, etc   │
├─────────────────────────────────────────────┤
│  Conteúdo da Análise (scroll)               │
│  • Parágrafos com espaçamento space-y-4    │
│  • Linhas com mb-1                          │
│  • Formatação inline processada             │
│  • Logos dos times inline                   │
└─────────────────────────────────────────────┘
```

### Espaçamento Vertical

**Entre Parágrafos:**
- `space-y-4` (16px entre parágrafos)
- Cria separação visual clara entre blocos de texto

**Entre Linhas:**
- `mb-1` (4px entre linhas dentro do mesmo parágrafo)
- Mantém coesão dentro do parágrafo

**Títulos de Seções:**
- Detectados automaticamente (começam com emoji numerado)
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

**Nomes de Times:**
- `text-gray-900` / `dark:text-white`
- `font-semibold`

### Tipografia

**Tamanhos:**
- Texto normal: `text-sm sm:text-base` (14px → 16px)
- Títulos: `text-base sm:text-lg` (16px → 18px)
- Leading: `leading-relaxed` (1.625)

**Pesos:**
- Normal: `font-normal` (400)
- Semibold: `font-semibold` (600) - nomes de times
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

### Responsividade

**Breakpoints:**
- Mobile first: classes base
- Desktop: classes com prefixo `sm:` (640px+)

**Ajustes por Tamanho:**
- Padding: `p-4` → `sm:p-6`
- Font: `text-sm` → `sm:text-base`
- Logos: `w-4 h-4` → `sm:w-5 sm:h-5`

---

## 🔧 PROCESSAMENTO TÉCNICO

### Pipeline de Renderização

1. **Backend (Python - AI Analyzer)**
   ```python
   # Gera texto estruturado com markdown
   texto = """
   📊 RESUMO EXECUTIVO
   
   O **Manchester City** enfrenta o **Arsenal** em um clássico...
   • City está invicto há 10 jogos
   • Arsenal tem 65% de aproveitamento fora
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

## ⭐ SISTEMA DE CONFIANÇA

### Níveis de Estrelas

- **5 Estrelas (⭐⭐⭐⭐⭐):** Confiança ≥ 70% - Dados completos, padrões claros
- **4 Estrelas (⭐⭐⭐⭐):** Confiança 60-69% - Bons dados, algumas incertezas
- **3 Estrelas (⭐⭐⭐):** Confiança 50-59% - Dados moderados
- **2 Estrelas (⭐⭐):** Confiança 40-49% - Dados limitados
- **1 Estrela (⭐):** Confiança < 40% - Dados insuficientes

### Visualização

- Estrelas preenchidas: amarelo brilhante (`text-yellow-400`)
- Estrelas vazias: cinza claro (`text-gray-300`)
- Tamanho: `w-5 h-5` (20px)
- Label ao lado: "Confiança: X/5"

---

## 📋 CHECKLIST DE QUALIDADE

### O Texto Deve:
- ✅ Ter 5 seções claras com emojis numerados
- ✅ Usar negrito para nomes de times e informações críticas
- ✅ Destacar números e percentuais em badges coloridos
- ✅ Incluir bullets para listas de pontos
- ✅ Exibir logos dos times inline quando mencionados
- ✅ Ter parágrafos bem espaçados (não linhas soltas)
- ✅ Usar emojis de forma estratégica (não excessiva)
- ✅ Ser responsivo (legível em mobile e desktop)
- ✅ Ter animação suave de entrada
- ✅ Refletir nível de confiança nas estrelas

### O Texto NÃO Deve:
- ❌ Mostrar asteriscos soltos (* ou **)
- ❌ Ter seções distorcidas ou mal formatadas
- ❌ Ter linhas soltas sem agrupamento em parágrafos
- ❌ Ter nomes de times sem logos
- ❌ Ter números sem destaque visual
- ❌ Ter excesso de emojis (poluição visual)
- ❌ Ter header fixo (deve scrollar junto)
- ❌ Ter design inconsistente (mixed border-radius, etc)

---

## 🎯 EXEMPLO COMPLETO

### Input do Backend (Markdown):
```markdown
📊 RESUMO EXECUTIVO

O **Manchester City** recebe o **Arsenal** no Etihad Stadium em confronto direto pelo topo da tabela. City está invicto há 12 jogos, enquanto Arsenal busca se recuperar de derrota recente.

1️⃣ ANÁLISE DE FORMA

🏠 **Casa - Manchester City**
• 8 vitórias consecutivas em casa
• 85% de aproveitamento no Etihad
• Média de 2.8 gols marcados por jogo

✈️ **Fora - Arsenal**
• 3 vitórias nos últimos 5 jogos fora
• 60% de aproveitamento como visitante
• Defesa sólida: apenas 0.8 gols sofridos

4️⃣ PREVISÃO

🎯 **Resultado mais provável:** Vitória do Manchester City
📊 **Probabilidades:** City 55%, Empate 25%, Arsenal 20%
⚽ **Placar esperado:** 2:1 para o City
```

### Output Renderizado:

![Modal com header gradiente]

**📊 RESUMO EXECUTIVO** (título grande, negrito, com emoji)

O [🛡️ Logo] **Manchester City** recebe o [🛡️ Logo] **Arsenal** no Etihad Stadium em confronto direto pelo topo da tabela. City está invicto há `12` jogos, enquanto Arsenal busca se recuperar de derrota recente.

**1️⃣ ANÁLISE DE FORMA** (título grande, negrito)

**🏠 Casa - Manchester City** (subtítulo negrito)
• `8` vitórias consecutivas em casa (bullet azul + badge)
• `85%` de aproveitamento no Etihad (percentual em badge)
• Média de `2.8` gols marcados por jogo (número em badge)

**✈️ Fora - Arsenal** (subtítulo negrito)
• `3` vitórias nos últimos `5` jogos fora
• `60%` de aproveitamento como visitante
• Defesa sólida: apenas `0.8` gols sofridos

**4️⃣ PREVISÃO**

🎯 **Resultado mais provável:** Vitória do [🛡️ Logo] **Manchester City**
📊 **Probabilidades:** City `55%`, Empate `25%`, Arsenal `20%`
⚽ **Placar esperado:** `2:1` para o City

---

## 🔄 MANUTENÇÃO E EVOLUÇÃO

### Para Adicionar Nova Formatação:

1. **Backend:** Adicione markdown no prompt da IA
2. **Frontend:** Adicione regex pattern em `formatInlineText()`
3. **Frontend:** Adicione case no rendering JSX
4. **Teste:** Verifique em mobile e desktop

### Para Ajustar Design:

- Cores: Modifique classes Tailwind (sempre use dark: variant)
- Espaçamento: Ajuste `space-y-X` e `mb-X`
- Animação: Modifique delay em `style={{ animationDelay }}`

### Para Debug:

- Console.log em `formatAnalysisText()` para ver parágrafos
- Console.log em `formatInlineText()` para ver parts
- Inspecionar elemento para verificar classes CSS aplicadas

---

## 📚 REFERÊNCIAS

**Arquivos-Chave:**
- Backend: `backend/apps/analysis/services/ai_analyzer.py` - Geração do prompt
- Frontend: `frontend/src/components/AnalysisModal.jsx` - Renderização
- Frontend: `frontend/src/components/TeamLogo.jsx` - Logos dos times

**Bibliotecas:**
- Tailwind CSS 3 - Estilização
- Lucide React - Ícones (estrelas, close)
- React 18 - Componentes

**Design System:**
- Border-radius: `rounded-2xl` (16px) - padrão do projeto
- Padding: `p-4` mobile, `p-6` desktop
- Shadow: `shadow-lg` para depth
- Primary color: Azul (#3B82F6)

---

**Última Atualização:** 31 de Dezembro de 2025
**Versão:** 2.0 (com logos inline dos times)
