"""
Consulta partidas no banco de dados
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from django.db.models import Q, Count

# Total de partidas
total = Match.objects.count()
print(f"="*80)
print(f"TOTAL DE PARTIDAS NO BANCO: {total}")
print(f"="*80)

# Por status
print(f"\nPOR STATUS:")

for status in Match.objects.values_list('status', flat=True).distinct():
    count = Match.objects.filter(status=status).count()
    print(f"  {status:20s}: {count:4d}")

# Finalizadas
finished = Match.objects.filter(
    Q(status='finished') | Q(status='FT')
).count()

finished_with_score = Match.objects.filter(
    Q(status='finished') | Q(status='FT')
).exclude(
    home_score__isnull=True
).exclude(
    away_score__isnull=True
).count()

print(f"\nPARTIDAS FINALIZADAS:")
print(f"  Total: {finished}")
print(f"  Com placar: {finished_with_score}")

# Por liga
print(f"\nPOR LIGA:")
league_counts = Match.objects.values('league__name').annotate(
    count=Count('id')
).order_by('-count')[:10]

for lc in league_counts:
    league_name = lc['league__name'] or 'Sem liga'
    count = lc['count']
    print(f"  {league_name:30s}: {count:4d}")

# Partidas recentes finalizadas com placar
print(f"\n" + "="*80)
print(f"ÚLTIMAS 20 PARTIDAS FINALIZADAS (com placar):")
print(f"="*80)

recent = Match.objects.filter(
    Q(status='finished') | Q(status='FT')
).exclude(
    home_score__isnull=True
).exclude(
    away_score__isnull=True
).select_related('home_team', 'away_team', 'league').order_by('-date')[:20]

for idx, match in enumerate(recent, 1):
    league = match.league.name if match.league else 'N/A'
    date = match.date.strftime('%Y-%m-%d') if match.date else 'N/A'
    print(f"{idx:2d}. [{date}] {league[:20]:20s} | {match.home_team.name[:20]:20s} {match.home_score}-{match.away_score} {match.away_team.name[:20]:20s}")

# Estatísticas por temporada
print(f"\n" + "="*80)
print(f"POR TEMPORADA:")
print(f"="*80)

season_counts = Match.objects.values('season').annotate(
    count=Count('id')
).order_by('-season')[:5]

for sc in season_counts:
    season = sc['season'] or 'N/A'
    count = sc['count']
    print(f"  {season}: {count} partidas")

print(f"\n" + "="*80)
