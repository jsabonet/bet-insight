import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Team, League

print('\n' + '='*60)
print('RESUMO FINAL - LIGAS E TIMES')
print('='*60)

total_leagues = League.objects.count()
total_teams = Team.objects.count()

print(f'\n📊 Totais:')
print(f'   • Ligas: {total_leagues}')
print(f'   • Times: {total_teams}')

print(f'\n🏆 Times por Liga:')
print('-'*60)

for league in League.objects.all().order_by('-priority'):
    # Contar times do mesmo país da liga
    times_count = Team.objects.filter(country=league.country).count()
    
    # Para ligas específicas, contar com mais precisão
    if 'Moçambola' in league.name or 'Taça de Moçambique' in league.name:
        mozambique_teams = Team.objects.filter(country='Moçambique').exclude(name='Moçambique').count()
        print(f'{league.name:40} | {mozambique_teams:3} times')
    elif 'Seleção Nacional' in league.name:
        print(f'{league.name:40} |   1 seleção')
    else:
        print(f'{league.name:40} | {times_count:3} times')

print('-'*60)

print(f'\n✅ Ligas com Times Cadastrados:')
countries_with_teams = Team.objects.values('country').distinct().count()
print(f'   • {countries_with_teams} países/regiões com times')

print(f'\n🔗 Integração API-Football:')
with_api = Team.objects.filter(api_football_id__isnull=False).count()
without_api = Team.objects.filter(api_football_id__isnull=True).count()
print(f'   • Times com API ID: {with_api}')
print(f'   • Times sem API ID: {without_api} (dados locais)')

print('\n' + '='*60)
