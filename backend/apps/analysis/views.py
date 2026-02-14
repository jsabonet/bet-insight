from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Count, Q, Avg, Sum
from datetime import timedelta

from .models import Analysis, DailyBet
from .serializers import (
    AnalysisSerializer, 
    AnalysisRequestSerializer,
    DailyBetSerializer,
    DailyBetListSerializer
)
from apps.matches.models import Match


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
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar se já existe análise
        match = Match.objects.get(id=match_id)
        existing = Analysis.objects.filter(user=user, match=match).first()
        
        if existing and not force_recalculate:
            return Response({
                'message': 'Você já analisou esta partida',
                'analysis': AnalysisSerializer(existing).data
            }, status=status.HTTP_200_OK)
        
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
        }, status=status.HTTP_201_CREATED)
    
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

