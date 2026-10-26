from urllib.parse import urlparse

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from .models import Notification, PushSubscription
from .push import web_push_is_configured


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        unread_count = notifications.filter(read_at__isnull=True).count()
        items = notifications[:30]
        return Response({
            'unread_count': unread_count,
            'results': [
                {
                    'id': item.id,
                    'event_key': item.event_key,
                    'title': item.title,
                    'body': item.body,
                    'url': item.url,
                    'created_at': item.created_at,
                    'read': item.read_at is not None,
                }
                for item in items
            ],
        })


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notification_id=None):
        notifications = Notification.objects.filter(user=request.user, read_at__isnull=True)
        if notification_id is None:
            updated = notifications.update(read_at=timezone.now())
            return Response({'updated': updated})

        updated = notifications.filter(pk=notification_id).update(read_at=timezone.now())
        if not updated and not Notification.objects.filter(user=request.user, pk=notification_id).exists():
            return Response({'error': 'Notificação não encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'updated': bool(updated)})


ALLOWED_PUSH_HOSTS = (
    'fcm.googleapis.com',
    'push.services.mozilla.com',
    'push.apple.com',
    'notify.windows.com',
    'wns.windows.com',
)


def _is_supported_push_endpoint(hostname):
    hostname = (hostname or '').lower().rstrip('.')
    return any(hostname == host or hostname.endswith(f'.{host}') for host in ALLOWED_PUSH_HOSTS)


class PushStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscription = request.user.push_subscriptions.filter(active=True).order_by('-updated_at').first()
        return Response({
            'available': web_push_is_configured(),
            'public_key': settings.WEBPUSH_VAPID_PUBLIC_KEY if web_push_is_configured() else '',
            'subscribed': bool(subscription),
            'push_enabled': bool(request.user.push_enabled and subscription),
            'analysis_ready_enabled': subscription.analysis_ready_enabled if subscription else True,
            'match_reminders_enabled': subscription.match_reminders_enabled if subscription else True,
            'match_events_enabled': subscription.match_events_enabled if subscription else True,
            'affiliate_notifications_enabled': (
                subscription.affiliate_notifications_enabled if subscription else True
            ),
            'premium_bets_enabled': subscription.premium_bets_enabled if subscription else True,
            'is_affiliate': hasattr(request.user, 'affiliate_profile'),
            'is_premium_active': request.user.is_premium_active(),
        })


class PushSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not web_push_is_configured():
            return Response(
                {'error': 'As notificações push ainda não estão configuradas no servidor.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        raw_subscription = request.data.get('subscription') or request.data
        endpoint = raw_subscription.get('endpoint', '')
        keys = raw_subscription.get('keys') or {}
        parsed_endpoint = urlparse(endpoint)
        if parsed_endpoint.scheme != 'https' or not _is_supported_push_endpoint(parsed_endpoint.hostname):
            return Response({'error': 'Endpoint de push inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        if not keys.get('p256dh') or not keys.get('auth'):
            return Response({'error': 'Chaves da assinatura push incompletas.'}, status=status.HTTP_400_BAD_REQUEST)

        PushSubscription.objects.filter(endpoint=endpoint).exclude(user=request.user).delete()
        subscription, _ = PushSubscription.objects.update_or_create(
            user=request.user,
            endpoint=endpoint,
            defaults={
                'p256dh_key': keys['p256dh'],
                'auth_key': keys['auth'],
                'active': True,
            },
        )
        return Response({'subscribed': True, 'id': subscription.id}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        endpoint = request.data.get('endpoint') or request.query_params.get('endpoint')
        if not endpoint:
            return Response({'error': 'Endpoint da assinatura é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)

        request.user.push_subscriptions.filter(endpoint=endpoint).delete()
        if not request.user.push_subscriptions.filter(active=True).exists():
            request.user.push_enabled = False
            request.user.save(update_fields=['push_enabled'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class PushPreferencesView(APIView):
    permission_classes = [IsAuthenticated]
    preference_fields = (
        'analysis_ready_enabled',
        'match_reminders_enabled',
        'match_events_enabled',
        'affiliate_notifications_enabled',
        'premium_bets_enabled',
    )

    def patch(self, request):
        push_enabled = request.data.get('push_enabled')
        if push_enabled is not None and type(push_enabled) is not bool:
            return Response({'error': 'push_enabled deve ser booleano.'}, status=status.HTTP_400_BAD_REQUEST)

        preferences = {}
        for field in self.preference_fields:
            value = request.data.get(field)
            if value is not None:
                if type(value) is not bool:
                    return Response({'error': f'{field} deve ser booleano.'}, status=status.HTTP_400_BAD_REQUEST)
                preferences[field] = value

        if push_enabled is True and not request.user.push_subscriptions.filter(active=True).exists():
            return Response(
                {'error': 'Registe este dispositivo antes de ativar notificações push.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if preferences:
            request.user.push_subscriptions.filter(active=True).update(**preferences)
        if push_enabled is not None:
            request.user.push_enabled = push_enabled
            request.user.save(update_fields=['push_enabled'])

        subscription = request.user.push_subscriptions.filter(active=True).order_by('-updated_at').first()
        return Response({
            'push_enabled': bool(request.user.push_enabled and subscription),
            'analysis_ready_enabled': subscription.analysis_ready_enabled if subscription else True,
            'match_reminders_enabled': subscription.match_reminders_enabled if subscription else True,
            'match_events_enabled': subscription.match_events_enabled if subscription else True,
            'affiliate_notifications_enabled': (
                subscription.affiliate_notifications_enabled if subscription else True
            ),
            'premium_bets_enabled': subscription.premium_bets_enabled if subscription else True,
        })