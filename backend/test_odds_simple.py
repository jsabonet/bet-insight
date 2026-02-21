import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.analysis.services.api_football_service import APIFootballService

# Testar fixture 1379234
api = APIFootballService()
odds = api.fetch_odds(1379234)

print("\n" + "="*100)
print(f"✅ TOTAL: {len(odds)} mercados com odds disponíveis")
print("="*100)

# Categorias críticas
categories = {
    '1X2': ['home_win', 'draw', 'away_win'],
    'Dupla Chance': ['1x', '12', 'x2'],
    'Over/Under 0.5': ['over_0.5', 'under_0.5'],
    'Over/Under 1.5': ['over_1.5', 'under_1.5'],
    'Over/Under 2.5': ['over_2.5', 'under_2.5'],
    'Over/Under 3.5': ['over_3.5', 'under_3.5'],
    'BTTS': ['btts_yes', 'btts_no'],
    'Odd/Even': ['odd_goals', 'even_goals'],
    'Home Totals': ['home_over_0.5', 'home_over_1.5', 'home_over_2.5'],
    'Away Totals': ['away_over_0.5', 'away_over_1.5', 'away_over_2.5']
}

for cat, markets in categories.items():
    found = sum(1 for m in markets if m in odds)
    status = "✅" if found == len(markets) else ("⚠️" if found > 0 else "❌")
    print(f"\n{status} {cat} ({found}/{len(markets)})")
    
    for m in markets:
        if m in odds:
            print(f"   {m}: {odds[m]}")
        else:
            print(f"   {m}: ❌ AUSENTE")

print("\n" + "="*100)
print(f"COMPARAÇÃO:\n  Antes (log): 10 mercados\n  Agora: {len(odds)} mercados")
print(f"  Melhoria: +{len(odds) - 10} mercados" if len(odds) > 10 else "  ❌ Problema persiste")
print("="*100 + "\n")
