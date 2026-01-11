"""
Teste simples: analisa partida e compara com mercado
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

print("\n" + "="*80)
print("TESTE: Última partida com análise disponível")
print("="*80)

orchestrator = HybridAnalysisOrchestrator()

# Buscar partida pelo fixture_id
from apps.matches.models import Match
match = Match.objects.filter(api_football_id__isnull=False).order_by('-match_date').first()
print(f"\nPartida: {match.home_team} vs {match.away_team}")
print(f"Fixture ID: {match.api_football_id}")
result = orchestrator.run(match)

if result:
    consensus = result.get('consensus', {})
    market_odds = result.get('market_odds', {})
    
    print("\nMODELO:")
    print(f"  Casa: {consensus.get('home_win', 0)*100:.1f}%")
    print(f"  Empate: {consensus.get('draw', 0)*100:.1f}%")
    print(f"  Fora: {consensus.get('away_win', 0)*100:.1f}%")
    
    print("\nODDS MERCADO:")
    print(f"  Casa: {market_odds.get('home_win', 'N/A')}")
    print(f"  Empate: {market_odds.get('draw', 'N/A')}")
    print(f"  Fora: {market_odds.get('away_win', 'N/A')}")
    
    if all(k in market_odds for k in ['home_win', 'draw', 'away_win']):
        # Normalizar odds
        p_h = 1/market_odds['home_win']
        p_d = 1/market_odds['draw']
        p_a = 1/market_odds['away_win']
        total = p_h + p_d + p_a
        
        print("\nMERCADO NORMALIZADO:")
        print(f"  Casa: {(p_h/total)*100:.1f}%")
        print(f"  Empate: {(p_d/total)*100:.1f}%")
        print(f"  Fora: {(p_a/total)*100:.1f}%")
        
        erro = abs(consensus['home_win'] - p_h/total) + abs(consensus['draw'] - p_d/total) + abs(consensus['away_win'] - p_a/total)
        print(f"\nERRO: {erro*100:.1f} pontos")
        
        vies_m = consensus['home_win'] - consensus['away_win']
        vies_merc = (p_h/total) - (p_a/total)
        print(f"\nVIES:")
        print(f"  Modelo: {vies_m*100:+.1f}pp")
        print(f"  Mercado: {vies_merc*100:+.1f}pp")
        print(f"  Diff: {(vies_m-vies_merc)*100:+.1f}pp")
        
        if abs(vies_m - vies_merc) < 0.05:
            print("\n=> APROVADO (<5pp)")
        else:
            print("\n=> PRECISA AJUSTE (>=5pp)")
else:
    print("ERRO: Analise falhou")
