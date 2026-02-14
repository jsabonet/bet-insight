"""
Debug das probabilidades da partida Brentford vs Arsenal
"""
import os
import sys
import django
import logging

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s %(name)s %(message)s'
)

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

# Buscar partida Brentford vs Arsenal
match = Match.objects.filter(api_football_id=1379220).first()

if not match:
    print("❌ Partida não encontrada!")
    sys.exit(1)

print(f"\n{'='*80}")
print(f"🎯 ANÁLISE DETALHADA - {match.home_team.name} vs {match.away_team.name}")
print(f"{'='*80}\n")

# Executar análise
orchestrator = HybridAnalysisOrchestrator()
result = orchestrator.run(match, strategy='value')

print(f"\n{'='*80}")
print(f"📊 RESULTADO FINAL")
print(f"{'='*80}")
print(f"Predição: {result['prediction']}")
print(f"Confiança: {result['confidence']}/5")
print(f"\nProbabilidades:")
print(f"  Casa: {result['home_probability']}%")
print(f"  Empate: {result['draw_probability']}%")
print(f"  Fora: {result['away_probability']}%")
print(f"\nExpected Goals:")
print(f"  Casa: {result['home_xg']}")
print(f"  Fora: {result['away_xg']}")

# Analisar componentes do ensemble
analysis_data = result.get('analysis_data', {})
consensus = analysis_data.get('consensus', {})
poisson = analysis_data.get('poisson', {})

print(f"\n{'='*80}")
print(f"🔍 ANÁLISE DOS MODELOS")
print(f"{'='*80}")

if consensus:
    print(f"\nConsensus (resultado final):")
    print(f"  Home: {consensus.get('home_win', 0)*100:.1f}%")
    print(f"  Draw: {consensus.get('draw', 0)*100:.1f}%")
    print(f"  Away: {consensus.get('away_win', 0)*100:.1f}%")

if poisson:
    probs = poisson.get('probabilities', {})
    print(f"\nPoisson (modelo estatístico):")
    print(f"  Home: {probs.get('home_win', 0)*100:.1f}%")
    print(f"  Draw: {probs.get('draw', 0)*100:.1f}%")
    print(f"  Away: {probs.get('away_win', 0)*100:.1f}%")
    
    xg = poisson.get('expected_goals', {})
    print(f"\nExpected Goals (Poisson):")
    print(f"  Home xG: {xg.get('home', 0):.2f}")
    print(f"  Away xG: {xg.get('away', 0):.2f}")

# Verificar features de strength
features_summary = analysis_data.get('features_summary', {})
strength = features_summary.get('strength', {})

print(f"\n{'='*80}")
print(f"💪 FEATURES DE FORÇA DOS TIMES")
print(f"{'='*80}")
if strength:
    print(f"\nCasa (Brentford):")
    print(f"  Goals per game: {strength.get('home_goals_per_game', 0):.2f}")
    print(f"  Goals conceded: {strength.get('home_goals_conceded_per_game', 0):.2f}")
    
    print(f"\nFora (Arsenal):")
    print(f"  Goals per game: {strength.get('away_goals_per_game', 0):.2f}")
    print(f"  Goals conceded: {strength.get('away_goals_conceded_per_game', 0):.2f}")

print(f"\n{'='*80}\n")
