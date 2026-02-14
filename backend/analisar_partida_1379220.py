"""
Analise da partida 1379220
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.analysis.services.statistical_models import ModelEnsemble
from apps.analysis.services.decision_engine import DecisionEngine
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
    match_id = 1379220
    
    print("\n" + "="*80)
    print(f"ANALISANDO PARTIDA {match_id}")
    print("="*80 + "\n")
    
    # 1. Fetch dados básicos
    from apps.analysis.services.api_football_service import APIFootballService
    api = APIFootballService()
    fixture = api.fetch_fixture_details(match_id)
    
    if not fixture:
        print("Erro ao buscar partida")
        return
    
    # Extrair nomes dos times (API retorna home_team e away_team)
    home_team = fixture.get('home_team', {}).get('name', 'N/A')
    away_team = fixture.get('away_team', {}).get('name', 'N/A')
    league = fixture.get('league', {}).get('name', 'N/A')
    date = fixture.get('date', 'N/A')
    
    print(f"Partida: {home_team} vs {away_team}")
    print(f"Liga: {league}")
    print(f"Data: {date}")
    
    # 2. Enrich com api_id para buscar todos os dados
    enricher = MatchDataEnricher()
    match_data = {'api_id': match_id}  # Passar o ID para o enricher buscar tudo
    enriched = enricher.enrich(match_data)
    
    # 3. Features
    engineer = FeatureEngineer()
    features = engineer.engineer_all_features(enriched)
    
    # Mostrar features relevantes
    print("\n" + "-"*80)
    print("FEATURES PRINCIPAIS:")
    print("-"*80)
    
    strength = features.get('strength', {})
    print(f"\nFORCA:")
    print(f"  Casa xG: {strength.get('home_goals_per_game', 0):.2f}")
    print(f"  Fora xG: {strength.get('away_goals_per_game', 0):.2f}")
    print(f"  Diferencial: {strength.get('strength_differential', 0):+.2f}")
    print(f"  Casa Defesa: {strength.get('home_defense_strength', 0):.2f}")
    print(f"  Fora Defesa: {strength.get('away_defense_strength', 0):.2f}")
    
    motivation = features.get('motivation', {})
    print(f"\nMOTIVACAO:")
    print(f"  Casa: {motivation.get('home_motivation', 0):.1f}/10")
    print(f"  Fora: {motivation.get('away_motivation', 0):.1f}/10")
    print(f"  Diferencial: {motivation.get('motivation_differential', 0):+.1f}")
    
    context = features.get('context', {})
    print(f"\nCONTEXTO:")
    print(f"  Descanso Casa: {context.get('home_rest_days', 0)} dias")
    print(f"  Descanso Fora: {context.get('away_rest_days', 0)} dias")
    
    competition = features.get('competition', {})
    print(f"\nCOMPETICAO:")
    print(f"  E Copa: {competition.get('is_cup_competition', False)}")
    print(f"  E Knockout: {competition.get('is_knockout', False)}")
    print(f"  Nome: {competition.get('competition_name', 'N/A')}")
    
    form = features.get('form', {})
    print(f"\nFORMA:")
    print(f"  Casa (ultimos 5): {form.get('home_last_5_form', 0):.2f}")
    print(f"  Fora (ultimos 5): {form.get('away_last_5_form', 0):.2f}")
    print(f"  Casa (ajustada): {form.get('home_adjusted_form', 0):.2f}")
    print(f"  Fora (ajustada): {form.get('away_adjusted_form', 0):.2f}")
    
    market = features.get('market', {})
    print(f"\nMERCADO:")
    print(f"  Odds Casa: {market.get('odds_home', 0):.2f}")
    print(f"  Odds Empate: {market.get('odds_draw', 0):.2f}")
    print(f"  Odds Fora: {market.get('odds_away', 0):.2f}")
    print(f"  Prob Casa (implied): {market.get('market_home_prob', 0):.1%}")
    print(f"  Prob Empate (implied): {market.get('market_draw_prob', 0):.1%}")
    print(f"  Prob Fora (implied): {market.get('market_away_prob', 0):.1%}")
    print(f"  Margem Bookmaker: {market.get('bookmaker_margin', 0):.1%}")
    
    # 4. ContextAnalyzer
    print("\n" + "="*80)
    print("CONTEXT ANALYZER")
    print("="*80 + "\n")
    
    analyzer = ContextAnalyzer()
    context_result = analyzer.analyze(features)
    
    patterns = context_result.get('patterns', [])
    if patterns:
        print(f"{len(patterns)} PADRAO(ES) DETECTADO(S):\n")
        for i, p in enumerate(patterns, 1):
            print(f"{i}. {p['name'].upper()}")
            print(f"   Confianca: {p['confidence']:.0%}")
            print(f"   Mercados: {', '.join(p['favorable_markets'][:5])}")
            print(f"   Razao: {p['reasoning']}")
            print()
    else:
        print("Nenhum padrao detectado\n")
    
    # Top mercados
    top_markets = context_result.get('top_markets', [])
    if top_markets:
        print("TOP 10 MERCADOS POR CONTEXTO:")
        for m in top_markets[:10]:
            patterns_str = ', '.join(m['supporting_patterns'])
            print(f"  {m['market']:20s}: {m['context_score']:>3.0%} (por: {patterns_str})")
    
    # 5. Modelos estatisticos
    print("\n" + "="*80)
    print("MODELOS ESTATISTICOS")
    print("="*80 + "\n")
    
    strength = features.get('strength', {})
    home_strength = strength.get('home_goals_per_game', 1.5)
    away_strength = strength.get('away_goals_per_game', 1.5)
    home_defense = strength.get('home_defense_strength', 1.0)
    away_defense = strength.get('away_defense_strength', 1.0)
    
    weather = features.get('weather', {})
    weather_impact = weather.get('weather_impact', 0.0)
    
    league_id = features.get('competition', {}).get('league_id')
    
    ensemble = ModelEnsemble()
    predictions = ensemble.predict(
        features, 
        home_strength, 
        away_strength, 
        weather_impact=weather_impact,
        league_id=league_id,
        home_defense=home_defense,
        away_defense=away_defense
    )
    
    consensus = predictions.get('consensus', {})
    poisson = predictions.get('poisson', {})
    logistic = predictions.get('logistic', {})
    market = predictions.get('market_prior', {})
    
    print("CONSENSUS (Ensemble):")
    print(f"  Casa:   {consensus.get('home_win', 0):.1%}")
    print(f"  Empate: {consensus.get('draw', 0):.1%}")
    print(f"  Fora:   {consensus.get('away_win', 0):.1%}")
    
    print("\nPOISSON (Puro):")
    poisson_probs = poisson.get('probabilities', {})
    print(f"  Casa:   {poisson_probs.get('home_win', 0):.1%}")
    print(f"  Empate: {poisson_probs.get('draw', 0):.1%}")
    print(f"  Fora:   {poisson_probs.get('away_win', 0):.1%}")
    
    print("\nLOGISTIC (Contexto):")
    print(f"  Casa:   {logistic.get('home_win', 0):.1%}")
    print(f"  Empate: {logistic.get('draw', 0):.1%}")
    print(f"  Fora:   {logistic.get('away_win', 0):.1%}")
    
    print("\nMARKET (Bookmakers):")
    print(f"  Casa:   {market.get('home_win', 0):.1%}")
    print(f"  Empate: {market.get('draw', 0):.1%}")
    print(f"  Fora:   {market.get('away_win', 0):.1%}")
    
    # 6. Decision Engine
    print("\n" + "="*80)
    print("RECOMENDACOES")
    print("="*80 + "\n")
    
    decision = DecisionEngine()
    decision_output = decision.make_decision(
        model_predictions=predictions,
        features=features,
        market_odds=enriched.get('odds', {}),
        strategy='multiple',
        context_analysis=context_result
    )

    top_bets = decision_output.get('top_bets', [])
    if top_bets:
        for i, rec in enumerate(top_bets[:3], 1):
            print(f"{i}. {rec['market_display'].upper()} - {rec['pick']}")
            print(f"   Probabilidade: {rec['probability']:.1%}")
            print(f"   Odd: {rec.get('market_odd', 0):.2f}")
            print(f"   EV: {rec.get('ev_pct', 0):+.1f}%")
            print(f"   Stake: {rec.get('stake_units', 0)}u")
            print(f"   Razao: {rec.get('reason', 'N/A')}")
            print()
    else:
        print("Nenhuma aposta recomendada")
    
    print("\n" + "="*80)
    print("ANALISE CONCLUIDA")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
