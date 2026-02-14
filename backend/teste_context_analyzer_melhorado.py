"""
Teste das correções do ContextAnalyzer
Simula cenário Atletico vs Barcelona para verificar se detect a corretamente
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Simular features da partida Atletico vs Barcelona
features_atletico_barcelona = {
    'strength': {
        'home_goals_per_game': 1.70,  # Atletico
        'away_goals_per_game': 2.70,  # Barcelona (maior!)
        'strength_differential': -0.67
    },
    'motivation': {
        'home_motivation': 9.5,  # Copa semifinal em casa!
        'away_motivation': 7.0,  # Mais um jogo
        'motivation_differential': 2.5
    },
    'competition': {
        'is_cup_competition': True,
        'is_knockout_stage': True,
        'competition_name': 'Copa del Rey',
        'knockout_adjustment_factor': 0.85
    },
    'context': {
        'home_rest_days': 7,
        'away_rest_days': 3,  # 72h antes
        'rest_advantage': 4,
        'home_advantage_strength': 0.55
    },
    'injuries_suspensions': {
        'home_injury_impact': 0.2,
        'away_injury_impact': 0.3,
        'injury_impact_differential': -0.1,
        'home_defensive_impact': 0.1,
        'away_defensive_impact': 0.2
    },
    'form': {
        'home_adjusted_form': 8.5,
        'away_adjusted_form': 12.0,
        'adjusted_form_diff': -3.5,
        'home_goals_scored_avg_l5': 1.8,
        'away_goals_scored_avg_l5': 2.5,
        'home_form_l5': 0.6,
        'away_form_l5': 0.8
    },
    'statistics': {
        'btts_percentage_overall': 0.65
    },
    'h2h': {
        'avg_goals_per_match': 2.8
    },
    'elo': {
        'elo_diff': -1.50  # Barcelona melhor ELO
    },
    'match_importance': {
        'is_derby': False
    }
}

print("\n" + "="*80)
print("TESTE: Atletico vs Barcelona - Copa del Rey Semifinal")
print("="*80)
print("\nFEATURES SIMULADAS:")
print(f"  Força: Casa {features_atletico_barcelona['strength']['home_goals_per_game']:.2f} vs Fora {features_atletico_barcelona['strength']['away_goals_per_game']:.2f}")
print(f"  Motivação: Casa {features_atletico_barcelona['motivation']['home_motivation']:.1f} vs Fora {features_atletico_barcelona['motivation']['away_motivation']:.1f}")
print(f"  Descanso: Casa {features_atletico_barcelona['context']['home_rest_days']}d vs Fora {features_atletico_barcelona['context']['away_rest_days']}d")
print(f"  Competição: {features_atletico_barcelona['competition']['competition_name']} (Knockout: {features_atletico_barcelona['competition']['is_knockout_stage']})")

# DEBUG: Ver por que knockout_upset não detecta
print("\nDEBUG Knockout Upset:")
strength_home = min(1.70 / 2.5, 1.0)
strength_away = min(2.70 / 2.5, 1.0)
print(f"  strength_home = {strength_home:.2f}, strength_away = {strength_away:.2f}")
print(f"  strength_diff = {abs(strength_home - strength_away):.2f} (threshold: 0.15)")
print(f"  favorite_is_home = {strength_home > strength_away} (False = Barcelona favorito)")
print(f"  favorite_rest = 3d (threshold < 4)")
print(f"  favorite_motivation = 0.70 (threshold < 0.75)")
print(f"  favorite_injuries = 0.3 (threshold > 0.2)")

vulnerability_score = 0
if 3 < 4:
    vulnerability_score += ((4-3)/4) * 0.35
    print(f"  Fadiga: +{((4-3)/4) * 0.35:.2f}")
if 0.70 < 0.75:
    vulnerability_score += ((0.75-0.70)/0.75) * 0.30
    print(f"  Motivação: +{((0.75-0.70)/0.75) * 0.30:.2f}")
if 0.3 > 0.2:
    vulnerability_score += 0.3 * 0.35
    print(f"  Lesões: +{0.3 * 0.35:.2f}")
print(f"  Total vulnerability: {vulnerability_score:.2f} (threshold: 0.25)")
print()

# Importar ContextAnalyzer
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.context_analyzer import ContextAnalyzer

analyzer = ContextAnalyzer()
result = analyzer.analyze(features_atletico_barcelona)

patterns = result.get('patterns', [])

print("\n" + "="*80)
print(f"PADRÕES DETECTADOS: {len(patterns)}")
print("="*80 + "\n")

if not patterns:
    print("❌ NENHUM PADRÃO DETECTADO (ERRO!)")
else:
    for i, pattern in enumerate(patterns, 1):
        print(f"{i}. {pattern['name'].upper()}")
        print(f"   Confiança: {pattern['confidence']:.0%}")
        print(f"   Mercados: {', '.join(pattern['favorable_markets'][:5])}")
        print(f"   Raciocínio: {pattern['reasoning']}")
        print()

# Verificar se detectou os padrões corretos
expected_patterns = ['knockout_upset', 'asymmetric_fatigue', 'asymmetric_motivation']
detected_names = [p['name'] for p in patterns]

print("\n" + "="*80)
print("VALIDAÇÃO")
print("="*80)

for expected in expected_patterns:
    if expected in detected_names:
        pattern = next(p for p in patterns if p['name'] == expected)
        print(f"OK {expected}: DETECTADO (confianca {pattern['confidence']:.0%})")
    else:
        print(f"FALTA {expected}: NAO DETECTADO")

if 'balanced_tight_game' in detected_names:
    print(f"ERRO balanced_tight_game: DETECTADO INCORRETAMENTE (deveria ser rejeitado em copa)")
else:
    print(f"OK balanced_tight_game: Corretamente NAO detectado")

print("\n" + "="*80)
print("Top Mercados:")
print("="*80)
top_markets = result.get('top_markets', [])
for market in top_markets[:10]:
    print(f"  {market['market']:20s}: {market['context_score']:.0%} (por: {', '.join(market['supporting_patterns'])})")

print("\n")
