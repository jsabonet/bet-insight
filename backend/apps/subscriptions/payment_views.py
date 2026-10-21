"""Views for reconciling VPay payments."""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging

from .models import Payment
from .vpay_service import vpay_service
from .payment_helpers import apply_vpay_status
from .serializers import SubscriptionSerializer, PaymentSerializer

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_payment_status(request, transaction_id):
    """
    Verifica o estado de um pedido VPay por polling.

    Os pagamentos de gateways antigos permanecem visíveis para preservar o
    histórico, mas não são consultados nem alterados por esta integração.
    """
    try:
        payment = Payment.objects.get(
            transaction_id=transaction_id,
            user=request.user
        )
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Pagamento não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Se já está num estado terminal, retornar imediatamente
    if payment.status in ('completed', 'failed', 'cancelled', 'expired'):
        return Response({
            'status': payment.status,
            'payment': PaymentSerializer(payment).data,
            'subscription': SubscriptionSerializer(payment.subscription).data if payment.subscription else None
        })

    if payment.gateway != 'vpay':
        return Response({
            'status': payment.status,
            'payment': PaymentSerializer(payment).data,
            'subscription': SubscriptionSerializer(payment.subscription).data if payment.subscription else None,
            'provider_status': None,
            'polling_enabled': False,
            'message': 'Este pagamento pertence a um gateway desativado e não pode ser reconciliado pelo VPay.',
        })

    provider_status = None
    order_id = payment.vpay_order_id or (payment.metadata or {}).get('vpay_order_id')
    if order_id:
        vpay_response = vpay_service.get_order_status(order_id)
        if vpay_response.get('success'):
            provider_status = vpay_response.get('status')
            logger.info("Status VPay para %s: %s", order_id, provider_status)
            apply_vpay_status(payment, provider_status, activate=True)
    else:
        logger.warning("Pagamento VPay %s sem order_id para consultar.", transaction_id)

    return Response({
        'status': payment.status,
        'payment': PaymentSerializer(payment).data,
        'subscription': SubscriptionSerializer(payment.subscription).data if payment.subscription else None,
        'provider_status': provider_status,
        'polling_enabled': True
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_payments(request):
    """
    Lista pagamentos do usuário
    """
    payments = request.user.payments.all().order_by('-created_at')
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data)
