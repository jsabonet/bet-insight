"""
Views para processar pagamentos via VPay Moçambique (checkout hospedado).

Fluxo:
  1. POST /subscriptions/payments/vpay/create/  -> cria pedido na VPay e devolve
     o URL de checkout hospedado.
  2. O cliente é redirecionado para https://checkout.vpay.co.mz/{orderId}.
  3. A confirmação ocorre via GET /v1/orders/{order_id}/status (polling no
     endpoint de check já existente) e/ou via webhook verificado (HMAC-SHA256).
"""
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

import uuid

from .models import Payment
from .vpay_service import vpay_service, VPayServiceError
from .plan_config import get_plan
from .serializers import PaymentSerializer
from .payment_helpers import VPAY_STATUS_MAP, apply_vpay_status

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_vpay_payment(request):
    """
    Cria um pedido VPay e devolve o URL de checkout hospedado.

    Body:
    {
        "plan_slug": "starter|pro|vip|teste"
    }
    """
    if not getattr(settings, 'VPAY_ENABLED', True):
        return Response(
            {'error': 'Gateway VPay desativado.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    user = request.user
    plan_slug = request.data.get('plan_slug')

    valid_plans = ['teste', 'starter', 'pro', 'vip']
    if not plan_slug or plan_slug not in valid_plans:
        return Response(
            {'error': f'Plano inválido. Use: {", ".join(valid_plans)}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    plan = get_plan(plan_slug)
    if not plan:
        return Response(
            {'error': 'Plano não encontrado'},
            status=status.HTTP_404_NOT_FOUND,
        )

    amount = Decimal(str(plan['price']))
    if amount <= 0:
        return Response(
            {'error': 'Valor do plano inválido.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Não permitir nova assinatura se já existe uma ativa.
    existing_subscription = user.subscriptions.filter(
        status='active',
        end_date__gt=timezone.now(),
    ).first()
    if existing_subscription:
        return Response(
            {
                'error': 'Você já possui uma assinatura ativa',
                'subscription': existing_subscription.id,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    ambiguous_payment = Payment.objects.filter(
        user=user,
        gateway='vpay',
        status='pending',
        metadata__plan=plan_slug,
        metadata__ambiguous=True,
    ).order_by('-created_at').first()
    if ambiguous_payment:
        return Response(
            {
                'error': (
                    'Existe um pedido VPay cujo resultado ainda não foi confirmado. '
                    'Contacte o suporte antes de tentar novamente.'
                ),
                'transaction_id': ambiguous_payment.transaction_id,
            },
            status=status.HTTP_409_CONFLICT,
        )

    # Idempotência: reaproveitar pedido pendente do mesmo usuário + plano,
    # consultando o estado antes de criar um novo pedido.
    pending_payment = (
        Payment.objects.filter(
            user=user,
            gateway='vpay',
            status='pending',
            metadata__plan=plan_slug,
        )
        .exclude(vpay_order_id='')
        .order_by('-created_at')
        .first()
    )
    if pending_payment:
        status_result = vpay_service.get_order_status(pending_payment.vpay_order_id)
        if status_result.get('success'):
            vpay_status = status_result.get('status')
            if vpay_status == 'paid':
                apply_vpay_status(pending_payment, vpay_status, activate=True)
                return Response({
                    'success': True,
                    'message': 'Pagamento já confirmado.',
                    'payment': PaymentSerializer(pending_payment).data,
                })
            if vpay_status in ('pending', None):
                checkout_url = (pending_payment.metadata or {}).get('checkout_url')
                if not checkout_url:
                    checkout_url = f"{vpay_service.checkout_base_url}/{pending_payment.vpay_order_id}"
                return Response({
                    'success': True,
                    'message': 'Pedido pendente reutilizado.',
                    'payment': PaymentSerializer(pending_payment).data,
                    'checkout_url': checkout_url,
                })
            # failed/cancelled/expired -> marcar localmente e criar novo pedido.
            apply_vpay_status(pending_payment, vpay_status)

    customer = {
        'merchantCustomerId': f'user-{user.id}',
        'name': user.get_full_name() or user.username,
        'email': user.email or '',
    }
    user_phone = getattr(user, 'phone', '') or ''
    if user_phone:
        customer['phone'] = user_phone

    items = [{
        'originProductId': f'plan-{plan_slug}',
        'name': plan['name'],
        'quantity': 1,
        'price': float(amount),
    }]

    try:
        with transaction.atomic():
            reference = f"BET{user.id}{uuid.uuid4().hex[:8].upper()}"
            payment = Payment.objects.create(
                user=user,
                subscription=None,
                amount=amount,
                currency='MZN',
                phone_number=user_phone,
                transaction_id=reference,
                gateway='vpay',
                payment_method='vpay',
                status='pending',
                metadata={
                    'plan': plan_slug,
                    'plan_name': plan['name'],
                    'gateway': 'vpay',
                },
            )

            order_result = vpay_service.create_order(
                customer=customer,
                items=items,
                merchant_order_reference=reference,
                currency='MZN',
            )

            if not order_result.get('success'):
                # Não repetir uma criação cujo resultado externo seja ambíguo.
                payment.status = 'pending' if order_result.get('ambiguous') else 'failed'
                payment.metadata = payment.metadata or {}
                payment.metadata['error'] = order_result.get('error')
                payment.metadata['ambiguous'] = bool(order_result.get('ambiguous'))
                payment.save()
                logger.warning(
                    'Falha ao criar pedido VPay: %s',
                    order_result.get('error'),
                )
                return Response(
                    {
                        'error': order_result.get('error', 'Erro ao processar pagamento.'),
                        'details': order_result.get('error'),
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            payment.vpay_order_id = order_result['order_id']
            payment.metadata = payment.metadata or {}
            payment.metadata['vpay_order_id'] = order_result['order_id']
            payment.metadata['checkout_url'] = order_result['checkout_url']
            payment.metadata['vpay_response'] = order_result.get('raw_response')
            payment.save()

            checkout_url = order_result['checkout_url']
            logger.info(
                'Pedido VPay criado: %s (orderId=%s)',
                reference, order_result['order_id'],
            )

            return Response({
                'success': True,
                'message': 'Pedido criado. Será redirecionado para o checkout VPay.',
                'payment': PaymentSerializer(payment).data,
                'checkout_url': checkout_url,
            }, status=status.HTTP_201_CREATED)

    except VPayServiceError as exc:
        logger.error('Erro ao criar pedido VPay: %s', str(exc))
        return Response(
            {'error': str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        logger.exception('Erro inesperado ao criar pedido VPay')
        return Response(
            {'error': 'Erro ao processar pagamento. Tente novamente.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def vpay_webhook(request):
    """
    Webhook VPay para confirmação de pagamento.

    Valida a assinatura HMAC-SHA256 (X-Voidpay-Signature: sha256=<hex>) sobre o
    corpo bruto antes de confiar nos dados.
    """
    if not getattr(settings, 'VPAY_ENABLED', True):
        return Response({'error': 'Gateway VPay desativado.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    signature = request.headers.get('X-Voidpay-Signature', '')
    if not vpay_service.verify_webhook_signature(request.body, signature):
        logger.warning('Webhook VPay rejeitado: assinatura inválida ou ausente.')
        return Response(
            {'error': 'Assinatura inválida'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        payload = request.data if isinstance(request.data, dict) else {}
        webhook = vpay_service.parse_webhook(payload)
    except Exception as exc:
        logger.error('Erro ao interpretar webhook VPay: %s', str(exc))
        return Response({'error': 'Payload inválido'}, status=status.HTTP_400_BAD_REQUEST)

    if not webhook.get('success'):
        return Response({'error': 'Payload inválido'}, status=status.HTTP_400_BAD_REQUEST)

    order_id = webhook.get('order_id')
    transaction_reference = webhook.get('transaction_reference') or webhook.get('transaction_id')

    payment = None
    if order_id:
        payment = Payment.objects.filter(gateway='vpay', vpay_order_id=order_id).first()
    if payment is None and transaction_reference:
        payment = Payment.objects.filter(
            gateway='vpay',
            transaction_id=transaction_reference,
        ).first()

    if payment is None:
        logger.error('Webhook VPay: pedido não encontrado (orderId=%s)', order_id)
        # Responder 200 para a VPay não voltar a entregar indefinidamente um
        # evento que não conseguimos reconciliar.
        return Response({'success': False, 'message': 'Pedido não encontrado'})

    vpay_status = webhook.get('status')
    # payment.confirmed -> paid; tratar explicitamente o evento confirmado.
    if webhook.get('event') == 'payment.confirmed':
        vpay_status = 'paid'

    if vpay_status in VPAY_STATUS_MAP:
        apply_vpay_status(payment, vpay_status, activate=True)
    else:
        logger.warning('Webhook VPay: status desconhecido %s', vpay_status)

    # Guardar dados do webhook para auditoria.
    payment.metadata = payment.metadata or {}
    payment.metadata['webhook_data'] = payload
    payment.save()

    return Response({'success': True, 'message': 'Webhook processado'})
