import os
import django
from datetime import datetime, timedelta
import math

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet

print("\n" + "="*80)
print("🔍 ANÁLISE: VIABILIDADE DE BILHETES 10X")
print("="*80 + "\n")

# Verificar suporte atual
print("📋 SUPORTE ATUAL NO SISTEMA:")
print("─"*80)
print("   Bilhetes suportados: 3X, 5X, 7X")
print("   ❌ Bilhetes 10X: NÃO IMPLEMENTADO")
print()

# Analisar últimos 14 dias
days_back = 14
start_date = datetime.now() - timedelta(days=days_back)

all_bets = DailyBet.objects.filter(
    created_at__gte=start_date
).order_by('-created_at')

# Extrair apostas individuais
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

print("="*80)
print("🧮 MATEMÁTICA DOS BILHETES 10X:")
print("="*80 + "\n")

# Calcular threshold necessário para diferentes probs combinadas
target_probs = [0.50, 0.40, 0.30, 0.25, 0.20]

print("   Para um bilhete 10X ter probabilidade combinada de:")
print()
for target in target_probs:
    individual_needed = target ** (1/10)
    print(f"   • {target*100:.0f}%: cada aposta precisa ter ≥{individual_needed*100:.2f}%")

print("\n" + "="*80)
print("📊 DISPONIBILIDADE DE APOSTAS:")
print("="*80 + "\n")

# Contar apostas por threshold
thresholds = [0.933, 0.912, 0.893, 0.870, 0.850, 0.800]
threshold_names = ["93.3% (50% comb)", "91.2% (40% comb)", "89.3% (30% comb)", "87.0% (25% comb)", "85.0% (20% comb)", "80.0% (ref 3X)"]

print(f"   📈 Total de apostas analisadas (14 dias): {len(individual_bets)}\n")

availability = {}
for threshold, name in zip(thresholds, threshold_names):
    eligible = [b for b in individual_bets if b['probability'] >= threshold]
    eligible_odds = [b for b in eligible if 1.10 <= b['odd'] <= 1.50]
    
    per_day = len(eligible_odds) / days_back
    availability[name] = {
        'total': len(eligible),
        'with_odds': len(eligible_odds),
        'per_day': per_day
    }
    
    print(f"   Threshold {name}:")
    print(f"      Total elegíveis: {len(eligible)} ({len(eligible)/len(individual_bets)*100:.1f}%)")
    print(f"      Com odd 1.10-1.50: {len(eligible_odds)} ({len(eligible_odds)/len(individual_bets)*100:.1f}%)")
    print(f"      Média por dia: {per_day:.2f}")
    
    if per_day >= 10:
        print(f"      ✅ VIÁVEL - Pode gerar ~1 bilhete 10X por dia")
    elif per_day >= 5:
        print(f"      ⚠️  LIMITADO - Bilhete 10X ocasional (2-3/semana)")
    elif per_day >= 2:
        print(f"      ⚠️  RARO - Bilhete 10X raro (1/semana)")
    else:
        print(f"      ❌ INVIÁVEL - Bilhete 10X muito raro ou impossível")
    print()

print("="*80)
print("💡 ANÁLISE DE VIABILIDADE:")
print("="*80 + "\n")

# Comparar com bilhetes existentes
print("   📊 Comparação com bilhetes atuais:\n")

sizes = [3, 5, 7, 10]
for size in sizes:
    # Target: 50% combined
    if size == 10:
        needed_prob = 0.50 ** (1/size)
        available = availability.get("93.3% (50% comb)", {}).get('per_day', 0)
    elif size == 7:
        needed_prob = 0.91
        available = availability.get("87.0% (25% comb)", {}).get('per_day', 0)  # Aproximação
    elif size == 5:
        needed_prob = 0.87
        available = availability.get("87.0% (25% comb)", {}).get('per_day', 0)
    else:  # 3
        needed_prob = 0.80
        available = availability.get("80.0% (ref 3X)", {}).get('per_day', 0)
    
    if size == 10:
        # Calcular para diferentes targets
        targets = [
            (0.50, 0.933),
            (0.40, 0.912),
            (0.30, 0.893),
            (0.25, 0.870),
            (0.20, 0.850)
        ]
        
        print(f"   🎯 Bilhete {size}X:")
        for target_comb, target_ind in targets:
            threshold_key = [k for k in availability.keys() if f"{target_ind*100:.1f}%" in k][0]
            avail = availability[threshold_key]['per_day']
            
            # Taxa de acerto esperada (em 10 bilhetes)
            expected_wins = int(target_comb * 10)
            
            viability = "✅" if avail >= size else "⚠️" if avail >= size/2 else "❌"
            
            print(f"      • Target {target_comb*100:.0f}% combinado (cada aposta ≥{target_ind*100:.1f}%):")
            print(f"        Disponibilidade: {avail:.2f} apostas/dia {viability}")
            print(f"        Taxa esperada: {expected_wins} acertos em 10 bilhetes")
    else:
        print(f"   🎯 Bilhete {size}X:")
        print(f"      Threshold individual: ≥{needed_prob*100:.0f}%")
        print(f"      Disponibilidade: {available:.2f} apostas/dia")

print("\n" + "="*80)
print("🎲 CENÁRIOS POSSÍVEIS PARA BILHETES 10X:")
print("="*80 + "\n")

scenarios = [
    {
        'name': 'CONSERVADOR (50% combinado)',
        'threshold': 93.3,
        'combined': 50,
        'available': availability.get("93.3% (50% comb)", {}).get('per_day', 0),
        'expected_wins': 5,
        'frequency': 'Muito Raro'
    },
    {
        'name': 'MODERADO (40% combinado)',
        'threshold': 91.2,
        'combined': 40,
        'available': availability.get("91.2% (40% comb)", {}).get('per_day', 0),
        'expected_wins': 4,
        'frequency': 'Raro'
    },
    {
        'name': 'ARRISCADO (30% combinado)',
        'threshold': 89.3,
        'combined': 30,
        'available': availability.get("89.3% (30% comb)", {}).get('per_day', 0),
        'expected_wins': 3,
        'frequency': 'Ocasional'
    },
    {
        'name': 'MUITO ARRISCADO (20% combinado)',
        'threshold': 85.0,
        'combined': 20,
        'available': availability.get("85.0% (20% comb)", {}).get('per_day', 0),
        'expected_wins': 2,
        'frequency': 'Possível'
    }
]

for scenario in scenarios:
    print(f"   📌 {scenario['name']}")
    print(f"      Threshold individual: ≥{scenario['threshold']:.1f}%")
    print(f"      Prob combinada: {scenario['combined']}%")
    print(f"      Apostas disponíveis/dia: {scenario['available']:.2f}")
    print(f"      Taxa de acerto esperada: {scenario['expected_wins']} em 10 bilhetes")
    print(f"      Frequência de geração: {scenario['frequency']}")
    
    if scenario['available'] >= 10:
        print(f"      Status: ✅ VIÁVEL (~1 bilhete/dia)")
    elif scenario['available'] >= 5:
        print(f"      Status: ⚠️  OCASIONAL (2-3 bilhetes/semana)")
    elif scenario['available'] >= 2:
        print(f"      Status: ⚠️  RARO (~1 bilhete/semana)")
    else:
        print(f"      Status: ❌ MUITO RARO (< 1 bilhete/semana)")
    print()

print("="*80)
print("🎯 RECOMENDAÇÃO FINAL:")
print("="*80 + "\n")

best_available = availability.get("85.0% (20% comb)", {}).get('per_day', 0)

if best_available >= 10:
    print("   ✅ IMPLEMENTAR bilhetes 10X")
    print("      • Há apostas suficientes para geração consistente")
    print("      • Usar threshold 85-87% (20-25% prob combinada)")
    print("      • Aceitar taxa de acerto de 2-3 em 10")
elif best_available >= 5:
    print("   ⚠️  CONSIDERAR bilhetes 10X (com ressalvas)")
    print("      • Geração será OCASIONAL (2-3 bilhetes/semana)")
    print("      • Usar threshold 85-89% (20-30% prob combinada)")
    print("      • Ideal para usuários que buscam odds ALTAS")
    print("      • ROI dependerá de gestão de banca rigorosa")
elif best_available >= 2:
    print("   ⚠️  NÃO RECOMENDADO (dados insuficientes)")
    print("      • Geração seria RARA (~1 bilhete/semana)")
    print("      • Taxa de acerto muito baixa (2-3 em 10)")
    print("      • Risco alto vs retorno incerto")
    print("      • Melhor focar em 3X, 5X, 7X")
else:
    print("   ❌ NÃO IMPLEMENTAR bilhetes 10X")
    print("      • Apostas insuficientes no histórico atual")
    print("      • Mesmo com threshold baixo (85%), < 2 apostas/dia")
    print("      • Taxa de acerto seria MUITO BAIXA")
    print("      • Foco deve estar em 3X e 5X com alta qualidade")

print("\n   💡 Alternativa melhor:")
print("      • Manter foco em bilhetes 3X e 5X com alta acertividade")
print("      • Bilhetes 7X já são desafiantes com dados atuais")
print("      • Odds altas podem vir de bilhetes 5X com apostas ~85-90%")
print("      • Exemplo: 5X com odds 1.40 cada = odd total 5.38 (vs 10X necessário)")

print("\n   📊 Odds comparadas:")
prob_85 = 0.85
odd_85 = 1 / prob_85

# 10X com 85%
combined_10x = prob_85 ** 10
odd_10x = 10 ** odd_85
print(f"      • Bilhete 10X (85% cada): Odd total ~{odd_10x:.2f}, Prob combinada: {combined_10x*100:.1f}%")

# 5X com 85%
combined_5x = prob_85 ** 5
odd_5x = 5 * odd_85
print(f"      • Bilhete 5X (85% cada): Odd total ~{odd_5x:.2f}, Prob combinada: {combined_5x*100:.1f}%")

# 3X com 85%
combined_3x = prob_85 ** 3
odd_3x = 3 * odd_85
print(f"      • Bilhete 3X (85% cada): Odd total ~{odd_3x:.2f}, Prob combinada: {combined_3x*100:.1f}%")

print("\n" + "="*80 + "\n")
