import math

print("\n" + "="*80)
print("📊 CENÁRIO ILUSTRATIVO DE MÚLTIPLAS (NÃO É PREVISÃO DE PRODUÇÃO)")
print("="*80 + "\n")

print("📋 FILTROS CONFIGURADOS:")
print("─"*80)
print("   MIN_MULTIPLE_PROBABILITY_3X = 0.65  # 65%")
print("   MIN_MULTIPLE_PROBABILITY_5X = 0.68  # 68%")
print("   MIN_MULTIPLE_PROBABILITY_7X = 0.70  # 70%")
print()
print("   MIN_COMBINED_PROBABILITY_3X = 0.25  # 25% ajustada")
print("   MIN_COMBINED_PROBABILITY_5X = 0.13  # 13% ajustada")
print("   MIN_COMBINED_PROBABILITY_7X = 0.08  # 8% ajustada")
print()
print("   MIN_MULTIPLE_EV = 0.0  # EV não-negativo por seleção e bilhete")
print("   Ticket odd: 2.50 a 25.00")
print("   MIN_CONFIDENCE_STARS = 4")
print("   MAX_DRAW_PROBABILITY = 0.35")
print("   ALLOWED_RISK_LEVELS = ['low', 'medium']")
print()

# Assumed distribution, used only to illustrate candidate counts.
print("="*80)
print("🎲 HIPÓTESE: 60 PARTIDAS/DIA; TAXA DE EV É UMA SUPOSIÇÃO")
print("="*80 + "\n")

# Assumed distribution for an illustrative simulation, not observed performance.
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
ev_filter = 0.70  # hipótese ilustrativa: 70% dos candidatos têm EV não-negativo

print(f"   Total de partidas analisadas: {total_matches}\n")

# Calcular apostas disponíveis por threshold
thresholds = {
    0.70: {'count': 0, 'with_ev': 0},  # 7X
    0.68: {'count': 0, 'with_ev': 0},  # 5X
    0.65: {'count': 0, 'with_ev': 0},  # 3X
}

for min_prob, max_prob, label, count in distribution:
    for threshold in thresholds.keys():
        if min_prob >= threshold:
            thresholds[threshold]['count'] += count
            thresholds[threshold]['with_ev'] += int(count * ev_filter)

print("   📊 Apostas disponíveis por threshold:\n")
for threshold in [0.70, 0.68, 0.65]:
    data = thresholds[threshold]
    print(f"      ≥{threshold*100:.0f}%: {data['count']} total → {data['with_ev']} com EV ≥0% (hipótese)")

print("\n" + "="*80)
print("🎯 CANDIDATOS ANTES DO FILTRO FINAL DE EV DO BILHETE:")
print("="*80 + "\n")

# Bilhetes 3X (threshold 65%)
available_3x = thresholds[0.65]['with_ev']
tickets_3x = available_3x // 3
prob_3x = 0.65 ** 3 * 0.95

print(f"   📌 BILHETES 3X (threshold ≥65%):")
print(f"      Apostas disponíveis: {available_3x}")
print(f"      Bilhetes possíveis: {tickets_3x} por dia")
print(f"      Prob combinada: {prob_3x*100:.1f}%")
print(f"      Status: {'✅ VIÁVEL' if tickets_3x >= 2 else '⚠️ LIMITADO' if tickets_3x >= 1 else '❌ INSUFICIENTE'}")
print()

# Bilhetes 5X (threshold 68%)
available_5x = thresholds[0.68]['with_ev']
tickets_5x = available_5x // 5
prob_5x = 0.68 ** 5 * 0.90

print(f"   📌 BILHETES 5X (threshold ≥68%):")
print(f"      Apostas disponíveis: {available_5x}")
print(f"      Bilhetes possíveis: {tickets_5x} por dia")
print(f"      Prob combinada: {prob_5x*100:.1f}%")
print(f"      Status: {'✅ VIÁVEL' if tickets_5x >= 2 else '⚠️ LIMITADO' if tickets_5x >= 1 else '❌ INSUFICIENTE'}")
print()

# Bilhetes 7X (threshold 70%)
available_7x = thresholds[0.70]['with_ev']
tickets_7x = available_7x // 7
prob_7x = 0.70 ** 7 * 0.85

print(f"   📌 BILHETES 7X (threshold ≥70%):")
print(f"      Apostas disponíveis: {available_7x}")
print(f"      Bilhetes possíveis: {tickets_7x} por dia")
print(f"      Prob combinada: {prob_7x*100:.1f}%")
print(f"      Status: {'✅ VIÁVEL' if tickets_7x >= 2 else '⚠️ LIMITADO' if tickets_7x >= 1 else '❌ INSUFICIENTE'}")
print()

# Candidate counts are upper bounds: fixture/correlation, context and ticket EV
# filters can reject further combinations.
print("="*80)
print("📅 CONTAGEM ILUSTRATIVA DE COMBINAÇÕES:")
print("="*80 + "\n")

total_daily = tickets_3x + tickets_5x + tickets_7x

print(f"   🎯 Combinações candidatas: {total_daily} (não representa bilhetes gerados)")
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

print(f"   📆 Escala semanal ilustrativa (antes dos filtros finais):")
print(f"      • {weekly_3x} bilhetes 3X")
print(f"      • {weekly_5x} bilhetes 5X")
print(f"      • {weekly_7x} bilhetes 7X")
print(f"      • Total: {total_weekly} combinações candidatas/semana")
print()

# Cálculo mensal
monthly_total = total_daily * 30
print(f"   📆 Escala mensal ilustrativa (~30 dias): {monthly_total} combinações candidatas")
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

# Fair-price illustration based on each size's minimum individual probability.

avg_odd_3x = (1 / 0.65) ** 3
avg_odd_5x = (1 / 0.68) ** 5
avg_odd_7x = (1 / 0.70) ** 7

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
print("   Com preço justo por seleção, a penalidade de correlação torna o EV do bilhete negativo.")
print("   Portanto, essas odds ilustrativas não passariam o filtro final EV ≥0%.")
print()

print("="*80)
print("💡 ANÁLISE CRÍTICA:")
print("="*80 + "\n")

if tickets_3x < 2:
    print("   ⚠️  PROBLEMA CRÍTICO: Bilhetes 3X")
    print(f"      • Apenas {tickets_3x} bilhete/dia (esperado: ≥2)")
    print("      • Poucos candidatos superam o piso de probabilidade e a hipótese de EV.")
    print()

if tickets_5x < 1:
    print("   ⚠️  PROBLEMA CRÍTICO: Bilhetes 5X")
    print(f"      • Apenas {tickets_5x} bilhete/dia (esperado: ≥1)")
    print("      • Poucos candidatos superam o piso de probabilidade e a hipótese de EV.")
    print()

if tickets_7x < 1:
    print("   ⚠️  PROBLEMA: Bilhetes 7X")
    print(f"      • Apenas {tickets_7x} bilhete/dia")
    print("      • Poucos candidatos superam o piso de probabilidade e a hipótese de EV.")
    print()

if total_daily < 5:
    print("   🎯 RECOMENDAÇÃO:")
    print(f"      • Simulação estima {total_daily} bilhetes/dia; isso não mede a produção real.")
    print("      • Não ajuste limiares com base nesta hipótese; valide cobertura e retorno por backtest.")
else:
    print("   ℹ️  A contagem não considera dados reais de odds, EV, contexto ou dependência.")
    print("      Não use este cenário como estimativa de produção ou rentabilidade.")

print("\n" + "="*80 + "\n")
