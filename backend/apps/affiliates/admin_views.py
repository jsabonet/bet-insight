"""Endpoints administrativos do sistema de afiliados."""
import csv
import logging

from django.conf import settings
from django.db import transaction
from django.db.models import Sum, Count, Q, Exists, OuterRef
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import (
    Affiliate, AffiliateCommission, AffiliateWithdrawal,
    AffiliateWithdrawalAllocation,
)
from apps.notifications.models import Notification
from .services import _update_affiliate_balances

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_overview(request):
    """Totais agregados para o painel admin de afiliados."""
    totals = AffiliateCommission.objects.aggregate(
        total_amount=Sum('amount'),
        total_count=Count('id'),
    )
    by_status = {
        s: AffiliateCommission.objects.filter(status=s).aggregate(
            amount=Sum('amount'), count=Count('id'),
        )
        for s in ('pending', 'available', 'paid', 'reversed')
    }
    return Response({
        'affiliates_active': Affiliate.objects.filter(status='active').count(),
        'affiliates_total': Affiliate.objects.count(),
        'commissions_total': totals['total_count'] or 0,
        'commissions_amount': totals['total_amount'] or 0,
        'by_status': {
            k: {'amount': v['amount'] or 0, 'count': v['count'] or 0}
            for k, v in by_status.items()
        },
        'top_affiliates': list(
            Affiliate.objects.filter(status='active')
            .annotate(total=Sum('commissions__amount'))
            .order_by('-total')[:10]
            .values('id', 'code', 'user__username', 'total', 'tier')
        ),
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_affiliates_list(request):
    """Lista de afiliados com filtros."""
    search = request.query_params.get('search', '')
    status_filter = request.query_params.get('status', '')

    qs = Affiliate.objects.select_related('user').all()
    if search:
        qs = qs.filter(Q(code__icontains=search) | Q(user__email__icontains=search) | Q(user__username__icontains=search))
    if status_filter:
        qs = qs.filter(status=status_filter)

    data = [{
        'id': a.id,
        'code': a.code,
        'username': a.user.username,
        'email': a.user.email,
        'status': a.status,
        'tier': a.tier,
        'commission_rate': str(a.commission_rate),
        'renewal_rate': str(a.renewal_rate),
        'total_earned': str(a.total_earned),
        'available_balance': str(a.available_balance),
        'pending_balance': str(a.pending_balance),
        'payout_method': a.payout_method,
        'payout_method_display': a.get_payout_method_display(),
        'payout_account': a.payout_account,
        'referrals_count': a.referrals.count(),
        'converted_count': a.referrals.filter(converted_at__isnull=False).count(),
        'created_at': a.created_at,
    } for a in qs[:200]]
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_commissions_list(request):
    """Lista de comissões com filtros."""
    status_filter = request.query_params.get('status', '')
    qs = AffiliateCommission.objects.select_related(
        'affiliate', 'payment', 'payment__user',
    ).annotate(
        withdrawal_allocated=Exists(
            AffiliateWithdrawalAllocation.objects.filter(
                commission_id=OuterRef('pk'),
            ).exclude(withdrawal__status='rejected')
        )
    )
    if status_filter:
        qs = qs.filter(status=status_filter)

    data = [{
        'id': c.id,
        'affiliate_code': c.affiliate.code,
        'affiliate_user': c.affiliate.user.username,
        'buyer_email': c.payment.user.email if c.payment and c.payment.user else None,
        'plan': (c.payment.metadata or {}).get('plan') if c.payment else None,
        'amount': str(c.amount),
        'rate': str(c.rate),
        'commission_type': c.commission_type,
        'status': c.status,
        'withdrawal_allocated': c.withdrawal_allocated,
        'available_at': c.available_at,
        'paid_at': c.paid_at,
        'created_at': c.created_at,
    } for c in qs[:500]]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_approve_commission(request, commission_id):
    """Marca uma comissão pending como available."""
    try:
        commission = AffiliateCommission.objects.get(id=commission_id)
    except AffiliateCommission.DoesNotExist:
        return Response({'error': 'Comissão não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    if commission.status != 'pending':
        return Response({'error': 'Comissão não está pendente.'}, status=status.HTTP_400_BAD_REQUEST)

    commission.status = 'available'
    commission.available_at = timezone.now()
    commission.save(update_fields=['status', 'available_at', 'updated_at'])
    _update_affiliate_balances(commission.affiliate)

    # Notificar o afiliado (não bloqueia a ação).
    try:
        from .emails import send_commission_available_email
        send_commission_available_email(commission)
    except Exception as exc:
        logger.warning('Falha ao enviar email de comissão disponível: %s', exc)
    from .services import _enqueue_commission_push
    _enqueue_commission_push(
        commission.pk,
        commission.affiliate.user_id,
        'commission_available',
    )

    return Response({'message': 'Comissão aprovada (available).'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_mark_paid(request, commission_id):
    """Marca uma comissão available como paid e debita do saldo disponível."""
    try:
        affiliate_id = AffiliateCommission.objects.values_list(
            'affiliate_id', flat=True,
        ).get(id=commission_id)
    except AffiliateCommission.DoesNotExist:
        return Response({'error': 'Comissão não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        Affiliate.objects.select_for_update().get(pk=affiliate_id)
        try:
            commission = AffiliateCommission.objects.select_for_update().get(id=commission_id)
        except AffiliateCommission.DoesNotExist:
            return Response({'error': 'Comissão não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        if commission.status != 'available':
            return Response({'error': 'Só comissões disponíveis podem ser marcadas como pagas.'}, status=status.HTTP_400_BAD_REQUEST)
        if commission.withdrawal_allocations.exclude(withdrawal__status='rejected').exists():
            return Response({
                'error': 'Esta comissão está associada a um pedido de levantamento. Processe ou rejeite esse pedido.',
            }, status=status.HTTP_400_BAD_REQUEST)

        commission.status = 'paid'
        commission.paid_at = timezone.now()
        commission.save(update_fields=['status', 'paid_at', 'updated_at'])
        _update_affiliate_balances(commission.affiliate)

    # Notificar o afiliado (não bloqueia a ação).
    try:
        from .emails import send_commission_paid_email
        send_commission_paid_email(commission)
    except Exception as exc:
        logger.warning('Falha ao enviar email de comissão paga: %s', exc)
    from .services import _enqueue_commission_push
    _enqueue_commission_push(
        commission.pk,
        commission.affiliate.user_id,
        'commission_paid',
    )

    return Response({'message': 'Comissão marcada como paga.'})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_withdrawals_list(request):
    """Lista pedidos de levantamento para a equipa administrativa."""
    status_filter = request.query_params.get('status', '')
    withdrawals = AffiliateWithdrawal.objects.select_related(
        'affiliate', 'affiliate__user', 'processed_by',
    )
    if status_filter:
        withdrawals = withdrawals.filter(status=status_filter)

    return Response([{
        'id': item.pk,
        'affiliate_id': item.affiliate_id,
        'affiliate_code': item.affiliate.code,
        'affiliate_username': item.affiliate.user.username,
        'affiliate_email': item.affiliate.user.email,
        'amount': str(item.amount),
        'fee_rate': str(item.fee_rate),
        'fee_amount': str(item.fee_amount),
        'payout_amount': str(item.payout_amount),
        'payout_method': item.payout_method,
        'payout_method_display': item.get_payout_method_display(),
        'payout_account': item.payout_account,
        'status': item.status,
        'status_display': item.get_status_display(),
        'transaction_reference': item.transaction_reference,
        'rejection_reason': item.rejection_reason,
        'requested_at': item.requested_at,
        'processed_at': item.processed_at,
        'processed_by': item.processed_by.username if item.processed_by else None,
    } for item in withdrawals[:500]])


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_process_withdrawal(request, withdrawal_id):
    """Coloca um pedido solicitado em processamento."""
    try:
        affiliate_id = AffiliateWithdrawal.objects.values_list(
            'affiliate_id', flat=True,
        ).get(id=withdrawal_id)
    except AffiliateWithdrawal.DoesNotExist:
        return Response({'error': 'Pedido de levantamento não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        Affiliate.objects.select_for_update().get(pk=affiliate_id)
        try:
            withdrawal = AffiliateWithdrawal.objects.select_for_update().get(id=withdrawal_id)
        except AffiliateWithdrawal.DoesNotExist:
            return Response({'error': 'Pedido de levantamento não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if withdrawal.status != 'requested':
            return Response({'error': 'Só pedidos solicitados podem entrar em processamento.'}, status=status.HTTP_400_BAD_REQUEST)

        withdrawal.status = 'processing'
        withdrawal.processed_by = request.user
        withdrawal.save(update_fields=['status', 'processed_by', 'updated_at'])

    return Response({'message': 'Pedido colocado em processamento.'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_complete_withdrawal(request, withdrawal_id):
    """Regista o pagamento efetivamente enviado ao afiliado."""
    reference = str(request.data.get('transaction_reference', '')).strip()
    if not reference:
        return Response({'error': 'Informe a referência da transação.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        affiliate_id = AffiliateWithdrawal.objects.values_list(
            'affiliate_id', flat=True,
        ).get(id=withdrawal_id)
    except AffiliateWithdrawal.DoesNotExist:
        return Response({'error': 'Pedido de levantamento não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        affiliate = Affiliate.objects.select_for_update().get(pk=affiliate_id)
        try:
            withdrawal = AffiliateWithdrawal.objects.select_for_update().get(id=withdrawal_id)
        except AffiliateWithdrawal.DoesNotExist:
            return Response({'error': 'Pedido de levantamento não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if withdrawal.status != 'processing':
            return Response({'error': 'Só pedidos em processamento podem ser marcados como pagos.'}, status=status.HTTP_400_BAD_REQUEST)
        if withdrawal.allocations.exclude(commission__status='available').exists():
            return Response({
                'error': 'Uma comissão reservada já não está disponível. Rejeite o pedido e verifique o saldo.',
            }, status=status.HTTP_400_BAD_REQUEST)

        withdrawal.status = 'paid'
        withdrawal.transaction_reference = reference[:100]
        withdrawal.processed_by = request.user
        withdrawal.processed_at = timezone.now()
        withdrawal.save(update_fields=[
            'status', 'transaction_reference', 'processed_by', 'processed_at', 'updated_at',
        ])
        _update_affiliate_balances(affiliate)
        Notification.objects.get_or_create(
            user=affiliate.user,
            event_key=f'affiliate_withdrawal_paid_{withdrawal.pk}',
            defaults={
                'title': 'Levantamento pago',
                'body': f'O seu levantamento de {withdrawal.payout_amount} MZN foi pago.',
                'url': '/affiliate',
            },
        )

    return Response({'message': 'Levantamento marcado como pago.'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_reject_withdrawal(request, withdrawal_id):
    """Rejeita um pedido e liberta o saldo reservado."""
    reason = str(request.data.get('reason', '')).strip()
    if not reason:
        return Response({'error': 'Informe o motivo da rejeição.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        affiliate_id = AffiliateWithdrawal.objects.values_list(
            'affiliate_id', flat=True,
        ).get(id=withdrawal_id)
    except AffiliateWithdrawal.DoesNotExist:
        return Response({'error': 'Pedido de levantamento não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    with transaction.atomic():
        affiliate = Affiliate.objects.select_for_update().get(pk=affiliate_id)
        try:
            withdrawal = AffiliateWithdrawal.objects.select_for_update().get(id=withdrawal_id)
        except AffiliateWithdrawal.DoesNotExist:
            return Response({'error': 'Pedido de levantamento não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if withdrawal.status not in ('requested', 'processing'):
            return Response({'error': 'Este pedido não pode ser rejeitado.'}, status=status.HTTP_400_BAD_REQUEST)

        withdrawal.status = 'rejected'
        withdrawal.rejection_reason = reason[:2000]
        withdrawal.processed_by = request.user
        withdrawal.processed_at = timezone.now()
        withdrawal.save(update_fields=[
            'status', 'rejection_reason', 'processed_by', 'processed_at', 'updated_at',
        ])
        _update_affiliate_balances(affiliate)

    return Response({'message': 'Pedido rejeitado e saldo libertado.'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_set_tier(request, affiliate_id):
    """Atualiza o nível (tier) e as taxas de um afiliado."""
    try:
        affiliate = Affiliate.objects.get(id=affiliate_id)
    except Affiliate.DoesNotExist:
        return Response({'error': 'Afiliado não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    tier = request.data.get('tier')
    if tier not in ('standard', 'vip'):
        return Response({'error': 'Nível inválido (standard|vip).'}, status=status.HTTP_400_BAD_REQUEST)

    affiliate.tier = tier
    default_rate = getattr(settings, 'AFFILIATE_VIP_RATE', 0.50) if tier == 'vip' else getattr(settings, 'AFFILIATE_DEFAULT_RATE', 0.40)
    affiliate.commission_rate = request.data.get('commission_rate', default_rate)
    affiliate.save(update_fields=['tier', 'commission_rate', 'updated_at'])
    return Response({'message': 'Nível atualizado.'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_toggle_suspend(request, affiliate_id):
    """Suspende/reativa um afiliado."""
    try:
        affiliate = Affiliate.objects.get(id=affiliate_id)
    except Affiliate.DoesNotExist:
        return Response({'error': 'Afiliado não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    affiliate.status = 'suspended' if affiliate.status == 'active' else 'active'
    affiliate.save(update_fields=['status', 'updated_at'])
    return Response({'message': 'Status atualizado.', 'status': affiliate.status})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_export_commissions(request):
    """Exporta comissões em CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="comissoes.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'id', 'afiliado', 'comprador', 'plano', 'valor',
        'tipo_comissao', 'taxa', 'status', 'criado_em',
    ])
    for c in AffiliateCommission.objects.select_related('affiliate', 'payment', 'payment__user').all():
        writer.writerow([
            c.id,
            c.affiliate.code,
            c.payment.user.email if c.payment and c.payment.user else '',
            (c.payment.metadata or {}).get('plan') if c.payment else '',
            c.amount,
            c.commission_type,
            c.rate,
            c.status,
            c.created_at,
        ])
    return response
