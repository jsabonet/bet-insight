import os
import django
from datetime import datetime, timedelta
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import Analysis, DailyBet

print("\n" + "="*80)
print("📊 ANÁLISE: PARTIDAS ANALISADAS vs BILHETES SEGUROS")
print("="*80 + "\n")

# Analisar últimos 30 dias
days_back = 30
start_date = datetime.now() - timedelta(days=days_back)

# Buscar todas as análises
all_analyses = Analysis.objects.filter(
    created_at__gte=start_date
).select_related('match')

print(f"📅 Período analisado: Últimos {days_back} dias")
print(f"📈 Total de análises no período: {all_analyses.count()}\n")

# Agrupar por dia
analyses_by_day = defaultdict(list)
for analysis in all_analyses:
    day = analysis.created_at.date()
    analyses_by_day[day].append(analysis)

# Calcular estatísticas
daily_counts = [len(analyses) for analyses in analyses_by_day.values()]
if daily_counts:
    avg_per_day = sum(daily_counts) / len(daily_counts)
    min_per_day = min(daily_counts)
    max_per_day = max(daily_counts)
    median_per_day = sorted(daily_counts)[len(daily_counts) // 2]
else:
    avg_per_day = min_per_day = max_per_day = median_per_day = 0

print("="*80)
print("📊 ESTATÍSTICAS DE ANÁLISES DIÁRIAS:")
print("="*80 + "\n")

print(f"   Média de partidas analisadas/dia: {avg_per_day:.1f}")
print(f"   Mediana: {median_per_day:.0f}")
print(f"   Mínimo: {min_per_day:.0f}")
print(f"   Máximo: {max_per_day:.0f}")
print(f"   Dias com análises: {len(analyses_by_day)}/{days_back}")

# Distribuição de partidas por dia
print(f"\n   📊 Distribuição de partidas/dia:\n")
ranges = [
    (0, 10, "0-10 partidas"),
    (10, 20, "10-20 partidas"),
    (20, 50, "20-50 partidas"),
    (50, 100, "50-100 partidas"),
    (100, 200, "100-200 partidas"),
    (200, 1000, ">200 partidas")
]

for min_count, max_count, label in ranges:
    days_in_range = len([c for c in daily_counts if min_count <= c < max_count])
    percentage = (days_in_range / len(daily_counts) * 100) if daily_counts else 0
    bar = "█" * int(percentage / 3)
    print(f"      {label:20s}: {days_in_range:3d} dias ({percentage:5.1f}%) {bar}")

# Analisar bilhetes gerados
print("\n" + "="*80)
print("🎯 BILHETES GERADOS vs APOSTAS DISPONÍVEIS:")
print("="*80 + "\n")

all_bets = DailyBet.objects.filter(
    created_at__gte=start_date,
    bet_type='multiple'
).order_by('-created_at')

# Extrair apostas individuais
individual_bets = []
bets_by_day = defaultdict(list)

for bet in all_bets:
    day = bet.created_at.date()
    if isinstance(bet.selections, list):
        for selection in bet.selections:
            bet_data = {
                'match': selection.get('match', 'N/A'),
                'probability': selection.get('probability', 0),
                'odd': selection.get('odd', 0),
                'market': selection.get('market', 'N/A'),
                'score': selection.get('score', 0),
                'day': day
            }
            individual_bets.append(bet_data)
            bets_by_day[day].append(bet_data)

print(f"📈 Total de apostas geradas: {len(individual_bets)}")
print(f"📅 Dias com bilhetes: {len(bets_by_day)}")

# Calcular apostas por dia
bets_per_day = [len(bets) for bets in bets_by_day.values()]
if bets_per_day:
    avg_bets_per_day = sum(bets_per_day) / len(bets_per_day)
    min_bets_per_day = min(bets_per_day)
    max_bets_per_day = max(bets_per_day)
    median_bets_per_day = sorted(bets_per_day)[len(bets_per_day) // 2]
else:
    avg_bets_per_day = min_bets_per_day = max_bets_per_day = median_bets_per_day = 0

print(f"\n   Média de apostas geradas/dia: {avg_bets_per_day:.1f}")
print(f"   Mediana: {median_bets_per_day:.0f}")
print(f"   Mínimo: {min_bets_per_day:.0f}")
print(f"   Máximo: {max_bets_per_day:.0f}")

# Taxa de conversão
if avg_per_day > 0:
    conversion_rate = (avg_bets_per_day / avg_per_day) * 100
    print(f"\n   📊 Taxa de conversão: {conversion_rate:.2f}%")
    print(f"      (apostas geradas / partidas analisadas)")

# Análise por threshold de probabilidade
print("\n" + "="*80)
print("🎯 APOSTAS DISPONÍVEIS POR THRESHOLD:")
print("="*80 + "\n")

thresholds = [
    (0.95, "≥95%", "Excelente"),
    (0.90, "≥90%", "Muito Bom"),
    (0.85, "≥85%", "Bom"),
    (0.80, "≥80%", "Aceitável"),
    (0.75, "≥75%", "Médio"),
    (0.70, "≥70%", "Baixo")
]

threshold_stats = {}
for threshold, label, quality in thresholds:
    eligible = [b for b in individual_bets if b['probability'] >= threshold]
    eligible_odds = [b for b in eligible if 1.10 <= b['odd'] <= 1.50]
    
    per_day = len(eligible_odds) / len(bets_by_day) if bets_by_day else 0
    
    threshold_stats[label] = {
        'total': len(eligible),
        'with_odds': len(eligible_odds),
        'per_day': per_day,
        'quality': quality
    }
    
    print(f"   {label} ({quality}):")
    print(f"      Total: {len(eligible)} apostas")
    print(f"      Com odd 1.10-1.50: {len(eligible_odds)} apostas")
    print(f"      Média/dia: {per_day:.2f} apostas")
    print()

# Calcular bilhetes seguros
print("="*80)
print("🎯 NÚMERO SEGURO DE APOSTAS POR BILHETE:")
print("="*80 + "\n")

print("   Baseado em: Ter apostas suficientes em 90% dos dias\n")

# Para cada threshold, calcular quantos dias têm apostas suficientes
for threshold, label, quality in thresholds:
    print(f"   📌 {label} ({quality}):")
    
    # Contar apostas elegíveis por dia
    eligible_by_day = defaultdict(int)
    for bet in individual_bets:
        if bet['probability'] >= threshold and 1.10 <= bet['odd'] <= 1.50:
            eligible_by_day[bet['day']] += 1
    
    if not eligible_by_day:
        print(f"      ❌ Nenhuma aposta disponível")
        print()
        continue
    
    # Ordenar dias por quantidade de apostas
    daily_eligible = sorted(eligible_by_day.values())
    
    # Percentis
    p10 = daily_eligible[int(len(daily_eligible) * 0.1)] if daily_eligible else 0
    p25 = daily_eligible[int(len(daily_eligible) * 0.25)] if daily_eligible else 0
    p50 = daily_eligible[int(len(daily_eligible) * 0.50)] if daily_eligible else 0
    p75 = daily_eligible[int(len(daily_eligible) * 0.75)] if daily_eligible else 0
    p90 = daily_eligible[int(len(daily_eligible) * 0.90)] if daily_eligible else 0
    
    print(f"      Apostas disponíveis (percentis):")
    print(f"         10% dos dias: ≤{p10} apostas")
    print(f"         25% dos dias: ≤{p25} apostas")
    print(f"         50% dos dias: ≤{p50} apostas (mediana)")
    print(f"         75% dos dias: ≤{p75} apostas")
    print(f"         90% dos dias: ≤{p90} apostas")
    
    # Determinar número seguro (p90 - garantido em 90% dos dias)
    safe_3x = p90 >= 3
    safe_5x = p90 >= 5
    safe_7x = p90 >= 7
    safe_10x = p90 >= 10
    
    print(f"\n      Bilhetes seguros (disponível em 90% dos dias):")
    if safe_3x:
        print(f"         ✅ Bilhetes 3X: SEGURO (≥3 apostas em 90% dos dias)")
    else:
        print(f"         ❌ Bilhetes 3X: INSEGURO (< 3 apostas em 90% dos dias)")
    
    if safe_5x:
        print(f"         ✅ Bilhetes 5X: SEGURO (≥5 apostas em 90% dos dias)")
    else:
        print(f"         ⚠️  Bilhetes 5X: ARRISCADO (< 5 apostas em 90% dos dias)")
    
    if safe_7x:
        print(f"         ✅ Bilhetes 7X: SEGURO (≥7 apostas em 90% dos dias)")
    else:
        print(f"         ❌ Bilhetes 7X: INSEGURO (< 7 apostas em 90% dos dias)")
    
    if safe_10x:
        print(f"         ✅ Bilhetes 10X: SEGURO (≥10 apostas em 90% dos dias)")
    else:
        print(f"         ❌ Bilhetes 10X: INSEGURO (< 10 apostas em 90% dos dias)")
    
    # Número máximo seguro
    safe_max = p90
    print(f"\n      🎯 NÚMERO MÁXIMO SEGURO: {safe_max} apostas/bilhete")
    print(f"         (garantido em 90% dos dias)")
    print()

# Recomendação final
print("="*80)
print("💡 RECOMENDAÇÃO FINAL:")
print("="*80 + "\n")

# Escolher threshold razoável (80% - aceitável)
threshold_80 = threshold_stats.get("≥80%", {})
per_day_80 = threshold_80.get('per_day', 0)

# Escolher threshold alto (85% - bom)
threshold_85 = threshold_stats.get("≥85%", {})
per_day_85 = threshold_85.get('per_day', 0)

# Escolher threshold muito alto (90% - muito bom)
threshold_90 = threshold_stats.get("≥90%", {})
per_day_90 = threshold_90.get('per_day', 0)

print(f"   📊 Partidas analisadas: ~{avg_per_day:.0f}/dia")
print(f"   📊 Apostas geradas (histórico): ~{avg_bets_per_day:.1f}/dia")
print(f"   📊 Taxa de conversão atual: {conversion_rate:.1f}%\n")

print(f"   🎯 CENÁRIOS POR THRESHOLD:\n")

if per_day_80 >= 3:
    print(f"      ✅ THRESHOLD 80% (Aceitável):")
    print(f"         • Apostas disponíveis: {per_day_80:.1f}/dia")
    print(f"         • Bilhetes seguros: 3X")
    if per_day_80 >= 5:
        print(f"         • Bilhetes possíveis: 5X (ocasional)")
    print()

if per_day_85 >= 3:
    print(f"      ✅ THRESHOLD 85% (Bom):")
    print(f"         • Apostas disponíveis: {per_day_85:.1f}/dia")
    print(f"         • Bilhetes seguros: 3X")
    if per_day_85 >= 5:
        print(f"         • Bilhetes possíveis: 5X (ocasional)")
    print()

if per_day_90 >= 3:
    print(f"      ⚠️  THRESHOLD 90% (Muito Bom):")
    print(f"         • Apostas disponíveis: {per_day_90:.1f}/dia")
    print(f"         • Bilhetes seguros: Nenhum consistente")
    print(f"         • Bilhetes possíveis: 3X (raro)")
    print()
else:
    print(f"      ❌ THRESHOLD 90% (Muito Bom):")
    print(f"         • Apostas disponíveis: {per_day_90:.1f}/dia")
    print(f"         • Bilhetes seguros: INVIÁVEL")
    print()

print(f"   🎯 CONFIGURAÇÃO RECOMENDADA:\n")

if per_day_85 >= 5:
    print(f"      • Bilhetes 3X: Threshold 85% (≥5 apostas/dia)")
    print(f"      • Bilhetes 5X: Threshold 82-83% (ocasional)")
    print(f"      • Bilhetes 7X: NÃO RECOMENDADO")
elif per_day_85 >= 3:
    print(f"      • Bilhetes 3X: Threshold 82-85% (≥3 apostas/dia)")
    print(f"      • Bilhetes 5X: NÃO RECOMENDADO ou muito raro")
    print(f"      • Bilhetes 7X: NÃO RECOMENDADO")
elif per_day_80 >= 3:
    print(f"      • Bilhetes 3X: Threshold 80% (≥3 apostas/dia)")
    print(f"      • Bilhetes 5X: NÃO RECOMENDADO")
    print(f"      • Bilhetes 7X: NÃO RECOMENDADO")
else:
    print(f"      ⚠️  DADOS INSUFICIENTES")
    print(f"      • Sistema precisa analisar mais partidas")
    print(f"      • Ou critérios de seleção estão muito restritos")

print(f"\n   💡 Para aumentar disponibilidade:")
print(f"      • Analisar mais ligas/competições")
print(f"      • Expandir busca de partidas (hybrid mode)")
print(f"      • Reduzir ligeiramente os thresholds de qualidade")
print(f"      • Aceitar range de odds mais amplo (1.10-1.80)")

print("\n" + "="*80 + "\n")
