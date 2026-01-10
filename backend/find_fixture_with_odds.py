#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para encontrar um jogo com odds disponíveis
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/d/Projectos/Football/bet-insight/backend')

django.setup()

import logging
from apps.analysis.services.api_football_service import APIFootballService
from datetime import datetime, timedelta

logging.basicConfig(level=logging.WARNING)

def find_fixture_with_odds():
    """Encontra um jogo com odds disponíveis"""
    
    api = APIFootballService()
    
    print("\n[INFO] Buscando fixtures com odds disponíveis...")
    print("[INFO] Procurando em jogos dos ultimos 30 dias...")
    
    # Procurar em jogos recentes
    for days_back in range(0, 30, 5):
        search_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        print(f"\n[CHECK] Data: {search_date}")
        
        try:
            # Buscar fixtures da API Football
            from .services.football_api import FootballAPIService
            fapi = FootballAPIService()
            result = fapi.get_fixtures_by_date(search_date)
            
            if result.get('success') and result.get('fixtures'):
                for fixture in result['fixtures'][:5]:  # Tentar os 5 primeiros
                    fixture_id = fixture['fixture']['id']
                    home = fixture['teams']['home']['name']
                    away = fixture['teams']['away']['name']
                    
                    # Tentar buscar odds
                    odds = api.fetch_odds(fixture_id)
                    
                    if odds and odds.get('home_win'):
                        print(f"\n[FOUND] Fixture com odds!")
                        print(f"   Fixture ID: {fixture_id}")
                        print(f"   {home} vs {away}")
                        print(f"   Home: {odds.get('home_win')}")
                        print(f"   Draw: {odds.get('draw')}")
                        print(f"   Away: {odds.get('away_win')}")
                        return fixture_id, home, away
                    else:
                        print(f"   - {home} vs {away}: Sem odds (ID: {fixture_id})")
        except Exception as e:
            print(f"   [ERROR] {str(e)}")
    
    print("\n[INFO] Nenhum fixture com odds encontrado")
    return None, None, None

if __name__ == '__main__':
    fixture_id, home, away = find_fixture_with_odds()
    if fixture_id:
        print(f"\n[RESULTADO] Use fixture_id={fixture_id} para testes com {home} vs {away}")
