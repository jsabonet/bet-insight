import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from apps.matches.models import League, Team, Match
from datetime import datetime, timedelta
from django.utils import timezone

print("=" * 80)
print("🚀 CARREGANDO PARTIDAS - ÚLTIMOS 30 DIAS E PRÓXIMOS 30 DIAS")
print("=" * 80)

api = FootballAPIService()

# Verificar API Key
if not api.api_key or api.api_key == 'YOUR_API_KEY_HERE':
    print("❌ API Key não configurada!")
    exit(1)

print(f"✅ API Key: {api.api_key[:20]}...")
print(f"✅ URL: {api.base_url}\n")

# IDs das ligas principais para buscar
MAIN_LEAGUES = {
    39: "Premier League",
    140: "La Liga",
    61: "Ligue 1",
    78: "Bundesliga",
    135: "Serie A",
    2: "UEFA Champions League",
    3: "UEFA Europa League",
    94: "Primeira Liga (Portugal)",
    71: "Serie A (Brasil)",
    88: "Eredivisie",
    203: "Super Lig (Turkey)",
}

def load_matches_by_league(league_id, from_date, to_date):
    """Carrega partidas de uma liga específica"""
    print(f"\n🏆 Liga ID {league_id}: {MAIN_LEAGUES[league_id]}")
    print(f"   Período: {from_date} a {to_date}")
    
    loaded = 0
    updated = 0
    
    result = api.get_fixtures_by_league(league_id, from_date, to_date)
    
    if result['success']:
        fixtures = result['fixtures']
        print(f"   Encontradas: {len(fixtures)} partidas")
        
        for fixture in fixtures:
            try:
                # Criar/Atualizar Liga
                league_data = fixture['league']
                league, created = League.objects.get_or_create(
                    external_id=league_data['id'],
                    defaults={
                        'name': league_data['name'],
                        'country': fixture['league'].get('country', ''),
                        'logo_url': league_data.get('logo', ''),
                        'is_active': True
                    }
                )
                
                # Criar/Atualizar Times
                home_data = fixture['teams']['home']
                home_team, created = Team.objects.get_or_create(
                    external_id=home_data['id'],
                    defaults={
                        'name': home_data['name'],
                        'logo_url': home_data.get('logo', ''),
                        'country': fixture['league'].get('country', '')
                    }
                )
                
                away_data = fixture['teams']['away']
                away_team, created = Team.objects.get_or_create(
                    external_id=away_data['id'],
                    defaults={
                        'name': away_data['name'],
                        'logo_url': away_data.get('logo', ''),
                        'country': fixture['league'].get('country', '')
                    }
                )
                
                # Criar/Atualizar Partida
                fixture_data = fixture['fixture']
                match_date = datetime.fromisoformat(fixture_data['date'].replace('Z', '+00:00'))
                
                status = fixture_data['status']['short']
                status_map = {
                    'NS': 'scheduled',
                    'TBD': 'scheduled',
                    'LIVE': 'live',
                    '1H': 'live',
                    'HT': 'live',
                    '2H': 'live',
                    'ET': 'live',
                    'P': 'live',
                    'FT': 'finished',
                    'AET': 'finished',
                    'PEN': 'finished',
                    'PST': 'postponed',
                    'CANC': 'cancelled',
                    'ABD': 'cancelled',
                }
                match_status = status_map.get(status, 'scheduled')
                
                # Scores
                goals = fixture.get('goals', {})
                home_score = goals.get('home')
                away_score = goals.get('away')
                
                match, created = Match.objects.update_or_create(
                    external_id=fixture_data['id'],
                    defaults={
                        'league': league,
                        'home_team': home_team,
                        'away_team': away_team,
                        'match_date': match_date,
                        'status': match_status,
                        'home_score': home_score,
                        'away_score': away_score,
                        'venue': fixture_data.get('venue', {}).get('name', ''),
                        'round': fixture['league'].get('round', ''),
                    }
                )
                
                if created:
                    loaded += 1
                else:
                    updated += 1
                
            except Exception as e:
                print(f"   ❌ Erro: {str(e)}")
        
        if loaded > 0 or updated > 0:
            print(f"   ✅ {loaded} criadas, {updated} atualizadas")
    else:
        print(f"   ❌ Erro: {result['error']}")
    
    return loaded, updated

# Período: últimos 30 dias + próximos 30 dias
today = datetime.now()
from_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
to_date = (today + timedelta(days=30)).strftime('%Y-%m-%d')

print(f"📅 Período total: {from_date} a {to_date}")
print("🔄 Buscando por ligas...\n")

total_loaded = 0
total_updated = 0

for league_id in MAIN_LEAGUES.keys():
    loaded, updated = load_matches_by_league(league_id, from_date, to_date)
    total_loaded += loaded
    total_updated += updated

print("\n" + "=" * 80)
print("📊 RESUMO FINAL")
print("=" * 80)
print(f"✅ Total de partidas criadas: {total_loaded}")
print(f"🔄 Total de partidas atualizadas: {total_updated}")
print(f"📈 Total geral: {total_loaded + total_updated}")

print("\n✅ Processo concluído!")
print("=" * 80)
