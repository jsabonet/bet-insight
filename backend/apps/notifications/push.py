import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def web_push_is_configured():
    return bool(settings.WEBPUSH_VAPID_PUBLIC_KEY and settings.WEBPUSH_VAPID_PRIVATE_KEY)


def send_web_push(subscription, payload):
    if not web_push_is_configured():
        logger.warning('Web Push ignorado: chaves VAPID não configuradas')
        return False

    from pywebpush import WebPushException, webpush

    try:
        webpush(
            subscription_info={
                'endpoint': subscription.endpoint,
                'keys': {
                    'p256dh': subscription.p256dh_key,
                    'auth': subscription.auth_key,
                },
            },
            data=json.dumps(payload),
            vapid_private_key=settings.WEBPUSH_VAPID_PRIVATE_KEY,
            vapid_claims={'sub': settings.WEBPUSH_VAPID_SUBJECT},
            ttl=3600,
            timeout=10,
        )
        return True
    except WebPushException as exc:
        response = getattr(exc, 'response', None)
        status_code = getattr(response, 'status_code', None)
        if status_code in (404, 410):
            subscription.delete()
            logger.info('Assinatura push expirada removida para usuário %s', subscription.user_id)
        else:
            logger.warning('Falha ao enviar Web Push para usuário %s: %s', subscription.user_id, exc)
        return False
    except Exception:
        logger.exception('Erro inesperado ao enviar Web Push para usuário %s', subscription.user_id)
        return False