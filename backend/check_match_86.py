import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import Analysis
from apps.matches.models import Match

# Análise ID 86
a = Analysis.objects.get(id=86)
print(f"\n{'='*80}")
print(f"ANALISE ID 86")
print(f"{'='*80}")
print(f"Match ID: {a.match.id}")
print(f"Match: {a.match.home_team} vs {a.match.away_team}")
print(f"Match API Football ID: {a.match.api_football_id}")
print(f"Match no banco? True (tem ID: {a.match.id})")
print(f"\nProbabilidades:")
print(f"  Casa: {a.home_probability}%")
print(f"  Empate: {a.draw_probability}%")
print(f"  Fora: {a.away_probability}%")
print(f"\nAnalysis_data: {a.analysis_data}")
print(f"{'='*80}\n")
