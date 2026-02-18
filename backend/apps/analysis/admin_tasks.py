"""
Admin configuration for TaskExecution model
Provides Django admin interface for monitoring Celery task executions
"""
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages

from .models import TaskExecution, DailyBet

# Import the custom admin site if it exists, otherwise use default
try:
    from .admin import admin_site
except ImportError:
    from django.contrib.admin import site as admin_site


@admin.register(TaskExecution, site=admin_site)
class TaskExecutionAdmin(admin.ModelAdmin):
    """Admin para Execuções de Tasks Celery"""
    
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


# Adicionar link no menu do admin
admin_site._registry[TaskExecution].change_list_template = 'admin/analysis/taskexecution_changelist.html'
