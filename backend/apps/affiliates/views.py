"""Endpoints públicos e do próprio afiliado."""
import uuid
import logging
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import (
    Affiliate, AffiliateReferral, AffiliateCommission, AffiliateClick,
    AffiliateWithdrawal, AffiliateWithdrawalAllocation,
)
from .serializers import (
    AffiliateSerializer,
    AffiliateApplySerializer,
    AffiliateCommissionSerializer,
    AffiliateReferralSerializer,
    WithdrawRequestSerializer,
)
from .services import resolve_affiliate_by_code, generate_unique_code, code_to_string

logger = logging.getLogger(__name__)


def _get_or_404_affiliate(user):
    try:
        return user.affiliate_profile
    except Affiliate.DoesNotExist:
        return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def member_referral_summary(request):
    """Resumo privado do programa de convites entre membros."""
    user = request.user
    if not user.member_referral_code:
        user.save(update_fields=['member_referral_code'])

    referrals = user.member_referrals_sent.all()
    return Response({
        'code': user.member_referral_code,
        'total_invites': referrals.count(),
        'completed_invites': referrals.filter(reward_status='rewarded').count(),
        'pending_invites': referrals.filter(reward_status='pending').count(),
        'ineligible_invites': referrals.filter(reward_status='ineligible').count(),
        'bonus_analysis_credits': user.bonus_analysis_credits,
        'reward_per_member': 5,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def apply_affiliate(request):
    """Candidata o utilizador a afiliado (gera código se ainda não existe)."""
    existing = _get_or_404_affiliate(request.user)
    if existing:
        return Response({
            'message': 'Já é afiliado.',
            'affiliate': AffiliateSerializer(existing, context={'request': request}).data,
        })

    serializer = AffiliateApplySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    code = generate_unique_code(request.user.username)
    affiliate = Affiliate.objects.create(
        user=request.user,
        code=code,
        status='active',
        tier='standard',
        commission_rate=getattr(settings, 'AFFILIATE_DEFAULT_RATE', 0.40),
        renewal_rate=getattr(settings, 'AFFILIATE_RENEWAL_RATE', 0.10),
        payout_method=serializer.validated_data.get('payout_method', 'mpesa'),
        payout_account=serializer.validated_data.get('payout_account', ''),
    )

    # Notificar o afiliado por email (não bloqueia a criação).
    try:
        from .emails import send_affiliate_approved_email
        send_affiliate_approved_email(affiliate)
    except Exception as exc:
        logger.warning('Falha ao enviar email de afiliado aprovado: %s', exc)

    return Response({
        'message': 'Conta de afiliado criada com sucesso.',
        'affiliate': AffiliateSerializer(affiliate, context={'request': request}).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def my_affiliate(request):
    """Lê/atualiza o perfil de afiliado do utilizador logado."""
    affiliate = _get_or_404_affiliate(request.user)
    if affiliate is None:
        return Response({'error': 'Ainda não é afiliado.'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        serializer = AffiliateApplySerializer(affiliate, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'Dados de pagamento atualizados.',
            'affiliate': AffiliateSerializer(affiliate, context={'request': request}).data,
        })

    return Response(AffiliateSerializer(affiliate, context={'request': request}).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_affiliate_stats(request):
    """Estatísticas agregadas do afiliado."""
    affiliate = _get_or_404_affiliate(request.user)
    if affiliate is None:
        return Response({'error': 'Ainda não é afiliado.'}, status=status.HTTP_404_NOT_FOUND)

    now = timezone.now()
    thirty_days_ago = now - timezone.timedelta(days=30)

    clicks_total = affiliate.clicks.count()
    clicks_30d = affiliate.clicks.filter(created_at__gte=thirty_days_ago).count()
    conversions_total = affiliate.referrals.filter(converted_at__isnull=False).count()
    conversions_30d = affiliate.referrals.filter(
        converted_at__isnull=False, converted_at__gte=thirty_days_ago,
    ).count()
    revenue_30d = affiliate.commissions.filter(
        created_at__gte=thirty_days_ago,
    ).exclude(status='reversed').aggregate(s=Sum('amount'))['s'] or 0

    # Série de 7 dias para o gráfico (cliques e conversões).
    daily = []
    for i in range(6, -1, -1):
        day = now.date() - timezone.timedelta(days=i)
        start = timezone.make_aware(
            timezone.datetime.combine(day, timezone.datetime.min.time())
        )
        end = start + timezone.timedelta(days=1)
        clicks = affiliate.clicks.filter(created_at__gte=start, created_at__lt=end).count()
        conv = affiliate.referrals.filter(
            converted_at__gte=start, converted_at__lt=end,
        ).count()
        daily.append({'date': day.isoformat(), 'clicks': clicks, 'conversions': conv})

    return Response({
        'clicks_total': clicks_total,
        'clicks_30d': clicks_30d,
        'conversions_total': conversions_total,
        'conversions_30d': conversions_30d,
        'revenue_30d': revenue_30d,
        'commissions_pending': affiliate.commissions.filter(status='pending').count(),
        'commissions_available': affiliate.commissions.filter(status='available').count(),
        'daily': daily,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_commissions(request):
    """Lista as comissões do afiliado logado."""
    affiliate = _get_or_404_affiliate(request.user)
    if affiliate is None:
        return Response({'error': 'Ainda não é afiliado.'}, status=status.HTTP_404_NOT_FOUND)

    status_filter = request.query_params.get('status')
    qs = affiliate.commissions.all().select_related('payment', 'payment__user')
    if status_filter:
        qs = qs.filter(status=status_filter)
    return Response(AffiliateCommissionSerializer(qs[:100], many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_referrals(request):
    """Lista as indicações (contas criadas via link) do afiliado logado."""
    affiliate = _get_or_404_affiliate(request.user)
    if affiliate is None:
        return Response({'error': 'Ainda não é afiliado.'}, status=status.HTTP_404_NOT_FOUND)

    qs = affiliate.referrals.select_related('user').all()[:50]
    return Response(AffiliateReferralSerializer(qs, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    """Pede levantamento (valida saldo disponível e threshold mínimo)."""
    affiliate = _get_or_404_affiliate(request.user)
    if affiliate is None:
        return Response({'error': 'Ainda não é afiliado.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = WithdrawRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    amount = serializer.validated_data['amount']

    min_withdrawal = int(getattr(settings, 'AFFILIATE_MIN_WITHDRAWAL', 200))
    if amount < min_withdrawal:
        return Response({
            'error': f'Valor mínimo de levantamento: {min_withdrawal} MZN.',
        }, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        affiliate = Affiliate.objects.select_for_update().get(pk=affiliate.pk)
        commissions = list(
            AffiliateCommission.objects.select_for_update()
            .filter(affiliate=affiliate, status='available')
            .order_by('created_at', 'id')
        )
        allocated = {
            row['commission_id']: row['total']
            for row in AffiliateWithdrawalAllocation.objects.filter(
                commission__in=commissions,
                withdrawal__status__in=('requested', 'processing', 'paid'),
            ).values('commission_id').annotate(total=Sum('amount'))
        }
        remaining_balance = sum(
            max(commission.amount - allocated.get(commission.id, Decimal('0.00')), Decimal('0.00'))
            for commission in commissions
        )
        if amount > remaining_balance:
            return Response({
                'error': 'Saldo disponível insuficiente.',
            }, status=status.HTTP_400_BAD_REQUEST)

        fee_rate = Decimal(str(getattr(settings, 'AFFILIATE_WITHDRAWAL_FEE_RATE', 6)))
        fee_amount = (amount * fee_rate / Decimal('100')).quantize(Decimal('0.01'))
        payout_amount = amount - fee_amount
        if not affiliate.payout_account.strip():
            return Response({
                'error': 'Configure uma conta de pagamento antes de pedir o levantamento.',
            }, status=status.HTTP_400_BAD_REQUEST)

        withdrawal = AffiliateWithdrawal.objects.create(
            affiliate=affiliate,
            amount=amount,
            fee_rate=fee_rate,
            fee_amount=fee_amount,
            payout_amount=payout_amount,
            payout_method=affiliate.payout_method,
            payout_account=affiliate.payout_account,
        )
        amount_to_allocate = amount
        for commission in commissions:
            available = max(
                commission.amount - allocated.get(commission.id, Decimal('0.00')),
                Decimal('0.00'),
            )
            allocation_amount = min(available, amount_to_allocate)
            if allocation_amount > 0:
                AffiliateWithdrawalAllocation.objects.create(
                    withdrawal=withdrawal,
                    commission=commission,
                    amount=allocation_amount,
                )
                amount_to_allocate -= allocation_amount
            if amount_to_allocate == 0:
                break

        from .services import _update_affiliate_balances
        _update_affiliate_balances(affiliate)

    # Notificar o afiliado por email (não bloqueia o pedido).
    try:
        from .emails import send_withdrawal_requested_email
        send_withdrawal_requested_email(affiliate, withdrawal)
    except Exception as exc:
        logger.warning('Falha ao enviar email de levantamento: %s', exc)
    try:
        from .emails import send_withdrawal_admin_email
        send_withdrawal_admin_email(withdrawal)
    except Exception as exc:
        logger.warning('Falha ao notificar administradores do levantamento: %s', exc)

    return Response({
        'message': 'Pedido de levantamento registado. Será processado pela equipa.',
        'id': withdrawal.pk,
        'requested_amount': amount,
        'fee_rate': withdrawal.fee_rate,
        'fee_amount': withdrawal.fee_amount,
        'payout_amount': withdrawal.payout_amount,
        'available_balance': affiliate.available_balance,
        'payout_method': withdrawal.payout_method,
        'payout_account': withdrawal.payout_account,
        'status': withdrawal.status,
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_withdrawals(request):
    affiliate = _get_or_404_affiliate(request.user)
    if affiliate is None:
        return Response({'error': 'Ainda não é afiliado.'}, status=status.HTTP_404_NOT_FOUND)

    withdrawals = affiliate.withdrawals.all()[:100]
    return Response([{
        'id': item.pk,
        'amount': str(item.amount),
        'fee_rate': str(item.fee_rate),
        'fee_amount': str(item.fee_amount),
        'payout_amount': str(item.payout_amount),
        'payout_method': item.payout_method,
        'payout_method_display': item.get_payout_method_display(),
        'status': item.status,
        'status_display': item.get_status_display(),
        'transaction_reference': item.transaction_reference,
        'rejection_reason': item.rejection_reason,
        'requested_at': item.requested_at,
        'processed_at': item.processed_at,
    } for item in withdrawals])


@api_view(['POST'])
@permission_classes([AllowAny])
def track_click(request):
    """Regista um clique em link de afiliado e devolve click_id + cookie.

    Body: { "code": "JOAO123" }
    """
    code = code_to_string(request.data.get('code', ''))
    affiliate = resolve_affiliate_by_code(code)
    if affiliate is None:
        return Response({'error': 'Código de afiliado inválido.'}, status=status.HTTP_404_NOT_FOUND)

    click_id = uuid.uuid4().hex
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = ip.split(',')[0].strip() if ip else request.META.get('REMOTE_ADDR')

    AffiliateClick.objects.create(
        affiliate=affiliate,
        code=code,
        click_id=click_id,
        ip=ip,
        user_agent=(request.META.get('HTTP_USER_AGENT', '') or '')[:255],
    )

    response = Response({'success': True, 'code': code, 'click_id': click_id})
    cookie_days = int(getattr(settings, 'AFFILIATE_COOKIE_DAYS', 30))
    response.set_cookie(
        'affiliate_ref', code,
        max_age=cookie_days * 24 * 3600,
        httponly=True,
        samesite='Lax',
    )
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def validate_code(request):
    """Valida um código de afiliado (usado no checkout/registo)."""
    code = code_to_string(request.data.get('code', ''))
    affiliate = resolve_affiliate_by_code(code)
    if affiliate is None:
        return Response({'valid': False, 'error': 'Código inválido.'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'valid': True, 'code': affiliate.code, 'name': affiliate.user.username})
