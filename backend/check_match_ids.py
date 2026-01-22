import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from apps.matches.models import Match

# Tentar encontrar por varios IDs
ids_to_check = [1436057, 11436057, 100]

for id_val in ids_to_check:
    try:
        m = Match.objects.get(id=id_val)
        print(f"✅ Match ID {id_val} EXISTE: {m.home_team} vs {m.away_team} (api_football_id={m.api_football_id})")
    except:
        print(f"❌ Match ID {id_val} NÃO encontrado")

# Buscar por api_football_id
try:
    m = Match.objects.get(api_football_id=1436057)
    print(f"\n✅ Match com api_football_id=1436057 EXISTE:")
    print(f"   ID do banco: {m.id}")
    print(f"   Match: {m.home_team} vs {m.away_team}")
except:
    print(f"\n❌ Match com api_football_id=1436057 NÃO encontrado")
