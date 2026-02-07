"""
Teste do MarketSelector com dados reais do Celta vs Osasuna
Diagnstico completo do mapeamento de mercados e probabilidades
"""

import os
import django
import json
import logging

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

from apps.matches.models import Match
from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.analysis.services.market_selector import MarketSelector

# Buscar match
match = Match.objects.filter(api_football_id=1391043).first()

if not match:
    print(" Match Celta vs Osasuna no encontrado")
    exit(1)

print("="*80)
print(f"TESTE: {match.home_team} vs {match.away_team}")
print(f"   Data: {match.match_date}")
print(f"   Liga: {match.league}")
print("="*80)

# Simular dados de anlise (baseado na estrutura do teste anterior)
print("\nSIMULANDO DADOS DE ANALISE...")

# Features (normalizar valores reais para 0-1)
features = {
    'home_motivation': 6,  # Escala 0-10
    'away_motivation': 7,  # Escala 0-10
    'home_goals_per_game': 1.2,  # Gols por jogo
    'away_goals_per_game': 1.4,
    'home_form': 0.6,  # 0-1
    'away_form': 0.7,
    'home_fatigue': 3,  # 0-10
    'away_fatigue': 4,
    'head_to_head_home_wins': 0.4,
    'head_to_head_draws': 0.3,
    'head_to_head_away_wins': 0.3,
    'is_derby': 0,
    'home_key_player_missing': 0,
    'away_key_player_missing': 0
}

# Model predictions (estrutura real do sistema)
model_predictions = {
    'consensus': {
        'home_win': 0.388,
        'draw': 0.312,
        'away_win': 0.299
    },
    'poisson': {
        'probabilities': {
            'over_0.5': 0.92,
            'under_0.5': 0.08,
            'over_1.5': 0.78,
            'under_1.5': 0.22,
            'over_2.5': 0.52,
            'under_2.5': 0.48,
            'over_3.5': 0.28,
            'under_3.5': 0.72,
            'btts_yes': 0.58,
            'btts_no': 0.42,
            'btts': 0.58
        }
    }
}

# Market odds (ajustados para gerar value)
market_odds = {
    'home': 2.58,
    'draw': 3.20,
    'away': 3.35,
    'over_2.5': 1.92,
    'under_2.5': 2.12,  # Odd melhor (EV positivo)
    'over_1.5': 1.40,
    'under_1.5': 3.10,
    'btts_yes': 1.72,
    'btts_no': 2.45,  # Odd melhor para 42% prob (fair=2.38)
    'draw_ht': 2.05
}

print("OK Features simulados")
print("OK Model predictions carregados")
print("OK Market odds carregados")

# 1. RODAR CONTEXT ANALYZER
print("\n" + "="*80)
print("1 RODANDO CONTEXT ANALYZER")
print("="*80)

analyzer = ContextAnalyzer()
context_analysis = analyzer.analyze(features)

print(f"\n PADRES DETECTADOS: {len(context_analysis.get('patterns', []))}")
for pattern in context_analysis.get('patterns', []):
    print(f"\n    {pattern['name']}")
    print(f"      Confiana: {pattern['confidence']:.0%}")
    print(f"      Reasoning: {pattern.get('reasoning', 'N/A')}")

print(f"\n TOP MERCADOS CONTEXTUAIS:")
for market in context_analysis.get('top_markets', [])[:5]:
    print(f"\n   {market['market']}")
    print(f"      Context Score: {market['context_score']:.0%}")
    print(f"      Suportado por: {', '.join(market['supporting_patterns'])}")

# 2. RODAR MARKET SELECTOR - VALUE
print("\n" + "="*80)
print("2 RODANDO MARKET SELECTOR - VALUE BET")
print("="*80)

selector = MarketSelector()
selected_value = selector.select_top_markets(
    context_analysis,
    model_predictions,
    market_odds,
    strategy='value'
)

print(f"\n SELECIONADOS (VALUE): {len(selected_value)}")
for bet in selected_value:
    print(f"\n   #{bet['rank']} {bet['market_display']}")
    print(f"      Mercado: {bet['market']}")
    print(f"      Probabilidade: {bet['probability']:.0%}")
    print(f"      Context Score: {bet['context_score']:.0%}")
    print(f"      Final Score: {bet['final_score']:.3f}")
    print(f"      Odd: {bet['market_odd']}")
    print(f"      EV: {bet['ev_pct']:+.1f}%")
    print(f"      Razo: {bet['reasoning']}")

# 3. RODAR MARKET SELECTOR - MULTIPLE
print("\n" + "="*80)
print("3 RODANDO MARKET SELECTOR - BILHETE MLTIPLO")
print("="*80)

selected_multiple = selector.select_top_markets(
    context_analysis,
    model_predictions,
    market_odds,
    strategy='multiple'
)

print(f"\n SELECIONADOS (MULTIPLE): {len(selected_multiple)}")
for bet in selected_multiple:
    print(f"\n   #{bet['rank']} {bet['market_display']}")
    print(f"      Mercado: {bet['market']}")
    print(f"      Probabilidade: {bet['probability']:.0%}")
    print(f"      Context Score: {bet['context_score']:.0%}")
    print(f"      Final Score: {bet['final_score']:.3f}")
    print(f"      Odd: {bet['market_odd']}")
    print(f"      EV: {bet['ev_pct']:+.1f}%")
    print(f"      Razo: {bet['reasoning']}")

# 4. DIAGNSTICO DE MAPEAMENTO
print("\n" + "="*80)
print("4 DIAGNSTICO DE MAPEAMENTO DE MERCADOS")
print("="*80)

print("\n MERCADOS DO CONTEXTO vs PROBABILIDADES DISPONVEIS:")

all_probabilities = {**model_predictions['poisson']['probabilities'], **model_predictions['consensus']}

for market_data in context_analysis.get('top_markets', [])[:10]:
    market = market_data['market']
    normalized = selector.MARKET_MAPPING.get(market, market)
    
    print(f"\n   {market}  {normalized}")
    print(f"      Context score: {market_data['context_score']:.0%}")
    
    # Tentar encontrar probabilidade
    prob = all_probabilities.get(normalized, 0)
    
    if prob > 0:
        print(f"       Probabilidade encontrada: {prob:.0%}")
    else:
        print(f"       Probabilidade NO encontrada")
        print(f"         Tentando variaes:")
        # Tentar variaes
        variations = [
            market,
            market.replace('_', ''),
            market.replace('.', ''),
            normalized.replace('_', ''),
            normalized.replace('.', '')
        ]
        for var in variations:
            if var in all_probabilities:
                print(f"          Encontrado em '{var}': {all_probabilities[var]:.0%}")
                break
        else:
            print(f"          Nenhuma variao encontrada")

print("\n" + "="*80)
print(" PROBABILIDADES DISPONVEIS NO MODELO:")
print("="*80)
for key in sorted(all_probabilities.keys()):
    print(f"   {key}: {all_probabilities[key]:.0%}")

print("\n" + "="*80)
print(" TESTE COMPLETO")
print("="*80)
