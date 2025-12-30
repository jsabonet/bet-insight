from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta, datetime
from .models import League, Team, Match
from .serializers import LeagueSerializer, TeamSerializer, MatchListSerializer, MatchDetailSerializer
from .services.football_api import FootballAPIService
from apps.analysis.services.ai_analyzer import AIAnalyzer
import logging

logger = logging.getLogger(__name__)


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Ligas"""
    queryset = League.objects.filter(is_active=True)
    serializer_class = LeagueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'country']
    ordering_fields = ['priority', 'name']
    ordering = ['-priority']


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Times"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'country']


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Partidas"""
    queryset = Match.objects.select_related('league', 'home_team', 'away_team').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['league', 'status']
    ordering_fields = ['match_date']
    ordering = ['match_date']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MatchDetailSerializer
        return MatchListSerializer
    
    def _generate_mock_matches(self, date):
        """Gerar partidas de exemplo para teste"""
        from datetime import datetime, timedelta
        from .models import Team, League as LeagueModel
        import random
        
        base_time = datetime.strptime(date, '%Y-%m-%d')
        
        mock_teams = [
            # Moçambique - Moçambola
            ('Costa do Sol', 'Ferroviário de Maputo', 'Moçambola', 'Moçambique'),
            ('UD Songo', 'Ferroviário de Nampula', 'Moçambola', 'Moçambique'),
            
            # África do Sul - DSTV Premiership
            ('Mamelodi Sundowns', 'Orlando Pirates', 'DSTV Premiership', 'África do Sul'),
            ('Kaizer Chiefs', 'SuperSport United', 'DSTV Premiership', 'África do Sul'),
            
            # CAF Champions League
            ('Al Ahly', 'Mamelodi Sundowns', 'CAF Champions League', 'África'),
            ('TP Mazembe', 'Wydad Casablanca', 'CAF Champions League', 'África'),
            
            # Premier League
            ('Manchester United', 'Liverpool', 'Premier League', 'Inglaterra'),
            ('Arsenal', 'Chelsea', 'Premier League', 'Inglaterra'),
            
            # La Liga
            ('Barcelona', 'Real Madrid', 'La Liga', 'Espanha'),
            ('Atlético Madrid', 'Sevilla', 'La Liga', 'Espanha'),
            
            # Bundesliga
            ('Bayern Munich', 'Borussia Dortmund', 'Bundesliga', 'Alemanha'),
            
            # Serie A
            ('Juventus', 'Inter Milan', 'Serie A', 'Itália'),
            
            # Ligue 1
            ('PSG', 'Marseille', 'Ligue 1', 'França'),
            
            # Primeira Liga
            ('Benfica', 'Porto', 'Primeira Liga', 'Portugal'),
            
            # UEFA Champions League
            ('Real Madrid', 'Manchester City', 'UEFA Champions League', 'Europa'),
            
            # Brasileirão
            ('Flamengo', 'Palmeiras', 'Brasileirão Série A', 'Brasil'),
            
            # Saudi Pro League
            ('Al-Nassr', 'Al-Hilal', 'Saudi Pro League', 'Arábia Saudita'),
            
            # MLS
            ('LA Galaxy', 'Inter Miami', 'MLS', 'Estados Unidos'),
        ]
        
        matches = []
        for i, (home_name, away_name, league_name, country) in enumerate(mock_teams):
            match_time = base_time + timedelta(hours=14 + (i * 2))
            
            # Buscar logos reais do banco
            home_team = Team.objects.filter(name=home_name).first()
            away_team = Team.objects.filter(name=away_name).first()
            league = LeagueModel.objects.filter(name=league_name).first()
            
            # Usar logos reais ou fallback
            home_logo = home_team.logo if home_team and home_team.logo else f'https://ui-avatars.com/api/?name={home_name.replace(" ", "+")}&background=random&size=128'
            away_logo = away_team.logo if away_team and away_team.logo else f'https://ui-avatars.com/api/?name={away_name.replace(" ", "+")}&background=random&size=128'
            league_logo = league.logo if league and league.logo else f'https://ui-avatars.com/api/?name={league_name.replace(" ", "+")}&background=0D47A1&color=fff&size=128'
            
            matches.append({
                'id': 1000000 + i,
                'home_team': {
                    'name': home_name,
                    'logo': home_logo,
                },
                'away_team': {
                    'name': away_name,
                    'logo': away_logo,
                },
                'league': {
                    'name': league_name,
                    'logo': league_logo,
                    'country': country,
                },
                'match_date': match_time.isoformat() + 'Z',
                'date': match_time.isoformat() + 'Z',
                'status': 'NS',
                'venue': f'{home_name} Stadium',
                'home_score': None,
                'away_score': None,
            })
        
        return matches
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Partidas futuras (próximos 7 dias)"""
        now = timezone.now()
        future = now + timedelta(days=7)
        
        matches = self.get_queryset().filter(
            status='scheduled',
            match_date__gte=now,
            match_date__lte=future,
            is_analysis_available=True
        )
        
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Partidas de hoje"""
        today = timezone.now().date()
        
        matches = self.get_queryset().filter(
            match_date__date=today,
            is_analysis_available=True
        )
        
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def live(self, request):
        """Partidas ao vivo"""
        matches = self.get_queryset().filter(status='live')
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def from_api(self, request):
        """Buscar partidas diretamente da API-Football"""
        date = request.query_params.get('date', datetime.now().strftime('%Y-%m-%d'))
        force_real = request.query_params.get('force_real', 'false').lower() == 'true'
        
        football_api = FootballAPIService()
        all_matches = []
        
        # Tentar buscar partidas dos próximos 14 dias
        logger.info("Buscando partidas reais (próximos 14 dias)...")
        
        for day_offset in range(15):
            search_date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
            result = football_api.get_fixtures_by_date(search_date)
            
            if result['success'] and result['fixtures']:
                all_matches.extend(result['fixtures'])
                logger.info(f"{search_date}: {len(result['fixtures'])} partidas")
        
        # Também buscar partidas ao vivo
        live_result = football_api.get_live_fixtures()
        if live_result['success'] and live_result['fixtures']:
            all_matches.extend(live_result['fixtures'])
            logger.info(f"Partidas ao vivo: {len(live_result['fixtures'])}")
        
        # Se encontrou partidas reais, retorná-las
        if all_matches:
            # Remover duplicatas por ID
            unique_matches = {m['fixture']['id']: m for m in all_matches}.values()
            matches_list = list(unique_matches)
            
            # Ordenar por data
            matches_list.sort(key=lambda x: x['fixture']['date'])
            
            logger.info(f"Total de {len(matches_list)} partidas únicas encontradas")
            matches = self._format_api_matches(matches_list[:50])  # Limitar a 50
            
            return Response({
                'date': date,
                'count': len(matches),
                'matches': matches,
                'is_mock': False,
                'source': 'api-football'
            })
        
        # Se force_real está ativo, retornar erro em vez de mock
        if force_real:
            return Response(
                {'error': 'Nenhuma partida real disponível no momento'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Se não houver partidas da API, retornar dados de exemplo
        logger.warning(f"Nenhuma partida real encontrada. Retornando dados de exemplo.")
        logger.info("Período de pausa (fim de ano). Partidas reais voltarão em Janeiro 2026.")
        mock_matches = self._generate_mock_matches(date)
        return Response({
            'date': date,
            'count': len(mock_matches),
            'matches': mock_matches,
            'is_mock': True,
            'source': 'mock'
        })

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def api_detail(self, request):
        """Detalhes de partida por ID diretamente da API-Football (sem DB)."""
        fixture_id = request.query_params.get('id')
        if not fixture_id:
            return Response({'error': 'Parâmetro id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            fixture_id = int(fixture_id)
        except ValueError:
            return Response({'error': 'Parâmetro id deve ser numérico'}, status=status.HTTP_400_BAD_REQUEST)

        football_api = FootballAPIService()
        result = football_api.get_fixture_by_id(fixture_id)

        if not result['success']:
            return Response(
                {'error': result.get('error'), 'details': result.get('details'), 'code': result.get('error_code')},
                status=result.get('http_status', status.HTTP_502_BAD_GATEWAY)
            )

        # Formatar resposta para o frontend reutilizando o formato das listas
        formatted = self._format_api_matches([result['fixture']])
        if not formatted:
            return Response({'error': 'Partida não encontrada'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'match': formatted[0], 'source': 'api-football'})
    
    def _format_api_matches(self, fixtures):
        """Formatar partidas da API para o formato do frontend"""
        matches = []
        for fixture in fixtures:
            match_date = fixture['fixture']['date']
            
            matches.append({
                'id': fixture['fixture']['id'],
                'home_team': {
                    'name': fixture['teams']['home']['name'],
                    'logo': fixture['teams']['home']['logo'],
                },
                'away_team': {
                    'name': fixture['teams']['away']['name'],
                    'logo': fixture['teams']['away']['logo'],
                },
                'league': {
                    'name': fixture['league']['name'],
                    'logo': fixture['league']['logo'],
                    'country': fixture['league'].get('country', ''),
                },
                'match_date': match_date,
                'date': match_date,
                'status': fixture['fixture']['status']['short'],
                'venue': fixture['fixture'].get('venue', {}).get('name'),
                'home_score': fixture['goals'].get('home'),
                'away_score': fixture['goals'].get('away'),
            })
        
        return matches
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Gerar análise com IA para uma partida"""
        match = self.get_object()
        
        # Verificar se usuário pode analisar
        if not request.user.can_analyze():
            return Response(
                {'error': 'Limite diário de análises atingido. Faça upgrade para Premium!'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Preparar dados para análise
        match_data = {
            'home_team': {'name': match.home_team.name if hasattr(match, 'home_team') else str(match.home_team)},
            'away_team': {'name': match.away_team.name if hasattr(match, 'away_team') else str(match.away_team)},
            'league': match.league.name if hasattr(match, 'league') else str(match.league),
            'date': str(match.match_date)
        }
        
        # Gerar análise com IA
        analyzer = AIAnalyzer()
        result = analyzer.analyze_match(match_data)
        
        if not result['success']:
            return Response(
                {'error': result.get('error'), 'details': result.get('details'), 'code': result.get('error_code')},
                status=result.get('http_status', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
        
        # Incrementar contador de análises do usuário
        request.user.increment_analysis_count()
        
        # TODO: Salvar análise no banco de dados
        
        return Response({
            'analysis': result['analysis'],
            'confidence': result['confidence'],
            'remaining_analyses': request.user.get_remaining_analyses()
        })
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def quick_analyze(self, request):
        """Análise rápida sem salvar (para preview)"""
        home_team = request.data.get('home_team')
        away_team = request.data.get('away_team')
        
        if not home_team or not away_team:
            return Response(
                {'error': 'home_team e away_team são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        match_data = {
            'home_team': {'name': home_team},
            'away_team': {'name': away_team},
            'league': request.data.get('league', 'Liga desconhecida')
        }
        
        analyzer = AIAnalyzer()
        result = analyzer.analyze_match(match_data)
        
        if not result['success']:
            return Response(
                {'error': result.get('error'), 'details': result.get('details'), 'code': result.get('error_code')},
                status=result.get('http_status', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
        
        return Response({
            'analysis': result['analysis'],
            'confidence': result['confidence']
        })

