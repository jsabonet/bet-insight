from django.conf import settings
from django.db import models


class PushSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
    )
    endpoint = models.URLField(max_length=2048)
    p256dh_key = models.CharField(max_length=255)
    auth_key = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    analysis_ready_enabled = models.BooleanField(default=True)
    match_reminders_enabled = models.BooleanField(default=True)
    match_events_enabled = models.BooleanField(default=True)
    affiliate_notifications_enabled = models.BooleanField(default=True)
    premium_bets_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['endpoint'],
                name='unique_push_endpoint',
            ),
        ]
        indexes = [models.Index(fields=['user', 'active'])]

    def __str__(self):
        return f'Push subscription for user {self.user_id}'


class PushDelivery(models.Model):
    subscription = models.ForeignKey(
        PushSubscription,
        on_delete=models.CASCADE,
        related_name='deliveries',
    )
    event_key = models.CharField(max_length=180)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscription', 'event_key'],
                name='unique_push_delivery_event',
            ),
        ]

    def __str__(self):
        return f'{self.event_key} to subscription {self.subscription_id}'