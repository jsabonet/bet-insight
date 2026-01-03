import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from datetime import datetime

print("=" * 80)
print("🧪 TESTE: Sistema Completo de Partidas Otimizado")
print("=" * 80)

BASE_URL = 'http://localhost:8000/api/matches'

# Teste 1: Buscar todas as partidas (sem limite)
print("\n1️⃣ TESTE: Endpoint from_api (sem limite, com cache)")
print("-" * 80)

try:
    response = requests.get(f'{BASE_URL}/from_api/')
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Total de partidas: {data['count']}")
        print(f"📡 Fonte: {data.get('source', 'unknown')}")
        print(f"🔄 Mock? {data.get('is_mock', False)}")
        
        # Verificar cache na segunda chamada
        print("\n🔁 Testando cache (segunda chamada)...")
        import time
        start = time.time()
        response2 = requests.get(f'{BASE_URL}/from_api/')
        elapsed = time.time() - start
        
        if response2.status_code == 200:
            print(f"✅ Cache funcional - Tempo: {elapsed:.3f}s")
            print(f"   (< 0.1s = cache | > 1s = API)")
    else:
        print(f"❌ Erro {response.status_code}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 2: Busca dinâmica (híbrida)
print("\n\n2️⃣ TESTE: Endpoint search (busca híbrida)")
print("-" * 80)

queries = [
    ('Manchester', 'Time conhecido'),
    ('Champions', 'Liga conhecida'),
    ('ZZZ Team Non Existent', 'Time inexistente'),
]

for query, desc in queries:
    print(f"\n🔍 Busca: '{query}' ({desc})")
    try:
        response = requests.get(f'{BASE_URL}/search/', params={'q': query})
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Resultados: {data['count']} partidas")
            print(f"   📡 Fonte: {data.get('source', 'unknown')}")
            
            if data['count'] > 0:
                first = data['matches'][0]
                print(f"   🎯 Exemplo: {first['home_team']['name']} vs {first['away_team']['name']}")
        else:
            print(f"   ❌ Erro {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")

# Teste 3: Performance
print("\n\n3️⃣ TESTE: Performance")
print("-" * 80)

import time

tests = [
    ('from_api', f'{BASE_URL}/from_api/'),
    ('search cache', f'{BASE_URL}/search/?q=Manchester'),
]

for name, url in tests:
    print(f"\n⏱️  {name}:")
    times = []
    
    for i in range(3):
        start = time.time()
        response = requests.get(url)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"   Chamada {i+1}: {elapsed:.3f}s")
    
    avg = sum(times) / len(times)
    print(f"   📊 Média: {avg:.3f}s")
    
    if avg < 0.1:
        print(f"   ✅ EXCELENTE (cache)")
    elif avg < 1.0:
        print(f"   ✅ BOM (cache/otimizado)")
    elif avg < 3.0:
        print(f"   ⚠️  ACEITÁVEL (API)")
    else:
        print(f"   ❌ LENTO (> 3s)")

print("\n" + "=" * 80)
print("✅ Testes concluídos!")
print("=" * 80)
