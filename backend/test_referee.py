"""
Verificar dados de árbitros na API-Football
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
import json

api = FootballAPIService()

print("\n" + "="*80)
print("🔍 VERIFICANDO DADOS DE ÁRBITROS")
print("="*80 + "\n")

fixture_id = 1391001

try:
    result = api.get_fixture_by_id(fixture_id)
    
    if result['success']:
        fixture = result['fixture']
        fixture_data = fixture.get('fixture', {})
        
        print("✅ Dados do fixture obtidos com sucesso!\n")
        
        # Verificar árbitro
        referee = fixture_data.get('referee')
        print(f"🧑‍⚖️ ÁRBITRO: {referee if referee else 'Não disponível'}")
        
        # Verificar estrutura completa
        print("\n📋 CHAVES DISPONÍVEIS EM 'fixture':")
        for key in fixture_data.keys():
            print(f"  - {key}: {type(fixture_data[key]).__name__}")
        
        # Mostrar todos os dados do fixture
        print("\n📊 DADOS COMPLETOS DO FIXTURE:")
        print(json.dumps(fixture_data, indent=2, ensure_ascii=False))
        
    else:
        print(f"❌ Erro: {result.get('error')}")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
