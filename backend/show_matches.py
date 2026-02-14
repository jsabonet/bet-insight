"""
Consulta partidas no banco de dados - Versão Simplificada
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from django.db.models import Q, Count

# Total
total = Match.objects.count()
print(f"="*80)
print(f"TOTAL DE PARTIDAS: {total}")
print(f"="*80)

# Por status
print(f"\nPOR STATUS:")
status_counts = Match.objects.values('status').annotate(
    total=Count('id')
).order_by('-total')

for item in status_counts:
    print(f"  {item['status']:20s}: {item['total']:4d}")

# Finalizadas
finished = Match.objects.filter(Q(status='finished') | Q(status='FT')).count()
finished_with_score = Match.objects.filter(
    Q(status='finished') | Q(status='FT'),
    home_score__isnull=False,
    away_score__isnull=False
).count()

print(f"\nFINALIZADAS:")
print(f"  Total: {finished}")
print(f"  Com placar: {finished_with_score}")

# Por liga
print(f"\nTOP 10 LIGAS:")
league_counts = Match.objects.values('league__name').annotate(
    total=Count('id')
).order_by('-total')[:10]

for item in league_counts:
    name = item['league__name'] or 'Sem liga'
    print(f"  {name:35s}: {item['total']:4d}")

# Por ano da partida
print(f"\nPOR ANO:")
from django.db.models.functions import ExtractYear
year_counts = Match.objects.annotate(
    year=ExtractYear('match_date')
).values('year').annotate(
    total=Count('id')
).order_by('-year')[:5]

for item in year_counts:
    year = item['year'] or 'Sem data'
    print(f"  Ano {year}: {item['total']} partidas")

# Últimas 20 finalizadas
print(f"\n" + "="*80)
print(f"ÚLTIMAS 20 FINALIZADAS (com placar):")
print(f"="*80)

recent = Match.objects.filter(
    Q(status='finished') | Q(status='FT'),
    home_score__isnull=False,
    away_score__isnull=False
).select_related('home_team', 'away_team', 'league').order_by('-match_date')[:20]

for idx, m in enumerate(recent, 1):
    league = m.league.name[:25] if m.league else 'N/A'
    date = m.match_date.strftime('%d/%m/%Y') if m.match_date else 'N/A'
    print(f"{idx:2d}. [{date}] {league:25s} | {m.home_team.name[:20]:20s} {m.home_score}-{m.away_score} {m.away_team.name[:20]:20s}")

print(f"\n" + "="*80)
