import logging

from django.db import transaction
from django.utils import timezone

from .models import Notification, PushDelivery
from .push import send_web_push

logger = logging.getLogger(__name__)


def deliver_push_once(subscription, event_key, payload):
    if not subscription.active or not subscription.user.push_enabled:
        return True

    with transaction.atomic():
        delivery, _ = PushDelivery.objects.get_or_create(
            subscription=subscription,
            event_key=event_key,
        )
        delivery = PushDelivery.objects.select_for_update().get(pk=delivery.pk)
        if delivery.sent_at:
            return True

        if not send_web_push(subscription, payload):
            return False

        delivery.sent_at = timezone.now()
        delivery.save(update_fields=['sent_at'])
        Notification.objects.get_or_create(
            user=subscription.user,
            event_key=event_key,
            defaults={
                'title': payload.get('title', 'Notificação'),
                'body': payload.get('body', ''),
                'url': payload.get('url', ''),
            },
        )
        return True