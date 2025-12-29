from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'is_premium', 'premium_until', 'daily_analysis_count', 'total_analyses', 'created_at']
    list_filter = ['is_premium', 'is_staff', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'phone']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações Adicionais', {
            'fields': ('phone', 'fcm_token', 'push_enabled')
        }),
        ('Status Premium', {
            'fields': ('is_premium', 'premium_until')
        }),
        ('Estatísticas', {
            'fields': ('daily_analysis_count', 'last_analysis_date', 'total_analyses', 'successful_predictions')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'total_analyses', 'successful_predictions']
