from datetime import timedelta

from django.utils import timezone

from .models import Payment

ABANDONED_CHECKOUT_DELAY = timedelta(hours=1)


def abandoned_checkout_queryset(now=None):
    now = now or timezone.now()
    return (
        Payment.objects.filter(
            gateway='vpay',
            status='pending',
            created_at__lte=now - ABANDONED_CHECKOUT_DELAY,
        )
        .exclude(vpay_order_id='')
        .select_related('user')
        .order_by('created_at')
    )
