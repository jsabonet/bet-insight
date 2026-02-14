"""
Teste do Hybrid Boost System
Valida se o sistema gera predições de alta qualidade
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.hybrid_boost_system import HybridBoostSystem

print("="*80)
print("TESTE HYBRID BOOST SYSTEM")
print("="*80)
print()

# Criar boost system
boost = HybridBoostSystem()

# Cenário 1: Favorito claro (Casa forte)
print("CENARIO 1: Favorito claro (Casa 60% vs Fora 20%)")
print("-"*80)

ml_probs_favorito = {
    'Casa': 0.60,
    'Empate': 0.20,
    'Fora': 0.20
}

result1 = boost.boost_predictions(ml_probs_favorito, league_id=39, min_quality='moderate')

print(f"\nSummary:")
print(f"  Total mercados: {result1['summary']['total_markets']}")
print(f"  Passaram threshold: {result1['summary']['passed_threshold']}")
print(f"  Alta qualidade: {result1['summary']['high_quality']}")
print(f"  Desabilitados: {result1['summary']['disabled_markets']}")

print(f"\nTop 5 mercados:")
for i, (market, prob) in enumerate(result1['sorted_markets'][:5], 1):
    print(f"  {i}. {market:25s} {prob*100:5.1f}%")

print()

# Cenário 2: Jogo equilibrado
print("CENARIO 2: Jogo equilibrado (Casa 35% vs Fora 35% vs Empate 30%)")
print("-"*80)

ml_probs_equilibrado = {
    'Casa': 0.35,
    'Empate': 0.30,
    'Fora': 0.35
}

result2 = boost.boost_predictions(ml_probs_equilibrado, league_id=39, min_quality='good')

print(f"\nSummary:")
print(f"  Total mercados: {result2['summary']['total_markets']}")
print(f"  Passaram threshold: {result2['summary']['passed_threshold']}")
print(f"  Alta qualidade (good+): {result2['summary']['high_quality']}")

print(f"\nTop 5 mercados:")
for i, (market, prob) in enumerate(result2['sorted_markets'][:5], 1):
    print(f"  {i}. {market:25s} {prob*100:5.1f}%")

print()

# Cenário 3: Best markets (top N)
print("CENARIO 3: Melhores mercados para apostar (favorito)")
print("-"*80)

best_markets = boost.get_best_markets(
    ml_probs_favorito,
    league_id=39,
    top_n=10,
    min_prob=0.65
)

print(f"\n{len(best_markets)} mercados com >65% probabilidade:")
for i, market_info in enumerate(best_markets, 1):
    print(f"  {i:2d}. {market_info['market']:25s} {market_info['probability']*100:5.1f}% " +
          f"(quality: {market_info['quality']}, threshold: {market_info['threshold']})")

print()
print("="*80)
print("TESTE CONCLUIDO")
print("="*80)
