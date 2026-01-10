#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar o fluxo completo de estatísticas, passando por:
1. Enriquecimento
2. Feature engineering  
3. Modelos
4. Decision engine
5. Conversão de odds
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/d/Projectos/Football/bet-insight/backend')

django.setup()

import json
import logging
from datetime import datetime
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.statistical_models import ModelEnsemble
from apps.analysis.services.decision_engine import DecisionEngine

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('test')

def test_complete_flow():
    """Testa o fluxo completo"""
    
    print("\n" + "="*80)
    print("[TESTE] FLUXO COMPLETO DE ANALISE")
    print("="*80)
    
    # Dados de entrada
    match_data = {
        'home_team': {'name': 'Real Madrid'},
        'away_team': {'name': 'Barcelona'},
        'league': 'La Liga',
        'date': '2026-01-15',
        'api_id': 533099
    }
    
    print(f"\n[STEP 1] Enriquecimento...")
    try:
        enricher = MatchDataEnricher()
        match_data = enricher.enrich(match_data)
        print(f"[OK] Enriquecimento concluido")
        print(f"     odds tipo: {type(match_data.get('odds'))}")
        print(f"     odds valor: {match_data.get('odds')}")
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return
    
    # 2. Feature Engineering
    print(f"\n[STEP 2] Feature Engineering...")
    engineer = FeatureEngineer()
    features = engineer.engineer_all_features(match_data)
    print(f"[OK] {len(features)} features criadas")
    
    # 3. Modelos
    print(f"\n[STEP 3] Modelos Estatisticos...")
    home_stats = match_data.get('home_stats', {})
    away_stats = match_data.get('away_stats', {})
    home_strength = home_stats.get('goals_per_game_avg', 1.5)
    away_strength = away_stats.get('goals_per_game_avg', 1.3)
    weather_impact = features.get('weather', {}).get('goal_impact', 0.0)
    
    ensemble = ModelEnsemble()
    model_predictions = ensemble.predict(features, home_strength, away_strength, weather_impact)
    print(f"[OK] Predicoes: Home {model_predictions.get('probabilities', {}).get('home', 0):.2%}")
    
    # 4. Decision Engine (temp)
    print(f"\n[STEP 4] Decision Engine (temporario)...")
    decision_engine = DecisionEngine()
    decision_data_temp = decision_engine.make_decision(
        model_predictions,
        features,
        {}
    )
    print(f"[OK] Fair odds: {decision_data_temp.get('fair_odds')}")
    
    # 5. CONVERSAO DE ODDS (PARTE CRITICA)
    print(f"\n[STEP 5] CONVERSAO DE ODDS...")
    raw_odds = match_data.get('odds') or {}
    logger.info(f"raw_odds tipo: {type(raw_odds)}, vazio: {not raw_odds}")
    
    market_odds = None
    
    if raw_odds.get('home_win'):
        market_odds = {
            'odds_home': raw_odds.get('home_win'),
            'odds_draw': raw_odds.get('draw'),
            'odds_away': raw_odds.get('away_win'),
            'odds_over_25': raw_odds.get('over_25'),
            'odds_under_25': raw_odds.get('under_25'),
            'odds_btts_yes': raw_odds.get('btts_yes'),
            'odds_btts_no': raw_odds.get('btts_no'),
        }
        print(f"[OK] Market odds da API: {market_odds}")
    else:
        # Fallback
        fair_odds_data = decision_data_temp.get('fair_odds', {})
        if fair_odds_data and fair_odds_data.get('home_win'):
            bookmaker_margin = 1.05
            market_odds = {
                'odds_home': round(fair_odds_data['home_win'] / bookmaker_margin, 2),
                'odds_draw': round(fair_odds_data.get('draw', 3.4) / bookmaker_margin, 2),
                'odds_away': round(fair_odds_data.get('away_win', 3.0) / bookmaker_margin, 2),
                'odds_over_25': round(fair_odds_data.get('over_2_5', 2.0) / bookmaker_margin, 2),
                'odds_btts_yes': round(fair_odds_data.get('btts', 2.0) / bookmaker_margin, 2),
            }
            print(f"[OK] Market odds fallback (fair_odds + 5% margin): {market_odds}")
        else:
            print(f"[WARN] Nao foi possivel gerar market_odds")
    
    # 6. Decision Engine FINAL
    print(f"\n[STEP 6] Decision Engine FINAL...")
    final_decision = decision_engine.make_decision(
        model_predictions,
        features,
        market_odds
    )
    print(f"[OK] Analise concluida")
    
    # 7. Resumo final
    print(f"\n" + "="*80)
    print("[RESUMO FINAL]")
    print("="*80)
    print(f"Market Odds: {market_odds}")
    print(f"Recommendation: {final_decision.get('recommendation')}")
    print(f"Confidence: {final_decision.get('confidence')}")

if __name__ == '__main__':
    test_complete_flow()
