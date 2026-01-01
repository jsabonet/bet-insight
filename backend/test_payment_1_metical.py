"""
Teste de pagamento de 1 Metical (Plano Teste)
"""
import requests
import json

# Configuração
API_BASE = 'https://paysuite.tech/api/v1'
API_KEY = '1193|4iu77r4TUkd0nsB3MP8Qjr1uYVvM7d0Y0lpOgwETc153d048'

# Dados do pagamento de teste
payload = {
    'amount': 1,  # 1 metical
    'reference': 'TESTE001',
    'description': 'Plano Teste - 1 MZN - Bet Insight',
    'return_url': 'http://localhost:5173/payment/confirmation/TESTE001',
    'method': 'emola',  # ou 'mpesa'
}

print("=" * 60)
print("TESTE DE PAGAMENTO - PLANO TESTE (1 MZN)")
print("=" * 60)
print(f"Valor: {payload['amount']} MZN")
print(f"Método: {payload['method']}")
print(f"Referência: {payload['reference']}")
print("=" * 60)

# Fazer requisição
try:
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print("\n📤 Enviando requisição para PaySuite...")
    response = requests.post(
        f'{API_BASE}/payments',
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"\n📊 Status Code: {response.status_code}")
    
    # Parse resposta
    try:
        data = response.json()
        print("\n📋 Resposta completa:")
        print(json.dumps(data, indent=2))
        
        if response.status_code == 201:
            print("\n✅ PAGAMENTO CRIADO COM SUCESSO!")
            
            if 'data' in data:
                payment_data = data['data']
                print(f"\n💳 ID do Pagamento: {payment_data.get('id')}")
                print(f"💰 Valor: {payment_data.get('amount')} MZN")
                print(f"📱 Status: {payment_data.get('status')}")
                
                if 'checkout_url' in payment_data:
                    print(f"\n🔗 CHECKOUT URL:")
                    print(f"   {payment_data['checkout_url']}")
                    print("\n👉 Abra este link no navegador para completar o pagamento de 1 MZN")
                    print("   (Você pode testar sem realmente pagar)")
        else:
            print("\n❌ ERRO ao criar pagamento")
            if 'message' in data:
                print(f"Mensagem: {data['message']}")
            
    except json.JSONDecodeError:
        print("\n❌ Erro ao processar resposta JSON")
        print(f"Resposta raw: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"\n❌ Erro na requisição: {str(e)}")

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
