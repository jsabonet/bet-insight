"""
Teste para identificar quais mercados agora têm odds (que antes não tinham)
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService

def main():
    print("\n" + "="*80)
    print("TESTE: MERCADOS QUE AGORA TÊM ODDS")
    print("="*80 + "\n")
    
    # Extrair odds da API
    api = APIFootballService()
    odds = api.fetch_odds(1388503)
    
    print(f"Total de odds extraídas: {len(odds)}\n")
    
    # Mercados antigos (que já tinham odds ANTES da expansão)
    mercados_antigos = {
        'home_win', 'draw', 'away_win',
        'over_0.5', 'under_0.5',
        'over_1.5', 'under_1.5', 'over_15', 'under_15',
        'over_2.5', 'under_2.5', 'over_25', 'under_25',
        'over_3.5', 'under_3.5', 'over_35', 'under_35',
        'btts_yes', 'btts_no'
    }
    
    # Separar em antigos e novos
    odds_antigas = {}
    odds_novas = {}
    
    for market, odd_value in odds.items():
        if market in mercados_antigos:
            odds_antigas[market] = odd_value
        else:
            odds_novas[market] = odd_value
    
    # Mostrar resultados
    print("="*80)
    print("MERCADOS ANTIGOS (já existiam)")
    print("="*80)
    print(f"Total: {len(odds_antigas)} mercados\n")
    
    # Agrupar por categoria
    categorias_antigas = {}
    for market in sorted(odds_antigas.keys()):
        if market in ['home_win', 'draw', 'away_win']:
            cat = '1X2'
        elif 'btts' in market:
            cat = 'BTTS'
        elif market.startswith('over_') or market.startswith('under_'):
            cat = 'Over/Under Total'
        else:
            cat = 'Outros'
        
        if cat not in categorias_antigas:
            categorias_antigas[cat] = []
        categorias_antigas[cat].append(market)
    
    for cat, markets in sorted(categorias_antigas.items()):
        print(f"  {cat}: {len(markets)} mercados")
    
    print("\n" + "="*80)
    print("🎉 MERCADOS NOVOS (agora disponíveis)")
    print("="*80)
    print(f"Total: {len(odds_novas)} mercados\n")
    
    if odds_novas:
        # Agrupar por categoria
        categorias_novas = {}
        for market in sorted(odds_novas.keys()):
            if market in ['1x', '12', 'x2']:
                cat = 'Double Chance'
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
                cat = 'Over/Under Extended'
            else:
                cat = 'Outros'
            
            if cat not in categorias_novas:
                categorias_novas[cat] = []
            categorias_novas[cat].append((market, odds_novas[market]))
        
        for cat, markets in sorted(categorias_novas.items()):
            print(f"\n{cat} ({len(markets)} mercados):")
            for market, odd in markets:
                print(f"  ✅ {market:30s} @ {odd:.2f}")
    else:
        print("Nenhum mercado novo encontrado")
    
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)
    print(f"  • Mercados antigos (já tinham odds): {len(mercados_antigos)}")
    print(f"  • Odds antigas extraídas: {len(odds_antigas)}")
    print(f"  • Odds NOVAS extraídas: {len(odds_novas)}")
    print(f"  • Total de odds agora: {len(odds)}")
    print(f"  • Aumento de cobertura: +{len(odds_novas)} mercados ({len(odds_novas)/len(odds)*100:.0f}%)")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
