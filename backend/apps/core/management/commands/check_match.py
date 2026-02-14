"""
Comando Django para verificar resultado de uma partida
Usage: python manage.py check_match 1520391
"""
from django.core.management.base import BaseCommand
from apps.core.models import Match
from apps.analysis.services.api_football_service import FootballAPIService


class Command(BaseCommand):
    help = 'Verifica o resultado de uma partida pelo ID'

    def add_arguments(self, parser):
        parser.add_argument('match_id', type=int, help='ID da partida na API-Football')

    def handle(self, *args, **options):
        match_id = options['match_id']
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write(f"RESULTADO DA PARTIDA {match_id}")
        self.stdout.write("="*80)
        
        # Tentar banco de dados primeiro
        self.stdout.write("\n🔍 Buscando no banco de dados...")
        match = Match.objects.filter(api_id=match_id).first()
        
        if match and match.home_score is not None:
            self.stdout.write(self.style.SUCCESS("✅ Encontrado no banco!"))
            self._display_result(match.home_team, match.away_team, match.home_score, match.away_score, match.league, match.status)
            return
        
        # Buscar via API
        self.stdout.write("\n🌐 Buscando via API-Football...")
        api = FootballAPIService()
        fixture = api.fetch_fixture_by_id(match_id)
        
        if not fixture:
            self.stdout.write(self.style.ERROR("❌ Partida não encontrada"))
            return
        
        teams = fixture.get('teams', {})
        goals = fixture.get('goals', {})
        league = fixture.get('league', {})
        status_data = fixture.get('fixture', {}).get('status', {})
        
        home_team = teams.get('home', {}).get('name')
        away_team = teams.get('away', {}).get('name')
        home_score = goals.get('home')
        away_score = goals.get('away')
        league_name = f"{league.get('name')} - {league.get('round')}"
        status = status_data.get('long')
        
        if home_score is None:
            self.stdout.write(self.style.WARNING(f"\n⏳ Partida ainda não foi realizada"))
            self.stdout.write(f"   {home_team} vs {away_team}")
            self.stdout.write(f"   {league_name}")
            self.stdout.write(f"   Status: {status}")
            return
        
        self.stdout.write(self.style.SUCCESS("\n✅ Dados recebidos!"))
        self._display_result(home_team, away_team, home_score, away_score, league_name, status)
    
    def _display_result(self, home_team, away_team, home_score, away_score, league, status):
        """Exibe o resultado formatado"""
        total = home_score + away_score
        
        self.stdout.write(f"\n📊 INFORMAÇÕES:")
        self.stdout.write(f"   {home_team} vs {away_team}")
        self.stdout.write(f"   Liga: {league}")
        self.stdout.write(f"   Status: {status}")
        
        self.stdout.write(f"\n⚽ PLACAR FINAL:")
        self.stdout.write(self.style.SUCCESS(f"   {home_team}: {home_score}"))
        self.stdout.write(self.style.SUCCESS(f"   {away_team}: {away_score}"))
        
        # Resultado 1X2
        if home_score > away_score:
            resultado = f"Casa venceu ({home_team})"
            style = self.style.SUCCESS
        elif away_score > home_score:
            resultado = f"Fora venceu ({away_team})"
            style = self.style.SUCCESS
        else:
            resultado = "Empate"
            style = self.style.WARNING
        
        self.stdout.write(f"\n📈 RESULTADO 1X2: {style(resultado)}")
        
        self.stdout.write(f"\n📊 VERIFICAÇÃO DOS MERCADOS:")
        self.stdout.write(f"   Total de gols: {total}")
        
        # Over/Under 2.5
        if total > 2.5:
            self.stdout.write(self.style.SUCCESS(f"   Over 2.5: ✅ GREEN ({total} gols)"))
            self.stdout.write(self.style.ERROR(f"   Under 2.5: ❌ RED ({total} gols)"))
        else:
            self.stdout.write(self.style.ERROR(f"   Over 2.5: ❌ RED ({total} gols)"))
            self.stdout.write(self.style.SUCCESS(f"   Under 2.5: ✅ GREEN ({total} gols)"))
        
        # BTTS
        if home_score > 0 and away_score > 0:
            self.stdout.write(self.style.SUCCESS(f"   BTTS (Ambos Marcam): ✅ GREEN"))
        else:
            self.stdout.write(self.style.ERROR(f"   BTTS (Ambos Marcam): ❌ RED"))
        
        # Over/Under 1.5
        if total > 1.5:
            self.stdout.write(self.style.SUCCESS(f"   Over 1.5: ✅ GREEN ({total} gols)"))
        else:
            self.stdout.write(self.style.ERROR(f"   Over 1.5: ❌ RED ({total} gols)"))
        
        self.stdout.write("\n" + "="*80)
