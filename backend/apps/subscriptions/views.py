from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Subscription, Payment
from .serializers import SubscriptionSerializer, PaymentSerializer


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Assinaturas"""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Assinatura atual ativa"""
        subscription = Subscription.objects.filter(
            user=request.user,
            status='active'
        ).first()
        
        if subscription:
            return Response(SubscriptionSerializer(subscription).data)
        
        return Response({
            'message': 'Nenhuma assinatura ativa',
            'is_premium': False
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancelar assinatura"""
        subscription = self.get_object()
        
        if subscription.user != request.user:
            return Response({
                'error': 'Não autorizado'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if subscription.status != 'active':
            return Response({
                'error': 'Assinatura não está ativa'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        subscription.cancel()
        
        return Response({
            'message': 'Assinatura cancelada com sucesso',
            'subscription': SubscriptionSerializer(subscription).data
        })


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para Pagamentos"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).order_by('-created_at')
