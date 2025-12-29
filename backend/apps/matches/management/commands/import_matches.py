"""
Management command para importar partidas das APIs externas
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.matches.models import Match
from apps.matches.services.football_api import football_api
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Importar partidas futuras das APIs de futebol'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Número de dias para importar (padrão: 7)'
        )
        parser.add_argument(
            '--league',
            type=str,
            help='ID da liga específica (opcional)'
        )

    def handle(self, *args, **options):
        days = options['days']
        league_id = options.get('league')
        
        self.stdout.write(self.style.SUCCESS(f'🔄 Importando partidas dos próximos {days} dias...'))
        
        total_imported = 0
        total_updated = 0
        
        # Buscar partidas para os próximos dias
        for day_offset in range(days):
            date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
            
            self.stdout.write(f'\n📅 Buscando partidas para {date}...')
            
            result = football_api.get_fixtures_by_date(date)
            
            if not result['success']:
                self.stdout.write(self.style.ERROR(f'❌ Erro: {result["error"]}'))
                continue
            
            fixtures = result['fixtures']
            self.stdout.write(f'   Encontradas {len(fixtures)} partidas')
            
            # Processar cada partida
            for fixture in fixtures:
                try:
                    imported, updated = self._process_fixture(fixture, league_id)
                    if imported:
                        total_imported += 1
                    elif updated:
                        total_updated += 1
                        
                except Exception as e:
                    logger.error(f'Erro ao processar partida: {e}')
                    continue
        
        # Resumo
        self.stdout.write(self.style.SUCCESS(f'\n✅ Importação concluída!'))
        self.stdout.write(f'   📥 Novas partidas: {total_imported}')
        self.stdout.write(f'   🔄 Partidas atualizadas: {total_updated}')

    def _process_fixture(self, fixture, league_filter=None):
        """Processar uma partida e salvar no banco"""
        
        fixture_data = fixture['fixture']
        league_data = fixture['league']
        teams_data = fixture['teams']
        goals_data = fixture.get('goals', {})
        score_data = fixture.get('score', {})
        
        # Filtrar por liga se especificado
        if league_filter and str(league_data['id']) != league_filter:
            return False, False
        
        # Dados da partida
        external_id = fixture_data['id']
        home_team = teams_data['home']['name']
        away_team = teams_data['away']['name']
        match_date = timezone.datetime.fromisoformat(fixture_data['date'].replace('Z', '+00:00'))
        league_name = league_data['name']
        status = fixture_data['status']['short']
        
        # Verificar se já existe
        match, created = Match.objects.update_or_create(
            external_id=external_id,
            defaults={
                'home_team': home_team,
                'away_team': away_team,
                'date': match_date,
                'league': league_name,
                'status': status,
                'home_score': goals_data.get('home'),
                'away_score': goals_data.get('away'),
                'venue': fixture_data.get('venue', {}).get('name'),
                'referee': fixture_data.get('referee'),
            }
        )
        
        if created:
            self.stdout.write(f'   ✅ {home_team} vs {away_team}')
        
        return created, not created
