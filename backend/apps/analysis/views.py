from rest_framework import viewsets, status as http_status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count, Q, Avg, Sum
from datetime import timedelta
import logging

from .models import Analysis, DailyBet
from .serializers import (
    AnalysisSerializer, 
    AnalysisRequestSerializer,
    DailyBetSerializer,
    DailyBetListSerializer
)
from apps.matches.models import Match

logger = logging.getLogger(__name__)


class AnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Análises"""
    serializer_class = AnalysisSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['prediction', 'confidence']
    
    def get_queryset(self):
        """Retorna apenas análises do usuário"""
        queryset = Analysis.objects.filter(user=self.request.user).select_related(
            'match', 'match__league', 'match__home_team', 'match__away_team'
        ).order_by('-created_at')
        
        # Filtro de pesquisa
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(match__home_team__name__icontains=search) |
                Q(match__away_team__name__icontains=search) |
                Q(match__league__name__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def request_analysis(self, request):
        """Solicita análise de uma partida"""
        # Validar dados
        serializer = AnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        match_id = serializer.validated_data['match_id']
        user = request.user
        
        # Parâmetro para forçar recálculo (útil para testar correções)
        force_recalculate = request.data.get('force_recalculate', False)
        
        # Verificar se usuário pode analisar
        if not user.can_analyze():
            return Response({
                'error': 'Limite de análises diárias atingido',
                'daily_limit': 5 if not user.is_premium_active() else 100,
                'used': user.daily_analysis_count
            }, status=http_status.HTTP_403_FORBIDDEN)
        
        # Verificar se já existe análise
        match = Match.objects.get(id=match_id)
        existing = Analysis.objects.filter(user=user, match=match).first()
        
        if existing and not force_recalculate:
            return Response({
                'message': 'Você já analisou esta partida',
                'analysis': AnalysisSerializer(existing).data
            }, status=http_status.HTTP_200_OK)
        
        # Se force_recalculate=True, deletar análise antiga
        if existing and force_recalculate:
            existing.delete()
        
        # Usar o orquestrador híbrido (modelos + decisão + IA explicativa)
        from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
        orchestrator = HybridAnalysisOrchestrator()
        result = orchestrator.run(match)

        prediction = result['prediction']
        confidence = result['confidence']
        home_p = result['home_probability']
        draw_p = result['draw_probability']
        away_p = result['away_probability']
        reasoning = result['reasoning']
        key_factors = result['key_factors']
        analysis_data = result['analysis_data']
        home_xg = result['home_xg']
        away_xg = result['away_xg']

        # Criar análise já com dados finais (IA ou fallback)
        analysis = Analysis.objects.create(
            user=user,
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
            analysis_data=analysis_data,
        )
        
        # Incrementar contador
        user.increment_analysis_count()
        
        return Response({
            'message': 'Análise gerada com sucesso!',
            'analysis': AnalysisSerializer(analysis).data
        }, status=http_status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def my_stats(self, request):
        """Estatísticas das análises do usuário"""
        analyses = self.get_queryset()
        total = analyses.count()
        
        if total == 0:
            return Response({
                'total': 0,
                'correct': 0,
                'accuracy': 0,
                'by_confidence': {}
            })
        
        correct = analyses.filter(is_correct=True).count()
        
        # Estatísticas por nível de confiança
        by_confidence = {}
        for level in range(1, 6):
            level_analyses = analyses.filter(confidence=level)
            level_total = level_analyses.count()
            level_correct = level_analyses.filter(is_correct=True).count()
            
            by_confidence[level] = {
                'total': level_total,
                'correct': level_correct,
                'accuracy': round((level_correct / level_total * 100), 1) if level_total > 0 else 0
            }
        
        return Response({
            'total': total,
            'correct': correct,
            'accuracy': round((correct / total * 100), 1),
            'by_confidence': by_confidence
        })


class DailyBetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para Apostas Diárias (Bilhetes e Value Bets)
    
    Endpoints públicos para transparência:
    - GET /daily-bets/today/ - Apostas geradas para hoje
    - GET /daily-bets/history/ - Histórico com estatísticas
    - GET /daily-bets/{id}/ - Detalhes de uma aposta específica
    """
    
    queryset = DailyBet.objects.all().order_by('-date', '-expected_value')
    permission_classes = [AllowAny]  # Público para transparência!
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['bet_type', 'status', 'is_validated']
    
    def get_serializer_class(self):
        """Usar serializer simplificado para list, completo para retrieve"""
        if self.action == 'list':
            return DailyBetListSerializer
        return DailyBetSerializer
    
    @action(detail=False, methods=['get'], url_path='today')
    def today(self, request):
        """
        Retorna apostas geradas para hoje
        
        Response:
        {
            "date": "2026-01-30",
            "multiple_tickets": [...],  # Bilhetes 3x, 5x, 7x
            "value_bets": [...],         # Top 10 value bets
            "stats": {
                "total_matches": 45,
                "total_bets": 13,
                "avg_multiple_odd": 5.6,
                "avg_value_ev": 12.3
            }
        }
        """
        today = timezone.now().date()
        
        # Buscar apostas de hoje
        today_bets = DailyBet.objects.filter(date=today)
        
        # Separar por tipo
        multiple_tickets = today_bets.filter(bet_type='multiple').order_by('-combined_probability')
        value_bets = today_bets.filter(bet_type='value').order_by('-expected_value')
        
        # Estatísticas
        total_matches = self._count_unique_matches(today_bets)
        
        stats = {
            'total_matches': total_matches,
            'total_bets': today_bets.count(),
            'multiple_count': multiple_tickets.count(),
            'value_count': value_bets.count(),
        }
        
        # Calcular médias se houver apostas
        if multiple_tickets.exists():
            stats['avg_multiple_odd'] = round(
                multiple_tickets.aggregate(avg=Avg('total_odd'))['avg'] or 0, 2
            )
            stats['avg_multiple_prob'] = round(
                multiple_tickets.aggregate(avg=Avg('combined_probability'))['avg'] or 0, 4
            )
        
        if value_bets.exists():
            stats['avg_value_ev'] = round(
                value_bets.aggregate(avg=Avg('expected_value'))['avg'] or 0, 1
            )
            stats['avg_value_prob'] = round(
                value_bets.aggregate(avg=Avg('combined_probability'))['avg'] or 0, 4
            )
        
        return Response({
            'date': today.isoformat(),
            'multiple_tickets': DailyBetSerializer(multiple_tickets, many=True).data,
            'value_bets': DailyBetSerializer(value_bets, many=True).data,
            'stats': stats
        })
    
    @action(detail=False, methods=['get'], url_path='history')
    def history(self, request):
        """
        Retorna histórico dos últimos N dias com estatísticas públicas
        
        Query params:
        - days: Número de dias (padrão: 30, máx: 90)
        
        Response:
        {
            "period": "Últimos 30 dias",
            "overall": {
                "total_bets": 150,
                "won": 68,
                "lost": 72,
                "win_rate": 45.3,
                "roi": -5.2
            },
            "multiple_tickets": {...},
            "value_bets": {...},
            "recent_bets": [...]  # Top 50 mais recentes
        }
        """
        # Parâmetros
        days = min(int(request.query_params.get('days', 30)), 90)
        cutoff_date = timezone.now().date() - timedelta(days=days)
        
        # Buscar apostas validadas no período
        bets = DailyBet.objects.filter(
            date__gte=cutoff_date,
            is_validated=True
        ).order_by('-date', '-expected_value')
        
        # Estatísticas gerais
        overall_stats = self._calculate_stats(bets, 'overall')
        
        # Estatísticas por tipo
        multiple_stats = self._calculate_stats(
            bets.filter(bet_type='multiple'), 
            'multiple'
        )
        value_stats = self._calculate_stats(
            bets.filter(bet_type='value'), 
            'value'
        )
        
        # Apostas recentes (top 50)
        recent_bets = bets[:50]
        
        return Response({
            'period': f'Últimos {days} dias',
            'cutoff_date': cutoff_date.isoformat(),
            'overall': overall_stats,
            'multiple_tickets': multiple_stats,
            'value_bets': value_stats,
            'recent_bets': DailyBetListSerializer(recent_bets, many=True).data
        })
    
    @action(detail=False, methods=['get'], url_path='stats')
    def public_stats(self, request):
        """
        Estatísticas públicas agregadas (todos os tempos)
        
        Response:
        {
            "all_time": {
                "total_bets": 500,
                "win_rate": 47.2,
                "roi": 3.5,
                "avg_odd": 2.8
            },
            "last_7_days": {...},
            "last_30_days": {...},
            "by_bet_type": {...}
        }
        """
        now = timezone.now().date()
        
        # Todos os tempos (validados)
        all_bets = DailyBet.objects.filter(is_validated=True)
        
        # Períodos
        last_7_days = all_bets.filter(date__gte=now - timedelta(days=7))
        last_30_days = all_bets.filter(date__gte=now - timedelta(days=30))
        
        return Response({
            'all_time': self._calculate_stats(all_bets, 'all_time'),
            'last_7_days': self._calculate_stats(last_7_days, '7_days'),
            'last_30_days': self._calculate_stats(last_30_days, '30_days'),
            'by_bet_type': {
                'multiple_3x': self._calculate_stats(
                    all_bets.filter(bet_type='multiple').annotate(
                        num_selections=Count('selections')
                    ).filter(num_selections=3),
                    'multiple_3x'
                ),
                'multiple_5x': self._calculate_stats(
                    all_bets.filter(bet_type='multiple').annotate(
                        num_selections=Count('selections')
                    ).filter(num_selections=5),
                    'multiple_5x'
                ),
                'multiple_7x': self._calculate_stats(
                    all_bets.filter(bet_type='multiple').annotate(
                        num_selections=Count('selections')
                    ).filter(num_selections=7),
                    'multiple_7x'
                ),
                'value': self._calculate_stats(
                    all_bets.filter(bet_type='value'),
                    'value'
                )
            }
        })
    
    def _calculate_stats(self, queryset, label=''):
        """Calcula estatísticas de um conjunto de apostas"""
        total = queryset.count()
        
        if total == 0:
            return {
                'label': label,
                'total': 0,
                'won': 0,
                'lost': 0,
                'partial': 0,
                'cancelled': 0,
                'win_rate': 0,
                'roi': 0,
                'avg_odd': 0,
                'avg_stake': 0
            }
        
        won = queryset.filter(status='won').count()
        lost = queryset.filter(status='lost').count()
        partial = queryset.filter(status='partial').count()
        cancelled = queryset.filter(status='cancelled').count()
        
        # Calcular ROI
        total_staked = float(queryset.aggregate(sum=Sum('suggested_stake'))['sum'] or 0)
        total_return = 0.0
        
        for bet in queryset.filter(status='won'):
            total_return += float(bet.total_odd) * float(bet.suggested_stake)
        
        profit = total_return - total_staked
        roi = (profit / total_staked * 100) if total_staked > 0 else 0
        
        return {
            'label': label,
            'total': total,
            'won': won,
            'lost': lost,
            'partial': partial,
            'cancelled': cancelled,
            'win_rate': round((won / total * 100) if total > 0 else 0, 1),
            'roi': round(roi, 1),
            'avg_odd': round(float(queryset.aggregate(avg=Avg('total_odd'))['avg'] or 0), 2),
            'avg_stake': round(float(queryset.aggregate(avg=Avg('suggested_stake'))['avg'] or 0), 1),
            'avg_probability': round(float(queryset.aggregate(avg=Avg('combined_probability'))['avg'] or 0), 4),
            'avg_ev': round(float(queryset.aggregate(avg=Avg('expected_value'))['avg'] or 0), 1)
        }
    
    def _count_unique_matches(self, queryset):
        """Conta partidas únicas nas apostas"""
        unique_match_ids = set()
        
        for bet in queryset:
            for selection in bet.selections:
                unique_match_ids.add(selection.get('match_id'))
        
        return len(unique_match_ids)
    
    # ============================================================================
    # ADMIN ACTIONS
    # ============================================================================
    
    @action(detail=False, methods=['post'], url_path='admin/generate-now', permission_classes=[IsAdminUser])
    def admin_generate_now(self, request):
        """
        🔐 ADMIN ONLY: Executa geração de daily bets manualmente (SINCRONO)
        
        Body (opcional):
        {
            "date": "2026-02-15",  // Data específica (padrão: hoje)
            "mode": "hybrid"       // Modo: 'priority', 'all', 'hybrid' (padrão: hybrid)
        }
        
        Response:
        {
            "status": "success",
            "task_id": "abc-123-def",
            "message": "Daily Bets gerados com sucesso",
            "execution_id": 42,
            "results": {...}
        }
        """
        from apps.analysis.services.daily_bet_generator import DailyBetGenerator
        from apps.analysis.models import TaskExecution
        import uuid
        
        # Executar de forma síncrona (sem Celery)
        try:
            task_id = str(uuid.uuid4())
            
            # Extrair parâmetros do body
            mode = request.data.get('mode', 'hybrid')  # default: hybrid
            
            # Criar registro de execução
            execution = TaskExecution.objects.create(
                task_name='generate_daily_bets',
                task_id=task_id,
                triggered_by='admin_manual',
                triggered_by_user=request.user
            )
            
            # Executar geração com modo especificado
            generator = DailyBetGenerator()
            results = generator.generate_for_today(mode=mode, execution=execution)
            
            # Atualizar execução com TODOS os dados (incluindo analyzed_matches)
            result_data = {
                'results': results  # Incluir resultado completo do generator
            }
            
            execution.mark_finished(status='success', result_data=result_data)
            
            return Response({
                'status': 'success',
                'task_id': task_id,
                'execution_id': execution.id,
                'message': f'Daily Bets gerados! {results.get("multiple_count", 0)} multiplos, {results.get("value_count", 0)} value bets',
                'results': result_data
            }, status=http_status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            
            # Tentar marcar execução como falha se existir
            if 'execution' in locals():
                execution.mark_finished(status='failed', result_data={'error': str(e)})
            
            return Response({
                'status': 'error',
                'message': f'Erro ao gerar daily bets: {str(e)}',
                'detail': error_detail
            }, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'], url_path='admin/validate-now', permission_classes=[IsAdminUser])
    def admin_validate_now(self, request):
        """
        🔐 ADMIN ONLY: Executa validação de apostas manualmente (SINCRONO)
        
        Response:
        {
            "status": "success",
            "task_id": "abc-123-def",
            "message": "Validação concluída",
            "results": {...}
        }
        """
        from apps.analysis.models import TaskExecution, DailyBet
        import uuid
        from apps.analysis.services.api_football_service import APIFootballService
        from django.utils import timezone
        from datetime import timedelta
        import uuid
        
        # Executar diretamente (síncrono) - não requer Celery/Redis
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Criar ID único para esta execução
            task_id = str(uuid.uuid4())
            
            # Criar registro de execução
            execution = TaskExecution.objects.create(
                task_name='validate_daily_bets',
                task_id=task_id,
                triggered_by='admin_manual',
                triggered_by_user=request.user
            )
            
            # Buscar apostas pendentes dos últimos 3 dias
            three_days_ago = timezone.now().date() - timedelta(days=3)
            pending_bets = DailyBet.objects.filter(
                date__gte=three_days_ago,
                status='pending',
                is_validated=False
            )
            
            logger.info(f"🔍 Validação: {pending_bets.count()} apostas pendentes dos últimos 3 dias")
            
            validated_count = 0
            finished_matches = 0
            ongoing_matches = 0
            api = APIFootballService()
            
            for bet in pending_bets:
                try:
                    # Verificar cada seleção da aposta
                    all_finished = True
                    selection_results = []
                    
                    for selection in bet.selections:
                        match_id = selection.get('match_id')
                        if not match_id:
                            all_finished = False
                            continue
                        
                        # Buscar resultado do jogo
                        try:
                            fixture_details = api.fetch_fixture_details(match_id)
                            if not fixture_details:
                                all_finished = False
                                logger.warning(f"⚠️  Fixture {match_id} não encontrado")
                                continue
                            
                            match_status = fixture_details.get('status')
                            
                            logger.info(f"📊 Match {match_id}: status={match_status}")
                            
                            # Verificar se o jogo finalizou
                            if match_status == 'FT':
                                finished_matches += 1
                                # TODO: Implementar lógica de verificação de resultado
                                # Por enquanto, marca como 'pending' para implementação futura
                                selection['result'] = 'pending'
                                selection['final_score'] = fixture_details.get('goals', {})
                                selection_results.append('pending')
                            else:
                                ongoing_matches += 1
                                all_finished = False
                                continue
                            
                        except Exception as e:
                            logger.error(f"❌ Erro ao buscar fixture {match_id}: {e}")
                            all_finished = False
                            continue
                    
                    # Se todos os jogos finalizaram, marcar como validado
                    if all_finished and len(selection_results) > 0:
                        bet.selections = bet.selections  # Salvar resultados nas seleções
                        bet.is_validated = True
                        bet.validated_at = timezone.now()
                        bet.status = 'pending'  # Aguardando implementação de lógica de resultado
                        bet.save()
                        validated_count += 1
                        logger.info(f"✅ Aposta {bet.id} validada")
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao validar aposta {bet.id}: {e}")
                    continue
            
            logger.info(f"📊 Validação concluída: {validated_count} validadas, {finished_matches} jogos finalizados, {ongoing_matches} jogos pendentes")
            
            # Atualizar registro de execução
            result_data = {
                'status': 'success',
                'validated_count': validated_count,
                'pending_count': pending_bets.count() - validated_count,
                'finished_matches': finished_matches,
                'ongoing_matches': ongoing_matches,
                'total_bets_checked': pending_bets.count()
            }
            execution.mark_finished(status='success', result_data=result_data)
            
            return Response({
                'status': 'success',
                'task_id': task_id,
                'execution_id': execution.id,
                'message': f'✅ {validated_count} apostas validadas ({finished_matches} jogos finalizados, {ongoing_matches} pendentes)',
                'results': result_data
            }, status=http_status.HTTP_200_OK)
            
        except Exception as e:
            # Se houver erro, marcar execução como falha
            if 'execution' in locals():
                execution.mark_finished(status='failed', error_message=str(e))
            
            import traceback
            error_detail = traceback.format_exc()
            
            return Response({
                'status': 'error',
                'message': f'Erro ao validar apostas: {str(e)}',
                'detail': error_detail
            }, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='admin/execution-status', permission_classes=[IsAdminUser])
    def admin_execution_status(self, request):
        """
        🔐 ADMIN ONLY: Retorna status das últimas execuções das tasks
        
        Query params:
        - limit: Número de execuções (padrão: 20, máx: 100)
        
        Response:
        {
            "executions": [
                {
                    "id": 42,
                    "task_name": "generate_daily_bets",
                    "status": "success",
                    "started_at": "2026-02-15T06:00:00Z",
                    "finished_at": "2026-02-15T06:05:30Z",
                    "duration_seconds": 330,
                    "triggered_by": "celery",
                    "result_summary": {...}
                }
            ],
            "summary": {
                "last_generation": "2026-02-15T06:00:00Z",
                "last_validation": "2026-02-15T07:00:00Z",
                "pending_count": 5,
                "celery_status": "running"
            }
        }
        """
        from apps.analysis.models import TaskExecution
        from celery import current_app
        
        limit = min(int(request.query_params.get('limit', 20)), 100)
        
        # Buscar últimas execuções
        executions = TaskExecution.objects.all().order_by('-started_at')[:limit]
        
        # Serializar execuções
        executions_data = []
        for execution in executions:
            data = {
                'id': execution.id,
                'task_name': execution.task_name,
                'task_id': execution.task_id,
                'status': execution.status,
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'finished_at': execution.finished_at.isoformat() if execution.finished_at else None,
                'duration_seconds': execution.duration_seconds,
                'triggered_by': execution.triggered_by,
                'triggered_by_user': execution.triggered_by_user.username if execution.triggered_by_user else None,
                'error_message': execution.error_message,
            }
            
            # Adicionar resumo do resultado se disponível
            if execution.result_data and execution.status == 'success':
                results = execution.result_data.get('results', {})
                data['result_summary'] = {
                    'matches_analyzed': results.get('matches_analyzed', 0),
                    'multiple_count': results.get('multiple_count', 0),
                    'value_count': results.get('value_count', 0),
                }
            
            executions_data.append(data)
        
        # Summary
        last_generation = TaskExecution.objects.filter(
            task_name='generate_daily_bets',
            status='success'
        ).order_by('-finished_at').first()
        
        last_validation = TaskExecution.objects.filter(
            task_name='validate_daily_bets',
            status='success'
        ).order_by('-finished_at').first()
        
        pending_bets = DailyBet.objects.filter(
            status='pending',
            is_validated=False
        ).count()
        
        # Verificar status do Celery
        try:
            inspect = current_app.control.inspect()
            active_tasks = inspect.active()
            celery_status = 'running' if active_tasks else 'idle'
        except Exception:
            celery_status = 'unknown'
        
        return Response({
            'executions': executions_data,
            'summary': {
                'last_generation': last_generation.finished_at.isoformat() if last_generation else None,
                'last_validation': last_validation.finished_at.isoformat() if last_validation else None,
                'pending_bets_count': pending_bets,
                'celery_status': celery_status,
                'total_executions': TaskExecution.objects.count(),
            }
        })
    
    @action(detail=False, methods=['get'], url_path='admin/generation-progress', permission_classes=[IsAdminUser])
    def admin_generation_progress(self, request):
        """
        🔐 ADMIN ONLY: Retorna progresso em tempo real da geração de bilhetes
        
        Verifica se há geração ativa e retorna seu progresso atual.
        
        Response:
        {
            "is_running": true,
            "execution_id": 42,
            "task_id": "abc-123",
            "current_stage": "analyzing",
            "progress": {
                "matches_found": 60,
                "matches_processed": 35,
                "bets_created": 8,
                "percentage": 58
            },
            "timing": {
                "started_at": "2026-02-17T14:00:00Z",
                "last_updated": "2026-02-17T14:03:15Z",
                "elapsed_seconds": 195
            },
            "progress_log": [...]
        }
        """
        from apps.analysis.models import TaskExecution
        
        # Buscar geração ativa
        active_execution = TaskExecution.objects.filter(
            task_name='generate_daily_bets',
            status='running'
        ).order_by('-started_at').first()
        
        if not active_execution:
            # Verificar última execução concluída
            last_execution = TaskExecution.objects.filter(
                task_name='generate_daily_bets'
            ).order_by('-started_at').first()
            
            if last_execution and last_execution.status == 'success':
                return Response({
                    'is_running': False,
                    'last_execution': {
                        'execution_id': last_execution.id,
                        'status': last_execution.status,
                        'finished_at': last_execution.finished_at.isoformat() if last_execution.finished_at else None,
                        'result_summary': last_execution.result_data
                    }
                })
            
            return Response({
                'is_running': False,
                'message': 'Nenhuma geração ativa'
            })
        
        # Retornar progresso da execução ativa
        return Response({
            'is_running': True,
            'execution_id': active_execution.id,
            'task_id': active_execution.task_id,
            'current_stage': active_execution.current_stage or 'starting',
            'progress': {
                'matches_found': active_execution.matches_found,
                'matches_processed': active_execution.matches_processed,
                'bets_created': active_execution.bets_created,
                'percentage': active_execution.get_progress_percentage()
            },
            'timing': {
                'started_at': active_execution.started_at.isoformat(),
                'last_updated': active_execution.last_updated.isoformat() if active_execution.last_updated else None,
                'elapsed_seconds': active_execution.get_elapsed_time()
            },
            'progress_log': active_execution.progress_log if isinstance(active_execution.progress_log, list) else []
        })
    
    @action(detail=False, methods=['get'], url_path='admin/execution-detail/(?P<execution_id>[^/.]+)', permission_classes=[IsAdminUser])
    def admin_execution_detail(self, request, execution_id=None):
        """
        🔐 ADMIN ONLY: Retorna detalhes completos de uma execução específica
        
        Inclui:
        - Dados básicos da execução
        - Métricas completas
        - Partidas analisadas agrupadas por liga
        - Progress log completo
        
        Response:
        {
            "id": 42,
            "task_name": "generate_daily_bets",
            "status": "success",
            "started_at": "2026-02-15T06:00:00Z",
            "finished_at": "2026-02-15T06:05:30Z",
            "duration_seconds": 330,
            "triggered_by": "celery",
            "triggered_by_user": "admin",
            "error_message": null,
            "current_stage": "completed",
            "progress_log": [...],
            "result_summary": {
                "matches_analyzed": 100,
                "multiple_count": 1,
                "value_count": 10,
                "api_calls": 200,
                "cache_hits": 150,
                "search_mode": "hybrid",
                "total_fixtures_found": 120,
                "scheduled_fixtures": 100,
                "analyzed_matches": [
                    {
                        "fixture_id": 1234,
                        "home_team": "Team A",
                        "away_team": "Team B",
                        "league_name": "Premier League",
                        "date": "2026-02-15T20:00:00Z",
                        "selected_market": "X2",
                        "odd": 1.11
                    }
                ]
            }
        }
        """
        from apps.analysis.models import TaskExecution
        import traceback
        
        try:
            try:
                execution = TaskExecution.objects.get(id=execution_id)
            except TaskExecution.DoesNotExist:
                return Response(
                    {'error': 'Execução não encontrada'},
                    status=404
                )
            
            # Log para debug
            logger.info(f"📋 Detalhes da execução #{execution_id}")
            logger.info(f"   Status: {execution.status}")
            logger.info(f"   result_data keys: {list(execution.result_data.keys()) if execution.result_data else 'None'}")
            if execution.result_data:
                results = execution.result_data.get('results', {})
                logger.info(f"   results keys: {list(results.keys()) if results else 'None'}")
                logger.info(f"   analyzed_matches count: {len(results.get('analyzed_matches', []))}")
        except Exception as e:
            logger.error(f"❌ Erro ao buscar execução: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {'error': f'Erro ao buscar execução: {str(e)}', 'traceback': traceback.format_exc()},
                status=500
            )
        
        try:
            # Serializar dados básicos
            data = {
                'id': execution.id,
                'task_name': execution.task_name,
                'task_id': execution.task_id,
                'status': execution.status,
                'started_at': execution.started_at.isoformat() if execution.started_at else None,
                'finished_at': execution.finished_at.isoformat() if execution.finished_at else None,
                'duration_seconds': execution.duration_seconds,
                'triggered_by': execution.triggered_by,
                'triggered_by_user': execution.triggered_by_user.username if execution.triggered_by_user else None,
                'error_message': execution.error_message,
                'current_stage': execution.current_stage,
                'matches_found': execution.matches_found,
                'matches_processed': execution.matches_processed,
                'bets_created': execution.bets_created,
                'last_updated': execution.last_updated.isoformat() if execution.last_updated else None,
                'progress_log': execution.progress_log if isinstance(execution.progress_log, list) else []
            }
            
            # Adicionar result_summary expandido
            if execution.result_data and execution.status == 'success':
                results = execution.result_data.get('results', {})
                
                # Buscar apostas para adicionar detalhes de mercado selecionado
                from django.utils import timezone
                from datetime import timedelta
                
                time_window_start = execution.started_at - timedelta(minutes=5)
                time_window_end = (execution.finished_at or timezone.now()) + timedelta(minutes=5)
                
                recent_bets = DailyBet.objects.filter(
                    created_at__gte=time_window_start,
                    created_at__lte=time_window_end
                )
                
                # Criar mapa de fixture_id para detalhes de aposta
                bet_details = {}
                for bet in recent_bets:
                    selections = bet.selections or []
                    for selection in selections:
                        fixture_id = selection.get('fixture_id')
                        if fixture_id:
                            bet_details[fixture_id] = {
                                'selected_market': selection.get('pick'),
                                'odd': selection.get('odd')
                            }
                
                # Pegar lista de partidas analisadas do resultado
                analyzed_matches_raw = results.get('analyzed_matches', [])
                
                # Enriquecer com detalhes de apostas
                analyzed_matches = []
                for match in analyzed_matches_raw:
                    fixture_id = match.get('fixture_id')
                    enriched_match = {
                        'fixture_id': fixture_id,
                        'home_team': match.get('home_team'),
                        'away_team': match.get('away_team'),
                        'league_name': match.get('league_name'),
                        'date': match.get('match_date')
                    }
                    
                    # Adicionar detalhes de aposta se disponível
                    if fixture_id in bet_details:
                        enriched_match.update(bet_details[fixture_id])
                    
                    analyzed_matches.append(enriched_match)
                
                data['result_summary'] = {
                    'matches_analyzed': results.get('matches_analyzed', 0),
                    'multiple_count': results.get('multiple_count', 0),
                    'value_count': results.get('value_count', 0),
                    'total_bets': results.get('total_bets', 0),
                    'api_calls': results.get('api_calls', 0),
                    'cache_hits': results.get('cache_hits', 0),
                    'search_mode': results.get('search_mode', 'N/A'),
                    'total_fixtures_found': results.get('total_fixtures_found', 0),
                    'scheduled_fixtures': results.get('scheduled_fixtures', 0),
                    'analyzed_matches': analyzed_matches,
                    'quality_stats': results.get('quality_stats')  # ✅ FASE 2: Estatísticas de qualidade
                }
            else:
                data['result_summary'] = None
            
            return Response(data)
        except Exception as e:
            logger.error(f"❌ Erro ao processar dados da execução: {str(e)}")
            logger.error(traceback.format_exc())
            return Response(
                {'error': f'Erro ao processar dados: {str(e)}', 'traceback': traceback.format_exc()},
                status=500
            )
    
    @action(detail=False, methods=['get'], url_path='admin/generator-stats', permission_classes=[IsAdminUser])
    def admin_generator_stats(self, request):
        """
        🔐 ADMIN ONLY: Estatísticas do gerador de daily bets
        
        Response:
        {
            "today": {
                "generated": true,
                "multiple_count": 3,
                "value_count": 10,
                "matches_analyzed": 45
            },
            "last_7_days": {
                "days_generated": 7,
                "avg_multiple_per_day": 3,
                "avg_value_per_day": 10,
                "total_matches_analyzed": 315
            },
            "performance": {
                "win_rate_multiple": 42.5,
                "win_rate_value": 51.2,
                "roi_multiple": -8.3,
                "roi_value": 5.7
            }
        }
        """
        today = timezone.now().date()
        
        # Hoje
        today_bets = DailyBet.objects.filter(date=today)
        today_stats = {
            'generated': today_bets.exists(),
            'multiple_count': today_bets.filter(bet_type='multiple').count(),
            'value_count': today_bets.filter(bet_type='value').count(),
            'matches_analyzed': self._count_unique_matches(today_bets),
            'generated_at': today_bets.first().created_at.isoformat() if today_bets.exists() else None
        }
        
        # Últimos 7 dias
        last_7_days = today - timedelta(days=7)
        recent_bets = DailyBet.objects.filter(date__gte=last_7_days)
        
        days_with_bets = recent_bets.values('date').distinct().count()
        
        last_7_stats = {
            'days_generated': days_with_bets,
            'avg_multiple_per_day': round(
                recent_bets.filter(bet_type='multiple').count() / max(days_with_bets, 1), 1
            ),
            'avg_value_per_day': round(
                recent_bets.filter(bet_type='value').count() / max(days_with_bets, 1), 1
            ),
            'total_matches_analyzed': self._count_unique_matches(recent_bets),
        }
        
        # Performance (últimos 30 dias validados)
        last_30_days = today - timedelta(days=30)
        validated_bets = DailyBet.objects.filter(
            date__gte=last_30_days,
            is_validated=True
        )
        
        performance = {
            'win_rate_multiple': self._calculate_stats(
                validated_bets.filter(bet_type='multiple'), 'multiple'
            )['win_rate'],
            'win_rate_value': self._calculate_stats(
                validated_bets.filter(bet_type='value'), 'value'
            )['win_rate'],
            'roi_multiple': self._calculate_stats(
                validated_bets.filter(bet_type='multiple'), 'multiple'
            )['roi'],
            'roi_value': self._calculate_stats(
                validated_bets.filter(bet_type='value'), 'value'
            )['roi'],
        }
        
        return Response({
            'today': today_stats,
            'last_7_days': last_7_stats,
            'performance': performance
        })
