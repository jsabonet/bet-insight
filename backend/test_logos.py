import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import Analysis

print("=== TESTE DE LOGOS ===\n")
analyses = Analysis.objects.all()
print(f"Total de análises: {analyses.count()}\n")

for i, a in enumerate(analyses, 1):
    print(f"--- Análise {i} ---")
    print(f"Match: {a.match.home_team.name} vs {a.match.away_team.name}")
    print(f"Home logo: {a.match.home_team.logo or '(vazio)'}")
    print(f"Away logo: {a.match.away_team.logo or '(vazio)'}")
    print(f"League: {a.match.league.name}")
    print(f"League logo: {a.match.league.logo or '(vazio)'}")
    print()
