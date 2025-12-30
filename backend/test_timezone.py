import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.utils import timezone
import pytz

print("=" * 80)
print("🌍 VERIFICAÇÃO DE FUSO HORÁRIO - MOÇAMBIQUE")
print("=" * 80)

# Configurações do Django
print(f"\n📋 Configurações Django:")
print(f"   LANGUAGE_CODE: {settings.LANGUAGE_CODE}")
print(f"   TIME_ZONE: {settings.TIME_ZONE}")
print(f"   USE_TZ: {settings.USE_TZ}")
print(f"   USE_I18N: {settings.USE_I18N}")

# Timezone atual
tz_maputo = pytz.timezone('Africa/Maputo')
tz_utc = pytz.UTC

print(f"\n🕐 Horários Atuais:")
print(f"   UTC: {datetime.now(tz_utc).strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"   Moçambique (Maputo): {datetime.now(tz_maputo).strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"   Django timezone.now(): {timezone.now().strftime('%Y-%m-%d %H:%M:%S %Z')}")

# Diferença de horário
now_utc = datetime.now(tz_utc)
now_maputo = datetime.now(tz_maputo)
diff = (now_maputo.utcoffset().total_seconds() / 3600)
print(f"\n⏰ Diferença UTC: +{int(diff)} horas (CAT - Central Africa Time)")

# Testar conversão de horários da API
print(f"\n🔄 Teste de Conversão:")
api_time_str = "2025-12-29T14:00:00+00:00"  # Exemplo de horário UTC da API
api_time = datetime.fromisoformat(api_time_str.replace('Z', '+00:00'))
api_time_maputo = api_time.astimezone(tz_maputo)

print(f"   Horário API (UTC): {api_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"   Convertido (Maputo): {api_time_maputo.strftime('%Y-%m-%d %H:%M:%S %Z')}")
print(f"   Diferença: +{int((api_time_maputo.hour - api_time.hour) % 24)} horas")

# Verificar banco de dados
print(f"\n💾 Teste com Banco de Dados:")
from apps.matches.models import Match

try:
    # Pegar uma partida recente
    recent_match = Match.objects.order_by('-match_date').first()
    
    if recent_match:
        print(f"   Partida: {recent_match.home_team.name} vs {recent_match.away_team.name}")
        print(f"   Data no BD (aware): {recent_match.match_date}")
        print(f"   Data formatada: {recent_match.match_date.strftime('%d/%m/%Y %H:%M')} CAT")
        
        # Testar se está em formato correto
        if recent_match.match_date.tzinfo is not None:
            print(f"   ✅ Timezone-aware: {recent_match.match_date.tzinfo}")
        else:
            print(f"   ❌ Timezone-naive (PROBLEMA!)")
    else:
        print(f"   ℹ️ Nenhuma partida no banco de dados ainda")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

print(f"\n" + "=" * 80)
print("📊 RESUMO")
print("=" * 80)

if settings.TIME_ZONE == 'Africa/Maputo' and settings.USE_TZ:
    print(f"✅ Configuração CORRETA!")
    print(f"   • Timezone: Africa/Maputo (CAT, UTC+2)")
    print(f"   • USE_TZ: True (armazena em UTC, exibe em Maputo)")
    print(f"   • Todas as datas serão automaticamente convertidas")
    print(f"\n💡 Quando salvar partidas da API:")
    print(f"   1. API retorna: 2025-12-29T14:00:00Z (UTC)")
    print(f"   2. Django salva: 2025-12-29 14:00:00+00:00 (UTC no BD)")
    print(f"   3. Frontend exibe: 29/12/2025 16:00 (CAT, +2h)")
else:
    print(f"⚠️ Configuração precisa ajuste!")

print("=" * 80)
