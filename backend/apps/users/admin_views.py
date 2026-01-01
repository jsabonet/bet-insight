from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import User
from .serializers import UserSerializer
from apps.analysis.models import Analysis
from apps.matches.models import Match


class AdminUserViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de usuários por admin"""
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-created_at')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros
        user_type = self.request.query_params.get('type', None)
        search = self.request.query_params.get('search', None)
        
        if user_type == 'premium':
            queryset = queryset.filter(is_premium=True)
        elif user_type == 'free':
            queryset = queryset.filter(is_premium=False)
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def toggle_premium(self, request, pk=None):
        """Ativar/desativar premium do usuário"""
        user = self.get_object()
        
        if user.is_premium:
            # Remover premium
            user.is_premium = False
            user.premium_until = None
        else:
            # Adicionar premium por 30 dias
            user.is_premium = True
            user.premium_until = timezone.now() + timedelta(days=30)
        
        user.save()
        
        return Response({
            'message': f'Premium {"ativado" if user.is_premium else "desativado"} com sucesso',
            'user': UserSerializer(user).data
        })
    
    @action(detail=True, methods=['post'])
    def reset_daily_limit(self, request, pk=None):
        """Resetar limite diário do usuário"""
        user = self.get_object()
        user.daily_analysis_count = 0
        user.save()
        
        return Response({
            'message': 'Limite diário resetado com sucesso',
            'user': UserSerializer(user).data
        })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_stats(request):
    """Estatísticas gerais do sistema"""
    
    # Usuários
    total_users = User.objects.count()
    premium_users = User.objects.filter(is_premium=True).count()
    new_users_today = User.objects.filter(
        created_at__date=timezone.now().date()
    ).count()
    
    # Análises
    total_analyses = Analysis.objects.count()
    today = timezone.now().date()
    analyses_today = Analysis.objects.filter(created_at__date=today).count()
    analyses_this_week = Analysis.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Partidas
    active_matches = Match.objects.filter(
        status__in=['SCHEDULED', 'LIVE', '1H', '2H', 'HT']
    ).count()
    
    # Receita estimada (500 MT por premium)
    revenue = premium_users * 500
    
    # Top usuários por análises
    top_users = User.objects.annotate(
        analysis_count=Count('analyses')
    ).order_by('-analysis_count')[:5]
    
    # Análises por dia (últimos 7 dias)
    analyses_by_day = []
    for i in range(7):
        day = today - timedelta(days=i)
        count = Analysis.objects.filter(created_at__date=day).count()
        analyses_by_day.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    return Response({
        'users': {
            'total': total_users,
            'premium': premium_users,
            'free': total_users - premium_users,
            'new_today': new_users_today,
        },
        'analyses': {
            'total': total_analyses,
            'today': analyses_today,
            'this_week': analyses_this_week,
            'by_day': analyses_by_day,
        },
        'matches': {
            'active': active_matches,
        },
        'revenue': {
            'monthly_estimate': revenue,
            'per_premium': 500,
        },
        'top_users': [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'analysis_count': u.analysis_count,
                'is_premium': u.is_premium,
            }
            for u in top_users
        ]
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_analyses_stats(request):
    """Estatísticas de análises"""
    
    # Total de análises por status
    total = Analysis.objects.count()
    
    # Análises por confiança
    by_confidence = Analysis.objects.values('confidence').annotate(
        count=Count('id')
    ).order_by('-confidence')
    
    # Análises por predição
    by_prediction = Analysis.objects.values('prediction').annotate(
        count=Count('id')
    )
    
    # Média de confiança
    from django.db.models import Avg
    avg_confidence = Analysis.objects.aggregate(Avg('confidence'))['confidence__avg'] or 0
    
    return Response({
        'total': total,
        'average_confidence': round(avg_confidence, 2),
        'by_confidence': list(by_confidence),
        'by_prediction': list(by_prediction),
    })


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_delete_user(request, user_id):
    """Deletar usuário (apenas admin)"""
    try:
        user = User.objects.get(id=user_id)
        
        # Não permitir deletar superusuários
        if user.is_superuser:
            return Response(
                {'message': 'Não é possível deletar superusuários'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        username = user.username
        user.delete()
        
        return Response({
            'message': f'Usuário {username} deletado com sucesso'
        })
    except User.DoesNotExist:
        return Response(
            {'message': 'Usuário não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
