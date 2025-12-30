import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from apps.matches.models import League, Team, Match
from datetime import datetime, timedelta
from django.utils import timezone

print("=" * 80)
print("🚀 CARREGANDO PARTIDAS DA API-FOOTBALL")
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
}

def load_matches_for_date_range(start_date, end_date):
    """Carrega partidas de um período"""
    total_loaded = 0
    total_updated = 0
    errors = []
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        print(f"\n📅 Buscando partidas para {date_str}...")
        
        result = api.get_fixtures_by_date(date_str)
        
        if result['success']:
            fixtures = result['fixtures']
            print(f"   Encontradas: {len(fixtures)} partidas")
            
            # Filtrar apenas ligas principais
            main_fixtures = [f for f in fixtures if f['league']['id'] in MAIN_LEAGUES.keys()]
            print(f"   Ligas principais: {len(main_fixtures)} partidas")
            
            for fixture in main_fixtures:
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
                        total_loaded += 1
                        print(f"   ✅ Criada: {home_team.name} vs {away_team.name}")
                    else:
                        total_updated += 1
                        print(f"   🔄 Atualizada: {home_team.name} vs {away_team.name}")
                    
                except Exception as e:
                    error_msg = f"Erro ao processar partida {fixture['fixture']['id']}: {str(e)}"
                    errors.append(error_msg)
                    print(f"   ❌ {error_msg}")
        else:
            error_msg = f"Erro ao buscar partidas de {date_str}: {result['error']}"
            errors.append(error_msg)
            print(f"   ❌ {error_msg}")
        
        current_date += timedelta(days=1)
    
    return total_loaded, total_updated, errors

# Perguntar ao usuário o período
print("\n" + "=" * 80)
print("Escolha o período para carregar partidas:")
print("1. Hoje")
print("2. Próximos 7 dias")
print("3. Próximos 30 dias")
print("4. Período personalizado")
print("=" * 80)

choice = input("\nEscolha (1-4): ").strip()

today = datetime.now().date()

if choice == "1":
    start_date = today
    end_date = today
    print(f"\n📅 Carregando partidas de hoje ({today})")
elif choice == "2":
    start_date = today
    end_date = today + timedelta(days=7)
    print(f"\n📅 Carregando partidas dos próximos 7 dias ({start_date} a {end_date})")
elif choice == "3":
    start_date = today
    end_date = today + timedelta(days=30)
    print(f"\n📅 Carregando partidas dos próximos 30 dias ({start_date} a {end_date})")
elif choice == "4":
    start_input = input("Data inicial (YYYY-MM-DD): ").strip()
    end_input = input("Data final (YYYY-MM-DD): ").strip()
    try:
        start_date = datetime.strptime(start_input, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_input, '%Y-%m-%d').date()
        print(f"\n📅 Carregando partidas de {start_date} a {end_date}")
    except ValueError:
        print("❌ Formato de data inválido!")
        exit(1)
else:
    print("❌ Opção inválida!")
    exit(1)

print("\n🔄 Iniciando carregamento...\n")

loaded, updated, errors = load_matches_for_date_range(start_date, end_date)

print("\n" + "=" * 80)
print("📊 RESUMO")
print("=" * 80)
print(f"✅ Partidas criadas: {loaded}")
print(f"🔄 Partidas atualizadas: {updated}")
print(f"❌ Erros: {len(errors)}")

if errors:
    print("\n⚠️ ERROS ENCONTRADOS:")
    for error in errors[:10]:  # Mostrar apenas os primeiros 10
        print(f"   - {error}")
    if len(errors) > 10:
        print(f"   ... e mais {len(errors) - 10} erros")

print("\n✅ Processo concluído!")
print("=" * 80)
