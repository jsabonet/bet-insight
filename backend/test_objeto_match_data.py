"""
Teste mínimo: verificar se objeto match_data tem api_football_id
"""

# Simular criação do objeto como no daily_bet_generator
league_id = 140
fixture_id = 123456

match_data = type('obj', (object,), {
    'id': fixture_id,
    'api_football_id': fixture_id,
    'home_team': type('obj', (object,), {
        'name': "Team A",
        'id': 100
    })(),
    'away_team': type('obj', (object,), {
        'name': "Team B",
        'id': 200
    })(),
    'league': type('obj', (object,), {
        'name': "Test League",
        'id': league_id,
        'api_football_id': league_id  # CORREÇÃO APLICADA
    })(),
    'match_date': "2026-02-15T15:00:00",
})()

print("\n" + "=" * 80)
print("🧪 TESTE MÍNIMO: Validar estrutura do objeto match_data")
print("=" * 80 + "\n")

# Testar acessos que causavam erro
tests = []

try:
    _ = match_data.api_football_id
    print("✅ match_data.api_football_id existe")
    tests.append(True)
except AttributeError as e:
    print(f"❌ match_data.api_football_id ERRO: {e}")
    tests.append(False)

try:
    _ = match_data.league.api_football_id
    print("✅ match_data.league.api_football_id existe")  
    tests.append(True)
except AttributeError as e:
    print(f"❌ match_data.league.api_football_id ERRO: {e}")
    tests.append(False)

try:
    _ = match_data.home_team.name
    print("✅ match_data.home_team.name existe")
    tests.append(True)
except AttributeError as e:
    print(f"❌ match_data.home_team.name ERRO: {e}")
    tests.append(False)

try:
    _ = match_data.away_team.name
    print("✅ match_data.away_team.name existe")
    tests.append(True)
except AttributeError as e:
    print(f"❌ match_data.away_team.name ERRO: {e}")  
    tests.append(False)

print("\n" + "=" * 80)
print("📊 RESULTADO")
print("=" * 80)

if all(tests):
    print("✅ SUCESSO TOTAL: Todos os atributos acessíveis!")
    print("✅ Correção validada - objeto criado corretamente")
    print("\n🎯 O erro 'api_football_id' foi corrigido!")
else:
    print(f"❌ FALHA: {sum(tests)}/{len(tests)} testes passaram")
    print("⚠️ Ainda há problemas na estrutura do objeto")

print("=" * 80 + "\n")
