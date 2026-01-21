"""
Análise rápida dos resultados da validação completa
"""
import json
import sys

# Carregar resultados
with open('validation_orchestrator_20260117_014717.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

summary = data['summary']
results = data['detailed_results']

print("\n" + "="*80)
print("RESULTADOS FINAIS - VALIDAÇÃO COM ARQUITETURA COMPLETA")
print("="*80)
print(f"\n📊 MÉTRICAS GERAIS:")
print(f"   Total de partidas: {summary['total_matches']}")
print(f"   Acurácia: {summary['accuracy']:.2f}%")
print(f"   Brier Score: {summary['brier_score']:.4f}")
print(f"   Log Loss: {summary['log_loss']:.4f}")
print(f"   Value Bets encontrados: {summary['value_bets_found']}")

print(f"\n⭐ ACURÁCIA POR CONFIANÇA:")
for conf, stats in sorted(summary['by_confidence'].items()):
    if stats['total'] > 0:
        acc = (stats['correct'] / stats['total']) * 100
        print(f"   {conf} estrelas: {acc:.1f}% ({stats['correct']}/{stats['total']})")

# Análise de resultados reais
home_wins_real = sum(1 for r in results if r['actual'] == [1,0,0])
draws_real = sum(1 for r in results if r['actual'] == [0,1,0])
away_wins_real = sum(1 for r in results if r['actual'] == [0,0,1])

print(f"\n🎯 RESULTADOS REAIS:")
print(f"   Casa: {home_wins_real} ({home_wins_real/len(results)*100:.1f}%)")
print(f"   Empate: {draws_real} ({draws_real/len(results)*100:.1f}%)")
print(f"   Fora: {away_wins_real} ({away_wins_real/len(results)*100:.1f}%)")

# Análise de previsões
home_pred = sum(1 for r in results if r['predicted'] == 'home')
draw_pred = sum(1 for r in results if r['predicted'] == 'draw')
away_pred = sum(1 for r in results if r['predicted'] == 'away')

print(f"\n🤖 PREVISÕES DO MODELO:")
print(f"   Casa: {home_pred} ({home_pred/len(results)*100:.1f}%)")
print(f"   Empate: {draw_pred} ({draw_pred/len(results)*100:.1f}%)")
print(f"   Fora: {away_pred} ({away_pred/len(results)*100:.1f}%)")

# Viés
print(f"\n📈 ANÁLISE DE VIÉS (Modelo - Real):")
print(f"   Casa: {(home_pred/len(results) - home_wins_real/len(results))*100:+.1f} pontos")
print(f"   Empate: {(draw_pred/len(results) - draws_real/len(results))*100:+.1f} pontos")
print(f"   Fora: {(away_pred/len(results) - away_wins_real/len(results))*100:+.1f} pontos")

# Acurácia por tipo de resultado
home_correct = sum(1 for r in results if r['actual'] == [1,0,0] and r['correct'])
draw_correct = sum(1 for r in results if r['actual'] == [0,1,0] and r['correct'])
away_correct = sum(1 for r in results if r['actual'] == [0,0,1] and r['correct'])

print(f"\n✅ ACURÁCIA POR TIPO DE RESULTADO:")
if home_wins_real > 0:
    print(f"   Vitória Casa: {home_correct/home_wins_real*100:.1f}% ({home_correct}/{home_wins_real})")
if draws_real > 0:
    print(f"   Empate: {draw_correct/draws_real*100:.1f}% ({draw_correct}/{draws_real})")
if away_wins_real > 0:
    print(f"   Vitória Fora: {away_correct/away_wins_real*100:.1f}% ({away_correct}/{away_wins_real})")

# Acurácia por tipo de previsão
home_pred_correct = sum(1 for r in results if r['predicted'] == 'home' and r['correct'])
draw_pred_correct = sum(1 for r in results if r['predicted'] == 'draw' and r['correct'])
away_pred_correct = sum(1 for r in results if r['predicted'] == 'away' and r['correct'])

print(f"\n🎲 ACURÁCIA POR TIPO DE PREVISÃO:")
if home_pred > 0:
    print(f"   Quando prevê Casa: {home_pred_correct/home_pred*100:.1f}% ({home_pred_correct}/{home_pred})")
if draw_pred > 0:
    print(f"   Quando prevê Empate: {draw_pred_correct/draw_pred*100:.1f}% ({draw_pred_correct}/{draw_pred})")
if away_pred > 0:
    print(f"   Quando prevê Fora: {away_pred_correct/away_pred*100:.1f}% ({away_pred_correct}/{away_pred})")

print(f"\n" + "="*80)
print("CONCLUSÃO")
print("="*80)

if summary['accuracy'] >= 50:
    print("✅ SISTEMA PRONTO PARA COMERCIALIZAÇÃO!")
    print(f"   Acurácia de {summary['accuracy']:.1f}% está acima do mínimo (50%)")
elif summary['accuracy'] >= 45:
    print("⚠️ SISTEMA PRÓXIMO DO IDEAL")
    print(f"   Acurácia de {summary['accuracy']:.1f}% está próxima do mínimo (50%)")
    print("   Recomenda-se ajustes finos antes do lançamento")
else:
    print("❌ SISTEMA PRECISA MELHORIAS")
    print(f"   Acurácia de {summary['accuracy']:.1f}% está abaixo do mínimo (45%)")
    print("   Necessário ajustar pesos e thresholds")

print(f"\n📊 Brier Score: {summary['brier_score']:.4f} {'✅ Excelente' if summary['brier_score'] < 0.22 else '✅ Bom' if summary['brier_score'] < 0.25 else '⚠️ Médio'}")
print(f"📊 Log Loss: {summary['log_loss']:.4f} {'✅ Bom' if summary['log_loss'] < 1.0 else '⚠️ Médio' if summary['log_loss'] < 1.2 else '❌ Alto (overconfident)'}")
print("="*80 + "\n")
