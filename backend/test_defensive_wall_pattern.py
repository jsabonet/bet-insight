"""
Teste do novo padrão motivated_favorite_vs_defensive_wall
Partida: Brentford vs Arsenal (1379220)
"""
import os
import django
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.context_analyzer import ContextAnalyzer

def test_brentford_arsenal():
    """
    Brentford (casa) vs Arsenal (fora)
    - Arsenal: Líder (1º), motivação 10/10, odd 1.66
    - Arsenal defesa: 2.14 (vulnerável)
    - Brentford defesa: 1.07 (sólida)
    - Brentford: 7º lugar, motivação 7.0
    - Força diferencial: 0.40
    """
    features = {
        'strength': {
            'home_goals_per_game': 1.60,
            'away_goals_per_game': 2.00,
            'home_defense_strength': 1.07,  # Brentford defesa sólida
            'away_defense_strength': 2.14,   # Arsenal vulnerável
            'strength_differential': 0.40
        },
        'motivation': {
            'home_motivation': 7.0,  # Brentford mid-table
            'away_motivation': 10.0,  # Arsenal líder
            'motivation_differential': 3.0
        },
        'market': {
            'odds_home': 5.00,
            'odds_draw': 3.75,
            'odds_away': 1.66,  # Arsenal favorito
            'market_home_prob': 0.187,
            'market_away_prob': 0.563
        },
        'context': {
            'home_rest_days': 7,
            'away_rest_days': 7
        },
        'competition': {
            'is_cup_competition': False,
            'is_knockout': False
        },
        'form': {
            'home_adjusted_form': 1.50,
            'away_adjusted_form': 1.50
        },
        'injuries_suspensions': {
            'home_injury_impact': 0.0,
            'away_injury_impact': 0.0
        }
    }
    
    print("\n" + "="*80)
    print("TESTE: motivated_favorite_vs_defensive_wall")
    print("="*80 + "\n")
    
    print("FEATURES:")
    print(f"  Brentford (casa) defesa: {features['strength']['home_defense_strength']:.2f}")
    print(f"  Arsenal (fora) defesa: {features['strength']['away_defense_strength']:.2f}")
    print(f"  Arsenal motivação: {features['motivation']['away_motivation']:.1f}/10")
    print(f"  Arsenal odd: {features['market']['odds_away']:.2f}")
    print(f"  Força diferencial: {features['strength']['strength_differential']:.2f}")
    
    analyzer = ContextAnalyzer()
    result = analyzer.analyze(features)
    
    patterns = result.get('patterns', [])
    
    print("\n" + "-"*80)
    print(f"PADRÕES DETECTADOS: {len(patterns)}")
    print("-"*80 + "\n")
    
    if patterns:
        for i, p in enumerate(patterns, 1):
            print(f"{i}. {p['name'].upper()}")
            print(f"   Confiança: {p['confidence']:.0%}")
            print(f"   Mercados: {', '.join(p['favorable_markets'][:5])}")
            print(f"   Raciocínio: {p['reasoning']}")
            print()
    else:
        print("❌ Nenhum padrão detectado\n")
    
    # Top mercados
    top_markets = result.get('top_markets', [])[:10]
    print("-"*80)
    print("TOP 10 MERCADOS:")
    print("-"*80 + "\n")
    for m in top_markets:
        patterns_str = ', '.join(m['supporting_patterns'])
        print(f"  {m['market']:20s}: {m['context_score']:>3.0%} ({patterns_str})")
    
    print("\n" + "="*80)
    print("RESULTADO REAL: Brentford 1-1 Arsenal")
    print("="*80 + "\n")
    
    print("✅ BTTS: GREEN (ambos marcaram)")
    print("✅ Under 3.5: GREEN (2 gols)")
    print("✅ Under 2.5: GREEN (2 gols)")
    print("✅ Draw: GREEN (empate 1-1)")
    print("❌ Over 2.5: RED (apenas 2 gols)")
    print("\n")

if __name__ == '__main__':
    test_brentford_arsenal()
