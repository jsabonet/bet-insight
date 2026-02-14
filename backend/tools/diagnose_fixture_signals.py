import os
import sys
from datetime import datetime
from pathlib import Path

# Ensure backend path
BACKEND_ROOT = str(Path(__file__).resolve().parents[1])
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.statistical_models import ModelEnsemble


def summarize_signals(enriched, features):
    print("=== SIGNALS SUMMARY ===")
    # Standings
    table = enriched.get('table_context') or {}
    home_tab = table.get('home') or {}
    away_tab = table.get('away') or {}
    print(f"Standings: home pos={home_tab.get('position')} pts={home_tab.get('points')} | away pos={away_tab.get('position')} pts={away_tab.get('points')}")
    print(f"Home record={home_tab.get('home_record')} | Away away_record={away_tab.get('away_record')}")

    # Rest
    rest = enriched.get('rest_context') or {}
    print(f"Rest: home_days={rest.get('home_days_rest')} away_days={rest.get('away_days_rest')} advantage={rest.get('advantage')}")

    # Injuries
    injuries = enriched.get('injuries') or {}
    print(f"Injuries: home={len(injuries.get('home', []))} away={len(injuries.get('away', []))}")

    # Odds
    odds = enriched.get('odds') or {}
    print(f"Odds: H={odds.get('home_win')} D={odds.get('draw')} A={odds.get('away_win')} over2.5={odds.get('over_25')} btts={odds.get('btts_yes')}")

    # Strength & form features
    strength = features.get('strength', {})
    form = features.get('form', {})
    print(f"Strength: home_attack={strength.get('home_attack_strength')} away_attack={strength.get('away_attack_strength')} diff={strength.get('strength_differential')}")
    print(f"Form: home_adj={form.get('home_adjusted_form')} away_adj={form.get('away_adjusted_form')} diff={form.get('adjusted_form_diff')}")

    # Weather
    weather = features.get('weather', {})
    print(f"Weather: impact={weather.get('goal_impact')} severity={weather.get('weather_severity')}")

    # H2H
    h2h = enriched.get('h2h') or []
    print(f"H2H: {len(h2h)} matches")


def main():
    fixture_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1387895
    enricher = MatchDataEnricher()
    enriched = enricher.enrich({'api_id': fixture_id})
    engineer = FeatureEngineer()
    features = engineer.engineer_all_features(enriched)
    summarize_signals(enriched, features)

    home_stats = enriched.get('home_stats', {})
    away_stats = enriched.get('away_stats', {})
    home_strength = float(home_stats.get('goals_per_game_avg', 1.5))
    away_strength = float(away_stats.get('goals_per_game_avg', 1.3))
    home_defense = float(home_stats.get('goals_conceded_avg', 1.3))
    away_defense = float(away_stats.get('goals_conceded_avg', 1.3))
    league_id = enriched.get('fixture_details', {}).get('league', {}).get('id')
    weather_impact = features.get('weather', {}).get('goal_impact', 0.0)

    ensemble = ModelEnsemble()
    preds = ensemble.predict(features, home_strength, away_strength, weather_impact, league_id, home_defense, away_defense)
    cons = preds.get('consensus', {})
    print("Consensus probs:", {k: round(v*100,1) for k,v in cons.items()})


if __name__ == '__main__':
    main()
