"""
Análise da partida 1520391 baseada nas probabilidades do mercado
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.statistical_models import ModelEnsemble
from apps.analysis.services.decision_engine import DecisionEngine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    fixture_id = 1520391
    
    print("\n" + "="*100)
    print(f"ANALISE DA PARTIDA {fixture_id} - BASEADA EM PROBABILIDADES DO MERCADO")
    print("="*100 + "\n")
    
    # 1. Buscar dados da partida da API
    print("Buscando dados da API-Football...")
    api_service = FootballAPIService()
    result = api_service.get_fixture_by_id(fixture_id)
    
    if not result.get('success'):
        print(f"ERRO ao buscar partida: {result.get('error')}")
        return
    
    fixture = result['fixture']
    
    # Extrair informações básicas
    home_team = fixture['teams']['home']['name']
    away_team = fixture['teams']['away']['name']
    league = fixture['league']['name']
    match_date = fixture['fixture']['date']
    
    print(f"Partida: {home_team} vs {away_team}")
    print(f"Liga: {league}")
    print(f"Data: {match_date}")
    print()
    
    # 2. Enriquecer dados
    print("Enriquecendo dados da partida...")
    match_data = {
        'home_team': {'name': home_team},
        'away_team': {'name': away_team},
        'league': league,
        'date': match_date,
        'api_id': fixture_id,
        'fixture_details': fixture
    }
    
    enricher = MatchDataEnricher()
    match_data = enricher.enrich(match_data)
    
    # 3. Verificar se temos odds do mercado
    market_odds_raw = match_data.get('odds')
    
    if not market_odds_raw or not market_odds_raw.get('home_win'):
        print("AVISO: Sem odds do mercado disponíveis")
        market_odds = None
    else:
        market_odds = {
            'home': market_odds_raw.get('home_win'),
            'draw': market_odds_raw.get('draw'),
            'away': market_odds_raw.get('away_win'),
            'over_2_5': market_odds_raw.get('over_25'),
            'under_2_5': market_odds_raw.get('under_25'),
            'btts_yes': market_odds_raw.get('btts_yes'),
            'btts_no': market_odds_raw.get('btts_no'),
        }
        print("Odds do mercado encontradas:")
        print(f"   Casa: {market_odds['home']}")
        print(f"   Empate: {market_odds['draw']}")
        print(f"   Fora: {market_odds['away']}")
        print()
    
    # 4. Calcular probabilidades do mercado (Market Prior)
    if market_odds:
        home_odd = market_odds['home']
        draw_odd = market_odds['draw']
        away_odd = market_odds['away']
        
        # Converter odds para probabilidades implícitas
        prob_home = 1 / home_odd
        prob_draw = 1 / draw_odd
        prob_away = 1 / away_odd
        
        # Remover margem do bookmaker (normalizar)
        total = prob_home + prob_draw + prob_away
        
        market_probabilities = {
            'home_win': prob_home / total,
            'draw': prob_draw / total,
            'away_win': prob_away / total
        }
        
        print("PROBABILIDADES DO MERCADO (Bookmakers):")
        print(f"   Casa: {market_probabilities['home_win']*100:.1f}%")
        print(f"   Empate: {market_probabilities['draw']*100:.1f}%")
        print(f"   Fora: {market_probabilities['away_win']*100:.1f}%")
        print(f"   (Margem removida: {(total-1)*100:.1f}%)")
        print()
    
    # 5. Executar análise completa
    print("Executando feature engineering...")
    engineer = FeatureEngineer()
    features = engineer.engineer_all_features(match_data)
    
    # Extrair força dos times
    home_stats = match_data.get('home_stats', {})
    away_stats = match_data.get('away_stats', {})
    
    home_strength = home_stats.get('goals_per_game_avg', 1.5)
    away_strength = away_stats.get('goals_per_game_avg', 1.3)
    home_defense = home_stats.get('conceded_per_game_avg', 1.3)
    away_defense = away_stats.get('conceded_per_game_avg', 1.3)
    
    weather_impact = features.get('weather', {}).get('goal_impact', 0.0)
    
    print("Executando modelos estatisticos...")
    ensemble = ModelEnsemble()
    model_predictions = ensemble.predict(
        features, 
        home_strength, 
        away_strength, 
        weather_impact,
        league_id=match_data.get('fixture', {}).get('league_id'),
        home_defense=home_defense, 
        away_defense=away_defense
    )
    
    # 6. Decision Engine
    print("Executando Decision Engine...")
    decision_engine = DecisionEngine()
    decision_data = decision_engine.make_decision(
        model_predictions,
        features,
        market_odds,
        strategy='value'
    )
    
    # 7. Exibir resultados
    print("\n" + "="*100)
    print("RESULTADOS DA ANALISE")
    print("="*100 + "\n")
    
    # Probabilidades dos modelos
    print("PROBABILIDADES DOS MODELOS ESTATISTICOS:")
    consensus = model_predictions['consensus']
    print(f"   Casa: {consensus['home_win']*100:.1f}%")
    print(f"   Empate: {consensus['draw']*100:.1f}%")
    print(f"   Fora: {consensus['away_win']*100:.1f}%")
    print()
    
    # Probabilidades do mercado (se disponíveis)
    if market_odds:
        print("PROBABILIDADES DO MERCADO:")
        print(f"   Casa: {market_probabilities['home_win']*100:.1f}%")
        print(f"   Empate: {market_probabilities['draw']*100:.1f}%")
        print(f"   Fora: {market_probabilities['away_win']*100:.1f}%")
        print()
        
        # Comparação
        print("COMPARACAO (Modelos vs Mercado):")
        diff_home = (consensus['home_win'] - market_probabilities['home_win']) * 100
        diff_draw = (consensus['draw'] - market_probabilities['draw']) * 100
        diff_away = (consensus['away_win'] - market_probabilities['away_win']) * 100
        
        print(f"   Casa: {diff_home:+.1f}% {'(modelos mais otimistas)' if diff_home > 0 else '(mercado mais otimista)'}")
        print(f"   Empate: {diff_draw:+.1f}%")
        print(f"   Fora: {diff_away:+.1f}% {'(modelos mais otimistas)' if diff_away > 0 else '(mercado mais otimista)'}")
        print()
    
    # Recomendação
    print("RECOMENDACAO:")
    recommendation = decision_data['recommendation']
    print(f"   Aposta: {recommendation['pick']}")
    print(f"   Confianca: {decision_data['confidence']['stars']}/5 ({decision_data['confidence']['level']})")
    print(f"   Risco: {decision_data.get('risk', 'medium').upper()}")
    print()
    
    # Value Bets
    if decision_data.get('value_bets'):
        print("VALUE BETS (Apostas com Valor):")
        for bet in decision_data['value_bets']:
            # Determinar o pick baseado no nome do mercado
            display_name = bet.get('display_name', bet.get('market', 'N/A'))
            market_type = bet.get('market_type', 'N/A')
            
            print(f"   - {display_name} ({market_type})")
            print(f"     Probabilidade: {bet.get('probability', 0)*100:.1f}%")
            print(f"     Fair Odd: {bet.get('fair_odd', 0):.2f} | Market Odd: {bet.get('market_odd', 'N/A')}")
            print(f"     EV: {bet.get('expected_value', 0):.1f}% | Stake: {bet.get('suggested_stake', 'N/A')}u")
            print(f"     Razao: {bet.get('reasoning', 'N/A')}")
            print()
    else:
        print("Nenhuma value bet identificada")
        print()
    
    # Fatores-chave
    print("FATORES-CHAVE:")
    for factor in decision_data.get('key_factors', []):
        print(f"   - {factor}")
    
    print("\n" + "="*100)
    print("ANALISE COMPLETA")
    print("="*100 + "\n")

if __name__ == '__main__':
    main()
