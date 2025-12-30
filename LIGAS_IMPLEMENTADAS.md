# 🏆 LIGAS IMPLEMENTADAS NO SISTEMA

## ✅ Status: 35 Competições Configuradas

O sistema agora inclui todas as ligas solicitadas, com prioridade especial para competições de Moçambique e África.

---

## 📊 Ligas por Região

### 🇲🇿 MOÇAMBIQUE (Prioridade Máxima)
| Liga | Prioridade | API-Football ID | Status |
|------|-----------|----------------|--------|
| **Moçambola** | 100 | - | ✅ Configurada |
| **Taça de Moçambique** | 95 | - | ✅ Configurada |
| **Supertaça de Moçambique** | 90 | - | ✅ Configurada |
| **Seleção Nacional** | 98 | - | ✅ Configurada |

### 🇿🇦 ÁFRICA DO SUL
| Liga | Prioridade | API-Football ID | Status |
|------|-----------|----------------|--------|
| **DSTV Premiership** | 85 | 288 | ✅ Configurada |
| **MTN 8** | 80 | 1367 | ✅ Configurada |
| **Nedbank Cup** | 80 | 1366 | ✅ Configurada |

### 🌍 COMPETIÇÕES AFRICANAS
| Liga | Prioridade | API-Football ID | Status |
|------|-----------|----------------|--------|
| **CAF Champions League** | 88 | 12 | ✅ Configurada |
| **CAF Confederation Cup** | 85 | 13 | ✅ Configurada |
| **Copa Africana de Nações** | 92 | 1 | ✅ Configurada |
| **Eliminatórias AFCON** | 88 | 20 | ✅ Configurada |
| **Eliminatórias Copa do Mundo** | 89 | 29 | ✅ Configurada |

### 🏴󠁧󠁢󠁥󠁮󠁧󠁿 INGLATERRA
| Liga | Prioridade | API-Football ID | Status |
|------|-----------|----------------|--------|
| **Premier League** | 95 | 39 | ✅ Configurada |
| **FA Cup** | 85 | 45 | ✅ Configurada |
| **EFL Cup** | 82 | 48 | ✅ Configurada |

### 🇪🇸 ESPANHA
| Liga | Prioridade | API-Football ID | Status |
|------|-----------|----------------|--------|
| **La Liga** | 95 | 140 | ✅ Configurada |
| **Copa del Rey** | 85 | 143 | ✅ Configurada |

### 🇮🇹 ITÁLIA
| Liga | Prioridade | API-Football ID | Status |
|------|-----------|----------------|--------|
| **Serie A** | 93 | 135 | ✅ Configurada |
| **Coppa Italia** | 83 | 137 | ✅ Configurada |

### 🇫🇷 FRANÇA
| Liga | Prioridade | API-Football ID | Status |
|------|-----------|----------------|--------|
| **Ligue 1** | 90 | 61 | ✅ Configurada |
| **Coupe de France** | 80 | 66 | ✅ Configurada |

### 🇩🇪 ALEMANHA
| Liga | Prioridade | API-Football ID | Status |
|------|-----------|----------------|--------|
| **Bundesliga** | 93 | 78 | ✅ Configurada |
| **DFB-Pokal** | 82 | 81 | ✅ Configurada |

### 🇵🇹 PORTUGAL
| Liga | Prioridade | API-Football ID | Status |
|------|-----------|----------------|--------|
| **Primeira Liga** | 88 | 94 | ✅ Configurada |
| **Taça de Portugal** | 80 | 96 | ✅ Configurada |

### 🌍 COMPETIÇÕES EUROPEIAS
| Liga | Prioridade | API-Football ID | Status |
|------|-----------|----------------|--------|
| **UEFA Champions League** | 99 | 2 | ✅ Configurada |
| **UEFA Europa League** | 90 | 3 | ✅ Configurada |
| **UEFA Conference League** | 85 | 848 | ✅ Configurada |

### 🌎 COMPETIÇÕES INTERNACIONAIS
| Liga | Prioridade | API-Football ID | Status |
|------|-----------|----------------|--------|
| **Copa do Mundo FIFA** | 100 | 1 | ✅ Configurada |
| **Eurocopa** | 98 | 4 | ✅ Configurada |
| **Liga das Nações UEFA** | 87 | 5 | ✅ Configurada |
| **Amistosos Internacionais** | 70 | 10 | ✅ Configurada |

### 🌍 OUTRAS LIGAS
| Liga | País | Prioridade | API-Football ID |
|------|------|-----------|----------------|
| **Brasileirão Série A** | 🇧🇷 Brasil | 88 | 71 |
| **Saudi Pro League** | 🇸🇦 Arábia Saudita | 85 | 307 |
| **MLS** | 🇺🇸 Estados Unidos | 83 | 253 |

---

## 🎯 Sistema de Prioridades

O sistema usa prioridades para ordenar as ligas no frontend:

- **100**: Copa do Mundo, Moçambola
- **95-99**: Competições nacionais top (Premier League, La Liga) e Seleção de Moçambique
- **90-94**: Competições africanas importantes, grandes ligas europeias
- **85-89**: Ligas africanas regionais, competições europeias secundárias
- **80-84**: Copas nacionais
- **70-79**: Amistosos e competições menores

---

## 🚀 Como Usar

### 1. Buscar Partidas de uma Liga Específica

Com a API-Football configurada:

```bash
# Buscar partidas da Premier League
GET /api/matches/from_api/?date=2025-12-29&league=39

# Buscar partidas da Moçambola (quando disponível na API)
GET /api/matches/from_api/?date=2025-12-29&league=mocambola
```

### 2. Popular Ligas Novamente

Se precisar recarregar ou atualizar as ligas:

```bash
cd backend
python manage.py populate_leagues
```

### 3. Adicionar Novas Ligas

Edite `backend/apps/matches/management/commands/populate_leagues.py` e adicione:

```python
{
    'name': 'Nome da Liga',
    'country': 'País',
    'priority': 85,  # 0-100
    'api_football_id': 123,  # ID da API-Football
},
```

Depois execute:
```bash
python manage.py populate_leagues
```

---

## 📝 IDs da API-Football

### Como Encontrar IDs de Ligas:

1. Acesse: https://www.api-football.com/documentation-v3#tag/Leagues
2. Use o endpoint `/leagues` com filtros:
   ```
   GET https://v3.football.api-sports.io/leagues?country=Mozambique
   ```
3. A resposta inclui o `league.id` para cada competição

### Ligas Moçambicanas na API-Football:

**Nota**: As competições de Moçambique podem não estar disponíveis na API-Football gratuita. Alternativas:

1. **Football-Data.org**: Não inclui Moçambique
2. **API própria**: Integrar com fonte local de dados
3. **Scraping**: Sites de notícias esportivas moçambicanas
4. **Manual**: Criar endpoint personalizado para partidas da Moçambola

---

## 🔄 Mock Data para Desenvolvimento

Quando a API não retorna dados, o sistema usa partidas de exemplo incluindo:

- **Costa do Sol vs Ferroviário de Maputo** (Moçambola)
- **UD Songo vs Ferroviário de Nampula** (Moçambola)
- **Mamelodi Sundowns vs Orlando Pirates** (DSTV Premiership)
- Partidas de todas as principais ligas europeias

---

## 📊 Estatísticas Atuais

```
Total de Ligas: 35
├── África: 5
├── Europa: 5
├── Moçambique: 4
├── Inglaterra: 3
├── África do Sul: 3
├── Portugal: 2
├── Espanha: 2
├── Mundial: 2
├── Itália: 2
├── França: 2
├── Alemanha: 2
└── Outras: 3
```

---

## 🛠️ Manutenção

### Atualizar Prioridades

```python
from apps.matches.models import League

# Aumentar prioridade da Moçambola
league = League.objects.get(name='Moçambola')
league.priority = 100
league.save()
```

### Listar Ligas Ativas

```bash
python manage.py shell

>>> from apps.matches.models import League
>>> leagues = League.objects.filter(is_active=True).order_by('-priority')
>>> for l in leagues:
...     print(f"{l.priority} - {l.name} ({l.country})")
```

### Desativar Liga

```python
league = League.objects.get(name='Nome da Liga')
league.is_active = False
league.save()
```

---

## 🎯 Próximos Passos

1. **Integrar fonte de dados para Moçambola**
   - Investigar APIs locais
   - Considerar parceria com federação moçambicana
   - Scraping de sites de notícias esportivas

2. **Filtros no Frontend**
   - Filtro por país/região
   - Filtro por competição
   - Busca por nome da liga

3. **Análises Específicas**
   - Análises personalizadas para ligas africanas
   - Contexto local (clima, viagens, etc.)
   - Históricos de confrontos

4. **Notificações**
   - Alertas para jogos da Moçambola
   - Notificações de seleção moçambicana
   - Alertas CAF Champions League

---

## ✅ Conclusão

Todas as 35 competições solicitadas estão **configuradas e prontas** para uso. O sistema:

✅ Inclui todas as ligas de Moçambique, África do Sul e África  
✅ Cobre as principais competições europeias e internacionais  
✅ Usa sistema de prioridades para destaque de ligas importantes  
✅ Tem IDs da API-Football para buscar partidas reais  
✅ Inclui mock data com times moçambicanos e africanos  
✅ Está pronto para análises e exibição no frontend  

Para dados reais da Moçambola, será necessário integrar fonte de dados específica.
