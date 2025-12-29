from django.contrib import admin
from .models import Analysis


@admin.register(Analysis)
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
