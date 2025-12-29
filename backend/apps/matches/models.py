from django.db import models
from django.utils import timezone


class League(models.Model):
    """Liga/Campeonato"""
    name = models.CharField(max_length=100, verbose_name="Nome")
    country = models.CharField(max_length=50, verbose_name="País")
    logo = models.URLField(blank=True, verbose_name="Logo")
    
    # IDs externos das APIs
    api_football_id = models.IntegerField(null=True, blank=True, verbose_name="API Football ID")
    football_data_id = models.IntegerField(null=True, blank=True, verbose_name="Football Data ID")
    
    # Configurações
    is_active = models.BooleanField(default=True, verbose_name="Ativa?")
    priority = models.IntegerField(default=0, verbose_name="Prioridade")  # Maior = mais importante
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")
    
    class Meta:
        verbose_name = "Liga"
        verbose_name_plural = "Ligas"
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['api_football_id']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.country})"


class Team(models.Model):
    """Time/Equipe"""
    name = models.CharField(max_length=100, verbose_name="Nome")
    logo = models.URLField(blank=True, verbose_name="Logo")
    country = models.CharField(max_length=50, blank=True, verbose_name="País")
    
    # IDs externos das APIs
    api_football_id = models.IntegerField(null=True, blank=True, verbose_name="API Football ID")
    football_data_id = models.IntegerField(null=True, blank=True, verbose_name="Football Data ID")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")
    
    class Meta:
        verbose_name = "Time"
        verbose_name_plural = "Times"
        ordering = ['name']
        indexes = [
            models.Index(fields=['api_football_id']),
        ]
    
    def __str__(self):
        return self.name


class Match(models.Model):
    """Partida de futebol"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Agendada'),
        ('live', 'Ao Vivo'),
        ('finished', 'Finalizada'),
        ('postponed', 'Adiada'),
        ('cancelled', 'Cancelada'),
    ]
    
    # Relacionamentos
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name='matches', verbose_name="Liga")
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches', verbose_name="Time Casa")
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches', verbose_name="Time Visitante")
    
    # Informações da partida
    match_date = models.DateTimeField(verbose_name="Data/Hora")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', verbose_name="Status")
    round = models.CharField(max_length=50, blank=True, verbose_name="Rodada")
    
    # Placares
    home_score = models.IntegerField(null=True, blank=True, verbose_name="Gols Casa")
    away_score = models.IntegerField(null=True, blank=True, verbose_name="Gols Visitante")
    
    # IDs externos
    api_football_id = models.IntegerField(null=True, blank=True, unique=True, verbose_name="API Football ID")
    football_data_id = models.IntegerField(null=True, blank=True, unique=True, verbose_name="Football Data ID")
    
    # Cache de estatísticas (JSON)
    stats_cache = models.JSONField(null=True, blank=True, verbose_name="Cache de Estatísticas")
    last_stats_update = models.DateTimeField(null=True, blank=True, verbose_name="Última Atualização Stats")
    
    # Controle
    is_analysis_available = models.BooleanField(default=True, verbose_name="Análise Disponível?")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")
    
    class Meta:
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"
        ordering = ['-match_date']
        indexes = [
            models.Index(fields=['match_date', 'status']),
            models.Index(fields=['league', 'match_date']),
            models.Index(fields=['api_football_id']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(home_team=models.F('away_team')),
                name='different_teams'
            )
        ]
    
    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.match_date.strftime('%d/%m/%Y')}"
    
    def is_upcoming(self):
        """Verifica se a partida é futura"""
        return self.status == 'scheduled' and self.match_date > timezone.now()
    
    def get_result(self):
        """Retorna resultado da partida"""
        if self.status != 'finished' or self.home_score is None:
            return None
        
        if self.home_score > self.away_score:
            return 'home'
        elif self.away_score > self.home_score:
            return 'away'
        return 'draw'
