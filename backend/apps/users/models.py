from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    Modelo customizado de usuário para Bet Insight Mozambique
    """
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Telefone")
    
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
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
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
        
        # Premium tem limite maior
        if self.is_premium_active():
            from django.conf import settings
            return self.daily_analysis_count < settings.PREMIUM_ANALYSIS_LIMIT
        
        # Free tem 5 análises por dia
        from django.conf import settings
        return self.daily_analysis_count < settings.FREE_ANALYSIS_LIMIT
    
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
