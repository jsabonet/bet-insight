"""
Contar partidas com xG real no stats_cache
"""
import json
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match

matches_with_stats = Match.objects.exclude(stats_cache__isnull=True).exclude(stats_cache='')
total_with_stats = matches_with_stats.count()
total_with_xg = 0

print(f"Analisando {total_with_stats} partidas com stats_cache...")

for i, match in enumerate(matches_with_stats, 1):
    if i % 20 == 0:
        print(f"  Progresso: {i}/{total_with_stats}")
    
    has_xg = False
    
    if isinstance(match.stats_cache, list):
        for team_stats in match.stats_cache:
            statistics = team_stats.get('statistics', [])
            for stat in statistics:
                stat_type = stat.get('type', '').lower()
                if 'expected' in stat_type or 'xg' in stat_type:
                    has_xg = True
                    break
            if has_xg:
                break
    
    if has_xg:
        total_with_xg += 1

print(f"\nRESULTADO:")
print(f"  Partidas com stats_cache: {total_with_stats}")
print(f"  Partidas com xG real: {total_with_xg}")
print(f"  Porcentagem: {(total_with_xg/total_with_stats*100):.1f}%")
