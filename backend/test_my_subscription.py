"""
Testar endpoint my-subscription
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.subscriptions.plan_views import my_subscription

# Buscar usuário com subscription
user = User.objects.get(email='jsabonete09@gmail.com')

# Criar request
factory = APIRequestFactory()
request = factory.get('/api/subscriptions/my-subscription/')
force_authenticate(request, user=user)

# Executar view
response = my_subscription(request)

print("📥 Resposta do endpoint my-subscription:")
print(f"Status: {response.status_code}")
print(f"Data: {response.data}")
