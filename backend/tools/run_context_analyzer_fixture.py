import os
import sys
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
from apps.analysis.services.context_analyzer import ContextAnalyzer


def main():
    fixture_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1387895
    enricher = MatchDataEnricher()
    enriched = enricher.enrich({'api_id': fixture_id})
    engineer = FeatureEngineer()
    features = engineer.engineer_all_features(enriched)

    analyzer = ContextAnalyzer()
    result = analyzer.analyze(features)

    print("=== CONTEXT ANALYZER OUTPUT ===")
    patterns = result.get('patterns', [])
    if not patterns:
        print("No patterns detected.")
    else:
        for p in patterns:
            print(f"Pattern: {p.get('name')} | Conf: {p.get('confidence'):.2f}")
            fav = p.get('favorable_markets') or []
            print(f"  Markets: {', '.join(fav)}")
            print(f"  Reason: {p.get('reasoning')}")

    top = result.get('top_markets', [])
    if top:
        print("\nTop markets by context:")
        for m in top[:5]:
            print(f"  {m.get('market')}: {m.get('context_score'):.2f}")


if __name__ == '__main__':
    main()
