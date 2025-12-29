#!/usr/bin/env python
"""
Script de teste rápido das APIs configuradas
Execute: python test_apis.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
import requests

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_gemini():
    """Testar Google Gemini AI"""
    print("\n🤖 Testando Google Gemini AI...")
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        
        # Listar modelos disponíveis
        models = genai.list_models()
        available = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        
        if not available:
            print(f"❌ Nenhum modelo disponível")
            return False
        
        # Usar primeiro modelo disponível
        model_name = available[0].replace('models/', '')
        model = genai.GenerativeModel(model_name)
        
        response = model.generate_content("Responda apenas 'API funcionando!'")
        
        print(f"✅ Gemini OK")
        print(f"   Modelo: {model_name}")
        print(f"   Resposta: {response.text[:60]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini ERRO: {e}")
        return False

def test_api_football():
    """Testar API-Football"""
    print("\n⚽ Testando API-Football...")
    try:
        headers = {'x-apisports-key': settings.API_FOOTBALL_KEY}
        
        response = requests.get(
            f'{settings.API_FOOTBALL_URL}/status',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            req_info = data['response']['requests']
            print(f"✅ API-Football OK")
            print(f"   Uso hoje: {req_info['current']}/{req_info['limit_day']} requisições")
            return True
        else:
            print(f"❌ API-Football ERRO: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API-Football ERRO: {e}")
        return False

def test_football_data():
    """Testar Football-Data.org"""
    print("\n⚽ Testando Football-Data.org...")
    try:
        headers = {'X-Auth-Token': settings.FOOTBALL_DATA_API_KEY}
        
        response = requests.get(
            f'{settings.FOOTBALL_DATA_URL}/competitions',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('competitions', []))
            print(f"✅ Football-Data OK")
            print(f"   {count} competições disponíveis")
            return True
        else:
            print(f"❌ Football-Data ERRO: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Football-Data ERRO: {e}")
        return False

def test_paysuite():
    """Testar PaySuite"""
    print("\n💰 Testando PaySuite...")
    try:
        if not settings.PAYSUITE_API_TOKEN:
            print("❌ PaySuite: Token não configurado")
            return False
        
        headers = {
            'Authorization': f'Bearer {settings.PAYSUITE_API_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        print(f"✅ PaySuite Token OK")
        print(f"   Token: {settings.PAYSUITE_API_TOKEN[:30]}...")
        print(f"   Webhook Secret: {settings.PAYSUITE_WEBHOOK_SECRET[:30]}...")
        
        # Nota: Criar teste real de pagamento quando tiver ambiente sandbox
        print("   ⚠️  Teste completo requer número real/sandbox")
        return True
        
    except Exception as e:
        print(f"❌ PaySuite ERRO: {e}")
        return False

def test_database():
    """Testar conexão com banco de dados"""
    print("\n🗄️  Testando Banco de Dados...")
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            
        print(f"✅ PostgreSQL OK")
        print(f"   Database: {settings.DATABASES['default']['NAME']}")
        return True
        
    except Exception as e:
        print(f"❌ PostgreSQL ERRO: {e}")
        return False

def main():
    print_header("🔍 TESTE DE APIS - BET INSIGHT MOZAMBIQUE")
    
    print("\n📋 Configurações:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   Ambiente: {'Desenvolvimento' if settings.DEBUG else 'Produção'}")
    
    # Executar testes
    results = {
        'Banco de Dados': test_database(),
        'Google Gemini AI': test_gemini(),
        'API-Football': test_api_football(),
        'Football-Data.org': test_football_data(),
        'PaySuite': test_paysuite()
    }
    
    # Resumo
    print_header("📊 RESUMO DOS TESTES")
    
    for api, status in results.items():
        icon = "✅" if status else "❌"
        status_text = "OK" if status else "FALHOU"
        print(f"  {icon} {api:.<40} {status_text}")
    
    total = sum(results.values())
    print(f"\n  ✨ {total}/{len(results)} serviços funcionando corretamente!")
    
    if total == len(results):
        print("\n  🎉 Todas as APIs estão funcionando! Pronto para desenvolvimento.")
        return 0
    else:
        print("\n  ⚠️  Algumas APIs falharam. Verifique as configurações acima.")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Testes cancelados pelo usuário")
        sys.exit(1)
