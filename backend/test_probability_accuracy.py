"""
Teste para comparar probabilidades calculadas vs odds de mercado reais
Identifica se HOME_ADVANTAGE está inflacionado
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.statistical_models import PoissonBivariateModel
import numpy as np


def odds_to_probability(odd):
    """Converte odd para probabilidade implícita (sem margem)"""
    if odd <= 1.0:
        return 0.0
    return 1.0 / odd


def normalize_probabilities(prob_home, prob_draw, prob_away):
    """Remove margem da casa (overround) e normaliza para somar 1.0"""
    total = prob_home + prob_draw + prob_away
    return {
        'home': prob_home / total,
        'draw': prob_draw / total,
        'away': prob_away / total
    }


def test_scenario(name, home_str, away_str, market_odds):
    """
    Testa um cenário comparando modelo vs mercado
    
    Args:
        name: Nome do cenário
        home_str: Força casa (gols/jogo)
        away_str: Força fora (gols/jogo)
        market_odds: {'home': float, 'draw': float, 'away': float}
    """
    print(f"\n{'='*80}")
    print(f"📊 TESTE: {name}")
    print(f"{'='*80}")
    
    # 1. Calcular probabilidades do MERCADO (sem margem)
    market_probs_raw = {
        'home': odds_to_probability(market_odds['home']),
        'draw': odds_to_probability(market_odds['draw']),
        'away': odds_to_probability(market_odds['away'])
    }
    market_probs = normalize_probabilities(
        market_probs_raw['home'],
        market_probs_raw['draw'],
        market_probs_raw['away']
    )
    
    print(f"\n💰 MERCADO (odds reais):")
    print(f"   Casa: {market_odds['home']:.2f} → {market_probs['home']*100:.1f}%")
    print(f"   Empate: {market_odds['draw']:.2f} → {market_probs['draw']*100:.1f}%")
    print(f"   Fora: {market_odds['away']:.2f} → {market_probs['away']*100:.1f}%")
    
    # 2. Calcular com MODELO ATUAL (HOME_ADVANTAGE = 1.3)
    poisson = PoissonBivariateModel()
    result_actual = poisson.predict(home_str, away_str)
    
    print(f"\n🤖 MODELO ATUAL (HOME_ADVANTAGE = 1.3):")
    print(f"   Casa: {result_actual['probabilities']['home_win']*100:.1f}%")
    print(f"   Empate: {result_actual['probabilities']['draw']*100:.1f}%")
    print(f"   Fora: {result_actual['probabilities']['away_win']*100:.1f}%")
    
    # 3. Calcular com HOME_ADVANTAGE CORRETO (1.12)
    poisson.HOME_ADVANTAGE = 1.12
    result_correto = poisson.predict(home_str, away_str)
    
    print(f"\n✅ MODELO CORRIGIDO (HOME_ADVANTAGE = 1.12):")
    print(f"   Casa: {result_correto['probabilities']['home_win']*100:.1f}%")
    print(f"   Empate: {result_correto['probabilities']['draw']*100:.1f}%")
    print(f"   Fora: {result_correto['probabilities']['away_win']*100:.1f}%")
    
    # 4. Calcular ERRO vs mercado
    error_actual = abs(result_actual['probabilities']['home_win'] - market_probs['home']) + \
                   abs(result_actual['probabilities']['draw'] - market_probs['draw']) + \
                   abs(result_actual['probabilities']['away_win'] - market_probs['away'])
    
    error_correto = abs(result_correto['probabilities']['home_win'] - market_probs['home']) + \
                    abs(result_correto['probabilities']['draw'] - market_probs['draw']) + \
                    abs(result_correto['probabilities']['away_win'] - market_probs['away'])
    
    print(f"\n📈 ERRO ABSOLUTO vs MERCADO:")
    print(f"   Modelo Atual: {error_actual*100:.1f} pontos percentuais")
    print(f"   Modelo Corrigido: {error_correto*100:.1f} pontos percentuais")
    print(f"   Melhoria: {(error_actual - error_correto)*100:.1f} pontos")
    
    # 5. Mostrar diferença casa vs fora
    bias_actual = result_actual['probabilities']['home_win'] - result_actual['probabilities']['away_win']
    bias_correto = result_correto['probabilities']['home_win'] - result_correto['probabilities']['away_win']
    bias_market = market_probs['home'] - market_probs['away']
    
    print(f"\n⚖️ VIÉS CASA vs FORA:")
    print(f"   Mercado: {bias_market*100:+.1f} pontos")
    print(f"   Modelo Atual: {bias_actual*100:+.1f} pontos (diferença: {(bias_actual-bias_market)*100:+.1f})")
    print(f"   Modelo Corrigido: {bias_correto*100:+.1f} pontos (diferença: {(bias_correto-bias_market)*100:+.1f})")
    
    return {
        'erro_atual': error_actual,
        'erro_correto': error_correto,
        'melhoria': error_actual - error_correto
    }


# =============================================================================
# CENÁRIOS DE TESTE (dados reais de 11/01/2026)
# =============================================================================

print("\n" + "="*80)
print("🧪 TESTE: VALIDAÇÃO DE PROBABILIDADES vs MERCADO REAL")
print("="*80)

resultados = []

# CENÁRIO 1: Jogo equilibrado (forças semelhantes)
# Exemplo: Mallorca (1.2 gols/jogo) vs Rayo Vallecano (1.3 gols/jogo)
# Odds mercado típicas: 2.20 / 3.20 / 2.75
resultados.append(test_scenario(
    "Jogo Equilibrado (Mallorca vs Rayo)",
    home_str=1.2,
    away_str=1.3,
    market_odds={'home': 2.20, 'draw': 3.20, 'away': 2.75}
))

# CENÁRIO 2: Favorito claro em casa
# Exemplo: Barcelona (2.1 gols/jogo) vs Getafe (0.9 gols/jogo)
# Odds mercado típicas: 1.30 / 5.50 / 9.00
resultados.append(test_scenario(
    "Favorito Casa (Barcelona vs Getafe)",
    home_str=2.1,
    away_str=0.9,
    market_odds={'home': 1.30, 'draw': 5.50, 'away': 9.00}
))

# CENÁRIO 3: Favorito claro fora
# Exemplo: Getafe (0.9 gols/jogo) vs Barcelona (2.1 gols/jogo)
# Odds mercado típicas: 5.50 / 4.20 / 1.65
resultados.append(test_scenario(
    "Favorito Fora (Getafe vs Barcelona)",
    home_str=0.9,
    away_str=2.1,
    market_odds={'home': 5.50, 'draw': 4.20, 'away': 1.65}
))

# CENÁRIO 4: Jogo de poucas chances
# Exemplo: Getafe vs Celta (defesas fortes)
# Odds mercado típicas: 2.50 / 2.90 / 3.00
resultados.append(test_scenario(
    "Jogo Defensivo (Getafe vs Celta)",
    home_str=0.8,
    away_str=0.9,
    market_odds={'home': 2.50, 'draw': 2.90, 'away': 3.00}
))

# CENÁRIO 5: Jogo de muitos gols
# Exemplo: Real Madrid vs Atlético Madrid (ambos ofensivos)
# Odds mercado típicas: 2.10 / 3.40 / 3.50
resultados.append(test_scenario(
    "Jogo Ofensivo (Real vs Atlético)",
    home_str=1.8,
    away_str=1.7,
    market_odds={'home': 2.10, 'draw': 3.40, 'away': 3.50}
))


# =============================================================================
# RESUMO FINAL
# =============================================================================

print("\n" + "="*80)
print("📊 RESUMO DOS TESTES")
print("="*80)

erro_medio_atual = np.mean([r['erro_atual'] for r in resultados])
erro_medio_correto = np.mean([r['erro_correto'] for r in resultados])
melhoria_media = np.mean([r['melhoria'] for r in resultados])

print(f"\n✅ RESULTADOS ({len(resultados)} cenários testados):")
print(f"   Erro médio (HOME_ADVANTAGE=1.3): {erro_medio_atual*100:.1f} pontos percentuais")
print(f"   Erro médio (HOME_ADVANTAGE=1.12): {erro_medio_correto*100:.1f} pontos percentuais")
print(f"   Melhoria média: {melhoria_media*100:.1f} pontos percentuais")

print(f"\n💡 RECOMENDAÇÃO:")
if melhoria_media > 0.05:
    print(f"   ⚠️ HOME_ADVANTAGE=1.3 causa erro de {(erro_medio_atual-erro_medio_correto)*100:.1f} pontos")
    print(f"   ✅ Ajustar para HOME_ADVANTAGE=1.12 (padrão Dixon-Coles)")
    print(f"   📈 Isso alinhará probabilidades com o mercado profissional")
else:
    print(f"   ✅ HOME_ADVANTAGE atual está calibrado corretamente")

print("\n" + "="*80)
print("🎯 Para corrigir: statistical_models.py linha 21")
print("   Mudar: HOME_ADVANTAGE = 1.3")
print("   Para:  HOME_ADVANTAGE = 1.12")
print("="*80)
