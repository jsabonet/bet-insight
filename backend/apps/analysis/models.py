import hashlib
import json
import re

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
    
    def validate_result(self, results_map=None):
        """
        Valida o bilhete apenas quando todos os jogos terminaram.

        A validação é deliberadamente estrita: se falta o resultado de uma
        perna, o bilhete continua pendente em vez de ser marcado como
        perdido/parcial com dados incompletos.
        """
        from django.utils import timezone
        from .services.match_result_sync import (
            build_results_map,
            evaluate_market_result,
            format_score,
            get_result_info,
        )

        selections = list(self.selections or [])
        if not selections:
            return False

        if results_map is None:
            results_map = build_results_map(selections, fallback_date=self.date)

        any_cancelled = False
        all_resolved = True

        for selection in selections:
            info = get_result_info(results_map, selection)

            if info is None:
                selection['result'] = None
                all_resolved = False
                continue

            status = info.get('status')

            if status in ('cancelled', 'postponed', 'abandoned'):
                selection['result'] = 'cancelled'
                selection['final_score'] = format_score(info)
                any_cancelled = True
                continue

            if status != 'finished':
                selection['result'] = None
                all_resolved = False
                continue

            home_score = info.get('home_score')
            away_score = info.get('away_score')
            if home_score is None or away_score is None:
                selection['result'] = None
                all_resolved = False
                continue

            if home_score > away_score:
                match_result = 'home'
            elif away_score > home_score:
                match_result = 'away'
            else:
                match_result = 'draw'

            result = evaluate_market_result(
                selection.get('market'),
                match_result,
                home_score,
                away_score,
            )

            if result is None:
                selection['result'] = None
                all_resolved = False
                continue

            selection['result'] = result
            selection['final_score'] = format_score(info)
            selection['result_source'] = 'api-football'
            selection['settled_at'] = timezone.now().isoformat()

        # Sem todos os resultados não há validação possível.
        if not all_resolved:
            self.selections = selections
            self.save(update_fields=['selections'])
            return False

        if any_cancelled:
            self.status = 'cancelled'
            self.actual_result = 'Jogo(s) cancelado(s) ou adiado(s)'
        else:
            results = [s.get('result') for s in selections]

            if self.bet_type == 'multiple':
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
                result = results[0] if results else None
                if result == 'won':
                    self.status = 'won'
                    self.actual_result = 'Aposta ganhou!'
                else:
                    self.status = 'lost'
                    self.actual_result = 'Aposta perdeu'

        self.selections = selections
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


class SocialProofTicket(models.Model):
    """
    Snapshot imutável de um bilhete usado para prova social (apenas admin).

    O snapshot existe para que a imagem exportada continue verificável mesmo
    que os DailyBet de origem sejam regenerados ou apagados.
    """

    KIND_CHOICES = [
        ('simulation', 'Simulação Pós-Jogo'),
    ]

    STATUS_CHOICES = [
        ('candidate', 'Candidato'),
        ('approved', 'Aprovado'),
        ('exported', 'Exportado'),
        ('discarded', 'Descartado'),
    ]

    date = models.DateField(verbose_name='Data de Referência', db_index=True)
    kind = models.CharField(max_length=24, choices=KIND_CHOICES, verbose_name='Tipo')
    status = models.CharField(
        max_length=16, choices=STATUS_CHOICES, default='candidate', verbose_name='Estado'
    )

    ticket_code = models.CharField(max_length=40, unique=True, verbose_name='Código do Bilhete')
    reserve_code = models.CharField(max_length=20, blank=True, verbose_name='Código de Reserva')

    legs = models.JSONField(default=list, verbose_name='Seleções')
    source_bet_ids = models.JSONField(default=list, blank=True, verbose_name='Bilhetes de Origem')

    total_odd = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Odd Total'
    )
    combined_probability = models.FloatField(
        null=True, blank=True, verbose_name='Probabilidade Combinada'
    )
    stake_units = models.FloatField(
        default=10.0,
        verbose_name='Valor da Aposta (MT)',
        help_text='Valor em meticais aplicado directamente no bilhete (1:1).',
    )

    disclosure = models.TextField(blank=True, verbose_name='Aviso Obrigatório')

    snapshot_hash = models.CharField(max_length=64, db_index=True, verbose_name='Hash do Snapshot')
    meta = models.JSONField(default=dict, blank=True, verbose_name='Metadados')

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='social_proof_tickets_created',
        verbose_name='Criado Por',
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='social_proof_tickets_approved',
        verbose_name='Aprovado Por',
    )
    last_exported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='social_proof_tickets_exported',
        verbose_name='Último Exportador',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado Em')
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Aprovado Em')
    last_exported_at = models.DateTimeField(null=True, blank=True, verbose_name='Última Exportação')
    export_count = models.PositiveIntegerField(default=0, verbose_name='Exportações')

    class Meta:
        verbose_name = 'Bilhete de Prova Social'
        verbose_name_plural = 'Bilhetes de Prova Social'
        ordering = ['-date', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['date', 'kind', 'snapshot_hash'],
                name='unique_social_proof_snapshot',
            )
        ]
        indexes = [
            models.Index(fields=['date', 'kind', 'status']),
        ]

    def __str__(self):
        return f"{self.get_kind_display()} - {self.ticket_code}"

    def compute_snapshot_hash(self):
        payload = {
            'date': self.date.isoformat() if self.date else None,
            'kind': self.kind,
            'legs': self.legs or [],
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        if not self.snapshot_hash:
            self.snapshot_hash = self.compute_snapshot_hash()
        if not self.ticket_code:
            self.ticket_code = self.build_ticket_code()
        if not self.reserve_code:
            self.reserve_code = self.build_reserve_code()
        super().save(*args, **kwargs)

    def _hash_hex(self) -> str:
        """Hash do snapshot em hexadecimal maiúsculo (nunca vazio)."""
        raw = str(self.snapshot_hash or '')
        if re.fullmatch(r'[0-9a-fA-F]{16,}', raw):
            return raw.upper()
        return hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()

    def build_ticket_code(self) -> str:
        """
        Referência do bilhete no formato da Betway: 9 dígitos, começa sempre por 7.

        Derivada do snapshot para que o mesmo snapshot gere sempre a mesma
        referência (o campo é único).
        """
        digits = int(self._hash_hex(), 16) % 10**8
        return f'7{digits:08d}'

    def build_reserve_code(self) -> str:
        """Código de reserva: prefixo BW7 seguido de 7 caracteres alfanuméricos."""
        return f'BW7{self._hash_hex()[6:13]}'


    @property
    def legs_count(self):
        return len(self.legs or [])

    @property
    def potential_return(self):
        """Retorno potencial em MT (valor da aposta × odd total)."""
        if self.total_odd is None:
            return None
        return round(float(self.total_odd) * float(self.stake_units or 0), 2)

    @property
    def potential_return_units(self):
        return self.potential_return

    def approve(self, user):
        from django.utils import timezone

        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save(update_fields=['status', 'approved_by', 'approved_at'])

    def register_export(self, user):
        from django.utils import timezone

        self.status = 'exported'
        self.last_exported_by = user
        self.last_exported_at = timezone.now()
        self.export_count = (self.export_count or 0) + 1
        self.save(
            update_fields=[
                'status',
                'last_exported_by',
                'last_exported_at',
                'export_count',
            ]
        )


class TaskExecution(models.Model):
    """Registro de execuções das tasks Celery (generate_daily_bets, validate_daily_bets)"""
    
    TASK_CHOICES = [
        ('generate_daily_bets', 'Gerar Bilhetes Diários'),
        ('validate_daily_bets', 'Validar Bilhetes'),
        ('sync_match_results', 'Sincronizar Resultados'),
    ]
    
    STATUS_CHOICES = [
        ('running', 'Em Execução'),
        ('success', 'Sucesso'),
        ('failed', 'Falhou'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Identificação
    task_name = models.CharField(max_length=50, choices=TASK_CHOICES, verbose_name="Task")
    task_id = models.CharField(max_length=255, unique=True, verbose_name="Celery Task ID")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running', verbose_name="Status")
    
    # Execução
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Iniciado Em")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Finalizado Em")
    duration_seconds = models.IntegerField(null=True, blank=True, verbose_name="Duração (segundos)")
    
    # Resultados
    result_data = models.JSONField(null=True, blank=True, verbose_name="Dados do Resultado")
    error_message = models.TextField(blank=True, verbose_name="Mensagem de Erro")
    
    # Estatísticas
    matches_analyzed = models.IntegerField(default=0, verbose_name="Partidas Analisadas")
    bets_generated = models.IntegerField(default=0, verbose_name="Apostas Geradas")
    bets_validated = models.IntegerField(default=0, verbose_name="Apostas Validadas")
    api_calls = models.IntegerField(default=0, verbose_name="Chamadas API")
    
    # ✅ NOVO: Progresso em tempo real (17/02/2026)
    current_stage = models.CharField(
        max_length=50,
        blank=True,
        default='',
        verbose_name="Etapa Atual",
        help_text="Etapa de execução: searching, analyzing, creating, completed"
    )
    matches_found = models.IntegerField(
        default=0,
        verbose_name="Partidas Encontradas",
        help_text="Total de partidas encontradas para análise"
    )
    matches_processed = models.IntegerField(
        default=0,
        verbose_name="Partidas Processadas",
        help_text="Partidas já processadas/analisadas"
    )
    bets_created = models.IntegerField(
        default=0,
        verbose_name="Apostas Criadas",
        help_text="Apostas criadas até agora"
    )
    last_updated = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Última Atualização",
        help_text="Timestamp da última atualização de progresso"
    )
    progress_log = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Log de Progresso",
        help_text="Log detalhado das etapas de execução"
    )
    
    # Trigger
    triggered_by = models.CharField(
        max_length=20,
        choices=[('celery', 'Automático (Celery)'), ('manual', 'Manual (Admin)')],
        default='celery',
        verbose_name="Iniciado Por"
    )
    triggered_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuário"
    )
    
    class Meta:
        verbose_name = "Execução de Task"
        verbose_name_plural = "Execuções de Tasks"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['task_name', '-started_at']),
            models.Index(fields=['status', '-started_at']),
        ]
    
    def __str__(self):
        return f"{self.get_task_name_display()} - {self.started_at.strftime('%d/%m/%Y %H:%M')}"
    
    def update_progress(self, stage=None, matches_found=None, matches_processed=None, bets_created=None, log_message=None):
        """
        Atualiza o progresso da execução em tempo real
        
        Args:
            stage: Etapa atual ('searching', 'analyzing', 'creating', 'completed')
            matches_found: Total de partidas encontradas
            matches_processed: Partidas já processadas
            bets_created: Apostas criadas até agora
            log_message: Mensagem para adicionar ao log
        """
        from django.utils import timezone
        
        if stage is not None:
            self.current_stage = stage
        if matches_found is not None:
            self.matches_found = matches_found
        if matches_processed is not None:
            self.matches_processed = matches_processed
        if bets_created is not None:
            self.bets_created = bets_created
        
        self.last_updated = timezone.now()
        
        if log_message:
            if not isinstance(self.progress_log, list):
                self.progress_log = []
            self.progress_log.append({
                'timestamp': self.last_updated.isoformat(),
                'stage': self.current_stage,
                'message': log_message
            })
        
        self.save(update_fields=['current_stage', 'matches_found', 'matches_processed', 'bets_created', 'last_updated', 'progress_log'])
    
    def get_progress_percentage(self):
        """Calcula a porcentagem de progresso baseada nas partidas processadas"""
        if self.matches_found == 0:
            return 0
        return int((self.matches_processed / self.matches_found) * 100)
    
    def get_elapsed_time(self):
        """Retorna o tempo decorrido em segundos"""
        from django.utils import timezone
        if self.finished_at:
            return int((self.finished_at - self.started_at).total_seconds())
        return int((timezone.now() - self.started_at).total_seconds())
    
    def mark_finished(self, status='success', result_data=None, error_message=''):
        """Marca a task como finalizada"""
        from django.utils import timezone
        
        self.status = status
        self.current_stage = 'completed'
        self.finished_at = timezone.now()
        self.last_updated = self.finished_at
        self.duration_seconds = int((self.finished_at - self.started_at).total_seconds())
        
        if result_data:
            self.result_data = result_data
            # Extrair estatísticas do result_data
            if 'results' in result_data:
                results = result_data['results']
                self.matches_analyzed = results.get('matches_analyzed', 0)
                self.bets_generated = results.get('multiple_count', 0) + results.get('value_count', 0)
                self.api_calls = results.get('api_calls', 0)
        
        if error_message:
            self.error_message = error_message
        
        self.save()
