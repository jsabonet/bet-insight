"""
Teste completo: Backend + Frontend
"""

import requests
import json

print("\n" + "="*80)
print("🧪 TESTE COMPLETO: BACKEND + FRONTEND")
print("="*80 + "\n")

# 1. Testar Backend
print("1️⃣ BACKEND: http://localhost:8000/api/matches/live/")
print("-"*80)

try:
    response = requests.get("http://localhost:8000/api/matches/live/", timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Total de partidas: {data['count']}")
        print(f"✅ Source: {data['source']}")
        
        if data['count'] > 0:
            print(f"\n📋 Primeiras 3 partidas:")
            for idx, match in enumerate(data['matches'][:3], 1):
                home = match['home_team']['name']
                away = match['away_team']['name']
                score_h = match['home_score']
                score_a = match['away_score']
                status = match['status']
                fixture_id = match['id']
                
                print(f"   {idx}. [{fixture_id}] {home} {score_h} x {score_a} {away} ({status})")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"Resposta: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Backend não está rodando!")
    print("Execute: python manage.py runserver")
except Exception as e:
    print(f"❌ Erro: {e}")

# 2. Verificar Frontend
print("\n\n2️⃣ FRONTEND: http://localhost:3001")
print("-"*80)

try:
    response = requests.get("http://localhost:3001", timeout=5)
    
    if response.status_code == 200:
        print(f"✅ Frontend está rodando (Status: {response.status_code})")
    else:
        print(f"⚠️  Frontend retornou: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Frontend não está rodando!")
    print("Execute: npm run dev (na pasta frontend)")
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "="*80)
print("🎯 PRÓXIMOS PASSOS:")
print("="*80)
print("1. Acesse: http://localhost:3001")
print("2. Clique no filtro: 🔴 Ao Vivo")
print("3. Você deve ver as 16 partidas ao vivo")
print()
print("Se ainda não aparecer:")
print("- Abra o Console do navegador (F12)")
print("- Verifique se há erros")
print("- Veja os logs da requisição para /api/matches/live/")
print("="*80 + "\n")
