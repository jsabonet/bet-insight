"""
Testar enriquecimento de dados em partida FUTURA (disponível na API)
Para verificar se a acurácia de 65% se mantém em produção
"""
import os
import sys
import django
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.matches.models import Match

print("="*80)
print("TESTE: Enriquecimento de Partida Futura")
print("="*80)

# Buscar uma partida futura/recente no banco
future_match = Match.objects.filter(
    status='NS'  # Not Started
).exclude(
    api_football_id__isnull=True
).first()

if not future_match:
    print("\n❌ Nenhuma partida futura encontrada no banco")
    print("   Tentando com partida mais recente...")
    future_match = Match.objects.exclude(
        api_football_id__isnull=True
    ).order_by('-match_date').first()

if not future_match:
    print("\n❌ Nenhuma partida com api_football_id encontrada")
    sys.exit(1)

print(f"\n[OK] Partida encontrada:")
print(f"   ID: {future_match.api_football_id}")
print(f"   Jogo: {future_match.home_team.name} vs {future_match.away_team.name}")
print(f"   Liga: {future_match.league.name}")
print(f"   Data: {future_match.match_date}")
print(f"   Status: {future_match.status}")

print("\n" + "="*80)
print("INICIANDO ENRIQUECIMENTO")
print("="*80)

enricher = MatchDataEnricher()
fe = FeatureEngineer()

# Tentar enriquecer
match_data = {'api_id': future_match.api_football_id}
enriched = enricher.enrich(match_data)

# Verificar se enriquecimento funcionou
has_fixture_details = enriched.get('fixture_details') is not None
has_standings = enriched.get('table_context') is not None
has_odds = enriched.get('odds') is not None
has_home_stats = enriched.get('home_stats') is not None
has_away_stats = enriched.get('away_stats') is not None
has_h2h = enriched.get('h2h') is not None

print("\n" + "="*80)
print("RESULTADO DO ENRIQUECIMENTO")
print("="*80)
print(f"\n[OK] Fixture Details: {'SIM' if has_fixture_details else '[X] NAO'}")
print(f"[OK] Standings: {'SIM' if has_standings else '[X] NAO'}")
print(f"[OK] Odds: {'SIM' if has_odds else '[X] NAO'}")
print(f"[OK] Home Stats: {'SIM' if has_home_stats else '[X] NAO'}")
print(f"[OK] Away Stats: {'SIM' if has_away_stats else '[X] NAO'}")
print(f"[OK] H2H: {'SIM' if has_h2h else '[X] NAO'}")

# Contar features gerados
features = fe.engineer_all_features(enriched)
feature_count = len([k for k, v in features.items() if v is not None and v != 0])
print(f"\n[*] Features gerados: {feature_count}")

# Verificar features críticos
critical_features = [
    'strength.home_goals_per_game',
    'strength.away_goals_per_game',
    'form.home_last_5_wins',
    'form.away_last_5_wins',
    'h2h.h2h_home_win_rate',
    'standings.home_position',
    'standings.away_position'
]

print("\n[*] Features Criticos:")
for feat in critical_features:
    value = features.get(feat, 'AUSENTE')
    status = "[OK]" if value != 'AUSENTE' and value != 0 else "[X]"
    print(f"   {status} {feat}: {value}")

# Calcular qualidade do enriquecimento
enrichment_score = 0
if has_fixture_details: enrichment_score += 20
if has_standings: enrichment_score += 20
if has_odds: enrichment_score += 15
if has_home_stats: enrichment_score += 15
if has_away_stats: enrichment_score += 15
if has_h2h: enrichment_score += 15

print("\n" + "="*80)
print("CONCLUSAO")
print("="*80)
print(f"\n[*] Score de Enriquecimento: {enrichment_score}/100")

if enrichment_score >= 80:
    print("\n[OK] ENRIQUECIMENTO COMPLETO!")
    print("   -> A acuracia de 65% deve se manter em producao")
    print("   -> Features suficientes para previsoes confiaveis")
elif enrichment_score >= 50:
    print("\n[!] ENRIQUECIMENTO PARCIAL")
    print("   -> Acuracia pode ser menor que 65%")
    print("   -> Alguns dados criticos estao faltando")
else:
    print("\n[X] ENRIQUECIMENTO INSUFICIENTE")
    print("   -> Acuracia sera significativamente menor que 65%")
    print("   -> Sistema operando com dados limitados")
    print("   -> Similar aos 25% do validation_orchestrator")

print("\n" + "="*80)
