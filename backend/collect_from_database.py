"""
Coletar dataset de treinamento direto do banco de dados Django
Usa partidas já armazenadas (sem depender da API)
"""
import os
import sys
import django
import json
from datetime import datetime
from pathlib import Path

# Setup Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

print("="*80)
print("📦 COLETA DE DATASET - BANCO DE DADOS")
print("="*80)

# Configuração
MAX_MATCHES = 3000
OUTPUT_FILE = 'ml_training/training_dataset.json'

# Inicializar orchestrator
orchestrator = HybridAnalysisOrchestrator()

# Buscar partidas finalizadas
print(f"\n🔍 Buscando partidas no banco...")
matches = Match.objects.filter(
    status='finished',
    home_score__isnull=False,
    away_score__isnull=False
).select_related('league').order_by('-match_date')[:MAX_MATCHES]

total = matches.count()
print(f"✅ {total} partidas encontradas")

# Coletar dados
dataset = {
    'metadata': {
        'collected_at': datetime.now().isoformat(),
        'total_matches': 0,
        'total_errors': 0,
        'source': 'database',
        'leagues': set(),
        'seasons': set()
    },
    'data': []
}

errors = 0
collected = 0

print(f"\n🚀 Iniciando processamento...")
for i, match in enumerate(matches, 1):
    try:
        # Resultado real (label)
        if match.home_score > match.away_score:
            result = 'home'
        elif match.away_score > match.home_score:
            result = 'away'
        else:
            result = 'draw'
        
        # Enriquecer dados
        match_data = {'api_id': match.api_football_id}
        enriched = orchestrator.enricher.enrich(match_data)
        
        # Feature engineering
        features = orchestrator.fe.engineer_all_features(enriched)
        
        # Flatten features
        flat_features = {}
        for category, values in features.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    flat_features[f"{category}.{key}"] = value
        
        # Adicionar ao dataset
        entry = {
            'fixture_id': match.api_football_id,
            'league': match.league.name if match.league else 'Unknown',
            'league_id': match.league.api_football_id if match.league else None,
            'season': match.match_date.year if match.match_date else None,
            'date': match.match_date.isoformat() if match.match_date else None,
            'teams': {
                'home': match.home_team,
                'away': match.away_team
            },
            'features': flat_features,
            'label': result,
            'score': {
                'home': match.home_score,
                'away': match.away_score
            }
        }
        
        dataset['data'].append(entry)
        collected += 1
        
        # Metadata
        if match.league:
            dataset['metadata']['leagues'].add(match.league.name)
        if match.match_date:
            dataset['metadata']['seasons'].add(match.match_date.year)
        
        # Progresso
        if i % 100 == 0 or i == total:
            print(f"   📊 Progresso: {i}/{total} | Coletadas: {collected} | Erros: {errors}")
    
    except Exception as e:
        errors += 1
        print(f"   ⚠️ Erro na partida {match.id}: {str(e)}")
        continue

# Finalizar metadata
dataset['metadata']['total_matches'] = collected
dataset['metadata']['total_errors'] = errors
dataset['metadata']['leagues'] = sorted(list(dataset['metadata']['leagues']))
dataset['metadata']['seasons'] = sorted(list(dataset['metadata']['seasons']))

# Salvar
output_path = Path(__file__).parent / OUTPUT_FILE
print(f"\n💾 Salvando dataset...")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

print(f"\n{'='*80}")
print("✅ COLETA FINALIZADA")
print(f"{'='*80}")
print(f"📊 Total coletado: {collected} partidas")
print(f"❌ Erros: {errors}")
print(f"💾 Arquivo: {output_path}")
print(f"{'='*80}")
