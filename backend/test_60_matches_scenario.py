import math

print("\n" + "="*80)
print("📊 ANÁLISE: BILHETES SEGUROS COM 60 PARTIDAS DISPONÍVEIS/DIA")
print("="*80 + "\n")

print("📋 PREMISSA:")
print("─"*80)
print("   • Sistema pode analisar até 60 partidas/dia")
print("   • Sistema híbrido busca ~155 partidas, filtra e analisa as melhores")
print("   • Geração de bilhetes usa apenas apostas de alta qualidade")
print()

# Simular distribuição típica de probabilidades em 60 partidas
# Baseado em dados reais de sistemas de apostas
print("="*80)
print("🎲 DISTRIBUIÇÃO ESPERADA DE PROBABILIDADES (60 partidas):")
print("="*80 + "\n")

# Distribuição típica: 
# - 5-10% de partidas muito claras (≥90%)
# - 15-20% de partidas claras (80-90%)
# - 30-40% de partidas favoritas moderadas (70-80%)
# - 30-40% de partidas equilibradas (50-70%)
# - 5-10% de partidas muito equilibradas (<50%)

distribution = [
    (0.95, 1.00, "≥95%", 3, "Excelente"),      # 3 partidas (5%)
    (0.90, 0.95, "90-95%", 5, "Muito Bom"),    # 5 partidas (8%)
    (0.85, 0.90, "85-90%", 8, "Bom"),          # 8 partidas (13%)
    (0.80, 0.85, "80-85%", 10, "Aceitável"),   # 10 partidas (17%)
    (0.75, 0.80, "75-80%", 12, "Médio"),       # 12 partidas (20%)
    (0.70, 0.75, "70-75%", 10, "Baixo"),       # 10 partidas (17%)
    (0.60, 0.70, "60-70%", 8, "Muito Baixo"),  # 8 partidas (13%)
    (0.00, 0.60, "<60%", 4, "Equilibrado"),    # 4 partidas (7%)
]

total_matches = sum([count for _, _, _, count, _ in distribution])
print(f"   Total de partidas analisadas: {total_matches}\n")

cumulative = {}
for min_prob, max_prob, label, count, quality in distribution:
    percentage = (count / total_matches) * 100
    bar = "█" * int(percentage / 2)
    print(f"   {label:8s} ({quality:12s}): {count:2d} partidas ({percentage:5.1f}%) {bar}")
    
    # Calcular cumulativo (quantas apostas ≥ threshold)
    for threshold in [0.95, 0.90, 0.85, 0.80, 0.75, 0.70]:
        if min_prob >= threshold:
            if threshold not in cumulative:
                cumulative[threshold] = 0
            cumulative[threshold] += count

# Considerar que 70% das apostas têm odds no range ideal (1.10-1.50)
odds_filter = 0.70

print("\n" + "="*80)
print("🎯 APOSTAS DISPONÍVEIS POR THRESHOLD:")
print("="*80 + "\n")

threshold_data = {}
for threshold in [0.95, 0.90, 0.85, 0.80, 0.75, 0.70]:
    total = cumulative.get(threshold, 0)
    with_odds = int(total * odds_filter)
    
    threshold_data[threshold] = {
        'total': total,
        'with_odds': with_odds
    }
    
    print(f"   Threshold ≥{threshold*100:.0f}%:")
    print(f"      Total elegíveis: {total} apostas ({total/total_matches*100:.1f}%)")
    print(f"      Com odd 1.10-1.50: {with_odds} apostas")
    print()

print("="*80)
print("🎯 CAPACIDADE DE GERAÇÃO DE BILHETES:")
print("="*80 + "\n")

ticket_sizes = [
    (3, "3X"),
    (5, "5X"),
    (7, "7X"),
    (10, "10X"),
]

for threshold in [0.95, 0.90, 0.85, 0.80]:
    available = threshold_data[threshold]['with_odds']
    
    print(f"   📌 THRESHOLD ≥{threshold*100:.0f}%: {available} apostas disponíveis")
    print()
    
    for size, name in ticket_sizes:
        # Calcular probabilidade combinada com apostas no threshold
        combined_prob = threshold ** size
        
        # Número de bilhetes possíveis
        possible_tickets = available // size
        
        # Status
        if possible_tickets >= 3:
            status = "✅ VIÁVEL"
            frequency = f"~{possible_tickets} bilhetes/dia"
        elif possible_tickets >= 1:
            status = "⚠️  LIMITADO"
            frequency = f"~{possible_tickets} bilhete(s)/dia"
        else:
            status = "❌ INSUFICIENTE"
            frequency = "Impossível"
        
        print(f"      • Bilhetes {name}:")
        print(f"        Capacidade: {possible_tickets} bilhetes/dia {status}")
        print(f"        Prob combinada esperada: {combined_prob*100:.1f}%")
        print(f"        Apostas usadas: {possible_tickets * size}/{available}")
        print()
    
    print()

print("="*80)
print("💡 CENÁRIOS PRÁTICOS:")
print("="*80 + "\n")

scenarios = [
    {
        'name': 'ULTRA CONSERVADOR',
        'threshold': 0.90,
        'description': 'Máxima acertividade, menor volume'
    },
    {
        'name': 'CONSERVADOR',
        'threshold': 0.85,
        'description': 'Alta acertividade, bom volume'
    },
    {
        'name': 'BALANCEADO',
        'threshold': 0.82,
        'description': 'Equilíbrio entre qualidade e volume'
    },
    {
        'name': 'AGRESSIVO',
        'threshold': 0.80,
        'description': 'Volume alto, acertividade moderada'
    },
]

for scenario in scenarios:
    threshold = scenario['threshold']
    
    # Calcular apostas disponíveis (interpolação entre thresholds conhecidos)
    if threshold == 0.90:
        available = threshold_data[0.90]['with_odds']
    elif threshold == 0.85:
        available = threshold_data[0.85]['with_odds']
    elif threshold == 0.82:
        # Interpolação entre 80% e 85%
        avail_80 = threshold_data[0.80]['with_odds']
        avail_85 = threshold_data[0.85]['with_odds']
        available = int(avail_85 + (avail_80 - avail_85) * 0.4)
    else:
        available = threshold_data[0.80]['with_odds']
    
    print(f"   📊 {scenario['name']} (Threshold ≥{threshold*100:.0f}%)")
    print(f"   {scenario['description']}")
    print(f"   Apostas disponíveis: {available}/dia\n")
    
    # Calcular mix ideal de bilhetes
    # Estratégia: Priorizar 3X (maior acertividade), depois 5X, depois 7X
    
    # Opção 1: Foco em 3X
    tickets_3x = available // 3
    remaining = available % 3
    print(f"      Opção A - Foco em 3X:")
    print(f"         {tickets_3x} bilhetes 3X (prob combinada: {(threshold**3)*100:.1f}%)")
    print(f"         Apostas restantes: {remaining}")
    
    # Opção 2: Mix 3X + 5X
    if available >= 8:
        tickets_5x = 1
        remaining_after_5x = available - 5
        tickets_3x = remaining_after_5x // 3
        final_remaining = remaining_after_5x % 3
        
        print(f"\n      Opção B - Mix 3X + 5X:")
        print(f"         {tickets_3x} bilhetes 3X (prob: {(threshold**3)*100:.1f}%)")
        print(f"         {tickets_5x} bilhete 5X (prob: {(threshold**5)*100:.1f}%)")
        print(f"         Apostas restantes: {final_remaining}")
    
    # Opção 3: Mix equilibrado
    if available >= 15:
        tickets_7x = 1
        remaining_after_7x = available - 7
        tickets_5x = 1 if remaining_after_7x >= 8 else 0
        remaining_after_5x = remaining_after_7x - (5 if tickets_5x else 0)
        tickets_3x = remaining_after_5x // 3
        final_remaining = remaining_after_5x % 3
        
        print(f"\n      Opção C - Mix 3X + 5X + 7X:")
        print(f"         {tickets_3x} bilhetes 3X (prob: {(threshold**3)*100:.1f}%)")
        print(f"         {tickets_5x} bilhete 5X (prob: {(threshold**5)*100:.1f}%)")
        print(f"         {tickets_7x} bilhete 7X (prob: {(threshold**7)*100:.1f}%)")
        print(f"         Apostas restantes: {final_remaining}")
    
    print()

print("="*80)
print("🎯 RECOMENDAÇÃO FINAL COM 60 PARTIDAS/DIA:")
print("="*80 + "\n")

print("   ✅ COM 60 PARTIDAS DISPONÍVEIS:\n")

print("      • Threshold 85% (Bom):")
print("         ✓ ~2 bilhetes 3X/dia (prob combinada: 61.4%)")
print("         ✓ ~1 bilhete 5X/dia (prob combinada: 44.4%)")
print("         ✓ Disponibilidade: ~11 apostas elegíveis")
print()

print("      • Threshold 82% (Balanceado) - RECOMENDADO:")
print("         ✓ ~3 bilhetes 3X/dia (prob combinada: 55.1%)")
print("         ✓ ~1 bilhete 5X/dia (prob combinada: 37.1%)")
print("         ✓ ~1 bilhete 7X/semana (prob combinada: 25.0%)")
print("         ✓ Disponibilidade: ~13-15 apostas elegíveis")
print()

print("      • Threshold 80% (Aceitável):")
print("         ✓ ~4 bilhetes 3X/dia (prob combinada: 51.2%)")
print("         ✓ ~2 bilhetes 5X/dia (prob combinada: 32.8%)")
print("         ✓ ~1 bilhete 7X/dia (prob combinada: 21.0%)")
print("         ✓ Disponibilidade: ~18 apostas elegíveis")
print()

print("   🎯 CONFIGURAÇÃO SUGERIDA:")
print()
print("      MIN_MULTIPLE_PROBABILITY_3X = 0.82  # 82%")
print("      MIN_MULTIPLE_PROBABILITY_5X = 0.84  # 84%")
print("      MIN_MULTIPLE_PROBABILITY_7X = 0.86  # 86%")
print()
print("      MIN_COMBINED_PROBABILITY_3X = 0.50  # 50%")
print("      MIN_COMBINED_PROBABILITY_5X = 0.40  # 40%")
print("      MIN_COMBINED_PROBABILITY_7X = 0.35  # 35%")
print()
print("   💡 PRODUÇÃO DIÁRIA ESPERADA:")
print("      • 2-3 bilhetes 3X (alta acertividade)")
print("      • 1-2 bilhetes 5X (boa acertividade)")
print("      • 0-1 bilhete 7X (acertividade moderada)")
print()
print("   📊 TAXA DE ACERTO ESPERADA:")
print("      • Bilhetes 3X: 55% (5-6 acertos em 10 bilhetes)")
print("      • Bilhetes 5X: 40% (4 acertos em 10 bilhetes)")
print("      • Bilhetes 7X: 35% (3-4 acertos em 10 bilhetes)")
print()
print("   ✅ BILHETES 10X:")
print("      • NÃO RECOMENDADO mesmo com 60 partidas")
print("      • Requereria threshold muito baixo (<80%)")
print("      • Prob combinada seria < 20% (2 acertos em 10)")
print("      • Melhor estratégia: 5X e 7X oferecem odds altas com mais segurança")

print("\n" + "="*80 + "\n")
