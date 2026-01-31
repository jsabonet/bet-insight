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


class DailyBet(models.Model):
    """Bilhete ou aposta gerada automaticamente pelo sistema"""
    
    BET_TYPE_CHOICES = [
        ('multiple', 'Bilhete Múltiplo'),
        ('value', 'Value Bet'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Aguardando'),
        ('won', 'Ganhou'),
        ('lost', 'Perdeu'),
        ('partial', 'Parcial'),  # Para bilhetes com algumas apostas certas
        ('cancelled', 'Cancelado'),  # Jogo adiado/cancelado
    ]
    
    # Identificação
    date = models.DateField(verbose_name="Data do Bilhete", db_index=True)
    bet_type = models.CharField(verbose_name="Tipo", max_length=20, choices=BET_TYPE_CHOICES)
    
    # Apostas incluídas (para bilhetes múltiplos ou value bets)
    selections = models.JSONField(verbose_name="Seleções", help_text='Lista de apostas do bilhete')
    # Estrutura: [
    #   {
    #     'match_id': 123,
    #     'match': 'Man Utd vs Liverpool',
    #     'league': 'Premier League',
    #     'date': '2026-01-30T20:00:00Z',
    #     'market': 'home_win',
    #     'pick': 'Man Utd',
    #     'probability': 0.65,
    #     'odd': 1.45,
    #     'fair_odd': 1.54,
    #     'ev_pct': 6.2,
    #     'score': 0.89,
    #     'result': null  # preenchido após jogo: 'won', 'lost', 'cancelled'
    #   },
    #   ...
    # ]
    
    # Odds
    total_odd = models.DecimalField(verbose_name='Odd Total', max_digits=10, decimal_places=2)
    fair_odd = models.DecimalField(verbose_name='Odd Justa', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Probabilidade
    combined_probability = models.FloatField(verbose_name='Prob. Combinada', help_text='Para bilhetes: produto das probabilidades')
    expected_value = models.FloatField(verbose_name='EV %', help_text='Expected Value em porcentagem')
    
    # Stake sugerido
    suggested_stake = models.FloatField(verbose_name='Stake Sugerido (unidades)', default=1.0)
    
    # Resultado
    status = models.CharField(verbose_name='Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    actual_result = models.CharField(verbose_name='Resultado Real', max_length=200, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(verbose_name='Criado em', auto_now_add=True)
    validated_at = models.DateTimeField(verbose_name='Validado em', null=True, blank=True)
    
    # Métricas
    is_validated = models.BooleanField(verbose_name='Validado', default=False)
    
    class Meta:
        verbose_name = 'Aposta Diária'
        verbose_name_plural = 'Apostas Diárias'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date', 'bet_type']),
            models.Index(fields=['status']),
            models.Index(fields=['is_validated', 'date']),
        ]
    
    def __str__(self):
        return f"{self.get_bet_type_display()} - {self.date} ({self.get_status_display()})"
    
    def validate_result(self):
        """Valida resultado do bilhete após jogos finalizarem"""
        from django.utils import timezone
        from apps.matches.models import Match
        
        # Verificar se todos os jogos das selections finalizaram
        match_ids = [s['match_id'] for s in self.selections]
        matches = Match.objects.filter(id__in=match_ids)
        
        # Mapear matches por ID para acesso rápido
        matches_dict = {m.id: m for m in matches}
        
        all_finished = True
        any_cancelled = False
        
        for selection in self.selections:
            match_id = selection['match_id']
            match = matches_dict.get(match_id)
            
            if not match:
                continue
            
            # Verificar se jogo foi cancelado/adiado
            if match.status in ['cancelled', 'postponed', 'abandoned']:
                selection['result'] = 'cancelled'
                any_cancelled = True
                continue
            
            # Verificar se jogo finalizou
            if match.status != 'finished':
                all_finished = False
                continue
            
            # Validar resultado baseado no market
            market = selection['market']
            match_result = match.get_result()  # 'home', 'draw', 'away'
            
            # Mercados principais
            if market == 'home_win':
                selection['result'] = 'won' if match_result == 'home' else 'lost'
            elif market == 'away_win':
                selection['result'] = 'won' if match_result == 'away' else 'lost'
            elif market == 'draw':
                selection['result'] = 'won' if match_result == 'draw' else 'lost'
            elif market == 'double_chance_1x':
                selection['result'] = 'won' if match_result in ['home', 'draw'] else 'lost'
            elif market == 'double_chance_x2':
                selection['result'] = 'won' if match_result in ['draw', 'away'] else 'lost'
            elif market == 'double_chance_12':
                selection['result'] = 'won' if match_result in ['home', 'away'] else 'lost'
            
            # Mercados de gols
            elif market.startswith('over_'):
                threshold = float(market.split('_')[1])
                total_goals = (match.home_score or 0) + (match.away_score or 0)
                selection['result'] = 'won' if total_goals > threshold else 'lost'
            elif market.startswith('under_'):
                threshold = float(market.split('_')[1])
                total_goals = (match.home_score or 0) + (match.away_score or 0)
                selection['result'] = 'won' if total_goals < threshold else 'lost'
            elif market == 'btts_yes':
                selection['result'] = 'won' if (match.home_score or 0) > 0 and (match.away_score or 0) > 0 else 'lost'
            elif market == 'btts_no':
                selection['result'] = 'won' if (match.home_score or 0) == 0 or (match.away_score or 0) == 0 else 'lost'
            
            # Casa gols
            elif market.startswith('home_over_'):
                threshold = float(market.split('_')[-1])
                selection['result'] = 'won' if (match.home_score or 0) > threshold else 'lost'
            elif market.startswith('home_under_'):
                threshold = float(market.split('_')[-1])
                selection['result'] = 'won' if (match.home_score or 0) < threshold else 'lost'
            
            # Fora gols
            elif market.startswith('away_over_'):
                threshold = float(market.split('_')[-1])
                selection['result'] = 'won' if (match.away_score or 0) > threshold else 'lost'
            elif market.startswith('away_under_'):
                threshold = float(market.split('_')[-1])
                selection['result'] = 'won' if (match.away_score or 0) < threshold else 'lost'
            
            else:
                # Market não suportado - marcar como não validado
                selection['result'] = None
        
        # Se nem todos jogos finalizaram, aguardar
        if not all_finished:
            return False
        
        # Se algum jogo foi cancelado, marcar bilhete como cancelado
        if any_cancelled:
            self.status = 'cancelled'
            self.actual_result = 'Jogo(s) cancelado(s) ou adiado(s)'
        else:
            # Determinar status do bilhete
            results = [s.get('result') for s in self.selections]
            
            if self.bet_type == 'multiple':
                # Bilhete múltiplo: TODAS apostas devem ganhar
                if all(r == 'won' for r in results):
                    self.status = 'won'
                    self.actual_result = f"Bilhete ganhou! {len(results)}/{len(results)} acertos"
                else:
                    won_count = sum(1 for r in results if r == 'won')
                    if won_count > 0:
                        self.status = 'partial'
                        self.actual_result = f"{won_count}/{len(results)} acertos"
                    else:
                        self.status = 'lost'
                        self.actual_result = f"Bilhete perdeu - 0/{len(results)} acertos"
            else:
                # Value bet individual
                result = results[0]
                if result == 'won':
                    self.status = 'won'
                    self.actual_result = 'Aposta ganhou!'
                else:
                    self.status = 'lost'
                    self.actual_result = 'Aposta perdeu'
        
        # Marcar como validado
        self.is_validated = True
        self.validated_at = timezone.now()
        self.save()
        
        return True
    
    def get_roi(self):
        """Calcula ROI da aposta (apenas se validada)"""
        if not self.is_validated:
            return None
        
        stake = self.suggested_stake
        
        if self.status == 'won':
            profit = (float(self.total_odd) * stake) - stake
            return (profit / stake) * 100
        elif self.status == 'lost':
            return -100.0
        elif self.status == 'cancelled':
            return 0.0
        else:
            return None
