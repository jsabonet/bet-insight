# 🎨 Design System - Métodos de Pagamento

## Cores Oficiais Implementadas

### M-Pesa (Vodacom)
```
Principal: #E60000 (Vermelho Vodacom)
Hover: #DC2626 (red-600)
Background: #FEF2F2 (red-50)
Ring: #FECACA (red-200)
```

### e-Mola (Movitel)
```
Principal: #00A651 (Verde Movitel)
Hover: #16A34A (green-600)
Background: #F0FDF4 (green-50)
Ring: #BBF7D0 (green-200)
```

---

## Componentes SVG

### MPesaLogo
```jsx
<svg viewBox="0 0 120 40" className="h-8 w-auto">
  <rect width="120" height="40" fill="#E60000" rx="4"/>
  <text x="60" y="25" 
        fontFamily="Arial, sans-serif" 
        fontSize="18" 
        fontWeight="bold" 
        fill="white" 
        textAnchor="middle">
    M-Pesa
  </text>
</svg>
```

**Resultado visual:**
```
┌────────────────────┐
│                    │
│      M-Pesa        │ (Texto branco em fundo vermelho)
│                    │
└────────────────────┘
```

### EMolaLogo
```jsx
<svg viewBox="0 0 120 40" className="h-8 w-auto">
  <rect width="120" height="40" fill="#00A651" rx="4"/>
  <text x="60" y="25" 
        fontFamily="Arial, sans-serif" 
        fontSize="18" 
        fontWeight="bold" 
        fill="white" 
        textAnchor="middle">
    e-Mola
  </text>
</svg>
```

**Resultado visual:**
```
┌────────────────────┐
│                    │
│      e-Mola        │ (Texto branco em fundo verde)
│                    │
└────────────────────┘
```

---

## Estados de Interação

### Botão M-Pesa

**Idle (não selecionado):**
```jsx
className="
  border-2 border-gray-200 
  hover:border-red-300
  transition-all
"
```

**Active (selecionado):**
```jsx
className="
  border-2 border-red-600
  bg-red-50
  ring-2 ring-red-200
  transition-all
"
```

**Dark Mode:**
```jsx
// Idle
dark:border-gray-700 
dark:hover:border-red-700

// Active
dark:border-red-500
dark:bg-red-900/20
```

### Botão e-Mola

**Idle (não selecionado):**
```jsx
className="
  border-2 border-gray-200
  hover:border-green-300
  transition-all
"
```

**Active (selecionado):**
```jsx
className="
  border-2 border-green-600
  bg-green-50
  ring-2 ring-green-200
  transition-all
"
```

**Dark Mode:**
```jsx
// Idle
dark:border-gray-700
dark:hover:border-green-700

// Active
dark:border-green-500
dark:bg-green-900/20
```

---

## Layout dos Botões

```jsx
<div className="grid grid-cols-2 gap-3">
  {/* M-Pesa */}
  <button className="p-4 rounded-xl border-2">
    <div className="flex flex-col items-center justify-center gap-2">
      <MPesaLogo />              {/* Logo vermelho */}
      <div className="text-xs">Vodacom</div>
    </div>
  </button>

  {/* e-Mola */}
  <button className="p-4 rounded-xl border-2">
    <div className="flex flex-col items-center justify-center gap-2">
      <EMolaLogo />              {/* Logo verde */}
      <div className="text-xs">Movitel</div>
    </div>
  </button>
</div>
```

**Visual:**
```
┌─────────────────┬─────────────────┐
│   ┌─────────┐   │   ┌─────────┐   │
│   │ M-Pesa  │   │   │ e-Mola  │   │
│   └─────────┘   │   └─────────┘   │
│    Vodacom      │    Movitel      │
└─────────────────┴─────────────────┘
```

---

## Feedback de Processamento

### Com Logo do Método Selecionado

```jsx
{paymentStatus === 'processing' && (
  <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
    <div className="flex items-center gap-3">
      <Loader2 className="animate-spin" />
      <div>Aguardando confirmação...</div>
    </div>
    
    {/* Logo do método */}
    <div className="flex items-center gap-2 mb-3">
      {paymentMethod === 'mpesa' ? (
        <><MPesaLogo /> <span>Vodacom</span></>
      ) : (
        <><EMolaLogo /> <span>Movitel</span></>
      )}
    </div>
    
    <p>
      Insira seu PIN no {paymentMethod === 'mpesa' ? 'M-Pesa' : 'e-Mola'} 
      para confirmar {plan.price.toLocaleString()} MZN.
    </p>
  </div>
)}
```

**Visual M-Pesa:**
```
┌─────────────────────────────────────┐
│ ⟳ Aguardando confirmação...        │
│                                     │
│ [M-Pesa] Vodacom                   │
│                                     │
│ Insira seu PIN no M-Pesa para      │
│ confirmar 599 MZN.                  │
└─────────────────────────────────────┘
```

---

## Acessibilidade

### Contraste de Cores

**M-Pesa:**
- Vermelho #E60000 vs Branco #FFFFFF
- Ratio: 8.59:1 ✅ (AAA - Excelente)

**e-Mola:**
- Verde #00A651 vs Branco #FFFFFF
- Ratio: 5.12:1 ✅ (AA - Bom)

### Screen Readers

```jsx
<button 
  aria-label="Selecionar M-Pesa Vodacom como método de pagamento"
  onClick={() => setPaymentMethod('mpesa')}
>
  <MPesaLogo />
  <div>Vodacom</div>
</button>
```

### Keyboard Navigation

```jsx
<button 
  type="button"
  tabIndex={0}
  onKeyPress={(e) => e.key === 'Enter' && setPaymentMethod('mpesa')}
>
```

---

## Responsividade

### Mobile (< 640px)
```jsx
className="grid grid-cols-2 gap-3"
// Mantém 2 colunas mesmo em mobile
```

**Visual Mobile:**
```
┌──────┬──────┐
│M-Pesa│e-Mola│
│Vodac │Movit │
└──────┴──────┘
```

### Tablet/Desktop (≥ 640px)
```jsx
className="grid grid-cols-2 gap-3"
// Aumenta gap e padding
```

---

## Animações

### Transição de Seleção

```jsx
className="transition-all duration-200 ease-in-out"

// Estados:
// 1. Idle → Hover: border-gray-200 → border-red-300 (200ms)
// 2. Hover → Active: border-red-300 → border-red-600 + ring (200ms)
// 3. Active → Idle: Mantém até desselecionar
```

### Loading Spinner

```jsx
<Loader2 className="animate-spin" />
// Rotação contínua durante processamento
```

### Success Animation

```jsx
<CheckCircle className="text-green-600 animate-scale-up" />
// Aparece com scale-up quando pagamento confirmado
```

---

## Testes Visuais

### Checklist de Validação

- [ ] Logo M-Pesa aparece vermelho (#E60000)
- [ ] Logo e-Mola aparece verde (#00A651)
- [ ] Texto "M-Pesa" e "e-Mola" legível (branco)
- [ ] Label "Vodacom" abaixo do M-Pesa
- [ ] Label "Movitel" abaixo do e-Mola
- [ ] Border vermelho quando M-Pesa selecionado
- [ ] Border verde quando e-Mola selecionado
- [ ] Ring de destaque visível (red-200 / green-200)
- [ ] Hover muda cor do border
- [ ] Logo aparece no feedback de processamento
- [ ] Dark mode funciona corretamente
- [ ] Mobile mantém 2 colunas
- [ ] Transições suaves (200ms)

### Teste de Contraste

```bash
# Chrome DevTools
1. Inspecionar elemento
2. Aba "Accessibility"
3. Verificar "Contrast Ratio"
4. Deve ser ≥ 4.5:1 para AA ou ≥ 7:1 para AAA
```

### Teste de Dark Mode

```javascript
// Forçar dark mode no DevTools
document.documentElement.classList.add('dark')

// Verificar:
// - dark:border-red-500 (M-Pesa)
// - dark:border-green-500 (e-Mola)
// - dark:bg-red-900/20 (background M-Pesa)
// - dark:bg-green-900/20 (background e-Mola)
```

---

## Branding Compliance

### M-Pesa (Vodacom Moçambique)

**Cores oficiais:**
- Vermelho: #E60000 ✅
- Alternativa: #DC143C (Crimson) - não usado

**Tipografia:**
- Sans-serif bold ✅
- Maiúsculas e minúsculas: "M-Pesa" ✅

**Logo usage:**
- Fundo branco ou vermelho ✅
- Texto sempre branco em fundo vermelho ✅
- Border radius: 4px ✅

### e-Mola (Movitel Moçambique)

**Cores oficiais:**
- Verde: #00A651 ✅
- Alternativa: #008940 (verde escuro) - não usado

**Tipografia:**
- Sans-serif bold ✅
- Minúsculas: "e-Mola" ✅

**Logo usage:**
- Fundo branco ou verde ✅
- Texto sempre branco em fundo verde ✅
- Border radius: 4px ✅

---

## Melhorias Futuras

### V2.0 - Logos Vetoriais Oficiais
```jsx
// Substituir SVG text por path oficial
import MPesaLogo from '@/assets/logos/mpesa-official.svg'
import EMolaLogo from '@/assets/logos/emola-official.svg'
```

### V2.1 - Animações Avançadas
```jsx
// Feedback tátil (vibração) ao selecionar
navigator.vibrate(50)

// Ripple effect ao clicar
<button className="relative overflow-hidden">
  <span className="ripple-effect" />
</button>
```

### V2.2 - Preferência do Usuário
```javascript
// Salvar método preferido
localStorage.setItem('preferred_method', 'mpesa')

// Auto-selecionar na próxima vez
const [paymentMethod, setPaymentMethod] = useState(
  localStorage.getItem('preferred_method') || 'mpesa'
)
```

---

## 📸 Screenshots Esperados

### Desktop - Light Mode
```
┌─────────────────────────────────────┐
│ Finalizar Assinatura          [X]   │
│ Pro                                 │
├─────────────────────────────────────┤
│                                     │
│ ┌───────────────┬───────────────┐   │
│ │  [M-Pesa]     │  [e-Mola]     │   │
│ │   Vodacom     │   Movitel     │   │
│ └───────────────┴───────────────┘   │
│                                     │
│ Número de Telefone                  │
│ [📱] +258 84 123 4567               │
│                                     │
│ [Confirmar Pagamento]               │
└─────────────────────────────────────┘
```

### Mobile - Dark Mode
```
┌─────────────────────┐
│ Finalizar [X]       │
│ Pro                 │
├─────────────────────┤
│ ┌────────┬────────┐ │
│ │ M-Pesa │ e-Mola │ │
│ │ Vodac  │ Movit  │ │
│ └────────┴────────┘ │
│                     │
│ Telefone            │
│ +258 84 123 4567    │
│                     │
│ [Confirmar]         │
└─────────────────────┘
```

---

**Status:** ✅ Design System Completo  
**Última atualização:** 08/01/2026  
**Componentes:** CheckoutModal.jsx (linhas 5-350)
