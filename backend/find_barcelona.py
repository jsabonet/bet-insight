import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from datetime import datetime, timedelta

# Buscar jogos do Barcelona
home_matches = list(Match.objects.filter(home_team__name__icontains='barcelona').order_by('-match_date')[:10])
away_matches = list(Match.objects.filter(away_team__name__icontains='barcelona').order_by('-match_date')[:10])

all_matches = home_matches + away_matches
all_matches = sorted(all_matches, key=lambda x: x.match_date, reverse=True)

# Remover duplicatas
seen = set()
unique_matches = []
for m in all_matches:
    if m.id not in seen:
        seen.add(m.id)
        unique_matches.append(m)

print(f'\n📋 Últimos {len(unique_matches[:10])} jogos do Barcelona:\n')
for i, m in enumerate(unique_matches[:10], 1):
    score = f"{m.home_score or '?'}-{m.away_score or '?'}"
    print(f"{i}. ID {m.id}: {m.home_team.name} {score} {m.away_team.name}")
    print(f"   Data: {m.match_date.date()} | Status: {m.status} | Liga: {m.league.name}")
    print()
