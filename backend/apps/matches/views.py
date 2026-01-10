from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta, datetime
from .models import League, Team, Match
from .serializers import LeagueSerializer, TeamSerializer, MatchListSerializer, MatchDetailSerializer
from .services.football_api import FootballAPIService
from .services.id_mapper import APIIDMapper
from apps.analysis.services.ai_analyzer import AIAnalyzer
from apps.analysis.models import Analysis
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
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def live(self, request):
        """Partidas ao vivo - busca direto da API-Football em tempo real COM estatísticas e escalações"""
        logger.info("🔴 Buscando partidas AO VIVO da API-Football...")
        
        football_api = FootballAPIService()
        result = football_api.get_live_fixtures()
        
        if result['success']:
            fixtures = result['fixtures']
            logger.info(f"✅ {len(fixtures)} partidas ao vivo encontradas")
            
            # Para cada partida ao vivo, buscar dados adicionais
            enriched_fixtures = []
            for fixture in fixtures:
                fixture_id = fixture['fixture']['id']
                
                # Buscar eventos (gols, cartões, etc.)
                events_result = football_api.get_fixture_events(fixture_id)
                if events_result['success']:
                    fixture['events'] = events_result.get('events', [])
                else:
                    fixture['events'] = []
                
                # Buscar estatísticas detalhadas
                stats_result = football_api.get_fixture_statistics(fixture_id)
                if stats_result['success']:
                    fixture['statistics'] = stats_result.get('statistics', [])
                else:
                    fixture['statistics'] = []
                
                # Buscar escalações
                lineups_result = football_api.get_fixture_lineups(fixture_id)
                if lineups_result['success']:
                    fixture['lineups'] = lineups_result.get('lineups', [])
                else:
                    fixture['lineups'] = []
                
                enriched_fixtures.append(fixture)
            
            logger.info(f"📊 Dados enriquecidos para {len(enriched_fixtures)} partidas ao vivo")
            
            # Formatar partidas usando a mesma função de from_api
            matches = self._format_api_matches(enriched_fixtures)
            
            return Response({
                'count': len(matches),
                'matches': matches,
                'source': 'api-football-live'
            })
        else:
            logger.error(f"❌ Erro ao buscar partidas ao vivo: {result.get('error')}")
            return Response({
                'count': 0,
                'matches': [],
                'error': result.get('error'),
                'source': 'api-football-live'
            })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def from_api(self, request):
        """Buscar partidas diretamente da API-Football (próximos 14 dias) com cache"""
        date = request.query_params.get('date', datetime.now().strftime('%Y-%m-%d'))
        force_real = request.query_params.get('force_real', 'false').lower() == 'true'
        
        # Cache key baseado na hora atual (atualiza a cada hora)
        cache_key = f'matches_api_{datetime.now().strftime("%Y%m%d_%H")}'
        
        # Tentar buscar do cache (30 minutos)
        if not force_real:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"✅ CACHE HIT: Retornando {len(cached_data['matches'])} partidas do cache")
                return Response(cached_data)
        
        logger.info(f"❌ CACHE MISS: Buscando partidas da API...")
        football_api = FootballAPIService()
        all_matches = []
        
        # Buscar apenas partidas futuras (próximos 14 dias)
        # Plataforma de apostas: foco em jogos que ainda não ocorreram
        logger.info("Buscando partidas futuras (próximos 14 dias)...")
        
        for day_offset in range(15):
            search_date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
            result = football_api.get_fixtures_by_date(search_date)
            
            if result['success'] and result['fixtures']:
                all_matches.extend(result['fixtures'])
                logger.info(f"{search_date}: {len(result['fixtures'])} partidas")
        
        # Se encontrou partidas reais, retorná-las
        if all_matches:
            # Remover duplicatas por ID
            unique_matches = {m['fixture']['id']: m for m in all_matches}.values()
            matches_list = list(unique_matches)
            
            # Ordenar por data
            matches_list.sort(key=lambda x: x['fixture']['date'])
            
            logger.info(f"Total de {len(matches_list)} partidas únicas encontradas")
            # Remover limite - carregar TODAS as partidas
            matches = self._format_api_matches(matches_list)
            
            response_data = {
                'date': date,
                'count': len(matches),
                'matches': matches,
                'is_mock': False,
                'source': 'api-football'
            }
            
            # Cachear resultado por 30 minutos
            cache.set(cache_key, response_data, 60 * 30)
            logger.info(f"Cache atualizado com {len(matches)} partidas")
            
            return Response(response_data)
        
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
    def search(self, request):
        """Busca inteligente de partidas - busca na API se não encontrar localmente"""
        query = request.query_params.get('q', '').strip()
        
        if not query or len(query) < 3:
            return Response({
                'error': 'Query deve ter pelo menos 3 caracteres',
                'matches': []
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Busca por: {query}")
        
        # Tentar buscar do cache primeiro
        cache_key = f'matches_api_{datetime.now().strftime("%Y%m%d_%H")}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            matches = cached_data.get('matches', [])
            query_lower = query.lower()
            
            # Busca local em cache
            filtered = [
                m for m in matches
                if query_lower in m['home_team']['name'].lower()
                or query_lower in m['away_team']['name'].lower()
                or query_lower in m['league']['name'].lower()
            ]
            
            if filtered:
                logger.info(f"Encontradas {len(filtered)} partidas no cache")
                return Response({
                    'query': query,
                    'count': len(filtered),
                    'matches': filtered,
                    'source': 'cache'
                })
        
        # Se não encontrou no cache, buscar direto na API
        logger.info(f"Partida não encontrada localmente, buscando na API...")
        football_api = FootballAPIService()
        
        # Buscar nos próximos 14 dias por time
        all_matches = []
        for day_offset in range(15):
            search_date = (datetime.now() + timedelta(days=day_offset)).strftime('%Y-%m-%d')
            result = football_api.get_fixtures_by_date(search_date)
            
            if result['success'] and result['fixtures']:
                all_matches.extend(result['fixtures'])
        
        if all_matches:
            # Filtrar por query
            query_lower = query.lower()
            matches = self._format_api_matches(all_matches)
            
            filtered = [
                m for m in matches
                if query_lower in m['home_team']['name'].lower()
                or query_lower in m['away_team']['name'].lower()
                or query_lower in m['league']['name'].lower()
            ]
            
            logger.info(f"Encontradas {len(filtered)} partidas na API")
            return Response({
                'query': query,
                'count': len(filtered),
                'matches': filtered,
                'source': 'api-football'
            })
        
        return Response({
            'query': query,
            'count': 0,
            'matches': [],
            'source': 'not-found'
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

        # Buscar eventos (gols, cartões, etc.) da partida
        events_result = football_api.get_fixture_events(fixture_id)
        if events_result['success']:
            result['fixture']['events'] = events_result.get('events', [])
        else:
            result['fixture']['events'] = []

        # Buscar estatísticas detalhadas (chutes, escanteios, etc.)
        stats_result = football_api.get_fixture_statistics(fixture_id)
        if stats_result['success']:
            result['fixture']['statistics'] = stats_result.get('statistics', [])
        else:
            result['fixture']['statistics'] = []
        
        # Buscar escalações (lineups)
        lineups_result = football_api.get_fixture_lineups(fixture_id)
        if lineups_result['success']:
            result['fixture']['lineups'] = lineups_result.get('lineups', [])
        else:
            result['fixture']['lineups'] = []
        
        # Buscar confronto direto (H2H)
        fixture_data = result['fixture']
        home_team_id = fixture_data['teams']['home']['id']
        away_team_id = fixture_data['teams']['away']['id']
        league_id = fixture_data['league']['id']
        
        h2h_result = football_api.get_head_to_head(home_team_id, away_team_id, last=10)
        if h2h_result['success']:
            result['fixture']['h2h'] = h2h_result.get('matches', [])
        else:
            result['fixture']['h2h'] = []
        
        # Buscar últimos 5 jogos de cada time
        home_last_result = football_api.get_team_last_matches(home_team_id, last=5)
        if home_last_result['success']:
            result['fixture']['home_last_matches'] = home_last_result.get('matches', [])
        else:
            result['fixture']['home_last_matches'] = []
        
        away_last_result = football_api.get_team_last_matches(away_team_id, last=5)
        if away_last_result['success']:
            result['fixture']['away_last_matches'] = away_last_result.get('matches', [])
        else:
            result['fixture']['away_last_matches'] = []
        
        # Buscar classificação da liga
        standings_result = football_api.get_standings(league_id, season=2025)
        if standings_result['success']:
            result['fixture']['standings'] = standings_result.get('standings', [])
        else:
            result['fixture']['standings'] = []

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
            fixture_id = fixture['fixture']['id']  # ID real da API
            
            # Enriquecer lineups com URLs de fotos dos jogadores
            lineups = fixture.get('lineups', [])
            for lineup in lineups:
                # Adicionar fotos aos titulares
                for player_data in lineup.get('startXI', []):
                    player = player_data.get('player', {})
                    player_id = player.get('id')
                    if player_id and not player.get('photo'):
                        player['photo'] = f"https://media.api-sports.io/football/players/{player_id}.png"
                
                # Adicionar fotos aos substitutos
                for player_data in lineup.get('substitutes', []):
                    player = player_data.get('player', {})
                    player_id = player.get('id')
                    if player_id and not player.get('photo'):
                        player['photo'] = f"https://media.api-sports.io/football/players/{player_id}.png"
            
            matches.append({
                'id': fixture_id,  # Usar ID real em vez de temporário
                'api_football_id': fixture_id,  # ID para buscar dados adicionais
                'home_team': {
                    'id': fixture['teams']['home']['id'],
                    'name': fixture['teams']['home']['name'],
                    'logo': fixture['teams']['home']['logo'],
                },
                'away_team': {
                    'id': fixture['teams']['away']['id'],
                    'name': fixture['teams']['away']['name'],
                    'logo': fixture['teams']['away']['logo'],
                },
                'league': {
                    'id': fixture['league']['id'],
                    'name': fixture['league']['name'],
                    'logo': fixture['league']['logo'],
                    'country': fixture['league'].get('country', ''),
                },
                'match_date': match_date,
                'date': match_date,
                'status': fixture['fixture']['status']['short'],
                'venue': fixture['fixture'].get('venue', {}).get('name'),
                'referee': fixture['fixture'].get('referee'),  # Adicionar árbitro
                'home_score': fixture['goals'].get('home'),
                'away_score': fixture['goals'].get('away'),
                'events': fixture.get('events', []),  # Adicionar eventos (gols, cartões, etc.)
                'statistics': fixture.get('statistics', []),  # Adicionar estatísticas detalhadas
                'lineups': lineups,  # Adicionar escalações com fotos
                'h2h': fixture.get('h2h', []),  # Confrontos diretos
                'home_last_matches': fixture.get('home_last_matches', []),  # Últimos jogos casa
                'away_last_matches': fixture.get('away_last_matches', []),  # Últimos jogos fora
                'standings': fixture.get('standings', []),  # Classificação da liga
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
        
        # Criar e salvar análise no banco de dados
        try:
            # Heurística simples para probabilidades e xG quando IA não fornece estruturado
            home_p, draw_p, away_p = 40.0, 30.0, 30.0
            home_xg, away_xg = 1.5, 1.3
            prediction = 'home'
            confidence = int(result.get('confidence', 3) or 3)
            reasoning = result.get('analysis') or 'Análise gerada pela IA.'
            key_factors = ['Mando de campo', 'Forma recente']

            analysis = Analysis.objects.create(
                user=request.user,
                match=match,
                prediction=prediction,
                confidence=confidence,
                home_probability=home_p,
                draw_probability=draw_p,
                away_probability=away_p,
                home_xg=home_xg,
                away_xg=away_xg,
                reasoning=reasoning,
                key_factors=key_factors,
                analysis_data={'source': 'ai', 'fallback': True}
            )
        except Exception:
            # Mesmo que salvar falhe, ainda retornamos a análise textual
            analysis = None
        
        # Incrementar contador de análises do usuário
        request.user.increment_analysis_count()
        
        payload = {
            'analysis': result['analysis'],
            'confidence': result['confidence'],
            'remaining_analyses': request.user.get_remaining_analyses()
        }
        if analysis:
            payload['saved'] = True
            payload['saved_analysis'] = {
                'id': analysis.id,
                'created_at': analysis.created_at,
            }
        
        return Response(payload)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def quick_analyze(self, request):
        """Análise rápida sem salvar (para preview) - COM ENRIQUECIMENTO DE DADOS"""
        logger.info(f"\n{'='*80}")
        logger.info(f"📥 QUICK_ANALYZE: Requisição recebida")
        logger.info(f"{'='*80}")
        
        home_team = request.data.get('home_team')
        away_team = request.data.get('away_team')
        
        logger.info(f"🏠 Home Team: {home_team}")
        logger.info(f"✈️ Away Team: {away_team}")
        logger.info(f"🏆 League: {request.data.get('league')}")
        logger.info(f"📅 Date: {request.data.get('date')}")
        logger.info(f"🆔 API ID: {request.data.get('api_id')}")
        logger.info(f"🆔 Football Data ID: {request.data.get('football_data_id')}")
        
        if not home_team or not away_team:
            return Response(
                {'error': 'home_team e away_team são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        match_data = {
            'home_team': {'name': home_team},
            'away_team': {'name': away_team},
            'league': request.data.get('league', 'Liga desconhecida'),
            'date': request.data.get('date'),
            'status': request.data.get('status'),
            'venue': request.data.get('venue'),
            'home_score': request.data.get('home_score'),
            'away_score': request.data.get('away_score'),
            'api_id': request.data.get('api_id')  # Adicionar para o enricher
        }
        
        # Buscar dados enriquecidos das APIs se api_id fornecido
        api_id = request.data.get('api_id')
        football_data_id = request.data.get('football_data_id')  # ID da Football-Data.org
        
        # 🆕 MAPEAR FOOTBALL_DATA_ID automaticamente se não fornecido
        if api_id and not football_data_id:
            logger.info(f"🔍 [ID Mapper] Tentando mapear football_data_id para {match_data.get('home_team')} vs {match_data.get('away_team')}")
            try:
                mapper = APIIDMapper()
                match_date_str = match_data.get('date')
                if match_date_str:
                    # Converter string para datetime
                    if isinstance(match_date_str, str):
                        match_date = datetime.fromisoformat(match_date_str.replace('Z', '+00:00'))
                    else:
                        match_date = match_date_str
                    
                    football_data_id = mapper.find_football_data_id(
                        home_team=match_data.get('home_team'),
                        away_team=match_data.get('away_team'),
                        match_date=match_date
                    )
                    
                    if football_data_id:
                        logger.info(f"✅ [ID Mapper] football_data_id={football_data_id} mapeado com sucesso!")
                        match_data['football_data_id'] = football_data_id
                    else:
                        logger.warning(f"⚠️ [ID Mapper] Não foi possível mapear football_data_id")
            except Exception as e:
                logger.error(f"❌ [ID Mapper] Erro ao mapear ID: {e}", exc_info=True)
        
        # 🔥 NOVO: Enriquecer dados se api_id fornecido
        if api_id:
            logger.info(f"\n{'='*80}")
            logger.info(f"🚀 ENRIQUECIMENTO DE DADOS ATIVADO - API ID: {api_id}")
            logger.info(f"{'='*80}\n")
            
            try:
                from apps.analysis.services.match_enricher import MatchDataEnricher
                enricher = MatchDataEnricher()
                match_data = enricher.enrich(match_data)
                
                logger.info(f"✅ Dados enriquecidos com sucesso!")
                logger.info(f"   Campos adicionados: {list(match_data.keys())}")
            except Exception as e:
                logger.error(f"❌ Erro ao enriquecer dados: {str(e)}")
                logger.exception(e)
        
        # Continuar com busca normal de dados adicionais (compatibilidade)
        if api_id:
            logger.info(f"🔍 QUICK_ANALYZE: Buscando dados adicionais para api_id={api_id}")
            try:
                from .services.football_api import FootballAPIService, FootballDataService
                api_service = FootballAPIService()
                
                # ===== API-FOOTBALL (RapidAPI) =====
                # Buscar detalhes da partida
                logger.info(f"📥 [API-Football] Buscando fixture_details...")
                fixture_result = api_service.get_fixture_by_id(api_id)
                if fixture_result.get('success') and fixture_result.get('fixture'):
                    fixture = fixture_result['fixture']
                    match_data['fixture_details'] = fixture
                    logger.info(f"✅ [API-Football] Fixture carregado: {list(fixture.keys())[:5]}")
                else:
                    logger.warning(f"❌ [API-Football] Fixture falhou: {fixture_result.get('error')}")
                
                # Buscar estatísticas da partida (para jogos ao vivo/finalizados)
                logger.info(f"📥 [API-Football] Buscando statistics...")
                stats_result = api_service.get_fixture_statistics(api_id)
                if stats_result.get('success') and stats_result.get('statistics'):
                    match_data['statistics'] = stats_result['statistics']
                    logger.info(f"✅ [API-Football] Statistics carregadas: {len(stats_result['statistics'])} times")
                else:
                    logger.warning(f"❌ [API-Football] Statistics falhou: {stats_result.get('error')}")
                
                # Buscar previsões/estatísticas
                logger.info(f"📥 [API-Football] Buscando predictions...")
                predictions_result = api_service.get_predictions(api_id)
                if predictions_result.get('success') and predictions_result.get('predictions'):
                    match_data['predictions'] = predictions_result['predictions']
                    logger.info(f"✅ [API-Football] Predictions carregadas: {list(predictions_result['predictions'].keys())[:5]}")
                else:
                    logger.warning(f"❌ [API-Football] Predictions falhou: {predictions_result.get('error')}")
                
                # ===== FOOTBALL-DATA.ORG =====
                # Buscar dados adicionais da Football-Data.org (H2H e estatísticas dos times)
                if football_data_id:
                    logger.info(f"📥 [Football-Data.org] Buscando dados adicionais para football_data_id={football_data_id}...")
                    try:
                        fd_service = FootballDataService()
                        
                        # Buscar H2H (histórico direto)
                        logger.info(f"📥 [Football-Data.org] Buscando H2H...")
                        h2h_data = fd_service.get_h2h(football_data_id)
                        if h2h_data and 'matches' in h2h_data:
                            match_data['h2h'] = h2h_data['matches']
                            logger.info(f"✅ [Football-Data.org] H2H carregado: {len(h2h_data['matches'])} jogos anteriores")
                        else:
                            logger.warning(f"❌ [Football-Data.org] H2H não disponível")
                        
                        # Buscar detalhes da partida (pode ter estatísticas adicionais)
                        logger.info(f"📥 [Football-Data.org] Buscando match details...")
                        match_details = fd_service.get_match_details(football_data_id)
                        if match_details:
                            match_data['football_data_match'] = match_details
                            logger.info(f"✅ [Football-Data.org] Match details carregados")
                        else:
                            logger.warning(f"❌ [Football-Data.org] Match details não disponível")
                            
                    except Exception as e:
                        logger.warning(f"⚠️ [Football-Data.org] Erro ao buscar dados: {e}")
                else:
                    logger.info(f"ℹ️ [Football-Data.org] Sem football_data_id - pulando")
                    
                logger.info(f"📊 TOTAL de dados enriquecidos: fixture={bool(match_data.get('fixture_details'))}, stats={bool(match_data.get('statistics'))}, predictions={bool(match_data.get('predictions'))}, h2h={bool(match_data.get('h2h'))}, fd_match={bool(match_data.get('football_data_match'))}")
            except Exception as e:
                logger.error(f"❌ ERRO ao buscar dados adicionais das APIs: {e}", exc_info=True)
        
        # 🎯 ARQUITETURA HÍBRIDA: Modelos Estatísticos DECIDEM, IA EXPLICA
        logger.info(f"\n{'='*80}")
        logger.info("🎯 INICIANDO ARQUITETURA HÍBRIDA")
        logger.info(f"{'='*80}\n")
        
        # Verificar se deve pular IA
        skip_ai = request.data.get('skip_ai', False)
        if skip_ai:
            logger.info("⏭️ SKIP_AI=True: Pulando geração da IA, apenas retornando dados estatísticos")
        
        # 1. Feature Engineering (TIER 1 - 40 variáveis)
        from apps.analysis.services.feature_engineer import FeatureEngineer
        engineer = FeatureEngineer()
        features = engineer.engineer_all_features(match_data)
        
        # 2. Calcular força ofensiva (para Poisson)
        home_stats = match_data.get('home_stats', {})
        away_stats = match_data.get('away_stats', {})
        
        home_strength = home_stats.get('goals_per_game_avg', 1.5)  # Default 1.5 gols/jogo
        away_strength = away_stats.get('goals_per_game_avg', 1.3)
        
        # Ajustar pela forma recente
        form_diff = features.get('form', {}).get('form_diff', 0)
        home_strength += form_diff * 0.1  # +10% por ponto de forma
        away_strength -= form_diff * 0.1
        
        # 3. Impacto climático (usar impacto numérico nos gols)
        # features['weather']['weather_impact'] é categórico ('low'/'medium'/'high');
        # usamos 'goal_impact' que já é um float calibrado.
        weather_impact = features.get('weather', {}).get('goal_impact', 0.0)
        
        # 4. Modelos Estatísticos (Poisson + Logística)
        from apps.analysis.services.statistical_models import ModelEnsemble
        ensemble = ModelEnsemble()
        model_predictions = ensemble.predict(features, home_strength, away_strength, weather_impact)
        
        # 5. Decision Engine (Value Bets + Confiança)
        from apps.analysis.services.decision_engine import DecisionEngine
        decision_engine = DecisionEngine()
        
        # Preparar odds do mercado - buscar do enriched_data (API Football)
        raw_odds = match_data.get('odds') or {}  # Se None, usar dicionário vazio
        logger.info(f"🔍 RAW_ODDS tipo: {type(raw_odds)}, valor: {raw_odds}")
        
        # Primeiro, executar decision engine para ter fair_odds
        decision_data_temp = decision_engine.make_decision(
            model_predictions,
            features,
            {}  # Passar vazio temporariamente
        )
        
        # Converter formato da API (home_win, draw, away_win) para formato frontend (odds_home, odds_draw, odds_away)
        if raw_odds.get('home_win'):
            market_odds = {
                'odds_home': raw_odds.get('home_win'),
                'odds_draw': raw_odds.get('draw'),
                'odds_away': raw_odds.get('away_win'),
                'odds_over_25': raw_odds.get('over_25'),
                'odds_under_25': raw_odds.get('under_25'),
                'odds_btts_yes': raw_odds.get('btts_yes'),
                'odds_btts_no': raw_odds.get('btts_no'),
            }
            logger.info(f"💰 Market odds da API Football: Home={market_odds['odds_home']}, Draw={market_odds['odds_draw']}, Away={market_odds['odds_away']}")
        else:
            # Fallback: simular com base nas fair odds + margem bookmaker (5%)
            # Isso só ocorre quando não há api_id ou odds não estão disponíveis na API
            fair_odds_data = decision_data_temp.get('fair_odds', {})
            if fair_odds_data and fair_odds_data.get('home_win'):
                bookmaker_margin = 1.05  # 5% de margem típica
                market_odds = {
                    'odds_home': round(fair_odds_data['home_win'] / bookmaker_margin, 2),
                    'odds_draw': round(fair_odds_data.get('draw', 3.4) / bookmaker_margin, 2),
                    'odds_away': round(fair_odds_data.get('away_win', 3.0) / bookmaker_margin, 2),
                    'odds_over_25': round(fair_odds_data.get('over_2_5', 2.0) / bookmaker_margin, 2),
                    'odds_btts_yes': round(fair_odds_data.get('btts', 2.0) / bookmaker_margin, 2),
                }
                logger.info(f"💰 Market odds simuladas com margem 5% (fallback): Home={market_odds['odds_home']}, Draw={market_odds['odds_draw']}, Away={market_odds['odds_away']}")
            else:
                market_odds = None
                logger.warning("⚠️ Não foi possível gerar market_odds (sem dados da API e sem fair_odds)")
        
        # Log para debug
        logger.info(f"📊 MARKET ODDS FINAL: {market_odds}")
        
        # Executar decision engine novamente com market_odds corretos
        decision_data = decision_engine.make_decision(
            model_predictions,
            features,
            market_odds
        )
        
        # 6. IA Explainer (Gemini Flash apenas EXPLICA) - OPCIONAL
        result = {'success': True, 'analysis': None}
        
        if not skip_ai:
            analyzer = AIAnalyzer()
            result = analyzer.explain_decision(decision_data, match_data)
            
            if not result['success']:
                return Response(
                    {'error': result.get('error'), 'details': result.get('details'), 'code': result.get('error_code')},
                    status=result.get('http_status', status.HTTP_500_INTERNAL_SERVER_ERROR)
                )
        else:
            logger.info("⏭️ Pulando geração da IA - retornando apenas dados estatísticos")
        
        # Criar metadados sobre quais dados foram analisados
        metadata = {
            'has_predictions': bool(match_data.get('predictions')),
            'has_statistics': bool(match_data.get('statistics')),
            'has_h2h': bool(match_data.get('h2h')),
            'h2h_count': len(match_data.get('h2h', [])) if match_data.get('h2h') else 0,
            'has_fixture_details': bool(match_data.get('fixture_details')),
            'has_football_data': bool(match_data.get('football_data_match'))
        }
        
        # 🔥 Extrair dados enriquecidos para enviar ao frontend
        enriched_data = {
            'table_context': match_data.get('table_context'),
            'injuries': match_data.get('injuries'),
            'odds': match_data.get('odds'),
            'home_stats': match_data.get('home_stats'),
            'away_stats': match_data.get('away_stats'),
            'rest_context': match_data.get('rest_context'),
            'motivation': match_data.get('motivation'),
            'trends': match_data.get('trends'),
            'season_context': match_data.get('season_context'),
            'fixture_details': match_data.get('fixture_details'),
            'h2h': match_data.get('h2h'),  # 🆕 Histórico direto (Football-Data.org)
            'football_data_id': football_data_id,  # 🆕 ID mapeado
            'football_data_match': match_data.get('football_data_match')  # 🆕 Detalhes do Football-Data.org
        }
        
        # Opcional: salvar no histórico se usuário autenticado e houver match mapeado
        saved = False
        saved_info = None
        try:
            if request.user.is_authenticated and request.data.get('save_to_history'):
                api_id_val = request.data.get('api_id')
                if api_id_val:
                    # Tentar mapear para uma partida existente no banco
                    db_match = Match.objects.filter(api_football_id=api_id_val).first()
                    if db_match:
                        # Evitar duplicar análises
                        existing = Analysis.objects.filter(user=request.user, match=db_match).first()
                        if not existing:
                            # Checar limite diário
                            if request.user.can_analyze():
                                home_p, draw_p, away_p = 40.0, 30.0, 30.0
                                home_xg, away_xg = 1.5, 1.3
                                prediction = 'home'
                                confidence = int(result.get('confidence', 3) or 3)
                                reasoning = result.get('analysis') or 'Análise gerada pela IA.'
                                key_factors = ['Mando de campo', 'Forma recente']
                                saved_analysis = Analysis.objects.create(
                                    user=request.user,
                                    match=db_match,
                                    prediction=prediction,
                                    confidence=confidence,
                                    home_probability=home_p,
                                    draw_probability=draw_p,
                                    away_probability=away_p,
                                    home_xg=home_xg,
                                    away_xg=away_xg,
                                    reasoning=reasoning,
                                    key_factors=key_factors,
                                    analysis_data={'source': 'ai', 'fallback': True}
                                )
                                request.user.increment_analysis_count()
                                saved = True
                                saved_info = {'id': saved_analysis.id, 'created_at': saved_analysis.created_at}
                    else:
                        # Criar um registro mínimo da partida e salvar análise
                        if request.user.can_analyze():
                            from django.utils import timezone
                            league_name = request.data.get('league') or 'Liga Desconhecida'
                            home_name = request.data.get('home_team') or 'Time Casa'
                            away_name = request.data.get('away_team') or 'Time Visitante'
                            match_date_str = request.data.get('date')
                            try:
                                match_date = datetime.fromisoformat(str(match_date_str).replace('Z', '+00:00')) if match_date_str else timezone.now()
                            except Exception:
                                match_date = timezone.now()

                            league_obj, _ = League.objects.get_or_create(
                                name=league_name,
                                defaults={
                                    'country': '',
                                    'logo': '',
                                    'is_active': True,
                                }
                            )
                            home_team_obj, _ = Team.objects.get_or_create(
                                name=home_name,
                                defaults={'country': '', 'logo': ''}
                            )
                            away_team_obj, _ = Team.objects.get_or_create(
                                name=away_name,
                                defaults={'country': '', 'logo': ''}
                            )

                            db_match = Match.objects.create(
                                league=league_obj,
                                home_team=home_team_obj,
                                away_team=away_team_obj,
                                match_date=match_date,
                                status=request.data.get('status') or 'scheduled',
                                api_football_id=api_id_val,
                                football_data_id=request.data.get('football_data_id') or None,
                                is_analysis_available=True,
                            )

                            home_p, draw_p, away_p = 40.0, 30.0, 30.0
                            home_xg, away_xg = 1.5, 1.3
                            prediction = 'home'
                            confidence = int(result.get('confidence', 3) or 3)
                            reasoning = result.get('analysis') or 'Análise gerada pela IA.'
                            key_factors = ['Mando de campo', 'Forma recente']
                            saved_analysis = Analysis.objects.create(
                                user=request.user,
                                match=db_match,
                                prediction=prediction,
                                confidence=confidence,
                                home_probability=home_p,
                                draw_probability=draw_p,
                                away_probability=away_p,
                                home_xg=home_xg,
                                away_xg=away_xg,
                                reasoning=reasoning,
                                key_factors=key_factors,
                                analysis_data={'source': 'ai', 'fallback': True}
                            )
                            request.user.increment_analysis_count()
                            saved = True
                            saved_info = {'id': saved_analysis.id, 'created_at': saved_analysis.created_at}
        except Exception:
            # Ignorar erros de persistência silenciosamente para não quebrar preview
            saved = False
            saved_info = None

        return Response({
            'analysis': result.get('analysis'),
            'confidence': decision_data['confidence']['stars'],  # Confiança do Decision Engine
            'confidence_display': f"{decision_data['confidence']['level']} ({decision_data['confidence']['stars']}/5)",
            'prediction_display': decision_data['recommendation']['pick'],
            'home_probability': model_predictions['consensus']['home_win'] * 100,
            'draw_probability': model_predictions['consensus']['draw'] * 100,
            'away_probability': model_predictions['consensus']['away_win'] * 100,
            'key_factors': decision_data.get('key_factors', []),
            'value_bets': decision_data.get('value_bets', []),
            'metadata': metadata,
            'enriched_data': enriched_data,
            'model_predictions': model_predictions,  # Dados completos dos modelos
            'fair_odds': decision_data.get('fair_odds', {}),
            'risk': decision_data.get('risk', 'medium'),
            'saved': saved,
            'saved_analysis': saved_info,
            # Estrutura completa para frontend (compatível com nova arquitetura)
            'analysis_data': {
                'consensus': model_predictions['consensus'],
                'poisson': model_predictions.get('poisson', {}),
                'logistic': model_predictions.get('logistic', {}),
                'fair_odds': decision_data.get('fair_odds', {}),
                'market_odds': market_odds,
                'value_bets': decision_data.get('value_bets', []),
                'recommendation': decision_data.get('recommendation', {}),
                'confidence': decision_data.get('confidence', {}),
                'risk': decision_data.get('risk', 'medium'),
                'features_summary': {
                    'strength': features.get('strength', {}),
                    'form': features.get('form', {}),
                    'weather': features.get('weather', {})
                }
            }
        })
    
    def _calculate_statistical_risk(self, consensus, confidence_stars, features=None, enriched_data=None):
        """
        Calcula o nível de risco baseado em:
        1. Entropia das probabilidades (incerteza)
        2. Confiança da predição
        3. Volatilidade de contexto (lesões, fadiga, clima)
        4. Odds do mercado (se disponíveis)
        
        Returns:
            str: 'low', 'medium', ou 'high'
        """
        risk_score = 0.0
        
        # 1. ENTROPIA (Incerteza da predição)
        # Quanto mais equilibradas as probabilidades, maior o risco
        import numpy as np
        probs = [consensus['home_win'], consensus['draw'], consensus['away_win']]
        entropy = -sum(p * np.log(p + 1e-10) for p in probs if p > 0)
        normalized_entropy = entropy / np.log(3)  # Normalizar (máximo = log(3))
        
        # Peso 40% para entropia
        risk_score += normalized_entropy * 0.4
        
        logger.info(f"📊 Cálculo de Risco:")
        logger.info(f"   Entropia: {normalized_entropy:.2f} (peso: 0.4) = {normalized_entropy * 0.4:.2f}")
        
        # 2. CONFIANÇA (Inverso)
        # Confiança baixa = alto risco
        confidence_risk = (5 - confidence_stars) / 5  # 1/5=0.2 (baixo), 4/5=0.2 (baixo)
        risk_score += confidence_risk * 0.3
        
        logger.info(f"   Confiança: {confidence_stars}/5 → risco={confidence_risk:.2f} (peso: 0.3) = {confidence_risk * 0.3:.2f}")
        
        # 3. CONTEXTO VOLÁTIL (lesões, clima, fadiga)
        context_risk = 0.0
        
        if features:
            # Clima severo aumenta risco
            weather = features.get('weather', {})
            weather_severity = weather.get('weather_severity', 'NENHUM')
            if weather_severity in ['ALTO', 'MUITO_ALTO']:
                context_risk += 0.3
                logger.info(f"   Clima severo: +0.3")
            elif weather_severity == 'MODERADO':
                context_risk += 0.15
                logger.info(f"   Clima moderado: +0.15")
            
            # Fadiga aumenta risco
            context = features.get('context', {})
            if context.get('home_is_fatigued') or context.get('away_is_fatigued'):
                context_risk += 0.2
                logger.info(f"   Fadiga detectada: +0.2")
        
        if enriched_data:
            # Muitas lesões aumentam risco
            injuries = enriched_data.get('injuries', {})
            home_injuries = len(injuries.get('home', []))
            away_injuries = len(injuries.get('away', []))
            total_injuries = home_injuries + away_injuries
            
            if total_injuries >= 5:
                context_risk += 0.3
                logger.info(f"   Muitas lesões ({total_injuries}): +0.3")
            elif total_injuries >= 3:
                context_risk += 0.15
                logger.info(f"   Lesões moderadas ({total_injuries}): +0.15")
        
        # Limitar context_risk a 0.5 máximo
        context_risk = min(context_risk, 0.5)
        risk_score += context_risk * 0.3
        
        logger.info(f"   Contexto volátil: {context_risk:.2f} (peso: 0.3) = {context_risk * 0.3:.2f}")
        
        # Score final (0 a 1)
        logger.info(f"   SCORE TOTAL: {risk_score:.2f}")
        
        # Classificação
        if risk_score < 0.35:
            risk_level = 'low'
        elif risk_score < 0.65:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        logger.info(f"   ✅ NÍVEL DE RISCO: {risk_level.upper()}")
        
        return risk_level
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def statistical_preview(self, request):
        """Preview rápido de estatísticas básicas - SEMPRE recalcula a cada request"""
        from apps.analysis.services.statistical_models import PoissonBivariateModel, LogisticRegressionModel
        from apps.analysis.services.feature_engineer import FeatureEngineer
        from apps.analysis.services.match_enricher import MatchDataEnricher
        
        home_team = request.data.get('home_team')
        away_team = request.data.get('away_team')
        league = request.data.get('league')
        match_date = request.data.get('date')
        match_id = request.data.get('match_id')
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 STATISTICAL PREVIEW - {home_team} vs {away_team}")
        logger.info(f"{'='*80}")
        
        if not home_team or not away_team:
            return Response(
                {'error': 'home_team e away_team são obrigatórios'},
                status=status.HTTP_BAD_REQUEST
            )
        
        try:
            # SEMPRE tentar buscar dados reais - prioridade 1: Enriquecimento completo
            enriched_data = None
            features = None
            api_id = None
            
            # 1. Tentar obter API ID da partida
            if match_id:
                try:
                    match = Match.objects.get(id=match_id)
                    api_id = match.api_football_id
                    logger.info(f"✅ Partida {match_id} encontrada no DB (API ID: {api_id})")
                except Match.DoesNotExist:
                    logger.info(f"⚠️ Partida {match_id} não encontrada no DB")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao buscar partida: {e}")
            
            # 2. Se não tem API ID do match, tentar buscar da API diretamente pelo nome dos times
            if not api_id:
                logger.info(f"🔍 Tentando buscar API ID pelos nomes dos times e data...")
                try:
                    from apps.matches.services.football_api import FootballAPIService
                    api_service = FootballAPIService()
                    
                    # Buscar partidas da data fornecida
                    if match_date:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(match_date.replace('Z', '+00:00'))
                        date_str = date_obj.strftime('%Y-%m-%d')
                        
                        result = api_service.get_fixtures_by_date(date_str)
                        
                        if result.get('success'):
                            fixtures = result.get('fixtures', [])
                            # Procurar a partida pelos nomes dos times
                            for fixture in fixtures:
                                home = fixture.get('teams', {}).get('home', {}).get('name', '')
                                away = fixture.get('teams', {}).get('away', {}).get('name', '')
                                
                                if home_team.lower() in home.lower() and away_team.lower() in away.lower():
                                    api_id = fixture.get('fixture', {}).get('id')
                                    logger.info(f"✅ API ID encontrado via busca: {api_id}")
                                    break
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao buscar API ID: {e}")
            
            # 3. Se tem API ID, tentar enriquecimento completo
            if api_id:
                try:
                    logger.info(f"🔄 Enriquecendo dados com API ID {api_id}...")
                    enricher = MatchDataEnricher()
                    enriched_data = enricher.enrich({
                        'home_team': home_team,
                        'away_team': away_team,
                        'league': league,
                        'date': match_date,
                        'api_id': api_id
                    })
                    
                    # Gerar features a partir dos dados enriquecidos
                    engineer = FeatureEngineer()
                    features = engineer.engineer_all_features(enriched_data)
                    
                    logger.info(f"✅ Enriquecimento completo realizado!")
                except Exception as e:
                    logger.error(f"❌ Erro no enriquecimento completo: {e}", exc_info=True)
                    enriched_data = None
                    features = None
            
            # Determinar home_strength e away_strength
            if features and features.get('strength'):
                home_strength = features['strength'].get('home_goals_per_game', 1.5)
                away_strength = features['strength'].get('away_goals_per_game', 1.3)
                logger.info(f"📊 Usando dados reais das features: Casa={home_strength:.2f}, Fora={away_strength:.2f}")
            elif enriched_data and enriched_data.get('home_stats'):
                home_strength = enriched_data['home_stats'].get('goals_per_game_avg', 1.5)
                away_strength = enriched_data['away_stats'].get('goals_per_game_avg', 1.3)
                logger.info(f"📊 Usando dados reais: Casa={home_strength:.2f}, Fora={away_strength:.2f}")
            else:
                # Valores padrão se não tiver dados
                home_strength = 1.5
                away_strength = 1.3
                logger.info("⚠️ Usando valores padrão (sem dados reais)")
            
            # Modelo Poisson (rápido - cálculo matemático direto)
            poisson = PoissonBivariateModel()
            
            # Usar impacto climático se disponível
            weather_impact = 0
            if features and features.get('weather'):
                weather_impact = features['weather'].get('weather_impact', 0)
            
            poisson_pred = poisson.predict(home_strength, away_strength, weather_impact=weather_impact)
            
            # Modelo Logístico (rápido - cálculo direto)
            logistic = LogisticRegressionModel()
            
            # Tentar usar features reais se disponíveis
            if features:
                logistic_pred = logistic.predict_1x2(features)
                logger.info("📊 Usando features reais para modelo logístico")
            else:
                # Features mínimas padrão
                logistic_pred = logistic.predict_1x2({
                    'strength': {
                        'offensive_diff': 0,
                        'defensive_diff': 0
                    },
                    'form': {
                        'form_diff': 0,
                        'momentum_diff': 0
                    },
                    'context': {
                        'rest_advantage': 0
                    }
                })
                logger.info("⚠️ Usando features padrão para modelo logístico")
            
            # Consensus (60% Poisson + 40% Logística)
            consensus = {
                'home_win': poisson_pred['probabilities']['home_win'] * 0.6 + logistic_pred['home_win'] * 0.4,
                'draw': poisson_pred['probabilities']['draw'] * 0.6 + logistic_pred['draw'] * 0.4,
                'away_win': poisson_pred['probabilities']['away_win'] * 0.6 + logistic_pred['away_win'] * 0.4,
            }
            
            # Calcular odds justas
            fair_odds = {
                'home_win': round(1 / consensus['home_win'], 2) if consensus['home_win'] > 0 else 999,
                'draw': round(1 / consensus['draw'], 2) if consensus['draw'] > 0 else 999,
                'away_win': round(1 / consensus['away_win'], 2) if consensus['away_win'] > 0 else 999,
            }
            
            # Confiança baseada em diferença de probabilidades
            prob_diff = abs(consensus['home_win'] - consensus['away_win'])
            if prob_diff > 0.3:
                confidence_level = 'Alta'
                confidence_stars = 4
            elif prob_diff > 0.15:
                confidence_level = 'Moderada'
                confidence_stars = 3
            else:
                confidence_level = 'Baixa'
                confidence_stars = 2
            
            # Recomendação simples
            max_prob = max(consensus['home_win'], consensus['draw'], consensus['away_win'])
            if consensus['home_win'] == max_prob:
                pick = 'Vitória Casa'
            elif consensus['away_win'] == max_prob:
                pick = 'Vitória Fora'
            else:
                pick = 'Empate'
            
            # Avaliar risco baseado em múltiplos fatores
            risk_level = self._calculate_statistical_risk(
                consensus=consensus,
                confidence_stars=confidence_stars,
                features=features,
                enriched_data=enriched_data
            )
            
            # Construir features_summary a partir dos dados disponíveis
            features_summary = {}
            if features:
                # Log detalhado das features disponíveis
                logger.info(f"🔍 Features disponíveis: {list(features.keys())}")
                logger.info(f"🔍 Strength features: {features.get('strength', {})}")
                logger.info(f"🔍 Form features: {features.get('form', {})}")
                
                # Usar features reais geradas
                features_summary = {
                    'strength': features.get('strength', {}),
                    'form': features.get('form', {}),
                }
                logger.info("✅ Usando features_summary real")
            elif enriched_data and (enriched_data.get('home_stats') or enriched_data.get('away_stats')):
                # Construir a partir das estatísticas básicas
                home_stats = enriched_data.get('home_stats', {})
                away_stats = enriched_data.get('away_stats', {})
                features_summary = {
                    'strength': {
                        'home_goals_per_game': home_stats.get('goals_per_game_avg', home_strength),
                        'away_goals_per_game': away_stats.get('goals_per_game_avg', away_strength),
                        'home_defensive_rating': home_stats.get('goals_conceded_per_game_avg', 1.2),
                        'away_defensive_rating': away_stats.get('goals_conceded_per_game_avg', 1.2),
                        'home_defense_strength': home_stats.get('defensive_rating', 1.0),
                        'away_defense_strength': away_stats.get('defensive_rating', 1.0),
                    },
                    'form': {
                        'home_form_weighted': home_stats.get('form_score', 1.5),
                        'away_form_weighted': away_stats.get('form_score', 1.5),
                        'home_momentum': home_stats.get('momentum', 0),
                        'away_momentum': away_stats.get('momentum', 0),
                    }
                }
                logger.info("✅ Usando features_summary construído de stats básicas")
            else:
                # Valores padrão
                features_summary = {
                    'strength': {
                        'home_goals_per_game': home_strength,
                        'away_goals_per_game': away_strength,
                        'home_defensive_rating': 1.2,
                        'away_defensive_rating': 1.2,
                        'home_defense_strength': 1.0,
                        'away_defense_strength': 1.0,
                    },
                    'form': {
                        'home_form_weighted': 1.5,
                        'away_form_weighted': 1.5,
                        'home_momentum': 0,
                        'away_momentum': 0,
                    }
                }
                logger.info("⚠️ Usando features_summary padrão")
            
            # Log detalhado do features_summary
            logger.info(f"\n📊 FEATURES_SUMMARY FINAL:")
            logger.info(f"   Strength - Casa Ataque: {features_summary['strength'].get('home_goals_per_game', 'N/A')}")
            logger.info(f"   Strength - Casa Defesa: {features_summary['strength'].get('home_defensive_rating', 'N/A')}")
            logger.info(f"   Strength - Fora Ataque: {features_summary['strength'].get('away_goals_per_game', 'N/A')}")
            logger.info(f"   Strength - Fora Defesa: {features_summary['strength'].get('away_defensive_rating', 'N/A')}")
            logger.info(f"   Form - Casa: {features_summary['form'].get('home_form_weighted', 'N/A')}")
            logger.info(f"   Form - Fora: {features_summary['form'].get('away_form_weighted', 'N/A')}")
            logger.info(f"   Momentum - Casa: {features_summary['form'].get('home_momentum', 'N/A')}")
            logger.info(f"   Momentum - Fora: {features_summary['form'].get('away_momentum', 'N/A')}")
            
            logger.info(f"\n{'='*80}")
            logger.info(f"✅ STATISTICAL PREVIEW CONCLUÍDO")
            logger.info(f"{'='*80}\n")
            
            return Response({
                'success': True,
                'analysis_data': {
                    'consensus': consensus,
                    'poisson': poisson_pred,
                    'logistic': logistic_pred,
                    'fair_odds': fair_odds,
                    'features_summary': features_summary,  # Adicionado
                    'recommendation': {
                        'pick': pick,
                        'probability': max_prob
                    },
                    'confidence': {
                        'level': confidence_level,
                        'stars': confidence_stars,
                        'score': prob_diff
                    },
                    'risk': risk_level,  # ← Usando cálculo dinâmico
                    'is_preview': True,  # Flag para indicar que são dados básicos
                    'has_real_data': bool(features or enriched_data)  # Indica se usou dados reais
                },
                'enriched_data': enriched_data or {}  # Passar dados enriquecidos para debug
            })
            
        except Exception as e:
            logger.error(f"Erro no statistical_preview: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Erro ao calcular estatísticas', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
