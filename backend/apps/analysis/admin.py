from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Analysis, DailyBet, SocialProofTicket, TaskExecution
from config.admin import admin_site


@admin.register(Analysis, site=admin_site)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'match', 'prediction', 'confidence', 'is_correct', 'created_at']
    list_filter = ['prediction', 'confidence', 'is_correct', 'created_at']
    search_fields = ['user__email', 'match__home_team__name', 'match__away_team__name']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'match', 'created_at')
        }),
        ('Predição', {
            'fields': ('prediction', 'confidence', 'home_probability', 'draw_probability', 'away_probability')
        }),
        ('Expected Goals', {
            'fields': ('home_xg', 'away_xg')
        }),
        ('Análise Detalhada', {
            'fields': ('reasoning', 'key_factors', 'analysis_data'),
            'classes': ('collapse',)
        }),
        ('Validação', {
            'fields': ('is_correct', 'actual_result')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'is_correct', 'actual_result']
    
    def has_add_permission(self, request):
        """Análises só podem ser criadas via API"""
        return False


@admin.register(DailyBet, site=admin_site)
class DailyBetAdmin(admin.ModelAdmin):
    """Admin para Apostas Diárias geradas automaticamente"""
    
    list_display = [
        'id', 'date', 'bet_type', 'status_badge', 'total_odd', 
        'combined_probability_pct', 'ev_pct', 'selections_count', 
        'is_validated', 'created_at'
    ]
    list_filter = ['bet_type', 'status', 'is_validated', 'date']
    search_fields = ['id', 'selections']
    date_hierarchy = 'date'
    ordering = ['-date', '-expected_value']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('id', 'date', 'bet_type', 'created_at')
        }),
        ('Seleções', {
            'fields': ('selections', 'selections_summary'),
            'description': 'Apostas incluídas neste bilhete'
        }),
        ('Odds e Probabilidades', {
            'fields': ('total_odd', 'fair_odd', 'combined_probability', 'expected_value')
        }),
        ('Stake e Resultado', {
            'fields': ('suggested_stake', 'status', 'actual_result', 'roi_display')
        }),
        ('Validação', {
            'fields': ('is_validated', 'validated_at')
        }),
    )
    
    readonly_fields = [
        'id', 'created_at', 'validated_at', 'selections_summary', 
        'combined_probability_pct', 'ev_pct', 'roi_display'
    ]
    
    def has_add_permission(self, request):
        """Apostas diárias são geradas automaticamente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Permitir deleção apenas de apostas não validadas"""
        if obj and obj.is_validated:
            return False
        return True
    
    def status_badge(self, obj):
        """Badge colorido para status"""
        colors = {
            'pending': 'gray',
            'won': 'green',
            'lost': 'red',
            'partial': 'orange',
            'cancelled': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def selections_count(self, obj):
        """Número de apostas no bilhete"""
        return len(obj.selections) if obj.selections else 0
    selections_count.short_description = 'Apostas'
    
    def combined_probability_pct(self, obj):
        """Probabilidade combinada em %"""
        return f"{obj.combined_probability * 100:.1f}%"
    combined_probability_pct.short_description = 'Prob. %'
    
    def ev_pct(self, obj):
        """Expected Value formatado"""
        ev = obj.expected_value
        color = 'green' if ev >= 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:+.1f}%</span>',
            color,
            ev
        )
    ev_pct.short_description = 'EV %'
    
    def roi_display(self, obj):
        """ROI formatado (se validado)"""
        roi = obj.get_roi()
        if roi is None:
            return '-'
        color = 'green' if roi >= 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:+.1f}%</span>',
            color,
            roi
        )
    roi_display.short_description = 'ROI'
    
    def selections_summary(self, obj):
        """Resumo legível das seleções"""
        if not obj.selections:
            return '-'
        
        html = '<table style="width: 100%; border-collapse: collapse;">'
        html += '<tr style="background-color: #f0f0f0; font-weight: bold;">'
        html += '<th style="padding: 5px; text-align: left;">Partida</th>'
        html += '<th style="padding: 5px; text-align: left;">Aposta</th>'
        html += '<th style="padding: 5px; text-align: center;">Odd</th>'
        html += '<th style="padding: 5px; text-align: center;">Prob</th>'
        html += '<th style="padding: 5px; text-align: center;">EV</th>'
        if obj.is_validated:
            html += '<th style="padding: 5px; text-align: center;">Resultado</th>'
        html += '</tr>'
        
        for sel in obj.selections:
            result = sel.get('result')
            result_color = {'won': 'green', 'lost': 'red', 'cancelled': 'gray'}.get(result, 'black')
            
            html += '<tr style="border-bottom: 1px solid #ddd;">'
            html += f'<td style="padding: 5px;">{sel.get("match", "N/A")}</td>'
            html += f'<td style="padding: 5px;">{sel.get("pick", "N/A")} ({sel.get("market", "N/A")})</td>'
            html += f'<td style="padding: 5px; text-align: center;">{sel.get("odd", 0):.2f}</td>'
            html += f'<td style="padding: 5px; text-align: center;">{sel.get("probability", 0)*100:.0f}%</td>'
            html += f'<td style="padding: 5px; text-align: center;">{sel.get("ev_pct", 0):+.1f}%</td>'
            if obj.is_validated:
                html += f'<td style="padding: 5px; text-align: center; color: {result_color}; font-weight: bold;">'
                html += f'{result or "-"}</td>'
            html += '</tr>'
        
        html += '</table>'
        return format_html(html)
    selections_summary.short_description = 'Detalhes das Apostas'


@admin.register(TaskExecution, site=admin_site)
class TaskExecutionAdmin(admin.ModelAdmin):
    """Admin para gerenciamento de execuções de tasks Celery"""
    
    list_display = [
        'id', 'task_name_display', 'status_badge', 'started_at', 
        'duration_display', 'stats_display', 'triggered_by_display'
    ]
    list_filter = ['task_name', 'status', 'triggered_by', 'started_at']
    search_fields = ['task_id', 'error_message']
    date_hierarchy = 'started_at'
    ordering = ['-started_at']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('task_name', 'task_id', 'started_at', 'finished_at', 'duration_seconds')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Estatísticas', {
            'fields': ('matches_analyzed', 'bets_generated', 'bets_validated', 'api_calls')
        }),
        ('Trigger', {
            'fields': ('triggered_by', 'triggered_by_user')
        }),
        ('Dados Completos', {
            'fields': ('result_data',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'task_id', 'started_at', 'finished_at', 'duration_seconds',
        'matches_analyzed', 'bets_generated', 'bets_validated', 'api_calls',
        'result_data'
    ]
    
    def has_add_permission(self, request):
        """Execuções são criadas automaticamente pelas tasks"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Permitir deleção de execuções antigas"""
        return True
    
    def task_name_display(self, obj):
        """Nome da task formatado"""
        icons = {
            'generate_daily_bets': '🎯',
            'validate_daily_bets': '✔️',
        }
        icon = icons.get(obj.task_name, '⚙️')
        return f"{icon} {obj.get_task_name_display()}"
    task_name_display.short_description = 'Task'
    
    def status_badge(self, obj):
        """Badge colorido para status"""
        colors = {
            'running': '#FFA500',  # orange
            'success': '#28a745',  # green
            'failed': '#dc3545',   # red
            'cancelled': '#6c757d' # gray
        }
        icons = {
            'running': '▶️',
            'success': '✅',
            'failed': '❌',
            'cancelled': '⏸️'
        }
        color = colors.get(obj.status, '#6c757d')
        icon = icons.get(obj.status, '❓')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 4px; font-weight: bold;">{} {}</span>',
            color,
            icon,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def duration_display(self, obj):
        """Duração formatada"""
        if not obj.duration_seconds:
            if obj.status == 'running':
                running_time = (timezone.now() - obj.started_at).total_seconds()
                return format_html('<span style="color: orange;">⏳ {}s</span>', int(running_time))
            return '-'
        
        minutes = obj.duration_seconds // 60
        seconds = obj.duration_seconds % 60
        
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    duration_display.short_description = 'Duração'
    
    def stats_display(self, obj):
        """Estatísticas resumidas"""
        stats = []
        if obj.matches_analyzed > 0:
            stats.append(f"⚽ {obj.matches_analyzed}")
        if obj.bets_generated > 0:
            stats.append(f"📋 {obj.bets_generated}")
        if obj.bets_validated > 0:
            stats.append(f"✔️ {obj.bets_validated}")
        if obj.api_calls > 0:
            stats.append(f"🔌 {obj.api_calls}")
        
        return ' | '.join(stats) if stats else '-'
    stats_display.short_description = 'Estatísticas'
    
    def triggered_by_display(self, obj):
        """Trigger formatado"""
        if obj.triggered_by == 'manual':
            user = f" ({obj.triggered_by_user.email})" if obj.triggered_by_user else ""
            return format_html('<span style="color: blue;">👤 Manual{}</span>', user)
        return '🤖 Automático'
    triggered_by_display.short_description = 'Iniciado Por'
    
    def get_urls(self):
        """Adicionar URLs customizadas para o painel de controle"""
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='daily_bets_dashboard'),
            path('run-generate/', self.admin_site.admin_view(self.run_generate_bets), name='run_generate_bets'),
            path('run-validate/', self.admin_site.admin_view(self.run_validate_bets), name='run_validate_bets'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        """View customizada para painel de controle das Daily Bets"""
        from django.db.models import Count, Q, Avg
        from datetime import timedelta
        
        # Últimas 10 execuções
        recent_executions = TaskExecution.objects.all()[:10]
        
        # Execuções em andamento
        running_executions = TaskExecution.objects.filter(status='running')
        
        # Estatísticas gerais (últimos 30 dias)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        executions_stats = TaskExecution.objects.filter(
            started_at__gte=thirty_days_ago
        ).aggregate(
            total=Count('id'),
            success=Count('id', filter=Q(status='success')),
            failed=Count('id', filter=Q(status='failed')),
            avg_duration=Avg('duration_seconds', filter=Q(status='success'))
        )
        
        # Estatísticas de Daily Bets (últimos 7 dias)
        seven_days_ago = timezone.now().date() - timedelta(days=7)
        
        bets_stats = DailyBet.objects.filter(
            date__gte=seven_days_ago
        ).aggregate(
            total=Count('id'),
            pending=Count('id', filter=Q(status='pending')),
            won=Count('id', filter=Q(status='won')),
            lost=Count('id', filter=Q(status='lost')),
            validated=Count('id', filter=Q(is_validated=True)),
            avg_odd=Avg('total_odd'),
            avg_ev=Avg('expected_value')
        )
        
        # Última geração automática
        last_auto_generation = TaskExecution.objects.filter(
            task_name='generate_daily_bets',
            triggered_by='celery',
            status='success'
        ).first()
        
        # Última validação automática
        last_auto_validation = TaskExecution.objects.filter(
            task_name='validate_daily_bets',
            triggered_by='celery',
            status='success'
        ).first()
        
        context = {
            **self.admin_site.each_context(request),
            'title': 'Painel de Controle - Daily Bets',
            'recent_executions': recent_executions,
            'running_executions': running_executions,
            'executions_stats': executions_stats,
            'bets_stats': bets_stats,
            'last_auto_generation': last_auto_generation,
            'last_auto_validation': last_auto_validation,
        }
        
        return render(request, 'admin/analysis/daily_bets_dashboard.html', context)
    
    def run_generate_bets(self, request):
        """Executar manualmente a task de geração de bilhetes"""
        if request.method == 'POST':
            try:
                from apps.analysis.tasks import generate_daily_bets
                
                # Executar task assincronamente
                result = generate_daily_bets.delay(
                    triggered_by='manual',
                    user_id=request.user.id
                )
                
                messages.success(
                    request,
                    f'✅ Task de geração de bilhetes iniciada com sucesso! Task ID: {result.id}'
                )
            except Exception as e:
                messages.error(request, f'❌ Erro ao iniciar task: {str(e)}')
        
        return redirect('admin:daily_bets_dashboard')
    
    def run_validate_bets(self, request):
        """Executar manualmente a task de validação de bilhetes"""
        if request.method == 'POST':
            try:
                from apps.analysis.tasks import validate_daily_bets
                
                # Executar task assincronamente
                result = validate_daily_bets.delay(
                    triggered_by='manual',
                    user_id=request.user.id
                )
                
                messages.success(
                    request,
                    f'✅ Task de validação iniciada com sucesso! Task ID: {result.id}'
                )
            except Exception as e:
                messages.error(request, f'❌ Erro ao iniciar task: {str(e)}')
        
        return redirect('admin:daily_bets_dashboard')


@admin.register(SocialProofTicket, site=admin_site)
class SocialProofTicketAdmin(admin.ModelAdmin):
    """Snapshots de prova social usados nas redes sociais (somente leitura + ações)"""

    list_display = [
        'id', 'date', 'kind', 'status_badge', 'ticket_code',
        'legs_count', 'total_odd', 'export_count', 'created_at',
    ]
    list_filter = ['kind', 'status', 'date']
    search_fields = ['ticket_code', 'reserve_code', 'snapshot_hash']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    list_per_page = 30

    fields = [
        'date', 'kind', 'status', 'ticket_code', 'reserve_code',
        'legs_count', 'total_odd', 'combined_probability', 'stake_units',
        'disclosure', 'watermark_required', 'snapshot_hash', 'meta',
        'source_bet_ids', 'created_by', 'approved_by', 'approved_at',
        'last_exported_by', 'last_exported_at', 'export_count',
        'created_at',
    ]
    readonly_fields = fields

    actions = ['mark_approved', 'mark_discarded']

    def has_add_permission(self, request):
        return False

    def status_badge(self, obj):
        colors = {
            'candidate': '#FFA500',
            'approved': '#28a745',
            'exported': '#007bff',
            'discarded': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;'
            'border-radius:10px;font-size:11px;">{}</span>',
            color,
            obj.get_status_display(),
        )
    status_badge.short_description = 'Estado'

    @admin.action(description='Aprovar bilhetes selecionados')
    def mark_approved(self, request, queryset):
        count = 0
        for ticket in queryset.exclude(status='discarded'):
            ticket.approve(request.user)
            count += 1
        self.message_user(request, f'{count} bilhete(s) aprovado(s).', messages.SUCCESS)

    @admin.action(description='Descartar bilhetes selecionados')
    def mark_discarded(self, request, queryset):
        updated = queryset.update(status='discarded')
        self.message_user(request, f'{updated} bilhete(s) descartado(s).', messages.SUCCESS)

