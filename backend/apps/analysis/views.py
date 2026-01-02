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

        # Fallback seguro quando IA não disponível: gerar análise básica
        if not ai_result or not isinstance(ai_result, dict) or ai_result.get('success') is False:
            # Probabilidades simples e estáveis
            home_p, draw_p, away_p = 40.0, 30.0, 30.0
            prediction = 'home'
            confidence = 3
            reasoning = (
                'Análise padrão aplicada devido à indisponibilidade temporária do serviço de IA. '
                'Distribuição neutra de probabilidades baseada em fatores gerais de mando de campo.'
            )
            key_factors = ['Mando de campo', 'Equilíbrio de forças presumido']
            analysis_data = {'fallback': True, 'source': 'heuristic'}
            home_xg, away_xg = 1.5, 1.3
        else:
            # Adaptar se o serviço retornar apenas texto + confiança
            # Esperados: prediction, confidence, probabilities, reasoning, key_factors
            prediction = ai_result.get('prediction', 'home')
            confidence = int(ai_result.get('confidence', 3) or 3)
            home_p = float(ai_result.get('home_probability', 40.0) or 40.0)
            draw_p = float(ai_result.get('draw_probability', 30.0) or 30.0)
            away_p = float(ai_result.get('away_probability', 30.0) or 30.0)
            reasoning = ai_result.get('reasoning') or ai_result.get('analysis') or 'Resumo gerado pela IA.'
            key_factors = ai_result.get('key_factors') or []
            analysis_data = ai_result.get('analysis_breakdown') or {'raw_text': ai_result.get('analysis')}
            home_xg = float(ai_result.get('home_xg', 1.5) or 1.5)
            away_xg = float(ai_result.get('away_xg', 1.3) or 1.3)

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
