#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar exatamente o que está sendo retornado pela API
e se market_odds está sendo incluído corretamente na resposta
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/d/Projectos/Football/bet-insight/backend')

django.setup()

import json
import logging
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.statistical_models import ModelEnsemble
from apps.analysis.services.decision_engine import DecisionEngine

logging.basicConfig(level=logging.WARNING)

def test_response_structure():
    """Testa a estrutura exata da resposta"""
    
    print("\n" + "="*80)
    print("[TESTE] ESTRUTURA DA RESPOSTA PARA FRONTEND")
    print("="*80)
    
    match_data = {
        'home_team': {'name': 'Real Madrid'},
        'away_team': {'name': 'Barcelona'},
        'league': 'La Liga',
        'date': '2026-01-15',
        'api_id': 533099
    }
    
    # Simular o fluxo de quick_analyze
    enricher = MatchDataEnricher()
    match_data = enricher.enrich(match_data)
    
    engineer = FeatureEngineer()
    features = engineer.engineer_all_features(match_data)
    
    home_stats = match_data.get('home_stats', {})
    away_stats = match_data.get('away_stats', {})
    home_strength = home_stats.get('goals_per_game_avg', 1.5)
    away_strength = away_stats.get('goals_per_game_avg', 1.3)
    weather_impact = features.get('weather', {}).get('goal_impact', 0.0)
    
    ensemble = ModelEnsemble()
    model_predictions = ensemble.predict(features, home_strength, away_strength, weather_impact)
    
    decision_engine = DecisionEngine()
    decision_data_temp = decision_engine.make_decision(
        model_predictions,
        features,
        {}
    )
    
    # CONVERSAO DE ODDS (COMO EM VIEWS.PY)
    raw_odds = match_data.get('odds') or {}
    
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
    else:
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
        else:
            market_odds = None
    
    final_decision = decision_engine.make_decision(
        model_predictions,
        features,
        market_odds
    )
    
    # MONTAR RESPONSE COMO EM VIEWS.PY (linha 1020-1038)
    response_data = {
        'analysis_data': {
            'consensus': model_predictions['consensus'],
            'poisson': model_predictions.get('poisson', {}),
            'logistic': model_predictions.get('logistic', {}),
            'fair_odds': final_decision.get('fair_odds', {}),
            'market_odds': market_odds,  # ESTA AQUI?
            'value_bets': final_decision.get('value_bets', []),
            'recommendation': final_decision.get('recommendation', {}),
            'confidence': final_decision.get('confidence', {}),
            'risk': final_decision.get('risk', 'medium'),
        }
    }
    
    # Exibir a resposta
    print("\n[RESPOSTA] analysis_data keys:")
    print(f"  {list(response_data['analysis_data'].keys())}")
    
    print("\n[MARKET_ODDS] Valor completo:")
    print(json.dumps(response_data['analysis_data']['market_odds'], indent=2))
    
    print("\n[FAIR_ODDS] Valor completo:")
    print(json.dumps(response_data['analysis_data']['fair_odds'], indent=2))
    
    print("\n[CONSENSUS] Valor completo:")
    print(json.dumps(response_data['analysis_data']['consensus'], indent=2))
    
    # Verificar se frontend conseguiria acessar
    print("\n[DEBUG] Frontend conseguiria acessar:")
    analysis_data = response_data['analysis_data']
    print(f"  analysis_data.market_odds: {analysis_data.get('market_odds')}")
    print(f"  analysis_data.market_odds['odds_home']: {analysis_data.get('market_odds', {}).get('odds_home')}")
    print(f"  analysis_data.fair_odds: {analysis_data.get('fair_odds')}")
    print(f"  analysis_data.fair_odds['home_win']: {analysis_data.get('fair_odds', {}).get('home_win')}")

if __name__ == '__main__':
    test_response_structure()
