"""
Script de teste para enviar pagamento PaySuite SEM número de telefone
O usuário preencherá na página externa
Uso: python test_paysuite_no_phone.py
"""
import os
import sys
import django
import requests
import json
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def test_payment_without_phone():
    """Testar pagamento sem telefone - checkout externo"""
    
    # Dados do teste
    amount = 10.00  # Valor pequeno para teste
    method = "mpesa"  # Pode ser mpesa ou emola
    
    # Configurar requisição
    base_url = settings.PAYSUITE_BASE_URL
    api_key = settings.PAYSUITE_API_KEY
    
    url = f"{base_url}/payments"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Payload SEM telefone (checkout externo)
    payload = {
        'amount': amount,
        'method': method,
        'reference': 'TEST002',
        'description': 'Teste de pagamento sem telefone - Checkout externo',
        'callback_url': 'http://localhost:8000/api/subscriptions/payments/webhook/'
    }
    
    print("=" * 60)
    print("TESTE DE PAGAMENTO PAYSUITE - CHECKOUT EXTERNO")
    print("=" * 60)
    print(f"\nEndpoint: {url}")
    print(f"Valor: {amount} MZN")
    print(f"Método: {method}")
    print(f"Telefone: NÃO ENVIADO (usuário preencherá na página)")
    print(f"\nPayload:")
    print(json.dumps(payload, indent=2))
    print("\n" + "=" * 60)
    print("Enviando requisição...")
    print("=" * 60 + "\n")
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            if key.lower() not in ['set-cookie', 'cookie']:
                print(f"  {key}: {value}")
        
        print(f"\nResponse Body:")
        try:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Interpretar resposta
            print("\n" + "=" * 60)
            print("RESULTADO")
            print("=" * 60)
            
            if data.get('status') == 'success':
                payment_data = data.get('data', {})
                print("✅ SUCESSO!")
                print(f"\nID Pagamento: {payment_data.get('id')}")
                print(f"Referência: {payment_data.get('reference')}")
                print(f"Status: {payment_data.get('status')}")
                
                if payment_data.get('checkout_url'):
                    print(f"\n🔗 Checkout URL: {payment_data.get('checkout_url')}")
                    print("\n📱 FLUXO DE CHECKOUT EXTERNO:")
                    print("   1. Abra o link acima em um navegador")
                    print("   2. Digite seu número de telefone na página")
                    print("   3. Confirme o pagamento no seu telefone")
                    print("   4. Aguarde a confirmação via webhook")
                    print(f"\n   Método de pagamento: {method.upper()}")
                else:
                    print("\n❌ ERRO: Checkout URL não foi retornado")
                
            else:
                print("❌ ERRO!")
                print(f"\nMensagem: {data.get('message')}")
                if data.get('errors'):
                    print(f"Erros: {json.dumps(data.get('errors'), indent=2)}")
        
        except json.JSONDecodeError:
            print(response.text[:500])
            print("\n❌ Resposta não é JSON válido")
        
        print("\n" + "=" * 60)
        
        response.raise_for_status()
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERRO NA REQUISIÇÃO:")
        print(f"   {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"\n   Response: {e.response.text[:500]}")
        return None

if __name__ == '__main__':
    test_payment_without_phone()
