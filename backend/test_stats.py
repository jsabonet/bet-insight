"""
Testar endpoint /api/users/stats/
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.users.views import UserStatsView

user = User.objects.filter(is_active=True).first()
assert user, "Nenhum usuário ativo encontrado para teste"

factory = APIRequestFactory()
request = factory.get('/api/users/stats/')
force_authenticate(request, user=user)

view = UserStatsView.as_view()
response = view(request)

print("📥 Resposta do endpoint users/stats:")
print(f"Status: {response.status_code}")
print(f"Data: {response.data}")
