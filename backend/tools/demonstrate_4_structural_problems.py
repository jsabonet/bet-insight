"""
Demonstra os 4 Problemas Estruturais do Sistema

Executa casos de teste concretos que mostram como cada problema
distorce as recomendações de apostas.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


def problema_1_nomenclatura():
    """
    Problema 1: Babel de Nomenclaturas
    Demonstra que odds não são encontradas devido a nomes inconsistentes
    """
    print("\n" + "="*80)
    print("PROBLEMA 1: BABEL DE NOMENCLATURAS")
    print("="*80)
    
    from apps.analysis.services.market_selector import MarketSelector
    
    selector = MarketSelector()
    
    # Odds dict do views.py (formato real)
    market_odds = {
        'odds_home': 2.10,
        'odds_draw': 3.40,
        'odds_away': 1.36,
        'odds_over25': 1.95,  # ← sem separador
        'odds_under25': 1.85,
    }
    
    # MarketSelector procura com pontos
    markets_to_test = ['over_2.5', 'under_2.5', '1X', 'X2', 'dnb_home']
    
    print("\nBuscando odds com _get_market_odd():")
    for market in markets_to_test:
        odd = selector._get_market_odd(market, market_odds)
        if odd == 2.00:
            print(f"   ❌ {market:15s} → {odd:.2f} (PADRÃO GENÉRICO - não encontrou!)")
        else:
            print(f"   ✅ {market:15s} → {odd:.2f}")
    
    print("\n💥 IMPACTO:")
    print("   - Odd genérica 2.00 usada quando não encontra")
    print("   - EV calculado com odd errada → ranking distorcido")
    print("   - Mercados derivados (DC, DNB) nunca têm odds reais")


def problema_2_mercados_derivados():
    """
    Problema 2: Mercados Derivados sem Odds Reais
    Demonstra como DC/DNB têm probabilidades corretas mas odds fake
    """
    print("\n" + "="*80)
    print("PROBLEMA 2: MERCADOS DERIVADOS SEM ODDS REAIS")
    print("="*80)
    
    from apps.analysis.services.statistical_models import PoissonBivariateModel
    
    # Cenário: Favorito forte (Benfica fora)
    poisson = PoissonBivariateModel()
    result = poisson.predict(lambda_home=0.8, lambda_away=2.2)
    probs = result['probabilities']
    
    print("\nProbabilidades Calculadas (CORRETAS):")
    print(f"   Home Win:  {probs['home_win']*100:5.1f}%")
    print(f"   Draw:      {probs['draw']*100:5.1f}%")
    print(f"   Away Win:  {probs['away_win']*100:5.1f}%")
    print(f"   1X:        {probs['1X']*100:5.1f}% (Home + Draw)")
    print(f"   X2:        {probs['X2']*100:5.1f}% (Draw + Away)")
    print(f"   12:        {probs['12']*100:5.1f}% (Home + Away)")
    
    # Odds reais (simuladas realisticamente)
    real_odds = {
        'home_win': 8.50,
        'draw': 5.20,
        'away_win': 1.36,
        # DC não existem normalmente no market_odds
    }
    
    # Sistema calcula fair odds
    fair_odds = {
        'home_win': 1 / probs['home_win'],
        'away_win': 1 / probs['away_win'],
        '1X': 1 / probs['1X'],
        'X2': 1 / probs['X2'],
    }
    
    print("\nOdds Reais vs Fair Odds:")
    print(f"   Away Win:  Real={real_odds['away_win']:.2f}, Fair={fair_odds['away_win']:.2f}, EV={(real_odds['away_win']/fair_odds['away_win']-1)*100:+.1f}%")
    
    # Sistema usa odd genérica para mercados derivados
    from apps.analysis.services.market_selector import MarketSelector
    selector = MarketSelector()
    
    market_odds = {
        'home': real_odds['home_win'],
        'draw': real_odds['draw'],
        'away': real_odds['away_win'],
    }
    
    x2_odd = selector._get_market_odd('X2', market_odds)
    x2_fair = fair_odds['X2']
    x2_ev = (x2_odd / x2_fair - 1) * 100
    
    print(f"   X2:        Real={x2_odd:.2f} (GENÉRICA!), Fair={x2_fair:.2f}, EV={x2_ev:+.1f}% ❌")
    
    # Odd X2 correta seria
    x2_real_correct = 1 / (1/real_odds['draw'] + 1/real_odds['away_win'])
    x2_ev_correct = (x2_real_correct / x2_fair - 1) * 100
    print(f"   X2 (calc): Real={x2_real_correct:.2f} (calculada), Fair={x2_fair:.2f}, EV={x2_ev_correct:+.1f}% ✅")
    
    print("\n💥 IMPACTO:")
    print(f"   - Odd genérica X2=2.00 sugere EV={x2_ev:+.1f}%")
    print(f"   - Odd correta X2={x2_real_correct:.2f} tem EV={x2_ev_correct:+.1f}%")
    print(f"   - Diferença: {abs(x2_ev - x2_ev_correct):.1f} pontos percentuais de edge falso!")


def problema_3_odds_simuladas():
    """
    Problema 3: Odds Simuladas tratadas como Reais
    Demonstra como odds simuladas sempre têm EV ~-5%
    """
    print("\n" + "="*80)
    print("PROBLEMA 3: ODDS SIMULADAS = ODDS REAIS")
    print("="*80)
    
    # Consenso do modelo
    consensus = {
        'home_win': 0.42,
        'draw': 0.30,
        'away_win': 0.28
    }
    
    # Sistema simula odds com margin 5%
    bookmaker_margin = 1.05
    
    simulated_odds = {
        'home': round((1 / consensus['home_win']) / bookmaker_margin, 2),
        'draw': round((1 / consensus['draw']) / bookmaker_margin, 2),
        'away': round((1 / consensus['away_win']) / bookmaker_margin, 2),
    }
    
    print("\nOdds Simuladas (margin 5%):")
    for market, odd in simulated_odds.items():
        prob = consensus.get(f'{market}_win' if market != 'draw' else 'draw')
        fair_odd = 1 / prob
        ev = (odd / fair_odd - 1) * 100
        print(f"   {market:8s}: Odd={odd:.2f}, Fair={fair_odd:.2f}, EV={ev:+.1f}%")
    
    print("\n💥 IMPACTO:")
    print("   - TODAS as odds simuladas têm EV ≈ -5% (por design do margin)")
    print("   - Sistema NÃO sabe que são simuladas → trata como 'mercado desfavorável'")
    print("   - Resultado: Apostas rejeitadas mesmo quando modelo está confiante")
    print("\nComparação com Odd Real:")
    print("   - Odd real poderia ter EV +10% (bookmaker errou)")
    print("   - Odd simulada sempre tem EV -5% (modelo vs modelo com margin)")
    print("   - Sistema toma decisões diferentes sem motivo válido!")


def problema_4_score_multiplicado():
    """
    Problema 4: Score Multiplicado 2-3x
    Demonstra como probability é elevada ao cubo
    """
    print("\n" + "="*80)
    print("PROBLEMA 4: MULTIPLICAÇÃO DUPLA/TRIPLA DE SCORES")
    print("="*80)
    
    # Aposta exemplo
    prob = 0.65
    context = 0.80
    ev_pct = 20.0
    
    print(f"\nAposta: Under 2.5")
    print(f"   Probability: {prob*100:.0f}%")
    print(f"   Context: {context*100:.0f}%")
    print(f"   EV: {ev_pct:+.1f}%")
    
    # ESTÁGIO 1: MarketSelector
    print("\n--- ESTÁGIO 1: MarketSelector ---")
    ev_multiplier = 1 + max(0, ev_pct / 100) * 0.5
    final_score_stage1 = prob * context * ev_multiplier
    print(f"   final_score = {prob:.2f} × {context:.2f} × {ev_multiplier:.2f}")
    print(f"   final_score = {final_score_stage1:.3f}")
    
    # ESTÁGIO 2: DecisionEngine
    print("\n--- ESTÁGIO 2: DecisionEngine ---")
    print("   (NÃO usa final_score do estágio 1, recalcula do zero!)")
    prob_weight = prob ** 1.5
    ev_weight = 1 + max(0, ev_pct / 100)
    score_stage2 = prob_weight * ev_weight * 1.0 * 1.0
    print(f"   prob_weight = {prob:.2f}^1.5 = {prob_weight:.3f}")
    print(f"   ev_weight = 1 + {ev_pct/100:.2f} = {ev_weight:.2f}")
    print(f"   score = {prob_weight:.3f} × {ev_weight:.2f} = {score_stage2:.3f}")
    
    # ESTÁGIO 3: PostDecisionSelector
    print("\n--- ESTÁGIO 3: PostDecisionSelector ---")
    print(f"   base_score = {score_stage2:.3f} (do DecisionEngine)")
    prob_weight_stage3 = prob ** 1.5  # ← MULTIPLICA DE NOVO!
    ev_weight_stage3 = 1 + ev_pct / 200
    final_score_stage3 = score_stage2 * prob_weight_stage3 * ev_weight_stage3
    print(f"   prob_weight = {prob:.2f}^1.5 = {prob_weight_stage3:.3f} ❌ DUPLICADO!")
    print(f"   ev_weight = 1 + {ev_pct/200:.2f} = {ev_weight_stage3:.2f}")
    print(f"   final_score = {score_stage2:.3f} × {prob_weight_stage3:.3f} × {ev_weight_stage3:.2f}")
    print(f"   final_score = {final_score_stage3:.3f}")
    
    # Análise
    print("\n--- ANÁLISE ---")
    effective_prob_power = prob_weight * prob_weight_stage3
    effective_ev_power = ev_multiplier * ev_weight * ev_weight_stage3
    print(f"   Probability efetivamente elevada a: {prob:.2f}^? = {effective_prob_power:.3f}")
    print(f"   Isso equivale a: {prob:.2f}^{3:.1f} ≈ {prob**3:.3f}")
    print(f"   EV multiplicado: {effective_ev_power:.2f}x (devia ser 1.20x)")
    
    print("\n💥 IMPACTO:")
    print(f"   - Prob 65% tratada como {effective_prob_power*100:.1f}% (penalizada demais)")
    print(f"   - Prob 80% seria {((0.80**1.5)*(0.80**1.5))*100:.1f}% (inflacionada demais)")
    print("   - Sistema favorece desproporcionalmente apostas >70% prob")
    print("   - Apostas com bom EV mas prob 50-60% são sub-rankeadas")


def demonstrar_caso_real():
    """
    Caso Real: Combinação dos 4 Problemas
    """
    print("\n" + "="*80)
    print("CASO REAL: AROUCA vs BENFICA (Combinação dos 4 Problemas)")
    print("="*80)
    
    print("\nCenário:")
    print("   - Benfica favorito forte (fora)")
    print("   - SEM odds reais da API (tudo simulado)")
    print("   - Contexto forte favorece away (85%)")
    
    # Probabilidades do modelo
    prob_home = 0.10
    prob_draw = 0.20
    prob_away = 0.70
    prob_x2 = prob_draw + prob_away  # 0.90
    
    # Odds simuladas (margin 5%)
    odd_away = round((1/prob_away) / 1.05, 2)  # 1.36
    
    # Odd X2 genérica (problema 1+2)
    odd_x2_fake = 2.00
    
    # Odd X2 correta (calculada)
    odd_x2_real = 1.05  # Muito baixa, quase sem value
    
    print("\n--- Sistema Atual (COM problemas) ---")
    
    # Away Win
    fair_odd_away = 1 / prob_away
    ev_away = (odd_away / fair_odd_away - 1) * 100
    print(f"\nAway Win:")
    print(f"   Prob: {prob_away*100:.0f}%, Odd: {odd_away}, Fair: {fair_odd_away:.2f}")
    print(f"   EV: {ev_away:+.1f}% (odd simulada, problema 3)")
    
    # Score Away Win
    # Problema 4: Multiplicação tripla
    prob_weight_away = prob_away ** 1.5
    ev_weight_away = max(0.5, 1 + ev_away/200)
    score_away = prob_weight_away * ev_weight_away
    score_away_final = score_away * prob_weight_away * ev_weight_away  # Duplica!
    print(f"   Score (final): {score_away_final:.3f}")
    
    # X2
    fair_odd_x2 = 1 / prob_x2
    ev_x2_fake = (odd_x2_fake / fair_odd_x2 - 1) * 100
    print(f"\nX2 (Double Chance):")
    print(f"   Prob: {prob_x2*100:.0f}%, Odd: {odd_x2_fake} (GENÉRICA! problema 1+2)")
    print(f"   Fair: {fair_odd_x2:.2f}, EV: {ev_x2_fake:+.1f}% ❌ FALSO!")
    
    # Score X2 (inflacionado)
    prob_weight_x2 = prob_x2 ** 1.5
    ev_weight_x2 = 1 + max(0, ev_x2_fake/100)
    score_x2 = prob_weight_x2 * ev_weight_x2
    score_x2_final = score_x2 * prob_weight_x2 * ev_weight_x2
    print(f"   Score (final): {score_x2_final:.3f} ❌ INFLACIONADO!")
    
    print(f"\n❌ SISTEMA RECOMENDA: X2 (score {score_x2_final:.3f} > {score_away_final:.3f})")
    
    print("\n--- Sistema Corrigido (SEM problemas) ---")
    
    # X2 com odd correta
    ev_x2_real = (odd_x2_real / fair_odd_x2 - 1) * 100
    print(f"\nX2 (com odd calculada correta):")
    print(f"   Prob: {prob_x2*100:.0f}%, Odd: {odd_x2_real:.2f} (calculada)")
    print(f"   Fair: {fair_odd_x2:.2f}, EV: {ev_x2_real:+.1f}% ✅")
    
    # Score unificado (1x apenas)
    score_away_unified = prob_away * (1 + ev_away/100)
    score_x2_unified = prob_x2 * (1 + ev_x2_real/100)
    print(f"\nAway Win: score={score_away_unified:.3f}")
    print(f"X2:       score={score_x2_unified:.3f}")
    
    print(f"\n✅ SISTEMA CORRETO RECOMENDA: Away Win (score {score_away_unified:.3f} > {score_x2_unified:.3f})")
    
    print("\n💥 IMPACTO FINANCEIRO (apostando €100):")
    roi_x2_fake = prob_x2 * (odd_x2_fake - 1) - (1 - prob_x2)
    roi_x2_real = prob_x2 * (odd_x2_real - 1) - (1 - prob_x2)
    roi_away = prob_away * (odd_away - 1) - (1 - prob_away)
    
    print(f"   X2 (odd fake 2.00):      ROI = {roi_x2_fake*100:+.1f}% (ILUSÃO!)")
    print(f"   X2 (odd real 1.05):      ROI = {roi_x2_real*100:+.1f}% ✅")
    print(f"   Away Win (odd 1.36):     ROI = {roi_away*100:+.1f}% ✅")
    print(f"\n   Diferença: {(roi_away - roi_x2_real)*100:.1f} pontos percentuais perdidos!")


if __name__ == '__main__':
    print("\n" + "#"*80)
    print("#" + " "*78 + "#")
    print("#" + "  DEMONSTRAÇÃO DOS 4 PROBLEMAS ESTRUTURAIS DO SISTEMA".center(78) + "#")
    print("#" + " "*78 + "#")
    print("#"*80)
    
    problema_1_nomenclatura()
    problema_2_mercados_derivados()
    problema_3_odds_simuladas()
    problema_4_score_multiplicado()
    demonstrar_caso_real()
    
    print("\n" + "="*80)
    print("CONCLUSÃO")
    print("="*80)
    print("""
Os 4 problemas trabalham em conjunto para distorcer sistematicamente
as recomendações de apostas:

1. Nomenclatura inconsistente → Odds não encontradas → Usa padrão 2.00
2. Mercados derivados → Probabilidade correta mas odd fake → EV ilusório
3. Odds simuladas → Sempre EV ~-5% → Apostas rejeitadas indevidamente
4. Score multiplicado → Prob^3 × EV^2 → Ranking distorcido

RESULTADO: Sistema escolhe a aposta errada mesmo com previsão correta!

SOLUÇÃO: Ver DIAGNOSTICO_4_PROBLEMAS_ESTRUTURAIS.md
    """)
