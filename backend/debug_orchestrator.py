"""
Debug do Orchestrator - Comparar predictions do ensemble isolado vs orchestrator completo
"""
import os
import sys
import django
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from apps.analysis.services.ml_integration import ModelEnsembleML
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.matches.models import Match, League, Team
from datetime import datetime

print("="*80)
print("DEBUG: Orchestrator vs Ensemble isolado")
print("="*80)

# Carregar dataset
dataset_path = Path(__file__).parent / 'ml_training' / 'training_dataset.json'
with open(dataset_path, 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# Usar apenas primeira partida para debug
match_data = dataset['data'][0]
fixture_id = match_data['fixture_id']
home_name = match_data['teams']['home']
away_name = match_data['teams']['away']
h_score = match_data['result']['home_goals']
a_score = match_data['result']['away_goals']
league_name = match_data['league']

print(f"\nPartida de teste:")
print(f"  ID: {fixture_id}")
print(f"  Jogo: {home_name} {h_score}-{a_score} {away_name}")
print(f"  Liga: {league_name}")
print(f"  Resultado real: {'HOME' if h_score > a_score else 'DRAW' if h_score == a_score else 'AWAY'}")
print()

# Criar objetos temporários
league, _ = League.objects.get_or_create(
    name=league_name,
    defaults={'country': 'Unknown'}
)

home_team = Team.objects.filter(name=home_name).first()
if not home_team:
    home_team, _ = Team.objects.get_or_create(
        name=home_name,
        defaults={'country': 'Unknown'}
    )

away_team = Team.objects.filter(name=away_name).first()
if not away_team:
    away_team, _ = Team.objects.get_or_create(
        name=away_name,
        defaults={'country': 'Unknown'}
    )

match_date = datetime.fromisoformat(match_data['date'].replace('Z', '+00:00'))

match = Match(
    api_football_id=fixture_id,
    league=league,
    home_team=home_team,
    away_team=away_team,
    match_date=match_date,
    status='FT',
    home_score=h_score,
    away_score=a_score
)

print("="*80)
print("TESTE 1: Ensemble isolado (sem Orchestrator)")
print("="*80)

# Enriquecimento + FE manual
enricher = MatchDataEnricher()
fe = FeatureEngineer()
ensemble = ModelEnsembleML()

enriched = enricher.enrich({'api_id': fixture_id})
features = fe.engineer_all_features(enriched)

# Extrair parâmetros
strength = features.get('strength', {})
weather = features.get('weather', {})
home_strength = strength.get('home_goals_per_game', 1.2)
away_strength = strength.get('away_goals_per_game', 1.2)
weather_impact = weather.get('goal_impact', 0.0)
league_id = league.api_football_id if league else None

# Predict no ensemble
ensemble_result = ensemble.predict(features, home_strength, away_strength, weather_impact, league_id)
ensemble_consensus = ensemble_result.get('consensus', {})

print(f"\nEnsemble Consensus:")
print(f"  HOME: {ensemble_consensus.get('home_win', 0):.4f} ({ensemble_consensus.get('home_win', 0)*100:.2f}%)")
print(f"  DRAW: {ensemble_consensus.get('draw', 0):.4f} ({ensemble_consensus.get('draw', 0)*100:.2f}%)")
print(f"  AWAY: {ensemble_consensus.get('away_win', 0):.4f} ({ensemble_consensus.get('away_win', 0)*100:.2f}%)")

# Determinar previsão
max_outcome = max(ensemble_consensus.items(), key=lambda x: x[1])
ensemble_prediction = max_outcome[0]
print(f"\nEnsemble Prediction: {ensemble_prediction} ({max_outcome[1]*100:.2f}%)")

print("\n" + "="*80)
print("TESTE 2: Orchestrator completo")
print("="*80)

orchestrator = HybridAnalysisOrchestrator()
orchestrator_result = orchestrator.run(match)

orchestrator_consensus = orchestrator_result['analysis_data']['consensus']
print(f"\nOrchestrator Consensus:")
print(f"  HOME: {orchestrator_consensus.get('home_win', 0):.4f} ({orchestrator_consensus.get('home_win', 0)*100:.2f}%)")
print(f"  DRAW: {orchestrator_consensus.get('draw', 0):.4f} ({orchestrator_consensus.get('draw', 0)*100:.2f}%)")
print(f"  AWAY: {orchestrator_consensus.get('away_win', 0):.4f} ({orchestrator_consensus.get('away_win', 0)*100:.2f}%)")

max_outcome_orch = max(orchestrator_consensus.items(), key=lambda x: x[1])
orchestrator_prediction = max_outcome_orch[0]
print(f"\nOrchestrator Prediction: {orchestrator_prediction} ({max_outcome_orch[1]*100:.2f}%)")

print("\n" + "="*80)
print("COMPARAÇÃO")
print("="*80)

# Comparar consensos
print(f"\nConsensus HOME:")
print(f"  Ensemble: {ensemble_consensus.get('home_win', 0):.6f}")
print(f"  Orchestrator: {orchestrator_consensus.get('home_win', 0):.6f}")
print(f"  Diferença: {abs(ensemble_consensus.get('home_win', 0) - orchestrator_consensus.get('home_win', 0)):.6f}")

print(f"\nConsensus DRAW:")
print(f"  Ensemble: {ensemble_consensus.get('draw', 0):.6f}")
print(f"  Orchestrator: {orchestrator_consensus.get('draw', 0):.6f}")
print(f"  Diferença: {abs(ensemble_consensus.get('draw', 0) - orchestrator_consensus.get('draw', 0)):.6f}")

print(f"\nConsensus AWAY:")
print(f"  Ensemble: {ensemble_consensus.get('away_win', 0):.6f}")
print(f"  Orchestrator: {orchestrator_consensus.get('away_win', 0):.6f}")
print(f"  Diferença: {abs(ensemble_consensus.get('away_win', 0) - orchestrator_consensus.get('away_win', 0)):.6f}")

print(f"\nPrevisões:")
print(f"  Ensemble: {ensemble_prediction}")
print(f"  Orchestrator: {orchestrator_prediction}")
print(f"  Match: {'Consistente ✓' if ensemble_prediction == orchestrator_prediction else '❌ INCONSISTENTE'}")

print("\n" + "="*80)
