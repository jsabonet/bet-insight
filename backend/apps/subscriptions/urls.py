from django.urls import path
from . import plan_views, payment_views

app_name = 'subscriptions'

urlpatterns = [
    # Planos
    path('plans/', plan_views.list_plans, name='list-plans'),
    path('plans/premium/', plan_views.list_premium_plans, name='list-premium-plans'),
    path('plans/<str:slug>/', plan_views.get_plan_details, name='plan-details'),
    
    # Assinaturas do usuário
    path('my-subscription/', plan_views.my_subscription, name='my-subscription'),
    path('cancel/', plan_views.cancel_subscription, name='cancel-subscription'),
    path('history/', plan_views.subscription_history, name='subscription-history'),

    # Admin - gerenciamento de assinaturas
    path('admin/assign-subscription/', plan_views.admin_assign_subscription, name='admin-assign-subscription'),
    path('admin/remove-subscription/', plan_views.admin_remove_subscription, name='admin-remove-subscription'),
    
    # Pagamentos
    path('payments/create/', payment_views.create_payment, name='create-payment'),
    path('payments/webhook/', payment_views.paysuite_webhook, name='paysuite-webhook'),
    path('payments/check/<str:transaction_id>/', payment_views.check_payment_status, name='check-payment'),
    path('payments/my-payments/', payment_views.my_payments, name='my-payments'),
]
