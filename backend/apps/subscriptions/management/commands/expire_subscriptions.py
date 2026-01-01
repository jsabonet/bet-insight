"""
Management Command para expirar assinaturas vencidas
Executar via cron: python manage.py expire_subscriptions
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.subscriptions.models import Subscription
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Expira assinaturas vencidas e atualiza status dos usuários'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Buscar assinaturas ativas que expiraram
        expired_subscriptions = Subscription.objects.filter(
            status='active',
            end_date__lte=now
        ).exclude(plan_slug='freemium')
        
        count = expired_subscriptions.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('Nenhuma assinatura expirada'))
            return
        
        self.stdout.write(f'Encontradas {count} assinaturas expiradas')
        
        # Processar cada assinatura
        for subscription in expired_subscriptions:
            user = subscription.user
            old_status = subscription.status
            
            # Marcar como expirada
            subscription.status = 'expired'
            subscription.save()
            
            # Atualizar usuário
            user.is_premium = False
            user.premium_until = None
            user.save()
            
            logger.info(
                f'Assinatura expirada: User {user.id} ({user.email}) '
                f'- Plan: {subscription.plan_slug}'
            )
            
            self.stdout.write(
                self.style.WARNING(
                    f'✓ {user.email} - {subscription.get_plan_display()} expirado'
                )
            )
            
            # TODO: Enviar email de expiração
            # send_subscription_expired_email(user, subscription)
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ {count} assinaturas expiradas com sucesso')
        )
