from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta
import secrets


class User(AbstractUser):
    """
    Modelo customizado de usuário para PlacarCerto Mozambique
    """
    email = models.EmailField(unique=True, verbose_name="Email")
    email_verified = models.BooleanField(default=False, verbose_name="Email Verificado")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Telefone")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    
    # Status Premium
    is_premium = models.BooleanField(default=False, verbose_name="É Premium?")
    premium_until = models.DateTimeField(null=True, blank=True, verbose_name="Premium Até")
    
    # Controle de análises
    daily_analysis_count = models.IntegerField(default=0, verbose_name="Análises Hoje")
    last_analysis_date = models.DateField(null=True, blank=True, verbose_name="Data Última Análise")
    bonus_analysis_credits = models.PositiveIntegerField(
        default=0,
        verbose_name="Créditos de Análise Bónus",
    )
    member_referral_code = models.CharField(
        max_length=12,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código de Convite de Membro",
    )
    
    # Notificações Push
    fcm_token = models.CharField(max_length=255, blank=True, verbose_name="FCM Token")
    push_enabled = models.BooleanField(default=True, verbose_name="Notificações Ativadas")
    
    # Estatísticas
    total_analyses = models.IntegerField(default=0, verbose_name="Total de Análises")
    successful_predictions = models.IntegerField(default=0, verbose_name="Previsões Corretas")

    # Anti-fraude / rastreio básico
    signup_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP de Cadastro")
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Último Login")
    device_fingerprint = models.CharField(max_length=255, blank=True, verbose_name="Fingerprint Dispositivo")
    last_device_fingerprint = models.CharField(max_length=255, blank=True, verbose_name="Último Fingerprint")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.member_referral_code:
            while True:
                code = secrets.token_hex(6).upper()
                if not type(self).objects.filter(member_referral_code=code).exists():
                    self.member_referral_code = code
                    break
            if kwargs.get('update_fields') is not None:
                update_fields = tuple(kwargs['update_fields'])
                if 'member_referral_code' not in update_fields:
                    kwargs['update_fields'] = update_fields + ('member_referral_code',)
        super().save(*args, **kwargs)
    
    @property
    def age(self):
        """Calcula a idade atual do usuário baseada na data de nascimento"""
        if not self.date_of_birth:
            return None
        
        today = date.today()
        age = today.year - self.date_of_birth.year
        
        # Ajustar se ainda não fez aniversário este ano
        if today.month < self.date_of_birth.month or \
           (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
            age -= 1
        
        return age
    
    def is_adult(self):
        """Verifica se o usuário é maior de 18 anos"""
        if not self.age:
            return False
        return self.age >= 18

    def get_daily_analysis_limit(self):
        from django.db.models import Q
        from apps.subscriptions.plan_config import get_plan_limit

        active_sub = self.subscriptions.filter(status='active').filter(
            Q(end_date__isnull=True) | Q(end_date__gt=timezone.now())
        ).first()
        if active_sub and active_sub.plan_slug:
            limit = get_plan_limit(active_sub.plan_slug)
            if limit is not None:
                return min(limit, get_plan_limit('premium_vitalicio'))

        if self.is_premium_active():
            from django.conf import settings
            return min(
                settings.PREMIUM_ANALYSIS_LIMIT,
                get_plan_limit('premium_vitalicio'),
            )
        return get_plan_limit('freemium')
    
    def is_premium_active(self):
        """Verifica se o usuário tem premium ativo"""
        if not self.is_premium:
            return False
        if not self.premium_until:
            return self.subscriptions.filter(
                status='active',
                plan_slug__in=('premium_vitalicio', 'premium_vitalicio_teste'),
                end_date__isnull=True,
            ).exists()
        return timezone.now() <= self.premium_until
    
    def can_analyze(self):
        """Verifica se o usuário pode fazer análises hoje"""
        today = timezone.now().date()
        
        # Reset contador se é um novo dia
        if self.last_analysis_date != today:
            self.daily_analysis_count = 0
            self.last_analysis_date = today
            self.save()
        
        limit = self.get_daily_analysis_limit()
        return self.daily_analysis_count < limit or self.bonus_analysis_credits > 0

    def increment_analysis_count(self):
        """Incrementa contador de análises"""
        today = timezone.now().date()
        if self.last_analysis_date != today:
            self.daily_analysis_count = 0
            self.last_analysis_date = today

        limit = self.get_daily_analysis_limit()
        if self.daily_analysis_count >= limit and self.bonus_analysis_credits > 0:
            self.bonus_analysis_credits -= 1

        self.daily_analysis_count += 1
        self.total_analyses = self.analyses.count()
        self.last_analysis_date = today
        self.save(update_fields=[
            'daily_analysis_count',
            'total_analyses',
            'last_analysis_date',
            'bonus_analysis_credits',
        ])
    
    def get_success_rate(self):
        """Calcula a taxa apenas sobre análises com resultado validado."""
        metrics = self.get_analysis_metrics()
        if not metrics['resolved']:
            return 0
        return round((metrics['correct'] / metrics['resolved']) * 100, 1)

    def get_analysis_metrics(self):
        """Devolve contagens a partir das análises persistidas, não de caches."""
        return self.analyses.aggregate(
            total=Count('id'),
            resolved=Count('id', filter=Q(is_correct__isnull=False)),
            correct=Count('id', filter=Q(is_correct=True)),
        )
