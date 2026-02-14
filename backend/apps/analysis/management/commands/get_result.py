"""
Comando Django para verificar resultado de uma partida
Usage: python manage.py get_result 1520391
"""
from django.core.management.base import BaseCommand
from apps.analysis.services.api_football_service import APIFootballService


class Command(BaseCommand):
    help = 'Busca o resultado de uma partida pelo ID'

    def add_arguments(self, parser):
        parser.add_argument('match_id', type=int, help='ID da partida na API-Football')

    def handle(self, *args, **options):
        match_id = options['match_id']
        
        self.stdout.write("\n" + "="*80)
        self.stdout.write(f"RESULTADO DA PARTIDA {match_id}")
        self.stdout.write("="*80)
        
        # Buscar via API
        self.stdout.write("\nBuscando via API-Football...")
        api = APIFootballService()
        fixture = api.fetch_fixture_details(match_id)
        
        if not fixture:
            self.stdout.write(self.style.ERROR("\nPartida nao encontrada ou erro na API"))
            return
        
        # DEBUG: Mostrar estrutura da resposta
        import json
        self.stdout.write("\nDEBUG - Estrutura da resposta:")
        self.stdout.write(json.dumps(fixture, indent=2, ensure_ascii=False))
        
        # Extrair dados da estrutura correta
        home_team_data = fixture.get('home_team', {})
        away_team_data = fixture.get('away_team', {})
        league = fixture.get('league', {})
        status_data = fixture.get('status', 'N/A')
        score = fixture.get('score', {})
        goals = fixture.get('goals', {})
        
        home_team = home_team_data.get('name')
        away_team = away_team_data.get('name')
        
        # Tentar pegar score de diferentes campos possiveis
        home_score = goals.get('home') if goals else None
        away_score = goals.get('away') if goals else None
        
        if home_score is None and score:
            home_score = score.get('fulltime', {}).get('home')
            away_score = score.get('fulltime', {}).get('away')
        league_name = league.get('name', 'N/A')
        league_round = league.get('round', 'N/A')
        status = status_data if isinstance(status_data, str) else status_data.get('long', 'N/A')
        
        self.stdout.write(self.style.SUCCESS("\nDados recebidos!"))
        
        self.stdout.write(f"\nINFORMACOES:")
        self.stdout.write(f"   Partida: {home_team} vs {away_team}")
        self.stdout.write(f"   Liga: {league_name}")
        self.stdout.write(f"   Fase: {league_round}")
        self.stdout.write(f"   Status: {status}")
        
        if home_score is None or away_score is None:
            self.stdout.write(self.style.WARNING(f"\nPartida ainda nao foi realizada ou nao tem placar"))
            return
        
        total = home_score + away_score
        
        self.stdout.write(f"\n" + "="*80)
        self.stdout.write(f"PLACAR FINAL:")
        self.stdout.write(f"="*80)
        self.stdout.write(self.style.SUCCESS(f"   {home_team}: {home_score}"))
        self.stdout.write(self.style.SUCCESS(f"   {away_team}: {away_score}"))
        
        # Placar por tempo
        halftime = score.get('halftime', {})
        fulltime = score.get('fulltime', {})
        
        if halftime and halftime.get('home') is not None:
            self.stdout.write(f"\nPLACARES POR TEMPO:")
            self.stdout.write(f"   Intervalo: {halftime.get('home')} - {halftime.get('away')}")
            if fulltime and fulltime.get('home') is not None:
                self.stdout.write(f"   Final: {fulltime.get('home')} - {fulltime.get('away')}")
        
        # Resultado 1X2
        self.stdout.write(f"\n" + "="*80)
        if home_score > away_score:
            self.stdout.write(self.style.SUCCESS(f"RESULTADO 1X2: Casa venceu ({home_team})"))
        elif away_score > home_score:
            self.stdout.write(self.style.SUCCESS(f"RESULTADO 1X2: Fora venceu ({away_team})"))
        else:
            self.stdout.write(self.style.WARNING(f"RESULTADO 1X2: Empate"))
        
        self.stdout.write(f"="*80)
        
        self.stdout.write(f"\nVERIFICACAO DOS MERCADOS:")
        self.stdout.write(f"   Total de gols: {total}")
        
        # Over/Under 2.5
        if total > 2.5:
            self.stdout.write(self.style.SUCCESS(f"   Over 2.5: GREEN ({total} gols)"))
            self.stdout.write(self.style.ERROR(f"   Under 2.5: RED ({total} gols)"))
        else:
            self.stdout.write(self.style.ERROR(f"   Over 2.5: RED ({total} gols)"))
            self.stdout.write(self.style.SUCCESS(f"   Under 2.5: GREEN ({total} gols)"))
        
        # BTTS
        if home_score > 0 and away_score > 0:
            self.stdout.write(self.style.SUCCESS(f"   BTTS (Ambos Marcam): GREEN"))
        else:
            self.stdout.write(self.style.ERROR(f"   BTTS (Ambos Marcam): RED"))
        
        # Over/Under 1.5
        if total > 1.5:
            self.stdout.write(self.style.SUCCESS(f"   Over 1.5: GREEN ({total} gols)"))
        else:
            self.stdout.write(self.style.ERROR(f"   Over 1.5: RED ({total} gols)"))
        
        # Over 3.5
        if total > 3.5:
            self.stdout.write(self.style.SUCCESS(f"   Over 3.5: GREEN ({total} gols)"))
        else:
            self.stdout.write(self.style.ERROR(f"   Over 3.5: RED ({total} gols)"))
        
        self.stdout.write("\n" + "="*80)
