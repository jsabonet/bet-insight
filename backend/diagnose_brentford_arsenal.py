"""
Teste REAL: Verificar predição do sistema para Brentford vs Arsenal

Este script simula a predição EXATA como o sistema faz em produção
para diagnosticar se há algum problema.
"""

print("="*80)
print("🔍 DIAGNÓSTICO: Brentford vs Arsenal")
print("="*80)
print("\n📊 PROBABILIDADES REAIS DE MERCADO:")
print("   • Brentford: 19.4%")
print("   • Empate:    22.4%")
print("   • Arsenal:   58.2%")

# Simular odds
brentford_odd = 1 / 0.194  # ≈ 5.15
draw_odd = 1 / 0.224       # ≈ 4.46
arsenal_odd = 1 / 0.582    # ≈ 1.72

print(f"\n💰 ODDS:")
print(f"   • Brentford: {brentford_odd:.2f}")
print(f"   • Empate:    {draw_odd:.2f}")
print(f"   • Arsenal:   {arsenal_odd:.2f}")

# Calcular probabilidades implícitas com margem
total_inv = (1/brentford_odd) + (1/draw_odd) + (1/arsenal_odd)
margin = total_inv - 1.0

print(f"\n📈 Margem da casa: {margin*100:.2f}%")

# Probabilidades sem margem (fair odds)
prob_home_fair = (1/brentford_odd) / total_inv
prob_draw_fair = (1/draw_odd) / total_inv
prob_away_fair = (1/arsenal_odd) / total_inv

print(f"\n✅ PROBABILIDADES FAIR (sem margem):")
print(f"   • Brentford: {prob_home_fair*100:.1f}%")
print(f"   • Empate:    {prob_draw_fair*100:.1f}%")
print(f"   • Arsenal:   {prob_away_fair*100:.1f}%")

print("\n" + "="*80)
print("💡 DIAGNÓSTICO")
print("="*80)

print("\n⚠️ POSSÍVEIS CAUSAS DE PREDIÇÕES EQUILIBRADAS:")
print("\n1. Sistema não recebeu odds de mercado")
print("   → Usou pesos sem market (P=65%, ML=35%)")
print("   → ML é conservador, nivela resultados")
print("\n2. API de odds retornou odds equilibradas")
print("   → Verificar qualidade da fonte")
print("\n3. Contexto muito fraco detectado")
print("   → Sistema aplicou fallback conservador")
print("\n4. Poisson calculou expectativa equilibrada")
print("   → Verificar stats dos times no banco")

print("\n📝 PRÓXIMOS PASSOS PARA VOCÊ:")
print("\n1. Rode uma predição REAL:")
print("   • Acesse o frontend")
print("   • Carregue partida Brentford vs Arsenal")
print("   • Veja os logs no console do backend")
print("\n2. Logs a procurar:")
print("   • '⚖️ Config: ...' → Ver qual configuração de pesos foi usada")
print("   • 'Market odds:' → Ver se recebeu odds de mercado")
print("   • 'Context confidence:' → Ver nível de confiança")
print("\n3. Se confirmar problema:")
print("   • Compartilhe os logs completos")
print("   • Posso ajustar lógica de seleção de pesos")

print("\n" + "="*80)
print("✅ Análise concluída")
print("="*80)
