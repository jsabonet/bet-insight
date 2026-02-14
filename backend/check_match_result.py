"""
Busca resultado da partida 1520391 via Django shell
"""
from apps.core.models import Match
from apps.analysis.services.api_football_service import FootballAPIService
import json

match_id = 1520391

print("\n" + "="*80)
print(f"RESULTADO DA PARTIDA {match_id}")
print("="*80)

# Tentar banco de dados primeiro
print("\n🔍 Buscando no banco de dados...")
match = Match.objects.filter(api_id=match_id).first()

if match:
    print(f"✅ Encontrado no banco!")
    print(f"\n📊 INFORMAÇÕES:")
    print(f"   {match.home_team} vs {match.away_team}")
    print(f"   Data: {match.match_date}")
    print(f"   Liga: {match.league}")
    print(f"   Status: {match.status}")
    
    if match.home_score is not None:
        print(f"\n⚽ PLACAR FINAL:")
        print(f"   {match.home_team}: {match.home_score}")
        print(f"   {match.away_team}: {match.away_score}")
        
        total = match.home_score + match.away_score
        
        print(f"\n📈 VERIFICAÇÃO DOS MERCADOS:")
        print(f"   Total de gols: {total}")
        print(f"   Over 2.5: {'✅ GREEN' if total > 2.5 else '❌ RED'} ({total} gols)")
        print(f"   Under 2.5: {'✅ GREEN' if total < 2.5 else '❌ RED'} ({total} gols)")
        print(f"   BTTS: {'✅ GREEN' if match.home_score > 0 and match.away_score > 0 else '❌ RED'}")
        
        if match.home_score > match.away_score:
            print(f"   Resultado 1X2: Casa venceu")
        elif match.away_score > match.home_score:
            print(f"   Resultado 1X2: Fora venceu")
        else:
            print(f"   Resultado 1X2: Empate")
    else:
        print(f"\n⏳ Partida ainda não realizada")
else:
    print(f"❌ Não encontrado no banco")
    print(f"\n🌐 Buscando via API-Football...")
    
    api = FootballAPIService()
    fixture = api.fetch_fixture_by_id(match_id)
    
    if fixture:
        teams = fixture.get('teams', {})
        goals = fixture.get('goals', {})
        league = fixture.get('league', {})
        status = fixture.get('fixture', {}).get('status', {})
        
        print(f"\n✅ Dados recebidos!")
        print(f"\n📊 INFORMAÇÕES:")
        print(f"   {teams.get('home', {}).get('name')} vs {teams.get('away', {}).get('name')}")
        print(f"   Liga: {league.get('name')} - {league.get('round')}")
        print(f"   Status: {status.get('long')}")
        
        if goals.get('home') is not None:
            home_score = goals['home']
            away_score = goals['away']
            total = home_score + away_score
            
            print(f"\n⚽ PLACAR FINAL:")
            print(f"   {teams.get('home', {}).get('name')}: {home_score}")
            print(f"   {teams.get('away', {}).get('name')}: {away_score}")
            
            print(f"\n📈 VERIFICAÇÃO DOS MERCADOS:")
            print(f"   Total de gols: {total}")
            print(f"   Over 2.5: {'✅ GREEN' if total > 2.5 else '❌ RED'} ({total} gols)")
            print(f"   Under 2.5: {'✅ GREEN' if total < 2.5 else '❌ RED'} ({total} gols)")
            print(f"   BTTS: {'✅ GREEN' if home_score > 0 and away_score > 0 else '❌ RED'}")
            
            if home_score > away_score:
                print(f"   Resultado 1X2: Casa venceu")
            elif away_score > home_score:
                print(f"   Resultado 1X2: Fora venceu")
            else:
                print(f"   Resultado 1X2: Empate")
    else:
        print(f"❌ Erro ao buscar da API")

print("\n" + "="*80)
