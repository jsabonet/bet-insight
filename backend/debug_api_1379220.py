"""
Debug API response for match 1379220
"""
import os
import django
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService

def main():
    match_id = 1379220
    
    api = APIFootballService()
    fixture = api.fetch_fixture_details(match_id)
    
    print("\n" + "="*80)
    print("ESTRUTURA COMPLETA DA RESPOSTA DA API")
    print("="*80 + "\n")
    
    print(json.dumps(fixture, indent=2, default=str))
    
    print("\n" + "="*80)
    print("CAMPOS ESPECÍFICOS")
    print("="*80 + "\n")
    
    print(f"fixture.get('teams'): {fixture.get('teams')}")
    print(f"fixture.get('league'): {fixture.get('league')}")
    print(f"fixture.get('goals'): {fixture.get('goals')}")
    print(f"fixture.get('odds'): {fixture.get('odds')}")
    print(f"fixture.get('statistics'): {fixture.get('statistics')}")

if __name__ == '__main__':
    main()
