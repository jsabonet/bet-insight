"""
Script para coletar partidas históricas de múltiplas ligas
para validação estratificada do modelo ML
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.api_football_service import APIFootballService

# Configuração das ligas para teste estratificado
LEAGUES_CONFIG = {
    # Top 5 Ligas Europeias - Temporada 2024
    'Premier League': {'id': 39, 'season': 2024, 'target': 200},
    'La Liga': {'id': 140, 'season': 2024, 'target': 200},
    'Bundesliga': {'id': 78, 'season': 2024, 'target': 200},
    'Serie A': {'id': 135, 'season': 2024, 'target': 200},
    'Ligue 1': {'id': 61, 'season': 2024, 'target': 200},
    
    # Competições Europeias - Temporada 2024
    'Champions League': {'id': 2, 'season': 2024, 'target': 150},
    'Europa League': {'id': 3, 'season': 2024, 'target': 150},
    
    # 2ª Divisões Europeias - Temporada 2024
    'Championship': {'id': 40, 'season': 2024, 'target': 150},
    'La Liga 2': {'id': 141, 'season': 2024, 'target': 150},
    'Serie B': {'id': 136, 'season': 2024, 'target': 150},
    'Bundesliga 2': {'id': 79, 'season': 2024, 'target': 150},
    'Ligue 2': {'id': 62, 'season': 2024, 'target': 150},
    
    # Outras Ligas Europeias - Temporada 2024
    'Eredivisie': {'id': 88, 'season': 2024, 'target': 150},
    'Primeira Liga': {'id': 94, 'season': 2024, 'target': 150},
    'Super Lig': {'id': 203, 'season': 2024, 'target': 150},
    
    # Américas - Temporada 2024
    'Brasileirão': {'id': 71, 'season': 2024, 'target': 150},
    'Liga MX': {'id': 262, 'season': 2024, 'target': 150},
    'MLS': {'id': 253, 'season': 2024, 'target': 150},
}

def collect_league_matches(league_name, league_id, season, target_matches):
    """
    Coleta partidas históricas de uma liga específica
    """
    print(f"\n{'='*80}")
    print(f"📊 Coletando {league_name} (ID: {league_id}, Temporada: {season})")
    print(f"{'='*80}")
    
    api_service = APIFootballService()
    
    try:
        # Buscar fixtures da liga
        print(f"🔍 Buscando fixtures da API...")
        fixtures_data = api_service.get_fixtures_by_league(
            league_id=league_id,
            season=season,
            status='FT'  # Apenas partidas finalizadas
        )
        
        if not fixtures_data or not fixtures_data.get('response'):
            print(f"❌ Nenhuma fixture encontrada para {league_name}")
            return 0
        
        fixtures = fixtures_data['response']
        print(f"✅ Encontradas {len(fixtures)} partidas finalizadas")
        
        # Limitar ao target
        fixtures = fixtures[:target_matches]
        
        saved_count = 0
        skipped_count = 0
        
        for i, fixture in enumerate(fixtures, 1):
            fixture_id = fixture['fixture']['id']
            
            # Verificar se já existe
            if Match.objects.filter(api_football_id=fixture_id).exists():
                skipped_count += 1
                continue
            
            # Extrair dados
            home_team = fixture['teams']['home']
            away_team = fixture['teams']['away']
            goals = fixture['goals']
            fixture_info = fixture['fixture']
            league_info = fixture['league']
            
            # Buscar ou criar times e liga
            from apps.matches.models import Team, League
            
            # Usar filter().first() para evitar MultipleObjectsReturned
            home_team_obj = Team.objects.filter(api_football_id=home_team['id']).first()
            if not home_team_obj:
                home_team_obj = Team.objects.create(
                    api_football_id=home_team['id'],
                    name=home_team['name'],
                    logo=home_team.get('logo', '')
                )
            
            away_team_obj = Team.objects.filter(api_football_id=away_team['id']).first()
            if not away_team_obj:
                away_team_obj = Team.objects.create(
                    api_football_id=away_team['id'],
                    name=away_team['name'],
                    logo=away_team.get('logo', '')
                )
            
            league_obj = League.objects.filter(api_football_id=league_info['id']).first()
            if not league_obj:
                league_obj = League.objects.create(
                    api_football_id=league_info['id'],
                    name=league_info['name'],
                    country=league_info.get('country', ''),
                    logo=league_info.get('logo', '')
                )
            
            # Criar partida
            match = Match.objects.create(
                api_football_id=fixture_id,
                home_team=home_team_obj,
                away_team=away_team_obj,
                league=league_obj,
                match_date=datetime.fromisoformat(fixture_info['date'].replace('Z', '+00:00')),
                status='finished',
                home_score=goals['home'] if goals['home'] is not None else 0,
                away_score=goals['away'] if goals['away'] is not None else 0,
                round=fixture_info.get('round', ''),
            )
            
            saved_count += 1
            
            if i % 50 == 0:
                print(f"   Progresso: {i}/{len(fixtures)} ({saved_count} salvas, {skipped_count} já existentes)")
        
        print(f"\n✅ {league_name} concluída:")
        print(f"   📥 Salvas: {saved_count}")
        print(f"   ⏭️  Ignoradas (já existentes): {skipped_count}")
        
        return saved_count
        
    except Exception as e:
        print(f"❌ Erro ao coletar {league_name}: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """
    Executa coleta estratificada de partidas históricas
    """
    print("\n" + "="*80)
    print("🎯 COLETA ESTRATIFICADA DE PARTIDAS HISTÓRICAS - EXPANDIDA")
    print("="*80)
    
    total_target = sum(config['target'] for config in LEAGUES_CONFIG.values())
    print(f"\nObjetivo: {total_target} partidas distribuídas em {len(LEAGUES_CONFIG)} ligas")
    print(f"Temporada: 2024")
    
    print(f"\n📊 TOP 5 LIGAS EUROPEIAS:")
    for name in ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1']:
        config = LEAGUES_CONFIG[name]
        print(f"   • {name:20s}: {config['target']} partidas (Liga ID: {config['id']})")
    
    print(f"\n🏆 COMPETIÇÕES EUROPEIAS:")
    for name in ['Champions League', 'Europa League']:
        config = LEAGUES_CONFIG[name]
        print(f"   • {name:20s}: {config['target']} partidas (Liga ID: {config['id']})")
    
    print(f"\n🥈 2ª DIVISÕES:")
    for name in ['Championship', 'La Liga 2', 'Serie B', 'Bundesliga 2', 'Ligue 2']:
        config = LEAGUES_CONFIG[name]
        print(f"   • {name:20s}: {config['target']} partidas (Liga ID: {config['id']})")
    
    print(f"\n🌍 OUTRAS LIGAS:")
    for name in ['Eredivisie', 'Primeira Liga', 'Super Lig', 'Brasileirão', 'Liga MX', 'MLS']:
        config = LEAGUES_CONFIG[name]
        print(f"   • {name:20s}: {config['target']} partidas (Liga ID: {config['id']})")
    
    input("\n⏸️  Pressione ENTER para iniciar a coleta...")
    
    total_saved = 0
    results = {}
    
    for league_name, config in LEAGUES_CONFIG.items():
        saved = collect_league_matches(
            league_name=league_name,
            league_id=config['id'],
            season=config['season'],
            target_matches=config['target']
        )
        results[league_name] = saved
        total_saved += saved
    
    # Relatório final
    print("\n" + "="*80)
    print("📊 RELATÓRIO FINAL DA COLETA")
    print("="*80)
    
    print("\n🏆 TOP 5 LIGAS:")
    for league_name in ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1']:
        count = results[league_name]
        target = LEAGUES_CONFIG[league_name]['target']
        percentage = (count / target * 100) if target > 0 else 0
        print(f"   {league_name:20s}: {count:3d}/{target} ({percentage:5.1f}%)")
    
    print("\n🏆 COMPETIÇÕES EUROPEIAS:")
    for league_name in ['Champions League', 'Europa League']:
        count = results[league_name]
        target = LEAGUES_CONFIG[league_name]['target']
        percentage = (count / target * 100) if target > 0 else 0
        print(f"   {league_name:20s}: {count:3d}/{target} ({percentage:5.1f}%)")
    
    print("\n🥈 2ª DIVISÕES:")
    for league_name in ['Championship', 'La Liga 2', 'Serie B', 'Bundesliga 2', 'Ligue 2']:
        count = results[league_name]
        target = LEAGUES_CONFIG[league_name]['target']
        percentage = (count / target * 100) if target > 0 else 0
        print(f"   {league_name:20s}: {count:3d}/{target} ({percentage:5.1f}%)")
    
    print("\n🌍 OUTRAS LIGAS:")
    for league_name in ['Eredivisie', 'Primeira Liga', 'Super Lig', 'Brasileirão', 'Liga MX', 'MLS']:
        count = results[league_name]
        target = LEAGUES_CONFIG[league_name]['target']
        percentage = (count / target * 100) if target > 0 else 0
        print(f"   {league_name:20s}: {count:3d}/{target} ({percentage:5.1f}%)")
    
    print(f"\n   {'TOTAL':20s}: {total_saved:3d}/{total_target}")
    
    # Verificar partidas no banco
    total_in_db = Match.objects.count()
    print(f"\n✅ Total de partidas no banco de dados: {total_in_db}")
    print(f"✅ Prontas para validação estratificada!")
    
    print("\n" + "="*80)
    print("🚀 PRÓXIMO PASSO:")
    print("   Execute: python validate_stratified.py")
    print("="*80)


if __name__ == '__main__':
    main()
