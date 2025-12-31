# 🔄 Sistema de Mapeamento de IDs entre APIs

## 📋 Contexto

O sistema Bet Insight usa **duas APIs diferentes** para obter dados:

1. **API-Football (RapidAPI)** - API Principal
   - URL: `https://v3.football.api-sports.io`
   - Dados: Standings, lesões, odds, estatísticas, tendências, descanso, motivação
   - ID Field: `api_id` ou `api_football_id`

2. **Football-Data.org** - API Secundária
   - URL: `https://api.football-data.org/v4`
   - Dados: **Histórico direto (H2H)** entre times
   - ID Field: `football_data_id`

## ❓ O Problema

As duas APIs usam **sistemas de ID completamente diferentes**:
- API-Football: fixture ID 1402780
- Football-Data.org: match ID 12345

**Não existe mapeamento direto** entre os IDs. Para buscar dados H2H, precisamos:
1. Saber o `football_data_id` correspondente ao jogo
2. As APIs não fornecem essa correlação

## ✅ A Solução: APIIDMapper

Criamos um serviço inteligente que **mapeia IDs por similaridade**:

### Como funciona:

```python
from apps.matches.services.id_mapper import APIIDMapper

mapper = APIIDMapper()

# Buscar football_data_id para um jogo
football_data_id = mapper.find_football_data_id(
    home_team="Manchester United",
    away_team="Liverpool",
    match_date=datetime(2025, 1, 5, 16, 30)
)
```

### Algoritmo:

1. **Busca por data**: Busca jogos no Football-Data.org num intervalo de ±1 dia
2. **Normalização**: Remove caracteres comuns (FC, SC, AC) dos nomes
3. **Similaridade**: Calcula % de similaridade entre nomes (0-100%)
4. **Match**: Se similaridade > 70%, considera que é o mesmo jogo
5. **Retorna**: `football_data_id` ou `None` se não encontrado

### Exemplo de normalização:

```
API-Football:     "Manchester United FC"  →  "manchester united"
Football-Data:    "Manchester United"     →  "manchester united"
Similaridade:     95% ✅ MATCH!
```

## 🔧 Integração Automática

O sistema agora **mapeia automaticamente** quando você analisa um jogo:

```python
# views.py - quick_analyze endpoint
# 1. Recebe api_id do jogo
# 2. Se football_data_id não fornecido, busca automaticamente
# 3. Usa football_data_id para buscar H2H
# 4. Inclui dados H2H na análise da IA
```

### Fluxo:

```
Usuário clica "Analisar" 
  ↓
Frontend envia api_id 
  ↓
Backend tenta mapear football_data_id
  ↓
Se encontrado: Busca dados H2H
  ↓
Enriquece análise da IA com histórico direto
  ↓
Retorna análise + H2H no console
```

## 📊 Console Logs

### Quando H2H está disponível:

```
🔄 HISTÓRICO DIRETO (H2H):
   📊 Total de confrontos: 15 jogos
   🏠 Vitórias Casa: 7
   ✈️ Vitórias Fora: 5
   ⚖️ Empates: 3
   📋 Últimos confrontos:
      1. 05/10/2024: Manchester United 2-1 Liverpool
      2. 07/04/2024: Liverpool 0-0 Manchester United
      3. 17/12/2023: Manchester United 0-3 Liverpool
```

### Quando não disponível:

```
🔄 HISTÓRICO DIRETO (H2H):
   ⚠️ Não disponível (football_data_id não mapeado)
```

## 🧪 Como Testar

### 1. Teste o mapeador isoladamente:

```bash
cd backend
python test_id_mapping.py
```

### 2. Teste numa análise real:

1. Abra o frontend
2. Clique em qualquer jogo
3. Clique "Analisar com IA"
4. Abra o Console do navegador (F12)
5. Procure a seção "🔄 HISTÓRICO DIRETO"

### 3. Logs do backend:

```bash
# Terminal do backend mostrará:
🔍 [ID Mapper] Buscando jogo: Manchester United vs Liverpool em 2025-01-05
🔍 [ID Mapper] Times normalizados: 'manchester united' vs 'liverpool'
✅ [ID Mapper] Match encontrado! football_data_id=123456 (score: 95%)
📋 Manchester United vs Liverpool
```

## 📝 Arquivos Modificados

### Criados:
- `backend/apps/matches/services/id_mapper.py` - Serviço de mapeamento
- `backend/test_id_mapping.py` - Script de teste
- `docs/H2H_INTEGRACAO.md` - Esta documentação

### Modificados:
- `backend/apps/matches/views.py`:
  - Import do APIIDMapper
  - Lógica de mapeamento automático em quick_analyze
  - Inclusão de h2h no enriched_data
  
- `frontend/src/pages/HomePage.jsx`:
  - Seção de logs H2H no console
  - Estatísticas de vitórias/empates/derrotas
  
- `frontend/src/pages/MatchDetailPage.jsx`:
  - Mesma lógica de logs H2H

## 🎯 Próximos Passos

1. ✅ Mapeamento automático implementado
2. ✅ Logs H2H no console
3. ✅ Integração com IA
4. 🔄 **Opcional**: Criar UI visual para mostrar H2H na página
5. 🔄 **Opcional**: Cache de IDs mapeados no banco
6. 🔄 **Opcional**: Comando manage.py para popular IDs em batch

## 💡 Considerações

### Taxa de Sucesso Esperada:
- **Ligas principais** (Premier League, La Liga, etc): ~80-90%
- **Ligas menores**: ~50-60%
- **Motivo**: Football-Data.org cobre principalmente ligas top

### Performance:
- **Primeira análise**: +1-2s (busca H2H)
- **Análises seguintes**: Rápido (dados em cache)

### Limitações:
- Football-Data.org tem plano gratuito limitado
- Alguns jogos podem não estar na API secundária
- Nomes muito diferentes podem não fazer match

## ❓ FAQ

**Q: Por que não salvar football_data_id no banco?**  
A: Seria ideal! Podemos implementar depois com um comando batch.

**Q: E se o mapeamento falhar?**  
A: A análise continua normalmente, apenas sem dados H2H.

**Q: A IA usa H2H na análise?**  
A: Sim! Se disponível, é incluído no prompt do ai_analyzer.py

**Q: Posso desativar H2H?**  
A: Sim, basta não configurar FOOTBALL_DATA_API_KEY no .env
