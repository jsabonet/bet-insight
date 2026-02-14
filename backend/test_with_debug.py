"""
Adicionar logging temporário para debug
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

# Patch the ContextAnalyzer to add debugging
from apps.analysis.services import context_analyzer
original_detect = context_analyzer.ContextAnalyzer._detect_motivated_favorite_vs_defensive_wall

def debug_detect(self, features):
    print("\n🔍 DEBUG: _detect_motivated_favorite_vs_defensive_wall CHAMADO")
    
    strength = features.get('strength', {})
    motivation = features.get('motivation', {})
    market = features.get('market', {})
    
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
    
    print(f"  favorite_is_home: {favorite_is_home}")
    print(f"  favorite_motivation: {favorite_motivation} (>= 9.0? {favorite_motivation >= 9.0})")
    print(f"  favorite_odds: {favorite_odds} (< 2.5? {favorite_odds < 2.5})")
    print(f"  check 1: {favorite_motivation >= 9.0 and favorite_odds < 2.5}")
    
    if favorite_motivation < 9.0 or favorite_odds >= 2.5:
        print("  ❌ RETORNOU None na condição 1")
        return None
    
    print(f"  underdog_defense: {underdog_defense} (< 1.3? {underdog_defense < 1.3})")
    if underdog_defense >= 1.3:
        print("  ❌ RETORNOU None na condição 2")
        return None
    
    print(f"  favorite_defense: {favorite_defense} (> 1.8? {favorite_defense > 1.8})")
    if favorite_defense <= 1.8:
        print("  ❌ RETORNOU None na condição 3")
        return None
    
    print(f"  strength_diff: {strength_diff} (< 0.65? {strength_diff < 0.65})")
    if strength_diff >= 0.65:
        print("  ❌ RETORNOU None na condição 4")
        return None
    
    if favorite_is_home:
        print("  ❌ RETORNOU None na condição 5 (favorito casa)")
        return None
    
    print("  ✅ TODAS AS CONDIÇÕES PASSARAM - Chamando original")
    return original_detect(self, features)

context_analyzer.ContextAnalyzer._detect_motivated_favorite_vs_defensive_wall = debug_detect

# Agora testar
from apps.analysis.services.context_analyzer import ContextAnalyzer

def main():
    match_id = 1379220
    
    enricher = MatchDataEnricher()
    engineer = FeatureEngineer()
    analyzer = ContextAnalyzer()
    
    match_data = {'api_id': match_id}
    enriched = enricher.enrich(match_data)
    features = engineer.engineer_all_features(enriched)
    
    result = analyzer.analyze(features)
    patterns = result.get('patterns', [])
    
    print("\n" + "="*80)
    if patterns:
        for p in patterns:
            print(f"✅ PADRÃO: {p['name']}")
    else:
        print("❌ Nenhum padrão detectado")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
