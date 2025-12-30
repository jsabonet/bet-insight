import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import League, Team

print('\n' + '='*80)
print('VERIFICAÇÃO DE LOGOS - LIGAS E TIMES')
print('='*80)

print('\n🏆 LOGOS DAS LIGAS (primeiras 15):')
print('-'*80)
for league in League.objects.all()[:15]:
    status = '✅' if league.logo else '❌'
    print(f'{status} {league.name:40} | {league.logo}')

print('\n⚽ LOGOS DOS TIMES (amostra):')
print('-'*80)

# Moçambique
print('\n🇲🇿 Moçambique:')
for team in Team.objects.filter(country='Moçambique')[:3]:
    print(f'  {team.name:30} | {team.logo}')

# Premier League
print('\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League:')
for team in Team.objects.filter(country='Inglaterra')[:3]:
    print(f'  {team.name:30} | {team.logo}')

# La Liga
print('\n🇪🇸 La Liga:')
for team in Team.objects.filter(country='Espanha')[:3]:
    print(f'  {team.name:30} | {team.logo}')

print('\n' + '='*80)
print('RESUMO:')
print('='*80)

leagues_with_logo = League.objects.exclude(logo='').count()
total_leagues = League.objects.count()
teams_with_logo = Team.objects.exclude(logo='').count()
total_teams = Team.objects.count()

print(f'\n✅ Ligas com logos: {leagues_with_logo}/{total_leagues}')
print(f'✅ Times com logos: {teams_with_logo}/{total_teams}')

print('\n📝 Tipos de URLs:')
print('   • API-Football Ligas: https://media.api-sports.io/football/leagues/{id}.png')
print('   • API-Football Times: https://media.api-sports.io/football/teams/{id}.png')
print('   • Bandeiras: https://flagcdn.com/w160/{code}.png')
print('   • Placeholders: https://ui-avatars.com/api/?name=...')

print('\n' + '='*80 + '\n')
