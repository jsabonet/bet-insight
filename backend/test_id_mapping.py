"""
Teste do mapeamento de IDs entre API-Football e Football-Data.org
"""
import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.id_mapper import APIIDMapper


def test_id_mapping():
    """Testa o mapeamento de ID para um jogo conhecido"""
    
    print("🔍 TESTE DE MAPEAMENTO DE IDs\n")
    print("="*80)
    
    mapper = APIIDMapper()
    
    # Exemplos de jogos reais para testar
    test_cases = [
        {
            'home_team': 'Manchester United',
            'away_team': 'Liverpool',
            'date': datetime(2025, 1, 5, 16, 30)
        },
        {
            'home_team': 'Real Madrid',
            'away_team': 'Barcelona',
            'date': datetime(2025, 1, 6, 20, 0)
        },
        {
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'date': datetime(2025, 1, 7, 19, 0)
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📋 TESTE {i}: {test['home_team']} vs {test['away_team']}")
        print(f"   Data: {test['date'].strftime('%Y-%m-%d %H:%M')}")
        print("-"*80)
        
        football_data_id = mapper.find_football_data_id(
            home_team=test['home_team'],
            away_team=test['away_team'],
            match_date=test['date']
        )
        
        if football_data_id:
            print(f"\n   ✅ SUCESSO!")
            print(f"   🎯 football_data_id = {football_data_id}")
        else:
            print(f"\n   ❌ Não encontrado")
            print(f"   💡 Possíveis razões:")
            print(f"      - Jogo não existe no Football-Data.org")
            print(f"      - Nomes dos times muito diferentes entre APIs")
            print(f"      - Data incorreta")
        
        print("="*80)
    
    print("\n✅ Teste concluído!\n")


if __name__ == '__main__':
    test_id_mapping()
