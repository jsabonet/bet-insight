# 🔍 Como Ver os Logs no Console do Navegador

## 📋 Passo a Passo

### 1. Abrir Developer Tools
- **Chrome/Edge:** Pressione `F12` ou `Ctrl+Shift+I`
- **Firefox:** Pressione `F12` ou `Ctrl+Shift+K`
- Ou clique com botão direito → "Inspecionar" → Aba "Console"

### 2. Iniciar o Frontend
```bash
cd frontend
npm run dev
```

### 3. Acessar a Aplicação
Abra: `http://localhost:5173` no navegador

### 4. Analisar uma Partida
- Clique em qualquer partida da lista
- Clique no botão "🤖 Analisar com IA"
- **Os logs aparecerão automaticamente no console!**

---

## 📊 Logs Disponíveis no Console

### 🔥 Estrutura dos Logs:

```
================================================================================
📥 HOMEPAGE: Resposta da análise recebida
================================================================================
✅ Status: 200
⭐ Confiança: 4 /5

📊 METADATA (dados analisados):
   Previsões (API-Football): ✅
   Estatísticas ao vivo: ✅
   H2H (Football-Data): ✅
   └─ Jogos H2H analisados: 5
   Detalhes da partida: ✅

🔥 DADOS ENRIQUECIDOS RECEBIDOS:
================================================================================

📊 POSIÇÃO NA TABELA:
   Casa: 14º lugar, 46 pts (Forma: LLLWL)
   Fora: 3º lugar, 82 pts (Forma: WWDWL)

🚑 LESÕES/SUSPENSÕES: 0 (casa), 4 (fora)

💰 ODDS:
   Casa: 2.10 | Empate: 3.40 | Fora: 3.50
   Over 2.5: 1.65 | Under 2.5: 2.20

📈 ESTATÍSTICAS DOS TIMES:
   Casa: 1.58 gols/jogo
   Fora: 2.16 gols/jogo

📊 TENDÊNCIAS (últimos 10 jogos):
   🏠 Casa: Over 2.5: 50% | BTTS: 60%
   ✈️ Fora: Over 2.5: 70% | BTTS: 70%
   💡 Probabilidade combinada Over 2.5: 60%
   💡 Probabilidade combinada BTTS: 65%

⏱️ DESCANSO ENTRE JOGOS:
   🏠 Casa: 3 dias de descanso
   ✈️ Fora: 7 dias de descanso
   📊 Vantagem física: ✈️ Fora

🎖️ MOTIVAÇÃO E CONTEXTO:
   Normal league match
   🏠 Casa: LOW - Mid-table sem objetivos
   ✈️ Fora: VERY_HIGH - Luta pelo título

📅 TEMPORADA: 2023 - Regular Season - 5
================================================================================
```

---

## 🎯 O Que Cada Seção Mostra

### 📊 POSIÇÃO NA TABELA
- Posição atual de cada time
- Pontos acumulados
- Forma recente (últimos 5 jogos)

### 🚑 LESÕES/SUSPENSÕES
- Número de jogadores indisponíveis
- Separado por time (casa/fora)

### 💰 ODDS
- Probabilidades das casas de apostas
- Odds para resultado (casa/empate/fora)
- Odds para Over/Under 2.5

### 📈 ESTATÍSTICAS DOS TIMES
- Média de gols marcados por jogo
- Dados da temporada atual

### 📊 TENDÊNCIAS (Últimos 10 Jogos) ⭐ NOVO!
- **Over 2.5:** Percentual de jogos com 3+ gols
- **BTTS:** Percentual de jogos onde ambos marcaram
- **Probabilidade combinada:** Média entre casa e fora

### ⏱️ DESCANSO ENTRE JOGOS ⭐ NOVO!
- Dias desde o último jogo de cada time
- Identificação de vantagem física
- Detecção de fadiga

### 🎖️ MOTIVAÇÃO E CONTEXTO ⭐ NOVO!
- Nível de motivação baseado na posição
- Razão (título, Champions, rebaixamento)
- Contexto especial (confrontos diretos)

### 📅 TEMPORADA
- Ano da temporada
- Rodada/fase do campeonato

---

## 🔍 Filtros Úteis no Console

### Ver Apenas Logs de Enriquecimento:
Digite no filtro do console: `ENRIQUECIDOS`

### Ver Apenas Tendências:
Digite no filtro: `TENDÊNCIAS`

### Ver Apenas Motivação:
Digite no filtro: `MOTIVAÇÃO`

### Ver Apenas Descanso:
Digite no filtro: `DESCANSO`

---

## 🐛 Troubleshooting

### "Não vejo os logs"
1. ✅ Verifique se o console está aberto (F12)
2. ✅ Confirme que a análise foi executada
3. ✅ Verifique se não há filtros ativos no console
4. ✅ Limpe o console (ícone 🚫) e tente novamente

### "Logs aparecem duplicados"
- Normal se você analisar a mesma partida 2x
- Limpe o console (Ctrl+L ou ícone 🚫)

### "Algumas seções não aparecem"
- ⚠️ Odds: Nem todas as partidas têm odds disponíveis
- ⚠️ Lesões: Só aparecem se houver jogadores indisponíveis
- ✅ Outras seções devem sempre aparecer

---

## 📸 Exemplo Visual

Quando você analisar uma partida, verá algo assim no console:

```
┌─────────────────────────────────────────────────────────────┐
│ 📥 HOMEPAGE: Resposta da análise recebida                   │
├─────────────────────────────────────────────────────────────┤
│ ✅ Status: 200                                              │
│ ⭐ Confiança: 5/5                                           │
│                                                              │
│ 🔥 DADOS ENRIQUECIDOS RECEBIDOS:                            │
│                                                              │
│ 📊 TENDÊNCIAS (últimos 10 jogos):                           │
│    🏠 Casa: Over 2.5: 80% | BTTS: 60%                       │
│    ✈️ Fora: Over 2.5: 70% | BTTS: 50%                       │
│    💡 Probabilidade combinada Over 2.5: 75%                 │
│                                                              │
│ ⏱️ DESCANSO ENTRE JOGOS:                                    │
│    🏠 Casa: 3 dias de descanso                              │
│    ✈️ Fora: 7 dias de descanso                              │
│    📊 Vantagem física: ✈️ Fora                              │
│                                                              │
│ 🎖️ MOTIVAÇÃO E CONTEXTO:                                    │
│    🔥 Confronto direto pelo topo da tabela                  │
│    🏠 Casa: VERY_HIGH - Luta pelo título                    │
│    ✈️ Fora: VERY_HIGH - Luta pelo título                    │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist de Verificação

Antes de relatar que os logs não funcionam, verifique:

- [ ] Frontend rodando (`npm run dev`)
- [ ] Backend rodando (`python manage.py runserver`)
- [ ] Console do navegador aberto (F12 → Console)
- [ ] Análise executada com sucesso
- [ ] Sem erros no console (linhas vermelhas)
- [ ] Resposta da API foi recebida (Status 200)

---

## 🚀 Testando Agora

**Execute este teste rápido:**

1. Abra o navegador em `http://localhost:5173`
2. Pressione `F12` para abrir o console
3. Clique em qualquer partida da lista
4. Clique em "🤖 Analisar com IA"
5. **Aguarde 5-10 segundos**
6. ✅ Os logs aparecem automaticamente!

---

## 📚 Documentação Adicional

- **Código Frontend:** `frontend/src/pages/HomePage.jsx` (linhas 155-250)
- **Código Backend:** `backend/apps/analysis/services/match_enricher.py`
- **Teste Backend:** `python backend/test_logs_variaveis.py`

---

**Última Atualização:** 31 de Dezembro de 2025
**Versão:** 2.0
