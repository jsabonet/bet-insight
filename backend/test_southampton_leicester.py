"""
Teste para investigar probabilidades absurdas
Southampton vs Leicester (ID: 1506263)
Under 2.5: 99.9% e BTTS No: 99.0% são impossíveis!
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from apps.matches.models import Match

def test_match_1506263():
    """Investiga probabilidades absurdas"""
    print("\n" + "="*80)
    print("INVESTIGACAO - Southampton vs Leicester (API ID: 1506263)")
    print("="*80)
    
    # Buscar partida pelo API Football ID
    try:
        match = Match.objects.get(api_football_id=1506263)
        print(f"\nPartida encontrada: {match.home_team.name} vs {match.away_team.name}")
        print(f"   Liga: {match.league.name}")
        print(f"   ID Interno: {match.id}")
    except Match.DoesNotExist:
        print(f"\nPartida com API ID 1506263 nao encontrada no banco!")
        print(f"   Verifique se a partida foi importada do API-Football")
        return
    
    orchestrator = HybridAnalysisOrchestrator()
    
    # Analisar partida
    result = orchestrator.run(match, strategy='multiple')
    
    # Extrair dados
    analysis_data = result.get('analysis_data', {})
    consensus = analysis_data.get('consensus', {})
    poisson = analysis_data.get('poisson', {})
    
    print("\n" + "-"*80)
    print("CONSENSUS (Ensemble normalizado)")
    print("-"*80)
    for market, prob in sorted(consensus.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {market:20s}: {prob:.1%}")
    
    print("\n" + "-"*80)
    print("POISSON (Probabilidades base)")
    print("-"*80)
    poisson_probs = poisson.get('probabilities', {})
    for market, prob in sorted(poisson_probs.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {market:20s}: {prob:.1%}")
    
    print("\n" + "-"*80)
    print("MERCADOS SUSPEITOS (>95%)")
    print("-"*80)
    
    # Verificar consensus
    suspicious_consensus = [(m, p) for m, p in consensus.items() if p > 0.95]
    if suspicious_consensus:
        print("\n   CONSENSUS (>>95%):")
        for market, prob in sorted(suspicious_consensus, key=lambda x: x[1], reverse=True):
            print(f"      ALERTA {market}: {prob:.3%}")
    else:
        print("\n   OK - Nenhum mercado no consensus com >95%")
    
    # Verificar poisson
    suspicious_poisson = [(m, p) for m, p in poisson_probs.items() if p > 0.95]
    if suspicious_poisson:
        print("\n   POISSON (>>95%):")
        for market, prob in sorted(suspicious_poisson, key=lambda x: x[1], reverse=True):
            print(f"      ALERTA {market}: {prob:.3%}")
    else:
        print("\n   OK - Nenhum mercado no Poisson com >95%")
    
    print("\n" + "-"*80)
    print("CONTEXT SCORE E REASONING TEXT")
    print("-"*80)
    
    # Verificar context_score e reasoning dos Top 3
    top_markets = result.get('top_markets', [])
    if top_markets:
        print(f"\n   Top 3 Mercados:")
        for i, market in enumerate(top_markets[:3], 1):
            prob = market.get('probability', 0)
            context = market.get('context_score', 1.0)
            reasoning = market.get('reasoning', 'N/A')
            market_type = market.get('market_type', 'N/A')
            
            print(f"\n   {i}. {market_type}")
            print(f"      Probabilidade: {prob:.1%}")
            print(f"      Context Score: {context:.3f}")
            print(f"      Reasoning: {reasoning[:100]}...")
            
            if context >= 0.99:
                print(f"      ✅ SEM influência contextual (context=1.0)")
            elif context >= 0.75:
                print(f"      ⚠️ COM influência contextual forte (context={context:.1%})")
            else:
                print(f"      ℹ️ Contexto fraco neutralizado")
    else:
        print("\n   ⚠️ Nenhum mercado selecionado!")
    
    print("\n" + "-"*80)
    print("DIAGNOSTICO")
    print("-"*80)
    
    # Verificar xG esperado
    home_xg = result.get('home_xg', 0)
    away_xg = result.get('away_xg', 0)
    
    print(f"\n   xG Esperado:")
    print(f"      Southampton: {home_xg:.2f}")
    print(f"      Leicester: {away_xg:.2f}")
    print(f"      Total: {home_xg + away_xg:.2f}")
    
    # Calcular probabilidade teórica de Under 2.5
    total_goals = home_xg + away_xg
    
    # Com Poisson: P(X <= 2) para média = total_goals
    from math import exp, factorial
    poisson_under_2_5 = sum(
        (total_goals**k * exp(-total_goals)) / factorial(k)
        for k in range(3)  # 0, 1, 2 gols
    )
    
    print(f"\n   Probabilidade TEÓRICA Under 2.5 (Poisson puro):")
    print(f"      Com xG total {total_goals:.2f}: {poisson_under_2_5:.1%}")
    
    if poisson_under_2_5 > 0.95:
        print(f"\n   ALERTA xG MUITO BAIXO! Total {total_goals:.2f} gera Under 2.5 > 95%")
        print(f"      Verificar feature_engineer se esta calculando xG corretamente")
    
    # Verificar probabilidades 1X2
    home_prob = result.get('home_probability', 0) / 100
    draw_prob = result.get('draw_probability', 0) / 100
    away_prob = result.get('away_probability', 0) / 100
    
    print(f"\n   1X2 (deve somar ~100%):")
    print(f"      Home: {home_prob:.1%}")
    print(f"      Draw: {draw_prob:.1%}")
    print(f"      Away: {away_prob:.1%}")
    print(f"      TOTAL: {(home_prob + draw_prob + away_prob):.1%}")
    
    if abs((home_prob + draw_prob + away_prob) - 1.0) > 0.05:
        print(f"      ALERTA 1X2 nao soma 100%! Normalizacao com erro!")
    
    # Verificar top bets
    print("\n" + "-"*80)
    print("TOP BETS SELECIONADAS")
    print("-"*80)
    top_bets = analysis_data.get('top_bets', [])
    for bet in top_bets:
        print(f"\n   #{bet.get('rank', '?')} {bet.get('market_display', 'Unknown')}")
        print(f"      Probabilidade: {bet.get('probability', 0):.1%}")
        print(f"      Contexto: {bet.get('context_score', 0):.1%}")
        print(f"      Odd: {bet.get('market_odd', 0)}")
        print(f"      Reasoning: {bet.get('reasoning', 'N/A')}")
    
    print("\n" + "="*80)
    print("Investigacao completa")
    print("="*80 + "\n")

if __name__ == '__main__':
    test_match_1506263()
