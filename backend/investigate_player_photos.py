"""
Investigar alternativas para obter fotos dos jogadores
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
import requests

api = FootballAPIService()

print("\n" + "="*80)
print("🔍 INVESTIGANDO ALTERNATIVAS PARA FOTOS DE JOGADORES")
print("="*80 + "\n")

# Teste 1: Verificar estrutura completa dos dados de lineups
print("1️⃣ ESTRUTURA COMPLETA DOS DADOS DE LINEUPS:")
print("-"*80)

fixture_id = 1391001  # La Liga - Getafe vs Real Sociedad
lineups_result = api.get_fixture_lineups(fixture_id)

if lineups_result['success']:
    import json
    lineup_sample = lineups_result['lineups'][0]['startXI'][0]
    print(json.dumps(lineup_sample, indent=2))
else:
    print("❌ Erro ao buscar lineups")

# Teste 2: Verificar se API-Football tem endpoint de players
print("\n\n2️⃣ TESTANDO ENDPOINT DE PLAYERS (se existir):")
print("-"*80)

try:
    # Tentar buscar dados de um jogador específico
    # Exemplo: Buscar por nome
    response = api.session.get(
        f'{api.base_url}/players',
        params={'search': 'David Soria', 'season': 2025},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Endpoint /players EXISTE!")
        print(f"Total de resultados: {len(data.get('response', []))}")
        
        if len(data.get('response', [])) > 0:
            player = data['response'][0]
            print("\n📋 Estrutura de dados do player:")
            import json
            print(json.dumps(player, indent=2)[:1000])
    else:
        print(f"⚠️  Status: {response.status_code}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n\n3️⃣ ALTERNATIVAS DISPONÍVEIS:")
print("-"*80)
print("""
✅ OPÇÃO 1: Endpoint /players da API-Football
   - Buscar jogador por ID ou nome
   - Retorna foto do jogador
   - PROBLEMA: Precisa fazer 1 requisição por jogador (22 por partida)
   - CUSTO: Alto número de chamadas à API

✅ OPÇÃO 2: Cache de fotos de jogadores
   - Primeira vez: buscar e salvar no banco de dados
   - Próximas vezes: usar cache local
   - BENEFÍCIO: Reduz chamadas à API
   - IMPLEMENTAÇÃO: Criar tabela Player no DB

✅ OPÇÃO 3: API alternativa gratuita
   - TheSportsDB API (gratuita, mas limitada)
   - Football-Data.org (gratuita com limites)
   - PROBLEMA: Qualidade e cobertura podem ser menores

✅ OPÇÃO 4: Avatares profissionais (ATUAL)
   - UI Avatars com iniciais do jogador
   - Design consistente e profissional
   - Funciona 100% do tempo
   - BENEFÍCIO: Sem custo, sem limites

❌ OPÇÃO 5: Web scraping
   - Sites como Transfermarkt, ESPN, etc.
   - PROBLEMA: Ilegal, viola termos de serviço
   - NÃO RECOMENDADO
""")

print("\n4️⃣ RECOMENDAÇÃO:")
print("-"*80)
print("""
🎯 MELHOR SOLUÇÃO: Implementar cache de fotos de jogadores

ETAPAS:
1. Criar modelo Player no Django
   - id, name, photo_url, api_player_id
   
2. Ao buscar lineups:
   - Verificar se jogador existe no DB
   - Se não: buscar da API /players e salvar
   - Se sim: usar foto do cache
   
3. Atualizar componente Lineups.jsx:
   - Usar foto do banco de dados quando disponível
   - Fallback para avatar se não encontrar

BENEFÍCIOS:
✅ Primeira partida: busca da API (lento)
✅ Próximas partidas: usa cache (rápido)
✅ Reduz 90% das chamadas à API
✅ Melhora performance
✅ Fotos reais dos jogadores
""")

print("="*80 + "\n")
