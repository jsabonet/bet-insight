"""
Análise de duplicação entre api_football_service.py e football_api.py
"""

print("\n" + "="*80)
print("🔍 ANÁLISE DE DUPLICAÇÃO - API FOOTBALL SERVICES")
print("="*80 + "\n")

print("📋 SITUAÇÃO ATUAL:")
print("-" * 80)
print("""
1️⃣ apps/analysis/services/api_football_service.py (APIFootballService)
   - 379 linhas
   - Usado por: match_enricher, parallel_enricher, form_analysis
   - Foco: ENRIQUECIMENTO de análises
   - Features:
     • Cache inteligente com TTL
     • fetch_standings() - classificação
     • fetch_injuries() - lesões
     • fetch_odds() - odds
     • fetch_team_statistics() - estatísticas de times
     • fetch_fixture_details() - detalhes de partidas
     • fetch_team_fixtures() - partidas de times

2️⃣ apps/matches/services/football_api.py (FootballAPIService)
   - 392 linhas
   - Usado por: views, 20+ scripts de teste
   - Foco: GESTÃO de partidas
   - Features:
     • Retry/backoff com Session
     • get_fixtures_by_date() - partidas por data
     • get_fixtures_by_league() - partidas por liga
     • get_live_fixtures() - partidas ao vivo
     • get_fixture_by_id() - detalhes de partida
     • get_fixture_statistics() - estatísticas
     • get_fixture_events() - eventos (gols, cartões)
     • get_fixture_lineups() - escalações
     • get_head_to_head() - confrontos diretos ✅ NOVO
     • get_team_last_matches() - últimos jogos ✅ NOVO
     • get_standings() - classificação ⚠️ DUPLICADO

🔴 PROBLEMAS IDENTIFICADOS:
""")

print("-" * 80)
print("1. DUPLICAÇÃO DE CÓDIGO:")
print("   - get_standings() existe em AMBOS")
print("   - Mesma API, mesma lógica, diferentes implementações")
print("")
print("2. CONFUSÃO DE RESPONSABILIDADES:")
print("   - APIFootballService (analysis) → enriquecimento")
print("   - FootballAPIService (matches) → gestão de partidas")
print("   - MAS: ambos fazem chamadas à mesma API")
print("")
print("3. FALTA DE REUTILIZAÇÃO:")
print("   - Cada serviço reimplementa conexão HTTP")
print("   - Duplicação de headers, base_url, timeout logic")
print("")
print("4. MANUTENÇÃO DIFÍCIL:")
print("   - Mudança na API-Football requer editar 2 arquivos")
print("   - Inconsistências entre implementações")

print("\n" + "="*80)
print("💡 SOLUÇÃO PROPOSTA - ARQUITETURA LIMPA")
print("="*80 + "\n")

print("""
OPÇÃO 1: CONSOLIDAR TUDO EM FootballAPIService (RECOMENDADO)
─────────────────────────────────────────────────────────────
apps/matches/services/football_api.py (BASE)
├── Manter como serviço único e completo
├── Adicionar cache (do api_football_service)
├── Manter retry/backoff (já tem)
└── Métodos:
    ├── Fixtures: get_fixtures_by_date, get_live_fixtures, etc
    ├── Detalhes: get_fixture_by_id, get_fixture_statistics, etc
    ├── Escalações: get_fixture_lineups
    ├── Histórico: get_head_to_head, get_team_last_matches
    ├── Tabela: get_standings (unificar)
    ├── Lesões: get_injuries (mover de api_football_service)
    ├── Odds: get_odds (mover de api_football_service)
    └── Estatísticas: get_team_statistics (mover de api_football_service)

apps/analysis/services/
├── match_enricher.py → Usar FootballAPIService
├── parallel_enricher.py → Usar FootballAPIService
└── form_analysis.py → Usar FootballAPIService

✅ VANTAGENS:
   • Serviço único, fácil de manter
   • Cache centralizado
   • Retry centralizado
   • Menos código duplicado
   • Imports mais simples

─────────────────────────────────────────────────────────────

OPÇÃO 2: MANTER SEPARADO MAS COM BASE COMPARTILHADA
─────────────────────────────────────────────────────────────
apps/core/services/base_api_client.py (NOVO)
├── Classe base com: cache, retry, headers
└── Métodos básicos de HTTP

apps/matches/services/football_api.py
└── Herda de BaseAPIClient
    └── Foco: fixtures, live, events

apps/analysis/services/api_football_service.py
└── Herda de BaseAPIClient
    └── Foco: enrichment, odds, injuries

⚠️ DESVANTAGENS:
   • Mais complexo
   • Ainda há overlap (standings)
   • Mais arquivos para manter
""")

print("\n" + "="*80)
print("🎯 RECOMENDAÇÃO FINAL")
print("="*80 + "\n")

print("""
IMPLEMENTAR OPÇÃO 1: CONSOLIDAR EM FootballAPIService

PASSOS:
1. ✅ Manter apps/matches/services/football_api.py (é o mais usado)
2. 📦 Adicionar cache do api_football_service
3. 🔀 Mover métodos únicos:
   - fetch_injuries → get_injuries
   - fetch_odds → get_odds
   - fetch_team_statistics → get_team_statistics
4. 🔄 Atualizar imports em:
   - match_enricher.py
   - parallel_enricher.py
   - form_analysis.py
5. 🗑️ Deletar api_football_service.py
6. ✅ Executar testes

RESULTADO:
• 1 arquivo ao invés de 2
• ~400 linhas ao invés de 760
• Código mais limpo e consistente
• Fácil manutenção
""")

print("="*80 + "\n")
