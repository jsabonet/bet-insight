from django.contrib import admin
from django.utils.html import format_html
from .models import Analysis, DailyBet
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

