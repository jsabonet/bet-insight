"""
Análise: Barcelona vs Real Madrid
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from apps.matches.models import Match

print("\n" + "="*80)
print("ANALISE: Barcelona vs Real Madrid")
print("="*80)

# Buscar ou criar partida
try:
    match = Match.objects.get(api_football_id=1503770)
    print(f"\nPartida encontrada: {match.home_team} vs {match.away_team}")
except Match.DoesNotExist:
    print("\nCriando partida no banco...")
    match = Match.objects.create(
        api_football_id=1503770,
        home_team="Barcelona",
        away_team="Real Madrid",
        league_id=140,  # La Liga
        match_date="2026-01-11"
    )
    print(f"Partida criada: {match.home_team} vs {match.away_team}")

print(f"Fixture ID: {match.api_football_id}")
print("\nExecutando analise hibrida...")

orchestrator = HybridAnalysisOrchestrator()
result = orchestrator.run(match)

if result:
    consensus = result.get('consensus', {})
    poisson = result.get('poisson', {})
    fair_odds = result.get('fair_odds', {})
    market_odds = result.get('market_odds', {})
    recommendation = result.get('recommendation', {})
    
    print("\n" + "="*80)
    print("PROBABILIDADES DO MODELO")
    print("="*80)
    print(f"\nCONSENSO (Poisson 60% + Logistica 40%):")
    print(f"  Casa (Barcelona): {consensus.get('home_win', 0)*100:.1f}%")
    print(f"  Empate:           {consensus.get('draw', 0)*100:.1f}%")
    print(f"  Fora (Real):      {consensus.get('away_win', 0)*100:.1f}%")
    
    print(f"\nEXPECTED GOALS (xG):")
    xg = poisson.get('expected_goals', {})
    print(f"  Barcelona: {xg.get('home', 0):.2f} gols")
    print(f"  Real Madrid: {xg.get('away', 0):.2f} gols")
    print(f"  Total: {xg.get('home', 0) + xg.get('away', 0):.2f} gols")
    
    print(f"\nPLACAR MAIS PROVAVEL:")
    print(f"  {poisson.get('most_likely_score', 'N/A')}")
    
    print(f"\nODDS JUSTAS (calculadas pelo modelo):")
    print(f"  Casa (Barcelona): {fair_odds.get('home_win', 0):.2f}")
    print(f"  Empate:           {fair_odds.get('draw', 0):.2f}")
    print(f"  Fora (Real):      {fair_odds.get('away_win', 0):.2f}")
    print(f"  Over 2.5:         {fair_odds.get('over_2_5', 0):.2f}")
    print(f"  BTTS:             {fair_odds.get('btts', 0):.2f}")
    
    if market_odds:
        print(f"\nODDS DO MERCADO (1xBet):")
        print(f"  Casa (Barcelona): {market_odds.get('home_win', 'N/A')}")
        print(f"  Empate:           {market_odds.get('draw', 'N/A')}")
        print(f"  Fora (Real):      {market_odds.get('away_win', 'N/A')}")
        print(f"  Over 2.5:         {market_odds.get('over_2_5', 'N/A')}")
        print(f"  BTTS:             {market_odds.get('btts', 'N/A')}")
    
    print("\n" + "="*80)
    print("RECOMENDACAO")
    print("="*80)
    print(f"\nMercado: {recommendation.get('market_display', 'N/A')}")
    print(f"Aposta: {recommendation.get('pick', 'N/A')}")
    print(f"Probabilidade: {recommendation.get('probability', 0)*100:.1f}%")
    print(f"Odd Mercado: {recommendation.get('odd', 'N/A')}")
    print(f"Odd Justa: {recommendation.get('fair_odd', 'N/A')}")
    print(f"Expected Value: {recommendation.get('expected_value', 0)*100:+.1f}%")
    
    confidence = result.get('confidence', {})
    print(f"\nConfianca: {'⭐' * confidence.get('stars', 0)} ({confidence.get('stars', 0)}/5)")
    print(f"Risco: {result.get('risk', 'N/A').upper()}")
    
    value_bets = result.get('value_bets', [])
    if value_bets:
        print(f"\n" + "="*80)
        print(f"VALUE BETS IDENTIFICADAS ({len(value_bets)})")
        print("="*80)
        for i, vb in enumerate(value_bets[:3], 1):
            print(f"\n{i}. {vb.get('market_display', 'N/A')}")
            print(f"   Odd Justa: {vb.get('fair_odd', 0):.2f}")
            print(f"   Odd Mercado: {vb.get('market_odd', 0):.2f}")
            print(f"   Value: {vb.get('value', 0)*100:+.1f}%")
            print(f"   Probabilidade: {vb.get('probability', 0)*100:.1f}%")
else:
    print("\n[ERRO] Falha ao executar analise")

print("\n" + "="*80)
