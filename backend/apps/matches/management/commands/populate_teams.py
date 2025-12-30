"""
Comando para popular o banco de dados com times de todas as ligas
"""
from django.core.management.base import BaseCommand
from apps.matches.models import League, Team


class Command(BaseCommand):
    help = 'Popula o banco de dados com times de todas as ligas'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n⚽ Populando Times de Futebol...\n'))
        
        teams_data = {
            # MOÇAMBIQUE - Moçambola
            'Moçambola': [
                ('Costa do Sol', None),
                ('Ferroviário de Maputo', None),
                ('UD Songo', None),
                ('Ferroviário de Nampula', None),
                ('Maxaquene', None),
                ('Liga Muçulmana', None),
                ('Black Bulls', None),
                ('Ferroviário de Lichinga', None),
                ('ENH Vilankulo', None),
                ('Matchedje de Mocuba', None),
                ('Incomáti de Xai-Xai', None),
                ('Textáfrica do Chimoio', None),
            ],
            
            # ÁFRICA DO SUL - DSTV Premiership
            'DSTV Premiership': [
                ('Mamelodi Sundowns', 382),
                ('Orlando Pirates', 383),
                ('Kaizer Chiefs', 384),
                ('SuperSport United', 385),
                ('Cape Town City', 8601),
                ('AmaZulu', 8603),
                ('Sekhukhune United', None),
                ('Royal AM', None),
                ('Golden Arrows', 8605),
                ('Stellenbosch', None),
                ('Moroka Swallows', 390),
                ('Chippa United', 8607),
            ],
            
            # INGLATERRA - Premier League
            'Premier League': [
                ('Manchester City', 50),
                ('Arsenal', 42),
                ('Liverpool', 40),
                ('Aston Villa', 66),
                ('Tottenham', 47),
                ('Chelsea', 49),
                ('Newcastle', 34),
                ('Manchester United', 33),
                ('West Ham', 48),
                ('Crystal Palace', 52),
                ('Brighton', 51),
                ('Bournemouth', 35),
                ('Fulham', 36),
                ('Wolves', 39),
                ('Everton', 45),
                ('Brentford', 55),
                ('Nottingham Forest', 65),
                ('Luton Town', 163),
                ('Burnley', 44),
                ('Sheffield United', 62),
            ],
            
            # ESPANHA - La Liga
            'La Liga': [
                ('Barcelona', 529),
                ('Real Madrid', 541),
                ('Atlético Madrid', 530),
                ('Athletic Bilbao', 531),
                ('Real Sociedad', 548),
                ('Real Betis', 543),
                ('Villarreal', 533),
                ('Valencia', 532),
                ('Sevilla', 536),
                ('Getafe', 546),
                ('Girona', 547),
                ('Osasuna', 727),
                ('Rayo Vallecano', 728),
                ('Las Palmas', 472),
                ('Celta Vigo', 538),
                ('Mallorca', 798),
                ('Cádiz', 724),
                ('Almería', 723),
                ('Granada', 715),
                ('Alavés', 542),
            ],
            
            # ITÁLIA - Serie A
            'Serie A': [
                ('Inter Milan', 505),
                ('Juventus', 496),
                ('AC Milan', 489),
                ('Napoli', 492),
                ('Lazio', 487),
                ('Atalanta', 499),
                ('Roma', 497),
                ('Fiorentina', 502),
                ('Bologna', 500),
                ('Torino', 503),
                ('Monza', 1579),
                ('Genoa', 495),
                ('Lecce', 867),
                ('Udinese', 494),
                ('Frosinone', 512),
                ('Empoli', 511),
                ('Sassuolo', 488),
                ('Verona', 504),
                ('Cagliari', 490),
                ('Salernitana', 514),
            ],
            
            # ALEMANHA - Bundesliga
            'Bundesliga': [
                ('Bayern Munich', 157),
                ('Borussia Dortmund', 165),
                ('RB Leipzig', 173),
                ('Union Berlin', 28),
                ('SC Freiburg', 160),
                ('Bayer Leverkusen', 168),
                ('Eintracht Frankfurt', 169),
                ('Wolfsburg', 178),
                ('Mainz 05', 164),
                ('Borussia Mönchengladbach', 163),
                ('FC Köln', 161),
                ('Hoffenheim', 167),
                ('Werder Bremen', 162),
                ('Bochum', 36),
                ('Augsburg', 170),
                ('Stuttgart', 172),
                ('Darmstadt 98', 26),
                ('Heidenheim', 180),
            ],
            
            # FRANÇA - Ligue 1
            'Ligue 1': [
                ('PSG', 85),
                ('Marseille', 81),
                ('Monaco', 91),
                ('Lille', 79),
                ('Lyon', 80),
                ('Nice', 82),
                ('Lens', 116),
                ('Rennes', 94),
                ('Reims', 547),
                ('Montpellier', 87),
                ('Strasbourg', 175),
                ('Nantes', 83),
                ('Lorient', 94),
                ('Le Havre', 3),
                ('Toulouse', 96),
                ('Brest', 97),
                ('Clermont Foot', 166),
                ('Metz', 545),
            ],
            
            # PORTUGAL - Primeira Liga
            'Primeira Liga': [
                ('Benfica', 211),
                ('Porto', 212),
                ('Sporting CP', 228),
                ('Braga', 218),
                ('Vitória Guimarães', 217),
                ('Rio Ave', 219),
                ('Santa Clara', 496),
                ('Gil Vicente', 222),
                ('Moreirense', 224),
                ('Casa Pia', 1024),
                ('Famalicão', 1451),
                ('Boavista', 215),
                ('Estoril', 2893),
                ('Arouca', 238),
                ('Vizela', 4947),
                ('Estrela Amadora', 5593),
                ('Chaves', 214),
                ('Portimonense', 221),
            ],
            
            # BRASIL - Brasileirão Série A
            'Brasileirão Série A': [
                ('Flamengo', 127),
                ('Palmeiras', 128),
                ('Atlético Mineiro', 129),
                ('São Paulo', 126),
                ('Fluminense', 124),
                ('Corinthians', 131),
                ('Internacional', 130),
                ('Botafogo', 118),
                ('Santos', 125),
                ('Vasco da Gama', 1371),
                ('Grêmio', 132),
                ('Athletico Paranaense', 134),
                ('Fortaleza', 142),
                ('Bragantino', 1237),
                ('Bahia', 136),
                ('Cruzeiro', 151),
                ('Goiás', 1062),
                ('Coritiba', 1207),
                ('América Mineiro', 2174),
                ('Cuiabá', 2223),
            ],
            
            # ARÁBIA SAUDITA - Saudi Pro League
            'Saudi Pro League': [
                ('Al-Nassr', 2939),
                ('Al-Hilal', 2928),
                ('Al-Ittihad', 2929),
                ('Al-Ahli', 2932),
                ('Al-Ettifaq', 2934),
                ('Al-Taawoun', 2931),
                ('Al-Fateh', 2938),
                ('Al-Wehda', 2944),
                ('Al-Raed', 2941),
                ('Al-Fayha', 2943),
                ('Damac', 2942),
                ('Al-Khaleej', 2940),
                ('Abha', 2937),
                ('Al-Tai', 2935),
                ('Al-Riyadh', 2933),
                ('Al-Hazem', 2936),
            ],
            
            # ESTADOS UNIDOS - MLS
            'MLS': [
                ('Inter Miami', 1611),
                ('LA Galaxy', 1337),
                ('Seattle Sounders', 1336),
                ('Nashville SC', 15995),
                ('FC Cincinnati', 14911),
                ('Columbus Crew', 1340),
                ('New England Revolution', 1345),
                ('New York Red Bulls', 1346),
                ('Orlando City', 1337),
                ('Philadelphia Union', 1349),
                ('Atlanta United', 1614),
                ('Charlotte FC', 20775),
                ('Chicago Fire', 1341),
                ('CF Montréal', 1342),
                ('DC United', 1338),
                ('Toronto FC', 1344),
                ('LAFC', 15994),
                ('Portland Timbers', 1347),
                ('Real Salt Lake', 1348),
                ('San Jose Earthquakes', 1350),
            ],
        }
        
        # Times para competições africanas e internacionais (seleções e clubes principais)
        special_teams = {
            'CAF Champions League': [
                ('Al Ahly', 1029),
                ('Mamelodi Sundowns', 382),
                ('Wydad Casablanca', 964),
                ('TP Mazembe', 967),
                ('Espérance Tunis', 969),
                ('CR Belouizdad', None),
                ('Simba SC', None),
                ('Young Africans', None),
            ],
            'CAF Confederation Cup': [
                ('RS Berkane', None),
                ('USM Alger', 968),
                ('Raja Casablanca', 965),
                ('Pyramids FC', 1040),
            ],
            'Seleção Nacional de Moçambique': [
                ('Moçambique', None),
            ],
        }
        
        # Adicionar times especiais
        teams_data.update(special_teams)
        
        created_count = 0
        updated_count = 0
        
        for league_name, teams in teams_data.items():
            try:
                league = League.objects.get(name=league_name)
                self.stdout.write(f'\n📋 {league_name} ({league.country}):')
                
                for team_name, api_id in teams:
                    # Verificar duplicatas
                    existing = Team.objects.filter(name=team_name)
                    if existing.count() > 1:
                        first = existing.first()
                        existing.exclude(id=first.id).delete()
                        self.stdout.write(
                            self.style.WARNING(f'  ⚠️  Removidas {existing.count() - 1} duplicatas de: {team_name}')
                        )
                    
                    # Gerar URL do logo
                    if api_id:
                        logo_url = f'https://media.api-sports.io/football/teams/{api_id}.png'
                    else:
                        # Para times sem API ID, usar placeholder ou logo genérico
                        logo_url = f'https://ui-avatars.com/api/?name={team_name.replace(" ", "+")}&background=random&size=128'
                    
                    team, created = Team.objects.update_or_create(
                        name=team_name,
                        defaults={
                            'api_football_id': api_id,
                            'country': league.country,
                            'logo': logo_url,
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f'  ✓ {team_name}'))
                    else:
                        updated_count += 1
                        self.stdout.write(self.style.WARNING(f'  ↻ {team_name}'))
                        
            except League.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'✗ Liga não encontrada: {league_name}'))
                continue
        
        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f'\n\n✅ Processo Concluído!\n'
                f'   • {created_count} times criados\n'
                f'   • {updated_count} times atualizados\n'
                f'   • {Team.objects.count()} times no total\n'
            )
        )
        
        # Estatísticas
        self.stdout.write(self.style.MIGRATE_HEADING('\n📊 Estatísticas:\n'))
        
        from django.db.models import Count
        
        # Times por país
        countries = Team.objects.values('country').annotate(
            total=Count('id')
        ).order_by('-total')[:10]
        
        self.stdout.write('Times por País (Top 10):')
        for country in countries:
            self.stdout.write(f"  • {country['country']}: {country['total']} times")
        
        # Times com/sem API ID
        with_api = Team.objects.filter(api_football_id__isnull=False).count()
        without_api = Team.objects.filter(api_football_id__isnull=True).count()
        with_logo = Team.objects.exclude(logo='').count()
        
        self.stdout.write(f'\nIntegração API-Football:')
        self.stdout.write(f'  • Com API ID: {with_api} times')
        self.stdout.write(f'  • Sem API ID: {without_api} times (dados locais)')
        self.stdout.write(f'  • Com Logo: {with_logo} times')
        
        self.stdout.write('\n')
