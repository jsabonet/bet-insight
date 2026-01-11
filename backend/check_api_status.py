"""
Verificar status da API Key
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
print("VERIFICAÇÃO: Status da API-Football")
print("="*80)

print(f"\n1. Configuração:")
print(f"   URL: {base_url}")
print(f"   Key: {api_key[:20]}..." if api_key else "   Key: NÃO CONFIGURADA")

# Testar status endpoint
print(f"\n2. Testando endpoint /status:")
try:
    response = requests.get(
        f'{base_url}/status',
        headers={'x-apisports-key': api_key},
        timeout=10
    )
    
    print(f"   Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Resposta: {data}")
        
        if 'response' in data:
            account = data['response'].get('account', {})
            requests_info = data['response'].get('requests', {})
            
            print(f"\n3. Informações da Conta:")
            print(f"   Plano: {account.get('firstname', 'N/A')} {account.get('lastname', 'N/A')}")
            print(f"   Email: {account.get('email', 'N/A')}")
            
            print(f"\n4. Uso da API:")
            print(f"   Limite diário: {requests_info.get('limit_day', 'N/A')}")
            print(f"   Usado hoje: {requests_info.get('current', 'N/A')}")
            print(f"   Restante: {requests_info.get('limit_day', 0) - requests_info.get('current', 0)}")
    else:
        print(f"   Erro: {response.text}")
        
except Exception as e:
    print(f"   Erro na conexão: {e}")

# Testar um endpoint simples
print(f"\n5. Testando endpoint /fixtures (live):")
try:
    response = requests.get(
        f'{base_url}/fixtures',
        headers={'x-apisports-key': api_key},
        params={'live': 'all'},
        timeout=10
    )
    
    print(f"   Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        count = len(data.get('response', []))
        print(f"   Partidas ao vivo: {count}")
    else:
        print(f"   Erro: {response.text[:200]}")
        
except Exception as e:
    print(f"   Erro: {e}")

print("\n" + "="*80)
