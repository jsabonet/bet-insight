"""
Script de teste para novos endpoints de administração
Teste as funcionalidades de gerenciamento de usuários e planos
"""
import requests
import json

# Configuração
BASE_URL = 'http://localhost:8000/api'
# Você precisa substituir pelo token de um usuário admin/superuser
ADMIN_TOKEN = 'SEU_TOKEN_ADMIN_AQUI'

headers = {
    'Authorization': f'Bearer {ADMIN_TOKEN}',
    'Content-Type': 'application/json'
}

print("=" * 60)
print("TESTE DE ENDPOINTS DE ADMINISTRAÇÃO")
print("=" * 60)

# 1. Listar todos os usuários
print("\n1. Listando todos os usuários...")
try:
    response = requests.get(
        f'{BASE_URL}/users/admin/users/all/',
        headers=headers,
        params={'page': 1, 'page_size': 5}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total de usuários: {data['count']}")
        print(f"Primeiros {len(data['results'])} usuários:")
        for user in data['results']:
            print(f"  - {user['username']} ({user['email']}) - Admin: {user.get('is_staff', False)}")
    else:
        print(f"Erro: {response.text}")
except Exception as e:
    print(f"Erro na requisição: {e}")

# 2. Testar endpoint de atribuir plano (aceita qualquer plano agora)
print("\n2. Testando atribuição de plano...")
print("(Este teste requer um user_id válido - ajuste o código)")
# Descomente e ajuste o user_id se quiser testar:
# try:
#     response = requests.post(
#         f'{BASE_URL}/subscriptions/admin/assign-subscription/',
#         headers=headers,
#         json={
#             'user_id': 2,  # Ajuste para um ID válido
#             'plan_slug': 'teste',
#             'duration_days': 1
#         }
#     )
#     print(f"Status: {response.status_code}")
#     print(f"Resposta: {json.dumps(response.json(), indent=2)}")
# except Exception as e:
#     print(f"Erro: {e}")

# 3. Testar endpoint de toggle admin
print("\n3. Testando toggle admin...")
print("(Este teste requer um user_id válido - ajuste o código)")
# Descomente e ajuste o user_id se quiser testar:
# try:
#     response = requests.post(
#         f'{BASE_URL}/users/admin/users/2/toggle-admin/',  # Ajuste o ID
#         headers=headers,
#         json={'is_staff': True}
#     )
#     print(f"Status: {response.status_code}")
#     print(f"Resposta: {json.dumps(response.json(), indent=2)}")
# except Exception as e:
#     print(f"Erro: {e}")

# 4. Testar endpoint de atualizar usuário
print("\n4. Testando atualização de usuário...")
print("(Este teste requer um user_id válido - ajuste o código)")
# Descomente e ajuste o user_id se quiser testar:
# try:
#     response = requests.put(
#         f'{BASE_URL}/users/admin/users/2/update/',  # Ajuste o ID
#         headers=headers,
#         json={
#             'phone': '841234567',
#             'first_name': 'Teste',
#             'is_active': True
#         }
#     )
#     print(f"Status: {response.status_code}")
#     print(f"Resposta: {json.dumps(response.json(), indent=2)}")
# except Exception as e:
#     print(f"Erro: {e}")

print("\n" + "=" * 60)
print("RESUMO DOS ENDPOINTS DISPONÍVEIS")
print("=" * 60)
print("""
1. GET  /users/admin/users/all/
   - Lista todos os usuários com filtros

2. POST /subscriptions/admin/assign-subscription/
   - Atribui qualquer plano a qualquer usuário
   Body: {"user_id": 123, "plan_slug": "pro", "duration_days": 30}

3. POST /subscriptions/admin/remove-subscription/
   - Remove assinatura ativa do usuário
   Body: {"user_id": 123}

4. POST /users/admin/users/<id>/toggle-admin/
   - Promove/remove privilégios de admin
   Body: {"is_staff": true, "is_superuser": false}

5. PUT  /users/admin/users/<id>/update/
   - Edita qualquer informação do usuário
   Body: {"username": "novo", "email": "novo@email.com", ...}

6. POST /users/admin/users/<id>/reset-password/
   - Reseta senha do usuário
   Body: {"new_password": "nova_senha"}

7. DELETE /users/admin/users/<id>/delete/
   - Deleta usuário (exceto superusers)

⚠️  IMPORTANTE: 
- Você precisa de um token de admin/superuser válido
- Substitua ADMIN_TOKEN no início do script
- Ajuste os user_id nos testes conforme necessário
""")
print("=" * 60)
