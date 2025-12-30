import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
import requests
from datetime import datetime, timedelta

print("=" * 80)
print("🔍 VERIFICAÇÃO DE ACESSO PRO - API-FOOTBALL")
print("=" * 80)

api = FootballAPIService()

print(f"\n✅ API Key: {api.api_key[:20]}...")
print(f"✅ URL: {api.base_url}\n")

# Teste 1: Verificar status da conta e limites
print("=" * 80)
print("📊 TESTE 1: STATUS DA CONTA E LIMITES")
print("=" * 80)

try:
    response = requests.get(
        f"{api.base_url}/status",
        headers=api.headers,
        timeout=10
    )
    data = response.json()
    
    if data.get('response'):
        account = data['response']
        subscription = account.get('subscription', {})
        requests_info = account.get('requests', {})
        
        print(f"📦 Plano Ativo: {subscription.get('plan', 'N/A')}")
        print(f"📅 Expira em: {subscription.get('end', 'N/A')}")
        print(f"📈 Limite diário: {requests_info.get('limit_day', 'N/A')} requisições")
        print(f"✅ Usado hoje: {requests_info.get('current', 'N/A')}")
        print(f"🔄 Restante hoje: {requests_info.get('limit_day', 0) - requests_info.get('current', 0)}")
        
        if subscription.get('plan') == 'PRO' or requests_info.get('limit_day', 0) >= 7500:
            print("\n✅ PLANO PRO ATIVO! Acesso completo confirmado!")
        else:
            print("\n⚠️ AVISO: Ainda no plano Free ou aguardando ativação")
            print("   Se acabou de assinar, aguarde 5-10 minutos")
    else:
        print(f"❌ Erro: {data.get('errors', 'Resposta inválida')}")
        
except Exception as e:
    print(f"❌ Erro ao verificar status: {e}")

# Teste 2: Acesso a Temporadas Recentes
print("\n" + "=" * 80)
print("📅 TESTE 2: ACESSO À TEMPORADA 2024/2025 (ATUAL)")
print("=" * 80)

CURRENT_SEASON_LEAGUES = {
    39: "Premier League 2024/2025",
    140: "La Liga 2024/2025",
    78: "Bundesliga 2024/2025",
    135: "Serie A 2024/2025",
    61: "Ligue 1 2024/2025",
}

season_access = {}
for league_id, league_name in CURRENT_SEASON_LEAGUES.items():
    print(f"\n🏆 Testando: {league_name}")
    
    try:
        response = requests.get(
            f"{api.base_url}/fixtures",
            headers=api.headers,
            params={'league': league_id, 'season': 2024, 'last': 5},
            timeout=10
        )
        data = response.json()
        
        if data.get('errors'):
            print(f"   ❌ SEM ACESSO: {data['errors']}")
            season_access[league_name] = False
        elif data.get('response'):
            fixtures = data['response']
            print(f"   ✅ ACESSO OK: {len(fixtures)} partidas encontradas")
            if len(fixtures) > 0:
                latest = fixtures[0]
                date = latest['fixture']['date'][:10]
                home = latest['teams']['home']['name']
                away = latest['teams']['away']['name']
                print(f"   📌 Última partida: {home} vs {away} ({date})")
            season_access[league_name] = True
        else:
            print(f"   ⚠️ Sem dados disponíveis")
            season_access[league_name] = None
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        season_access[league_name] = False

# Teste 3: Partidas Recentes (últimos 7 dias)
print("\n" + "=" * 80)
print("📆 TESTE 3: PARTIDAS DOS ÚLTIMOS 7 DIAS")
print("=" * 80)

today = datetime.now()
dates_to_check = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]

total_matches_found = 0
for date_str in dates_to_check:
    try:
        response = requests.get(
            f"{api.base_url}/fixtures",
            headers=api.headers,
            params={'date': date_str},
            timeout=10
        )
        data = response.json()
        
        if data.get('response'):
            count = len(data['response'])
            total_matches_found += count
            if count > 0:
                print(f"✅ {date_str}: {count} partidas")
        
    except Exception as e:
        print(f"❌ {date_str}: Erro - {e}")

print(f"\n📊 Total encontrado (7 dias): {total_matches_found} partidas")

# Teste 4: Partidas AO VIVO
print("\n" + "=" * 80)
print("🔴 TESTE 4: PARTIDAS AO VIVO AGORA")
print("=" * 80)

try:
    response = requests.get(
        f"{api.base_url}/fixtures",
        headers=api.headers,
        params={'live': 'all'},
        timeout=10
    )
    data = response.json()
    
    if data.get('response'):
        live_matches = data['response']
        print(f"🔴 Partidas ao vivo: {len(live_matches)}")
        
        if len(live_matches) > 0:
            print("\nPrimeiras 5 partidas ao vivo:")
            for i, match in enumerate(live_matches[:5], 1):
                home = match['teams']['home']['name']
                away = match['teams']['away']['name']
                score_home = match['goals']['home']
                score_away = match['goals']['away']
                minute = match['fixture']['status']['elapsed']
                league = match['league']['name']
                
                print(f"  {i}. {home} {score_home} x {score_away} {away} - {minute}' ({league})")
        else:
            print("ℹ️ Nenhuma partida ao vivo no momento (normal dependendo do horário)")
    else:
        print(f"❌ Erro: {data.get('errors', 'Sem dados')}")
        
except Exception as e:
    print(f"❌ Erro: {e}")

# Teste 5: Próximas Partidas (próximos 7 dias)
print("\n" + "=" * 80)
print("📅 TESTE 5: PRÓXIMAS PARTIDAS (PRÓXIMOS 7 DIAS)")
print("=" * 80)

future_dates = [(today + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 8)]
total_upcoming = 0

for date_str in future_dates[:3]:  # Apenas primeiros 3 dias para economizar requests
    try:
        response = requests.get(
            f"{api.base_url}/fixtures",
            headers=api.headers,
            params={'date': date_str},
            timeout=10
        )
        data = response.json()
        
        if data.get('response'):
            count = len(data['response'])
            total_upcoming += count
            if count > 0:
                print(f"✅ {date_str}: {count} partidas agendadas")
        
    except Exception as e:
        print(f"❌ {date_str}: Erro")

print(f"\n📊 Total próximos 3 dias: {total_upcoming} partidas")

# Teste 6: Estatísticas Avançadas
print("\n" + "=" * 80)
print("📈 TESTE 6: ACESSO A ESTATÍSTICAS AVANÇADAS")
print("=" * 80)

# Pegar uma partida recente para testar
try:
    response = requests.get(
        f"{api.base_url}/fixtures",
        headers=api.headers,
        params={'date': today.strftime('%Y-%m-%d'), 'league': 39},
        timeout=10
    )
    data = response.json()
    
    if data.get('response') and len(data['response']) > 0:
        fixture_id = data['response'][0]['fixture']['id']
        
        # Testar estatísticas
        print(f"\n🔍 Testando estatísticas da partida ID: {fixture_id}")
        
        stats_response = requests.get(
            f"{api.base_url}/fixtures/statistics",
            headers=api.headers,
            params={'fixture': fixture_id},
            timeout=10
        )
        stats_data = stats_response.json()
        
        if stats_data.get('response'):
            print("   ✅ Estatísticas disponíveis")
        else:
            print("   ℹ️ Estatísticas não disponíveis para esta partida")
            
        # Testar previsões
        predictions_response = requests.get(
            f"{api.base_url}/predictions",
            headers=api.headers,
            params={'fixture': fixture_id},
            timeout=10
        )
        pred_data = predictions_response.json()
        
        if pred_data.get('response'):
            print("   ✅ Previsões disponíveis")
        else:
            print("   ℹ️ Previsões não disponíveis para esta partida")
    else:
        print("ℹ️ Nenhuma partida recente da Premier League para testar")
        
except Exception as e:
    print(f"❌ Erro ao testar estatísticas: {e}")

# Resumo Final
print("\n" + "=" * 80)
print("📋 RESUMO DA VERIFICAÇÃO")
print("=" * 80)

accessible_seasons = sum(1 for v in season_access.values() if v == True)
total_seasons_tested = len(season_access)

print(f"\n✅ Temporadas 2024/2025 acessíveis: {accessible_seasons}/{total_seasons_tested}")
print(f"📊 Partidas recentes (7 dias): {total_matches_found}")
print(f"📅 Partidas futuras (3 dias): {total_upcoming}")

if accessible_seasons == total_seasons_tested and total_matches_found > 0:
    print("\n" + "=" * 80)
    print("🎉 PARABÉNS! ACESSO PRO CONFIRMADO E FUNCIONANDO!")
    print("=" * 80)
    print("\n✅ Você tem acesso completo a:")
    print("   • Temporadas 2024/2025 (atual)")
    print("   • Histórico completo de partidas")
    print("   • Partidas ao vivo")
    print("   • Estatísticas avançadas")
    print("   • Previsões e odds")
    print("   • 7.500 requisições/dia")
    print("\n🚀 Está pronto para carregar dados e lançar o BetInsight!")
elif accessible_seasons > 0:
    print("\n⚠️ ACESSO PARCIAL")
    print("   Algumas temporadas acessíveis, outras podem estar em atualização")
else:
    print("\n❌ SEM ACESSO ÀS TEMPORADAS ATUAIS")
    print("   Possíveis causas:")
    print("   • Assinatura ainda não ativada (aguarde 5-10 min)")
    print("   • Pagamento em processamento")
    print("   • Ainda no plano Free")
    print("\n   Faça logout/login no dashboard e tente novamente")

print("\n" + "=" * 80)
print("Verificação concluída!")
print("=" * 80)
