#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TESTE FINAL: Validar que market_odds está sendo retornado corretamente
e que o frontend consegue acessar e exibir os dados
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/d/Projectos/Football/bet-insight/backend')

django.setup()

import json
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.statistical_models import ModelEnsemble
from apps.analysis.services.decision_engine import DecisionEngine

def test_final():
    """Teste final completo"""
    
    print("\n" + "="*80)
    print("TESTE FINAL: Market Odds Pipeline - Backend até Frontend")
    print("="*80)
    
    # Dados de entrada
    match_data = {
        'home_team': {'name': 'Real Madrid'},
        'away_team': {'name': 'Barcelona'},
        'league': 'La Liga',
        'date': '2026-01-15',
        'api_id': 533099
    }
    
    # 1. Enriquecimento
    print("\n[1/5] Enriquecimento...")
    enricher = MatchDataEnricher()
    match_data = enricher.enrich(match_data)
    
    raw_odds = match_data.get('odds') or {}
    print(f"      raw_odds tipo: {type(raw_odds).__name__}")
    print(f"      raw_odds vazio: {not raw_odds}")
    
    # 2. Features
    print("\n[2/5] Feature Engineering...")
    engineer = FeatureEngineer()
    features = engineer.engineer_all_features(match_data)
    
    # 3. Modelos
    print("\n[3/5] Modelos Estatísticos...")
    home_stats = match_data.get('home_stats', {})
    away_stats = match_data.get('away_stats', {})
    home_strength = home_stats.get('goals_per_game_avg', 1.5)
    away_strength = away_stats.get('goals_per_game_avg', 1.3)
    weather_impact = features.get('weather', {}).get('goal_impact', 0.0)
    
    ensemble = ModelEnsemble()
    model_predictions = ensemble.predict(features, home_strength, away_strength, weather_impact)
    
    # 4. Decision Engine
    print("\n[4/5] Decision Engine...")
    decision_engine = DecisionEngine()
    decision_data_temp = decision_engine.make_decision(
        model_predictions,
        features,
        {}
    )
    
    # 5. Conversão de Odds (como em views.py)
    print("\n[5/5] Conversão para Market Odds...")
    
    if raw_odds.get('home_win'):
        market_odds = {
            'odds_home': raw_odds.get('home_win'),
            'odds_draw': raw_odds.get('draw'),
            'odds_away': raw_odds.get('away_win'),
        }
        print(f"      [OK] Market odds da API")
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
            print(f"      [OK] Market odds com fallback (fair_odds + 5%)")
        else:
            market_odds = None
            print(f"      [ERROR] Nao foi possivel gerar market_odds")
    
    # Montar resposta como views.py
    print("\n" + "="*80)
    print("RESPOSTA HTTP (JSON para Frontend)")
    print("="*80 + "\n")
    
    response = {
        'analysis_data': {
            'consensus': model_predictions['consensus'],
            'poisson': model_predictions.get('poisson', {}),
            'fair_odds': decision_data_temp.get('fair_odds', {}),
            'market_odds': market_odds,
            'confidence': decision_data_temp.get('confidence', {}),
        }
    }
    
    print(json.dumps(response['analysis_data'], indent=2, default=str))
    
    # VALIDAÇÃO: Simular acesso do frontend
    print("\n" + "="*80)
    print("VALIDAÇÃO: Frontend consegue acessar os dados?")
    print("="*80 + "\n")
    
    analysis_data = response['analysis_data']
    
    # Simular mapKeyToOddKey do frontend
    def mapKeyToOddKey(key):
        mapping = {
            'home_win': 'odds_home',
            'draw': 'odds_draw',
            'away_win': 'odds_away',
            'over_2_5': 'odds_over_25',
            'btts_yes': 'odds_btts_yes',
        }
        return mapping.get(key, f'odds_{key}')
    
    def calcImpliedProb(odd):
        return (1 / odd * 100) if odd > 0 else 0
    
    # Testes de acesso
    tests = [
        ('home_win', 'Vitória Casa'),
        ('draw', 'Empate'),
        ('away_win', 'Vitória Fora'),
        ('over_2_5', 'Over 2.5'),
        ('btts_yes', 'Ambas Marcam'),
    ]
    
    all_ok = True
    for key, label in tests:
        fair_odd = analysis_data.get('fair_odds', {}).get(key)
        oddKey = mapKeyToOddKey(key)
        market_odd = analysis_data.get('market_odds', {}).get(oddKey)
        
        if market_odd:
            implied_prob = calcImpliedProb(market_odd)
            status = "[OK]"
        else:
            implied_prob = None
            status = "[FAIL]"
            if key in ('home_win', 'draw', 'away_win'):
                all_ok = False
        
        print(f"{status} {label}")
        if market_odd:
            print(f"    - Odd Mercado: {market_odd}")
            print(f"    - Prob. Implicita: {implied_prob:.1f}%")
        else:
            print(f"    - Dados nao disponíveis")
        print()
    
    print("="*80)
    if all_ok:
        print("[OK] SUCESSO: Frontend consegue exibir 'Odd Mercado' e 'Prob. Implicita'")
    else:
        print("[FAIL] FALHA: Alguns dados estao faltando")
    print("="*80 + "\n")

if __name__ == '__main__':
    test_final()
