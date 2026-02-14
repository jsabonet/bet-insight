"""Teste rapido ContextAnalyzer"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.context_analyzer import ContextAnalyzer

# Cenario 1: Copa eliminatoria com favorito vulneravel
print("\n" + "="*60)
print("TESTE 1: Copa Eliminatoria - Favorito Vulneravel")
print("="*60)

features_copa = {
    'strength': {'home_goals_per_game': 1.5, 'away_goals_per_game': 2.5},
    'motivation': {'home_motivation': 9.0, 'away_motivation': 7.0},
    'competition': {'is_cup_competition': True, 'is_knockout_stage': True},
    'context': {'home_rest_days': 7, 'away_rest_days': 3, 'home_advantage_strength': 0.55},
    'injuries_suspensions': {'home_injury_impact': 0.2, 'away_injury_impact': 0.3},
    'form': {'home_form_l5': 0.6, 'away_form_l5': 0.8, 'home_goals_scored_avg_l5': 1.5, 'away_goals_scored_avg_l5': 2.0},
    'statistics': {'btts_percentage_overall': 0.6},
    'h2h': {'avg_goals_per_match': 2.5},
    'elo': {'elo_diff': -1.2},
    'match_importance': {'is_derby': False}
}

result = ContextAnalyzer().analyze(features_copa)
for p in result['patterns']:
    print(f"\n{p['name']:20s}: {p['confidence']:.0%}")
    print(f"  {p['reasoning']}")

print(f"\nTop 3 mercados:")
for m in result['top_markets'][:3]:
    print(f"  {m['market']:20s}: {m['context_score']:.0%}")

# Cenario 2: Jogo equilibrado normal
print("\n" + "="*60)
print("TESTE 2: Jogo Equilibrado (Liga Regular)")
print("="*60)

features_equilibrado = {
    'strength': {'home_goals_per_game': 1.5, 'away_goals_per_game': 1.6},
    'motivation': {'home_motivation': 5.5, 'away_motivation': 5.0},
    'competition': {'is_cup_competition': False, 'is_knockout_stage': False},
    'context': {'home_rest_days': 5, 'away_rest_days': 6, 'home_advantage_strength': 0.55},
    'injuries_suspensions': {'home_injury_impact': 0.1, 'away_injury_impact': 0.1},
    'form': {'home_form_l5': 0.5, 'away_form_l5': 0.5, 'home_goals_scored_avg_l5': 1.2, 'away_goals_scored_avg_l5': 1.3},
    'statistics': {'btts_percentage_overall': 0.5},
    'h2h': {'avg_goals_per_match': 2.0},
    'elo': {'elo_diff': 0.1},
    'match_importance': {'is_derby': False}
}

result2 = ContextAnalyzer().analyze(features_equilibrado)
for p in result2['patterns']:
    print(f"\n{p['name']:20s}: {p['confidence']:.0%}")
    print(f"  {p['reasoning']}")

print(f"\nTop 3 mercados:")
for m in result2['top_markets'][:3]:
    print(f"  {m['market']:20s}: {m['context_score']:.0%}")

# Cenario 3: Fadiga assimetrica
print("\n" + "="*60)
print("TESTE 3: Fadiga Assimetrica")
print("="*60)

features_fadiga = {
    'strength': {'home_goals_per_game': 1.8, 'away_goals_per_game': 1.7},
    'motivation': {'home_motivation': 6.0, 'away_motivation': 6.5},
    'competition': {'is_cup_competition': False, 'is_knockout_stage': False},
    'context': {'home_rest_days': 8, 'away_rest_days': 2, 'home_advantage_strength': 0.55},
    'injuries_suspensions': {'home_injury_impact': 0.1, 'away_injury_impact': 0.2},
    'form': {'home_form_l5': 0.6, 'away_form_l5': 0.6, 'home_goals_scored_avg_l5': 1.5, 'away_goals_scored_avg_l5': 1.5},
    'statistics': {'btts_percentage_overall': 0.5},
    'h2h': {'avg_goals_per_match': 2.3},
    'elo': {'elo_diff': 0.05},
    'match_importance': {'is_derby': False}
}

result3 = ContextAnalyzer().analyze(features_fadiga)
for p in result3['patterns']:
    print(f"\n{p['name']:20s}: {p['confidence']:.0%}")
    print(f"  {p['reasoning']}")

print(f"\nTop 3 mercados:")
for m in result3['top_markets'][:3]:
    print(f"  {m['market']:20s}: {m['context_score']:.0%}")

print("\n" + "="*60)
print("TESTES CONCLUIDOS")
print("="*60 + "\n")
