import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet

# Ontem = 16 de fevereiro de 2026
yesterday = date.today() - timedelta(days=1)

print(f"\n{'='*80}")
print(f"ANÁLISE DETALHADA DOS BILHETES DE {yesterday.strftime('%d/%m/%Y')}")
print(f"{'='*80}\n")

# Buscar bilhete 3x que venceu
bet_3x = DailyBet.objects.get(id=70)

print("📊 BILHETE 3X (ID: 70) - VENCEU")
print(f"{'─'*80}")
print(f"Odd Total: {bet_3x.total_odd}")
print(f"Probabilidade Combinada: {bet_3x.combined_probability * 100:.4f}%")
print(f"Expected Value: {bet_3x.expected_value:.2f}%")
print(f"\n🔍 ANÁLISE DAS SELEÇÕES:\n")

for i, sel in enumerate(bet_3x.selections, 1):
    print(f"{i}. {sel.get('match', 'N/A')}")
    print(f"   Mercado: {sel.get('market', 'N/A')}")
    print(f"   Pick: {sel.get('pick', 'N/A')}")
    print(f"   Odd: {sel.get('odd', 0):.2f}")
    print(f"   Probabilidade: {sel.get('probability', 0) * 100:.2f}%")
    print(f"   EV: {sel.get('ev_pct', 0):.2f}%")
    if 'score' in sel:
        print(f"   Score: {sel.get('score', 0):.4f}")
    print()

# Verificar cálculo manual
print(f"{'─'*80}")
print("🧮 VERIFICAÇÃO DE CÁLCULOS:\n")

manual_odd = 1.0
manual_prob = 1.0

for sel in bet_3x.selections:
    odd = sel.get('odd', 0)
    prob = sel.get('probability', 0)
    manual_odd *= odd
    manual_prob *= prob
    print(f"   {sel.get('market', 'N/A')}: {prob*100:.2f}% @ {odd:.2f}")

print(f"\n📐 Odd calculada manualmente: {manual_odd:.2f}")
print(f"📐 Odd no banco: {float(bet_3x.total_odd):.2f}")
print(f"✅ Match: {abs(manual_odd - float(bet_3x.total_odd)) < 0.01}")

print(f"\n📊 Prob calculada manualmente: {manual_prob * 100:.4f}%")
print(f"📊 Prob no banco: {bet_3x.combined_probability * 100:.4f}%")
print(f"✅ Match: {abs(manual_prob - bet_3x.combined_probability) < 0.0001}")

print(f"\n{'─'*80}")
print("⚠️  PROBLEMA IDENTIFICADO:\n")

if manual_prob < 0.01:  # < 1%
    print("❌ Probabilidade combinada EXTREMAMENTE BAIXA!")
    print(f"   Com prob combinada de {manual_prob*100:.4f}%, esperamos 1 acerto a cada {int(1/manual_prob)} tentativas")
    print(f"\n💡 Para bilhete 3x ter 50% de chance de acerto:")
    print(f"   Cada aposta precisa ter ≥ {(0.5**(1/3))*100:.1f}% de probabilidade")
    print(f"   (Cálculo: 0.5^(1/3) = {0.5**(1/3):.4f})")
    
    print(f"\n💡 Probabilidades atuais das apostas:")
    for i, sel in enumerate(bet_3x.selections, 1):
        prob = sel.get('probability', 0) * 100
        print(f"   {i}. {prob:.2f}% {'❌ MUITO BAIXA!' if prob < 79 else '✅'}")

print(f"\n{'='*80}\n")
