"""
Script de teste para enviar pagamento PaySuite via e-Mola
Uso: python test_paysuite_payment.py
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

def test_emola_payment():
    """Testar pagamento via e-Mola"""
    
    # Dados do teste
    phone = "861527090"
    amount = 10.00  # Valor pequeno para teste
    method = "emola"
    
    # Formatar telefone
    clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
    if not clean_phone.startswith('258'):
        clean_phone = '258' + clean_phone
    
    # Configurar requisição
    base_url = settings.PAYSUITE_BASE_URL
    api_key = settings.PAYSUITE_API_KEY
    
    url = f"{base_url}/payments"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Payload
    payload = {
        'amount': amount,
        'method': method,
        'reference': 'TEST001',
        'description': 'Teste de pagamento e-Mola',
        'msisdn': clean_phone,
        'callback_url': 'http://localhost:8000/api/subscriptions/payments/webhook/'
    }
    
    print("=" * 60)
    print("TESTE DE PAGAMENTO PAYSUITE - E-MOLA")
    print("=" * 60)
    print(f"\nEndpoint: {url}")
    print(f"Telefone: {clean_phone}")
    print(f"Valor: {amount} MZN")
    print(f"Método: {method}")
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
                    print(f"\nCheckout URL: {payment_data.get('checkout_url')}")
                    print("\n⚠️ NOTA: Para e-Mola, o usuário deve:")
                    print("   1. Receber notificação no telefone")
                    print("   2. Inserir PIN e confirmar")
                    print("   3. Pagamento será processado")
                else:
                    print("\n📱 PAGAMENTO DIRETO")
                    print("   O usuário receberá notificação no telefone 861527090")
                    print("   para confirmar o pagamento de 10.00 MZN")
                
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
    test_emola_payment()
