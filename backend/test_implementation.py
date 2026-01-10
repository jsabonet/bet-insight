import requests
import json

print("\n🧪 TESTANDO IMPLEMENTAÇÃO H2H + FORM + STANDINGS")
print("=" * 60)

try:
    url = "http://localhost:8000/api/matches/api_detail/?id=1391001"
    print(f"\n📡 Chamando: {url}")
    
    response = requests.get(url)
    response.raise_for_status()
    
    data = response.json()
    match = data.get('match', {})
    
    print("\n✅ DADOS RECEBIDOS:")
    print("-" * 60)
    print(f"📊 H2H: {len(match.get('h2h', []))} confrontos")
    print(f"🏠 Últimos jogos casa: {len(match.get('home_last_matches', []))} partidas")
    print(f"✈️  Últimos jogos fora: {len(match.get('away_last_matches', []))} partidas")
    print(f"🏆 Classificação: {len(match.get('standings', []))} ligas")
    
    # Detalhes H2H
    h2h = match.get('h2h', [])
    if h2h:
        print("\n📋 AMOSTRA H2H (3 primeiros):")
        for game in h2h[:3]:
            home = game['teams']['home']['name']
            away = game['teams']['away']['name']
            home_goals = game['goals']['home']
            away_goals = game['goals']['away']
            date = game['fixture']['date'][:10]
            print(f"  • {home} {home_goals} x {away_goals} {away} - {date}")
    
    # Classificação
    standings = match.get('standings', [])
    if standings and len(standings) > 0:
        print("\n🏆 CLASSIFICAÇÃO:")
        table = standings[0]['league']['standings'][0]
        
        # Procurar Getafe e Real Sociedad
        for team in table:
            if team['team']['id'] in [546, 548]:  # IDs dos times
                name = team['team']['name']
                rank = team['rank']
                points = team['points']
                form = team.get('form', '')
                icon = "🔵" if team['team']['id'] == 546 else "🔴"
                print(f"  {icon} {name}: {rank}º - {points}pts - Forma: {form}")
    
    # Team IDs
    print("\n🆔 TEAM IDs:")
    home_team = match.get('home_team', {})
    away_team = match.get('away_team', {})
    print(f"  Casa: {home_team.get('name')} (ID: {home_team.get('id')})")
    print(f"  Fora: {away_team.get('name')} (ID: {away_team.get('id')})")
    
    print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)

except requests.exceptions.ConnectionError:
    print("\n❌ ERRO: Servidor não está rodando em http://localhost:8000")
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
