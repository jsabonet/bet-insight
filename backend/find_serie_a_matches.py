import os, sys, django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match

# Buscar partidas Serie A
matches = Match.objects.filter(
    league__name__icontains='Serie A',
    status='NS'
).order_by('match_date')[:10]

print("Partidas Serie A disponiveis:")
if matches:
    for m in matches:
        print(f"{m.match_date.strftime('%d/%m %H:%M')} - {m.home_team.name} vs {m.away_team.name} (ID: {m.api_football_id})")
else:
    print("Nenhuma partida encontrada")
    
# Buscar Verona especificamente
verona_matches = Match.objects.filter(
    home_team__name__icontains='Verona'
).exclude(status='FT').order_by('match_date')[:5]

print("\nPartidas do Verona (casa):")
if verona_matches:
    for m in verona_matches:
        print(f"{m.match_date.strftime('%d/%m %H:%M')} - {m.home_team.name} vs {m.away_team.name} (ID: {m.api_football_id})")
