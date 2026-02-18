"""
Teste da análise completa com odds expandidas - Leipzig vs Wolfsburg
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

def main():
    print("\n" + "="*80)
    print("TESTE DE ODDS EXPANDIDAS - LEIPZIG VS WOLFSBURG")
    print("="*80 + "\n")
    
    # Buscar partida
    match = Match.objects.get(api_football_id=1388503)
    
    print(f"Partida: {match.home_team.name} vs {match.away_team.name}")
    print(f"Liga: {match.league.name}")
    print(f"Data: {match.match_date}")
    print()
    
    # Executar análise
    print("Executando análise com odds expandidas...")
    print()
    
    orchestrator = HybridAnalysisOrchestrator()
    result = orchestrator.run(match, strategy='multiple')
    
    # Extrair dados
    analysis_data = result.get('analysis_data', {})
    decision_analysis = result.get('decision_analysis', {})
    top_markets = decision_analysis.get('top_markets', [])
    
    # Mostrar odds disponíveis
    print("\n" + "="*80)
    print("ODDS EXTRAÍDAS DA API")
    print("="*80)
    
    odds_dict = analysis_data.get('odds', {})
    if odds_dict:
        print(f"\nTotal: {len(odds_dict)} mercados")
        
        # Contar por categoria
        categorias = {}
        for market in odds_dict.keys():
            if market in ['home_win', 'draw', 'away_win']:
                cat = '1X2'
            elif market in ['1x', '12', 'x2']:
                cat = 'Double Chance'
            elif 'btts' in market:
                cat = 'BTTS' 
            elif market.startswith('home_over_') or market.startswith('home_under_'):
                cat = 'Team Totals - Home'
            elif market.startswith('away_over_') or market.startswith('away_under_'):
                cat = 'Team Totals - Away'
            elif 'clean_sheet' in market:
                cat = 'Clean Sheet'
            elif 'odd' in market or 'even' in market:
                cat = 'Odd/Even'
            elif 'win_to_nil' in market:
                cat = 'Win to Nil'
            elif market.startswith('over_') or market.startswith('under_'):
                cat = 'Over/Under Total'
            else:
                cat = 'Outros'
            
            categorias[cat] = categorias.get(cat, 0) + 1
        
        print("\nPor categoria:")
        for cat, count in sorted(categorias.items()):
            print(f"  • {cat}: {count} mercados")
    
    # Mostrar Top 3
    print("\n" + "="*80)
    print("TOP 3 APOSTAS SELECIONADAS")
    print("="*80)
    
    if top_markets:
        for i, market in enumerate(top_markets, 1):
            market_name = market.get('market_name', '?')
            prob = market.get('probability', 0)
            odd = market.get('market_odd')
            ev = market.get('ev_percentage', 0)
            has_odd = "✅" if odd else "❌"
            
            print(f"\n#{i} - {market_name}")
            print(f"   Probabilidade: {prob:.1%}")
            print(f"   Odd: {odd if odd else 'N/A'} {has_odd}")
            print(f"   EV: {ev:+.1%}")
    else:
        print("\nNenhuma aposta selecionada")
    
    # Analisar mercados com odds agora disponíveis
    print("\n" + "="*80)
    print("MERCADOS QUE AGORA TÊM ODDS (antes não tinham)")
    print("="*80)
    
    # Lista de mercados calculados pelo Poisson
    poisson_probs = analysis_data.get('poisson', {}).get('probabilities', {})
    
    mercados_novos = []
    for market in poisson_probs.keys():
        # Verificar se tem odd disponível
        if odds_dict.get(market):
            # Estes são mercados que agora têm odd
            if market not in ['home_win', 'draw', 'away_win', 'over_2.5', 'under_2.5', 
                              'over_1.5', 'under_1.5', 'over_3.5', 'under_3.5', 
                              'btts_yes', 'btts_no']:
                mercados_novos.append({
                    'market': market,
                    'prob': poisson_probs[market],
                    'odd': odds_dict[market]
                })
    
    if mercados_novos:
        print(f"\nTotal: {len(mercados_novos)} mercados com odds agora disponíveis")
        print()
        
        # Mostrar os mais relevantes (prob > 50%)
        relevantes = [m for m in mercados_novos if m['prob'] > 0.5]
        if relevantes:
            print("Mercados com alta probabilidade (>50%):")
            for m in sorted(relevantes, key=lambda x: x['prob'], reverse=True):
                print(f"  • {m['market']}: {m['prob']:.1%} @ {m['odd']}")
    else:
        print("\nNenhum mercado novo com odd disponível")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
