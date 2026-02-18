"""
Teste HTTP do endpoint admin/generate-now
"""
import requests
import json

# URL do endpoint
url = "http://localhost:8000/api/daily-bets/admin/generate-now/"

# Headers com autenticação (ajuste o token se necessário)
headers = {
    "Content-Type": "application/json",
}

print("=" * 70)
print("TESTE HTTP: POST /api/daily-bets/admin/generate-now/")
print("=" * 70)
print()

try:
    # Fazer requisição POST (sem autenticação para teste inicial)
    print("Enviando requisição POST...")
    response = requests.post(url, headers=headers, timeout=180)
    
    print(f"Status Code: {response.status_code}")
    print()
    
    # Mostrar response
    if response.status_code == 200:
        print("[OK] Requisição bem-sucedida!")
        print()
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))
    elif response.status_code == 401 or response.status_code == 403:
        print("[ESPERADO] Erro de autenticação (precisa de admin login)")
        print()
        print("Response:")
        print(response.text)
    else:
        print(f"[ERRO] Status {response.status_code}")
        print()
        print("Response:")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("[ERRO] Não foi possível conectar ao servidor Django")
    print("Certifique-se de que o servidor está rodando em http://localhost:8000")
except Exception as e:
    print(f"[ERRO] {str(e)}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
