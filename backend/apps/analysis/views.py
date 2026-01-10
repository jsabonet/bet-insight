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
