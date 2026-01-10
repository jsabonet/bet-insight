"""
Teste do Sistema de Escalações (Lineups)
Verifica se a API retorna dados de escalação corretamente
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
print("🧪 TESTE: Sistema de Escalações (Lineups)")
print("="*80 + "\n")

# Teste 1: Buscar partida recente (exemplo: ID 1035086)
fixture_id = 1035086  # Wolves vs Man United (partida finalizada)

print(f"📋 Testando fixture ID: {fixture_id}\n")

# Buscar escalações
print("1️⃣ Buscando escalações...")
lineups_result = api.get_fixture_lineups(fixture_id)

if lineups_result['success']:
    lineups = lineups_result['lineups']
    print(f"   ✅ Escalações encontradas: {len(lineups)} times\n")
    
    # Exibir informações de cada time
    for idx, lineup in enumerate(lineups):
        team_name = lineup.get('team', {}).get('name', 'N/A')
        formation = lineup.get('formation', 'N/A')
        coach = lineup.get('coach', {}).get('name', 'N/A')
        
        start_xi = lineup.get('startXI', [])
        substitutes = lineup.get('substitutes', [])
        
        print(f"{'='*80}")
        print(f"   TIME {idx + 1}: {team_name}")
        print(f"{'='*80}")
        print(f"   📐 Formação: {formation}")
        print(f"   👔 Treinador: {coach}")
        print(f"   👥 Titulares: {len(start_xi)} jogadores")
        print(f"   🔄 Substitutos: {len(substitutes)} jogadores\n")
        
        # Exibir primeiros 5 titulares
        print(f"   🟢 TITULARES (primeiros 5):")
        for i, player_data in enumerate(start_xi[:5]):
            player = player_data.get('player', {})
            name = player.get('name', 'N/A')
            number = player.get('number', '?')
            pos = player.get('pos', '?')
            print(f"      {i+1}. #{number} - {name} ({pos})")
        
        # Exibir primeiros 3 substitutos
        print(f"\n   🔄 SUBSTITUTOS (primeiros 3):")
        for i, player_data in enumerate(substitutes[:3]):
            player = player_data.get('player', {})
            name = player.get('name', 'N/A')
            number = player.get('number', '?')
            pos = player.get('pos', '?')
            print(f"      {i+1}. #{number} - {name} ({pos})")
        
        print("\n")
    
    # Teste 2: Verificar estrutura dos dados
    print("2️⃣ Verificando estrutura dos dados...")
    
    first_lineup = lineups[0]
    checks = {
        'team': 'team' in first_lineup,
        'formation': 'formation' in first_lineup,
        'coach': 'coach' in first_lineup,
        'startXI': 'startXI' in first_lineup,
        'substitutes': 'substitutes' in first_lineup
    }
    
    all_ok = all(checks.values())
    
    for field, ok in checks.items():
        status = "✅" if ok else "❌"
        print(f"   {status} Campo '{field}': {'OK' if ok else 'FALTANDO'}")
    
    if all_ok:
        print("\n   ✅ Estrutura de dados completa!\n")
    else:
        print("\n   ⚠️ Alguns campos faltando!\n")
    
    # Teste 3: Verificar organização por formação
    print("3️⃣ Testando organização por formação...")
    
    formation = first_lineup.get('formation', '4-4-2')
    formation_array = formation.split('-')
    
    print(f"   📐 Formação: {formation}")
    print(f"   📊 Array: {formation_array}")
    print(f"   🧮 Linhas de campo: {len(formation_array) + 1} (+ goleiro)")
    
    expected_players = 1 + sum(int(x) for x in formation_array)  # 1 goleiro + demais
    actual_players = len(first_lineup.get('startXI', []))
    
    if expected_players == actual_players:
        print(f"   ✅ Número de jogadores correto: {actual_players}")
    else:
        print(f"   ⚠️ Esperado: {expected_players}, Encontrado: {actual_players}")
    
    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*80 + "\n")
    
else:
    print(f"   ❌ Erro ao buscar escalações: {lineups_result.get('error')}")
    print(f"   📋 Detalhes: {lineups_result.get('details', 'N/A')}")
    print(f"   🔢 Código: {lineups_result.get('error_code', 'N/A')}")
    
    print("\n" + "="*80)
    print("⚠️ TESTE FALHOU")
    print("="*80 + "\n")
    
    # Informações adicionais
    print("💡 DICAS:")
    print("   - Escalações só estão disponíveis para partidas já iniciadas ou próximas")
    print("   - Tente com um fixture_id de partida recente")
    print("   - Verifique se a API-Football está acessível")
    print("   - Verifique o limite de requisições da API")
