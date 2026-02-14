"""
Lista todos os mercados disponíveis no sistema
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.statistical_models import PoissonBivariateModel

# Criar modelo e gerar predição de exemplo
model = PoissonBivariateModel()

# Fazer predição com valores genéricos
prediction = model.predict(
    home_strength=1.4,
    away_strength=1.2,
    home_defense=1.1,
    away_defense=1.1,
    weather_impact=0.0,
    league_id=None
)

# Pegar todos os mercados disponíveis
markets = prediction['probabilities']

print("="*80)
print("MERCADOS DISPONÍVEIS NO SISTEMA")
print("="*80)

# Agrupar por categoria
categories = {
    '1X2 Principais': ['home_win', 'draw', 'away_win'],
    'Double Chance': ['1X', '12', 'X2'],
    'Over/Under Padrão': [
        'over_0_5', 'under_0_5',
        'over_1_5', 'under_1_5', 
        'over_2_5', 'under_2_5',
        'over_3_5', 'under_3_5',
        'over_4_5', 'under_4_5'
    ],
    'Asian Lines': [
        'over_1_75', 'under_1_75',
        'over_2_25', 'under_2_25',
        'over_2_75', 'under_2_75',
        'over_3_25', 'under_3_25'
    ],
    'BTTS (Ambas Marcam)': ['btts', 'btts_yes', 'btts_no'],
    'Clean Sheets': ['home_clean_sheet', 'away_clean_sheet'],
    'Team Total - Casa': [
        'home_over_0.5', 'home_under_0.5',
        'home_over_1.5', 'home_under_1.5',
        'home_over_2.5', 'home_under_2.5'
    ],
    'Team Total - Fora': [
        'away_over_0.5', 'away_under_0.5',
        'away_over_1.5', 'away_under_1.5',
        'away_over_2.5', 'away_under_2.5'
    ],
    'Margens de Vitória': [
        'home_by_1', 'home_by_2plus',
        'away_by_1', 'away_by_2plus',
        'any_by_1', 'any_by_2plus'
    ],
    'Odd/Even': ['odd_goals', 'even_goals']
}

total_markets = 0

for category, market_list in categories.items():
    print(f"\n{category}:")
    count = 0
    for market in market_list:
        if market in markets:
            prob = markets[market] * 100
            print(f"  {market:25s}: {prob:6.2f}%")
            count += 1
    print(f"  Subtotal: {count} mercados")
    total_markets += count

# Verificar se há mercados não categorizados
all_categorized = set()
for market_list in categories.values():
    all_categorized.update(market_list)

uncategorized = set(markets.keys()) - all_categorized

if uncategorized:
    print(f"\nMercados não categorizados:")
    for market in sorted(uncategorized):
        prob = markets[market] * 100
        print(f"  {market:25s}: {prob:6.2f}%")
    total_markets += len(uncategorized)

print("\n" + "="*80)
print(f"TOTAL DE MERCADOS: {total_markets}")
print("="*80)

# Informações adicionais
print(f"\nINFORMAÇÕES ADICIONAIS:")
print(f"  Expected Goals - Casa: {prediction['expected_goals']['home']:.2f}")
print(f"  Expected Goals - Fora: {prediction['expected_goals']['away']:.2f}")
print(f"  Placar mais provável: {prediction['most_likely_score']['score']}")
print(f"  Modelo: {prediction['model']}")

print("\n" + "="*80)
