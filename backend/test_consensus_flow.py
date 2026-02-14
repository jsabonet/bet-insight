"""
Teste do fluxo completo: External Match Analysis
Simula o que o frontend faz ao analisar match 1520391
"""
import os
import django
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import logging
logging.basicConfig(level=logging.INFO)

def test_external_match_analysis():
    """Simula análise de match externo (API ID 1520391)"""
    
    from apps.matches.services.football_api import FootballAPIService
    from apps.analysis.services.match_enricher import MatchDataEnricher
    from apps.analysis.services.feature_engineer import FeatureEngineer
    from apps.analysis.services.statistical_models import ModelEnsemble
    from apps.analysis.services.decision_engine import DecisionEngine
    
    api_id = 1520391
    strategy = 'value'
    
    print("\n" + "="*100)
    print(f"TESTE ANÁLISE MATCH EXTERNO: {api_id}")
    print("="*100 + "\n")
    
    # 1. Buscar via API    print("1. Buscando dados da API...")
    api_service = FootballAPIService()
    result = api_service.get_fixture_by_id(api_id)
    
    if not result.get('success'):
        print(f"ERRO: {result.get('error')}")
        return
    
    fixture = result['fixture']
    match_data = {
        'home_team': {'name': fixture['teams']['home']['name']},
        'away_team': {'name': fixture['teams']['away']['name']},
        'league': fixture['league']['name'],
        'date': fixture['fixture']['date'],
        'api_id': api_id,
        'fixture': fixture
    }
    
    print(f"   Partida: {match_data['home_team']['name']} vs {match_data['away_team']['name']}")
    
    # 2. Enriquecer dados
    print("\n2. Enriquecendo dados...")
    enricher = MatchDataEnricher()
    match_data = enricher.enrich(match_data)
    
    print(f"   Odds disponíveis: {match_data.get('odds', {}).get('home_win', 'N/A')}")
    
    # 3. Feature Engineering
    print("\n3. Feature Engineering...")
    engineer = FeatureEngineer()
    features = engineer.engineer_all_features(match_data)
    
    # 4. ModelEnsemble
    print("\n4. ModelEnsemble...")
    home_strength = match_data.get('home_stats', {}).get('goals_per_game_avg', 1.5)
    away_strength = match_data.get('away_stats', {}).get('goals_per_game_avg', 1.3)
    home_defense = match_data.get('home_stats', {}).get('conceded_per_game_avg', 1.3)
    away_defense = match_data.get('away_stats', {}).get('conceded_per_game_avg', 1.3)
    
    ensemble = ModelEnsemble()
    model_predictions = ensemble.predict(
        features,
        home_strength,
        away_strength,
        0.0,  # weather_impact
        league_id=143,  # Copa del Rey
        home_defense=home_defense,
        away_defense=away_defense
    )
    
    print("\n" + "="*100)
    print("RESULTADO MODEL_PREDICTIONS:")
    print("="*100)
    print(f"Keys: {list(model_predictions.keys())}")
    
    consensus = model_predictions.get('consensus', {})
    market_prior = model_predictions.get('market_prior', {})
    
    print(f"\nCONSENSUS (Modelos ML):")
    print(f"   Casa: {consensus.get('home_win', 0) * 100:.1f}%")
    print(f"   Empate: {consensus.get('draw', 0) * 100:.1f}%")
    print(f"   Fora: {consensus.get('away_win', 0) * 100:.1f}%")
    
    if market_prior:
        print(f"\nMARKET_PRIOR (Bookmakers):")
        print(f"   Casa: {market_prior.get('home_win', 0) * 100:.1f}%")
        print(f"   Empate: {market_prior.get('draw', 0) * 100:.1f}%")
        print(f"   Fora: {market_prior.get('away_win', 0) * 100:.1f}%")
    
    # 5. Simular mapeamento do backend para frontend
    print("\n" + "="*100)
    print("SIMULAÇÃO MAPEAMENTO BACKEND → FRONTEND:")
    print("="*100)
    
    # Como seria mapeado (linha 2334 de views.py)
    analysis_result = {
        'analysis_data': {
            'model_predictions': model_predictions
        }
    }
    
    # Path usado: analysis_result['analysis_data']['model_predictions']['consensus']
    consensus_frontend = analysis_result.get('analysis_data', {}).get('model_predictions', {}).get('consensus', {})
    
    print(f"\nCampo 'consensus' enviado ao frontend:")
    print(f"   Casa: {consensus_frontend.get('home_win', 0) * 100:.1f}%")
    print(f"   Empate: {consensus_frontend.get('draw', 0) * 100:.1f}%")
    print(f"   Fora: {consensus_frontend.get('away_win', 0) * 100:.1f}%")
    
    # Verificar se está correto
    print(f"\n✅ VERIFICAÇÃO:")
    if abs(consensus_frontend.get('home_win', 0) - consensus.get('home_win', 0)) < 0.01:
        print(f"   ✓ Consensus está sendo mapeado CORRETAMENTE")
    else:
        print(f"   ✗ ERRO: Consensus NÃO está sendo mapeado corretamente!")
        print(f"   Esperado: {consensus.get('home_win', 0)}")
        print(f"   Recebido: {consensus_frontend.get('home_win', 0)}")
    
    print("\n" + "="*100)

if __name__ == '__main__':
    test_external_match_analysis()
