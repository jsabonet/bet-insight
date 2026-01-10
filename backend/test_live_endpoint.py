"""
Testar endpoint /api/matches/live/
"""

import requests
import json

BASE_URL = "http://localhost:8000"

print("\n" + "="*80)
print("🔍 TESTANDO ENDPOINT /api/matches/live/")
print("="*80 + "\n")

# 1. Testar endpoint live
print("1️⃣ GET /api/matches/live/")
print("-"*80)

try:
    response = requests.get(f"{BASE_URL}/api/matches/live/", timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCESSO!")
        print(f"Tipo de resposta: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Chaves: {list(data.keys())}")
            if 'matches' in data:
                print(f"Total de partidas: {len(data['matches'])}")
            elif 'results' in data:
                print(f"Total de resultados: {len(data['results'])}")
        elif isinstance(data, list):
            print(f"Total de itens: {len(data)}")
            if len(data) > 0:
                print(f"\nPrimeiro item:")
                print(json.dumps(data[0], indent=2, ensure_ascii=False)[:500])
        
        print(f"\nResposta completa (primeiros 1000 chars):")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
    else:
        print(f"\n❌ ERRO {response.status_code}")
        print(f"Resposta: {response.text[:500]}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERRO: Backend não está rodando!")
    print("Execute: python manage.py runserver")
except Exception as e:
    print(f"❌ ERRO: {e}")

# 2. Verificar se há partidas AO VIVO na API diretamente
print("\n\n2️⃣ VERIFICAR API-FOOTBALL (partidas ao vivo)")
print("-"*80)

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService

api = FootballAPIService()
live_result = api.get_live_fixtures()

if live_result['success']:
    fixtures = live_result['fixtures']
    print(f"✅ {len(fixtures)} partidas ao vivo na API-Football")
    
    if len(fixtures) > 0:
        print("\nPrimeiras 3:")
        for idx, f in enumerate(fixtures[:3], 1):
            home = f['teams']['home']['name']
            away = f['teams']['away']['name']
            score_h = f['goals']['home'] or 0
            score_a = f['goals']['away'] or 0
            status = f['fixture']['status']['short']
            fixture_id = f['fixture']['id']
            print(f"   {idx}. [{fixture_id}] {home} {score_h} x {score_a} {away} ({status})")
else:
    print(f"❌ Erro: {live_result.get('error')}")

# 3. Verificar database (partidas com status='live')
print("\n\n3️⃣ VERIFICAR DATABASE (Match.objects.filter(status='live'))")
print("-"*80)

from apps.matches.models import Match

live_matches_db = Match.objects.filter(status='live')
print(f"Total de partidas com status='live' no DB: {live_matches_db.count()}")

if live_matches_db.count() > 0:
    print("\nPartidas encontradas:")
    for m in live_matches_db[:5]:
        print(f"   - [{m.id}] {m.home_team.name} vs {m.away_team.name}")

print("\n" + "="*80)
print("🎯 DIAGNÓSTICO:")
print("="*80)
print("📌 Se API-Football tem partidas ao vivo mas /api/matches/live/ retorna vazio:")
print("   → O endpoint está consultando apenas o DATABASE, não a API")
print("   → Solução: Modificar o endpoint 'live' para buscar da API em tempo real")
print()
print("📌 Se /api/matches/live/ retorna erro 401/403:")
print("   → Problema de autenticação")
print("   → Solução: Remover IsAuthenticated ou fazer login")
print("="*80 + "\n")
