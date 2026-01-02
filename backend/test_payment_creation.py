"""
Script de teste para o endpoint de criação de pagamento
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.users.models import User
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from apps.subscriptions.payment_views import create_payment

def test_payment_creation():
    """Testa criação de pagamento"""
    
    # Obter ou criar usuário de teste
    user, created = User.objects.get_or_create(
        email='teste@placercerto.co.mz',
        defaults={
            'username': 'teste',
            'first_name': 'Usuario',
            'last_name': 'Teste'
        }
    )
    
    if created:
        user.set_password('teste123')
        user.save()
        print(f"✅ Usuário criado: {user.email}")
    else:
        print(f"✅ Usuário existente: {user.email}")
    
    # Criar request simulado
    factory = APIRequestFactory()
    request = factory.post('/api/subscriptions/payments/create/', {
        'plan_slug': 'teste',
        'payment_method': 'emola'
    }, format='json')
    
    # Autenticar request
    force_authenticate(request, user=user)
    
    print("\n📤 Enviando requisição de pagamento...")
    print(f"   Plan: teste (1 MZN)")
    print(f"   Método: emola")
    print(f"   Usuário: {user.email}")
    
    # Executar view
    try:
        response = create_payment(request)
        
        print(f"\n📥 Resposta recebida:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Data: {response.data}")
        
        if response.status_code == 201:
            print("\n✅ SUCESSO! Pagamento criado com sucesso!")
            if 'checkout_url' in response.data:
                print(f"   Checkout URL: {response.data['checkout_url']}")
        else:
            print(f"\n❌ ERRO: Status {response.status_code}")
            
    except Exception as e:
        print(f"\n❌ ERRO EXCEÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_payment_creation()
