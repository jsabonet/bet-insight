import math

print("\n" + "="*80)
print("📊 PRODUÇÃO DE BILHETES COM CONFIGURAÇÕES ATUAIS")
print("="*80 + "\n")

print("📋 CONFIGURAÇÕES IMPLEMENTADAS (17/02/2026):")
print("─"*80)
print("   MIN_MULTIPLE_PROBABILITY_3X = 0.80  # 80%")
print("   MIN_MULTIPLE_PROBABILITY_5X = 0.87  # 87%")
print("   MIN_MULTIPLE_PROBABILITY_7X = 0.91  # 91%")
print()
print("   MIN_COMBINED_PROBABILITY_3X = 0.50  # 50%")
print("   MIN_COMBINED_PROBABILITY_5X = 0.50  # 50%")
print("   MIN_COMBINED_PROBABILITY_7X = 0.50  # 50%")
print()
print("   MIN_ODD_MULTIPLE = 1.10")
print("   MAX_ODD_MULTIPLE = 1.50")
print("   MIN_CONFIDENCE_STARS = 4")
print("   MAX_DRAW_PROBABILITY = 0.35")
print("   ALLOWED_RISK_LEVELS = ['low', 'medium']")
print()

# Distribuição esperada com 60 partidas analisadas
print("="*80)
print("🎲 SIMULAÇÃO: 60 PARTIDAS DISPONÍVEIS/DIA")
print("="*80 + "\n")

# Distribuição típica baseada em dados reais de sistemas de apostas
distribution = [
    (0.95, 1.00, "≥95%", 3),       # 5%
    (0.91, 0.95, "91-95%", 3),     # 5%
    (0.87, 0.91, "87-91%", 5),     # 8%
    (0.80, 0.87, "80-87%", 10),    # 17%
    (0.75, 0.80, "75-80%", 12),    # 20%
    (0.70, 0.75, "70-75%", 10),    # 17%
    (0.60, 0.70, "60-70%", 8),     # 13%
    (0.00, 0.60, "<60%", 9),       # 15%
]

total_matches = 60
odds_filter = 0.70  # 70% têm odds no range 1.10-1.50

print(f"   Total de partidas analisadas: {total_matches}\n")

# Calcular apostas disponíveis por threshold
thresholds = {
    0.91: {'count': 0, 'with_odds': 0},  # 7X
    0.87: {'count': 0, 'with_odds': 0},  # 5X
    0.80: {'count': 0, 'with_odds': 0},  # 3X
}

for min_prob, max_prob, label, count in distribution:
    for threshold in thresholds.keys():
        if min_prob >= threshold:
            thresholds[threshold]['count'] += count
            thresholds[threshold]['with_odds'] += int(count * odds_filter)

print("   📊 Apostas disponíveis por threshold:\n")
for threshold in [0.91, 0.87, 0.80]:
    data = thresholds[threshold]
    print(f"      ≥{threshold*100:.0f}%: {data['count']} total → {data['with_odds']} com odd 1.10-1.50")

print("\n" + "="*80)
print("🎯 CAPACIDADE DE GERAÇÃO ATUAL:")
print("="*80 + "\n")

# Bilhetes 3X (threshold 80%)
available_3x = thresholds[0.80]['with_odds']
tickets_3x = available_3x // 3
prob_3x = 0.80 ** 3

print(f"   📌 BILHETES 3X (threshold ≥80%):")
print(f"      Apostas disponíveis: {available_3x}")
print(f"      Bilhetes possíveis: {tickets_3x} por dia")
print(f"      Prob combinada: {prob_3x*100:.1f}%")
print(f"      Status: {'✅ VIÁVEL' if tickets_3x >= 2 else '⚠️ LIMITADO' if tickets_3x >= 1 else '❌ INSUFICIENTE'}")
print()

# Bilhetes 5X (threshold 87%)
available_5x = thresholds[0.87]['with_odds']
tickets_5x = available_5x // 5
prob_5x = 0.87 ** 5

print(f"   📌 BILHETES 5X (threshold ≥87%):")
print(f"      Apostas disponíveis: {available_5x}")
print(f"      Bilhetes possíveis: {tickets_5x} por dia")
print(f"      Prob combinada: {prob_5x*100:.1f}%")
print(f"      Status: {'✅ VIÁVEL' if tickets_5x >= 2 else '⚠️ LIMITADO' if tickets_5x >= 1 else '❌ INSUFICIENTE'}")
print()

# Bilhetes 7X (threshold 91%)
available_7x = thresholds[0.91]['with_odds']
tickets_7x = available_7x // 7
prob_7x = 0.91 ** 7

print(f"   📌 BILHETES 7X (threshold ≥91%):")
print(f"      Apostas disponíveis: {available_7x}")
print(f"      Bilhetes possíveis: {tickets_7x} por dia")
print(f"      Prob combinada: {prob_7x*100:.1f}%")
print(f"      Status: {'✅ VIÁVEL' if tickets_7x >= 2 else '⚠️ LIMITADO' if tickets_7x >= 1 else '❌ INSUFICIENTE'}")
print()

# Resumo diário
print("="*80)
print("📅 PRODUÇÃO DIÁRIA ESPERADA:")
print("="*80 + "\n")

total_daily = tickets_3x + tickets_5x + tickets_7x

print(f"   🎯 Total de bilhetes/dia: {total_daily}")
print()
print(f"   Detalhamento:")
print(f"      • {tickets_3x} bilhetes 3X (prob: {prob_3x*100:.1f}%)")
print(f"      • {tickets_5x} bilhetes 5X (prob: {prob_5x*100:.1f}%)")
print(f"      • {tickets_7x} bilhetes 7X (prob: {prob_7x*100:.1f}%)")
print()

# Cálculo de apostas semanais
weekly_3x = tickets_3x * 7
weekly_5x = tickets_5x * 7
weekly_7x = tickets_7x * 7
total_weekly = total_daily * 7

print(f"   📆 Produção semanal (7 dias):")
print(f"      • {weekly_3x} bilhetes 3X")
print(f"      • {weekly_5x} bilhetes 5X")
print(f"      • {weekly_7x} bilhetes 7X")
print(f"      • Total: {total_weekly} bilhetes/semana")
print()

# Cálculo mensal
monthly_total = total_daily * 30
print(f"   📆 Produção mensal (~30 dias): {monthly_total} bilhetes")
print()

print("="*80)
print("📊 TAXA DE ACERTO ESPERADA:")
print("="*80 + "\n")

# Taxa de acerto esperada em 10 bilhetes
expected_wins_3x = int(prob_3x * 10)
expected_wins_5x = int(prob_5x * 10)
expected_wins_7x = int(prob_7x * 10)

print(f"   Em 10 bilhetes de cada tipo:")
print(f"      • 3X: {expected_wins_3x} acertos (taxa: {prob_3x*100:.1f}%)")
print(f"      • 5X: {expected_wins_5x} acertos (taxa: {prob_5x*100:.1f}%)")
print(f"      • 7X: {expected_wins_7x} acertos (taxa: {prob_7x*100:.1f}%)")
print()

# ROI teórico (simplificado)
print("="*80)
print("💰 ANÁLISE DE RETORNO TEÓRICO:")
print("="*80 + "\n")

# Calcular odds médias esperadas
# Com prob 80%, odd justa = 1/0.80 = 1.25
# Com prob 87%, odd justa = 1/0.87 = 1.15
# Com prob 91%, odd justa = 1/0.91 = 1.10

avg_odd_3x = 1.25 ** 3  # Odd total bilhete 3X
avg_odd_5x = 1.15 ** 5  # Odd total bilhete 5X
avg_odd_7x = 1.10 ** 7  # Odd total bilhete 7X

print(f"   Odds médias esperadas:")
print(f"      • 3X: {avg_odd_3x:.2f}")
print(f"      • 5X: {avg_odd_5x:.2f}")
print(f"      • 7X: {avg_odd_7x:.2f}")
print()

# ROI teórico = (prob_acerto × odd_media) - 1
roi_3x = (prob_3x * avg_odd_3x - 1) * 100
roi_5x = (prob_5x * avg_odd_5x - 1) * 100
roi_7x = (prob_7x * avg_odd_7x - 1) * 100

print(f"   ROI teórico (valor esperado):")
print(f"      • 3X: {roi_3x:+.1f}% {'✅' if roi_3x > 0 else '❌'}")
print(f"      • 5X: {roi_5x:+.1f}% {'✅' if roi_5x > 0 else '❌'}")
print(f"      • 7X: {roi_7x:+.1f}% {'✅' if roi_7x > 0 else '❌'}")
print()

print("="*80)
print("💡 ANÁLISE CRÍTICA:")
print("="*80 + "\n")

if tickets_3x < 2:
    print("   ⚠️  PROBLEMA CRÍTICO: Bilhetes 3X")
    print(f"      • Apenas {tickets_3x} bilhete/dia (esperado: ≥2)")
    print(f"      • Threshold 80% é MUITO RESTRITIVO para 60 partidas")
    print()

if tickets_5x < 1:
    print("   ⚠️  PROBLEMA CRÍTICO: Bilhetes 5X")
    print(f"      • Apenas {tickets_5x} bilhete/dia (esperado: ≥1)")
    print(f"      • Threshold 87% é MUITO RESTRITIVO para 60 partidas")
    print()

if tickets_7x < 1:
    print("   ⚠️  PROBLEMA: Bilhetes 7X")
    print(f"      • Apenas {tickets_7x} bilhete/dia")
    print(f"      • Threshold 91% é EXTREMAMENTE RESTRITIVO")
    print(f"      • Geração será MUITO RARA ou INEXISTENTE")
    print()

if total_daily < 5:
    print("   🎯 RECOMENDAÇÃO:")
    print("      • Configuração atual é MUITO CONSERVADORA")
    print("      • Gerando apenas {total_daily} bilhetes/dia com 60 partidas disponíveis")
    print("      • Sugestão: Ajustar thresholds para valores balanceados:")
    print()
    print("         MIN_MULTIPLE_PROBABILITY_3X = 0.80  # OK - mantém")
    print("         MIN_MULTIPLE_PROBABILITY_5X = 0.84  # Reduzir de 87%")
    print("         MIN_MULTIPLE_PROBABILITY_7X = 0.86  # Reduzir de 91%")
    print()
    print("         MIN_COMBINED_PROBABILITY_3X = 0.50  # OK - mantém")
    print("         MIN_COMBINED_PROBABILITY_5X = 0.40  # Reduzir de 50%")
    print("         MIN_COMBINED_PROBABILITY_7X = 0.35  # Reduzir de 50%")
    print()
    print("      • Com ajuste, produção esperada:")
    
    # Recalcular com thresholds sugeridos
    suggested_available_5x = int((3 + 3 + 5 + 10 * 0.6) * odds_filter)  # Aproximação
    suggested_available_7x = int((3 + 3 + 5 * 0.5) * odds_filter)
    
    suggested_tickets_3x = available_3x // 3
    suggested_tickets_5x = suggested_available_5x // 5
    suggested_tickets_7x = suggested_available_7x // 7
    suggested_total = suggested_tickets_3x + suggested_tickets_5x + suggested_tickets_7x
    
    print(f"         • {suggested_tickets_3x} bilhetes 3X/dia")
    print(f"         • {suggested_tickets_5x} bilhetes 5X/dia")
    print(f"         • {suggested_tickets_7x} bilhetes 7X/dia")
    print(f"         • Total: ~{suggested_total} bilhetes/dia")
else:
    print("   ✅ CONFIGURAÇÃO ATUAL:")
    print(f"      • Produção: {total_daily} bilhetes/dia")
    print(f"      • Taxa de acerto esperada: {prob_3x*100:.1f}% (3X) a {prob_7x*100:.1f}% (7X)")
    print(f"      • Volume adequado para sistema de apostas consistente")

print("\n" + "="*80 + "\n")
