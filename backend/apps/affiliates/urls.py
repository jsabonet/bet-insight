from django.urls import path
from . import views, admin_views

app_name = 'affiliates'

urlpatterns = [
    # Público
    path('track/', views.track_click, name='track-click'),
    path('validate-code/', views.validate_code, name='validate-code'),

    # Afiliado (autenticado)
    path('apply/', views.apply_affiliate, name='apply'),
    path('me/', views.my_affiliate, name='my-affiliate'),
    path('me/stats/', views.my_affiliate_stats, name='my-affiliate-stats'),
    path('me/commissions/', views.my_commissions, name='my-commissions'),
    path('me/referrals/', views.my_referrals, name='my-referrals'),
    path('me/withdrawals/', views.my_withdrawals, name='my-withdrawals'),
    path('me/withdraw/', views.withdraw, name='withdraw'),

    # Admin
    path('admin/overview/', admin_views.admin_overview, name='admin-overview'),
    path('admin/affiliates/', admin_views.admin_affiliates_list, name='admin-affiliates-list'),
    path('admin/commissions/', admin_views.admin_commissions_list, name='admin-commissions-list'),
    path('admin/withdrawals/', admin_views.admin_withdrawals_list, name='admin-withdrawals-list'),
    path('admin/withdrawals/<int:withdrawal_id>/process/', admin_views.admin_process_withdrawal, name='admin-process-withdrawal'),
    path('admin/withdrawals/<int:withdrawal_id>/complete/', admin_views.admin_complete_withdrawal, name='admin-complete-withdrawal'),
    path('admin/withdrawals/<int:withdrawal_id>/reject/', admin_views.admin_reject_withdrawal, name='admin-reject-withdrawal'),
    path('admin/commissions/export/', admin_views.admin_export_commissions, name='admin-commissions-export'),
    path('admin/commissions/<int:commission_id>/approve/', admin_views.admin_approve_commission, name='admin-approve-commission'),
    path('admin/commissions/<int:commission_id>/mark-paid/', admin_views.admin_mark_paid, name='admin-mark-paid'),
    path('admin/affiliates/<int:affiliate_id>/set-tier/', admin_views.admin_set_tier, name='admin-set-tier'),
    path('admin/affiliates/<int:affiliate_id>/toggle-suspend/', admin_views.admin_toggle_suspend, name='admin-toggle-suspend'),
]
