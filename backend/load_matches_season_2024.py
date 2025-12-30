import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from apps.matches.models import League, Team, Match
from datetime import datetime
from django.utils import timezone

print("=" * 80)
print("🚀 CARREGANDO PARTIDAS DAS PRINCIPAIS LIGAS - TEMPORADA 2024")
print("=" * 80)

api = FootballAPIService()

# Verificar API Key
if not api.api_key or api.api_key == 'YOUR_API_KEY_HERE':
    print("❌ API Key não configurada!")
    exit(1)

print(f"✅ API Key: {api.api_key[:20]}...")
print(f"✅ URL: {api.base_url}\n")

# IDs das ligas principais com temporada 2024
MAIN_LEAGUES = {
    39: ("Premier League", 2024),
    140: ("La Liga", 2024),
    61: ("Ligue 1", 2024),
    78: ("Bundesliga", 2024),
    135: ("Serie A", 2024),
    94: ("Primeira Liga", 2024),
    71: ("Serie A Brasil", 2024),
}

def load_matches_by_league_season(league_id, league_name, season):
    """Carrega partidas de uma liga específica"""
    print(f"\n🏆 {league_name} - Temporada {season}")
    print(f"   Liga ID: {league_id}")
    
    loaded = 0
    updated = 0
    
    result = api.get_fixtures_by_league(league_id, season=season)
    
    if result['success']:
        fixtures = result['fixtures']
        print(f"   Encontradas: {len(fixtures)} partidas")
        
        # Processar apenas as primeiras 50 para economizar tempo
        fixtures_to_process = fixtures[:50] if len(fixtures) > 50 else fixtures
        
        for fixture in fixtures_to_process:
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
        
        print(f"   ✅ {loaded} criadas, {updated} atualizadas (processadas {len(fixtures_to_process)} de {len(fixtures)})")
    else:
        print(f"   ❌ Erro: {result['error']}")
    
    return loaded, updated

print("🔄 Iniciando carregamento...\n")

total_loaded = 0
total_updated = 0

for league_id, (league_name, season) in MAIN_LEAGUES.items():
    loaded, updated = load_matches_by_league_season(league_id, league_name, season)
    total_loaded += loaded
    total_updated += updated

print("\n" + "=" * 80)
print("📊 RESUMO FINAL")
print("=" * 80)
print(f"✅ Total de partidas criadas: {total_loaded}")
print(f"🔄 Total de partidas atualizadas: {total_updated}")
print(f"📈 Total geral: {total_loaded + total_updated}")

# Mostrar estatísticas do banco
from django.db.models import Count
leagues_count = League.objects.count()
teams_count = Team.objects.count()
matches_count = Match.objects.count()

print(f"\n📊 Estatísticas do Banco de Dados:")
print(f"   Ligas: {leagues_count}")
print(f"   Times: {teams_count}")
print(f"   Partidas: {matches_count}")

print("\n✅ Processo concluído!")
print("=" * 80)
