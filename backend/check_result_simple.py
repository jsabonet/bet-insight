"""
Buscar resultado usando o serviço existente
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService

fixture_id = 1508602
api = APIFootballService()

# Usar o método existente que já funciona
details = api.fetch_fixture_details(fixture_id)

if details:
    print("\n" + "="*80)
    print("DETALHES DA PARTIDA")
    print("="*80)
    
    print(f"\nHome: {details.get('home_team', {}).get('name')}")
    print(f"Away: {details.get('away_team', {}).get('name')}")
    print(f"Liga: {details.get('league', {}).get('name')}")
    print(f"Data: {details.get('date')}")
    print(f"Status: {details.get('status')}")
    
    print(f"\n" + "="*80)
    print("PLACAR")
    print("="*80)
    
    home_score = details.get('home_score')
    away_score = details.get('away_score')
    
    print(f"Home Score: {home_score}")
    print(f"Away Score: {away_score}")
    
    if home_score is not None and away_score is not None:
        home_name = details.get('home_team', {}).get('name')
        away_name = details.get('away_team', {}).get('name')
        
        print(f"\nRESULTADO: {home_name} {home_score} x {away_score} {away_name}")
        
        if home_score > away_score:
            print(f"Vencedor: {home_name} (Casa)")
        elif away_score > home_score:
            print(f"Vencedor: {away_name} (Fora)")
        else:
            print(f"Empate")
    else:
        print("\nPlacar nao disponivel nos detalhes basicos")
    
    # Exibir estrutura completa
    print(f"\n" + "="*80)
    print("ESTRUTURA COMPLETA")
    print("="*80)
    import json
    print(json.dumps(details, indent=2, ensure_ascii=False)[:2000])
