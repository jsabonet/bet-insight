"""
Script para testar o sistema de cache da API-Football
"""
import os
import sys
import django
import time

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.cache import cache
from apps.analysis.services.api_football_service import APIFootballService

def print_separator(title=""):
    print("\n" + "="*80)
    if title:
        print(f"{'='*10} {title:^56} {'='*10}")
        print("="*80)

def test_cache_system():
    """Testa o sistema de cache fazendo múltiplas requisições"""
    
    print_separator("🧪 TESTE DO SISTEMA DE CACHE")
    
    # Limpar cache antes do teste
    cache.clear()
    print("🗑️ Cache limpo!\n")
    
    # Inicializar serviço
    service = APIFootballService()
    
    # Parâmetros de teste (mesmo fixture do teste anterior)
    fixture_id = 1035086
    league_id = 39  # Premier League
    season = 2023
    team_id = 42  # Arsenal
    
    print_separator("📊 TESTE 1: Standings (Cache Hit após 2ª chamada)")
    
    print("\n1️⃣ Primeira chamada (deve buscar da API):")
    start = time.time()
    standings1 = service.fetch_standings(league_id, season)
    time1 = time.time() - start
    print(f"   ⏱️ Tempo: {time1:.3f}s")
    print(f"   ✅ Times na tabela: {len(standings1) if standings1 else 0}")
    
    print("\n2️⃣ Segunda chamada (deve usar cache):")
    start = time.time()
    standings2 = service.fetch_standings(league_id, season)
    time2 = time.time() - start
    print(f"   ⏱️ Tempo: {time2:.3f}s")
    print(f"   ✅ Times na tabela: {len(standings2) if standings2 else 0}")
    
    speedup1 = time1 / time2 if time2 > 0 else 0
    print(f"\n   📈 Speedup: {speedup1:.1f}x mais rápido com cache!")
    
    print_separator("🚑 TESTE 2: Injuries (Cache Hit após 2ª chamada)")
    
    print("\n1️⃣ Primeira chamada (deve buscar da API):")
    start = time.time()
    injuries1 = service.fetch_injuries(fixture_id)
    time1 = time.time() - start
    print(f"   ⏱️ Tempo: {time1:.3f}s")
    print(f"   ✅ Lesões: {len(injuries1['home'])} casa, {len(injuries1['away'])} fora")
    
    print("\n2️⃣ Segunda chamada (deve usar cache):")
    start = time.time()
    injuries2 = service.fetch_injuries(fixture_id)
    time2 = time.time() - start
    print(f"   ⏱️ Tempo: {time2:.3f}s")
    print(f"   ✅ Lesões: {len(injuries2['home'])} casa, {len(injuries2['away'])} fora")
    
    speedup2 = time1 / time2 if time2 > 0 else 0
    print(f"\n   📈 Speedup: {speedup2:.1f}x mais rápido com cache!")
    
    print_separator("📈 TESTE 3: Team Statistics (Cache Hit após 2ª chamada)")
    
    print("\n1️⃣ Primeira chamada (deve buscar da API):")
    start = time.time()
    stats1 = service.fetch_team_statistics(team_id, league_id, season)
    time1 = time.time() - start
    print(f"   ⏱️ Tempo: {time1:.3f}s")
    print(f"   ✅ Stats: {stats1['games_played']} jogos" if stats1 else "   ❌ Sem dados")
    
    print("\n2️⃣ Segunda chamada (deve usar cache):")
    start = time.time()
    stats2 = service.fetch_team_statistics(team_id, league_id, season)
    time2 = time.time() - start
    print(f"   ⏱️ Tempo: {time2:.3f}s")
    print(f"   ✅ Stats: {stats2['games_played']} jogos" if stats2 else "   ❌ Sem dados")
    
    speedup3 = time1 / time2 if time2 > 0 else 0
    print(f"\n   📈 Speedup: {speedup3:.1f}x mais rápido com cache!")
    
    print_separator("🏟️ TESTE 4: Fixture Details (Cache Hit após 2ª chamada)")
    
    print("\n1️⃣ Primeira chamada (deve buscar da API):")
    start = time.time()
    fixture1 = service.fetch_fixture_details(fixture_id)
    time1 = time.time() - start
    print(f"   ⏱️ Tempo: {time1:.3f}s")
    print(f"   ✅ Fixture: {fixture1['home_team']['name']} vs {fixture1['away_team']['name']}" if fixture1 else "   ❌ Sem dados")
    
    print("\n2️⃣ Segunda chamada (deve usar cache):")
    start = time.time()
    fixture2 = service.fetch_fixture_details(fixture_id)
    time2 = time.time() - start
    print(f"   ⏱️ Tempo: {time2:.3f}s")
    print(f"   ✅ Fixture: {fixture2['home_team']['name']} vs {fixture2['away_team']['name']}" if fixture2 else "   ❌ Sem dados")
    
    speedup4 = time1 / time2 if time2 > 0 else 0
    print(f"\n   📈 Speedup: {speedup4:.1f}x mais rápido com cache!")
    
    print_separator("📅 TESTE 5: Team Fixtures (Cache Hit após 2ª chamada)")
    
    print("\n1️⃣ Primeira chamada (deve buscar da API):")
    start = time.time()
    fixtures1 = service.fetch_team_fixtures(team_id, league_id, season, last=10)
    time1 = time.time() - start
    print(f"   ⏱️ Tempo: {time1:.3f}s")
    print(f"   ✅ Fixtures: {len(fixtures1)} jogos" if fixtures1 else "   ❌ Sem dados")
    
    print("\n2️⃣ Segunda chamada (deve usar cache):")
    start = time.time()
    fixtures2 = service.fetch_team_fixtures(team_id, league_id, season, last=10)
    time2 = time.time() - start
    print(f"   ⏱️ Tempo: {time2:.3f}s")
    print(f"   ✅ Fixtures: {len(fixtures2)} jogos" if fixtures2 else "   ❌ Sem dados")
    
    speedup5 = time1 / time2 if time2 > 0 else 0
    print(f"\n   📈 Speedup: {speedup5:.1f}x mais rápido com cache!")
    
    print_separator("📊 RESUMO DO TESTE")
    
    print(f"""
    ✅ Standings:        {speedup1:.1f}x mais rápido
    ✅ Injuries:         {speedup2:.1f}x mais rápido
    ✅ Statistics:       {speedup3:.1f}x mais rápido
    ✅ Fixture Details:  {speedup4:.1f}x mais rápido
    ✅ Team Fixtures:    {speedup5:.1f}x mais rápido
    
    🎯 Média de Speedup: {(speedup1+speedup2+speedup3+speedup4+speedup5)/5:.1f}x
    
    💡 BENEFÍCIOS DO CACHE:
       • Reduz chamadas à API (economiza quota)
       • Reduz latência (respostas instantâneas)
       • Melhora experiência do usuário
       • Permite múltiplas análises sem overhead
    """)
    
    print_separator("✅ TESTE CONCLUÍDO")

if __name__ == '__main__':
    test_cache_system()
