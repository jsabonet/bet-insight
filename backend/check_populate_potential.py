"""
Verificar quantas partidas ainda podem ser populadas
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match

MAIN_LEAGUES = [
    'Premier League',
    'La Liga', 
    'Serie A',
    'Bundesliga',
    'Ligue 1',
    'Primeira Liga',
    'Eredivisie',
    'Champions League',
    'Europa League',
]

print("="*80)
print("ANÁLISE: Potencial de Partidas para Popular xG")
print("="*80)

# 1. Candidatos atuais (com filtro atual)
candidates = Match.objects.filter(
    home_score__isnull=False,
    away_score__isnull=False,
    match_date__year__gte=2023,
    api_football_id__isnull=False
).filter(
    league__name__in=MAIN_LEAGUES
).exclude(
    stats_cache__isnull=False
).exclude(
    stats_cache=''
)

print(f"\n[1] CANDIDATOS ATUAIS (filtro restrito):")
print(f"    Com api_football_id + sem stats_cache: {candidates.count()}")

# 2. Todas finalizadas com api_football_id (ligas principais)
all_finished = Match.objects.filter(
    home_score__isnull=False,
    away_score__isnull=False,
    match_date__year__gte=2023,
    api_football_id__isnull=False,
    league__name__in=MAIN_LEAGUES
)

print(f"\n[2] TODAS FINALIZADAS (ligas principais, 2023+):")
print(f"    Total: {all_finished.count()}")

# 3. Já populadas
populated = all_finished.exclude(stats_cache__isnull=True).exclude(stats_cache='')
print(f"    Já com stats_cache: {populated.count()}")

# 4. Potencial restante
remaining = all_finished.count() - populated.count()
print(f"    Restantes para popular: {remaining}")

# 5. Sem api_football_id
finished_no_api_id = Match.objects.filter(
    home_score__isnull=False,
    away_score__isnull=False,
    match_date__year__gte=2023,
    api_football_id__isnull=True,
    league__name__in=MAIN_LEAGUES
).count()

print(f"\n[3] SEM api_football_id (não podem ser populadas):")
print(f"    {finished_no_api_id} partidas")

# 6. Todas as partidas (incluindo anos anteriores)
all_years_finished = Match.objects.filter(
    home_score__isnull=False,
    away_score__isnull=False,
    api_football_id__isnull=False,
    league__name__in=MAIN_LEAGUES
)

print(f"\n[4] TODAS AS PARTIDAS (qualquer ano):")
print(f"    Total finalizadas: {all_years_finished.count()}")
print(f"    Já com stats_cache: {Match.objects.filter(id__in=all_years_finished, stats_cache__isnull=False).exclude(stats_cache='').count()}")

# 7. Por liga
print(f"\n[5] POR LIGA (finalizadas 2023+, com api_football_id):")
for league in MAIN_LEAGUES:
    total = all_finished.filter(league__name=league).count()
    with_cache = populated.filter(league__name=league).count()
    remaining_league = total - with_cache
    print(f"    {league:20s}: {total:4d} total | {with_cache:4d} populado | {remaining_league:4d} restante")

print("\n" + "="*80)
print("CONCLUSÃO")
print("="*80)

if remaining > 0:
    print(f"\n✅ Ainda há {remaining} partidas para popular!")
    print(f"   Execute novamente populate_xg_from_api.py")
elif finished_no_api_id > 0:
    print(f"\n⚠️  Esgotados candidatos com api_football_id")
    print(f"   {finished_no_api_id} partidas não têm api_football_id (não podem ser populadas)")
else:
    print(f"\n🎉 Todas as partidas possíveis foram populadas!")

print("\n💡 PARA AUMENTAR xG:")
print("   1. Popular partidas de anos anteriores (2020-2022)")
print("   2. Adicionar mais ligas ao MAIN_LEAGUES")
print("   3. Buscar novas partidas da API e adicionar ao banco")
print("="*80 + "\n")
