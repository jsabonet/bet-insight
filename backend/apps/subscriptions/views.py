from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Subscription, Payment
from .serializers import SubscriptionSerializer, PaymentSerializer, PaymentCreateSerializer
import uuid


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
    
    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """Iniciar pagamento M-Pesa"""
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plan = serializer.validated_data['plan']
        phone_number = serializer.validated_data['phone_number']
        
        # Definir valores
        amounts = {
            'monthly': 499.00,
            'quarterly': 1299.00,
            'yearly': 4499.00
        }
        
        amount = amounts[plan]
        
        # Criar assinatura
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status='pending',
            amount_paid=amount
        )
        
        # Criar pagamento
        transaction_id = f"BET{uuid.uuid4().hex[:12].upper()}"
        
        payment = Payment.objects.create(
            user=request.user,
            subscription=subscription,
            amount=amount,
            phone_number=phone_number,
            transaction_id=transaction_id,
            status='pending'
        )
        
        # TODO: Integrar com M-Pesa API (Fase 6)
        # Por enquanto, simular sucesso
        
        return Response({
            'message': 'Pagamento iniciado. Verifique seu telefone para confirmar.',
            'payment': PaymentSerializer(payment).data,
            'instructions': 'Digite seu PIN M-Pesa quando solicitado'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Confirmar pagamento (webhook M-Pesa)"""
        payment = self.get_object()
        
        if payment.status == 'completed':
            return Response({
                'message': 'Pagamento já foi confirmado'
            })
        
        # TODO: Validar callback M-Pesa (Fase 6)
        
        payment.complete_payment()
        
        return Response({
            'message': 'Pagamento confirmado!',
            'payment': PaymentSerializer(payment).data
        })
