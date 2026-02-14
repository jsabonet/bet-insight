"""
Busca o resultado real da partida 1520391 (Atletico Madrid vs Barcelona)
"""
import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

API_KEY = os.getenv('APIFOOTBALL_KEY')
BASE_URL = "https://v3.football.api-sports.io"

def fetch_fixture_result(fixture_id):
    """Busca resultado de uma partida específica"""
    url = f"{BASE_URL}/fixtures"
    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': 'v3.football.api-sports.io'
    }
    params = {'id': fixture_id}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('response'):
            return data['response'][0]
        return None
    except Exception as e:
        print(f"Erro ao buscar partida: {e}")
        return None

def main():
    print("\nBuscando resultado da partida ID 1520391 via API-Football...")
    print("Aguarde...\n")
    
    match_data = fetch_fixture_result(1520391)
    
    if not match_data:
        print("\n❌ Erro ao buscar dados da partida")
        print("Possíveis motivos:")
        print("  - Partida ainda não foi realizada")
        print("  - ID incorreto")
        print("  - Limite de requests da API atingido")
        return
    
    print("\n" + "="*80)
    print("RESULTADO REAL DA PARTIDA 1520391")
    print("="*80)
    
    fixture = match_data.get('fixture', {})
    teams = match_data.get('teams', {})
    goals = match_data.get('goals', {})
    score = match_data.get('score', {})
    league = match_data.get('league', {})
    
    print(f"\nCOMPETICAO: {league.get('name')} - {league.get('round')}")
    print(f"Partida: {teams.get('home', {}).get('name')} vs {teams.get('away', {}).get('name')}")
    print(f"Data: {fixture.get('date')}")
    print(f"Status: {fixture.get('status', {}).get('long')}")
    
    # Placar final
    if goals:
        home_goals = goals.get('home')
        away_goals = goals.get('away')
        
        print(f"\n{'='*80}")
        print(f" PLACAR FINAL:")
        print(f"{'='*80}")
        print(f"   {teams.get('home', {}).get('name')}: {home_goals} gols")
        print(f"   {teams.get('away', {}).get('name')}: {away_goals} gols")
        
        # Resultado
        if home_goals is not None and away_goals is not None:
            total_goals = home_goals + away_goals
            
            print(f"\n RESUMO:")
            print(f"   Total de gols: {total_goals}")
            
            if home_goals > away_goals:
                print(f"   Resultado: Vitoria CASA ({teams.get('home', {}).get('name')})")
                resultado_1x2 = "Casa"
            elif away_goals > home_goals:
                print(f"   Resultado: Vitoria FORA ({teams.get('away', {}).get('name')})")
                resultado_1x2 = "Fora"
            else:
                print(f"   Resultado: EMPATE")
                resultado_1x2 = "Empate"
            
            print(f"\n{'='*80}")
            print(f" VERIFICACAO DOS MERCADOS:")
            print(f"{'='*80}")
            print(f"   1X2: {resultado_1x2}")
            print(f"   Over 2.5: {'GREEN' if total_goals > 2.5 else 'RED'} ({total_goals} gols)")
            print(f"   Under 2.5: {'GREEN' if total_goals < 2.5 else 'RED'} ({total_goals} gols)")
            print(f"   BTTS (Ambos Marcam): {'GREEN (Sim)' if home_goals > 0 and away_goals > 0 else 'RED (Nao)'}")
            print(f"   Over 1.5: {'GREEN' if total_goals > 1.5 else 'RED'} ({total_goals} gols)")
            
            # Score detalhado
            if score:
                print(f"\n PLACARES POR TEMPO:")
                halftime = score.get('halftime', {})
                fulltime = score.get('fulltime', {})
                extratime = score.get('extratime', {})
                penalty = score.get('penalty', {})
                
                if halftime and halftime.get('home') is not None:
                    print(f"   Intervalo: {halftime.get('home')} - {halftime.get('away')}")
                if fulltime and fulltime.get('home') is not None:
                    print(f"   Tempo Normal: {fulltime.get('home')} - {fulltime.get('away')}")
                if extratime and (extratime.get('home') is not None):
                    print(f"   Prorrogacao: {extratime.get('home')} - {extratime.get('away')}")
                if penalty and (penalty.get('home') is not None):
                    print(f"   Penaltis: {penalty.get('home')} - {penalty.get('away')}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()
