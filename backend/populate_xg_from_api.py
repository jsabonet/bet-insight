"""
Popular xG real das partidas finalizadas via API-Football
"""
import os
import sys

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import django
import time
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.matches.services.football_api import FootballAPIService

print("="*80)
print("POPULANDO xG REAL DAS PARTIDAS VIA API-FOOTBALL")
print("="*80)

# Inicializar API
api = FootballAPIService()

# Ligas principais (maior chance de ter xG)
MAIN_LEAGUES = [
    'Premier League',
    'La Liga', 
    'Serie A',
    'Bundesliga',
    'Ligue 1',
    'Primeira Liga',
    'Eredivisie',
    'Champions League',
    'Europa League',
]

print(f"\n📊 CONFIGURAÇÃO:")
print(f"   Ligas principais: {len(MAIN_LEAGUES)}")
print(f"   Período: 2020-2026 (expandido para maximizar xG)")
print(f"   Rate limit: 100 requisições/dia (plano básico)")

# Buscar partidas candidatas
print(f"\n🔍 Buscando partidas candidatas...")
candidates = Match.objects.filter(
    home_score__isnull=False,
    away_score__isnull=False,
    match_date__year__gte=2020,  # EXPANDIDO: 2020-2026
    api_football_id__isnull=False  # IMPORTANTE: só partidas com ID válido
).filter(
    league__name__in=MAIN_LEAGUES
).exclude(
    # Não buscar partidas que já têm stats_cache com dados válidos
    stats_cache__isnull=False
).exclude(
    stats_cache=''
).order_by('-match_date')

total_candidates = candidates.count()
print(f"✅ Encontradas {total_candidates} partidas para popular")

if total_candidates == 0:
    print("\n⚠️  Nenhuma partida nova para popular!")
    print("   Todas as partidas candidatas já têm stats_cache.")
    sys.exit(0)

# Perguntar quantas processar
print(f"\n💡 IMPORTANTE:")
print(f"   - API-Football Rate Limit: ~100 req/dia (plano básico)")
print(f"   - Processando: 100 partidas por execução")
print(f"   - Tempo estimado: ~2-3 min para 100 partidas")

batch_size = min(100, total_candidates)

print(f"\n🚀 Processando {batch_size} partidas...")
print("-" * 80)

# Contadores
success_count = 0
with_xg_count = 0
without_xg_count = 0
error_count = 0
api_errors = []

batch = candidates[:batch_size]

for i, match in enumerate(batch, 1):
    try:
        print(f"\n[{i}/{batch_size}] {match.home_team.name} vs {match.away_team.name}")
        print(f"   Fixture ID: {match.api_football_id}")
        print(f"   Data: {match.match_date.strftime('%Y-%m-%d')}")
        print(f"   Liga: {match.league.name}")
        print(f"   Placar: {match.home_score}-{match.away_score}")
        
        # Buscar estatísticas da API
        result = api.get_fixture_statistics(match.api_football_id)
        
        if result.get('success') and result.get('statistics'):
            stats = result['statistics']
            
            # Verificar se tem xG
            has_xg = False
            xg_home = None
            xg_away = None
            
            if isinstance(stats, list) and len(stats) >= 2:
                for team_stats in stats:
                    statistics = team_stats.get('statistics', [])
                    for stat in statistics:
                        stat_type = stat.get('type', '').lower()
                        if 'expected' in stat_type or stat_type == 'expected goals':
                            has_xg = True
                            stat_value = stat.get('value')
                            team_id = team_stats.get('team', {}).get('id')
                            
                            # Determinar se é home ou away
                            if team_id == match.home_team.api_football_id:
                                xg_home = stat_value
                            else:
                                xg_away = stat_value
            
            # Salvar stats_cache
            match.stats_cache = stats
            match.save()
            
            success_count += 1
            
            if has_xg:
                with_xg_count += 1
                print(f"   ✅ Salvo com xG: {xg_home} vs {xg_away}")
            else:
                without_xg_count += 1
                print(f"   ⚠️  Salvo SEM xG (stats básicos apenas)")
        
        elif result.get('error'):
            error_count += 1
            error_msg = result.get('error', 'Unknown error')
            print(f"   ❌ Erro API: {error_msg}")
            api_errors.append({
                'match_id': match.id,
                'fixture_id': match.api_football_id,
                'error': error_msg
            })
        
        else:
            error_count += 1
            print(f"   ❌ Sem dados retornados")
        
        # Rate limiting - aguardar entre requisições
        if i < batch_size:
            time.sleep(0.5)  # 500ms entre requisições
        
        # Status a cada 10 partidas
        if i % 10 == 0:
            print(f"\n📊 Progresso: {i}/{batch_size}")
            print(f"   ✅ Sucesso: {success_count} ({with_xg_count} com xG)")
            print(f"   ❌ Erros: {error_count}")
    
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrompido pelo usuário após {i} partidas")
        break
    except Exception as e:
        error_count += 1
        print(f"   ❌ Erro Python: {e}")
        continue

# Relatório Final
print("\n" + "="*80)
print("RELATÓRIO FINAL")
print("="*80)

print(f"\n📊 ESTATÍSTICAS:")
print(f"   Total processado: {success_count + error_count}")
print(f"   ✅ Salvos com sucesso: {success_count}")
print(f"      └─ Com xG real: {with_xg_count} ({with_xg_count/success_count*100:.1f}%)" if success_count > 0 else "")
print(f"      └─ Sem xG (stats básicos): {without_xg_count}")
print(f"   ❌ Erros: {error_count}")

if api_errors:
    print(f"\n⚠️  ERROS DA API (primeiros 5):")
    for err in api_errors[:5]:
        print(f"   - Match {err['match_id']} (Fixture {err['fixture_id']}): {err['error']}")

# Verificar total atualizado no banco
print(f"\n🎯 TOTAL NO BANCO AGORA:")
total_with_cache = Match.objects.exclude(stats_cache__isnull=True).exclude(stats_cache='').count()
print(f"   Partidas com stats_cache: {total_with_cache}")

# Contar quantas têm xG
print(f"\n🔄 Contando partidas com xG real...")
matches_with_stats = Match.objects.exclude(stats_cache__isnull=True).exclude(stats_cache='')
xg_count = 0

for match in matches_with_stats:
    if isinstance(match.stats_cache, list):
        for team_stats in match.stats_cache:
            statistics = team_stats.get('statistics', [])
            for stat in statistics:
                if 'expected' in stat.get('type', '').lower():
                    xg_count += 1
                    break
            else:
                continue
            break

print(f"   Partidas com xG real: {xg_count}")
print(f"   Porcentagem: {xg_count/total_with_cache*100:.1f}%" if total_with_cache > 0 else "")

print("\n💡 PRÓXIMOS PASSOS:")
if xg_count < 500:
    print(f"   ⚠️  Apenas {xg_count} partidas com xG - insuficiente para calibração robusta")
    print(f"   📌 Execute novamente para processar mais partidas")
    print(f"   📌 Restam {total_candidates - batch_size} partidas candidatas")
elif xg_count < 1000:
    print(f"   ✅ {xg_count} partidas com xG - calibração básica possível")
    print(f"   📌 Recomendado: buscar mais 500-1000 para calibração robusta")
else:
    print(f"   ✅ {xg_count} partidas com xG - suficiente para calibração robusta!")
    print(f"   🚀 Pronto para treinar modelo de calibração xG")

print("="*80 + "\n")
