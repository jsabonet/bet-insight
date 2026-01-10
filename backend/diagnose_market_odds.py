#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostico: Verificar se market_odds está sendo retornado pela API
para um jogo real (Atletico Hidalgo vs Gavilanes FC)
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, '/d/Projectos/Football/bet-insight/backend')

django.setup()

import json
import logging
from apps.matches.models import Match
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.statistical_models import ModelEnsemble
from apps.analysis.services.decision_engine import DecisionEngine

logging.basicConfig(level=logging.WARNING)

def diagnose_market_odds():
    """Diagnostica se market_odds está sendo retornado"""
    
    print("\n" + "="*80)
    print("DIAGNOSTICO: Market Odds na API Real")
    print("="*80)
    
    # Procurar por um jogo real no banco de dados
    print("\n[STEP 1] Procurando por um jogo real no banco de dados...")
    
    matches = Match.objects.all()[:5]
    
    if not matches.exists():
        print("[ERROR] Nenhum jogo encontrado no banco de dados")
        return
    
    for match in matches:
        print(f"\n[FOUND] {match.home_team.name} vs {match.away_team.name}")
        print(f"        ID: {match.id}")
        print(f"        Data: {match.match_date}")
        print(f"        Liga: {match.league.name if match.league else 'N/A'}")
        
        # Tentar analisar este jogo
        try:
            print("\n[STEP 2] Enriquecendo dados da partida...")
            
            match_data = {
                'home_team': {'name': match.home_team.name},
                'away_team': {'name': match.away_team.name},
                'league': match.league.name if match.league else 'Unknown',
                'date': str(match.match_date),
                'api_id': match.api_id if hasattr(match, 'api_id') else None
            }
            
            print(f"        api_id: {match_data.get('api_id')}")
            
            # Só continuar se tiver api_id
            if not match_data.get('api_id'):
                print("[SKIP] Sem api_id, pulando para proximo jogo")
                continue
            
            enricher = MatchDataEnricher()
            match_data = enricher.enrich(match_data)
            
            print("[OK] Dados enriquecidos")
            
            # Verificar odds
            raw_odds = match_data.get('odds')
            print(f"\n[STEP 3] Verificando raw_odds...")
            print(f"        tipo: {type(raw_odds).__name__}")
            print(f"        vazio: {not raw_odds}")
            if raw_odds:
                print(f"        conteudo: {raw_odds}")
            
            # Continuar com features e modelos
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
            decision_data_temp = decision_engine.make_decision(model_predictions, features, {})
            
            # CONVERSAO DE ODDS
            print(f"\n[STEP 4] Convertendo odds para market_odds...")
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
                print(f"        [OK] Market odds da API")
                print(f"        {market_odds}")
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
                    print(f"        [OK] Market odds com fallback")
                    print(f"        {market_odds}")
                else:
                    market_odds = None
                    print(f"        [ERROR] Nao foi possivel gerar market_odds")
            
            # Montar resposta como views.py faria
            print(f"\n[STEP 5] Montando response para frontend...")
            
            response = {
                'analysis_data': {
                    'consensus': model_predictions.get('consensus'),
                    'poisson': model_predictions.get('poisson'),
                    'fair_odds': decision_data_temp.get('fair_odds'),
                    'market_odds': market_odds,
                    'recommendation': decision_data_temp.get('recommendation'),
                    'confidence': decision_data_temp.get('confidence'),
                    'risk': decision_data_temp.get('risk', 'medium'),
                }
            }
            
            # Verificar se market_odds está na resposta
            print(f"\n[STEP 6] Verificando resposta...")
            if response['analysis_data'].get('market_odds'):
                print(f"        [OK] market_odds presente na response")
                print(f"        market_odds: {response['analysis_data']['market_odds']}")
            else:
                print(f"        [ERROR] market_odds NAO presente na response")
                print(f"        Keys: {list(response['analysis_data'].keys())}")
            
            # Sucesso!
            print(f"\n[RESULTADO] Jogo analisado com sucesso!")
            print(f"             Frontend deveria receber market_odds corretamente")
            return
            
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n[ERROR] Nenhum jogo pude ser analisado com sucesso")

if __name__ == '__main__':
    diagnose_market_odds()
