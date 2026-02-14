"""
Procura partidas de Copas no banco de dados
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from django.db.models import Q

print("="*80)
print("PROCURANDO PARTIDAS DE COPAS")
print("="*80)
print()

# Procurar por ligas que contenham "Copa", "Cup", "World Cup", etc
copa_keywords = ['Copa', 'Cup', 'Mundial', 'World']

all_leagues = Match.objects.values_list('league__name', flat=True).distinct()

print("Ligas disponíveis com palavra-chave de Copa:")
print("-" * 80)

copa_leagues = []
for league in all_leagues:
    if league:
        for keyword in copa_keywords:
            if keyword.lower() in league.lower():
                copa_leagues.append(league)
                break

if copa_leagues:
    for league in sorted(set(copa_leagues)):
        count = Match.objects.filter(league__name=league).count()
        finished = Match.objects.filter(
            league__name=league,
            status='finished',
            home_score__isnull=False
        ).count()
        print(f"  {league:50s} - Total: {count:4d} | Finalizadas: {finished:4d}")
else:
    print("  Nenhuma liga com palavras-chave de Copa encontrada")

print()
print("="*80)
print("TODAS AS LIGAS NO SISTEMA:")
print("="*80)
print()

# Mostrar todas as ligas
from collections import Counter
league_counter = Counter()

for league in all_leagues:
    if league:
        count = Match.objects.filter(league__name=league).count()
        league_counter[league] = count

print(f"Total de ligas: {len(league_counter)}")
print()
print("Top 30 ligas por número de partidas:")
print("-" * 80)

for league, count in league_counter.most_common(30):
    finished = Match.objects.filter(
        league__name=league,
        status='finished',
        home_score__isnull=False
    ).count()
    print(f"  {league:50s} - Total: {count:4d} | Finalizadas: {finished:4d}")

print()
print("="*80)

# Procurar especificamente por partidas da Copa do Mundo
print()
print("PROCURANDO 'WORLD CUP' ou 'COPA DO MUNDO':")
print("-" * 80)

world_cup_matches = Match.objects.filter(
    Q(league__name__icontains='World Cup') |
    Q(league__name__icontains='Copa do Mundo') |
    Q(league__name__icontains='Mundial')
)

if world_cup_matches.exists():
    print(f"\nEncontradas {world_cup_matches.count()} partidas")
    print("\nAmostras:")
    for match in world_cup_matches[:20].select_related('home_team', 'away_team', 'league'):
        score = f"{match.home_score}-{match.away_score}" if match.home_score is not None else "N/A"
        print(f"  [{match.match_date}] {match.league.name:30s} | {match.home_team.name} vs {match.away_team.name} - {score}")
else:
    print("  Nenhuma partida encontrada")

print()
print("="*80)
