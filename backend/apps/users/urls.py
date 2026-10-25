from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    UserProfileView,
    UserStatsView,
    LoginView,
    verify_email,
    resend_verification,
    password_reset_request,
    password_reset_confirm,
)
from .admin_views import AdminUserViewSet, admin_stats, admin_analyses_stats, admin_delete_user
from .admin_management_views import (
    admin_toggle_admin_status,
    admin_update_user,
    admin_reset_user_password,
    admin_list_all_users,
)
from apps.notifications.push_views import (
    NotificationListView,
    NotificationReadView,
    PushPreferencesView,
    PushStatusView,
    PushSubscriptionView,
)

admin_router = DefaultRouter()
admin_router.register(r'admin/users', AdminUserViewSet, basename='admin-users')

urlpatterns = [
    # Autenticação JWT
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Verificação de email
    path('auth/verify-email/', verify_email, name='verify-email'),
    path('auth/resend-verification/', resend_verification, name='resend-verification'),

    # Recuperação de senha
    path('auth/password-reset/', password_reset_request, name='password-reset'),
    path('auth/password-reset/confirm/', password_reset_confirm, name='password-reset-confirm'),
    
    # Perfil
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('stats/', UserStatsView.as_view(), name='user-stats'),
    path('push/status/', PushStatusView.as_view(), name='push-status'),
    path('push/subscriptions/', PushSubscriptionView.as_view(), name='push-subscriptions'),
    path('push/preferences/', PushPreferencesView.as_view(), name='push-preferences'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/read/', NotificationReadView.as_view(), name='notifications-read-all'),
    path('notifications/<int:notification_id>/read/', NotificationReadView.as_view(), name='notification-read'),

    # Admin - router (CRUD de usuários + actions)
    path('', include(admin_router.urls)),

    # Admin - estatísticas e ações extras
    path('admin/stats/', admin_stats, name='admin-stats'),
    path('admin/analyses-stats/', admin_analyses_stats, name='admin-analyses-stats'),
    path('admin/users/all/', admin_list_all_users, name='admin-users-all'),
    path('admin/users/<int:user_id>/delete/', admin_delete_user, name='admin-delete-user'),
    path('admin/users/<int:user_id>/toggle-admin/', admin_toggle_admin_status, name='admin-toggle-admin'),
    path('admin/users/<int:user_id>/update/', admin_update_user, name='admin-update-user'),
    path('admin/users/<int:user_id>/reset-password/', admin_reset_user_password, name='admin-reset-password'),
]
