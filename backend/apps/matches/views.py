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
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
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
        """Buscar partidas diretamente da API-Football com cache"""
        date = request.query_params.get('date', datetime.now().strftime('%Y-%m-%d'))
        force_real = request.query_params.get('force_real', 'false').lower() == 'true'
        
        # Cache key baseado na hora atual (atualiza a cada 6 horas)
        cache_key = f'matches_api_{datetime.now().strftime("%Y%m%d_%H")}'
        
        # Tentar buscar do cache (6 horas para economizar MUITO mais requisições)
        if not force_real:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"✅ CACHE HIT: Retornando {len(cached_data['matches'])} partidas do cache")
                return Response(cached_data)
        
        logger.info(f"❌ CACHE MISS: Buscando partidas da API...")
        football_api = FootballAPIService()
        all_matches = []
        
        # Buscar TODAS as partidas dos próximos dias (não filtrar por liga)
        logger.info("⚽ Buscando TODAS as partidas disponíveis...")
        
        # Buscar partidas dos próximos 3 dias para ter variedade
        today = datetime.now()
        for i in range(3):  # Hoje, amanhã e depois
            target_date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
            result = football_api.get_fixtures_by_date(target_date)
            
            if result['success'] and result['fixtures']:
                all_matches.extend(result['fixtures'])
                logger.info(f"   {target_date}: {len(result['fixtures'])} partidas")
        
        # Definir ligas principais para priorização (serão exibidas primeiro)
        PRIORITY_LEAGUES = {
            'Premier League': 1,
            'La Liga': 1,
            'Serie A': 1,
            'Bundesliga': 1,
            'Ligue 1': 1,
            'Eredivisie': 2,
            'Liga Portugal': 2,
            'Championship': 2,
            'Brasileirão Série A': 1,
            'Serie B': 2,
            'Brasileirão Série B': 2,
            'Copa Libertadores': 1,
            'UEFA Champions League': 1,
            'UEFA Europa League': 2,
            'UEFA Conference League': 2,
            'Scottish Premiership': 2,
            'Belgian Pro League': 2,
            'Süper Lig': 2,
            'La Liga 2': 3,
            'Bundesliga 2': 3,
            'Ligue 2': 3,
        }
        
        logger.info(f"   Total de partidas brutas: {len(all_matches)}")
        
        # Se encontrou partidas reais, retorná-las
        if all_matches:
            # Remover duplicatas por ID
            unique_matches = {m['fixture']['id']: m for m in all_matches}.values()
            matches_list = list(unique_matches)
            
            # Ordenar por data
            matches_list.sort(key=lambda x: x['fixture']['date'])
            
            logger.info(f"Total de {len(matches_list)} partidas únicas encontradas")
            
            # Formatar partidas e adicionar prioridade da liga
            matches = self._format_api_matches(matches_list)
            
            # Adicionar prioridade às partidas baseado na liga
            for match in matches:
                league_name = match.get('league', {}).get('name', '') if isinstance(match.get('league'), dict) else match.get('league', '')
                match['league_priority'] = PRIORITY_LEAGUES.get(league_name, 3)  # 3 = outras ligas
            
            # Ordenar por prioridade da liga (menor = mais importante) e depois por data
            matches.sort(key=lambda x: (x.get('league_priority', 3), x.get('match_date', '')))
            
            response_data = {
                'date': date,
                'count': len(matches),
                'matches': matches,
                'is_mock': False,
                'source': 'api-football'
            }
            
            # Cachear resultado por 6 horas (economizar MUITO mais requisições)
            cache.set(cache_key, response_data, 60 * 360)
            logger.info(f"✅ Cache atualizado com {len(matches)} partidas (válido por 6h)")
            
            return Response(response_data)
        
        # Se force_real está ativo, retornar erro em vez de mock
        if force_real:
            return Response(
                {'error': 'Nenhuma partida real disponível no momento'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Se não houver partidas da API, retornar dados de exemplo
        logger.warning(f"⚠️  Limite de requisições da API-Football atingido ou sem partidas disponíveis.")
        logger.info("ℹ️  Exibindo partidas de exemplo. Partidas reais voltarão quando limite resetar (meia-noite UTC).")
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

        # Detectar partidas de exemplo (IDs >= 10000000 - 10 milhões)
        # API-Football usa IDs até ~2 milhões, então 10M é seguro para detectar mocks
        if fixture_id >= 10000000:
            return Response({
                'error': 'Partida de exemplo não disponível para visualização detalhada',
                'message': 'Esta é uma partida de exemplo. Detalhes completos estão disponíveis apenas para partidas reais.',
                'is_mock': True
            }, status=status.HTTP_404_NOT_FOUND)

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
            
            # Normalizar nome da liga para evitar duplicatas
            league_name = fixture['league']['name']
            league_id = fixture['league']['id']
            league_country = fixture['league'].get('country', '')
            
            # Mapear IDs de ligas conhecidas para nomes consistentes (com país quando necessário)
            LEAGUE_NAME_MAP = {
                # Inglaterra
                39: 'Premier League',
                40: 'Championship',
                41: 'League One',
                42: 'League Two',
                
                # Espanha
                140: 'La Liga',
                141: 'La Liga 2',
                
                # Itália
                135: 'Serie A',
                136: 'Serie B',
                
                # Alemanha
                78: 'Bundesliga',
                79: 'Bundesliga 2',
                
                # França
                61: 'Ligue 1',
                62: 'Ligue 2',
                
                # Portugal
                94: 'Liga Portugal',
                
                # Holanda
                88: 'Eredivisie',
                
                # Brasil
                71: 'Brasileirão Série A',
                72: 'Brasileirão Série B',
                
                # Competições Internacionais
                2: 'UEFA Champions League',
                3: 'UEFA Europa League',
                848: 'UEFA Conference League',
                13: 'Copa Libertadores',
                11: 'Copa Sudamericana',
                
                # Escócia
                179: 'Scottish Premiership',
                
                # Bélgica
                144: 'Belgian Pro League',
                
                # Turquia
                203: 'Süper Lig',
            }
            
            # Usar nome normalizado se disponível, caso contrário adicionar país ao nome
            if league_id in LEAGUE_NAME_MAP:
                normalized_league_name = LEAGUE_NAME_MAP[league_id]
            else:
                # Para ligas não mapeadas, adicionar país se o nome for genérico
                generic_names = [
                    'Premier League',
                    'Premiership',
                    'First Division',
                    'Segunda División',
                    'Segunda Division',
                    'Serie A',
                    'Serie B',
                    'Serie C',
                    'Division 1',
                    'Division 2',
                    'Division 3',
                    'Ligue 1',
                    'Ligue 2',
                    'Championship',
                    'Super League',
                    'Super Cup',
                    'Primera Division',
                    'Primera División',
                    'National League',
                    'Pro League',
                    'Professional League',
                    'League One',
                    'League Two',
                    'Cup',
                    'FA Cup',
                    'League Cup',
                    'Primeira Liga',
                    'Segunda Liga',
                    'Tercera Division'
                ]
                if any(generic in league_name for generic in generic_names) and league_country:
                    # Se não for a liga principal mapeada, adicionar país
                    normalized_league_name = f"{league_name} ({league_country})"
                else:
                    normalized_league_name = league_name
            
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
                    'name': normalized_league_name,  # Usar nome normalizado
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
        """Gerar análise COMPLETA com Orchestrator (109 features + ensemble + decision + IA)"""
        match = self.get_object()
        
        # Verificar se usuário pode analisar
        if not request.user.can_analyze():
            return Response(
                {'error': 'Limite diário de análises atingido. Faça upgrade para Premium!'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Usar HybridAnalysisOrchestrator (sistema validado com 55% de acurácia)
            print("\n" + "="*100)
            print(f"🎯 VIEWS.PY - Iniciando análise da partida {match.id}")
            print(f"🎯 Match: {match.home_team.name} vs {match.away_team.name}")
            print("="*100 + "\n")
            
            logger.info(f"🎯 Analisando partida {match.id} com HybridAnalysisOrchestrator")
            orchestrator = HybridAnalysisOrchestrator()
            result = orchestrator.run(match)
            
            print("\n" + "="*100)
            print(f"🎯 VIEWS.PY - Análise completa RETORNADA")
            print(f"🎯 Probabilidades: Casa={result.get('home_probability', 0):.1%}, Empate={result.get('draw_probability', 0):.1%}, Fora={result.get('away_probability', 0):.1%}")
            print("="*100 + "\n")
            
            if not result:
                return Response(
                    {'error': 'Falha ao gerar análise completa'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # O orchestrator já retorna os dados no formato correto
            prediction = result.get('prediction', 'home')
            confidence = result.get('confidence', 3)
            home_probability = result.get('home_probability', 40.0)
            draw_probability = result.get('draw_probability', 30.0)
            away_probability = result.get('away_probability', 30.0)
            home_xg = result.get('home_xg', 1.5)
            away_xg = result.get('away_xg', 1.3)
            reasoning = result.get('reasoning', 'Análise baseada em ensemble estatístico.')
            key_factors = result.get('key_factors', ['Análise estatística', 'Dados históricos'])
            analysis_data = result.get('analysis_data', {})
            should_publish = result.get('should_publish', True)
            
            # Criar e salvar análise no banco
            analysis = Analysis.objects.create(
                user=request.user,
                match=match,
                prediction=prediction,
                confidence=confidence,
                home_probability=home_probability,
                draw_probability=draw_probability,
                away_probability=away_probability,
                home_xg=home_xg,
                away_xg=away_xg,
                reasoning=reasoning,
                key_factors=key_factors,
                analysis_data={
                    'source': 'hybrid_orchestrator',
                    'should_publish': should_publish,
                    **analysis_data
                }
            )
            
            # Incrementar contador de análises do usuário
            request.user.increment_analysis_count()
            
            # Mapear predição para display
            prediction_display_map = {
                'home': f'{match.home_team.name} vence',
                'away': f'{match.away_team.name} vence',
                'draw': 'Empate',
                'btts_yes': 'Ambas Marcam',
                'btts_no': 'Ambas NÃO marcam'
            }
            
            # Resposta completa compatível com o frontend
            # Calcular análises restantes inline (fix temporário)
            from apps.subscriptions.plan_config import get_plan_limit
            limit = None
            try:
                active_sub = request.user.subscriptions.filter(status='active', end_date__gt=timezone.now()).first()
                if active_sub and active_sub.plan_slug:
                    limit = get_plan_limit(active_sub.plan_slug)
            except Exception:
                limit = None
            
            if limit is None:
                limit = 3 if not request.user.is_staff and not request.user.is_superuser else 999
            
            remaining = max(0, limit - request.user.daily_analysis_count) if hasattr(request.user, 'daily_analysis_count') else limit
            
            payload = {
                'analysis': reasoning,
                'confidence': confidence,
                'remaining_analyses': remaining,
                'saved': True,
                'saved_analysis': {
                    'id': analysis.id,
                    'created_at': analysis.created_at,
                },
                # Dados estruturados para o modal
                'prediction': prediction,
                'prediction_display': prediction_display_map.get(prediction, prediction),
                'home_probability': home_probability,
                'draw_probability': draw_probability,
                'away_probability': away_probability,
                'home_xg': home_xg,
                'away_xg': away_xg,
                'reasoning': reasoning,
                'key_factors': key_factors,
                'should_publish': should_publish,
                # Dados extras do orchestrator
                'value_bets': analysis_data.get('value_bets', []),
                'fair_odds': analysis_data.get('fair_odds', {}),
                'risk': analysis_data.get('risk', 'medium'),
            }
            
            logger.info(f"✅ Análise completa salva: ID={analysis.id}, Predição={prediction}, Conf={confidence}")
            return Response(payload)
            
        except Exception as e:
            logger.error(f"❌ Erro ao analisar partida {match.id}: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao gerar análise: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def quick_analyze(self, request):
        """Análise rápida sem salvar (para preview) - COM ENRIQUECIMENTO DE DADOS"""
        logger.info(f"\n{'='*80}")
        logger.info(f"📥 QUICK_ANALYZE: Requisição recebida")
        logger.info(f"{'='*80}")
        
        home_team = request.data.get('home_team')
        away_team = request.data.get('away_team')
        strategy = request.data.get('strategy', 'value')  # ✅ NOVO: Estratégia de apostas
        
        # Validar strategy
        if strategy not in ['value', 'multiple']:
            strategy = 'value'  # Fallback para value se inválido
        
        logger.info(f"🏠 Home Team: {home_team}")
        logger.info(f"✈️ Away Team: {away_team}")
        logger.info(f"🏆 League: {request.data.get('league')}")
        logger.info(f"📅 Date: {request.data.get('date')}")
        logger.info(f"⚡ Estratégia: {strategy.upper()}")
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

        # 1.1 Context Analyzer (usar padrões contextuais para seleção de mercados)
        try:
            from apps.analysis.services.context_analyzer import ContextAnalyzer
            context_analyzer = ContextAnalyzer()
            context_analysis = context_analyzer.analyze(features)
            logger.info(f"✅ ContextAnalyzer executado: {len(context_analysis.get('patterns', []))} padrões detectados")
        except Exception as e:
            logger.error(f"❌ Erro ao executar ContextAnalyzer: {e}")
            context_analysis = None
        
        # 2. Calcular força ofensiva e defensiva (para Poisson)
        home_stats = match_data.get('home_stats', {})
        away_stats = match_data.get('away_stats', {})
        
        home_strength = home_stats.get('goals_per_game_avg', 1.5)  # Default 1.5 gols/jogo
        away_strength = away_stats.get('goals_per_game_avg', 1.3)
        
        # NOVO: Extrair defesa
        home_defense = home_stats.get('conceded_per_game_avg', 1.3)  # Gols sofridos/jogo
        away_defense = away_stats.get('conceded_per_game_avg', 1.3)
        
        # Ajustar pela forma recente
        form_diff = features.get('form', {}).get('adjusted_form_diff', 0)  # MUDOU: usa forma ajustada
        home_strength += form_diff * 0.1  # +10% por ponto de forma
        away_strength -= form_diff * 0.1
        
        logger.info(f"🕹️ Forças ajustadas:")
        logger.info(f"   Casa: {home_strength:.2f} gols/jogo (ataque) | {home_defense:.2f} (defesa)")
        logger.info(f"   Fora: {away_strength:.2f} gols/jogo (ataque) | {away_defense:.2f} (defesa)")
        
        # 3. Impacto climático (usar impacto numérico nos gols)
        # features['weather']['weather_impact'] é categórico ('low'/'medium'/'high');
        # usamos 'goal_impact' que já é um float calibrado.
        weather_impact = features.get('weather', {}).get('goal_impact', 0.0)
        
        # 4. Modelos Estatísticos (Poisson + Logística)
        from apps.analysis.services.statistical_models import ModelEnsemble
        ensemble = ModelEnsemble()
        model_predictions = ensemble.predict(features, home_strength, away_strength, weather_impact,
                                            league_id=match_data.get('fixture', {}).get('league_id'),
                                            home_defense=home_defense, away_defense=away_defense)
        
        # 5. Decision Engine (Value Bets + Confiança)
        from apps.analysis.services.decision_engine import DecisionEngine
        decision_engine = DecisionEngine()
        
        # Preparar odds do mercado - buscar do enriched_data (API Football)
        raw_odds = match_data.get('odds') or {}  # Se None, usar dicionário vazio
        logger.info(f"🔍 RAW_ODDS tipo: {type(raw_odds)}, valor: {raw_odds}")
        
        # Converter formato da API para formato esperado pelo Decision Engine
        # Formato consistente: home, draw, away, over_2_5, under_2_5 (COM underscores)
        if raw_odds.get('home_win'):
            market_odds = {
                'home': raw_odds.get('home_win'),
                'draw': raw_odds.get('draw'),
                'away': raw_odds.get('away_win'),
                'over_2_5': raw_odds.get('over_25'),  # ✅ Converter over_25 → over_2_5
                'under_2_5': raw_odds.get('under_25'),  # ✅ Converter under_25 → under_2_5
                'btts_yes': raw_odds.get('btts_yes'),
                'btts_no': raw_odds.get('btts_no'),
            }
            logger.info(f"💰 Market odds da API Football: Home={market_odds['home']}, Draw={market_odds['draw']}, Away={market_odds['away']}, Over2.5={market_odds.get('over_2_5')}, Under2.5={market_odds.get('under_2_5')}")
        else:
            # Sem odds da API - Decision Engine vai calcular apenas fair odds (sem EV)
            market_odds = None
            logger.warning("⚠️ Sem odds da API - análise será feita sem cálculo de EV")
        
        # Log para debug
        logger.info(f"📊 MARKET ODDS FINAL: {market_odds}")
        
        # Executar decision engine UMA vez com odds corretos (ou None)
        decision_data = decision_engine.make_decision(
            model_predictions,
            features,
            market_odds,
            strategy=strategy,  # ✅ Passar strategy
            context_analysis=context_analysis  # ✅ Passar análise contextual para seleção de mercados
        )
        
        # 🔥 Extrair dados enriquecidos para enviar ao frontend E PARA A IA
        enriched_data = {
            'fixture_details': match_data.get('fixture_details'),
            'table_context': match_data.get('table_context'),
            'injuries': match_data.get('injuries'),
            'odds': match_data.get('odds'),
            'home_stats': match_data.get('home_stats'),
            'away_stats': match_data.get('away_stats'),
            'rest_context': match_data.get('rest_context'),
            'motivation': match_data.get('motivation'),
            'trends': match_data.get('trends'),
            'season_context': match_data.get('season_context'),
            'weather': match_data.get('weather'),  # 🌤️ Condições climáticas
            'h2h': match_data.get('h2h', []),  # 🆕 Histórico direto (Football-Data.org)
            'football_data_id': football_data_id,  # 🆕 ID mapeado
            'football_data_match': match_data.get('football_data_match')  # 🆕 Detalhes do Football-Data.org
        }
        
        # 6. IA Explainer (Gemini Flash apenas EXPLICA) - OPCIONAL
        result = {'success': True, 'analysis': None}
        
        logger.info(f"🤖 Verificando se deve chamar IA: skip_ai={skip_ai}")
        
        if not skip_ai:
            logger.info(f"🚀 CHAMANDO AI ANALYZER (Google Gemini) com estratégia={strategy}...")
            try:
                analyzer = AIAnalyzer()
                result = analyzer.explain_decision(decision_data, enriched_data, strategy=strategy)
                
                if not result.get('success'):
                    # Não quebrar a resposta: seguir sem IA
                    logger.error(f"❌ IA falhou: {result.get('error')} | Prosseguindo sem IA")
                    result = {'success': False, 'analysis': None, 'reasoning': None}
            except Exception as e:
                # Não retornar 500 por falha de IA; manter preview estatístico
                logger.error(f"❌ EXCEÇÃO na chamada da IA: {e}", exc_info=True)
                result = {'success': False, 'analysis': None, 'reasoning': None}
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

        # Filtrar análise IA inválida antes de retornar
        ai_analysis_text = result.get('analysis')
        if ai_analysis_text and (
            ai_analysis_text == 'None' or 
            ('ANÁLISE COMPLETA DE APOSTAS' in str(ai_analysis_text) and 'Via Placar Certo' in str(ai_analysis_text))
        ):
            logger.warning("⚠️ Análise IA inválida no quick_analyze - removendo")
            ai_analysis_text = None

        return Response({
            'analysis': ai_analysis_text,  # Texto da IA (legado - manter compatibilidade)
            'reasoning': ai_analysis_text,  # Texto da IA (novo - usado pelo AnalysisModal)
            'confidence': decision_data['confidence']['stars'],  # Confiança do Decision Engine
            'confidence_display': f"{decision_data['confidence']['level']} ({decision_data['confidence']['stars']}/5)",
            'prediction_display': decision_data['recommendation']['pick'],
            'home_probability': model_predictions['consensus']['home_win'] * 100,
            'draw_probability': model_predictions['consensus']['draw'] * 100,
            'away_probability': model_predictions['consensus']['away_win'] * 100,
            'key_factors': decision_data.get('key_factors', []),
            'value_bets': decision_data.get('value_bets', []),
            'top_bets': decision_data.get('top_bets', []),  # ✅ Incluir top apostas multi-mercado
            'strategy': decision_data.get('strategy', strategy),
            'context_analysis': context_analysis if context_analysis else {},
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
                'top_bets': decision_data.get('top_bets', []),  # ✅ Repetir dentro de analysis_data para compatibilidade
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
    
    def _calculate_market_prior(self, market_odds):
        """
        Calcula probabilidades implícitas das odds do mercado (Market Prior).
        Usa as odds para extrair a "sabedoria da multidão" (bookmakers).
        
        Args:
            market_odds (dict): Odds do mercado {'odds_home': float, 'odds_draw': float, 'odds_away': float}
        
        Returns:
            dict: Probabilidades implícitas {'home_win': float, 'draw': float, 'away_win': float}
        """
        try:
            # Extrair odds
            home_odd = market_odds.get('odds_home', 0)
            draw_odd = market_odds.get('odds_draw', 0)
            away_odd = market_odds.get('odds_away', 0)
            
            # Se alguma odd estiver faltando, retornar uniforme
            if not all([home_odd, draw_odd, away_odd]) or any(o <= 1.0 for o in [home_odd, draw_odd, away_odd]):
                logger.warning("⚠️ Market odds inválidas, usando prior uniforme")
                return {'home_win': 0.33, 'draw': 0.33, 'away_win': 0.34}
            
            # Converter odds para probabilidades implícitas
            # prob = 1 / odd (sem margem)
            prob_home = 1 / home_odd
            prob_draw = 1 / draw_odd
            prob_away = 1 / away_odd
            
            # Remover margem do bookmaker (overround)
            total = prob_home + prob_draw + prob_away
            
            # Normalizar para somar 1.0
            market_prior = {
                'home_win': prob_home / total,
                'draw': prob_draw / total,
                'away_win': prob_away / total
            }
            
            logger.info(f"📈 Market Prior calculado:")
            logger.info(f"   Odds: H={home_odd} D={draw_odd} A={away_odd}")
            logger.info(f"   Probs: H={market_prior['home_win']*100:.1f}% D={market_prior['draw']*100:.1f}% A={market_prior['away_win']*100:.1f}%")
            logger.info(f"   Margem removida: {(total-1)*100:.1f}%")
            
            return market_prior
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular Market Prior: {e}")
            return {'home_win': 0.33, 'draw': 0.33, 'away_win': 0.34}
    
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
            
            # Inicializar market_odds (para o cálculo do market prior)
            market_odds = None
            if enriched_data and enriched_data.get('odds'):
                from apps.analysis.services.odds_calculator import OddsCalculator
                from apps.analysis.config.market_standards import normalize_market_name
                
                raw_odds = enriched_data['odds']
                if raw_odds.get('home_win'):
                    # Criar dict base com nomenclatura canônica
                    base_odds = {
                        'home_win': raw_odds.get('home_win'),
                        'draw': raw_odds.get('draw'),
                        'away_win': raw_odds.get('away_win'),
                        'over_2.5': raw_odds.get('over_25'),
                        'under_2.5': raw_odds.get('under_25'),
                        'over_1.5': raw_odds.get('over_15'),
                        'under_1.5': raw_odds.get('under_15'),
                        'over_3.5': raw_odds.get('over_35'),
                        'under_3.5': raw_odds.get('under_35'),
                        'btts_yes': raw_odds.get('btts_yes'),
                    }
                    
                    # Enriquecer odds: adicionar metadados + calcular derivadas
                    odds_calc = OddsCalculator()
                    market_odds = odds_calc.enrich_odds_dict(base_odds)
                    
                    logger.info(f"💰 Market odds da API: {len([v for v in market_odds.values() if v])} mercados")
                    logger.info(f"   - Odds base (API): {len(base_odds)}")
                    logger.info(f"   - Odds calculadas (DC/DNB): {len(market_odds) - len(base_odds)}")
            
            # Ensemble com 3 modelos: 50% Poisson + 35% Logística + 15% Market Prior
            # Market Prior = probabilidades implícitas das odds do mercado
            market_prior = self._calculate_market_prior(market_odds)
            
            # Pesos calibrados (após análise de 50 jogos: 42% accuracy)
            W_POISSON = 0.50   # Modelo principal (xG, placares)
            W_LOGISTIC = 0.35  # Features contextuais (forma, lesões, clima)
            W_MARKET = 0.15    # Sabedoria das odds (bookmakers)
            
            consensus = {
                'home_win': (
                    poisson_pred['probabilities']['home_win'] * W_POISSON +
                    logistic_pred['home_win'] * W_LOGISTIC +
                    market_prior.get('home_win', 0.33) * W_MARKET
                ),
                'draw': (
                    poisson_pred['probabilities']['draw'] * W_POISSON +
                    logistic_pred['draw'] * W_LOGISTIC +
                    market_prior.get('draw', 0.33) * W_MARKET
                ),
                'away_win': (
                    poisson_pred['probabilities']['away_win'] * W_POISSON +
                    logistic_pred['away_win'] * W_LOGISTIC +
                    market_prior.get('away_win', 0.33) * W_MARKET
                ),
            }
            
            # Normalizar para somar 1.0
            total = sum(consensus.values())
            if total > 0:
                consensus = {k: v/total for k, v in consensus.items()}
            
            # Calcular odds justas a partir do consensus
            fair_odds = {
                'home_win': round(1 / consensus['home_win'], 2) if consensus['home_win'] > 0 else 999,
                'draw': round(1 / consensus['draw'], 2) if consensus['draw'] > 0 else 999,
                'away_win': round(1 / consensus['away_win'], 2) if consensus['away_win'] > 0 else 999,
            }
            
            # Se não há odds reais, simular com base nas probabilidades do consensus + margem bookmaker (5%)
            if not market_odds:
                from apps.analysis.services.odds_calculator import OddsCalculator
                
                # Preparar probabilidades para simulação
                probabilities_to_simulate = {
                    'home_win': consensus.get('home_win', 0.33),
                    'draw': consensus.get('draw', 0.33),
                    'away_win': consensus.get('away_win', 0.33),
                    'over_2.5': poisson_pred['probabilities'].get('over_2.5', 0.5),
                    'under_2.5': poisson_pred['probabilities'].get('under_2.5', 0.5),
                    'over_1.5': poisson_pred['probabilities'].get('over_1.5', 0.7),
                    'under_1.5': poisson_pred['probabilities'].get('under_1.5', 0.3),
                    'over_3.5': poisson_pred['probabilities'].get('over_3.5', 0.3),
                    'under_3.5': poisson_pred['probabilities'].get('under_3.5', 0.7),
                    'btts_yes': poisson_pred['probabilities'].get('btts', 0.5),
                    'home_over_0.5': poisson_pred['probabilities'].get('home_over_0.5', 0.8),
                    'home_over_1.5': poisson_pred['probabilities'].get('home_over_1.5', 0.4),
                    'away_over_0.5': poisson_pred['probabilities'].get('away_over_0.5', 0.8),
                    'away_over_1.5': poisson_pred['probabilities'].get('away_over_1.5', 0.4),
                    'home_clean_sheet': poisson_pred['probabilities'].get('home_clean_sheet', 0.2),
                    'away_clean_sheet': poisson_pred['probabilities'].get('away_clean_sheet', 0.2),
                }
                
                # Simular odds com margin 5% e marcar como 'simulated'
                odds_calc = OddsCalculator(bookmaker_margin=1.05)
                market_odds = odds_calc.calculate_simulated_odds(probabilities_to_simulate)
                
                logger.info("💰 Market odds simuladas com base no consensus")
                logger.info("   ⚠️ Odds simuladas não devem ser usadas para cálculo de EV")
            
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
            
            # 🆕 ContextAnalyzer - Analisar padrões contextuais
            context_analysis = None
            if features:
                try:
                    from apps.analysis.services.context_analyzer import ContextAnalyzer
                    context_analyzer = ContextAnalyzer()
                    context_analysis = context_analyzer.analyze(features)
                    logger.info(f"✅ ContextAnalyzer executado: {len(context_analysis.get('patterns', []))} padrões detectados")
                except Exception as e:
                    logger.error(f"❌ Erro ao executar ContextAnalyzer: {e}")
                    context_analysis = None
            
            # Chamar DecisionEngine para gerar top_bets com múltiplos mercados
            from apps.analysis.services.decision_engine import DecisionEngine
            decision_engine = DecisionEngine()
            
            model_predictions = {
                'consensus': consensus,
                'poisson': poisson_pred,
                'logistic': logistic_pred,
            }
            
            # make_decision com strategy padrão 'value' (preview neutro)
            decision_data = decision_engine.make_decision(
                model_predictions,
                features if features else {},
                market_odds,
                strategy='value',  # Preview sempre usa VALUE (neutro)
                context_analysis=context_analysis  # 🆕 Passar análise contextual
            )
            
            logger.info(f"✅ DecisionEngine gerou {len(decision_data.get('top_bets', []))} apostas")
            
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
                    'market_odds': market_odds,
                    'features_summary': features_summary,
                    'recommendation': {
                        'pick': pick,
                        'probability': max_prob
                    },
                    'confidence': {
                        'level': confidence_level,
                        'stars': confidence_stars,
                        'score': prob_diff
                    },
                    'risk': risk_level,
                    'top_bets': decision_data.get('top_bets', []),  # ✅ ADICIONADO: Top apostas multi-mercado
                    'is_preview': True,
                    'has_real_data': bool(features or enriched_data)
                },
                'enriched_data': enriched_data or {}
            })
            
        except Exception as e:
            logger.error(f"Erro no statistical_preview: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Erro ao calcular estatísticas', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def live_probabilities(self, request, pk=None):
        """
        Recalcula probabilidades durante jogo ao vivo baseado no score atual.
        Endpoint chamado pelo polling de 30s para manter dados frescos.
        
        Ajusta o modelo Poisson baseado em:
        - Score atual (home_score, away_score)
        - Tempo decorrido (elapsed_minutes)
        - Estatísticas do jogo (posse, chutes, cantos)
        """
        try:
            match = self.get_object()
            
            # Verificar se o jogo está ao vivo
            if match.status not in ['LIVE', '1H', '2H', 'HT', 'ET', 'P']:
                return Response({
                    'error': 'Esta partida não está ao vivo',
                    'status': match.status
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"\n🔴 RECALCULANDO PROBABILIDADES AO VIVO")
            logger.info(f"   Partida: {match.home_team.name} vs {match.away_team.name}")
            logger.info(f"   Score: {match.home_score} x {match.away_score}")
            logger.info(f"   Status: {match.status}")
            
            from apps.analysis.services.match_enricher import MatchDataEnricher
            from apps.analysis.services.feature_engineer import FeatureEngineer
            from apps.analysis.services.statistical_models import PoissonBivariateModel, LogisticRegressionModel
            from apps.analysis.models import Analysis
            
            # 1. Buscar dados ao vivo do API-Football
            api_service = FootballAPIService()
            
            # Tentar obter API ID do match (se armazenado)
            api_id = getattr(match, 'external_api_id', None) or getattr(match, 'api_id', None)
            
            live_data = {}
            if api_id:
                try:
                    result = api_service.get_fixture_live(api_id)
                    if result.get('success') and result.get('fixture'):
                        fixture = result['fixture']
                        
                        # Extrair estatísticas ao vivo
                        live_data = {
                            'home_score': fixture.get('goals', {}).get('home', match.home_score),
                            'away_score': fixture.get('goals', {}).get('away', match.away_score),
                            'elapsed': fixture.get('fixture', {}).get('status', {}).get('elapsed', 45),
                            'statistics': fixture.get('statistics', [])
                        }
                        
                        # Atualizar score do match se mudou
                        if live_data['home_score'] != match.home_score or live_data['away_score'] != match.away_score:
                            match.home_score = live_data['home_score']
                            match.away_score = live_data['away_score']
                            match.save(update_fields=['home_score', 'away_score'])
                            logger.info(f"✅ Score atualizado: {match.home_score} x {match.away_score}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao buscar dados ao vivo: {e}")
            
            # 2. Ajustar λ do Poisson baseado no score e tempo
            home_score = match.home_score or 0
            away_score = match.away_score or 0
            
            # Estimar tempo decorrido baseado no status
            elapsed = 45 if match.status in ['1H', 'HT'] else 70
            remaining_minutes = max(0, 90 - elapsed)
            
            # Buscar análise prévia para obter λ original, ou usar valores padrão
            previous_analysis = Analysis.objects.filter(match=match).order_by('-created_at').first()
            
            # λ ajustado = gols já marcados + (λ_original × tempo_restante/90)
            if previous_analysis and previous_analysis.analysis_data.get('poisson'):
                poisson_data = previous_analysis.analysis_data['poisson']
                lambda_home_original = poisson_data.get('lambda_home', 1.5)
                lambda_away_original = poisson_data.get('lambda_away', 1.3)
            else:
                # Valores padrão baseados em xG médio
                lambda_home_original = 1.5  # xG médio casa
                lambda_away_original = 1.3  # xG médio fora
            
            # Calcular novo λ baseado em performance até agora
            lambda_home_adjusted = home_score + (lambda_home_original * remaining_minutes / 90)
            lambda_away_adjusted = away_score + (lambda_away_original * remaining_minutes / 90)
            
            logger.info(f"📊 λ ajustado: Casa={lambda_home_adjusted:.2f}, Fora={lambda_away_adjusted:.2f}")
            
            # 3. Recalcular probabilidades com Poisson ajustado
            poisson = PoissonBivariateModel()
            poisson_result = poisson.predict(lambda_home_adjusted, lambda_away_adjusted)
            adjusted_probs = poisson_result['probabilities']
            
            # 4. Calcular fair odds
            def calc_fair_odd(probability):
                if probability <= 0:
                    return 999.0
                return round(1.0 / probability, 2)
            
            fair_odds = {
                'home_win': calc_fair_odd(adjusted_probs['home_win']),
                'draw': calc_fair_odd(adjusted_probs['draw']),
                'away_win': calc_fair_odd(adjusted_probs['away_win'])
            }
            
            # 5. Determinar recomendação
            max_prob = max(adjusted_probs['home_win'], adjusted_probs['draw'], adjusted_probs['away_win'])
            if adjusted_probs['home_win'] == max_prob:
                pick = 'home_win'
            elif adjusted_probs['draw'] == max_prob:
                pick = 'draw'
            else:
                pick = 'away_win'
            
            # 6. Calcular confiança
            prob_values = [adjusted_probs['home_win'], adjusted_probs['draw'], adjusted_probs['away_win']]
            prob_values.sort(reverse=True)
            prob_diff = prob_values[0] - prob_values[1]
            
            if prob_diff > 0.25:
                confidence_level = 'high'
                confidence_stars = 4
            elif prob_diff > 0.15:
                confidence_level = 'medium'
                confidence_stars = 3
            else:
                confidence_level = 'low'
                confidence_stars = 2
            
            # 7. Retornar dados atualizados
            return Response({
                'success': True,
                'updated_at': timezone.now().isoformat(),
                'match_state': {
                    'home_score': home_score,
                    'away_score': away_score,
                    'elapsed_minutes': elapsed,
                    'status': match.status
                },
                'analysis_data': {
                    'consensus': {
                        'home_win': adjusted_probs['home_win'],
                        'draw': adjusted_probs['draw'],
                        'away_win': adjusted_probs['away_win']
                    },
                    'poisson': {
                        'home_win': adjusted_probs['home_win'],
                        'draw': adjusted_probs['draw'],
                        'away_win': adjusted_probs['away_win'],
                        'lambda_home': lambda_home_adjusted,
                        'lambda_away': lambda_away_adjusted,
                        'adjusted_for_live': True
                    },
                    'fair_odds': fair_odds,
                    'recommendation': {
                        'pick': pick,
                        'probability': max_prob
                    },
                    'confidence': {
                        'level': confidence_level,
                        'stars': confidence_stars,
                        'score': prob_diff
                    },
                    'is_live': True,
                    'last_update': timezone.now().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"Erro no live_probabilities: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Erro ao recalcular probabilidades ao vivo', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='unified-analysis')
    def unified_analysis(self, request, pk=None):
        """
        🚀 ENDPOINT UNIFICADO: Retorna análise completa com cache inteligente
        
        POST /api/matches/{id}/unified-analysis/
        Body: {
            "strategy": "value" | "multiple",
            "include_ai": true | false,
            "force_refresh": false
        }
        
        Response: {
            "phase": "complete",
            "cached": false,
            "statistical_data": {...},  # Onda 1
            "decision_data": {...},      # Onda 2
            "ai_analysis": "...",         # Onda 3
            "metadata": {...}
        }
        
        Performance:
        - Cache Hit: ~50ms (90% das requests após primeira análise)
        - Cache Miss: 2-8s (depende de include_ai)
        """
        # LOG IMEDIATO PARA CONFIRMAR EXECUÇÃO
        print("="*100)
        print("TESTE TESTE TESTE - UNIFIED_ANALYSIS FOI CHAMADO - VERSAO NOVA")
        print(f"Match ID recebido: {self.kwargs.get('pk')}")
        print("="*100)
        
        from apps.analysis.services.cache_service import get_cache
        
        logger.info("="*80)
        logger.info("🚀🚀🚀 UNIFIED_ANALYSIS INICIADO - VERSÃO ATUALIZADA")
        logger.info("="*80)
        
        try:
            # Tentar buscar match do banco de dados
            match_id = self.kwargs.get('pk')
            match = None
            is_external_match = False
            
            logger.info(f"🔍 UNIFIED_ANALYSIS - Iniciando busca do match. ID recebido: {match_id} (tipo: {type(match_id)})")
            
            # 1. Tentar buscar por ID do banco
            try:
                logger.info(f"📍 Tentativa 1: Buscar por self.get_object()...")
                match = self.get_object()
                logger.info(f"✅ Match encontrado no banco de dados por ID: {match.id} (api_football_id: {match.api_football_id})")
            except Exception as e1:
                logger.warning(f"⚠️ get_object() falhou: {type(e1).__name__}: {e1}")
                # 2. Tentar buscar por api_football_id
                try:
                    logger.info(f"📍 Tentativa 2: Buscar por api_football_id={match_id}...")
                    match = Match.objects.get(api_football_id=match_id)
                    logger.info(f"✅ Match encontrado por api_football_id: {match_id} → DB ID: {match.id}")
                except Match.DoesNotExist as e2:
                    logger.warning(f"⚠️ Match.DoesNotExist: Match {match_id} não existe na tabela")
                    # 3. Match não existe - criar automaticamente antes de processar
                    logger.info(f"⚠️ Match {match_id} não encontrado no banco - tentando criar automaticamente...")
                    
                    from .services.football_api import FootballAPIService
                    api_service = FootballAPIService()
                    
                    try:
                        logger.info(f"📡 Buscando dados do match {match_id} da API externa...")
                        match_data = api_service.get_fixture_by_id(match_id)
                        logger.info(f"📡 Resposta da API: success={match_data.get('success') if match_data else None}")
                        
                        if match_data and match_data.get('success') and match_data.get('fixture'):
                            fixture = match_data['fixture']
                            logger.info(f"✅ Dados do fixture recebidos: {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']}")
                            
                            # Buscar ou criar times
                            logger.info(f"👥 Criando/buscando time casa (ID: {fixture['teams']['home']['id']})")
                            home_team, created_home = Team.objects.get_or_create(
                                api_football_id=fixture['teams']['home']['id'],
                                defaults={
                                    'name': fixture['teams']['home']['name'],
                                    'logo': fixture['teams']['home']['logo']
                                }
                            )
                            logger.info(f"✅ Time casa: {home_team.name} ({'criado' if created_home else 'existente'})")
                            
                            logger.info(f"👥 Criando/buscando time fora (ID: {fixture['teams']['away']['id']})")
                            away_team, created_away = Team.objects.get_or_create(
                                api_football_id=fixture['teams']['away']['id'],
                                defaults={
                                    'name': fixture['teams']['away']['name'],
                                    'logo': fixture['teams']['away']['logo']
                                }
                            )
                            logger.info(f"✅ Time fora: {away_team.name} ({'criado' if created_away else 'existente'})")
                            
                            # Buscar ou criar a League
                            logger.info(f"🏆 Criando/buscando liga (ID: {fixture['league']['id']})")
                            from apps.matches.models import League
                            league, created_league = League.objects.get_or_create(
                                api_football_id=fixture['league']['id'],
                                defaults={
                                    'name': fixture['league']['name'],
                                    'country': fixture['league'].get('country', ''),
                                    'logo': fixture['league'].get('logo', '')
                                }
                            )
                            logger.info(f"✅ Liga: {league.name} ({'criada' if created_league else 'existente'})")
                            
                            # Criar o match no banco (ou buscar se já existe)
                            logger.info(f"⚽ Criando/buscando match no banco de dados...")
                            match, created = Match.objects.get_or_create(
                                api_football_id=match_id,
                                defaults={
                                    'league': league,
                                    'home_team': home_team,
                                    'away_team': away_team,
                                    'match_date': fixture['fixture']['date'],
                                    'status': fixture['fixture']['status']['short'],
                                    'round': fixture['league'].get('round', '')
                                }
                            )
                            
                            # ✅ IMPORTANTE: Match criado/encontrado com sucesso, NÃO é externo!
                            is_external_match = False
                            logger.info(f"✅✅✅ Match {'criado' if created else 'encontrado'} no banco: ID {match.id} (api_football_id: {match_id})")
                            logger.info(f"✅ is_external_match = {is_external_match} - SERÁ SALVO NO HISTÓRICO!")
                        else:
                            # Se falhar ao buscar da API, marcar como externo
                            logger.warning(f"⚠️ API não retornou fixture válido - tratando como externo")
                            logger.warning(f"⚠️ match_data: {match_data}")
                            is_external_match = True
                    except Exception as create_error:
                        logger.error(f"❌ ERRO ao criar match automaticamente: {create_error}", exc_info=True)
                        logger.error(f"❌ Tipo do erro: {type(create_error).__name__}")
                        is_external_match = True
            
            strategy = request.data.get('strategy', 'value')
            include_ai = request.data.get('include_ai', True)
            force_refresh = request.data.get('force_refresh', False)
            
            # 🔍 DEBUG: Log completo do request
            logger.info(f"🔍 DEBUG REQUEST DATA: {request.data}")
            logger.info(f"🔍 force_refresh recebido: {force_refresh} (tipo: {type(force_refresh)})")
            
            # Garantir que strategy é string
            if isinstance(strategy, dict):
                strategy = strategy.get('strategy', 'value')
            if not isinstance(strategy, str):
                strategy = 'value'
            
            logger.info(f"\n{'='*80}")
            if is_external_match:
                logger.info(f"🚀 UNIFIED ANALYSIS - Match EXTERNO (API ID: {self.kwargs.get('pk')})")
            else:
                logger.info(f"🚀 UNIFIED ANALYSIS - Match {match.id}")
            logger.info(f"   Strategy: {strategy}, Include AI: {include_ai}, Force: {force_refresh}")
            logger.info(f"{'='*80}\n")
            
            # 🔥 VERIFICAR LIMITE ANTES DE PROCESSAR (se usuário autenticado)
            if request.user.is_authenticated and not request.user.can_analyze():
                logger.warning(f"⚠️ Usuário {request.user.username} atingiu limite diário antes de processar")
                return Response(
                    {'error': 'Limite diário de análises atingido', 'code': 'QUOTA_EXCEEDED'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Inicializar cache_service (pode ser usado em ambos os casos)
            cache_service = get_cache() if not is_external_match else None
            
            # Inicializar api_id (para ambos os casos)
            api_id = self.kwargs.get('pk') if is_external_match else (match.id if match else None)
            
            # SE FOR MATCH EXTERNO: usar quick_analyze internamente
            if is_external_match:
                logger.info("🌐 Match externo detectado - usando lógica de quick_analyze...")
                
                # api_id já foi definido acima
                
                from .services.football_api import FootballAPIService
                api_service = FootballAPIService()
                
                try:
                    # Buscar dados básicos do match
                    fixture_result = api_service.get_fixture_by_id(api_id)
                    
                    if not fixture_result.get('success') or not fixture_result.get('fixture'):
                        raise Exception(f"Não foi possível buscar fixture {api_id} da API")
                    
                    fixture = fixture_result['fixture']
                    
                    # Construir match_data para análise
                    match_data = {
                        'home_team': {'name': fixture['teams']['home']['name']},
                        'away_team': {'name': fixture['teams']['away']['name']},
                        'league': fixture.get('league', {}).get('name', 'Liga desconhecida'),
                        'date': fixture.get('fixture', {}).get('date'),
                        'status': fixture.get('fixture', {}).get('status', {}).get('short'),
                        'venue': fixture.get('fixture', {}).get('venue', {}).get('name'),
                        'home_score': fixture.get('goals', {}).get('home'),
                        'away_score': fixture.get('goals', {}).get('away'),
                        'api_id': api_id
                    }
                    
                    logger.info(f"✅ Dados do match externo carregados: {match_data['home_team']['name']} vs {match_data['away_team']['name']}")
                    
                    # Enriquecer dados (buscar estatísticas, predictions, etc.)
                    from apps.analysis.services.match_enricher import MatchDataEnricher
                    enricher = MatchDataEnricher()
                    match_data = enricher.enrich(match_data)
                    
                    # DEBUG: Verificar se odds existem após enrichment
                    logger.info(f"🔍 APÓS ENRICHMENT - match_data.keys(): {list(match_data.keys())}")
                    logger.info(f"🔍 APÓS ENRICHMENT - match_data.get('odds'): {match_data.get('odds')}")
                    
                    # Executar análise estatística + decisão
                    from apps.analysis.services.feature_engineer import FeatureEngineer
                    from apps.analysis.services.statistical_models import ModelEnsemble
                    from apps.analysis.services.decision_engine import DecisionEngine
                    from apps.analysis.services.ai_analyzer import AIAnalyzer
                    
                    # Feature Engineering
                    engineer = FeatureEngineer()
                    features = engineer.engineer_all_features(match_data)
                    
                    # 🆕 ContextAnalyzer - Analisar padrões contextuais
                    context_analysis = None
                    try:
                        from apps.analysis.services.context_analyzer import ContextAnalyzer
                        context_analyzer = ContextAnalyzer()
                        context_analysis = context_analyzer.analyze(features)
                        logger.info(f"✅ ContextAnalyzer executado: {len(context_analysis.get('patterns', []))} padrões detectados")
                    except Exception as e:
                        logger.error(f"❌ Erro ao executar ContextAnalyzer: {e}")
                        context_analysis = None
                    
                    # Modelos estatísticos usando ModelEnsemble
                    home_strength = match_data.get('home_stats', {}).get('goals_per_game_avg', 1.5)
                    away_strength = match_data.get('away_stats', {}).get('goals_per_game_avg', 1.3)
                    home_defense = match_data.get('home_stats', {}).get('conceded_per_game_avg', 1.3)
                    away_defense = match_data.get('away_stats', {}).get('conceded_per_game_avg', 1.3)
                    
                    # Ajustar pela forma recente
                    form_diff = features.get('form', {}).get('adjusted_form_diff', 0)
                    home_strength += form_diff * 0.1
                    away_strength -= form_diff * 0.1
                    
                    weather_impact = features.get('weather', {}).get('goal_impact', 0.0)
                    
                    # Usar ModelEnsemble (combina Poisson + Logistic)
                    ensemble = ModelEnsemble()
                    model_predictions = ensemble.predict(
                        features, 
                        home_strength, 
                        away_strength, 
                        weather_impact,
                        league_id=match_data.get('fixture', {}).get('league_id'),
                        home_defense=home_defense, 
                        away_defense=away_defense
                    )
                    
                    # 🔍 DEBUG: Log model_predictions retornado pelo ensemble
                    logger.info(f"🔍 DEBUG MODEL_PREDICTIONS RETORNADO PELO ENSEMBLE:")
                    logger.info(f"   Keys disponíveis: {list(model_predictions.keys())}")
                    logger.info(f"   consensus: {model_predictions.get('consensus', 'NOT FOUND')}")
                    logger.info(f"   market_prior: {model_predictions.get('market_prior', 'NOT FOUND')}")
                    logger.info(f"   poisson probs: {model_predictions.get('poisson', {}).get('probabilities', 'NOT FOUND')}")
                    
                    # Decision Engine - Preparar odds do mercado
                    raw_odds = match_data.get('odds') or {}
                    logger.info(f"🔍 RAW_ODDS tipo: {type(raw_odds)}, valor: {raw_odds}")
                    
                    # Converter formato da API para formato esperado pelo Decision Engine
                    has_odds = bool(raw_odds.get('home_win'))
                    
                    if has_odds:
                        # Enriquecer odds com derivados (DC/DNB/Asian) para cálculo de EV real
                        from apps.analysis.services.odds_calculator import OddsCalculator
                        base_odds = {
                            'home_win': raw_odds.get('home_win'),
                            'draw': raw_odds.get('draw'),
                            'away_win': raw_odds.get('away_win'),
                            'over_2.5': raw_odds.get('over_25'),
                            'under_2.5': raw_odds.get('under_25'),
                            'over_1.5': raw_odds.get('over_15'),
                            'under_1.5': raw_odds.get('under_15'),
                            'over_3.5': raw_odds.get('over_35'),
                            'under_3.5': raw_odds.get('under_35'),
                            'btts_yes': raw_odds.get('btts_yes'),
                            'btts_no': raw_odds.get('btts_no'),
                        }
                        odds_calc = OddsCalculator()
                        market_odds = odds_calc.enrich_odds_dict(base_odds)
                        logger.info(f"💰 Market odds enriquecidas: {len([k for k,v in market_odds.items() if v])} mercados")
                    else:
                        market_odds = None
                        logger.warning(f"⚠️ Sem odds da API para fixture {api_id} - Liga pode não ter cobertura de bookmakers")
                    
                    decision_engine = DecisionEngine()
                    decision = decision_engine.make_decision(
                        model_predictions=model_predictions,
                        features=features,
                        market_odds=market_odds,
                        strategy=strategy,
                        context_analysis=context_analysis  # 🆕 Passar análise contextual
                    )
                    
                    # DEBUG: Verificar top_bets na decisão
                    logger.info(f"🔍 DECISION retornou top_bets: {decision.get('top_bets', [])}")
                    logger.info(f"🔍 DECISION keys: {list(decision.keys())}")
                    
                    # IA (se solicitado) - SEMPRE gerar quando include_ai=True
                    ai_analysis = None
                    if include_ai:
                        logger.info(f"🤖 Chamando IA para análise...")
                        ai_analyzer = AIAnalyzer()
                        ai_result = ai_analyzer.explain_decision(
                            decision_data=decision,
                            enriched_data=match_data,
                            strategy=strategy
                        )
                        raw_analysis = ai_result.get('analysis', '')
                        
                        # Filtrar APENAS análises com o texto estruturado COMPLETO antigo
                        # Aceitar fallback (que tem formato similar à IA)
                        if raw_analysis and \
                           raw_analysis != 'None' and \
                           not ('ANÁLISE COMPLETA DE APOSTAS' in str(raw_analysis) and 'Via Placar Certo' in str(raw_analysis)):
                            ai_analysis = raw_analysis
                        else:
                            if raw_analysis:
                                logger.warning("⚠️ Análise IA inválida - ignorando")
                            ai_analysis = None
                    
                    # Estruturar resposta
                    analysis_result = {
                        'analysis_data': {
                            'model_predictions': model_predictions,
                            'decision': decision,
                            'fair_odds': decision.get('fair_odds', {}),
                            'market_odds': market_odds,
                        },
                        'enriched_data': match_data.get('enriched_data', {}),
                        'analysis': ai_analysis
                    }
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao processar match externo: {e}", exc_info=True)
                    return Response(
                        {'error': 'Erro ao processar match externo', 'details': str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            
            else:
                # MATCH DO BANCO DE DADOS: usar cache e orchestrator normal
                # Verificar cache (se não forçar refresh)
                logger.info(f"🔍 Verificando cache: force_refresh={force_refresh}")
                if not force_refresh:
                    logger.info("🔍 Tentando buscar do CACHE...")
                    cached_result = cache_service.get(match.id, strategy, include_ai)
                    
                    if cached_result:
                        logger.info("✅ Retornando dados do CACHE")
                        logger.info(f"🔍 Consensus do cache: {cached_result.get('statistical_data', {}).get('consensus', {})}")
                        return Response({
                            **cached_result,
                            'cached': True,
                            'cache_stats': cache_service.stats()
                        })
                    else:
                        logger.info("❌ Cache MISS - não encontrado no cache")
                else:
                    logger.info("🔥 FORCE REFRESH = TRUE - IGNORANDO CACHE!")
                
                # Cache miss ou force refresh: gerar análise
                logger.info(f"🔄 Gerando NOVA análise com estratégia {strategy}...")
                
                # Usar AnalysisOrchestrator existente (método run)
                orchestrator = HybridAnalysisOrchestrator()
                analysis_result = orchestrator.run(match, strategy=strategy)
                
                logger.info(f"🔍 Consensus gerado pelo orchestrator: {analysis_result.get('consensus', {})}")
                
                # Se include_ai=False, remover a análise IA
                if not include_ai:
                    analysis_result['reasoning'] = None
                    logger.info("⏭️ include_ai=False: removendo análise de IA")
            
            # Estruturar resposta unificada (para ambos os casos)
            unified_response = {
                'phase': 'complete',
                'cached': False if is_external_match else False,  # Externos nunca em cache
                'match_id': api_id if is_external_match else match.id,
                'strategy': strategy,
                
                # Adicionar informações do match (para external matches)
                'match_info': {
                    'home_team': {'name': match_data.get('home_team', {}).get('name', 'Casa')} if is_external_match else {'name': match.home_team},
                    'away_team': {'name': match_data.get('away_team', {}).get('name', 'Fora')} if is_external_match else {'name': match.away_team},
                    'league': {'name': match_data.get('league', 'N/A')} if is_external_match else {'name': match.league.name if match.league else 'N/A'},
                    'match_date': match_data.get('date') if is_external_match else (match.match_date.isoformat() if match.match_date else None),
                } if is_external_match else None,
                
                # Onda 1: Dados estatísticos (preview)
                'statistical_data': {
                    'consensus': analysis_result.get('analysis_data', {}).get('model_predictions', {}).get('consensus', {}) if is_external_match else analysis_result.get('analysis_data', {}).get('consensus', {}),
                    'confidence': analysis_result.get('analysis_data', {}).get('decision', {}).get('confidence', {}) if is_external_match else analysis_result.get('analysis_data', {}).get('confidence', {}),
                    'poisson': analysis_result.get('analysis_data', {}).get('model_predictions', {}).get('poisson', {}) if is_external_match else analysis_result.get('analysis_data', {}).get('poisson', {}),
                },
                
                # 🔍 DEBUG: Log consensus retornado
                # TEMPORÁRIO - remover após debug
            }
            
            logger.info(f"🔍 DEBUG CONSENSUS RETORNADO AO FRONTEND:")
            logger.info(f"   is_external_match: {is_external_match}")
            logger.info(f"   statistical_data.consensus: {unified_response['statistical_data']['consensus']}")
            logger.info(f"   Valores numéricos:")
            consensus_debug = unified_response['statistical_data']['consensus']
            if consensus_debug:
                logger.info(f"      Casa: {consensus_debug.get('home_win', 'N/A')}")
                logger.info(f"      Empate: {consensus_debug.get('draw', 'N/A')}")
                logger.info(f"      Fora: {consensus_debug.get('away_win', 'N/A')}")
            else:
                logger.warning(f"   ⚠️ CONSENSUS ESTÁ VAZIO!")
                
            if is_external_match:
                logger.info(f"   EXTERNAL - Path usado: analysis_result['analysis_data']['model_predictions']['consensus']")
                logger.info(f"   model_predictions keys: {list(analysis_result.get('analysis_data', {}).get('model_predictions', {}).keys())}")
                
                # Verificar se market_prior existe e comparar
                market_prior_check = analysis_result.get('analysis_data', {}).get('model_predictions', {}).get('market_prior')
                if market_prior_check:
                    logger.info(f"   MARKET_PRIOR também existe:")
                    logger.info(f"      Casa: {market_prior_check.get('home_win', 'N/A')}")
                    logger.info(f"      Empate: {market_prior_check.get('draw', 'N/A')}")
                    logger.info(f"      Fora: {market_prior_check.get('away_win', 'N/A')}")
            else:
                logger.info(f"   INTERNAL - Path usado: analysis_result['analysis_data']['consensus']")
            
            unified_response2 = {
                'decision_data': {
                    # Usar 'top_bets' - agora com estrutura completa do DecisionEngine
                    'top_bets': analysis_result.get('analysis_data', {}).get('decision', {}).get('top_bets', []) if is_external_match else analysis_result.get('analysis_data', {}).get('top_bets', []),
                    'recommendation': analysis_result.get('analysis_data', {}).get('decision', {}).get('recommendation', {}) if is_external_match else analysis_result.get('analysis_data', {}).get('recommendation', {}),
                    'risk': analysis_result.get('analysis_data', {}).get('decision', {}).get('risk', 'medium') if is_external_match else analysis_result.get('analysis_data', {}).get('risk', 'medium'),
                    'has_odds': bool(analysis_result.get('analysis_data', {}).get('market_odds')),  # Flag para frontend
                },
                
                # Onda 3: Análise IA (se solicitado)
                'ai_analysis': analysis_result.get('analysis', '') if is_external_match else analysis_result.get('reasoning', ''),
                
                # Metadata
                'metadata': {
                    'enriched_data': analysis_result.get('enriched_data', {}),
                    'fair_odds': analysis_result.get('analysis_data', {}).get('decision', {}).get('fair_odds', {}) if is_external_match else analysis_result.get('analysis_data', {}).get('fair_odds', {}),
                    'market_odds': analysis_result.get('analysis_data', {}).get('market_odds', {}),
                    'generated_at': timezone.now().isoformat(),
                },
                
                # Stats (não há cache para externos)
                'cache_stats': {} if is_external_match else cache_service.stats()
            }
            
            # Merge unified_response e unified_response2
            unified_response.update(unified_response2)
            
            # Salvar no cache (apenas se for match do banco)
            if not is_external_match and cache_service:
                cache_service.set(match.id, strategy, unified_response, include_ai)
                logger.info(f"✅ Análise completa gerada e cacheada")
            else:
                logger.info(f"✅ Análise completa gerada (match externo - sem cache)")
            
            # 🔥 SALVAR NO HISTÓRICO E INCREMENTAR CONTADOR
            analysis_id = None
            
            logger.info(f"🔍 SALVAMENTO - Estado antes de salvar:")
            logger.info(f"   - Usuário autenticado: {request.user.is_authenticated}")
            logger.info(f"   - User: {request.user if request.user.is_authenticated else 'AnonymousUser'}")
            logger.info(f"   - is_external_match: {is_external_match}")
            logger.info(f"   - match existe: {match is not None}")
            logger.info(f"   - match.id: {match.id if match else 'N/A'}")
            
            if request.user.is_authenticated and not is_external_match and match:
                # ⚠️ Só salvar se for match do banco (não external)
                try:
                    logger.info(f"🔍 SALVAMENTO - Iniciando criação de Analysis...")
                    logger.info(f"🔍 DEBUG - unified_response['decision_data']: {unified_response.get('decision_data', {})}")
                    
                    # Preparar dados para salvar
                    consensus = unified_response['statistical_data'].get('consensus', {})
                    confidence = unified_response['statistical_data'].get('confidence', {})
                    
                    # Determinar predição
                    home_prob = consensus.get('home_win', 0)
                    draw_prob = consensus.get('draw', 0)
                    away_prob = consensus.get('away_win', 0)
                    
                    if home_prob > draw_prob and home_prob > away_prob:
                        prediction = 'home'
                    elif away_prob > home_prob and away_prob > draw_prob:
                        prediction = 'away'
                    else:
                        prediction = 'draw'
                    
                    # ✅ Converter confidence de string para número (1-5)
                    confidence_level = confidence.get('level', 3)
                    if isinstance(confidence_level, str):
                        # Mapear string → número
                        confidence_map = {
                            'very_low': 1,
                            'low': 2,
                            'medium': 3,
                            'high': 4,
                            'very_high': 5
                        }
                        confidence_level = confidence_map.get(confidence_level, 3)
                    
                    # ✅ Converter probabilidades de decimal (0-1) para porcentagem (0-100)
                    home_prob_pct = home_prob * 100
                    draw_prob_pct = draw_prob * 100
                    away_prob_pct = away_prob * 100
                    
                    # Criar ou atualizar registro de análise (APENAS PARA MATCHES DO BANCO)
                    analysis, created = Analysis.objects.update_or_create(
                        user=request.user,
                        match=match,
                        defaults={
                            'prediction': prediction,
                            'confidence': confidence_level,
                            'home_probability': home_prob_pct,
                            'draw_probability': draw_prob_pct,
                            'away_probability': away_prob_pct,
                            'home_xg': unified_response['statistical_data'].get('poisson', {}).get('home_xg'),
                            'away_xg': unified_response['statistical_data'].get('poisson', {}).get('away_xg'),
                            'analysis_data': unified_response['decision_data'],
                            'reasoning': unified_response.get('ai_analysis', ''),
                            'key_factors': []
                        }
                    )
                    
                    analysis_id = analysis.id
                    
                    # Incrementar contador do usuário apenas se for nova análise
                    if created:
                        request.user.daily_analysis_count += 1
                        request.user.last_analysis_date = timezone.now().date()
                        request.user.save(update_fields=['daily_analysis_count', 'last_analysis_date'])
                        logger.info(f"✅ Nova análise salva no histórico (ID: {analysis_id}), contador: {request.user.daily_analysis_count}")
                    else:
                        logger.info(f"♻️ Análise atualizada no histórico (ID: {analysis_id})")

                    
                    # Adicionar analysis_id na resposta
                    unified_response['analysis_id'] = analysis_id
                    logger.info(f"🔍 SALVAMENTO - analysis_id adicionado à resposta: {analysis_id}")
                    
                except Exception as save_error:
                    logger.error(f"❌ Erro ao salvar análise no histórico: {save_error}", exc_info=True)
                    # Continuar mesmo se falhar ao salvar
            elif request.user.is_authenticated and is_external_match:
                # ⚠️ Match externo: incrementar contador mas não salvar histórico
                logger.warning(f"⚠️ SALVAMENTO - Match VERDADEIRAMENTE externo ({api_id if is_external_match else 'N/A'}) - incrementando contador sem salvar histórico")
                request.user.daily_analysis_count += 1
                request.user.last_analysis_date = timezone.now().date()
                request.user.save(update_fields=['daily_analysis_count', 'last_analysis_date'])
                logger.info(f"✅ Contador incrementado: {request.user.daily_analysis_count}")
            else:
                logger.warning(f"⚠️ SALVAMENTO - Análise NÃO será salva. Razões:")
                logger.warning(f"   - Usuário autenticado: {request.user.is_authenticated}")
                logger.warning(f"   - is_external_match: {is_external_match}")
                logger.warning(f"   - match existe: {match is not None}")
            
            logger.info(f"🔍 RESPOSTA FINAL - Keys: {list(unified_response.keys())}, has analysis_id: {'analysis_id' in unified_response}")
            
            return Response(unified_response)
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"❌ ERRO NO UNIFIED_ANALYSIS: {str(e)}")
            logger.error(f"📍 Traceback completo:\n{error_traceback}")
            return Response(
                {
                    'error': 'Erro ao gerar análise unificada',
                    'details': str(e),
                    'type': type(e).__name__,
                    'match_id': self.kwargs.get('pk')
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
