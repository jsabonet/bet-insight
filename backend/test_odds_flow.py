#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar o fluxo completo de odds: enriquecimento -> conversao -> resposta
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/d/Projectos/Football/bet-insight/backend')

django.setup()

import json
import logging
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.api_football_service import APIFootballService

# Configurar logs detalhados
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_odds_flow():
    """Testa o fluxo completo de odds"""
    
    print("\n" + "="*80)
    print("[TESTE] FLUXO DE ODDS")
    print("="*80)
    
    # Dados de entrada
    match_data = {
        'home_team': {'name': 'Real Madrid'},
        'away_team': {'name': 'Barcelona'},
        'league': 'La Liga',
        'date': '2026-01-15',
        'api_id': 533099  # ID real de um jogo Real Madrid vs Barcelona
    }
    
    print(f"\n[INPUT] Dados de entrada:")
    print(f"   Home: {match_data['home_team']['name']}")
    print(f"   Away: {match_data['away_team']['name']}")
    print(f"   API ID: {match_data['api_id']}")
    
    # 1. Testar enriquecimento
    print(f"\n{'='*80}")
    print("[STEP 1] TESTANDO ENRIQUECIMENTO (match_enricher.enrich)")
    print("="*80)
    
    try:
        enricher = MatchDataEnricher()
        enriched_data = enricher.enrich(match_data)
        
        print(f"\n[OK] Enriquecimento concluido!")
        print(f"   Campos retornados: {list(enriched_data.keys())}")
        
        # Verificar se 'odds' está presente
        if 'odds' in enriched_data:
            odds = enriched_data['odds']
            print(f"\n[ODDS] ODDSENCONTRADAS:")
            if odds:
                print(f"   Home Win: {odds.get('home_win')}")
                print(f"   Draw: {odds.get('draw')}")
                print(f"   Away Win: {odds.get('away_win')}")
                print(f"   Over 2.5: {odds.get('over_25')}")
                print(f"   BTTS Yes: {odds.get('btts_yes')}")
            else:
                print(f"   [WARN] ODDS RETORNOU NONE/VAZIO")
                print(f"   Tipo: {type(odds)}")
                print(f"   Valor: {repr(odds)}")
        else:
            print(f"\n[ERROR] ODDS NAO ESTA NA CHAVE DE ENRICHED_DATA")
        
    except Exception as e:
        print(f"\n[ERROR] Erro durante enriquecimento: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # 2. Testar se raw_odds pode ser extraído
    print(f"\n{'='*80}")
    print("[STEP 2] TESTANDO EXTRACAO DE RAW_ODDS")
    print("="*80)
    
    raw_odds = enriched_data.get('odds', {})
    print(f"   raw_odds = enriched_data.get('odds', {{}})")
    print(f"   Resultado tipo: {type(raw_odds)}")
    print(f"   Resultado: {repr(raw_odds)}")
    
    # 3. Verificar lógica de conversão
    print(f"\n{'='*80}")
    print("[STEP 3] TESTANDO LOGICA DE CONVERSAO PARA market_odds")
    print("="*80)
    
    market_odds = None
    
    if raw_odds and raw_odds.get('home_win'):
        market_odds = {
            'odds_home': raw_odds.get('home_win'),
            'odds_draw': raw_odds.get('draw'),
            'odds_away': raw_odds.get('away_win'),
            'odds_over_25': raw_odds.get('over_25'),
            'odds_under_25': raw_odds.get('under_25'),
            'odds_btts_yes': raw_odds.get('btts_yes'),
            'odds_btts_no': raw_odds.get('btts_no'),
        }
        print(f"[OK] Conversao bem-sucedida! market_odds criado:")
        print(f"   {json.dumps(market_odds, indent=2)}")
    else:
        print(f"[WARN] raw_odds vazio ou sem home_win")
        print(f"   Entraria no fallback com fair_odds")
    
    print(f"\n{'='*80}")
    print("[SUMMARY] RESUMO DO TESTE")
    print("="*80)
    print(f"1. Enriquecimento: [OK]")
    print(f"2. Odds na resposta: {'[OK]' if enriched_data.get('odds') else '[FAIL]'}")
    print(f"3. Odds tem dados: {'[OK]' if enriched_data.get('odds') and enriched_data['odds'].get('home_win') else '[FAIL]'}")
    print(f"4. Conversao seria bem-sucedida: {'[OK]' if market_odds else '[FAIL]'}")

if __name__ == '__main__':
    test_odds_flow()
