from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
    
    @action(detail=False, methods=['get'])
    def from_api(self, request):
        """Buscar partidas diretamente da API-Football"""
        date = request.query_params.get('date', datetime.now().strftime('%Y-%m-%d'))
        
        football_api = FootballAPIService()
        result = football_api.get_fixtures_by_date(date)
        
        if not result['success']:
            return Response(
                {'error': result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Formatar resposta para frontend
        matches = []
        for fixture in result['fixtures'][:20]:  # Limitar a 20 partidas
            # Converter timestamp Unix para ISO 8601 se necessário
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
                'match_date': match_date,  # Usar match_date para consistência
                'date': match_date,  # Manter date também para retrocompatibilidade
                'status': fixture['fixture']['status']['short'],
                'venue': fixture['fixture'].get('venue', {}).get('name'),
                'home_score': fixture['goals'].get('home'),
                'away_score': fixture['goals'].get('away'),
            })
        
        return Response({
            'date': date,
            'count': len(matches),
            'matches': matches
        })
    
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
                {'error': result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Incrementar contador de análises do usuário
        request.user.increment_analysis_count()
        
        # TODO: Salvar análise no banco de dados
        
        return Response({
            'analysis': result['analysis'],
            'confidence': result['confidence'],
            'remaining_analyses': request.user.get_remaining_analyses()
        })
    
    @action(detail=False, methods=['post'])
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
                {'error': result['error']},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'analysis': result['analysis'],
            'confidence': result['confidence']
        })

