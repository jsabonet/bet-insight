"""
Verificar limite do plano PRO
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from django.conf import settings

api_key = settings.API_FOOTBALL_KEY
base_url = settings.API_FOOTBALL_URL

print("\n" + "="*80)
print("STATUS DO PLANO PRO")
print("="*80)

try:
    response = requests.get(
        f'{base_url}/status',
        headers={'x-apisports-key': api_key},
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        
        if 'response' in data and data['response']:
            info = data['response']
            account = info.get('account', {})
            requests_info = info.get('requests', {})
            subscription = info.get('subscription', {})
            
            print(f"\n📊 CONTA:")
            print(f"   Nome: {account.get('firstname', 'N/A')} {account.get('lastname', 'N/A')}")
            print(f"   Email: {account.get('email', 'N/A')}")
            
            print(f"\n💳 ASSINATURA:")
            print(f"   Plano: {subscription.get('plan', 'N/A')}")
            print(f"   Fim: {subscription.get('end', 'N/A')}")
            print(f"   Ativo: {subscription.get('active', 'N/A')}")
            
            print(f"\n📈 USO DA API (HOJE):")
            print(f"   Limite diário: {requests_info.get('limit_day', 'N/A')}")
            print(f"   Usado: {requests_info.get('current', 'N/A')}")
            
            remaining = requests_info.get('limit_day', 0) - requests_info.get('current', 0)
            print(f"   Restante: {remaining}")
            
            percentage = (requests_info.get('current', 0) / requests_info.get('limit_day', 1)) * 100
            print(f"   Uso: {percentage:.1f}%")
            
            if remaining == 0:
                print(f"\n❌ LIMITE ATINGIDO!")
                print(f"   Reset em: meia-noite UTC")
        else:
            print(f"\n❌ Resposta vazia da API")
            print(f"   Data completa: {data}")
    else:
        print(f"\n❌ Erro HTTP: {response.status_code}")
        print(f"   Resposta: {response.text}")
        
except Exception as e:
    print(f"\n❌ Erro: {e}")

print("\n" + "="*80)
