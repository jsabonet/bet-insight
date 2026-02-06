"""
Buscar resultado da partida 1508602 direto da API-Football
"""
import requests
import json

# Credenciais da API
API_KEY = "e80d6c82ac7c1d03170757f605d83531"
API_HOST = "v3.football.api-sports.io"

fixture_id = 1508602

# Fazer requisição
url = f"https://{API_HOST}/fixtures"
headers = {
    'x-rapidapi-host': API_HOST,
    'x-rapidapi-key': API_KEY
}
params = {
    'id': fixture_id
}

print(f"Buscando fixture {fixture_id}...")
print(f"URL: {url}")
print(f"Headers: {headers}")
print(f"Params: {params}")
print("="*80)

response = requests.get(url, headers=headers, params=params)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    
    print(f"Results: {data.get('results', 0)}")
    
    if data.get('response') and len(data['response']) > 0:
        fixture = data['response'][0]
        
        # Extrair dados
        fixture_info = fixture.get('fixture', {})
        teams = fixture.get('teams', {})
        goals = fixture.get('goals', {})
        score = fixture.get('score', {})
        league_info = fixture.get('league', {})
        
        print("\n" + "="*80)
        print("INFORMACOES DA PARTIDA")
        print("="*80)
        
        home_name = teams.get('home', {}).get('name', 'N/A')
        away_name = teams.get('away', {}).get('name', 'N/A')
        
        print(f"Home: {home_name}")
        print(f"Away: {away_name}")
        print(f"Liga: {league_info.get('name', 'N/A')}")
        print(f"Rodada: {league_info.get('round', 'N/A')}")
        print(f"Data: {fixture_info.get('date', 'N/A')}")
        print(f"Status: {fixture_info.get('status', {}).get('long', 'N/A')}")
        
        print("\n" + "="*80)
        print("PLACAR")
        print("="*80)
        
        # Goals (placar final)
        home_goals = goals.get('home')
        away_goals = goals.get('away')
        
        print(f"\nGOALS (Placar Final):")
        print(f"  Home: {home_goals}")
        print(f"  Away: {away_goals}")
        
        # Score detalhado
        print(f"\nSCORE (Detalhado):")
        print(f"  Halftime: {score.get('halftime', {})}")
        print(f"  Fulltime: {score.get('fulltime', {})}")
        print(f"  Extratime: {score.get('extratime', {})}")
        print(f"  Penalty: {score.get('penalty', {})}")
        
        if home_goals is not None and away_goals is not None:
            print(f"\n" + "="*80)
            print(f"RESULTADO FINAL: {home_name} {home_goals} x {away_goals} {away_name}")
            print("="*80)
            
            if home_goals > away_goals:
                print(f"Vencedor: {home_name} (CASA)")
                result_code = "home"
            elif away_goals > home_goals:
                print(f"Vencedor: {away_name} (FORA)")
                result_code = "away"
            else:
                print(f"EMPATE")
                result_code = "draw"
            
            # Mercados
            total = home_goals + away_goals
            print(f"\nMERCADOS:")
            print(f"  Total de Gols: {total}")
            print(f"  Over 2.5: {'SIM' if total > 2 else 'NAO'}")
            print(f"  BTTS: {'SIM' if home_goals > 0 and away_goals > 0 else 'NAO'}")
            
        else:
            print("\nPlacar nao disponivel")
        
        # JSON completo para debug
        print("\n" + "="*80)
        print("JSON COMPLETO (primeiros 2000 chars)")
        print("="*80)
        print(json.dumps(fixture, indent=2, ensure_ascii=False)[:2000])
        
    else:
        print("Nenhum resultado encontrado")
        print(f"Response: {json.dumps(data, indent=2)[:500]}")
else:
    print(f"Erro na requisicao: {response.status_code}")
    print(f"Response: {response.text[:500]}")
