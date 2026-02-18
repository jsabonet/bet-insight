import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet

print("\n" + "="*80)
print("🔍 ANÁLISE: VIABILIDADE DE BILHETES 5X E 7X COM NOVOS THRESHOLDS")
print("="*80 + "\n")

# Analisar últimos 14 dias
days_back = 14
start_date = datetime.now() - timedelta(days=days_back)

all_bets = DailyBet.objects.filter(
    created_at__gte=start_date
).order_by('-created_at')

print(f"📊 Período analisado: Últimos {days_back} dias")
print(f"📈 Total de apostas geradas: {all_bets.count()}\n")

# Extrair todas as apostas individuais dos bilhetes
individual_bets = []
for bet in all_bets:
    if isinstance(bet.selections, list):
        for selection in bet.selections:
            individual_bets.append({
                'match': selection.get('match', 'N/A'),
                'probability': selection.get('probability', 0),
                'odd': selection.get('odd', 0),
                'market': selection.get('market', 'N/A'),
                'score': selection.get('score', 0),
                'date': bet.created_at.strftime('%d/%m/%Y')
            })

print(f"🎯 Apostas individuais extraídas: {len(individual_bets)}\n")

print("="*80)
print("📊 DISTRIBUIÇÃO DE PROBABILIDADES:")
print("="*80 + "\n")

# Contar apostas por faixa de probabilidade
ranges = [
    (0.95, 1.00, "≥95%", "🌟"),
    (0.91, 0.95, "91-95%", "⭐⭐⭐"),
    (0.87, 0.91, "87-91%", "⭐⭐"),
    (0.80, 0.87, "80-87%", "⭐"),
    (0.70, 0.80, "70-80%", "✓"),
    (0.60, 0.70, "60-70%", "○"),
    (0.00, 0.60, "<60%", "✗"),
]

range_counts = {}
for min_prob, max_prob, label, icon in ranges:
    count = len([b for b in individual_bets if min_prob <= b['probability'] < max_prob])
    percentage = (count / len(individual_bets) * 100) if individual_bets else 0
    range_counts[label] = count
    
    bar = "█" * int(percentage / 2)
    print(f"   {icon} {label:8s}: {count:4d} apostas ({percentage:5.1f}%) {bar}")

print("\n" + "="*80)
print("🎯 VIABILIDADE DOS THRESHOLDS:")
print("="*80 + "\n")

# Threshold para 3X (80%)
eligible_3x = [b for b in individual_bets if b['probability'] >= 0.80]
eligible_3x_odds = [b for b in eligible_3x if 1.10 <= b['odd'] <= 1.50]

print("   📌 BILHETES 3X (threshold: ≥80%)")
print(f"      Apostas elegíveis: {len(eligible_3x)} ({len(eligible_3x)/len(individual_bets)*100:.1f}%)")
print(f"      Com odd no range (1.10-1.50): {len(eligible_3x_odds)} ({len(eligible_3x_odds)/len(individual_bets)*100:.1f}%)")
print(f"      Bilhetes possíveis/dia: ~{len(eligible_3x_odds) // 3}")
if len(eligible_3x_odds) >= 3:
    print(f"      Status: ✅ VIÁVEL - Suficiente para formar bilhetes 3X")
else:
    print(f"      Status: ⚠️  BAIXA - Pode haver dias sem bilhetes 3X")

# Threshold para 5X (87%)
eligible_5x = [b for b in individual_bets if b['probability'] >= 0.87]
eligible_5x_odds = [b for b in eligible_5x if 1.10 <= b['odd'] <= 1.50]

print(f"\n   📌 BILHETES 5X (threshold: ≥87%)")
print(f"      Apostas elegíveis: {len(eligible_5x)} ({len(eligible_5x)/len(individual_bets)*100:.1f}%)")
print(f"      Com odd no range (1.10-1.50): {len(eligible_5x_odds)} ({len(eligible_5x_odds)/len(individual_bets)*100:.1f}%)")
print(f"      Bilhetes possíveis/dia: ~{len(eligible_5x_odds) // 5}")
if len(eligible_5x_odds) >= 5:
    print(f"      Status: ✅ VIÁVEL - Suficiente para formar bilhetes 5X")
elif len(eligible_5x_odds) >= 3:
    print(f"      Status: ⚠️  LIMITADO - Pode não haver bilhetes 5X todos os dias")
else:
    print(f"      Status: ❌ INVIÁVEL - Threshold muito alto para bilhetes 5X consistentes")

# Threshold para 7X (91%)
eligible_7x = [b for b in individual_bets if b['probability'] >= 0.91]
eligible_7x_odds = [b for b in eligible_7x if 1.10 <= b['odd'] <= 1.50]

print(f"\n   📌 BILHETES 7X (threshold: ≥91%)")
print(f"      Apostas elegíveis: {len(eligible_7x)} ({len(eligible_7x)/len(individual_bets)*100:.1f}%)")
print(f"      Com odd no range (1.10-1.50): {len(eligible_7x_odds)} ({len(eligible_7x_odds)/len(individual_bets)*100:.1f}%)")
print(f"      Bilhetes possíveis/dia: ~{len(eligible_7x_odds) // 7}")
if len(eligible_7x_odds) >= 7:
    print(f"      Status: ✅ VIÁVEL - Suficiente para formar bilhetes 7X")
elif len(eligible_7x_odds) >= 3:
    print(f"      Status: ⚠️  LIMITADO - Pode não haver bilhetes 7X todos os dias")
else:
    print(f"      Status: ❌ INVIÁVEL - Threshold muito alto para bilhetes 7X consistentes")

# Mostrar exemplos das apostas mais prováveis
print("\n" + "="*80)
print("🌟 TOP 10 APOSTAS MAIS PROVÁVEIS (últimos 14 dias):")
print("="*80 + "\n")

top_bets = sorted(individual_bets, key=lambda x: x['probability'], reverse=True)[:10]
for i, bet in enumerate(top_bets, 1):
    eligible_for = []
    if bet['probability'] >= 0.91:
        eligible_for.append("7X")
    if bet['probability'] >= 0.87:
        eligible_for.append("5X")
    if bet['probability'] >= 0.80:
        eligible_for.append("3X")
    
    odds_ok = "✅" if 1.10 <= bet['odd'] <= 1.50 else "❌"
    
    print(f"   {i}. {bet['match'][:50]}")
    print(f"      Prob: {bet['probability']*100:.2f}% | Odd: {bet['odd']:.2f} {odds_ok}")
    print(f"      Elegível para: {', '.join(eligible_for) if eligible_for else 'Nenhum'}")
    print(f"      Data: {bet['date']}")
    print()

print("="*80)
print("💡 RECOMENDAÇÕES:")
print("="*80 + "\n")

# Calcular taxa de disponibilidade por dia
apostas_por_dia = len(individual_bets) / days_back
eligible_3x_por_dia = len(eligible_3x_odds) / days_back
eligible_5x_por_dia = len(eligible_5x_odds) / days_back
eligible_7x_por_dia = len(eligible_7x_odds) / days_back

print(f"   📊 Apostas médias por dia:")
print(f"      Total: {apostas_por_dia:.1f}")
print(f"      Elegíveis 3X (≥80%): {eligible_3x_por_dia:.1f}")
print(f"      Elegíveis 5X (≥87%): {eligible_5x_por_dia:.1f}")
print(f"      Elegíveis 7X (≥91%): {eligible_7x_por_dia:.1f}")

print(f"\n   🎯 Cenários esperados:\n")

if eligible_3x_por_dia >= 3:
    print(f"      ✅ Bilhetes 3X: Geração CONSISTENTE (~1 bilhete/dia)")
else:
    print(f"      ⚠️  Bilhetes 3X: Geração INTERMITENTE")

if eligible_5x_por_dia >= 5:
    print(f"      ✅ Bilhetes 5X: Geração FREQUENTE (~1 bilhete/dia)")
elif eligible_5x_por_dia >= 2:
    print(f"      ⚠️  Bilhetes 5X: Geração OCASIONAL (~2-3 bilhetes/semana)")
else:
    print(f"      ❌ Bilhetes 5X: Geração RARA ou INEXISTENTE")

if eligible_7x_por_dia >= 7:
    print(f"      ✅ Bilhetes 7X: Geração POSSÍVEL (~1 bilhete/dia)")
elif eligible_7x_por_dia >= 3:
    print(f"      ⚠️  Bilhetes 7X: Geração RARA (~1 bilhete/semana)")
else:
    print(f"      ❌ Bilhetes 7X: Geração MUITO RARA ou INEXISTENTE")

print(f"\n   💡 Ajustes sugeridos:\n")

if eligible_5x_por_dia < 5:
    print(f"      📉 BILHETES 5X:")
    # Calcular threshold alternativo
    target_count = 5
    sorted_probs = sorted([b['probability'] for b in individual_bets], reverse=True)
    if len(sorted_probs) >= target_count * days_back:
        alt_threshold_5x = sorted_probs[int(target_count * days_back) - 1]
        print(f"         Threshold atual: 87%")
        print(f"         Para ter ~5 apostas/dia: {alt_threshold_5x*100:.1f}%")
        print(f"         Sugestão: Reduzir para 84-85% OU")
        print(f"         Aceitar geração ocasional (2-3 bilhetes/semana)")
    else:
        print(f"         Threshold atual: 87%")
        print(f"         ⚠️  Dados insuficientes para calcular threshold alternativo")
        print(f"         Sugestão: Reduzir para 82-85% OU")
        print(f"         Aceitar geração rara/ocasional")

if eligible_7x_por_dia < 7:
    print(f"\n      📉 BILHETES 7X:")
    target_count = 7
    sorted_probs = sorted([b['probability'] for b in individual_bets], reverse=True)
    if len(sorted_probs) >= target_count * days_back:
        alt_threshold_7x = sorted_probs[int(target_count * days_back) - 1]
        print(f"         Threshold atual: 91%")
        print(f"         Para ter ~7 apostas/dia: {alt_threshold_7x*100:.1f}%")
        print(f"         Sugestão: Reduzir para 86-88% OU")
        print(f"         Aceitar geração rara (1-2 bilhetes/semana)")
    else:
        print(f"         Threshold atual: 91%")
        print(f"         ⚠️  Dados insuficientes para calcular threshold alternativo")
        print(f"         Sugestão: Reduzir para 85-88% OU")
        print(f"         Aceitar geração muito rara")

print(f"\n   🎲 ALTERNATIVA - THRESHOLDS BALANCEADOS:")
print(f"      Para manter prob combinada ≥50% E ter disponibilidade:")
print(f"      • 3X: ≥80% (mantém) → Combinado: 51.2%")
print(f"      • 5X: ≥85% (reduz 2pp) → Combinado: 44.4% (ajustar min combinado para 44%)")
print(f"      • 7X: ≥88% (reduz 3pp) → Combinado: 42.5% (ajustar min combinado para 42%)")
print(f"\n      Ou aceitar que bilhetes 5X e 7X sejam mais raros mas com alta qualidade.")

print("\n" + "="*80 + "\n")
