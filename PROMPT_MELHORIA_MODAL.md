# 🎨 PROMPT: Melhorias para o Modal de Análise de Apostas

## Contexto
Tenho um modal React que exibe análises de IA para apostas de futebol. O modal usa Tailwind CSS, ícones Lucide-React, e suporta dark mode. Preciso de sugestões específicas e implementáveis para melhorar a UX, legibilidade e visual.

---

## 📊 Estrutura Visual Atual

### HEADER (Gradiente primário → accent)
```
┌─────────────────────────────────────────────────────────┐
│  [Sparkles Icon] Análise com IA          [X Fechar]    │
│  Powered by Google Gemini                               │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  [Logo]         VS         [Logo]                │  │
│  │  Time Casa   [★★★★★]    Time Fora               │  │
│  │  (confiança: 5 estrelas)                         │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Elementos:**
- Botão X (canto superior direito): circular, bg-white/20, hover:bg-white/30
- Ícone Sparkles + Título "Análise com IA" (text-2xl, font-bold, white)
- Subtexto "Powered by Google Gemini" (text-primary-100, text-sm)
- Card central (bg-white/10, rounded-xl):
  - 3 colunas: Logo Casa | VS + Estrelas | Logo Fora
  - Logos em círculos brancos (w-16 h-16)
  - Nomes em font-bold, text-base, text-center
  - 5 estrelas amarelas (fill-yellow-400) mostrando confiança

---

### CORPO DO MODAL

#### 1. Box de Veredicto
```
┌────────────────────────────────────────────────────┐
│  [🏆 Icon]  🔥 FORTE!                              │
│             Aposte com confiança                    │
└────────────────────────────────────────────────────┘
```

**Estilos:**
- Background: gradient from-primary-50 via-primary-100 to-accent-50 (dark: gray-700 → gray-600)
- Border: 2px border-primary-300 (dark: primary-600)
- Ícone animado (animate-pulse para confiança 5):
  - Trophy (verde) = Confiança 4-5
  - Shield (amarelo) = Confiança 3
  - AlertTriangle (laranja) = Confiança 1-2
- Badges:
  - "🔥 FORTE!" = 4-5 estrelas
  - "⚖️ EQUILIBRADO" = 3 estrelas
  - "⚠️ CAUTELA" = 1-2 estrelas

---

#### 2. Para quick_analyze (Análise Simples)

**Card "ANÁLISE RÁPIDA":**
```
┌────────────────────────────────────────────────────┐
│  ⚡ ANÁLISE RÁPIDA                                  │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │ [✓] Ponto-chave extraído 1                   │ │
│  │     (primeira frase importante)              │ │
│  └──────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────┐ │
│  │ [✓] Ponto-chave extraído 2                   │ │
│  └──────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────┐ │
│  │ [✓] Ponto-chave extraído 3                   │ │
│  └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
```

**Problemas identificados:**
- ❌ Extração muito simples: apenas `.split(/[.!?]+/)` pega primeiras 3 frases
- ❌ Não identifica pontos realmente importantes
- ❌ Pode pegar frases de introdução/contexto em vez de insights

**Colapsável "Ver Análise Completa":**
```
▼ Ver Análise Completa
┌────────────────────────────────────────────────────┐
│  [Texto completo em whitespace-pre-wrap]           │
│  - Sem formatação                                  │
│  - Bloco corrido                                   │
│  - Difícil de escanear                             │
└────────────────────────────────────────────────────┘
```

**Problemas:**
- ❌ Texto em bloco corrido sem estrutura
- ❌ Sem destaques (negrito, cores)
- ❌ Sem separação visual de seções
- ❌ Parágrafos não são visualmente separados

---

#### 3. Para request_analysis (Análise Estruturada)

**Card PREDIÇÃO (Hero Section):**
```
┌────────────────────────────────────────────────────┐
│     [🎯 Icon animate-pulse]                        │
│           PREDIÇÃO                                  │
│                                                     │
│         VITÓRIA CASA                                │
│         ★★★★☆                                       │
└────────────────────────────────────────────────────┘
```

**Estilos:**
- Background: gradient primary-500 → accent-600
- Decoração: círculos white/10 (canto superior direito, inferior esquerdo)
- Predição: text-5xl font-black
- Estrelas: text-3xl text-yellow-300

**Grid de Probabilidades (3 colunas):**
```
┌─────────┐  ┌─────────┐  ┌─────────┐
│🏠 CASA  │  │🤝 EMPATE│  │✈️ FORA  │
│         │  │         │  │         │
│   65%   │  │   20%   │  │   15%   │
│ [barra] │  │ [barra] │  │ [barra] │
└─────────┘  └─────────┘  └─────────┘
```

**Cores:**
- Casa: green-500 → green-600
- Empate: gray-500 → gray-600
- Fora: blue-500 → blue-600
- Hover: scale-105
- Barra de progresso: white com width dinâmico

**Problemas:**
- ⚠️ Em mobile (< 640px), cards ficam apertados
- ⚠️ Text-4xl pode ser grande demais em telas pequenas

**PONTOS-CHAVE:**
```
⚡ PONTOS-CHAVE
┌────────────────────────────────────────────────────┐
│  [✓] Fator importante 1                            │
│  [✓] Fator importante 2                            │
│  [✓] Fator importante 3                            │
└────────────────────────────────────────────────────┘
```

**Estilos:**
- Border-left: 4px primary-500
- Ícone CheckCircle2 em círculo primary-100
- Hover: shadow aumenta

---

## 🚨 PROBLEMAS PRINCIPAIS

### 1. Formatação de Texto da Análise
**Problema:** IA retorna texto em bloco corrido sem formatação
```
Exemplo:
"Boas malta, Como vosso especialista com 20 anos... A análise tática mostra que..."
```

**Necessário:**
- Detectar seções (1️⃣, 2️⃣, etc.)
- Separar parágrafos visualmente
- Destacar palavras-chave (negrito)
- Aplicar cores para ênfase

### 2. Extração de Pontos-Chave
**Atual:** `text.split(/[.!?]+/).slice(0, 3)`
**Problema:** Pega primeiras 3 frases, não as mais importantes

**Necessário:**
- Detectar frases com palavras-chave: "recomendo", "importante", "destaque"
- Priorizar frases com estatísticas/números
- Evitar frases introdutórias genéricas

### 3. Responsividade
**Problemas em mobile:**
- Grid de probabilidades (3 colunas) fica apertado
- Text-4xl muito grande
- Logos 16x16 podem ser grandes

### 4. Contraste Dark Mode
**Áreas com baixa legibilidade:**
- text-gray-300 em bg-gray-700
- primary-100 em primary-900/30
- Alguns textos secundários

### 5. Hierarquia Visual
**Problema:** Tudo tem importância similar
- Difícil identificar o que é mais importante
- Falta escaneabilidade
- Usuário precisa ler tudo para extrair insights

---

## 💡 O QUE PRECISO

### 1. Formatação Inteligente do Texto
```javascript
// Converter texto da IA em estrutura visual
function formatAnalysisText(text) {
  // Detectar seções (1️⃣, 2️⃣, ═══, etc.)
  // Separar parágrafos
  // Aplicar negrito em palavras-chave
  // Adicionar ícones
  // Colorir estatísticas/números
}
```

**Sugestões:**
- Como detectar seções automaticamente?
- Regex para identificar estruturas importantes?
- CSS/Tailwind para estilizar sem quebrar o texto?

### 2. Extração Inteligente de Pontos-Chave
```javascript
function extractKeyPoints(text) {
  // Não apenas primeiras 3 frases
  // Buscar frases com:
  //   - Palavras-chave importantes
  //   - Estatísticas/números
  //   - Recomendações
  //   - Conclusões
}
```

**Critérios de importância:**
- Frases com "recomendo", "importante", "atenção"
- Frases com números/percentuais
- Frases começando com "1.", "•", "-"
- Última frase (conclusão)

### 3. Melhorias de Responsividade
**Mobile (< 640px):**
```jsx
// Grid de probabilidades
<div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
  {/* Cards empilhados em mobile */}
</div>

// Tamanhos de texto
<div className="text-3xl sm:text-4xl">
  {/* Menor em mobile */}
</div>
```

### 4. Melhorias de Acessibilidade/Contraste
**Dark mode:**
- Aumentar contraste de textos secundários
- Usar text-gray-200 em vez de text-gray-300
- Bordas mais visíveis

### 5. Micro-animações
**Adicionar transições suaves:**
- Fade-in ao abrir seções colapsáveis
- Slide-up dos cards
- Pulse em elementos importantes
- Hover states mais suaves

### 6. Melhorias de Escaneabilidade
**Visual Hierarchy:**
- Tags/badges para categorizar informações
- Separadores visuais claros
- Cores semânticas (verde=positivo, vermelho=negativo, azul=neutro)
- Ícones consistentes

---

## 🎯 PERGUNTAS ESPECÍFICAS

1. **Como formatar o texto da IA sem quebrar?**
   - Detectar seções automaticamente via regex?
   - Aplicar spans com classes Tailwind dinamicamente?
   - Converter markdown simples (**negrito**, `código`)?

2. **Como extrair pontos-chave de forma inteligente?**
   - Algoritmo de pontuação de frases?
   - NLP básico em JavaScript?
   - Regex patterns específicos?

3. **Como melhorar responsividade sem criar breakpoints complexos?**
   - Usar `container queries`?
   - Classes Tailwind com sm:/md:/lg:?
   - Ajustar apenas o essencial?

4. **Como melhorar contraste no dark mode?**
   - Quais combinações de cores são acessíveis?
   - Ferramentas para testar contraste?
   - Alternativas aos grays atuais?

5. **Como adicionar animações sem pesar o bundle?**
   - Usar apenas Tailwind animations?
   - Framer Motion vale a pena?
   - CSS transitions básicas são suficientes?

6. **Como tornar o modal mais "escaneável"?**
   - Cards vs Lista vs Grid?
   - Uso de cores para categorização?
   - Iconografia consistente?

---

## 📦 TECNOLOGIAS DISPONÍVEIS

- React 18
- Tailwind CSS 3
- Lucide-React (ícones)
- Suporta dark mode via `dark:` prefix

**Não usar:**
- Bibliotecas extras pesadas
- Frameworks de UI (Material-UI, Chakra)
- Preferir soluções puras Tailwind + React

---

## 🚀 ENTREGÁVEIS ESPERADOS

1. **Código React/JSX** para formatação de texto
2. **Função JavaScript** para extração de pontos-chave
3. **Classes Tailwind** para melhorias de layout
4. **Regex patterns** para parsing do texto da IA
5. **Breakpoints responsivos** específicos
6. **Paleta de cores** para dark mode acessível
7. **Animações CSS/Tailwind** recomendadas

---

## 💡 EXEMPLO DE OUTPUT DESEJADO

**Texto da IA atual:**
```
Boas malta! Como vosso especialista... 1️⃣ ANÁLISE TÁTICA O time da casa tem vantagem...
```

**Formatado:**
```jsx
<div>
  <p className="text-lg text-gray-700 dark:text-gray-200">
    Boas malta! Como vosso especialista...
  </p>
  
  <div className="mt-4 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg">
    <h3 className="flex items-center gap-2 font-bold text-primary-600">
      <Target className="w-5 h-5" />
      1️⃣ ANÁLISE TÁTICA
    </h3>
    <p className="mt-2">
      O time da casa tem <span className="font-bold text-green-600">vantagem</span>...
    </p>
  </div>
</div>
```

---

## ⚠️ IMPORTANTE

- **Seja específico**: Forneça código completo, não pseudocódigo
- **Seja prático**: Soluções implementáveis imediatamente
- **Considere performance**: Evite regex complexos ou loops pesados
- **Mantenha consistência**: Seguir padrões já existentes no código
- **Pense em edge cases**: Texto curto, muito longo, mal formatado

---

**Aguardo suas sugestões concretas e implementáveis!** 🎨
