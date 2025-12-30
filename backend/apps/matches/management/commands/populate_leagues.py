"""
Comando para popular o banco de dados com ligas de futebol
Inclui competições de Moçambique, África do Sul, África e principais ligas europeias
"""
from django.core.management.base import BaseCommand
from apps.matches.models import League


class Command(BaseCommand):
    help = 'Popula o banco de dados com ligas de futebol'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n🏆 Populando Ligas de Futebol...\n'))
        
        leagues_data = [
            # MOÇAMBIQUE - Prioridade Máxima
            {
                'name': 'Moçambola',
                'country': 'Moçambique',
                'priority': 100,
                'api_football_id': None,
                'logo': 'https://ui-avatars.com/api/?name=Moçambola&background=1B5E20&color=fff&size=128',
            },
            {
                'name': 'Taça de Moçambique',
                'country': 'Moçambique',
                'priority': 95,
                'api_football_id': None,
                'logo': 'https://ui-avatars.com/api/?name=Taça+MZ&background=C62828&color=fff&size=128',
            },
            {
                'name': 'Supertaça de Moçambique',
                'country': 'Moçambique',
                'priority': 90,
                'api_football_id': None,
                'logo': 'https://ui-avatars.com/api/?name=Supertaça+MZ&background=F57C00&color=fff&size=128',
            },
            {
                'name': 'Seleção Nacional de Moçambique',
                'country': 'Moçambique',
                'priority': 98,
                'api_football_id': None,
                'logo': 'https://flagcdn.com/w160/mz.png',
            },
            
            # ÁFRICA DO SUL
            {
                'name': 'DSTV Premiership',
                'country': 'África do Sul',
                'priority': 85,
                'api_football_id': 288,
                'logo': 'https://media.api-sports.io/football/leagues/288.png',
            },
            {
                'name': 'MTN 8',
                'country': 'África do Sul',
                'priority': 80,
                'api_football_id': 1367,
                'logo': 'https://media.api-sports.io/football/leagues/1367.png',
            },
            {
                'name': 'Nedbank Cup',
                'country': 'África do Sul',
                'priority': 80,
                'api_football_id': 1366,
                'logo': 'https://media.api-sports.io/football/leagues/1366.png',
            },
            
            # COMPETIÇÕES AFRICANAS
            {
                'name': 'CAF Champions League',
                'country': 'África',
                'priority': 88,
                'api_football_id': 12,
                'logo': 'https://media.api-sports.io/football/leagues/12.png',
            },
            {
                'name': 'CAF Confederation Cup',
                'country': 'África',
                'priority': 85,
                'api_football_id': 13,
                'logo': 'https://media.api-sports.io/football/leagues/13.png',
            },
            {
                'name': 'Copa Africana de Nações',
                'country': 'África',
                'priority': 92,
                'api_football_id': 1,
                'logo': 'https://media.api-sports.io/football/leagues/1.png',
            },
            {
                'name': 'Eliminatórias Copa Africana',
                'country': 'África',
                'priority': 88,
                'api_football_id': 20,
                'logo': 'https://media.api-sports.io/football/leagues/20.png',
            },
            {
                'name': 'Eliminatórias Africanas Copa do Mundo',
                'country': 'África',
                'priority': 89,
                'api_football_id': 29,
                'logo': 'https://media.api-sports.io/football/leagues/29.png',
            },
            
            # INGLATERRA
            {
                'name': 'Premier League',
                'country': 'Inglaterra',
                'priority': 95,
                'api_football_id': 39,
                'logo': 'https://media.api-sports.io/football/leagues/39.png',
            },
            {
                'name': 'FA Cup',
                'country': 'Inglaterra',
                'priority': 85,
                'api_football_id': 45,
                'logo': 'https://media.api-sports.io/football/leagues/45.png',
            },
            {
                'name': 'EFL Cup',
                'country': 'Inglaterra',
                'priority': 82,
                'api_football_id': 48,
                'logo': 'https://media.api-sports.io/football/leagues/48.png',
            },
            
            # ESPANHA
            {
                'name': 'La Liga',
                'country': 'Espanha',
                'priority': 95,
                'api_football_id': 140,
                'logo': 'https://media.api-sports.io/football/leagues/140.png',
            },
            {
                'name': 'Copa del Rey',
                'country': 'Espanha',
                'priority': 85,
                'api_football_id': 143,
                'logo': 'https://media.api-sports.io/football/leagues/143.png',
            },
            
            # ITÁLIA
            {
                'name': 'Serie A',
                'country': 'Itália',
                'priority': 93,
                'api_football_id': 135,
                'logo': 'https://media.api-sports.io/football/leagues/135.png',
            },
            {
                'name': 'Coppa Italia',
                'country': 'Itália',
                'priority': 83,
                'api_football_id': 137,
                'logo': 'https://media.api-sports.io/football/leagues/137.png',
            },
            
            # FRANÇA
            {
                'name': 'Ligue 1',
                'country': 'França',
                'priority': 90,
                'api_football_id': 61,
                'logo': 'https://media.api-sports.io/football/leagues/61.png',
            },
            {
                'name': 'Coupe de France',
                'country': 'França',
                'priority': 80,
                'api_football_id': 66,
                'logo': 'https://media.api-sports.io/football/leagues/66.png',
            },
            
            # ALEMANHA
            {
                'name': 'Bundesliga',
                'country': 'Alemanha',
                'priority': 93,
                'api_football_id': 78,
                'logo': 'https://media.api-sports.io/football/leagues/78.png',
            },
            {
                'name': 'DFB-Pokal',
                'country': 'Alemanha',
                'priority': 82,
                'api_football_id': 81,
                'logo': 'https://media.api-sports.io/football/leagues/81.png',
            },
            
            # PORTUGAL
            {
                'name': 'Primeira Liga',
                'country': 'Portugal',
                'priority': 88,
                'api_football_id': 94,
                'logo': 'https://media.api-sports.io/football/leagues/94.png',
            },
            {
                'name': 'Taça de Portugal',
                'country': 'Portugal',
                'priority': 80,
                'api_football_id': 96,
                'logo': 'https://media.api-sports.io/football/leagues/96.png',
            },
            
            # COMPETIÇÕES EUROPEIAS
            {
                'name': 'UEFA Champions League',
                'country': 'Europa',
                'priority': 99,
                'api_football_id': 2,
                'logo': 'https://media.api-sports.io/football/leagues/2.png',
            },
            {
                'name': 'UEFA Europa League',
                'country': 'Europa',
                'priority': 90,
                'api_football_id': 3,
                'logo': 'https://media.api-sports.io/football/leagues/3.png',
            },
            {
                'name': 'UEFA Europa Conference League',
                'country': 'Europa',
                'priority': 85,
                'api_football_id': 848,
                'logo': 'https://media.api-sports.io/football/leagues/848.png',
            },
            
            # COMPETIÇÕES INTERNACIONAIS
            {
                'name': 'Copa do Mundo FIFA',
                'country': 'Mundial',
                'priority': 100,
                'api_football_id': 1,
                'logo': 'https://media.api-sports.io/football/leagues/1.png',
            },
            {
                'name': 'Eurocopa',
                'country': 'Europa',
                'priority': 98,
                'api_football_id': 4,
                'logo': 'https://media.api-sports.io/football/leagues/4.png',
            },
            {
                'name': 'Liga das Nações UEFA',
                'country': 'Europa',
                'priority': 87,
                'api_football_id': 5,
                'logo': 'https://media.api-sports.io/football/leagues/5.png',
            },
            {
                'name': 'Amistosos Internacionais',
                'country': 'Mundial',
                'priority': 70,
                'api_football_id': 10,
                'logo': 'https://media.api-sports.io/football/leagues/10.png',
            },
            
            # OUTRAS LIGAS IMPORTANTES
            {
                'name': 'Brasileirão Série A',
                'country': 'Brasil',
                'priority': 88,
                'api_football_id': 71,
                'logo': 'https://media.api-sports.io/football/leagues/71.png',
            },
            {
                'name': 'Saudi Pro League',
                'country': 'Arábia Saudita',
                'priority': 85,
                'api_football_id': 307,
                'logo': 'https://media.api-sports.io/football/leagues/307.png',
            },
            {
                'name': 'MLS',
                'country': 'Estados Unidos',
                'priority': 83,
                'api_football_id': 253,
                'logo': 'https://media.api-sports.io/football/leagues/253.png',
            },
        ]
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for league_data in leagues_data:
            try:
                # Verificar se já existe
                existing = League.objects.filter(
                    name=league_data['name'],
                    country=league_data['country']
                )
                
                if existing.count() > 1:
                    # Remover duplicatas, manter a primeira
                    first = existing.first()
                    existing.exclude(id=first.id).delete()
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Removidas {existing.count() - 1} duplicatas de: {league_data["name"]}')
                    )
                
                league, created = League.objects.update_or_create(
                    name=league_data['name'],
                    country=league_data['country'],
                    defaults={
                        'priority': league_data['priority'],
                        'api_football_id': league_data['api_football_id'],
                        'logo': league_data.get('logo', ''),
                        'is_active': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Criada: {league.name} ({league.country}) - Prioridade: {league.priority}')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Atualizada: {league.name} ({league.country})')
                    )
            except Exception as e:
                skipped_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Erro ao processar {league_data["name"]}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f'\n✅ Processo Concluído!\n'
                f'   • {created_count} ligas criadas\n'
                f'   • {updated_count} ligas atualizadas\n'
                f'   • {skipped_count} erros/puladas\n'
                f'   • {League.objects.count()} ligas no total\n'
            )
        )
        
        # Mostrar estatísticas por país
        self.stdout.write(self.style.MIGRATE_HEADING('\n📊 Ligas por País/Região:\n'))
        
        from django.db.models import Count
        stats = League.objects.values('country').annotate(total=Count('id')).order_by('-total')
        
        for stat in stats:
            self.stdout.write(f"   • {stat['country']}: {stat['total']} competições")
        
        self.stdout.write('\n')
