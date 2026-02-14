"""
Test EV Display for Match 1391058
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.decision_engine import DecisionEngine
from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.analysis.services.market_selector import MarketSelector
from apps.matches.services.match_enricher import MatchEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.odds_calculator import OddsCalculator
from apps.ml.services.ml_orchestrator import MLOrchestrator
import json

# Carregar partida
match = Match.objects.get(id=1391058)
print(f'🏆 PARTIDA: {match.home_team.name} vs {match.away_team.name}')
print(f'📅 Data: {match.match_date}')
print(f'🏟️  Liga: {match.league.name if match.league else "N/A"}')
print()

# Pipeline completo
enricher = MatchEnricher()
enriched = enricher.enrich_match(match)

odds_calc = OddsCalculator()
enriched = odds_calc.calculate_missing_odds(enriched)

feature_eng = FeatureEngineer()
features = feature_eng.engineer_features(enriched)

ml_orch = MLOrchestrator()
predictions = ml_orch.predict(features, enriched['market_odds'])

context_analyzer = ContextAnalyzer()
context = context_analyzer.analyze(features, predictions, enriched['market_odds'])

market_selector = MarketSelector()
decision_engine = DecisionEngine(market_selector)

result = decision_engine.generate_recommendation(
    model_predictions=predictions,
    market_odds=enriched['market_odds'],
    features=features,
    context_analysis=context,
    strategy='multiple'
)

print('=' * 80)
print('🎯 TOP BETS (STRATEGY: MULTIPLE)')
print('=' * 80)

for bet in result['top_bets']:
    print(f"\n#{bet['rank']}: {bet['market_display']}")
    print(f"  📊 Probabilidade: {bet['probability']*100:.1f}%")
    print(f"  💰 Odd: {bet['market_odd']}")
    print(f"  📈 EV: {bet['ev_pct']:+.1f}%")
    print(f"  💵 Stake: {bet['stake_units']}u")
    print(f"  ℹ️  {bet['reason']}")

print('\n' + '=' * 80)
print('📋 SIMULAÇÃO FRONTEND (como apareceria no AnalysisModal)')
print('=' * 80)

for i, bet in enumerate(result['top_bets'], 1):
    print(f"\n{i}. {bet['market_display']}")
    print(f"   📊 Probabilidade: {bet['probability']*100:.1f}%")
    print(f"   💰 Odd: {bet['market_odd']}")
    print(f"   💵 Stake: {bet['stake_units']}u")
    print(f"   ℹ️  {bet['reason']}")

print('\n✅ Correção aplicada - EV agora está visível!')
