import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Team

print('\n' + '='*80)
print('BRASÕES DOS TIMES - DEMONSTRAÇÃO')
print('='*80)

print('\n🇲🇿 TIMES MOÇAMBICANOS:')
print('-'*80)
moz_teams = Team.objects.filter(country='Moçambique').exclude(name='Moçambique')[:5]
for team in moz_teams:
    print(f'{team.name:30} | {team.logo}')

print('\n🏴󠁧󠁢󠁥󠁮󠁧󠁿 PREMIER LEAGUE (amostra):')
print('-'*80)
epl_teams = Team.objects.filter(country='Inglaterra')[:5]
for team in epl_teams:
    print(f'{team.name:30} | {team.logo}')

print('\n🇪🇸 LA LIGA (amostra):')
print('-'*80)
laliga_teams = Team.objects.filter(country='Espanha')[:5]
for team in laliga_teams:
    print(f'{team.name:30} | {team.logo}')

print('\n🇧🇷 BRASILEIRÃO (amostra):')
print('-'*80)
br_teams = Team.objects.filter(country='Brasil')[:5]
for team in br_teams:
    print(f'{team.name:30} | {team.logo}')

print('\n🇸🇦 SAUDI PRO LEAGUE (amostra):')
print('-'*80)
saudi_teams = Team.objects.filter(country='Arábia Saudita')[:5]
for team in saudi_teams:
    print(f'{team.name:30} | {team.logo}')

print('\n' + '='*80)
print('RESUMO:')
print('='*80)

total_teams = Team.objects.count()
with_real_logo = Team.objects.filter(api_football_id__isnull=False).count()
with_placeholder = Team.objects.filter(api_football_id__isnull=True).exclude(name='Moçambique').count()

print(f'\n✅ Total de Times: {total_teams}')
print(f'   • Com brasão real (API-Football): {with_real_logo}')
print(f'   • Com placeholder colorido: {with_placeholder}')
print(f'   • Seleção nacional: 1')

print('\n📝 Tipos de Logos:')
print('   1. API-Football: https://media.api-sports.io/football/teams/{id}.png')
print('      → Brasões oficiais de alta qualidade')
print('   2. UI Avatars: https://ui-avatars.com/api/?name=...')
print('      → Placeholders coloridos com iniciais (times sem API)')

print('\n💡 Como Melhorar:')
print('   • Para times moçambicanos: adicionar logos locais')
print('   • Criar pasta de assets com brasões personalizados')
print('   • Integrar com scraping de sites oficiais dos clubes')

print('\n' + '='*80 + '\n')
