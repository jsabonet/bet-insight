"""
Testar endpoint admin/assign-subscription
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.subscriptions.plan_views import admin_assign_subscription
from django.utils import timezone

# Pegar ou criar superuser para teste
admin_user = User.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = User.objects.create_superuser(username='admin_test', email='admin_test@example.com', password='admin123')

# Pegar um usuário comum
user = User.objects.filter(is_superuser=False).first()
if not user:
    user = User.objects.create_user(username='user_test', email='user_test@example.com', password='user123')

factory = APIRequestFactory()
request = factory.post('/api/subscriptions/admin/assign-subscription/', {
    'user_id': user.id,
    'plan_slug': 'teste'
}, format='json')
force_authenticate(request, user=admin_user)

response = admin_assign_subscription(request)
print("📥 Resposta admin/assign-subscription (teste):")
print(f"Status: {response.status_code}")
print(f"Data: {response.data}")

# Verificar que assinaturas do usuário
active = user.subscriptions.filter(status='active', end_date__gt=timezone.now()).first()
print("Assinatura ativa computada:", bool(active), "end_date:", active.end_date if active else None)
user.refresh_from_db()
print("User.is_premium:", user.is_premium, "premium_until:", user.premium_until)

# Atribuir freemium (não deve criar registro, apenas cancelar)
request2 = factory.post('/api/subscriptions/admin/assign-subscription/', {
    'user_id': user.id,
    'plan_slug': 'freemium'
}, format='json')
force_authenticate(request2, user=admin_user)
response2 = admin_assign_subscription(request2)
print("📥 Resposta admin/assign-subscription (freemium):")
print(f"Status: {response2.status_code}")
print(f"Data: {response2.data}")
active2 = user.subscriptions.filter(status='active', end_date__gt=timezone.now()).first()
print("Assinatura ativa após freemium:", bool(active2))
user.refresh_from_db()
print("User.is_premium após freemium:", user.is_premium, "premium_until:", user.premium_until)
