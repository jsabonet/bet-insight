"""
Teste direto: verificar quais mercados críticos estão realmente disponíveis
"""
import django
import os
import sys

sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService

# Mercados CRÍTICOS que o sistema precisa (baseado no Poisson)
CRITICAL_MARKETS = [
    # 1X2
    'home_win', 'draw', 'away_win',
    # Double Chance
    '1x', '12', 'x2',
    # Over/Under principais
    'over_0.5', 'under_0.5',
    'over_1.5', 'under_1.5',
    'over_2.5', 'under_2.5',
    'over_3.5', 'under_3.5',
    'over_4.5', 'under_4.5',
    # Asiáticas
    'over_1.75', 'under_1.75',
    'over_2.25', 'under_2.25',
    'over_2.75', 'under_2.75',
    'over_3.25', 'under_3.25',
    # BTTS
    'btts_yes', 'btts_no', 'btts',
    # Team Totals
    'home_over_0.5', 'home_under_0.5',
    'home_over_1.5', 'home_under_1.5',
    'home_over_2.5', 'home_under_2.5',
    'away_over_0.5', 'away_under_0.5',
    'away_over_1.5', 'away_under_1.5',
    'away_over_2.5', 'away_under_2.5',
    # Odd/Even
    'odd_goals', 'even_goals',
]

print("\n" + "="*80)
print("TESTE DIRETO: Odds disponiveis vs Mercados Criticos")
print("="*80 + "\n")

api_service = APIFootballService()
fixture_id = 1379234

odds = api_service.fetch_odds(fixture_id)
print(f"Total de mercados retornados: {len(odds)}\n")

# Verificar mercados críticos
available = []
missing = []
alternative = {}

for market in CRITICAL_MARKETS:
    if market in odds:
        available.append(market)
    else:
        missing.append(market)
        # Verificar se existe variante alternativa
        if market == 'btts_yes' and 'btts' in odds:
            alternative[market] = 'btts'
        elif market == 'btts_no' and 'btts' not in odds:
            pass  # Não há alternativa

print(f"DISPONIVEIS: {len(available)}/{len(CRITICAL_MARKETS)} ({len(available)/len(CRITICAL_MARKETS)*100:.1f}%)")
for market in sorted(available):
    print(f"   OK {market} = {odds[market]}")

if missing:
    print(f"\nFALTANDO: {len(missing)} mercados")
    for market in sorted(missing):
        if market in alternative:
            print(f"   X {market} (alternativa: {alternative[market]} = {odds[alternative[market]]})")
        else:
            print(f"   X {market}")

if alternative:
    print(f"\nALTERNATIVAS ENCONTRADAS: {len(alternative)} mercados")
    for original, alt in alternative.items():
        print(f"   '{original}' -> '{alt}'")

# Mostrar todos os mercados disponiveis
print(f"\nTODOS OS MERCADOS DISPONIVEIS ({len(odds)}):")
for market in sorted(odds.keys()):
    print(f"   {market} = {odds[market]}")

print("\n" + "="*80)
print("ANÁLISE:")
print("="*80)

# Verificar categorias específicas
categories = {
    '1X2': ['home_win', 'draw', 'away_win'],
    'Double Chance': ['1x', '12', 'x2'],
    'Over/Under Global': ['over_0.5', 'over_1.5', 'over_2.5', 'over_3.5', 'over_4.5',
                          'under_0.5', 'under_1.5', 'under_2.5', 'under_3.5', 'under_4.5'],
    'BTTS': ['btts', 'btts_yes', 'btts_no'],
    'Team Totals Casa': ['home_over_0.5', 'home_over_1.5', 'home_over_2.5'],
    'Team Totals Fora': ['away_over_0.5', 'away_over_1.5', 'away_over_2.5'],
    'Odd/Even': ['odd_goals', 'even_goals'],
}

for category, markets in categories.items():
    available_cat = [m for m in markets if m in odds]
    print(f"\n{category}: {len(available_cat)}/{len(markets)}")
    for m in markets:
        status = "OK" if m in odds else "X"
        value = f"= {odds[m]}" if m in odds else ""
        print(f"   {status} {m} {value}")

print("\n" + "="*80)
