"""Endpoints administrativos do sistema de afiliados."""
import csv
import logging

from django.conf import settings
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Affiliate, AffiliateCommission
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
    qs = AffiliateCommission.objects.select_related('affiliate', 'payment', 'payment__user').all()
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
        'status': c.status,
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

    return Response({'message': 'Comissão aprovada (available).'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_mark_paid(request, commission_id):
    """Marca uma comissão available como paid e debita do saldo disponível."""
    try:
        commission = AffiliateCommission.objects.get(id=commission_id)
    except AffiliateCommission.DoesNotExist:
        return Response({'error': 'Comissão não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

    if commission.status not in ('available',):
        return Response({'error': 'Só comissões disponíveis podem ser marcadas como pagas.'}, status=status.HTTP_400_BAD_REQUEST)

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

    return Response({'message': 'Comissão marcada como paga.'})


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
    writer.writerow(['id', 'afiliado', 'comprador', 'plano', 'valor', 'taxa', 'status', 'criado_em'])
    for c in AffiliateCommission.objects.select_related('affiliate', 'payment', 'payment__user').all():
        writer.writerow([
            c.id,
            c.affiliate.code,
            c.payment.user.email if c.payment and c.payment.user else '',
            (c.payment.metadata or {}).get('plan') if c.payment else '',
            c.amount,
            c.rate,
            c.status,
            c.created_at,
        ])
    return response
