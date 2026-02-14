#!/usr/bin/env python
"""Verificar análises no banco de dados"""
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import Analysis
from apps.matches.models import Match
from datetime import datetime, timedelta

print("\n" + "="*80)
print("🔍 VERIFICANDO ANÁLISES NO BANCO DE DADOS")
print("="*80 + "\n")

# Partidas Brentford vs Arsenal
matches = Match.objects.filter(
    home_team__name__icontains='Brentford', 
    away_team__name__icontains='Arsenal'
)
print(f"Partidas Brentford vs Arsenal: {matches.count()}")
for m in matches:
    print(f"  - {m.home_team.name} vs {m.away_team.name} ({m.match_date})")
    analyses = Analysis.objects.filter(match=m)
    print(f"    Análises: {analyses.count()}")
    for a in analyses:
        print(f"      Usuário: {a.user.username}")
        print(f"      Arsenal: {a.away_probability}%")
        print(f"      Criada: {a.created_at}")

# Total de análises
total = Analysis.objects.count()
print(f"\n📊 TOTAL de análises no banco: {total}")

# Análises recentes
cutoff = datetime.now() - timedelta(days=1)
recentes = Analysis.objects.filter(created_at__gte=cutoff).order_by('-created_at')[:10]
print(f"\n📅 Análises nas últimas 24 horas: {recentes.count()}")
for a in recentes:
    print(f"  {a.match.home_team.name} vs {a.match.away_team.name}")
    print(f"    {a.home_team.name if hasattr(a, 'home_team') else a.match.home_team.name}: {a.home_probability}%")
    print(f"    Empate: {a.draw_probability}%")
    print(f"    {a.away_team.name if hasattr(a, 'away_team') else a.match.away_team.name}: {a.away_probability}%")
    print(f"    Criada: {a.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
    print()

print("="*80 + "\n")
