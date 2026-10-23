from django.contrib import admin
from .models import Affiliate, AffiliateReferral, AffiliateCommission, AffiliateClick
from config.admin import admin_site


@admin.register(Affiliate, site=admin_site)
class AffiliateAdmin(admin.ModelAdmin):
    list_display = ['code', 'user', 'status', 'tier', 'commission_rate', 'available_balance', 'pending_balance', 'total_earned', 'created_at']
    list_filter = ['status', 'tier', 'created_at']
    search_fields = ['code', 'user__email', 'user__username']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['code', 'total_earned', 'available_balance', 'pending_balance', 'created_at', 'updated_at']


@admin.register(AffiliateReferral, site=admin_site)
class AffiliateReferralAdmin(admin.ModelAdmin):
    list_display = ['user', 'affiliate', 'code', 'source', 'converted_at', 'first_touch_at']
    list_filter = ['source', 'converted_at']
    search_fields = ['user__email', 'affiliate__code']


@admin.register(AffiliateCommission, site=admin_site)
class AffiliateCommissionAdmin(admin.ModelAdmin):
    list_display = ['affiliate', 'amount', 'rate', 'status', 'available_at', 'paid_at', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['affiliate__code', 'payment__transaction_id']
    date_hierarchy = 'created_at'


@admin.register(AffiliateClick, site=admin_site)
class AffiliateClickAdmin(admin.ModelAdmin):
    list_display = ['affiliate', 'code', 'click_id', 'ip', 'created_at']
    search_fields = ['code', 'click_id']
    date_hierarchy = 'created_at'
