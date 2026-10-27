import logging

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from apps.notifications.delivery import deliver_push_once
from apps.notifications.models import Notification, PushSubscription
from apps.notifications.push import web_push_is_configured
from apps.notifications.service import send_template_email

from .abandoned_checkouts import abandoned_checkout_queryset
from .emails import send_abandoned_checkout_email
from .models import Payment

logger = logging.getLogger(__name__)


@shared_task(name='subscriptions.send_abandoned_checkout_emails')
def send_abandoned_checkout_emails():
    """Envia lembretes uma vez para checkouts VPay pendentes há pelo menos uma hora."""
    now = timezone.now()
    candidates = abandoned_checkout_queryset(now).filter(
        recovery_email_sent_at__isnull=True,
    ).exclude(user__email='')

    sent_count = 0
    failed_count = 0

    for payment in candidates.iterator():
        claimed = Payment.objects.filter(
            pk=payment.pk,
            gateway='vpay',
            status='pending',
            recovery_email_sent_at__isnull=True,
        ).update(recovery_email_sent_at=now)
        if not claimed:
            continue

        if send_abandoned_checkout_email(payment):
            sent_count += 1
            continue

        Payment.objects.filter(
            pk=payment.pk,
            recovery_email_sent_at=now,
        ).update(recovery_email_sent_at=None)
        failed_count += 1
        logger.error(
            'Email de recuperação não enviado para o pagamento pendente %s; será tentado novamente.',
            payment.pk,
        )

    return {'sent': sent_count, 'failed': failed_count}


def _admin_payment_notification(payment, event_type):
    event_fields = {
        'sale': ('admin_sale_email_sent_at', 'admin_sale_push_sent_at'),
        'abandoned': ('admin_abandoned_email_sent_at', 'admin_abandoned_push_sent_at'),
    }
    if event_type not in event_fields:
        raise ValueError(f'Tipo de notificação administrativa inválido: {event_type}')

    email_field, push_field = event_fields[event_type]
    admins = get_user_model().objects.filter(
        Q(is_staff=True) | Q(is_superuser=True),
        is_active=True,
    ).order_by('pk')
    admin_emails = list(
        admins.exclude(email='').values_list('email', flat=True).distinct()
    )
    metadata = payment.metadata or {}
    plan_name = metadata.get('plan_name') or metadata.get('plan') or 'Plano Premium'
    event_key = f'admin-payment-{event_type}:{payment.pk}'
    is_sale = event_type == 'sale'
    title = 'Nova venda confirmada' if is_sale else 'Carrinho abandonado'
    body = (
        f'{plan_name} - {payment.amount} {payment.currency or "MZN"}'
        if is_sale else
        f'Checkout de {plan_name} pendente há pelo menos uma hora.'
    )
    url = '/admin' if is_sale else '/admin/abandoned-checkouts'

    for admin in admins:
        Notification.objects.get_or_create(
            user=admin,
            event_key=event_key,
            defaults={'title': title, 'body': body, 'url': url},
        )

    email_sent = getattr(payment, email_field) is not None
    if not email_sent:
        if not admin_emails:
            logger.error('Nenhuma conta administrativa com email para notificação %s', event_key)
        else:
            try:
                sent = send_template_email(
                    to=admin_emails,
                    subject=f'{title} - PlacarCerto',
                    template_name='admin_payment_event',
                    context={
                        'event_title': title,
                        'event_description': (
                            'Um pagamento foi confirmado.'
                            if is_sale else
                            'Um checkout permaneceu pendente por pelo menos uma hora.'
                        ),
                        'customer_name': (
                            payment.user.get_full_name().strip() or payment.user.username
                        ),
                        'customer_email': payment.user.email,
                        'plan_name': plan_name,
                        'amount': f'{payment.amount:g}',
                        'currency': payment.currency or 'MZN',
                        'transaction_id': payment.transaction_id,
                        'created_at': payment.created_at,
                        'admin_url': f'{settings.FRONTEND_URL.rstrip("/")}{url}',
                    },
                    tags=['admin', 'payment', event_type],
                    fail_silently=False,
                )
                email_sent = sent > 0
            except Exception:
                logger.exception('Erro ao enviar email administrativo %s', event_key)

        if email_sent:
            setattr(payment, email_field, timezone.now())
            payment.save(update_fields=[email_field])

    push_sent = getattr(payment, push_field) is not None
    if not push_sent:
        if not web_push_is_configured():
            logger.error('Web Push não configurado para notificação administrativa %s', event_key)
        else:
            subscriptions = PushSubscription.objects.filter(
                user__in=admins,
                user__push_enabled=True,
                active=True,
            ).select_related('user')
            subscription_count = subscriptions.count()
            if not subscription_count:
                logger.error(
                    'Nenhuma assinatura push ativa de administrador para %s',
                    event_key,
                )
            else:
                payload = {
                    'title': title,
                    'body': body,
                    'url': url,
                    'tag': event_key,
                }
                failed = False
                for subscription in subscriptions:
                    if not deliver_push_once(subscription, event_key, payload):
                        if PushSubscription.objects.filter(pk=subscription.pk, active=True).exists():
                            failed = True
                push_sent = not failed

        if push_sent:
            setattr(payment, push_field, timezone.now())
            payment.save(update_fields=[push_field])

    return {'email_sent': email_sent, 'push_sent': push_sent}


@shared_task(
    bind=True,
    name='subscriptions.send_admin_payment_notification',
    max_retries=5,
    default_retry_delay=300,
)
def send_admin_payment_notification(self, payment_id, event_type):
    payment = Payment.objects.select_related('user').filter(pk=payment_id).first()
    if not payment:
        logger.warning('Pagamento %s não encontrado para notificação administrativa', payment_id)
        return {'sent': False, 'reason': 'payment_not_found'}

    if event_type == 'sale' and payment.status != 'completed':
        return {'sent': False, 'reason': 'payment_not_completed'}
    if event_type == 'abandoned' and payment.status != 'pending':
        return {'sent': False, 'reason': 'payment_not_pending'}

    result = _admin_payment_notification(payment, event_type)
    if not all(result.values()):
        raise self.retry(
            exc=RuntimeError(f'Entrega administrativa incompleta para pagamento {payment_id}'),
        )
    return result


@shared_task(name='subscriptions.reconcile_admin_payment_notifications')
def reconcile_admin_payment_notifications():
    now = timezone.now()
    sales = Payment.objects.filter(status='completed').filter(
        Q(admin_sale_email_sent_at__isnull=True)
        | Q(admin_sale_push_sent_at__isnull=True)
    ).select_related('user')
    abandoned = abandoned_checkout_queryset(now).filter(
        Q(admin_abandoned_email_sent_at__isnull=True)
        | Q(admin_abandoned_push_sent_at__isnull=True)
    )

    results = {'sales': 0, 'abandoned': 0, 'incomplete': 0}
    for event_type, payments in (('sale', sales), ('abandoned', abandoned)):
        count_key = 'sales' if event_type == 'sale' else 'abandoned'
        for payment in payments.iterator():
            result = _admin_payment_notification(payment, event_type)
            results[count_key] += 1
            if not all(result.values()):
                results['incomplete'] += 1
    return results
