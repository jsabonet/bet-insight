from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta


class User(AbstractUser):
    """
    Modelo customizado de usuário para PlacarCerto Mozambique
    """
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Telefone")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    
    # Status Premium
    is_premium = models.BooleanField(default=False, verbose_name="É Premium?")
    premium_until = models.DateTimeField(null=True, blank=True, verbose_name="Premium Até")
    
    # Controle de análises
    daily_analysis_count = models.IntegerField(default=0, verbose_name="Análises Hoje")
    last_analysis_date = models.DateField(null=True, blank=True, verbose_name="Data Última Análise")
    
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
    
    def is_premium_active(self):
        """Verifica se o usuário tem premium ativo"""
        if not self.is_premium:
            return False
        if not self.premium_until:
            return False
        return timezone.now() <= self.premium_until
    
    def can_analyze(self):
        """Verifica se o usuário pode fazer análises hoje"""
        today = timezone.now().date()
        
        # Reset contador se é um novo dia
        if self.last_analysis_date != today:
            self.daily_analysis_count = 0
            self.last_analysis_date = today
            self.save()
        
        # Definir limite diário com base na assinatura ativa (plan_slug)
        from apps.subscriptions.plan_config import get_plan_limit
        limit = None
        try:
            active_sub = self.subscriptions.filter(status='active', end_date__gt=timezone.now()).first()
            if active_sub and active_sub.plan_slug:
                limit = get_plan_limit(active_sub.plan_slug)
        except Exception:
            limit = None

        if limit is None:
            # Fallback para configurações existentes
            if self.is_premium_active():
                from django.conf import settings
                limit = settings.PREMIUM_ANALYSIS_LIMIT
            else:
                limit = get_plan_limit('freemium')

        return self.daily_analysis_count < limit
    
    def increment_analysis_count(self):
        """Incrementa contador de análises"""
        self.daily_analysis_count += 1
        self.total_analyses += 1
        self.last_analysis_date = timezone.now().date()
        self.save()
    
    def get_success_rate(self):
        """Calcula taxa de acerto"""
        if self.total_analyses == 0:
            return 0
        return round((self.successful_predictions / self.total_analyses) * 100, 1)
