"""Lógica de negócio do sistema de afiliados.

Centraliza a resolução de códigos de afiliado, a criação (idempotente) de
comissões quando um pagamento é concluído e a gestão de saldos.
"""
import logging
import random
import string
import hashlib
import hmac
from decimal import Decimal

from django.conf import settings
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Affiliate, AffiliateReferral, AffiliateCommission, MemberReferral

logger = logging.getLogger(__name__)


def get_setting(name, default):
    return getattr(settings, name, default)


def excluded_plans():
    """Planos que NÃO geram comissão (ex.: 'teste')."""
    value = get_setting(
        'AFFILIATE_EXCLUDED_PLANS',
        ['teste', 'premium_vitalicio_teste'],
    )
    if isinstance(value, str):
        value = [p.strip() for p in value.split(',') if p.strip()]
    return set(value) | {'teste', 'premium_vitalicio_teste'}


def resolve_affiliate_by_code(code):
    """Devolve um Affiliate ativo para um código, ou None."""
    if not code:
        return None
    return Affiliate.objects.filter(code__iexact=code, status='active').first()


def code_to_string(code):
    """Normaliza um código (trim + uppercase)."""
    return (code or '').strip().upper()


def generate_unique_code(base):
    """Gera um código único a partir de uma base (ex.: username).

    Inclui sempre dígitos numéricos para evitar códigos iguais entre
    utilizadores com o mesmo nome (ex.: 'joao' -> 'JOAO4821').
    """
    base = (base or 'AFF').upper()
    base = ''.join(ch for ch in base if ch.isalnum())[:8] or 'AFF'

    # Código com 4 dígitos aleatórios; em caso de colisão, tenta novamente.
    for _ in range(50):
        candidate = f"{base}{''.join(random.choices(string.digits, k=4))}"
        if not Affiliate.objects.filter(code=candidate).exists():
            return candidate

    # Fallback determinístico (extremamente raro).
    counter = 1
    code = f"{base}{counter}"
    while Affiliate.objects.filter(code=code).exists():
        counter += 1
        code = f"{base}{counter}"
    return code


def assign_referral(user, code, source='link', click_id=''):
    """Cria/atualiza o vínculo de indicação de um utilizador (idempotente).

    Retorna o AffiliateReferral (ou None se o código for inválido/inativo).
    Nunca permite auto-indicação.
    """
    code = code_to_string(code)
    affiliate = resolve_affiliate_by_code(code)
    if not affiliate:
        return None
    if affiliate.user_id == user.id:
        return None

    referral, created = AffiliateReferral.objects.get_or_create(
        user=user,
        defaults={
            'affiliate': affiliate,
            'code': code,
            'source': source,
            'click_id': click_id or '',
        },
    )
    if not created:
        # Atualizar o último afiliado (last-click) apenas se for outro afiliado.
        referral.affiliate = affiliate
        referral.code = code
        if source == 'promo_code' or referral.source != 'promo_code':
            # Código promocional tem prioridade e não pode ser "sobrescrito"
            # por um link posterior.
            referral.source = source
        if click_id:
            referral.click_id = click_id
        referral.last_touch_at = timezone.now()
        referral.save(update_fields=['affiliate', 'code', 'source', 'click_id', 'last_touch_at'])
    else:
        # Nova conta criada com o link/código do afiliado: notifica por email.
        _notify_new_referral(referral)
        transaction.on_commit(
            lambda: _enqueue_new_referral_push(referral.pk, affiliate.user_id)
        )
    return referral


def assign_member_referral(user, code):
    """Regista um convite entre membros sem misturar o programa de afiliados."""
    code = code_to_string(code)
    if not code:
        return None

    from django.contrib.auth import get_user_model
    User = get_user_model()
    inviter = User.objects.filter(member_referral_code__iexact=code).first()
    if inviter is None or inviter.pk == user.pk:
        return None

    referral, _ = MemberReferral.objects.get_or_create(
        invitee=user,
        defaults={'inviter': inviter},
    )
    return referral


def reward_member_referral_for_first_analysis(user):
    """Concede cinco análises uma vez, limitando a uma recompensa por IP/dispositivo."""
    from django.contrib.auth import get_user_model
    from apps.notifications.models import Notification
    from apps.users.models import User as UserModel

    User = get_user_model()
    if user.total_analyses != 1:
        return False

    try:
        with transaction.atomic():
            referral = (
                MemberReferral.objects.select_for_update()
                .filter(invitee=user, reward_status='pending')
                .first()
            )
            if referral is None:
                return False

            inviter = User.objects.select_for_update().get(pk=referral.inviter_id)
            invitee = User.objects.select_for_update().get(pk=referral.invitee_id)

            ip = invitee.signup_ip
            fingerprint = invitee.device_fingerprint.strip()
            shared_ip = bool(
                ip and UserModel.objects.filter(signup_ip=ip).exclude(pk=invitee.pk).exists()
            )
            shared_device = bool(
                fingerprint
                and UserModel.objects.filter(device_fingerprint=fingerprint)
                .exclude(pk=invitee.pk)
                .exists()
            )
            if not ip or shared_ip or shared_device:
                referral.reward_status = 'ineligible'
                referral.save(update_fields=['reward_status'])
                return False

            secret = settings.SECRET_KEY.encode('utf-8')
            ip_hash = hmac.new(secret, f'ip:{ip}'.encode('utf-8'), hashlib.sha256).hexdigest() if ip else None
            device_hash = (
                hmac.new(secret, f'device:{fingerprint}'.encode('utf-8'), hashlib.sha256).hexdigest()
                if fingerprint else None
            )
            referral.reward_ip_hash = ip_hash
            referral.reward_device_hash = device_hash
            referral.reward_status = 'rewarded'
            referral.rewarded_at = timezone.now()
            referral.save(update_fields=[
                'reward_ip_hash',
                'reward_device_hash',
                'reward_status',
                'rewarded_at',
            ])

            inviter.bonus_analysis_credits += 5
            invitee.bonus_analysis_credits += 5
            inviter.save(update_fields=['bonus_analysis_credits'])
            invitee.save(update_fields=['bonus_analysis_credits'])

            for recipient in (inviter, invitee):
                Notification.objects.get_or_create(
                    user=recipient,
                    event_key=f'member_referral_reward_{referral.pk}',
                    defaults={
                        'title': 'Convite concluído: +5 análises',
                        'body': 'O seu convite concluiu a primeira análise. Recebeu 5 análises bónus.',
                        'url': '/member-referrals',
                    },
                )
    except IntegrityError:
        MemberReferral.objects.filter(invitee=user, reward_status='pending').update(
            reward_status='ineligible',
        )
        return False

    return True


def _enqueue_new_referral_push(referral_id, affiliate_user_id):
    from apps.notifications.tasks import enqueue_affiliate_push
    enqueue_affiliate_push(
        affiliate_user_id,
        'referral_registered',
        str(referral_id),
        'Nova referência registada',
        'Um novo utilizador registou-se através do seu link de afiliado.',
    )


def _notify_new_referral(referral):
    """Envia email ao afiliado quando alguém cria conta com o seu link."""
    from apps.notifications.models import Notification

    Notification.objects.get_or_create(
        user=referral.affiliate.user,
        event_key=f'affiliate_referral_registered_{referral.pk}',
        defaults={
            'title': 'Nova indicação registada',
            'body': 'Uma nova conta registou-se através do seu link de afiliado.',
            'url': '/affiliate',
        },
    )
    try:
        from .emails import send_new_referral_email
        send_new_referral_email(referral)
    except Exception as exc:
        logger.exception('Erro ao enviar email de nova indicação: %s', exc)


def get_payment_affiliate(payment):
    """Lê o código de afiliado gravado no metadata do pagamento."""
    metadata = payment.metadata or {}
    return metadata.get('affiliate_code'), metadata.get('affiliate_id'), metadata.get('referral_source')


def create_commission_if_applicable(payment):
    """Cria a comissão para um pagamento concluído (idempotente).

    Deve ser chamada após `mark_payment_completed(payment)`. Só gera comissão
    na primeira venda do plano (excluindo planos como 'teste') e quando o
    pagamento tem um código de afiliado válido.
    """
    if payment.status != 'completed':
        return None

    # Idempotência: OneToOne com o pagamento garante uma única comissão.
    if hasattr(payment, 'affiliate_commission'):
        return payment.affiliate_commission

    affiliate_code, affiliate_id, source = get_payment_affiliate(payment)
    code = code_to_string(affiliate_code)

    affiliate = None
    if affiliate_id:
        affiliate = Affiliate.objects.filter(id=affiliate_id, status='active').first()
    if affiliate is None and code:
        affiliate = resolve_affiliate_by_code(code)
    if affiliate is None:
        return None

    # Anti-fraude: auto-compra não gera comissão.
    if affiliate.user_id == payment.user_id:
        return None

    # Planos excluídos (ex.: teste de 1 MZN) não geram comissão.
    plan_slug = (payment.metadata or {}).get('plan') or ''
    if plan_slug in excluded_plans():
        return None

    plan_price = Decimal(str(payment.amount or 0))
    if plan_price <= 0:
        return None

    referral = None
    if payment.user_id:
        referral = AffiliateReferral.objects.filter(user_id=payment.user_id).first()

    amount = Decimal(str(get_setting('AFFILIATE_FIXED_COMMISSION', 100))).quantize(
        Decimal('0.01')
    )
    rate = Decimal('0.00')

    if amount <= 0:
        return None

    if referral and referral.converted_at is None:
        referral.converted_at = timezone.now()
        referral.save(update_fields=['converted_at'])

    with transaction.atomic():
        commission, created = AffiliateCommission.objects.get_or_create(
            payment=payment,
            defaults={
                'affiliate': affiliate,
                'referral': referral,
                'amount': amount,
                'rate': rate,
                'commission_type': 'fixed',
                'status': 'pending',
                'available_at': timezone.now() + timezone.timedelta(
                    days=int(get_setting('AFFILIATE_PENDING_DAYS', 14))
                ),
            },
        )

    if created:
        _update_affiliate_balances(affiliate)
        logger.info(
            'Comissão fixa criada: %s MZN para %s via pagamento %s',
            amount, affiliate.code, payment.transaction_id,
        )
        # Notificar o afiliado por email (não bloqueia a criação da comissão).
        try:
            from .emails import send_commission_earned_email
            send_commission_earned_email(commission)
        except Exception as exc:
            logger.exception('Erro ao enviar email de comissão ganha: %s', exc)
        transaction.on_commit(
            lambda: _enqueue_commission_push(commission.pk, affiliate.user_id, 'commission_created')
        )

    return commission


def _enqueue_commission_push(commission_id, affiliate_user_id, event_type):
    commission = AffiliateCommission.objects.filter(pk=commission_id).first()
    if not commission:
        logger.warning('Comissão %s não foi encontrada ao preparar push de afiliado.', commission_id)
        return
    from apps.notifications.tasks import enqueue_affiliate_push
    descriptions = {
        'commission_created': ('Nova comissão gerada', 'Uma venda foi confirmada e a comissão está pendente.'),
        'commission_available': ('Comissão disponível', 'Uma comissão ficou disponível para levantamento.'),
        'commission_paid': ('Comissão paga', 'Uma comissão foi marcada como paga.'),
    }
    title, body = descriptions[event_type]
    enqueue_affiliate_push(
        affiliate_user_id,
        event_type,
        str(commission_id),
        title,
        f'{body} Valor: {commission.amount} MZN.',
    )


def _update_affiliate_balances(affiliate):
    """Recalcula os saldos (pending/available/total) do afiliado."""
    from django.db.models import Sum
    from .models import AffiliateWithdrawalAllocation

    pending = affiliate.commissions.filter(status='pending').aggregate(s=Sum('amount'))['s'] or 0
    available = affiliate.commissions.filter(status='available').aggregate(s=Sum('amount'))['s'] or 0
    reserved = AffiliateWithdrawalAllocation.objects.filter(
        withdrawal__affiliate=affiliate,
        withdrawal__status__in=('requested', 'processing', 'paid'),
        commission__status='available',
    ).aggregate(s=Sum('amount'))['s'] or 0
    total = affiliate.commissions.exclude(status='reversed').aggregate(s=Sum('amount'))['s'] or 0
    affiliate.pending_balance = pending
    affiliate.available_balance = max(available - reserved, 0)
    affiliate.total_earned = total
    affiliate.save(update_fields=['pending_balance', 'available_balance', 'total_earned', 'updated_at'])


def reverse_commission_for_payment(payment):
    """Reverte a comissão associada quando o pagamento é reembolsado."""
    commission = getattr(payment, 'affiliate_commission', None)
    if not commission or commission.status == 'reversed':
        return
    commission.status = 'reversed'
    commission.save(update_fields=['status', 'updated_at'])
    _update_affiliate_balances(commission.affiliate)
    logger.info(
        'Comissão revertida: %s para %s (pagamento %s)',
        commission.amount, commission.affiliate.code, payment.transaction_id,
    )
