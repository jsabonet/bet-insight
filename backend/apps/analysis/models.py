from django.db import models
from django.conf import settings
from apps.matches.models import Match


class Analysis(models.Model):
    """Análise de uma partida"""
    
    CONFIDENCE_CHOICES = [
        (1, '⭐ Baixa'),
        (2, '⭐⭐ Média-Baixa'),
        (3, '⭐⭐⭐ Média'),
        (4, '⭐⭐⭐⭐ Alta'),
        (5, '⭐⭐⭐⭐⭐ Muito Alta'),
    ]
    
    PREDICTION_CHOICES = [
        ('home', 'Vitória Casa'),
        ('draw', 'Empate'),
        ('away', 'Vitória Visitante'),
    ]
    
    # Relacionamentos
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='analyses', verbose_name="Usuário")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='analyses', verbose_name="Partida")
    
    # Predição
    prediction = models.CharField(max_length=10, choices=PREDICTION_CHOICES, verbose_name="Predição")
    confidence = models.IntegerField(choices=CONFIDENCE_CHOICES, verbose_name="Confiança")
    
    # Probabilidades (%)
    home_probability = models.FloatField(verbose_name="Prob. Casa (%)")
    draw_probability = models.FloatField(verbose_name="Prob. Empate (%)")
    away_probability = models.FloatField(verbose_name="Prob. Visitante (%)")
    
    # Expected Goals
    home_xg = models.FloatField(null=True, blank=True, verbose_name="xG Casa")
    away_xg = models.FloatField(null=True, blank=True, verbose_name="xG Visitante")
    
    # Análise detalhada (JSON com breakdown por categoria)
    analysis_data = models.JSONField(verbose_name="Dados da Análise")
    
    # Raciocínio da IA
    reasoning = models.TextField(verbose_name="Raciocínio")
    key_factors = models.JSONField(verbose_name="Fatores Chave")  # Lista de strings
    
    # Validação (após o jogo)
    is_correct = models.BooleanField(null=True, blank=True, verbose_name="Predição Correta?")
    actual_result = models.CharField(max_length=10, blank=True, verbose_name="Resultado Real")
    
    # Controle
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado Em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado Em")
    
    class Meta:
        verbose_name = "Análise"
        verbose_name_plural = "Análises"
        ordering = ['-created_at']
        unique_together = [['user', 'match']]  # Um usuário só pode analisar uma partida uma vez
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['match', 'is_correct']),
        ]
    
    def __str__(self):
        return f"Análise de {self.user.email} - {self.match}"
    
    def validate_result(self):
        """Valida o resultado após a partida terminar"""
        if self.match.status == 'finished':
            actual = self.match.get_result()
            self.actual_result = actual
            self.is_correct = (self.prediction == actual)
            self.save()
            
            # Atualizar estatísticas do usuário
            if self.is_correct:
                self.user.successful_predictions += 1
                self.user.save()
    
    def get_confidence_stars(self):
        """Retorna estrelas visuais de confiança"""
        return '⭐' * self.confidence
