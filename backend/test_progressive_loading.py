"""
Teste rápido do fluxo Progressive Loading + Cache
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_unified_analysis():
    """Testa o endpoint unificado com cache."""
    
    print("🚀 TESTE: Unified Analysis + Cache Inteligente\n")
    print("="*80)
    
    # Login
    print("1. Fazendo login...")
    login_response = requests.post(f"{BASE_URL}/users/auth/login/", json={
        "username": "admin",
        "password": "admin"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.status_code}")
        return
    
    token = login_response.json()['access']
    headers = {'Authorization': f'Bearer {token}'}
    print("✅ Login OK\n")
    
    # Buscar primeiro jogo
    print("2. Buscando primeiro jogo...")
    matches_response = requests.get(f"{BASE_URL}/matches/today/", headers=headers)
    
    if matches_response.status_code != 200 or not matches_response.json().get('results'):
        print(f"❌ Nenhum jogo encontrado")
        return
    
    match = matches_response.json()['results'][0]
    match_id = match['id']
    print(f"✅ Match ID: {match_id} - {match['home_team']['name']} vs {match['away_team']['name']}\n")
    
    # Teste 1: Cache MISS (primeira chamada)
    print("="*80)
    print("3. TESTE 1: Cache MISS (primeira chamada)\n")
    
    start = time.time()
    response1 = requests.post(
        f"{BASE_URL}/matches/{match_id}/unified-analysis/",
        headers=headers,
        json={
            "strategy": "value",
            "include_ai": True,
            "force_refresh": False
        }
    )
    elapsed1 = time.time() - start
    
    if response1.status_code != 200:
        print(f"❌ Erro: {response1.status_code}")
        print(response1.text)
        return
    
    data1 = response1.json()
    
    print(f"⏱️  Tempo: {elapsed1:.2f}s")
    print(f"💾 Cached: {data1.get('cached')}")
    print(f"📊 Cache Stats: {data1.get('cache_stats')}\n")
    
    print("Dados retornados:")
    print(f"  ✅ statistical_data: {'✓' if data1.get('statistical_data') else '✗'}")
    print(f"  ✅ decision_data: {'✓' if data1.get('decision_data') else '✗'}")
    print(f"  ✅ top_bets: {len(data1.get('decision_data', {}).get('top_bets', []))} apostas")
    print(f"  ✅ ai_analysis: {len(data1.get('ai_analysis', '') or '')} caracteres")
    
    # Teste 2: Cache HIT (segunda chamada)
    print("\n" + "="*80)
    print("4. TESTE 2: Cache HIT (segunda chamada imediata)\n")
    
    start = time.time()
    response2 = requests.post(
        f"{BASE_URL}/matches/{match_id}/unified-analysis/",
        headers=headers,
        json={
            "strategy": "value",
            "include_ai": True,
            "force_refresh": False
        }
    )
    elapsed2 = time.time() - start
    
    data2 = response2.json()
    
    print(f"⏱️  Tempo: {elapsed2:.2f}s")
    print(f"💾 Cached: {data2.get('cached')}")
    print(f"📊 Cache Stats: {data2.get('cache_stats')}")
    
    # Comparação
    print("\n" + "="*80)
    print("5. COMPARAÇÃO DE PERFORMANCE\n")
    
    speedup = (elapsed1 / elapsed2) if elapsed2 > 0 else 0
    print(f"  Cache MISS: {elapsed1:.2f}s")
    print(f"  Cache HIT:  {elapsed2:.2f}s")
    print(f"  Speedup:    {speedup:.1f}x mais rápido 🚀")
    
    improvement = ((elapsed1 - elapsed2) / elapsed1) * 100
    print(f"  Melhoria:   {improvement:.1f}% redução no tempo")
    
    # Teste 3: Estratégia diferente (outro cache)
    print("\n" + "="*80)
    print("6. TESTE 3: Estratégia MULTIPLE (cache separado)\n")
    
    start = time.time()
    response3 = requests.post(
        f"{BASE_URL}/matches/{match_id}/unified-analysis/",
        headers=headers,
        json={
            "strategy": "multiple",
            "include_ai": True,
            "force_refresh": False
        }
    )
    elapsed3 = time.time() - start
    
    data3 = response3.json()
    
    print(f"⏱️  Tempo: {elapsed3:.2f}s")
    print(f"💾 Cached: {data3.get('cached')}")
    print(f"📊 Strategy: {data3.get('strategy')}")
    print(f"📊 Top bets: {len(data3.get('decision_data', {}).get('top_bets', []))}")
    
    # Cache stats finais
    print("\n" + "="*80)
    print("7. ESTATÍSTICAS FINAIS DO CACHE\n")
    
    final_stats = data3.get('cache_stats', {})
    print(f"  Tamanho: {final_stats.get('size')}/{final_stats.get('max_size')} entradas")
    print(f"  Hits: {final_stats.get('hits')}")
    print(f"  Misses: {final_stats.get('misses')}")
    print(f"  Hit Rate: {final_stats.get('hit_rate')}%")
    print(f"  TTL: {final_stats.get('ttl_minutes')} minutos")
    
    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("="*80)

if __name__ == "__main__":
    test_unified_analysis()
