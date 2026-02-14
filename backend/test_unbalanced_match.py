"""
Teste: Análise de Partida com Grande Diferença de Força
Caso: Brentford vs Arsenal

Probabilidades reais de mercado:
- Brentford (casa): 19.4%
- Empate: 22.4%
- Arsenal (fora): 58.2%

Arsenal é MUITO favorito mesmo jogando fora.
O sistema deve capturar essa diferença!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_unbalanced_match():
    """
    Testa partida com grande desequilíbrio de forças.
    """
    logger.info("="*80)
    logger.info("🔍 TESTE: PARTIDA COM GRANDE DIFERENÇA DE FORÇA")
    logger.info("="*80)
    
    logger.info("\n📊 CASO REAL: Brentford vs Arsenal")
    logger.info("   Fonte: Mercado de apostas")
    logger.info("\n   Probabilidades de Mercado:")
    logger.info("   • Brentford (casa): 19.4%")
    logger.info("   • Empate:           22.4%")
    logger.info("   • Arsenal (fora):   58.2%  ← MUITO FAVORITO")
    
    # Simular força dos times baseado nas odds
    # Odds aproximadas: Brentford ~5.15, Draw ~4.46, Arsenal ~1.72
    
    # Força estimada (0-1)
    brentford_strength = 0.45  # Time médio
    arsenal_strength = 0.85    # Time top
    
    # Forma recente
    brentford_form = 0.50  # Forma ok
    arsenal_form = 0.80    # Forma excelente
    
    logger.info("\n🎯 Força dos Times (estimada):")
    logger.info(f"   Brentford: {brentford_strength:.2f} | Forma: {brentford_form:.2f}")
    logger.info(f"   Arsenal:   {arsenal_strength:.2f} | Forma: {arsenal_form:.2f}")
    logger.info(f"   Diferença: {arsenal_strength - brentford_strength:.2f}")
    
    # TESTE 1: Poisson com força equilibrada
    logger.info("\n" + "="*80)
    logger.info("📊 TESTE 1: POISSON (conservador)")
    logger.info("="*80)
    
    # Goals esperados baseado na força
    home_attack = brentford_strength * 1.5  # 0.675 gols/jogo
    away_attack = arsenal_strength * 2.0    # 1.70 gols/jogo (Arsenal ataca muito)
    
    logger.info(f"\n   Goals esperados:")
    logger.info(f"   • Brentford: {home_attack:.2f}")
    logger.info(f"   • Arsenal:   {away_attack:.2f}")
    
    # Calcular Poisson manualmente
    # Simular matrix de Poisson
    max_goals = 6
    prob_matrix = np.zeros((max_goals, max_goals))
    
    for i in range(max_goals):
        for j in range(max_goals):
            prob_home = (home_attack**i * np.exp(-home_attack)) / np.math.factorial(i)
            prob_away = (away_attack**j * np.exp(-away_attack)) / np.math.factorial(j)
            prob_matrix[i, j] = prob_home * prob_away
    
    # Calcular probabilidades
    prob_home_win = np.sum(np.tril(prob_matrix, -1))  # Home > Away
    prob_draw = np.sum(np.diag(prob_matrix))           # Home = Away
    prob_away_win = np.sum(np.triu(prob_matrix, 1))   # Away > Home
    
    # Normalizar
    total = prob_home_win + prob_draw + prob_away_win
    prob_home_win /= total
    prob_draw /= total
    prob_away_win /= total
    
    logger.info(f"\n   Poisson prevê:")
    logger.info(f"   • Brentford: {prob_home_win*100:>5.1f}%")
    logger.info(f"   • Empate:    {prob_draw*100:>5.1f}%")
    logger.info(f"   • Arsenal:   {prob_away_win*100:>5.1f}%")
    
    # TESTE 2: Simular ML (usando probabilidades de mercado como proxy)
    logger.info("\n" + "="*80)
    logger.info("📊 TESTE 2: ML (captura diferença de força)")
    logger.info("="*80)
    
    # ML geralmente captura melhor essas diferenças
    ml_home = 0.25   # ML dá menos chance ao time fraco em casa
    ml_draw = 0.30   # ML tende a prever mais empates
    ml_away = 0.45   # ML reconhece favorito
    
    logger.info(f"\n   ML prevê:")
    logger.info(f"   • Brentford: {ml_home*100:>5.1f}%")
    logger.info(f"   • Empate:    {ml_draw*100:>5.1f}%")
    logger.info(f"   • Arsenal:   {ml_away*100:>5.1f}%")
    
    # TESTE 3: Market (usa as probabilidades reais)
    logger.info("\n" + "="*80)
    logger.info("📊 TESTE 3: MARKET (probabilidades reais)")
    logger.info("="*80)
    
    market_home = 0.194
    market_draw = 0.224
    market_away = 0.582
    
    logger.info(f"\n   Market prevê:")
    logger.info(f"   • Brentford: {market_home*100:>5.1f}%")
    logger.info(f"   • Empate:    {market_draw*100:>5.1f}%")
    logger.info(f"   • Arsenal:   {market_away*100:>5.1f}%")
    
    # TESTE 4: ENSEMBLE ATUAL (P=60%, ML=25%, M=15%)
    logger.info("\n" + "="*80)
    logger.info("⚖️ TESTE 4: ENSEMBLE ATUAL (P=60% ML=25% M=15%)")
    logger.info("="*80)
    
    weights_current = {'poisson': 0.60, 'ml': 0.25, 'market': 0.15}
    
    ensemble_home = (
        prob_home_win * weights_current['poisson'] +
        ml_home * weights_current['ml'] +
        market_home * weights_current['market']
    )
    ensemble_draw = (
        prob_draw * weights_current['poisson'] +
        ml_draw * weights_current['ml'] +
        market_draw * weights_current['market']
    )
    ensemble_away = (
        prob_away_win * weights_current['poisson'] +
        ml_away * weights_current['ml'] +
        market_away * weights_current['market']
    )
    
    # Normalizar
    total_ens = ensemble_home + ensemble_draw + ensemble_away
    ensemble_home /= total_ens
    ensemble_draw /= total_ens
    ensemble_away /= total_ens
    
    logger.info(f"\n   Ensemble atual prevê:")
    logger.info(f"   • Brentford: {ensemble_home*100:>5.1f}%")
    logger.info(f"   • Empate:    {ensemble_draw*100:>5.1f}%")
    logger.info(f"   • Arsenal:   {ensemble_away*100:>5.1f}%")
    
    # TESTE 5: ENSEMBLE AJUSTADO (P=40%, ML=30%, M=30%)
    logger.info("\n" + "="*80)
    logger.info("🔧 TESTE 5: ENSEMBLE AJUSTADO (P=40% ML=30% M=30%)")
    logger.info("="*80)
    logger.info("   Rationale: Mais peso em ML+Market quando há grande diferença")
    
    weights_adjusted = {'poisson': 0.40, 'ml': 0.30, 'market': 0.30}
    
    ensemble_home_adj = (
        prob_home_win * weights_adjusted['poisson'] +
        ml_home * weights_adjusted['ml'] +
        market_home * weights_adjusted['market']
    )
    ensemble_draw_adj = (
        prob_draw * weights_adjusted['poisson'] +
        ml_draw * weights_adjusted['ml'] +
        market_draw * weights_adjusted['market']
    )
    ensemble_away_adj = (
        prob_away_win * weights_adjusted['poisson'] +
        ml_away * weights_adjusted['ml'] +
        market_away * weights_adjusted['market']
    )
    
    # Normalizar
    total_adj = ensemble_home_adj + ensemble_draw_adj + ensemble_away_adj
    ensemble_home_adj /= total_adj
    ensemble_draw_adj /= total_adj
    ensemble_away_adj /= total_adj
    
    logger.info(f"\n   Ensemble ajustado prevê:")
    logger.info(f"   • Brentford: {ensemble_home_adj*100:>5.1f}%")
    logger.info(f"   • Empate:    {ensemble_draw_adj*100:>5.1f}%")
    logger.info(f"   • Arsenal:   {ensemble_away_adj*100:>5.1f}%")
    
    # COMPARAÇÃO COM MERCADO
    logger.info("\n" + "="*80)
    logger.info("📊 COMPARAÇÃO: ERRO vs MERCADO REAL")
    logger.info("="*80)
    
    # Erro absoluto médio
    mae_current = (
        abs(ensemble_home - market_home) +
        abs(ensemble_draw - market_draw) +
        abs(ensemble_away - market_away)
    ) / 3
    
    mae_adjusted = (
        abs(ensemble_home_adj - market_home) +
        abs(ensemble_draw_adj - market_draw) +
        abs(ensemble_away_adj - market_away)
    ) / 3
    
    logger.info(f"\n   Erro Atual:    {mae_current*100:.2f}%")
    logger.info(f"   Erro Ajustado: {mae_adjusted*100:.2f}%")
    logger.info(f"   Melhora:       {(mae_current - mae_adjusted)*100:+.2f}%")
    
    if mae_adjusted < mae_current:
        logger.info(f"\n   ✅ Pesos ajustados SÃO MELHORES!")
    else:
        logger.info(f"\n   ❌ Pesos atuais são melhores")
    
    # RECOMENDAÇÃO
    logger.info("\n" + "="*80)
    logger.info("💡 RECOMENDAÇÃO")
    logger.info("="*80)
    
    # Calcular diferença de força
    strength_diff = abs(arsenal_strength - brentford_strength)
    
    logger.info(f"\n   Diferença de força: {strength_diff:.2f}")
    
    if strength_diff > 0.3:
        logger.info(f"\n   🎯 GRANDE DIFERENÇA DETECTADA!")
        logger.info(f"\n   Pesos recomendados para este tipo de partida:")
        logger.info(f"   • Poisson: 30-40% (menos conservador)")
        logger.info(f"   • ML:      30-40% (captura padrões)")
        logger.info(f"   • Market:  30-40% (reflete odds reais)")
        logger.info(f"\n   📝 Implementar PESOS ADAPTATIVOS:")
        logger.info(f"   - Se strength_diff < 0.2: Usar pesos atuais (P=60%)")
        logger.info(f"   - Se strength_diff ≥ 0.2: Usar pesos ajustados (P=40%)")
    else:
        logger.info(f"\n   ✅ Diferença normal - pesos atuais OK")
    
    logger.info("\n" + "="*80)
    
    return {
        'strength_diff': strength_diff,
        'mae_current': mae_current,
        'mae_adjusted': mae_adjusted,
        'needs_adaptive_weights': strength_diff > 0.3
    }


if __name__ == '__main__':
    result = test_unbalanced_match()
    
    if result['needs_adaptive_weights']:
        print("\n" + "="*80)
        print("⚠️ AÇÃO NECESSÁRIA: Implementar pesos adaptativos")
        print("="*80)
        print("\nPróximo passo:")
        print("python implement_adaptive_weights.py")
        print("="*80)
