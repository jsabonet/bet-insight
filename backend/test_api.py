#!/usr/bin/env python
"""
Script de teste da API Bet Insight
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def print_response(title, response):
    """Exibe resposta formatada"""
    print(f"\n{'='*60}")
    print(f"🔹 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print()

def test_auth():
    """Testa autenticação"""
    print("\n" + "="*60)
    print("🔐 TESTE DE AUTENTICAÇÃO")
    print("="*60)
    
    # Login
    login_data = {
        "username": "testuser",
        "password": "Test@123"
    }
    
    response = requests.post(f"{BASE_URL}/users/auth/login/", json=login_data)
    print_response("Login", response)
    
    if response.status_code == 200:
        tokens = response.json()
        return tokens['access']
    
    return None

def test_profile(token):
    """Testa endpoints de perfil"""
    print("\n" + "="*60)
    print("👤 TESTE DE PERFIL")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Ver perfil
    response = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
    print_response("Perfil do Usuário", response)
    
    # Estatísticas
    response = requests.get(f"{BASE_URL}/users/stats/", headers=headers)
    print_response("Estatísticas", response)

def test_leagues(token):
    """Testa endpoints de ligas"""
    print("\n" + "="*60)
    print("🏆 TESTE DE LIGAS")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/leagues/", headers=headers)
    print_response("Listar Ligas", response)

def test_matches(token):
    """Testa endpoints de partidas"""
    print("\n" + "="*60)
    print("⚽ TESTE DE PARTIDAS")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Listar todas
    response = requests.get(f"{BASE_URL}/matches/", headers=headers)
    print_response("Todas as Partidas", response)
    
    # Próximas
    response = requests.get(f"{BASE_URL}/matches/upcoming/", headers=headers)
    print_response("Partidas Futuras", response)
    
    # Retornar primeira partida para análise
    matches = response.json()
    if matches and len(matches) > 0:
        return matches[0]['id']
    
    return None

def test_analysis(token, match_id):
    """Testa endpoints de análise"""
    print("\n" + "="*60)
    print("🤖 TESTE DE ANÁLISE IA")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    if not match_id:
        print("❌ Nenhuma partida disponível para análise")
        return
    
    # Solicitar análise
    data = {"match_id": match_id}
    response = requests.post(f"{BASE_URL}/analyses/request_analysis/", 
                            json=data, headers=headers)
    print_response(f"Análise da Partida #{match_id}", response)
    
    # Listar minhas análises
    response = requests.get(f"{BASE_URL}/analyses/", headers=headers)
    print_response("Minhas Análises", response)
    
    # Estatísticas de análises
    response = requests.get(f"{BASE_URL}/analyses/my_stats/", headers=headers)
    print_response("Estatísticas de Análises", response)

def test_subscriptions(token):
    """Testa endpoints de assinaturas"""
    print("\n" + "="*60)
    print("💳 TESTE DE ASSINATURAS")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Ver assinatura atual
    response = requests.get(f"{BASE_URL}/subscriptions/current/", headers=headers)
    print_response("Assinatura Atual", response)

def main():
    """Executa todos os testes"""
    print("\n" + "🚀"*30)
    print("BET INSIGHT MOZAMBIQUE - TESTE DE API")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚀"*30)
    
    try:
        # 1. Autenticação
        token = test_auth()
        if not token:
            print("❌ Falha na autenticação. Abortando testes.")
            return
        
        print(f"\n✅ Token obtido: {token[:50]}...")
        
        # 2. Perfil
        test_profile(token)
        
        # 3. Ligas
        test_leagues(token)
        
        # 4. Partidas
        match_id = test_matches(token)
        
        # 5. Análise
        test_analysis(token, match_id)
        
        # 6. Assinaturas
        test_subscriptions(token)
        
        print("\n" + "="*60)
        print("✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERRO: Servidor não está rodando!")
        print("Execute: python manage.py runserver")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
