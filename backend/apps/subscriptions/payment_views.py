"""
Views para processar pagamentos via PaySuite
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import uuid
import logging

from .models import Subscription, Payment
from .paysuite_service import paysuite_service
from .plan_config import get_plan
from .serializers import SubscriptionSerializer, PaymentSerializer
from .emails import (
    send_payment_confirmed_email,
    send_payment_failed_email,
    send_subscription_activated_email
)

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request):
    """
    Inicia processo de pagamento via PaySuite
    
    Body:
    {
        "plan_slug": "starter|pro|vip",
        "payment_method": "mpesa|emola"
    }
    
    Nota: Telefone NÃO é mais obrigatório. 
    O usuário preencherá na página externa da PaySuite.
    """
    user = request.user
    plan_slug = request.data.get('plan_slug')
    payment_method = request.data.get('payment_method', 'mpesa')
    
    # Validações
    valid_plans = ['teste', 'starter', 'pro', 'vip', 'monthly', 'quarterly', 'yearly']
    if not plan_slug or plan_slug not in valid_plans:
        plans_str = ', '.join(valid_plans)
        return Response(
            {'error': f'Plano inválido. Use: {plans_str}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Buscar configuração do plano
    plan = get_plan(plan_slug)
    if not plan:
        return Response(
            {'error': 'Plano não encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    amount = Decimal(str(plan['price']))
    
    # Verificar se usuário já tem assinatura ativa
    existing_subscription = user.subscriptions.filter(
        status='active',
        end_date__gt=timezone.now()
    ).exclude(plan_slug='freemium').first()
    
    if existing_subscription:
        return Response(
            {
                'error': 'Você já possui uma assinatura ativa',
                'subscription': SubscriptionSerializer(existing_subscription).data
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        with transaction.atomic():
            # Gerar referência única (apenas letras e números conforme PaySuite)
            reference = f"BET{user.id}{uuid.uuid4().hex[:8].upper()}"
            
            # Criar assinatura pendente
            subscription = Subscription.objects.create(
                user=user,
                plan=plan_slug,
                plan_slug=plan_slug,
                status='pending',
                amount_paid=amount,
                auto_renew=True,
            )
            
            # Criar registro de pagamento
            payment = Payment.objects.create(
                user=user,
                subscription=subscription,
                amount=amount,
                currency='MZN',
                phone_number='',  # Será preenchido na página externa
                transaction_id=reference,
                payment_method=payment_method,
                status='pending',
                metadata={
                    'plan': plan_slug,
                    'plan_name': plan['name'],
                }
            )
            
            # Iniciar pagamento via PaySuite (sem telefone)
            paysuite_response = paysuite_service.create_payment(
                phone_number=None,  # Sem telefone - checkout externo
                amount=amount,
                reference=reference,
                description=f"PlacarCerto - {plan['name']}",
                method=payment_method
            )
            
            if not paysuite_response.get('success'):
                # Marcar como falho
                payment.mark_as_failed(paysuite_response.get('error', 'Erro desconhecido'))
                subscription.status = 'cancelled'
                subscription.save()
                
                return Response(
                    {
                        'error': paysuite_response.get('message', 'Erro ao processar pagamento'),
                        'details': paysuite_response.get('error'),
                        'paysuite_raw': paysuite_response.get('raw_response')
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Atualizar com dados do PaySuite
            payment.paysuite_reference = paysuite_response.get('paysuite_reference', '')
            payment.metadata['paysuite_response'] = paysuite_response.get('raw_response', {})
            checkout_url = paysuite_response.get('checkout_url', '')
            if checkout_url:
                payment.metadata['checkout_url'] = checkout_url
            payment.save()
            
            logger.info(f"Pagamento iniciado: {reference} - User: {user.id} - Plan: {plan_slug}")
            logger.info(f"Checkout URL: {checkout_url}")
            
            instructions_msg = 'Pagamento iniciado.'
            if checkout_url:
                instructions_msg += ' Abriremos a página de checkout para confirmação.'

            # Criar resposta com checkout_url explícito
            response_data = {
                'success': True,
                'message': instructions_msg,
                'payment': PaymentSerializer(payment).data,
                'subscription': SubscriptionSerializer(subscription).data,
                'instructions': instructions_msg
            }
            
            # Adicionar checkout_url diretamente na resposta
            if checkout_url:
                response_data['checkout_url'] = checkout_url
                response_data['payment']['checkout_url'] = checkout_url
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"Erro ao criar pagamento: {str(e)}")
        return Response(
            {'error': 'Erro ao processar pagamento. Tente novamente.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def paysuite_webhook(request):
    """
    Webhook para receber notificações do PaySuite
    
    Este endpoint é chamado pela PaySuite quando o status
    de um pagamento muda (confirmado, falho, etc.)
    """
    try:
        # Obter assinatura do header (se disponível)
        signature = request.headers.get('X-PaySuite-Signature', '')
        
        # Processar webhook
        webhook_data = paysuite_service.process_webhook(
            payload=request.data,
            signature=signature if signature else None
        )
        
        if not webhook_data.get('success'):
            logger.warning(f"Webhook inválido: {webhook_data}")
            return Response(
                {'error': 'Invalid webhook'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction_id = webhook_data['transaction_id']
        payment_status = webhook_data['status']
        
        # Buscar pagamento
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            logger.error(f"Pagamento não encontrado: {transaction_id}")
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Atualizar status
        if payment_status == 'completed' or payment_status == 'success':
            payment.mark_as_completed(
                paid_at=webhook_data.get('paid_at')
            )
            logger.info(f"Pagamento confirmado: {transaction_id}")
            
            # Enviar emails de confirmação
            send_payment_confirmed_email(payment.user, payment, payment.subscription)
            send_subscription_activated_email(payment.user, payment.subscription)
            
        elif payment_status == 'failed' or payment_status == 'cancelled':
            payment.mark_as_failed(
                reason=webhook_data.get('error', 'Pagamento não confirmado')
            )
            logger.warning(f"Pagamento falhou: {transaction_id}")
            
            # Enviar email de falha
            send_payment_failed_email(payment.user, payment)
        
        # Atualizar metadata com dados do webhook
        if not payment.metadata:
            payment.metadata = {}
        payment.metadata['webhook_data'] = webhook_data
        payment.save()
        
        return Response({
            'success': True,
            'message': 'Webhook processed'
        })
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return Response(
            {'error': 'Internal error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_payment_status(request, transaction_id):
    """
    Verifica status de um pagamento específico consultando a PaySuite
    Usado para polling do frontend (1 requisição por segundo por até 2 minutos)
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
    
    # Se já está completo, retornar imediatamente
    if payment.status == 'completed':
        return Response({
            'status': 'completed',
            'payment': PaymentSerializer(payment).data,
            'subscription': SubscriptionSerializer(payment.subscription).data if payment.subscription else None
        })
    
    # Consultar status na PaySuite usando o UUID do provider (paysuite_reference)
    provider_id = payment.paysuite_reference or transaction_id
    
    logger.info(f"🔍 Consultando status PaySuite para: {provider_id}")
    paysuite_response = paysuite_service.check_payment_status(provider_id)
    
    if paysuite_response.get('success'):
        paysuite_status = paysuite_response.get('status')
        logger.info(f"📊 Status PaySuite: {paysuite_status}")
        
        # Atualizar payment se status mudou para completed
        if paysuite_status == 'completed' and payment.status != 'completed':
            logger.info(f"✅ Ativando assinatura via polling para pagamento {transaction_id}")
            payment.mark_as_completed(
                paid_at=paysuite_response.get('paid_at') or timezone.now()
            )
            
            # Enviar emails de confirmação
            try:
                send_payment_confirmed_email(payment.user, payment, payment.subscription)
                send_subscription_activated_email(payment.user, payment.subscription)
            except Exception as e:
                logger.error(f"Erro ao enviar emails: {str(e)}")
        
        elif paysuite_status == 'failed' and payment.status == 'pending':
            logger.warning(f"❌ Pagamento falhou na PaySuite: {transaction_id}")
            payment.mark_as_failed(reason='Pagamento rejeitado pela PaySuite')
    
    return Response({
        'status': payment.status,
        'payment': PaymentSerializer(payment).data,
        'subscription': SubscriptionSerializer(payment.subscription).data if payment.subscription else None,
        'paysuite_status': paysuite_response.get('status'),
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
