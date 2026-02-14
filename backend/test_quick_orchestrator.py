"""
Teste Final - Orchestrator com Estrategia Hibrida
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from django.db.models import Q

# Teste rapido
matches = Match.objects.filter(
    Q(status='finished') | Q(status='FT')
).exclude(
    home_score__isnull=True
).exclude(
    away_score__isnull=True
).select_related('home_team', 'away_team', 'league').first()

if matches:
    print(f"Testando: {matches.home_team.name} vs {matches.away_team.name}")
    print(f"API ID: {matches.api_football_id}")
    print("\nCampo confirmado!")
else:
    print("Nenhuma partida encontrada")
