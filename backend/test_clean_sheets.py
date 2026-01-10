"""
Teste rápido para verificar se as probabilidades de clean sheet estão sendo calculadas
"""

from apps.analysis.services.statistical_models import PoissonBivariateModel

# Inicializar modelo
model = PoissonBivariateModel()

# Teste com força ofensiva real
home_strength = 1.5  # Casa marca 1.5 gols/jogo em média
away_strength = 1.2  # Fora marca 1.2 gols/jogo em média

print("\n" + "="*80)
print("TESTE: Probabilidades de Clean Sheet")
print("="*80)

result = model.predict(home_strength, away_strength, weather_impact=0.0)

print("\n📊 RESULTADO:")
print(f"   Expected Goals - Casa: {result['expected_goals']['home']:.2f}")
print(f"   Expected Goals - Fora: {result['expected_goals']['away']:.2f}")
print(f"\n   Placar mais provável: {result['most_likely_score']}")

print(f"\n📈 PROBABILIDADES:")
probs = result['probabilities']
print(f"   Casa vence: {probs['home_win']*100:.1f}%")
print(f"   Empate: {probs['draw']*100:.1f}%")
print(f"   Fora vence: {probs['away_win']*100:.1f}%")
print(f"\n   Over 2.5: {probs['over_2_5']*100:.1f}%")
print(f"   Under 2.5: {probs['under_2_5']*100:.1f}%")
print(f"   Ambas marcam: {probs['btts']*100:.1f}%")

print(f"\n🛡️  CLEAN SHEETS:")
print(f"   Casa não sofre: {probs.get('home_clean_sheet', 0)*100:.1f}%")
print(f"   Fora não sofre: {probs.get('away_clean_sheet', 0)*100:.1f}%")

print("\n" + "="*80)
print("✅ Teste concluído!")
print("="*80 + "\n")
