"""
Teste rápido: verificar quantas partidas de HOJE são encontradas
"""
import os
import sys
import django
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService

TOP_LEAGUES = [39, 140, 135, 78, 61, 94, 88, 144, 203, 2, 3, 848, 45, 137]

api = APIFootballService()
today = datetime.now().date()

print("\n" + "=" * 80)
print(f"🔍 TESTE: Verificando partidas de HOJE ({today.strftime('%d/%m/%Y')})")
print("=" * 80 + "\n")

# Buscar apenas hoje (1 dia)
all_fixtures_1_day = []
date_str = today.strftime('%Y-%m-%d')

print(f"📅 Buscando: {date_str}\n")

for league_id in TOP_LEAGUES:
    try:
        response = api.get_fixtures_by_date(date_str, league_id=league_id, season=2025)
        if response and response.get('response'):
            fixtures = response['response']
            if len(fixtures) > 0:
                all_fixtures_1_day.extend(fixtures)
                print(f"   ✅ Liga {league_id}: {len(fixtures)} partida(s)")
    except:
        pass

print("\n" + "=" * 80)
print("📊 RESULTADO - APENAS HOJE (days_ahead=1)")
print("=" * 80)
print(f"Total de partidas encontradas: {len(all_fixtures_1_day)}")
print("=" * 80)

# Comparar com busca de 3 dias
print("\n" + "=" * 80)
print("🔍 COMPARAÇÃO: Buscando próximos 3 dias")
print("=" * 80 + "\n")

all_fixtures_3_days = []
for i in range(3):
    date = today + timedelta(days=i)
    date_str = date.strftime('%Y-%m-%d')
    day_count = 0
    
    for league_id in TOP_LEAGUES:
        try:
            response = api.get_fixtures_by_date(date_str, league_id=league_id, season=2025)
            if response and response.get('response'):
                fixtures = response['response']
                day_count += len(fixtures)
                all_fixtures_3_days.extend(fixtures)
        except:
            pass
    
    if day_count > 0:
        print(f"   {date.strftime('%d/%m/%Y')}: {day_count} partidas")

print("\n" + "=" * 80)
print("📊 RESULTADO - 3 DIAS (days_ahead=3)")
print("=" * 80)
print(f"Total de partidas nos próximos 3 dias: {len(all_fixtures_3_days)}")
print("=" * 80)

print("\n" + "=" * 80)
print("✅ CONCLUSÃO")
print("=" * 80)
print(f"Com days_ahead=1 (padrão novo): {len(all_fixtures_1_day)} partidas")
print(f"Com days_ahead=3 (padrão antigo): {len(all_fixtures_3_days)} partidas")
print(f"Diferença: {len(all_fixtures_3_days) - len(all_fixtures_1_day)} partidas reduzidas")
print("=" * 80 + "\n")
