from django.contrib import admin
from .models import Subscription, Payment


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew', 'amount_paid']
    list_filter = ['status', 'plan', 'auto_renew', 'created_at']
    search_fields = ['user__email', 'user__username']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Usuário', {
            'fields': ('user',)
        }),
        ('Plano', {
            'fields': ('plan', 'status', 'amount_paid')
        }),
        ('Período', {
            'fields': ('start_date', 'end_date')
        }),
        ('Renovação', {
            'fields': ('auto_renew', 'cancelled_at')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['cancel_subscriptions', 'activate_subscriptions']
    
    def cancel_subscriptions(self, request, queryset):
        """Ação para cancelar assinaturas selecionadas"""
        for subscription in queryset:
            subscription.cancel()
        self.message_user(request, f"{queryset.count()} assinatura(s) cancelada(s).")
    cancel_subscriptions.short_description = "Cancelar assinaturas selecionadas"
    
    def activate_subscriptions(self, request, queryset):
        """Ação para ativar assinaturas"""
        queryset.update(status='active')
        self.message_user(request, f"{queryset.count()} assinatura(s) ativada(s).")
    activate_subscriptions.short_description = "Ativar assinaturas selecionadas"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'phone_number', 'transaction_id', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__email', 'transaction_id', 'mpesa_reference', 'phone_number']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informações do Pagamento', {
            'fields': ('user', 'subscription', 'amount', 'phone_number')
        }),
        ('M-Pesa', {
            'fields': ('transaction_id', 'mpesa_reference', 'payment_method')
        }),
        ('Status', {
            'fields': ('status', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    
    def has_add_permission(self, request):
        """Pagamentos só podem ser criados via API"""
        return False
