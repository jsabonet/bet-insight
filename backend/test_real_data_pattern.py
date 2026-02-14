"""
Teste com dados REAIS da API
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
    
    # Enriquecer dados
    enricher = MatchDataEnricher()
    engineer = FeatureEngineer()
    analyzer = ContextAnalyzer()
    
    match_data = {'api_id': match_id}
    enriched = enricher.enrich(match_data)
    features = engineer.engineer_all_features(enriched)
    
    print("\n" + "="*80)
    print("FEATURES EXTRAIDAS (REAIS):")
    print("="*80 + "\n")
    
    # Mostrar features relevantes
    strength = features.get('strength', {})
    motivation = features.get('motivation', {})
    market = features.get('market', {})
    
    print("STRENGTH:")
    for k, v in strength.items():
        if 'defense' in k or 'differential' in k:
            print(f"  {k}: {v}")
    
    print("\nMOTIVATION:")
    for k, v in motivation.items():
        if 'motivation' in k:
            print(f"  {k}: {v} (type: {type(v).__name__})")
    
    print("\nMARKET:")
    print(f"  odds_home: {market.get('odds_home')} (type: {type(market.get('odds_home')).__name__})")
    print(f"  odds_away: {market.get('odds_away')} (type: {type(market.get('odds_away')).__name__})")
    
    # Testar detecção manual
    print("\n" + "="*80)
    print("TESTE MANUAL DAS CONDICOES:")
    print("="*80 + "\n")
    
    home_defense = strength.get('home_defense_strength', 1.5)
    away_defense = strength.get('away_defense_strength', 1.5)
    home_motivation = float(motivation.get('home_motivation', 5.0))
    away_motivation = float(motivation.get('away_motivation', 5.0))
    strength_diff = abs(strength.get('strength_differential', 0.0))
    odds_home = market.get('odds_home', 3.0)
    odds_away = market.get('odds_away', 3.0)
    
    favorite_is_home = odds_home < odds_away
    favorite_motivation = home_motivation if favorite_is_home else away_motivation
    favorite_odds = odds_home if favorite_is_home else odds_away
    favorite_defense = home_defense if favorite_is_home else away_defense
    underdog_defense = away_defense if favorite_is_home else home_defense
    
    print(f"1. Favorito fora? {not favorite_is_home} (requer True)")
    print(f"2. Favorito motivação: {favorite_motivation} >= 9.0? {favorite_motivation >= 9.0}")
    print(f"3. Favorito odd: {favorite_odds} < 2.5? {favorite_odds < 2.5}")
    print(f"4. Underdog defesa: {underdog_defense} < 1.3? {underdog_defense < 1.3}")
    print(f"5. Favorito defesa: {favorite_defense} > 1.8? {favorite_defense > 1.8}")
    print(f"6. Força diff: {strength_diff} < 0.65? {strength_diff < 0.65}")
    
    # Testar analyzer
    print("\n" + "="*80)
    print("RESULTADO DO ANALYZER:")
    print("="*80 + "\n")
    
    result = analyzer.analyze(features)
    patterns = result.get('patterns', [])
    
    if patterns:
        for p in patterns:
            print(f"✅ {p['name']}: {p['confidence']:.0%}")
    else:
        print("❌ Nenhum padrão detectado")

if __name__ == '__main__':
    main()
