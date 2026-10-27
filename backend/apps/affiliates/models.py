"""Modelos do sistema de afiliados PlacarCerto.

Estes modelos suportam a atribuição de vendas a afiliados via link de
indicação (`?ref=CODE`) ou código promocional, e o cálculo de comissões sobre
pagamentos concluídos (VPay). Posicionamento: infoproduto de análise
matemática e estatística — nunca um serviço de apostas.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta


class MemberReferral(models.Model):
    """Convite entre membros, recompensado após a primeira análise do convidado."""

    REWARD_STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('rewarded', 'Recompensado'),
        ('ineligible', 'Não elegível'),
    ]

    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member_referrals_sent',
    )
    invitee = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member_referral_received',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    rewarded_at = models.DateTimeField(null=True, blank=True)
    reward_status = models.CharField(
        max_length=12,
        choices=REWARD_STATUS_CHOICES,
        default='pending',
    )
    reward_ip_hash = models.CharField(max_length=64, null=True, blank=True, unique=True)
    reward_device_hash = models.CharField(max_length=64, null=True, blank=True, unique=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['inviter', 'rewarded_at'])]

    def __str__(self):
        return f'{self.inviter_id} invited {self.invitee_id}'


class Affiliate(models.Model):
    """Perfil de afiliado ligado (1:1) a um utilizador."""

    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('suspended', 'Suspenso'),
    ]
    TIER_CHOICES = [
        ('standard', 'Padrão'),
        ('vip', 'VIP'),
    ]
    PAYOUT_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('emola', 'e-Mola'),
        ('bank', 'Transferência Bancária'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='affiliate_profile',
        verbose_name="Usuário",
    )
    code = models.CharField(
        max_length=32, unique=True, verbose_name="Código de Indicação",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active',
        verbose_name="Status",
    )
    accepted_terms_version = models.CharField(max_length=20, blank=True, default='')
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    tier = models.CharField(
        max_length=20, choices=TIER_CHOICES, default='standard',
        verbose_name="Nível",
    )
    # Campos históricos mantidos por compatibilidade; as comissões atuais são fixas.
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.40, verbose_name="Comissão (1ª venda)",
    )
    renewal_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.10, verbose_name="Comissão (renovação)",
    )
    total_earned = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Total Ganho",
    )
    available_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Saldo Disponível",
    )
    pending_balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, verbose_name="Saldo Pendente",
    )
    payout_method = models.CharField(
        max_length=20, choices=PAYOUT_CHOICES, default='mpesa',
        verbose_name="Método de Pagamento",
    )
    payout_account = models.CharField(
        max_length=60, blank=True, verbose_name="Conta para Pagamento",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")

    class Meta:
        verbose_name = "Afiliado"
        verbose_name_plural = "Afiliados"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.code} - {self.user.username}"

    @property
    def is_active(self):
        return self.status == 'active'


class AffiliateTermsAcceptance(models.Model):
    affiliate = models.ForeignKey(
        Affiliate,
        on_delete=models.CASCADE,
        related_name='terms_acceptances',
    )
    terms_version = models.CharField(max_length=20)
    accepted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-accepted_at']
        constraints = [
            models.UniqueConstraint(
                fields=['affiliate', 'terms_version'],
                name='unique_affiliate_terms_acceptance',
            ),
        ]


class AffiliateReferral(models.Model):
    """Liga um utilizador indicado ao afiliado que o trouxe (atribuição)."""

    SOURCE_CHOICES = [
        ('link', 'Link de Indicação'),
        ('promo_code', 'Código Promocional'),
    ]

    affiliate = models.ForeignKey(
        Affiliate, on_delete=models.CASCADE, related_name='referrals',
        verbose_name="Afiliado",
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referred_by',
        verbose_name="Usuário Indicado",
    )
    code = models.CharField(max_length=32, blank=True, verbose_name="Código Usado")
    source = models.CharField(
        max_length=20, choices=SOURCE_CHOICES, default='link', verbose_name="Origem",
    )
    click_id = models.CharField(max_length=64, blank=True, verbose_name="Click ID")
    first_touch_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Primeiro Toque",
    )
    last_touch_at = models.DateTimeField(
        default=timezone.now, verbose_name="Último Toque",
    )
    converted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Convertido Em",
    )

    class Meta:
        verbose_name = "Indicação"
        verbose_name_plural = "Indicações"
        ordering = ['-first_touch_at']

    def __str__(self):
        return f"{self.user.email} <- {self.affiliate.code}"


class AffiliateCommission(models.Model):
    """Comissão gerada a partir de um pagamento concluído."""

    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('available', 'Disponível'),
        ('paid', 'Pago'),
        ('reversed', 'Revertido'),
    ]
    COMMISSION_TYPE_CHOICES = [
        ('percentage', 'Percentual (histórico)'),
        ('fixed', 'Fixa'),
    ]

    affiliate = models.ForeignKey(
        Affiliate, on_delete=models.CASCADE, related_name='commissions',
        verbose_name="Afiliado",
    )
    payment = models.OneToOneField(
        'subscriptions.Payment',
        on_delete=models.CASCADE,
        related_name='affiliate_commission',
        verbose_name="Pagamento",
    )
    referral = models.ForeignKey(
        AffiliateReferral, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='commissions', verbose_name="Indicação",
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Valor",
    )
    rate = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Taxa Aplicada",
    )
    commission_type = models.CharField(
        max_length=20, choices=COMMISSION_TYPE_CHOICES, default='percentage',
        verbose_name="Tipo de Comissão",
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status",
    )
    available_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Disponível Em",
    )
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="Pago Em")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")

    class Meta:
        verbose_name = "Comissão"
        verbose_name_plural = "Comissões"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['available_at']),
        ]

    def __str__(self):
        return f"{self.amount} MZN - {self.affiliate.code} ({self.status})"


class AffiliateWithdrawal(models.Model):
    """Pedido de levantamento com dados de pagamento e histórico de processamento."""

    STATUS_CHOICES = [
        ('requested', 'Solicitado'),
        ('processing', 'Em processamento'),
        ('paid', 'Pago'),
        ('rejected', 'Rejeitado'),
    ]

    affiliate = models.ForeignKey(
        Affiliate, on_delete=models.CASCADE, related_name='withdrawals',
        verbose_name="Afiliado",
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name="Valor",
    )
    fee_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Taxa de Saque (%)",
    )
    fee_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name="Taxa de Saque",
    )
    payout_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        verbose_name="Valor Líquido a Pagar",
    )
    payout_method = models.CharField(
        max_length=20, choices=Affiliate.PAYOUT_CHOICES,
        verbose_name="Método de Pagamento",
    )
    payout_account = models.CharField(max_length=60, verbose_name="Conta para Pagamento")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='requested',
        verbose_name="Status",
    )
    transaction_reference = models.CharField(
        max_length=100, blank=True, verbose_name="Referência da Transação",
    )
    rejection_reason = models.TextField(blank=True, verbose_name="Motivo da Rejeição")
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='processed_affiliate_withdrawals', verbose_name="Processado Por",
    )
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="Solicitado Em")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Processado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")

    class Meta:
        verbose_name = "Levantamento de Afiliado"
        verbose_name_plural = "Levantamentos de Afiliados"
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status', 'requested_at']),
            models.Index(fields=['affiliate', 'status']),
        ]

    def __str__(self):
        return f"{self.amount} MZN - {self.affiliate.code} ({self.status})"


class AffiliateWithdrawalAllocation(models.Model):
    """Parte de uma comissão reservada ou paga por um pedido de levantamento."""

    withdrawal = models.ForeignKey(
        AffiliateWithdrawal, on_delete=models.CASCADE, related_name='allocations',
        verbose_name="Levantamento",
    )
    commission = models.ForeignKey(
        AffiliateCommission, on_delete=models.CASCADE, related_name='withdrawal_allocations',
        verbose_name="Comissão",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor")

    class Meta:
        verbose_name = "Alocação de Levantamento"
        verbose_name_plural = "Alocações de Levantamento"
        constraints = [
            models.UniqueConstraint(
                fields=['withdrawal', 'commission'],
                name='unique_withdrawal_commission_allocation',
            ),
        ]


class AffiliateClick(models.Model):
    """Registo de cliques em links de afiliado (analítica/anti-fraude)."""

    affiliate = models.ForeignKey(
        Affiliate, on_delete=models.CASCADE, related_name='clicks',
        verbose_name="Afiliado",
    )
    code = models.CharField(max_length=32, verbose_name="Código")
    click_id = models.CharField(max_length=64, unique=True, verbose_name="Click ID")
    ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")

    class Meta:
        verbose_name = "Clique"
        verbose_name_plural = "Cliques"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.click_id}"


def default_available_at():
    """Data em que uma comissão pending passa a available."""
    days = int(getattr(settings, 'AFFILIATE_PENDING_DAYS', 14))
    return timezone.now() + timedelta(days=days)
