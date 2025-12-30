import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import League, Team, Match
from datetime import datetime, timedelta
import requests
from django.conf import settings

print("=" * 80)
print("🚀 CARREGANDO PARTIDAS - FOOTBALL-DATA.ORG API")
print("=" * 80)

API_KEY = settings.FOOTBALL_DATA_API_KEY
BASE_URL = "https://api.football-data.org/v4"

headers = {
    'X-Auth-Token': API_KEY
}

print(f"✅ API Key: {API_KEY[:20]}...")
print(f"✅ URL: {BASE_URL}")
print(f"\n💡 Esta API tem limite de 10 requisições/minuto (plano gratuito)\n")

# Competições disponíveis na Football-Data.org
COMPETITIONS = {
    'PL': ('Premier League', 2021),
    'PD': ('La Liga', 2021),
    'BL1': ('Bundesliga', 2021),
    'SA': ('Serie A', 2021),
    'FL1': ('Ligue 1', 2021),
    'PPL': ('Primeira Liga', 2021),
    'DED': ('Eredivisie', 2021),
    'CL': ('UEFA Champions League', 2021),
}

def load_matches_from_competition(comp_code, comp_name, season):
    """Carrega partidas de uma competição"""
    print(f"\n🏆 {comp_name} ({comp_code})")
    
    loaded = 0
    updated = 0
    
    try:
        # Buscar partidas da competição
        url = f"{BASE_URL}/competitions/{comp_code}/matches"
        params = {'season': season}
        
        response = requests.get(url, headers=headers, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get('matches', [])
            print(f"   Encontradas: {len(matches)} partidas")
            
            if len(matches) == 0:
                print(f"   ⚠️  Sem dados disponíveis")
                return 0, 0
            
            # Processar primeiras 50 partidas
            matches_to_process = matches[:50] if len(matches) > 50 else matches
            
            for match_data in matches_to_process:
                try:
                    # Criar/Atualizar Liga
                    competition = match_data.get('competition', {})
                    league, created = League.objects.get_or_create(
                        external_id=f"fd_{competition.get('id', comp_code)}",
                        defaults={
                            'name': competition.get('name', comp_name),
                            'country': competition.get('area', {}).get('name', ''),
                            'logo_url': competition.get('emblem', ''),
                            'is_active': True
                        }
                    )
                    
                    # Criar/Atualizar Times
                    home_team_data = match_data.get('homeTeam', {})
                    home_team, created = Team.objects.get_or_create(
                        external_id=f"fd_{home_team_data.get('id')}",
                        defaults={
                            'name': home_team_data.get('name', 'Unknown'),
                            'logo_url': home_team_data.get('crest', ''),
                            'country': competition.get('area', {}).get('name', '')
                        }
                    )
                    
                    away_team_data = match_data.get('awayTeam', {})
                    away_team, created = Team.objects.get_or_create(
                        external_id=f"fd_{away_team_data.get('id')}",
                        defaults={
                            'name': away_team_data.get('name', 'Unknown'),
                            'logo_url': away_team_data.get('crest', ''),
                            'country': competition.get('area', {}).get('name', '')
                        }
                    )
                    
                    # Criar/Atualizar Partida
                    match_date = datetime.fromisoformat(match_data['utcDate'].replace('Z', '+00:00'))
                    
                    status_api = match_data.get('status')
                    status_map = {
                        'SCHEDULED': 'scheduled',
                        'TIMED': 'scheduled',
                        'IN_PLAY': 'live',
                        'PAUSED': 'live',
                        'FINISHED': 'finished',
                        'POSTPONED': 'postponed',
                        'CANCELLED': 'cancelled',
                        'SUSPENDED': 'cancelled',
                    }
                    match_status = status_map.get(status_api, 'scheduled')
                    
                    # Scores
                    score = match_data.get('score', {})
                    full_time = score.get('fullTime', {})
                    home_score = full_time.get('home')
                    away_score = full_time.get('away')
                    
                    match, created = Match.objects.update_or_create(
                        external_id=f"fd_{match_data.get('id')}",
                        defaults={
                            'league': league,
                            'home_team': home_team,
                            'away_team': away_team,
                            'match_date': match_date,
                            'status': match_status,
                            'home_score': home_score,
                            'away_score': away_score,
                            'venue': match_data.get('venue', ''),
                            'round': match_data.get('matchday', ''),
                        }
                    )
                    
                    if created:
                        loaded += 1
                    else:
                        updated += 1
                    
                except Exception as e:
                    print(f"   ❌ Erro ao processar partida: {str(e)}")
            
            print(f"   ✅ {loaded} criadas, {updated} atualizadas (processadas {len(matches_to_process)} de {len(matches)})")
            
        elif response.status_code == 403:
            print(f"   ❌ Acesso negado - verifique a API key")
        elif response.status_code == 429:
            print(f"   ❌ Limite de requisições atingido - aguarde 1 minuto")
        else:
            print(f"   ❌ Erro HTTP {response.status_code}: {response.text[:100]}")
    
    except Exception as e:
        print(f"   ❌ Erro: {str(e)}")
    
    return loaded, updated

print("🔄 Iniciando carregamento...\n")
print("⏳ Aguardando entre requisições para respeitar limite da API...\n")

total_loaded = 0
total_updated = 0
import time

for comp_code, (comp_name, season) in COMPETITIONS.items():
    loaded, updated = load_matches_from_competition(comp_code, comp_name, season)
    total_loaded += loaded
    total_updated += updated
    
    # Aguardar 7 segundos entre requisições (10 req/min = 6s mínimo)
    if comp_code != list(COMPETITIONS.keys())[-1]:
        print("   ⏳ Aguardando 7 segundos...")
        time.sleep(7)

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
