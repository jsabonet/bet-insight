from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .abandoned_checkouts import ABANDONED_CHECKOUT_DELAY, abandoned_checkout_queryset


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_abandoned_checkouts(_request):
    now = timezone.now()
    checkouts = abandoned_checkout_queryset(now)
    results = []

    for payment in checkouts:
        user = payment.user
        metadata = payment.metadata or {}
        results.append({
            'payment_id': payment.pk,
            'name': user.get_full_name().strip() or user.username,
            'username': user.username,
            'email': user.email,
            'phone': payment.phone_number or user.phone,
            'account_phone': user.phone,
            'amount': str(payment.amount),
            'currency': payment.currency,
            'plan': metadata.get('plan', ''),
            'plan_name': metadata.get('plan_name', ''),
            'transaction_id': payment.transaction_id,
            'vpay_order_id': payment.vpay_order_id,
            'created_at': payment.created_at,
            'minutes_abandoned': max(
                int((now - payment.created_at).total_seconds() // 60),
                0,
            ),
            'recovery_email_sent_at': payment.recovery_email_sent_at,
        })

    return Response({
        'count': len(results),
        'abandonment_delay_minutes': int(ABANDONED_CHECKOUT_DELAY.total_seconds() // 60),
        'results': results,
    })
