import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet

# Ontem = 16 de fevereiro de 2026
yesterday = date.today() - timedelta(days=1)

print(f"\n{'='*80}")
print(f"ANÁLISE COMPLETA - TODOS OS BILHETES DE {yesterday.strftime('%d/%m/%Y')}")
print(f"{'='*80}\n")

for bet_id in [70, 71, 72]:  # 3x, 5x, 7x
    bet = DailyBet.objects.get(id=bet_id)
    size = len(bet.selections)
    
    print(f"\n{'═'*80}")
    print(f"BILHETE {size}X (ID: {bet_id})")
    print(f"{'═'*80}")
    print(f"Odd Total: {bet.total_odd}")
    print(f"Prob Combinada: {bet.combined_probability * 100:.2f}%")
    print(f"Expected Value: {bet.expected_value:.2f}%")
    print(f"Status: {bet.get_status_display()}")
    
    print(f"\n📊 SELEÇÕES INDIVIDUAIS:\n")
    manual_prob = 1.0
    
    for i, sel in enumerate(bet.selections, 1):
        prob = sel.get('probability', 0)
        odd = sel.get('odd', 0)
        manual_prob *= prob
        
        status = ''
        if prob < 0.50:
            status = '❌ < 50%'
        elif prob < 0.70:
            status = '⚠️ < 70%'
        elif prob < 0.80:
            status = '🟡 < 80%'
        else:
            status = '✅ ≥ 80%'
        
        print(f"   {i}. {sel.get('match', 'N/A')}")
        print(f"      Mercado: {sel.get('market', 'N/A')} - {sel.get('pick', 'N/A')}")
        print(f"      Prob: {prob*100:.2f}% @ {odd:.2f} {status}")
    
    # Calcular probabilidade mínima necessária
    target_combined = 0.50  # 50% de chance de acerto
    min_individual = target_combined ** (1/size)
    
    print(f"\n{'─'*80}")
    print(f"📐 MATEMÁTICA DO BILHETE {size}X:\n")
    print(f"   Prob Combinada Atual: {manual_prob*100:.2f}%")
    print(f"   Prob Combinada Alvo (50%): {target_combined*100:.0f}%")
    print(f"   Prob Individual Necessária: ≥ {min_individual*100:.2f}%")
    print(f"   (Cálculo: {target_combined}^(1/{size}) = {min_individual:.4f})")
    
    # Verificar quantas apostas atendem o critério
    meets_criteria = sum(1 for sel in bet.selections if sel.get('probability', 0) >= min_individual)
    print(f"\n   ✅ Apostas que atendem critério: {meets_criteria}/{size}")
    
    if manual_prob >= 0.50:
        print(f"\n   ✅ BILHETE BOM: Prob combinada ≥ 50%")
    elif manual_prob >= 0.30:
        print(f"\n   🟡 BILHETE MÉDIO: Prob combinada entre 30-50%")
    else:
        print(f"\n   ❌ BILHETE ARRISCADO: Prob combinada < 30%")
    
    # Taxa de acerto esperada
    expected_wins = int(1 / manual_prob) if manual_prob > 0 else 0
    print(f"\n   📊 Taxa esperada: 1 acerto a cada ~{expected_wins} tentativas")

print(f"\n{'═'*80}")
print(f"CONCLUSÕES:")
print(f"{'═'*80}\n")

# Análise geral
bet_3x = DailyBet.objects.get(id=70)
bet_5x = DailyBet.objects.get(id=71)
bet_7x = DailyBet.objects.get(id=72)

probs = [
    (3, bet_3x.combined_probability),
    (5, bet_5x.combined_probability), 
    (7, bet_7x.combined_probability)
]

print("📊 Probabilidades Combinadas:")
for size, prob in probs:
    status = '✅' if prob >= 0.50 else ('🟡' if prob >= 0.30 else '❌')
    print(f"   {size}x: {prob*100:.2f}% {status}")

print(f"\n💡 RECOMENDAÇÕES:\n")
print("   Para bilhetes múltiplos com ≥50% de acerto:")
print("   • 3x: cada aposta ≥ 79.4%")
print("   • 5x: cada aposta ≥ 87.1%")
print("   • 7x: cada aposta ≥ 90.7%")
print("   • 10x: cada aposta ≥ 93.3%")

print(f"\n{'='*80}\n")
