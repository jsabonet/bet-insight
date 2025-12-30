# ⏰ CONFIGURAÇÃO DE FUSO HORÁRIO - MOÇAMBIQUE

## 📋 Resumo

O sistema está configurado para o fuso horário de **Moçambique (Africa/Maputo - UTC+2)**.

---

## 🔧 Configurações Atuais

### Backend (Django)

**Arquivo**: `backend/config/settings.py`

```python
TIME_ZONE = "Africa/Maputo"  # UTC+2 (CAT - Central Africa Time)
USE_TZ = True                 # Timezone-aware (armazena em UTC)
LANGUAGE_CODE = "pt-br"       # Português
CELERY_TIMEZONE = 'Africa/Maputo'  # Tasks em horário local
```

**Como funciona:**
1. 🌐 API externa retorna: `2025-12-29T14:00:00Z` (UTC)
2. 💾 Django salva no BD: `2025-12-29 14:00:00+00:00` (UTC)
3. 📤 API retorna ao frontend: `2025-12-29T14:00:00+00:00` (UTC)
4. 🖥️ JavaScript converte automaticamente para horário local

### Frontend (React)

**Arquivo**: `frontend/src/utils/dateUtils.js`

Criamos utilitários específicos que garantem exibição correta:

```javascript
import { formatMatchDate, formatDateTime, isToday } from '@/utils/dateUtils';

// Exemplo de uso
const { day, time } = formatMatchDate(match.match_date);
// Resultado: day = "Hoje", time = "16:00"

const fullDate = formatDateTime(match.match_date);
// Resultado: "29 de dezembro de 2025, 16:00"

if (isToday(match.match_date)) {
  // Partida é hoje!
}
```

---

## ✅ Testes Realizados

### Teste 1: Configuração Backend
```bash
python test_timezone.py
```

**Resultados:**
- ✅ TIME_ZONE: Africa/Maputo
- ✅ UTC+2 aplicado corretamente
- ✅ Banco de dados timezone-aware
- ✅ Conversões automáticas funcionando

### Teste 2: Conversão de Horários

| Horário API (UTC) | Horário Moçambique (CAT) | Diferença |
|-------------------|--------------------------|-----------|
| 14:00 UTC | 16:00 CAT | +2 horas |
| 21:00 UTC | 23:00 CAT | +2 horas |
| 00:00 UTC | 02:00 CAT | +2 horas |

---

## 📱 Usando no Frontend

### Antes (ERRADO - não use):

```javascript
// ❌ NÃO fazer isso
<span>{new Date(match.match_date).toString()}</span>
// Pode exibir timezone errado dependendo do navegador

// ❌ NÃO fazer isso
<span>{match.match_date.split('T')[0]}</span>
// Ignora timezone completamente
```

### Depois (CORRETO - use sempre):

```javascript
// ✅ Usar utilitários
import { formatMatchDate, formatDateTime } from '@/utils/dateUtils';

// Para exibir data de partida
const { day, time } = formatMatchDate(match.match_date);
<div>
  <span>{day}</span>  {/* "Hoje", "Amanhã", ou "Sáb, 30 Dez" */}
  <span>{time}</span>  {/* "16:00" */}
</div>

// Para data completa
<span>{formatDateTime(match.match_date)}</span>
// "29 de dezembro de 2025, 16:00"

// Para data curta
<span>{formatDateShort(analysis.created_at)}</span>
// "29/12/2025"

// Para hora relativa
<span>{formatRelativeTime(notification.created_at)}</span>
// "há 2 horas"
```

---

## 🔄 Atualizar Componentes Existentes

### 1. MatchCard.jsx

**Antes:**
```javascript
const formatDate = (dateString) => {
  const date = new Date(dateString);
  // ... código manual ...
};
```

**Depois:**
```javascript
import { formatMatchDate } from '@/utils/dateUtils';

// No JSX
const { day, time } = formatMatchDate(match.match_date);
```

### 2. MatchDetailPage.jsx

**Antes:**
```javascript
{new Date(match.match_date).toLocaleString('pt-PT')}
```

**Depois:**
```javascript
import { formatDateTime } from '@/utils/dateUtils';

{formatDateTime(match.match_date)}
```

### 3. MyAnalysesPage.jsx

**Antes:**
```javascript
{new Date(analysis.match.match_date).toLocaleDateString('pt-PT', {...})}
```

**Depois:**
```javascript
import { formatDate } from '@/utils/dateUtils';

{formatDate(analysis.match.match_date)}
```

---

## 🌍 Teste em Diferentes Ambientes

### Desenvolvimento Local (Qualquer País)

O sistema funcionará corretamente mesmo se você estiver desenvolvendo fora de Moçambique, porque:

1. Backend sempre trabalha em UTC internamente
2. Frontend usa `timeZone: 'Africa/Maputo'` explicitamente
3. Conversões são forçadas para o timezone correto

### Produção (Servidor em Moçambique)

Se o servidor estiver em Moçambique:
- Sistema operacional provavelmente já está em CAT
- Django ainda usa UTC internamente (melhor prática)
- Frontend continua convertendo explicitamente

### Produção (Servidor Fora de Moçambique)

Se o servidor estiver na AWS/Heroku/DigitalOcean (geralmente UTC):
- ✅ Funciona perfeitamente
- Django `USE_TZ=True` garante consistência
- Frontend força timezone correto

---

## 🐛 Troubleshooting

### Problema: Datas exibidas com 2h de diferença

**Causa**: Código não está usando utilitários `dateUtils.js`

**Solução**:
```javascript
// Trocar
{new Date(date).toLocaleString()}

// Por
import { formatDateTime } from '@/utils/dateUtils';
{formatDateTime(date)}
```

### Problema: "Hoje" não aparece para jogos de hoje

**Causa**: Comparação de datas sem considerar timezone

**Solução**:
```javascript
import { isToday } from '@/utils/dateUtils';

if (isToday(match.match_date)) {
  // É hoje!
}
```

### Problema: Partidas ao vivo não detectadas

**Causa**: Não considera timezone na comparação

**Solução**:
```javascript
import { isLiveOrSoon } from '@/utils/dateUtils';

if (isLiveOrSoon(match.match_date, 2)) {
  // Partida ao vivo ou começa em 2h
}
```

---

## 📊 Verificação Rápida

Execute para verificar se tudo está OK:

```bash
# Backend
cd backend
python test_timezone.py

# Deve mostrar:
# ✅ Configuração CORRETA!
# • Timezone: Africa/Maputo (CAT, UTC+2)
```

---

## 💡 Boas Práticas

1. ✅ **Sempre use `dateUtils.js` no frontend**
2. ✅ **Nunca manipule strings de data manualmente**
3. ✅ **Backend sempre retorna ISO 8601 com timezone**
4. ✅ **Armazene em UTC, exiba em local**
5. ✅ **Use `Intl.DateTimeFormat` com `timeZone` explícito**

---

## 📚 Referências

- [Django Timezone Documentation](https://docs.djangoproject.com/en/5.0/topics/i18n/timezones/)
- [JavaScript Intl.DateTimeFormat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat)
- [IANA Timezone Database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
- [Africa/Maputo Timezone Info](https://www.timeanddate.com/worldclock/mozambique/maputo)

---

## ✅ Conclusão

✅ **Backend**: Configurado e testado
✅ **Frontend**: Utilitários criados
⏳ **Próximo passo**: Atualizar componentes para usar `dateUtils.js`

Tudo pronto para exibir corretamente horários de Moçambique! 🇲🇿
