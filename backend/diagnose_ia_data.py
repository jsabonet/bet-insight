"""
Verificar por que a IA não está recebendo dados completos
"""
import os
import django
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.matches.services.football_api import FootballAPIService
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

print("\n" + "="*100)
print("🔍 DIAGNÓSTICO: Por que a IA não recebe dados completos?")
print("="*100 + "\n")

# 1. Verificar partidas mock (from_api)
print("📊 VERIFICANDO PARTIDAS DA API (from_api endpoint):")
print("-"*100)

api = FootballAPIService()
result = api.get_fixtures_by_date('2025-12-30')

if result.get('success'):
    fixtures = result.get('fixtures', [])
    print(f"✅ Encontradas {len(fixtures)} partidas hoje\n")
    
    # Procurar Maniema
    maniema_games = [f for f in fixtures if 'Maniema' in f['teams']['home']['name'] or 'Maniema' in f['teams']['away']['name']]
    
    if maniema_games:
        game = maniema_games[0]
        print(f"🎯 JOGO ENCONTRADO:")
        print(f"   Home: {game['teams']['home']['name']}")
        print(f"   Away: {game['teams']['away']['name']}")
        print(f"   API ID: {game['fixture']['id']}")
        print(f"   Status: {game['fixture']['status']['short']}")
        print(f"   Liga: {game['league']['name']}")
        
        # Verificar se tem dados disponíveis
        fixture_id = game['fixture']['id']
        
        print(f"\n📥 Testando busca de dados para fixture_id={fixture_id}:")
        print("-"*100)
        
        # Predictions
        print("\n  1. Predictions:")
        pred = api.get_predictions(fixture_id)
        if pred.get('success'):
            print(f"     ✅ Predictions disponíveis")
            print(f"     📊 Chaves: {list(pred['predictions'].keys())[:5]}")
        else:
            print(f"     ❌ Não disponível: {pred.get('error')}")
        
        # Statistics
        print("\n  2. Statistics:")
        stats = api.get_fixture_statistics(fixture_id)
        if stats.get('success'):
            print(f"     ✅ Statistics disponíveis")
        else:
            print(f"     ❌ Não disponível: {stats.get('error')}")
        
        # Fixture details
        print("\n  3. Fixture Details:")
        fix = api.get_fixture_by_id(fixture_id)
        if fix.get('success'):
            print(f"     ✅ Fixture disponível")
        else:
            print(f"     ❌ Não disponível: {fix.get('error')}")
    else:
        print("❌ Jogo Maniema Union não encontrado na API hoje")
else:
    print(f"❌ Erro ao buscar partidas: {result.get('error')}")

# 2. Verificar partidas no banco
print("\n\n" + "="*100)
print("🗄️  VERIFICANDO BANCO DE DADOS:")
print("="*100 + "\n")

maniema_db = Match.objects.filter(home_team__name__icontains='Maniema').first()

if maniema_db:
    print(f"✅ Partida encontrada no banco:")
    print(f"   ID: {maniema_db.id}")
    print(f"   Home: {maniema_db.home_team.name}")
    print(f"   Away: {maniema_db.away_team.name}")
    print(f"   api_football_id: {maniema_db.api_football_id or '❌ NULL'}")
    print(f"   football_data_id: {maniema_db.football_data_id or '❌ NULL'}")
    print(f"   Status: {maniema_db.status}")
    
    if not maniema_db.api_football_id:
        print(f"\n⚠️  PROBLEMA ENCONTRADO:")
        print(f"   A partida no banco NÃO tem api_football_id!")
        print(f"   Sem esse ID, o backend não consegue buscar dados da API.")
else:
    print("❌ Partida não encontrada no banco (partida vem de from_api)")
    print("   Isso é normal - partidas mock não ficam no banco")

# 3. Conclusão
print("\n\n" + "="*100)
print("📝 CONCLUSÃO:")
print("="*100 + "\n")

print("O problema identificado:")
print("-"*100)
print("  1. As partidas vêm do endpoint from_api (não estão no banco)")
print("  2. O from_api retorna partidas com 'id' temporário (1000000+)")
print("  3. Esses IDs temporários NÃO são api_football_id reais")
print("  4. O frontend envia esses IDs temporários como 'api_id'")
print("  5. O backend tenta buscar dados com ID inválido")
print("  6. APIs retornam erro ou dados vazios")
print("  7. IA recebe apenas dados básicos = Confiança 1 estrela")
print("-"*100)

print("\n💡 SOLUÇÃO:")
print("-"*100)
print("  Opção 1: Usar o ID real da API-Football nos mock matches")
print("           - Mudar _generate_mock_matches() para usar IDs reais")
print("           - Exemplo: match['id'] = real_fixture_id (não 1000000+i)")
print()
print("  Opção 2: Salvar partidas da API no banco antes de exibir")
print("           - from_api salva Match objects com api_football_id")
print("           - Frontend carrega do banco em vez de from_api")
print()
print("  Opção 3: Frontend detecta se é mock (id > 1000000) e usa ID real")
print("           - Adicionar campo 'api_football_id' nas partidas mock")
print("           - Frontend envia esse campo em vez do 'id' temporário")
print("-"*100)

print("\n🎯 RECOMENDAÇÃO:")
print("-"*100)
print("  Implementar Opção 3 (mais rápida):")
print("  1. _format_api_matches() adiciona 'api_football_id' real")
print("  2. Frontend usa match.api_football_id (já implementado!)")
print("  3. Backend recebe ID correto e busca dados completos")
print("  4. IA recebe statistics + predictions + H2H = Alta confiança!")
print("-"*100)

print("\n" + "="*100)
print("✅ DIAGNÓSTICO COMPLETO")
print("="*100 + "\n")
