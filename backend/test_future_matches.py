import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from datetime import datetime, timedelta

print("=" * 80)
print("🧪 TESTE: Sistema de Carregamento de Partidas Futuras")
print("=" * 80)

# Testar endpoint from_api
print("\n📡 Testando endpoint /api/matches/from_api/")
print(f"Data/Hora atual: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

try:
    response = requests.get('http://localhost:8000/api/matches/from_api/')
    
    if response.status_code == 200:
        data = response.json()
        matches = data.get('matches', [])
        
        print(f"\n✅ Resposta bem-sucedida!")
        print(f"   Total de partidas: {len(matches)}")
        print(f"   Fonte: {data.get('source', 'unknown')}")
        print(f"   Mock? {data.get('is_mock', False)}")
        
        if matches:
            # Analisar distribuição temporal
            now = datetime.now()
            today = now.date()
            
            matches_by_day = {}
            past_matches = 0
            future_matches = 0
            
            for match in matches:
                match_date = datetime.fromisoformat(match['match_date'].replace('Z', '+00:00'))
                day = match_date.date()
                
                if day not in matches_by_day:
                    matches_by_day[day] = []
                matches_by_day[day].append(match)
                
                if match_date < now:
                    past_matches += 1
                else:
                    future_matches += 1
            
            print(f"\n📊 Análise Temporal:")
            print(f"   ❌ Partidas passadas: {past_matches}")
            print(f"   ✅ Partidas futuras: {future_matches}")
            
            print(f"\n📅 Distribuição por dia:")
            for day in sorted(matches_by_day.keys()):
                count = len(matches_by_day[day])
                days_from_now = (day - today).days
                status = "HOJE" if days_from_now == 0 else f"+{days_from_now}d"
                print(f"   {day.strftime('%Y-%m-%d')} ({status:>6}): {count:>3} partidas")
            
            # Mostrar primeiras e últimas partidas
            print(f"\n🔍 Primeira partida:")
            first = matches[0]
            print(f"   {first['match_date'][:16]} | {first['home_team']['name']} vs {first['away_team']['name']}")
            
            print(f"\n🔍 Última partida:")
            last = matches[-1]
            print(f"   {last['match_date'][:16]} | {last['home_team']['name']} vs {last['away_team']['name']}")
            
            # Validações
            print(f"\n✅ VALIDAÇÕES:")
            if past_matches == 0:
                print(f"   ✅ Nenhuma partida passada (correto!)")
            else:
                print(f"   ❌ ERRO: {past_matches} partidas passadas encontradas")
            
            max_day = max(matches_by_day.keys())
            days_ahead = (max_day - today).days
            if days_ahead <= 14:
                print(f"   ✅ Carregamento até +{days_ahead} dias (dentro do limite)")
            else:
                print(f"   ⚠️  Carregamento até +{days_ahead} dias (excede 14 dias)")
                
        else:
            print("\n⚠️  Nenhuma partida retornada")
            
    else:
        print(f"\n❌ Erro {response.status_code}")
        print(response.text[:500])
        
except Exception as e:
    print(f"\n❌ Erro na requisição: {e}")

print("\n" + "=" * 80)
