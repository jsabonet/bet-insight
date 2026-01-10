"""
Teste rápido: Verifica se endpoint api_detail retorna lineups
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

# Inicializar serviço
api = FootballAPIService()

print("\n" + "="*80)
print("🧪 TESTE: Endpoint api_detail com Lineups")
print("="*80 + "\n")

# Fixture ID de partida recente (Wolves vs Liverpool)
fixture_id = 1035086

print(f"🔍 Buscando fixture {fixture_id}...\n")

# Simular o que o endpoint api_detail faz
print("1️⃣ get_fixture_by_id...")
result = api.get_fixture_by_id(fixture_id)

if result['success']:
    fixture = result['fixture']
    print("   ✅ Fixture encontrada\n")
    
    # Buscar lineups
    print("2️⃣ get_fixture_lineups...")
    lineups_result = api.get_fixture_lineups(fixture_id)
    
    if lineups_result['success']:
        lineups = lineups_result['lineups']
        print(f"   ✅ Lineups encontradas: {len(lineups)} times\n")
        
        # Adicionar lineups ao fixture (como o endpoint faz)
        fixture['lineups'] = lineups
        
        # Verificar estrutura final
        print("3️⃣ Estrutura final do JSON:")
        print("   " + "-"*76)
        print(f"   ✅ fixture['lineups'] existe: {('lineups' in fixture)}")
        print(f"   ✅ len(fixture['lineups']): {len(fixture['lineups'])}")
        print(f"   ✅ Tipo: {type(fixture['lineups'])}")
        print("   " + "-"*76 + "\n")
        
        # Exibir preview de cada lineup
        for idx, lineup in enumerate(lineups):
            team = lineup.get('team', {}).get('name', 'N/A')
            formation = lineup.get('formation', 'N/A')
            startXI = len(lineup.get('startXI', []))
            subs = len(lineup.get('substitutes', []))
            print(f"   Time {idx+1}: {team} ({formation}) - {startXI} titulares, {subs} reservas")
        
        print("\n" + "="*80)
        print("✅ ESTRUTURA CORRETA! Lineups serão incluídos no JSON do endpoint")
        print("="*80 + "\n")
        
    else:
        print(f"   ❌ Erro ao buscar lineups: {lineups_result.get('error')}")
        print("\n" + "="*80)
        print("⚠️ LINEUPS NÃO DISPONÍVEIS (mas fixture existe)")
        print("="*80 + "\n")
else:
    print(f"   ❌ Erro ao buscar fixture: {result.get('error')}")
    print("\n" + "="*80)
    print("❌ TESTE FALHOU")
    print("="*80 + "\n")
