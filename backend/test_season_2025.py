import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

print("⚽ Testando busca de partidas - Temporada 2025/2026\n")
print("="*80)

api = FootballAPIService()

# Principais ligas
leagues = {
    'Premier League': 39,
    'La Liga': 140,
    'Serie A': 135,
    'Bundesliga': 78,
    'Ligue 1': 61,
    'Primeira Liga': 94,
}

total = 0

for league_name, league_id in leagues.items():
    print(f"\n🔍 {league_name} (ID: {league_id})...")
    result = api.get_fixtures_by_league(league_id, season=2025)
    
    if result['success']:
        count = result['count']
        total += count
        
        if count > 0:
            print(f"✅ {count} partidas encontradas!")
            
            # Mostrar primeiras 3
            for i, fixture in enumerate(result['fixtures'][:3], 1):
                home = fixture['teams']['home']['name']
                away = fixture['teams']['away']['name']
                date = fixture['fixture']['date'][:10]
                time = fixture['fixture']['date'][11:16]
                status = fixture['fixture']['status']['short']
                
                print(f"  {i}. {date} {time} | {home} vs {away} [{status}]")
        else:
            print(f"⚠️ 0 partidas")
    else:
        print(f"❌ Erro: {result['error']}")

print("\n" + "="*80)
print(f"\n📊 TOTAL: {total} partidas encontradas na temporada 2025!")

if total > 0:
    print("\n✅ SUCESSO! Dados reais disponíveis!")
else:
    print("\n⚠️ Nenhuma partida - provavelmente temporada ainda não iniciada na API")
