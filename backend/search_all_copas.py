"""
Busca detalhada por partidas de copas
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match

print("="*80)
print("BUSCA DETALHADA - TODAS AS COPAS")
print("="*80)
print()

# Buscar por todos os nomes de liga únicos
all_leagues = Match.objects.values_list('league__name', flat=True).distinct().order_by('league__name')

print("TODAS AS LIGAS (ordenadas alfabeticamente):")
print("-" * 80)

copa_related = []
for league in all_leagues:
    if league:
        count = Match.objects.filter(league__name=league).count()
        finished = Match.objects.filter(
            league__name=league,
            status='finished',
            home_score__isnull=False
        ).count()
        
        # Destacar se tiver "copa", "cup", "champions", "europa"
        is_copa = any(word in league.lower() for word in ['copa', 'cup', 'champions', 'europa', 'libertadores'])
        
        marker = ">>> " if is_copa else "    "
        print(f"{marker}{league:50s} - Total: {count:4d} | Finalizadas: {finished:4d}")
        
        if is_copa:
            copa_related.append((league, count, finished))

print()
print("="*80)
print(f"RESUMO - COPAS/CHAMPIONSHIPS ENCONTRADAS: {len(copa_related)}")
print("="*80)
print()

for league, total, finished in copa_related:
    print(f"  {league:50s} - Total: {total:4d} | Finalizadas: {finished:4d}")
    
    # Mostrar amostra de partidas
    if finished > 0:
        print(f"    Amostra das últimas 5 partidas finalizadas:")
        matches = Match.objects.filter(
            league__name=league,
            status='finished',
            home_score__isnull=False
        ).select_related('home_team', 'away_team').order_by('-match_date')[:5]
        
        for match in matches:
            print(f"      [{match.match_date}] {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name}")
    print()

print("="*80)
