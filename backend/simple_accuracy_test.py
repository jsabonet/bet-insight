"""
Teste de acertividade sem salvar no banco - Analise direta da API
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.statistical_models import ModelEnsemble
import numpy as np

def get_actual(home, away):
    if home > away: return [1, 0, 0]
    elif home < away: return [0, 0, 1]
    else: return [0, 1, 0]

def predict(probs):
    vals = [probs.get('home_win', 0), probs.get('draw', 0), probs.get('away_win', 0)]
    idx = vals.index(max(vals))
    return ['home_win', 'draw', 'away_win'][idx]

def correct(pred, actual):
    mapping = {'home_win': [1,0,0], 'draw': [0,1,0], 'away_win': [0,0,1]}
    return mapping[pred] == actual

def brier(probs, actual):
    p = [probs.get('home_win', 0), probs.get('draw', 0), probs.get('away_win', 0)]
    return np.mean([(p[i] - actual[i])**2 for i in range(3)])

print("\n" + "="*70)
print("TESTE DE ACERTIVIDADE - ANALISE DIRETA")
print("="*70 + "\n")

api = FootballAPIService()
enricher = MatchDataEnricher()
fe = FeatureEngineer()
ensemble = ModelEnsemble()

# Buscar partidas de ontem (mais provavel ter finalizadas)
from datetime import datetime, timedelta
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

print(f"Buscando partidas de {yesterday}...")
result = api.get_fixtures_by_date(yesterday)

if not result.get('success'):
    print("ERRO ao buscar partidas")
    sys.exit(1)

finished = [f for f in result['fixtures'] if f['fixture']['status']['short'] == 'FT']
print(f"Encontradas {len(finished)} partidas finalizadas\n")

if len(finished) == 0:
    print("Sem partidas finalizadas. Tentando hoje...")
    result = api.get_fixtures_by_date()
    finished = [f for f in result['fixtures'] if f['fixture']['status']['short'] == 'FT']
    print(f"Hoje: {len(finished)} partidas finalizadas\n")

if len(finished) == 0:
    print("Nenhuma partida disponivel para teste")
    sys.exit(0)

# Testar primeiras 10
finished = finished[:10]

results = []
print("Analisando...\n")
print("-" * 70)

for i, f in enumerate(finished, 1):
    fid = f['fixture']['id']
    home = f['teams']['home']['name']
    away = f['teams']['away']['name']
    h_score = f['goals']['home']
    a_score = f['goals']['away']
    
    print(f"[{i}/{len(finished)}] {home} {h_score}-{a_score} {away}...", end=" ")
    
    try:
        # Enriquecer
        enriched = enricher.enrich({'api_id': fid})
        
        # Features
        features = fe.engineer_all_features(enriched)
        
        # Modelo
        strength = features.get('strength', {})
        weather = features.get('weather', {})
        h_str = strength.get('home_goals_per_game', 1.2)
        a_str = strength.get('away_goals_per_game', 1.2)
        w_imp = weather.get('goal_impact', 0.0)
        
        model_result = ensemble.predict(features, h_str, a_str, w_imp)
        probs = model_result.get('consensus', {})
        
        if not probs or sum(probs.values()) == 0:
            print("FALHOU (sem probs)")
            continue
        
        actual = get_actual(h_score, a_score)
        pred = predict(probs)
        is_correct = correct(pred, actual)
        b = brier(probs, actual)
        
        results.append({'correct': is_correct, 'brier': b})
        
        print(f"{'OK' if is_correct else 'ERRO'} (B:{b:.3f})")
        
    except Exception as e:
        print(f"FALHOU ({str(e)[:25]})")

print("-" * 70)

if not results:
    print("\nNenhum resultado obtido")
    sys.exit(1)

# Metricas
acc = sum(1 for r in results if r['correct']) / len(results) * 100
avg_b = np.mean([r['brier'] for r in results])

print("\n" + "="*70)
print("METRICAS DE ACERTIVIDADE")
print("="*70)
print(f"\nPartidas testadas:   {len(results)}")
print(f"\nACERTIVIDADE:        {acc:.1f}%")
print(f"Brier Score:         {avg_b:.4f}")
print(f"\nBaseline aleatorio:  33.3%")
print(f"Melhoria:            {(acc-33.3)/33.3*100:+.1f}%")

print("\n" + "-"*70)
if acc >= 50:
    print("STATUS: EXCELENTE")
elif acc >= 45:
    print("STATUS: BOM (adequado para uso comercial)")
elif acc >= 40:
    print("STATUS: ACEITAVEL")
else:
    print("STATUS: INSUFICIENTE")

if avg_b <= 0.20:
    print("CALIBRACAO: Excelente")
elif avg_b <= 0.25:
    print("CALIBRACAO: Boa")
else:
    print("CALIBRACAO: Necessita melhorias")
print("="*70 + "\n")
