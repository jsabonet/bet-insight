import os
import sys
from pathlib import Path

BACKEND_ROOT = str(Path(__file__).resolve().parents[1])
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.statistical_models import ModelEnsemble
from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.analysis.services.decision_engine import DecisionEngine


def main():
    fixture_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1387895
    enricher = MatchDataEnricher()
    enriched = enricher.enrich({'api_id': fixture_id})

    engineer = FeatureEngineer()
    features = engineer.engineer_all_features(enriched)

    ensemble = ModelEnsemble()
    home_stats = enriched.get('home_stats', {})
    away_stats = enriched.get('away_stats', {})
    home_strength = float(home_stats.get('goals_per_game_avg', 1.5))
    away_strength = float(away_stats.get('goals_per_game_avg', 1.3))
    home_defense = float(home_stats.get('conceded_per_game_avg', 1.3))
    away_defense = float(away_stats.get('conceded_per_game_avg', 1.3))
    league_id = enriched.get('fixture_details', {}).get('league', {}).get('id')
    weather_impact = features.get('weather', {}).get('goal_impact', 0.0)

    preds = ensemble.predict(features, home_strength, away_strength, weather_impact, league_id, home_defense, away_defense)

    analyzer = ContextAnalyzer()
    context = analyzer.analyze(features)

    decision = DecisionEngine().make_decision(
        preds,
        features,
        enriched.get('odds') or {},
        strategy='value',
        context_analysis=context
    )

    print("\n" + "="*80)
    print("=== RECOMENDAÇÃO PRINCIPAL ===")
    rec = decision.get('recommendation', {})
    print(f"Market: {rec.get('market')} ({rec.get('market_display', 'N/A')})")
    print(f"Pick: {rec.get('pick')}")
    print(f"Probabilidade: {rec.get('probability', 0)*100:.1f}%")
    print(f"Odd: {rec.get('odd', 0)}")
    print(f"Razão: {rec.get('reason_pt', rec.get('reason', 'N/A'))}")
    
    # Mostrar se houve override contextual
    source = decision.get('recommendation_source')
    if source:
        print(f"FONTE: {source.upper()} (override contextual ativado!)")
    else:
        print(f"FONTE: MODEL (padrao)")
    
    print("\n" + "="*80)
    print("=== TOP BETS (CONTEXT) ===")
    for b in decision.get('top_bets', []):
        print(f"#{b['rank']} {b['market_display']} - Prob {b['probability']*100:.1f}% | Odd {b['market_odd']} | EV {b['ev_pct']:+.1f}% | Score {b.get('score', b.get('final_score', 0)):.3f}")
        print(f"   Reason: {b['reason']}")
    
    print("\n" + "="*80)
    print("=== FILTRO DE PUBLICAÇÃO ===")
    pub = decision.get('publish_filter', {})
    print(f"Should Publish: {pub.get('should_publish')}")
    print(f"Max Prob: {pub.get('max_probability', 0)*100:.1f}%")
    print(f"Confidence: {pub.get('confidence_score', 0):.2f}")
    print(f"Razão: {pub.get('reason')}")
    print("="*80)


if __name__ == '__main__':
    main()
