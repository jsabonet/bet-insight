"""
Análise COMPLETA - Partida 1388503
Mostra TODOS os mercados com probabilidades
"""

import os
import sys
import django

sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from apps.matches.models import Match

def main():
    print("\n" + "="*100)
    print("ANÁLISE COMPLETA - PARTIDA 1388503")
    print("="*100)
    
    # Buscar partida
    try:
        match = Match.objects.get(api_football_id=1388503)
    except Match.DoesNotExist:
        print("[ERRO] Partida nao encontrada!")
        return
    
    print(f"\n** {match.home_team.name} vs {match.away_team.name}")
    print(f"   Liga: {match.league.name}")
    print(f"   Data: {match.match_date}")
    
    # Analisar
    orchestrator = HybridAnalysisOrchestrator()
    result = orchestrator.run(match, strategy='multiple')
    
    analysis_data = result.get('analysis_data', {})
    
    # INFORMAÇÕES BÁSICAS
    print("\n" + "="*100)
    print("[INFO] INFORMACOES BASICAS")
    print("="*100)
    print(f"\n   xG Casa: {result.get('home_xg', 0):.2f}")
    print(f"   xG Fora: {result.get('away_xg', 0):.2f}")
    print(f"   Total xG: {result.get('home_xg', 0) + result.get('away_xg', 0):.2f}")
    print(f"\n   Home Win: {result.get('home_probability', 0):.1f}%")
    print(f"   Draw: {result.get('draw_probability', 0):.1f}%")
    print(f"   Away Win: {result.get('away_probability', 0):.1f}%")
    
    # POISSON - TODOS OS MERCADOS
    print("\n" + "="*100)
    print("[POISSON] PROBABILIDADES DE TODOS OS MERCADOS")
    print("="*100)
    
    poisson = analysis_data.get('poisson', {})
    poisson_probs = poisson.get('probabilities', {})
    
    print(f"\n   Total de mercados calculados: {len(poisson_probs)}")
    print("\n   " + "-"*96)
    print(f"   {'MERCADO':<35} {'PROBABILIDADE':>20} {'CATEGORIA':>35}")
    print("   " + "-"*96)
    
    # Categorizar e ordenar mercados
    categorias = {
        '1X2': [],
        'Over/Under': [],
        'BTTS': [],
        'Double Chance': [],
        'Team Totals': [],
        'Clean Sheet': [],
        'Margin': [],
        'Outros': []
    }
    
    for market, prob in poisson_probs.items():
        if market in ['home_win', 'draw', 'away_win']:
            categorias['1X2'].append((market, prob))
        elif 'over' in market or 'under' in market:
            if 'home' in market or 'away' in market:
                categorias['Team Totals'].append((market, prob))
            else:
                categorias['Over/Under'].append((market, prob))
        elif 'btts' in market:
            categorias['BTTS'].append((market, prob))
        elif 'clean_sheet' in market:
            categorias['Clean Sheet'].append((market, prob))
        elif 'dc' in market or market in ['1x', '12', 'x2']:
            categorias['Double Chance'].append((market, prob))
        elif 'by_' in market or 'margin' in market:
            categorias['Margin'].append((market, prob))
        else:
            categorias['Outros'].append((market, prob))
    
    # Imprimir por categoria
    for categoria, mercados in categorias.items():
        if mercados:
            print(f"\n   {'─'*96}")
            print(f"   {categoria}")
            print(f"   {'─'*96}")
            for market, prob in sorted(mercados, key=lambda x: x[1], reverse=True):
                print(f"   {market:<35} {prob:>19.1%} {categoria:>35}")
    
    # ML PREDICTIONS (se disponível)
    ml_predictions = analysis_data.get('ml_predictions', {})
    if ml_predictions:
        print("\n" + "="*100)
        print("[ML] MACHINE LEARNING - PREVISOES")
        print("="*100)
        print(f"\n   Total de mercados: {len(ml_predictions)}")
        print("\n   " + "-"*60)
        print(f"   {'MERCADO':<35} {'PROBABILIDADE':>20}")
        print("   " + "-"*60)
        for market, prob in sorted(ml_predictions.items(), key=lambda x: x[1], reverse=True):
            print(f"   {market:<35} {prob:>19.1%}")
    
    # CONSENSUS FINAL
    print("\n" + "="*100)
    print("[CONSENSUS] FINAL (Ensemble: Poisson + ML + Market)")
    print("="*100)
    
    consensus = analysis_data.get('consensus', {})
    print(f"\n   Total de mercados: {len(consensus)}")
    print("\n   " + "-"*60)
    print(f"   {'MERCADO':<35} {'PROBABILIDADE':>20}")
    print("   " + "-"*60)
    for market, prob in sorted(consensus.items(), key=lambda x: x[1], reverse=True):
        print(f"   {market:<35} {prob:>19.1%}")
    
    # TOP 3 SELECIONADAS
    print("\n" + "="*100)
    print("[TOP 3] APOSTAS SELECIONADAS (MODO MULTIPLAS)")
    print("="*100)
    
    top_bets = analysis_data.get('top_bets', [])
    for bet in top_bets:
        print(f"\n   #{bet.get('rank', '?')} {bet.get('market_display', 'Unknown')}")
        print(f"      Probabilidade: {bet.get('probability', 0):.1%}")
        print(f"      Odd: {bet.get('market_odd', 'N/A')}")
        print(f"      EV: {bet.get('expected_value', 0):+.1f}%")
        print(f"      Context Score: {bet.get('context_score', 0):.1%}")
    
    # MERCADOS COM ALTA PROBABILIDADE
    print("\n" + "="*100)
    print("[ALTA PROB] MERCADOS COM ALTA PROBABILIDADE (>=60%) - POISSON")
    print("="*100)
    
    high_prob = [(m, p) for m, p in poisson_probs.items() if p >= 0.60]
    if high_prob:
        print(f"\n   Total: {len(high_prob)} mercados")
        print("\n   " + "-"*60)
        for market, prob in sorted(high_prob, key=lambda x: x[1], reverse=True):
            print(f"   {market:<35} {prob:>19.1%}")
    
    # REASONING
    print("\n" + "="*100)
    print("[REASONING] ANALISE E RACIOCINIO")
    print("="*100)
    print(f"\n{result.get('reasoning', 'N/A')}\n")
    
    print("="*100)
    print("[OK] ANALISE COMPLETA CONCLUIDA")
    print("="*100 + "\n")

if __name__ == '__main__':
    main()
