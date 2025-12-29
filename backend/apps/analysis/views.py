from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Analysis
from .serializers import AnalysisSerializer, AnalysisRequestSerializer
from apps.matches.models import Match


class AnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Análises"""
    serializer_class = AnalysisSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['prediction', 'confidence']
    
    def get_queryset(self):
        """Retorna apenas análises do usuário"""
        return Analysis.objects.filter(user=self.request.user).select_related(
            'match', 'match__league', 'match__home_team', 'match__away_team'
        ).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def request_analysis(self, request):
        """Solicita análise de uma partida"""
        # Validar dados
        serializer = AnalysisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        match_id = serializer.validated_data['match_id']
        user = request.user
        
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
        
        if existing:
            return Response({
                'message': 'Você já analisou esta partida',
                'analysis': AnalysisSerializer(existing).data
            }, status=status.HTTP_200_OK)
        
        # Usar AI Analyzer para gerar análise
        from apps.analysis.services.ai_analyzer import AIAnalyzer
        
        analyzer = AIAnalyzer()
        match_data = {
            'home_team': {
                'name': match.home_team.name,
                'stats': match.stats_cache or {}
            },
            'away_team': {
                'name': match.away_team.name,
                'stats': match.stats_cache or {}
            },
            'h2h': [],
            'league': match.league.name,
            'date': match.match_date.strftime('%Y-%m-%d')
        }
        
        ai_result = analyzer.analyze_match(match_data)
        
        # Criar análise com resultado da IA
        analysis = Analysis.objects.create(
            user=user,
            match=match,
            prediction=ai_result['prediction'],
            confidence=ai_result['confidence'],
            home_probability=ai_result['home_probability'],
            draw_probability=ai_result['draw_probability'],
            away_probability=ai_result['away_probability'],
            home_xg=ai_result.get('home_xg', 1.5),
            away_xg=ai_result.get('away_xg', 1.5),
            reasoning=ai_result['reasoning'],
            key_factors=ai_result['key_factors'],
            analysis_data=ai_result.get('analysis_breakdown', {})
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
