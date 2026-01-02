from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Subscription(models.Model):
    """Assinatura Premium"""
    
    STATUS_CHOICES = [
        ('active', 'Ativa'),
        ('expired', 'Expirada'),
        ('cancelled', 'Cancelada'),
    ]
    
    PLAN_CHOICES = [
        ('monthly', 'Mensal - 499 MZN'),
        ('quarterly', 'Trimestral - 1299 MZN'),
        ('yearly', 'Anual - 4499 MZN'),
    ]
    
    # Relacionamento
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions', verbose_name="Usuário")
    
    # Plano
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, verbose_name="Plano")
    plan_slug = models.CharField(max_length=50, null=True, blank=True, verbose_name="Plan Slug")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    
    # Período
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Data Início")
    end_date = models.DateTimeField(verbose_name="Data Fim")
    
    # Controle de renovação
    auto_renew = models.BooleanField(default=True, verbose_name="Renovação Automática")
    cancelled_at = models.DateTimeField(null=True, blank=True, verbose_name="Cancelado Em")
    
    # Pagamento
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Pago")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")
    
    class Meta:
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['end_date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_plan_display()} ({self.status})"
    
    def save(self, *args, **kwargs):
        """Calcula end_date baseado no plano"""
        if not self.end_date:
            # Preferir duração derivada do plan_slug configurado
            try:
                from .plan_config import get_plan_duration
                if self.plan_slug:
                    duration_days = get_plan_duration(self.plan_slug)
                    if duration_days:
                        self.end_date = self.start_date + timedelta(days=duration_days)
            except Exception:
                # Fallback silencioso para lógica antiga
                pass
            # Se ainda não definimos end_date, usar mapeamento por plan (choices)
            if not self.end_date:
                if self.plan == 'monthly':
                    self.end_date = self.start_date + timedelta(days=30)
                elif self.plan == 'quarterly':
                    self.end_date = self.start_date + timedelta(days=90)
                elif self.plan == 'yearly':
                    self.end_date = self.start_date + timedelta(days=365)
        
        super().save(*args, **kwargs)
        
        # Atualizar status premium do usuário
        self.update_user_premium_status()
    
    def update_user_premium_status(self):
        """Atualiza status premium do usuário baseado nas assinaturas ativas."""
        # Encontrar qualquer assinatura ativa atual do usuário
        active = self.user.subscriptions.filter(status='active', end_date__gt=timezone.now()).order_by('-end_date').first()
        if active:
            self.user.is_premium = True
            self.user.premium_until = active.end_date
        else:
            self.user.is_premium = False
            self.user.premium_until = None
        try:
            self.user.save(update_fields=['is_premium', 'premium_until'])
        except Exception:
            self.user.save()
    
    def is_active(self):
        """Verifica se assinatura está ativa"""
        return self.status == 'active' and self.end_date > timezone.now()
    
    def cancel(self):
        """Cancela a assinatura"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.auto_renew = False
        self.save()


class Payment(models.Model):
    """Registro de pagamento M-Pesa"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('completed', 'Completo'),
        ('failed', 'Falhou'),
        ('refunded', 'Reembolsado'),
    ]
    
    # Relacionamentos
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments', verbose_name="Usuário")
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments', verbose_name="Assinatura")
    
    # Informações de pagamento
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    currency = models.CharField(max_length=3, default='MZN', verbose_name="Moeda")
    phone_number = models.CharField(max_length=15, verbose_name="Telefone")
    
    # M-Pesa
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name="ID Transação")
    mpesa_reference = models.CharField(max_length=100, blank=True, verbose_name="Referência M-Pesa")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    
    # Metadata
    payment_method = models.CharField(max_length=50, default='mpesa', verbose_name="Método")
    metadata = models.JSONField(null=True, blank=True, verbose_name="Metadata")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completado Em")
    
    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} MZN ({self.status})"
    
    def complete_payment(self):
        """Marca pagamento como completo e ativa assinatura"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        
        # Ativar assinatura se existir
        if self.subscription:
            self.subscription.status = 'active'
            self.subscription.save()
