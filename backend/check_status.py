import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from django.db.models import Count

result = Match.objects.values('status').annotate(count=Count('id'))

print('\n📊 STATUS DAS PARTIDAS NO BANCO:\n')
for r in result:
    print(f'  {r["status"]}: {r["count"]} partidas')
print()
