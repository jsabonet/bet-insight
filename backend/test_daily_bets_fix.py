"""
Teste rápido: simular geração com 1 partida apenas
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.daily_bet_generator import DailyBetGenerator
import logging

# Reduzir logging
logging.getLogger('apps.analysis.services.match_enricher').setLevel(logging.WARNING)
logging.getLogger('apps.analysis.services.api_football_service').setLevel(logging.WARNING)
logging.getLogger('apps.analysis.services.feature_engineer').setLevel(logging.WARNING)
logging.getLogger('apps.analysis.services.context_analyzer').setLevel(logging.WARNING)
logging.getLogger('apps.analysis.services.analysis_orchestrator').setLevel(logging.ERROR)

print("\n" + "=" * 80)
print("🧪 TESTE: Gerar Daily Bets (análise de 1 partida para validar correção)")
print("=" * 80 + "\n")

generator = DailyBetGenerator()

# Buscar apenas 1 partida passando limite
print("🔍 Buscando apenas 1 partida para teste rápido...\n")

# Modificar o método para limitar fixtures
from datetime import datetime, timedelta
from django.utils import timezone

today = timezone.now().date()
date_str = today.strftime('%Y-%m-%d')

# Buscar manualmente 1 fixture
from apps.analysis.services.api_football_service import APIFootballService
api = APIFootballService()

# Buscar da primeira liga com partidas hoje
test_fixture = None
for league_id in [140, 135, 78, 61, 94]:  # Testar ligas principais
    response = api.get_fixtures_by_date(date_str, league_id=league_id, season=2025)
    if response and response.get('response'):
        fixtures = response['response']
        if fixtures:
            test_fixture = fixtures[0]
            print(f"✅ Encontrada partida de teste: {test_fixture.get('teams', {}).get('home', {}).get('name')} vs {test_fixture.get('teams', {}).get('away', {}).get('name')}")
            break

if not test_fixture:
    print("❌ Nenhuma partida encontrada para teste")
    exit(1)

# Criar objeto match_data manualmente
fixture_data = test_fixture.get('fixture', {})
teams = test_fixture.get('teams', {})
league = test_fixture.get('league', {})

fixture_id = fixture_data.get('id')
home_team = teams.get('home', {}).get('name', 'Unknown')
away_team = teams.get('away', {}).get('name', 'Unknown')
league_name = league.get('name', 'Unknown')
league_id = league.get('id')

match_data = type('obj', (object,), {
    'id': fixture_id,
    'api_football_id': fixture_id,
    'home_team': type('obj', (object,), {
        'name': home_team,
        'id': teams.get('home', {}).get('id')
    })(),
    'away_team': type('obj', (object,), {
        'name': away_team,
        'id': teams.get('away', {}).get('id')
    })(),
    'league': type('obj', (object,), {
        'name': league_name,
        'id': league_id,
        'api_football_id': league_id
    })(),
    'match_date': fixture_data.get('date'),
})()

print(f"\n📋 Testando análise...")
print(f"   🏟️ Partida: {home_team} vs {away_team}")
print(f"   🏆 Liga: {league_name} (ID: {league_id})")
print(f"   🆔 Fixture ID: {fixture_id}\n")

# Testar análise VALUE
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
orchestrator = HybridAnalysisOrchestrator()

try:
    print("🔍 Executando análise VALUE...")
    result_value = orchestrator.run(match_data, strategy='value')
    print("✅ Análise VALUE concluída SEM ERROS!")
    success_value = True
except Exception as e:
    print(f"❌ ERRO na análise VALUE: {e}")
    success_value = False

try:
    print("🔍 Executando análise MULTIPLE...")
    result_multiple = orchestrator.run(match_data, strategy='multiple')
    print("✅ Análise MULTIPLE concluída SEM ERROS!")
    success_multiple = True
except Exception as e:
    print(f"❌ ERRO na análise MULTIPLE: {e}")
    success_multiple = False

print("\n" + "=" * 80)
print("📊 RESULTADO DO TESTE")
print("=" * 80)

if success_value and success_multiple:
    print("✅ SUCESSO TOTAL: Ambas análises executadas sem erro 'api_football_id'!")
    print("✅ Correção validada - objeto match_data está correto")
elif success_value or success_multiple:
    print("⚠️ PARCIAL: Uma análise funcionou, outra falhou")
else:
    print("❌ FALHA: Ambas análises falharam")
    
print("=" * 80 + "\n")
