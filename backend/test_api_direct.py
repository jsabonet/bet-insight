"""
Teste direto da API para fixture 1520391
"""
import requests
import json

# Tentar com diferentes métodos
match_id = 1520391

print("\n" + "="*80)
print(f"BUSCANDO PARTIDA {match_id} - TESTE DIRETO")
print("="*80)

# Método 1: Via cache/database do Django
try:
    import os
    import sys
    import django
    
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    
    from apps.core.models import Match
    
    print("\n1️⃣ Buscando no banco de dados local...")
    
    match = Match.objects.filter(api_id=match_id).first()
    
    if match:
        print(f"✅ Partida encontrada no banco!")
        print(f"\n📊 DADOS DA PARTIDA:")
        print(f"   ID: {match.api_id}")
        print(f"   Casa: {match.home_team}")
        print(f"   Fora: {match.away_team}")
        print(f"   Data: {match.match_date}")
        print(f"   Status: {match.status}")
        
        if match.home_score is not None and match.away_score is not None:
            print(f"\n⚽ PLACAR:")
            print(f"   {match.home_team}: {match.home_score}")
            print(f"   {match.away_team}: {match.away_score}")
            
            total = match.home_score + match.away_score
            print(f"\n📈 MERCADOS:")
            print(f"   Total de gols: {total}")
            print(f"   Over 2.5: {'✅ GREEN' if total > 2.5 else '❌ RED'}")
            print(f"   BTTS: {'✅ GREEN' if match.home_score > 0 and match.away_score > 0 else '❌ RED'}")
        else:
            print(f"\n⏳ Partida ainda não foi realizada ou placar não disponível")
    else:
        print(f"❌ Partida não encontrada no banco de dados local")
        print(f"\n2️⃣ Tentando buscar via API-Football...")
        
        from apps.analysis.services.api_football_service import FootballAPIService
        
        api = FootballAPIService()
        fixture = api.fetch_fixture_by_id(match_id)
        
        if fixture:
            print(f"✅ Dados recebidos da API!")
            print(f"\n📄 RESPOSTA COMPLETA:")
            print(json.dumps(fixture, indent=2, ensure_ascii=False))
        else:
            print(f"❌ API não retornou dados")
            
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
