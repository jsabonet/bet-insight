"""
Management Command para remover todas as assinaturas dos usuários

Uso:
  python manage.py clear_subscriptions

Opcional:
  --cancel  Cancela em vez de deletar (mantém registro)
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.subscriptions.models import Subscription
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Remove TODAS as assinaturas (não-freemium) dos usuários para reset de ambiente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cancel',
            action='store_true',
            help='Cancela assinaturas em vez de deletar'
        )

    def handle(self, *args, **options):
        cancel_only = options.get('cancel', False)

        # Buscar todas as assinaturas (exceto freemium)
        subs = Subscription.objects.exclude(plan_slug='freemium')
        total = subs.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS('Nenhuma assinatura premium encontrada para remover'))
            return

        self.stdout.write(f'Encontradas {total} assinatura(s) para processamento')

        # Processar
        processed = 0
        for sub in subs.iterator():
            user: User = sub.user

            if cancel_only:
                # Cancela e mantém registro
                sub.cancel()
                action = 'cancelada'
            else:
                # Deleta registro
                sub.delete()
                action = 'deletada'

            # Atualizar usuário
            user.is_premium = False
            user.premium_until = None
            user.save(update_fields=['is_premium', 'premium_until'])

            logger.info(f'Assinatura {action}: User {user.id} ({user.email}) - Plano {sub.plan_slug}')
            self.stdout.write(self.style.WARNING(f'✓ {user.email} - assinatura {action}'))
            processed += 1

        self.stdout.write(self.style.SUCCESS(f'\n✓ {processed} assinatura(s) processada(s) com sucesso'))