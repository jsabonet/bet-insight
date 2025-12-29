from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.matches.models import League, Team, Match
from apps.users.models import User


class Command(BaseCommand):
    help = 'Popula banco de dados com partidas de teste'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando dados de teste...')
        
        # Criar usuários de teste
        self.stdout.write('Criando usuários...')
        
        # Usuário normal
        user_normal, created = User.objects.get_or_create(
            username='joao',
            defaults={
                'email': 'joao@example.com',
                'phone': '+258843334444',
                'is_premium': False
            }
        )
        if created:
            user_normal.set_password('senha123')
            user_normal.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Usuário normal criado: joao/senha123'))
        
        # Usuário premium
        user_premium, created = User.objects.get_or_create(
            username='maria',
            defaults={
                'email': 'maria@example.com',
                'phone': '+258844445555',
                'is_premium': True
            }
        )
        if created:
            user_premium.set_password('senha123')
            user_premium.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Usuário premium criado: maria/senha123'))
        
        self.stdout.write(self.style.SUCCESS(f'✓ {User.objects.count()} usuários no sistema'))
        
        # Criar Ligas
        premier_league = League.objects.create(
            name='Premier League',
            country='Inglaterra',
            logo='https://crests.football-data.org/PL.png',
            priority=100,
            is_active=True
        )
        
        la_liga = League.objects.create(
            name='La Liga',
            country='Espanha',
            logo='https://crests.football-data.org/PD.png',
            priority=95,
            is_active=True
        )
        
        serie_a = League.objects.create(
            name='Serie A',
            country='Itália',
            logo='https://crests.football-data.org/SA.png',
            priority=90,
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ {League.objects.count()} ligas criadas'))
        
        # Criar Times - Premier League com logos
        man_city = Team.objects.create(
            name='Manchester City', 
            country='Inglaterra',
            logo='https://crests.football-data.org/65.png'
        )
        liverpool = Team.objects.create(
            name='Liverpool', 
            country='Inglaterra',
            logo='https://crests.football-data.org/64.png'
        )
        arsenal = Team.objects.create(
            name='Arsenal', 
            country='Inglaterra',
            logo='https://crests.football-data.org/57.png'
        )
        chelsea = Team.objects.create(
            name='Chelsea', 
            country='Inglaterra',
            logo='https://crests.football-data.org/61.png'
        )
        man_utd = Team.objects.create(
            name='Manchester United', 
            country='Inglaterra',
            logo='https://crests.football-data.org/66.png'
        )
        tottenham = Team.objects.create(
            name='Tottenham', 
            country='Inglaterra',
            logo='https://crests.football-data.org/73.png'
        )
        
        # Times - La Liga com logos
        real_madrid = Team.objects.create(
            name='Real Madrid', 
            country='Espanha',
            logo='https://crests.football-data.org/86.png'
        )
        barcelona = Team.objects.create(
            name='Barcelona', 
            country='Espanha',
            logo='https://crests.football-data.org/81.png'
        )
        atletico = Team.objects.create(
            name='Atlético Madrid', 
            country='Espanha',
            logo='https://crests.football-data.org/78.png'
        )
        sevilla = Team.objects.create(
            name='Sevilla', 
            country='Espanha',
            logo='https://crests.football-data.org/559.png'
        )
        
        # Times - Serie A com logos
        inter = Team.objects.create(
            name='Inter Milan', 
            country='Itália',
            logo='https://crests.football-data.org/108.png'
        )
        juventus = Team.objects.create(
            name='Juventus', 
            country='Itália',
            logo='https://crests.football-data.org/109.png'
        )
        milan = Team.objects.create(
            name='AC Milan', 
            country='Itália',
            logo='https://crests.football-data.org/98.png'
        )
        napoli = Team.objects.create(
            name='Napoli', 
            country='Itália',
            logo='https://crests.football-data.org/113.png'
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ {Team.objects.count()} times criados'))
        
        # Criar Partidas Futuras
        now = timezone.now()
        
        matches_data = [
            # Premier League - Próximos dias
            (premier_league, man_city, arsenal, now + timedelta(days=1, hours=15)),
            (premier_league, liverpool, chelsea, now + timedelta(days=1, hours=17, minutes=30)),
            (premier_league, man_utd, tottenham, now + timedelta(days=2, hours=16)),
            (premier_league, arsenal, liverpool, now + timedelta(days=3, hours=20)),
            (premier_league, chelsea, man_city, now + timedelta(days=4, hours=15)),
            
            # La Liga
            (la_liga, real_madrid, barcelona, now + timedelta(days=2, hours=21)),
            (la_liga, atletico, sevilla, now + timedelta(days=2, hours=19)),
            (la_liga, barcelona, atletico, now + timedelta(days=5, hours=21)),
            (la_liga, sevilla, real_madrid, now + timedelta(days=6, hours=18)),
            
            # Serie A
            (serie_a, inter, juventus, now + timedelta(days=3, hours=20, minutes=45)),
            (serie_a, milan, napoli, now + timedelta(days=3, hours=18)),
            (serie_a, juventus, milan, now + timedelta(days=5, hours=20)),
            (serie_a, napoli, inter, now + timedelta(days=6, hours=20, minutes=45)),
        ]
        
        for league, home, away, match_date in matches_data:
            Match.objects.create(
                league=league,
                home_team=home,
                away_team=away,
                match_date=match_date,
                status='scheduled',
                round=f'Rodada {(timezone.now().day % 10) + 1}',
                is_analysis_available=True
            )
        
        self.stdout.write(self.style.SUCCESS(f'✓ {Match.objects.count()} partidas criadas'))
        
        # Criar algumas partidas já finalizadas (para histórico)
        finished_matches = [
            (premier_league, man_city, liverpool, now - timedelta(days=7), 2, 1),
            (premier_league, arsenal, chelsea, now - timedelta(days=6), 3, 1),
            (la_liga, barcelona, real_madrid, now - timedelta(days=5), 2, 2),
            (serie_a, inter, milan, now - timedelta(days=4), 1, 0),
        ]
        
        for league, home, away, match_date, home_score, away_score in finished_matches:
            Match.objects.create(
                league=league,
                home_team=home,
                away_team=away,
                match_date=match_date,
                status='finished',
                home_score=home_score,
                away_score=away_score,
                is_analysis_available=False
            )
        
        total_matches = Match.objects.count()
        upcoming = Match.objects.filter(status='scheduled').count()
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Banco populado com sucesso!'))
        self.stdout.write(f'   • {League.objects.count()} ligas')
        self.stdout.write(f'   • {Team.objects.count()} times')
        self.stdout.write(f'   • {total_matches} partidas ({upcoming} futuras)')
