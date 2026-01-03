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
    
    @action(detail=False, methods=['get'])
    def live(self, request):
        """Partidas ao vivo"""
        matches = self.get_queryset().filter(status='live')
        serializer = self.get_serializer(matches, many=True)
        return Response(serializer.data)
    
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
            
            matches.append({
                'id': fixture_id,  # Usar ID real em vez de temporário
                'api_football_id': fixture_id,  # ID para buscar dados adicionais
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
        
        analyzer = AIAnalyzer()
        result = analyzer.analyze_match(match_data)
        
        if not result['success']:
            return Response(
                {'error': result.get('error'), 'details': result.get('details'), 'code': result.get('error_code')},
                status=result.get('http_status', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
        
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
            'analysis': result['analysis'],
            'confidence': result['confidence'],
            'metadata': metadata,
            'enriched_data': enriched_data,  # 🔥 ADICIONADO!
            'saved': saved,
            'saved_analysis': saved_info
        })

