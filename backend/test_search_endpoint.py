import requests

print("🧪 Testando endpoint /api/matches/search/")
print("=" * 60)

try:
    response = requests.get('http://localhost:8000/api/matches/search/', params={'q': 'Barcelona'})
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Sucesso!")
        print(f"   Query: {data.get('query')}")
        print(f"   Resultados: {data.get('count')}")
        print(f"   Fonte: {data.get('source')}")
        
        if data.get('matches'):
            print(f"\n🎯 Primeira partida:")
            match = data['matches'][0]
            print(f"   {match['home_team']['name']} vs {match['away_team']['name']}")
            print(f"   Liga: {match['league']['name']}")
    else:
        print(f"❌ Erro {response.status_code}")
        print(f"   {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

print("=" * 60)
