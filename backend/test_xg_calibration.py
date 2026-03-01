"""
Testar calibração xG integrada no PoissonBivariateModel
"""
import os
import sys
import django

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.statistical_models import PoissonBivariateModel
from apps.analysis.services.xg_calibrator import get_xg_calibrator

print("=" * 80)
print("TESTE: Calibração xG Integrada")
print("=" * 80)

# Verificar se calibrador está disponível
print("\n🔍 [1] Verificando calibrador...")
calibrator = get_xg_calibrator()
if calibrator.is_available():
    print("✅ Calibrador disponível")
    stats = calibrator.get_improvement_stats()
    if stats:
        print(f"   MAE melhoria: {stats['mae_improvement_pct']:.1f}%")
        print(f"   Treinado com: {stats['n_samples']} observações")
else:
    print("❌ Calibrador não disponível")
    print("   Execute: python train_xg_calibration.py")
    sys.exit(1)

# Testar modelo Poisson com calibração
print("\n⚙️  [2] Testando PoissonBivariateModel...")
model = PoissonBivariateModel()

# Caso de teste: time forte (casa) vs time médio (fora)
print("\n📊 TESTE 1: Time Forte (Casa) vs Time Médio (Fora)")
print("   Força casa: 2.0 gols/jogo")
print("   Força fora: 1.2 gols/jogo")
print("   Liga: Premier League (39)")

result = model.predict(
    home_strength=2.0,
    away_strength=1.2,
    league_id=39
)

print(f"\n✅ Resultado:")
print(f"   xG Casa: {result['expected_goals']['home']:.2f}")
print(f"   xG Fora: {result['expected_goals']['away']:.2f}")
print(f"   Placar provável: {result['most_likely_score']}")
print(f"   Probabilidades:")
print(f"      Casa vence: {result['probabilities']['home_win']*100:.1f}%")
print(f"      Empate: {result['probabilities']['draw']*100:.1f}%")
print(f"      Fora vence: {result['probabilities']['away_win']*100:.1f}%")

# Caso de teste 2: Times equilibrados
print("\n" + "=" * 80)
print("📊 TESTE 2: Times Equilibrados")
print("   Força casa: 1.5 gols/jogo")
print("   Força fora: 1.5 gols/jogo")

result2 = model.predict(
    home_strength=1.5,
    away_strength=1.5,
    league_id=39
)

print(f"\n✅ Resultado:")
print(f"   xG Casa: {result2['expected_goals']['home']:.2f}")
print(f"   xG Fora: {result2['expected_goals']['away']:.2f}")
print(f"   Placar provável: {result2['most_likely_score']}")
print(f"   Probabilidades:")
print(f"      Casa vence: {result2['probabilities']['home_win']*100:.1f}%")
print(f"      Empate: {result2['probabilities']['draw']*100:.1f}%")
print(f"      Fora vence: {result2['probabilities']['away_win']*100:.1f}%")

# Caso de teste 3: Jogos defensivos (Copa)
print("\n" + "=" * 80)
print("📊 TESTE 3: Jogo Defensivo (Copa)")
print("   Força casa: 1.0 gols/jogo")
print("   Força fora: 1.0 gols/jogo")
print("   Ajuste Copa: 0.85 (jogos mais cautelosos)")

result3 = model.predict(
    home_strength=1.0,
    away_strength=1.0,
    knockout_adjustment=0.85,
    league_id=39
)

print(f"\n✅ Resultado:")
print(f"   xG Casa: {result3['expected_goals']['home']:.2f}")
print(f"   xG Fora: {result3['expected_goals']['away']:.2f}")
print(f"   Placar provável: {result3['most_likely_score']}")
print(f"   Probabilidades:")
print(f"      Casa vence: {result3['probabilities']['home_win']*100:.1f}%")
print(f"      Empate: {result3['probabilities']['draw']*100:.1f}%")
print(f"      Fora vence: {result3['probabilities']['away_win']*100:.1f}%")

print("\n" + "=" * 80)
print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
print("=" * 80)

print("\n💡 PRÓXIMOS PASSOS:")
print("   1. Monitorar previsões em partidas reais")
print("   2. Comparar xG previsto vs xG real (se disponível)")
print("   3. Ajustar calibrador periodicamente com novos dados")
print("   4. Exportar métricas de melhoria para dashboard admin")

print("\n" + "=" * 80)
