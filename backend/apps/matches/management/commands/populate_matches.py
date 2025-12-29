from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.matches.models import League, Team, Match


class Command(BaseCommand):
    help = 'Popula banco de dados com partidas de teste'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando dados de teste...')
        
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
        
        # Criar Times - Premier League
        man_city = Team.objects.create(name='Manchester City', country='Inglaterra')
        liverpool = Team.objects.create(name='Liverpool', country='Inglaterra')
        arsenal = Team.objects.create(name='Arsenal', country='Inglaterra')
        chelsea = Team.objects.create(name='Chelsea', country='Inglaterra')
        man_utd = Team.objects.create(name='Manchester United', country='Inglaterra')
        tottenham = Team.objects.create(name='Tottenham', country='Inglaterra')
        
        # Times - La Liga
        real_madrid = Team.objects.create(name='Real Madrid', country='Espanha')
        barcelona = Team.objects.create(name='Barcelona', country='Espanha')
        atletico = Team.objects.create(name='Atlético Madrid', country='Espanha')
        sevilla = Team.objects.create(name='Sevilla', country='Espanha')
        
        # Times - Serie A
        inter = Team.objects.create(name='Inter Milan', country='Itália')
        juventus = Team.objects.create(name='Juventus', country='Itália')
        milan = Team.objects.create(name='AC Milan', country='Itália')
        napoli = Team.objects.create(name='Napoli', country='Itália')
        
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
