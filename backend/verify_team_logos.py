import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Team, League

print("🔍 Verificação Detalhada de Logos\n")
print("="*80)

# Verificar times principais por liga
leagues_to_check = {
    'Premier League': ['Manchester City', 'Arsenal', 'Liverpool', 'Manchester United', 'Chelsea'],
    'La Liga': ['Barcelona', 'Real Madrid', 'Atlético Madrid', 'Sevilla', 'Valencia'],
    'Serie A': ['Inter Milan', 'Juventus', 'AC Milan', 'Napoli', 'Roma'],
    'Bundesliga': ['Bayern Munich', 'Borussia Dortmund', 'RB Leipzig', 'Bayer Leverkusen'],
    'Ligue 1': ['PSG', 'Marseille', 'Monaco', 'Lyon', 'Lille'],
    'Brasileirão Série A': ['Flamengo', 'Palmeiras', 'Corinthians', 'São Paulo', 'Fluminense'],
}

for league_name, teams in leagues_to_check.items():
    print(f"\n📋 {league_name}")
    print("-" * 80)
    
    for team_name in teams:
        team = Team.objects.filter(name=team_name).first()
        if team:
            print(f"  {team_name}")
            print(f"    API ID: {team.api_football_id}")
            print(f"    Logo: {team.logo}")
            print(f"    Expected: https://media.api-sports.io/football/teams/{team.api_football_id}.png")
            if team.logo == f"https://media.api-sports.io/football/teams/{team.api_football_id}.png":
                print(f"    ✅ Logo correto")
            else:
                print(f"    ❌ Logo incorreto!")
        else:
            print(f"  {team_name} - ❌ Time não encontrado no banco!")

print("\n" + "="*80)
print("\n🔍 Verificando todos os times com API ID:\n")

teams_with_id = Team.objects.exclude(api_football_id__isnull=True).order_by('name')
incorrect_logos = []

for team in teams_with_id:
    expected_logo = f"https://media.api-sports.io/football/teams/{team.api_football_id}.png"
    if team.logo != expected_logo:
        incorrect_logos.append({
            'name': team.name,
            'api_id': team.api_football_id,
            'current_logo': team.logo,
            'expected_logo': expected_logo
        })

if incorrect_logos:
    print(f"❌ {len(incorrect_logos)} times com logos incorretos:\n")
    for item in incorrect_logos[:20]:  # Mostrar primeiros 20
        print(f"  • {item['name']} (ID: {item['api_id']})")
        print(f"    Atual: {item['current_logo']}")
        print(f"    Esperado: {item['expected_logo']}\n")
else:
    print("✅ Todos os times com API ID têm logos corretos!")

print(f"\n📊 Resumo:")
print(f"  • Total de times: {Team.objects.count()}")
print(f"  • Times com API ID: {teams_with_id.count()}")
print(f"  • Times com logos incorretos: {len(incorrect_logos)}")
