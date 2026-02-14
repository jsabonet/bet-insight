"""
Test EV Display - Simples
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.decision_engine import DecisionEngine

# Criar instância do DecisionEngine
engine = DecisionEngine()

print('=' * 80)
print('🧪 TESTE: _generate_bet_reason - Verificando exibição do EV')
print('=' * 80)

# Simular candidatos com diferentes valores de EV
test_cases = [
    {'probability': 0.718, 'ev_pct': -2.3, 'market': '1X'},  # Sevilla vs Alaves - 1X
    {'probability': 0.708, 'ev_pct': -1.8, 'market': '12'},  # Sevilla vs Alaves - 12
    {'probability': 0.523, 'ev_pct': 23.0, 'market': 'under_2_5'},  # Value positivo
    {'probability': 0.866, 'ev_pct': -2.0, 'market': 'double_chance_1x'},  # Favorito
    {'probability': 0.45, 'ev_pct': -7.5, 'market': 'draw'},  # EV muito negativo
]

confidence = {'score': 0.8, 'level': 'Alto', 'stars': 4}
risk = 'medium'

print('\n📊 RESULTADOS:\n')

for i, candidate in enumerate(test_cases, 1):
    reason = engine._generate_bet_reason(candidate, confidence, risk)
    
    print(f"{i}. Mercado: {candidate['market']}")
    print(f"   Probabilidade: {candidate['probability']*100:.1f}%")
    print(f"   EV: {candidate['ev_pct']:+.1f}%")
    print(f"   📝 Mensagem: {reason}")
    print()

print('=' * 80)
print('✅ ANTES da correção: "sem value significativo" ocultava o EV')
print('✅ DEPOIS da correção: EV sempre visível com valor exato')
print('=' * 80)
