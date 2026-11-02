import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.daily_bet_generator import DailyBetGenerator

print("\n" + "="*80)
print("TESTE: FILTROS ATUAIS PARA BILHETES")
print("="*80 + "\n")

generator = DailyBetGenerator()

print("📊 CONFIGURAÇÕES ANTERIORES (16/02/2026):")
print("─"*80)
print("   Probabilidades Mínimas Individuais:")
print("      3X, 5X, 7X: ≥50% (única para todos)")
print("   Probabilidades Combinadas Mínimas:")
print("      3X: ≥15%")
print("      5X: ≥8%")
print("      7X: ≥4%")
print("   Filtros de Contexto:")
print("      ❌ Sem filtro de empate")
print("      ❌ Sem filtro de confidence")
print("      ❌ Sem filtro de risco")
print("   Ordenação:")
print("      Por probabilidade apenas (sem contexto)")
print("   EV por seleção:")
print("      EV ≥ 0%; sem faixa fixa de odds individuais")

print("\n" + "="*80)
print("📊 CONFIGURAÇÕES ATUAIS:")
print("─"*80)
print("   Probabilidades Mínimas Individuais:")
print(f"      3X: ≥{generator.MIN_MULTIPLE_PROBABILITY_3X*100:.0f}% (era 50%)")
print(f"      5X: ≥{generator.MIN_MULTIPLE_PROBABILITY_5X*100:.0f}% (era 50%)")
print(f"      7X: ≥{generator.MIN_MULTIPLE_PROBABILITY_7X*100:.0f}% (era 50%)")
print("   Probabilidades Combinadas Mínimas:")
print(f"      3X: ≥{generator.MIN_COMBINED_PROBABILITY_3X*100:.0f}% (era 15%)")
print(f"      5X: ≥{generator.MIN_COMBINED_PROBABILITY_5X*100:.0f}% (era 8%)")
print(f"      7X: ≥{generator.MIN_COMBINED_PROBABILITY_7X*100:.0f}% (era 4%)")
print("   Filtros de Contexto:")
print(f"      ✅ Empate máximo: {generator.MAX_DRAW_PROBABILITY*100:.0f}%")
print(f"      ✅ Confidence mínima: {generator.MIN_CONFIDENCE_STARS} estrelas")
print(f"      ✅ Risco permitido: {', '.join(generator.ALLOWED_RISK_LEVELS)}")
print("   Ordenação:")
print("      ✅ Por SCORE contextual (prob × contexto × EV × conf × risco)")
print("   EV por seleção:")
print(f"      ≥{generator.MIN_MULTIPLE_EV:.0f}%; odd total do bilhete: {generator.MIN_TICKET_ODD:.2f}-{generator.MAX_TICKET_ODD:.2f}")

print("\n" + "="*80)
print("🧮 MATEMÁTICA DOS BILHETES:")
print("─"*80)

# Calcular probabilidades esperadas
for size in [3, 5, 7]:
    if size == 3:
        min_prob = generator.MIN_MULTIPLE_PROBABILITY_3X
        combined_target = generator.MIN_COMBINED_PROBABILITY_3X
    elif size == 5:
        min_prob = generator.MIN_MULTIPLE_PROBABILITY_5X
        combined_target = generator.MIN_COMBINED_PROBABILITY_5X
    else:
        min_prob = generator.MIN_MULTIPLE_PROBABILITY_7X
        combined_target = generator.MIN_COMBINED_PROBABILITY_7X
    
    # Calcular prob combinada se todas as apostas tiverem prob mínima
    correlation_penalty = {3: 0.95, 5: 0.90, 7: 0.85}[size]
    combined_actual = min_prob ** size * correlation_penalty
    
    print(f"\n   Bilhete {size}X:")
    print(f"      Prob Individual Mínima: {min_prob*100:.1f}%")
    print(f"      Prob Combinada Esperada: {combined_actual*100:.2f}%")
    print(f"      Prob Combinada Mínima: {combined_target*100:.0f}%")
    status = "✅" if combined_actual >= combined_target else "❌"
    print(f"      Status: {status} {'Atende' if combined_actual >= combined_target else 'Não atende'}")
    
    # Taxa de acerto esperada
    expected_wins = int(1 / combined_actual) if combined_actual > 0 else 0
    print(f"      Taxa Esperada: 1 acerto a cada ~{expected_wins} tentativas")

print("\n" + "="*80)
print("📈 IMPACTO NOS BILHETES DE 16/02/2026:")
print("─"*80)

# Simular com dados antigos
old_bets = [
    {"match": "Deportivo Riestra vs Newells Old Boys", "prob": 0.9583, "odd": 1.33},
    {"match": "Macclesfield vs Brentford", "prob": 0.8779, "odd": 1.33},
    {"match": "Septemvri Sofia vs Montana", "prob": 0.8442, "odd": 1.36},
    {"match": "Qabala vs Sabah FA", "prob": 0.8361, "odd": 1.35},
    {"match": "Enppi vs National Bank", "prob": 0.7725, "odd": 1.33},
    {"match": "Borac Cacak vs Jedinstvo Ub", "prob": 0.7455, "odd": 1.62},
    {"match": "Santa Clara U23 vs Leixões U23", "prob": 0.7302, "odd": 1.80},
]

print("\n   🔍 VALIDAÇÃO COM NOVOS FILTROS:\n")

for i, bet in enumerate(old_bets, 1):
    print(f"   {i}. {bet['match']}")
    print(f"      Prob: {bet['prob']*100:.2f}% | Odd: {bet['odd']:.2f}")
    
    # Verificar se passa nos novos filtros
    passes = []
    fails = []
    
    # Check 3X (mais permissivo)
    if bet['prob'] >= generator.MIN_MULTIPLE_PROBABILITY_3X:
        passes.append(f"3X (≥{generator.MIN_MULTIPLE_PROBABILITY_3X*100:.0f}%)")
    else:
        fails.append(f"3X (≥{generator.MIN_MULTIPLE_PROBABILITY_3X*100:.0f}%)")
    
    # Check 5X
    if bet['prob'] >= generator.MIN_MULTIPLE_PROBABILITY_5X:
        passes.append(f"5X (≥{generator.MIN_MULTIPLE_PROBABILITY_5X*100:.0f}%)")
    else:
        fails.append(f"5X (≥{generator.MIN_MULTIPLE_PROBABILITY_5X*100:.0f}%)")
    
    # Check 7X (mais restritivo)
    if bet['prob'] >= generator.MIN_MULTIPLE_PROBABILITY_7X:
        passes.append(f"7X (≥{generator.MIN_MULTIPLE_PROBABILITY_7X*100:.0f}%)")
    else:
        fails.append(f"7X (≥{generator.MIN_MULTIPLE_PROBABILITY_7X*100:.0f}%)")
    
    ev_pct = (bet['prob'] * bet['odd'] - 1) * 100
    if ev_pct >= generator.MIN_MULTIPLE_EV:
        passes.append(f"EV ≥{generator.MIN_MULTIPLE_EV:.0f}% ({ev_pct:+.1f}%)")
    else:
        fails.append(f"EV <{generator.MIN_MULTIPLE_EV:.0f}% ({ev_pct:+.1f}%)")
    
    if passes:
        print(f"      ✅ Passa em: {', '.join(passes)}")
    if fails:
        print(f"      ❌ Falha em: {', '.join(fails)}")
    print()

print("="*80)
print("💡 CONCLUSÕES:")
print("─"*80)
print("   • Bilhetes 3X: cada seleção exige probabilidade ≥65%")
print("   • Bilhetes 5X: cada seleção exige probabilidade ≥68%")
print("   • Bilhetes 7X: cada seleção exige probabilidade ≥70%")
print("   • Filtros de contexto excluem jogos arriscados (empate, baixa conf)")
print("   • Ordenação por score prioriza qualidade total, não só probabilidade")
print("   • Odds individuais avaliadas pelo EV; limites de odds aplicam-se ao bilhete")
print("\n   🎯 Meta: probabilidade combinada e EV do bilhete respeitam os limites configurados")
print("="*80 + "\n")
