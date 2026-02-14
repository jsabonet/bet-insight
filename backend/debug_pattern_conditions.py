"""
Debug: Por que padrão não está sendo detectado na análise completa?
"""
import os
import django
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.context_analyzer import ContextAnalyzer

def main():
    match_id = 1379220
    
    # Buscar e enriquecer
    api = APIFootballService()
    enricher = MatchDataEnricher()
    engineer = FeatureEngineer()
    
    match_data = {'api_id': match_id}
    enriched = enricher.enrich(match_data)
    features = engineer.engineer_all_features(enriched)
    
    print("\n" + "="*80)
    print("DEBUG: Features relevantes")
    print("="*80 + "\n")
    
    strength = features.get('strength', {})
    motivation = features.get('motivation', {})
    market = features.get('market', {})
    
    print("STRENGTH:")
    print(f"  home_defense_strength: {strength.get('home_defense_strength', 'N/A')}")
    print(f"  away_defense_strength: {strength.get('away_defense_strength', 'N/A')}")
    print(f"  strength_differential: {strength.get('strength_differential', 'N/A')}")
    
    print("\nMOTIVATION:")
    print(f"  home_motivation: {motivation.get('home_motivation', 'N/A')}")
    print(f"  away_motivation: {motivation.get('away_motivation', 'N/A')}")
    
    print("\nMARKET:")
    print(f"  odds_home: {market.get('odds_home', 'N/A')}")
    print(f"  odds_away: {market.get('odds_away', 'N/A')}")
    
    print("\n" + "="*80)
    print("CONDICOES DO PADRAO:")
    print("="*80 + "\n")
    
    odds_home = market.get('odds_home', 3.0)
    odds_away = market.get('odds_away', 3.0)
    favorite_is_home = odds_home < odds_away
    
    print(f"1. Favorito é home? {favorite_is_home} (home={odds_home:.2f}, away={odds_away:.2f})")
    
    if favorite_is_home:
        print("   ❌ PADRÃO REQUER: Favorito fora (underdog casa)")
    else:
        print("   ✅ Favorito é fora")
    
    favorite_motivation = motivation.get('home_motivation', 5.0) if favorite_is_home else motivation.get('away_motivation', 5.0)
    print(f"\n2. Favorito motivação: {favorite_motivation:.1f}/10 (requer >= 9.0)")
    if favorite_motivation >= 9.0:
        print("   ✅ Motivação suficiente")
    else:
        print("   ❌ Motivação insuficiente")
    
    favorite_odds = odds_home if favorite_is_home else odds_away
    print(f"\n3. Favorito odd: {favorite_odds:.2f} (requer < 2.5)")
    if favorite_odds < 2.5:
        print("   ✅ Odd válida")
    else:
        print("   ❌ Odd muito alta")
    
    underdog_defense = strength.get('away_defense_strength', 1.5) if favorite_is_home else strength.get('home_defense_strength', 1.5)
    print(f"\n4. Underdog defesa: {underdog_defense:.2f} (requer < 1.3)")
    if underdog_defense < 1.3:
        print("   ✅ Defesa sólida")
    else:
        print("   ❌ Defesa não suficientemente forte")
    
    favorite_defense = strength.get('home_defense_strength', 1.5) if favorite_is_home else strength.get('away_defense_strength', 1.5)
    print(f"\n5. Favorito defesa: {favorite_defense:.2f} (requer > 1.8)")
    if favorite_defense > 1.8:
        print("   ✅ Defesa vulnerável")
    else:
        print("   ❌ Defesa não vulnerável")
    
    strength_diff = abs(strength.get('strength_differential', 0.0))
    print(f"\n6. Força diferencial: {strength_diff:.2f} (requer < 0.65)")
    if strength_diff < 0.65:
        print("   ✅ Força moderada")
    else:
        print("   ❌ Diferença muito grande")
    
    print("\n" + "="*80)
    print("CONCLUSÃO:")
    print("="*80 + "\n")
    
    all_conditions = [
        not favorite_is_home,
        favorite_motivation >= 9.0,
        favorite_odds < 2.5,
        underdog_defense < 1.3,
        favorite_defense > 1.8,
        strength_diff < 0.65
    ]
    
    if all(all_conditions):
        print("✅ TODAS AS CONDIÇÕES ATENDIDAS - Padrão deveria ser detectado")
    else:
        print("❌ CONDIÇÕES NÃO ATENDIDAS:")
        if not all_conditions[0]:
            print("   - Favorito não está fora (está em casa)")
        if not all_conditions[1]:
            print(f"   - Motivação insuficiente ({favorite_motivation:.1f} < 9.0)")
        if not all_conditions[2]:
            print(f"   - Odd muito alta ({favorite_odds:.2f} >= 2.5)")
        if not all_conditions[3]:
            print(f"   - Defesa underdog não forte ({underdog_defense:.2f} >= 1.3)")
        if not all_conditions[4]:
            print(f"   - Defesa favorito não vulnerável ({favorite_defense:.2f} <= 1.8)")
        if not all_conditions[5]:
            print(f"   - Força diferencial muito grande ({strength_diff:.2f} >= 0.65)")

if __name__ == '__main__':
    main()
