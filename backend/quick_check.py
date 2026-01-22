import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import Analysis
import json

# Buscar análise mais recente
a = Analysis.objects.select_related('match').order_by('-created_at').first()

if not a:
    print("NENHUMA ANALISE ENCONTRADA")
    sys.exit(0)

print(f"\n{'='*80}")
print(f"ANALISE ID: {a.id} - {a.created_at}")
print(f"{'='*80}")
print(f"Match: {a.match.home_team} vs {a.match.away_team}")
print(f"Predicao: {a.prediction}")
print(f"Confianca: {a.confidence}")
print(f"\nPROBABILIDADES:")
print(f"  Casa: {a.home_probability}%")
print(f"  Empate: {a.draw_probability}%")
print(f"  Fora: {a.away_probability}%")
print(f"\nxG:")
print(f"  Casa: {a.home_xg}")
print(f"  Fora: {a.away_xg}")
print(f"\nANALYSIS_DATA:")
print(json.dumps(a.analysis_data, indent=2))
print(f"\nTop Bets presente: {'top_bets' in a.analysis_data}")
print(f"Recommendation presente: {'recommendation' in a.analysis_data}")
print(f"\nTotal analises: {Analysis.objects.count()}")
