import sys
print(f"Python: {sys.executable}")
print(f"Versão: {sys.version}")
print(f"Path[0]: {sys.path[0]}")
print("")

# Importar e mostrar valores
from apps.analysis.config.analysis_config import EnsembleWeights
print("✅ EnsembleWeights importado de:")
print(f"   {EnsembleWeights.__module__}")
print("")
print("📊 Valores carregados:")
print(f"   DEFAULT_WITH_MARKET poisson: {EnsembleWeights.DEFAULT_WITH_MARKET['poisson']}")
print(f"   CLEAR_FAVORITE poisson: {EnsembleWeights.CLEAR_FAVORITE['poisson']}")
print("")

if EnsembleWeights.DEFAULT_WITH_MARKET['poisson'] == 0.60:
    print("✅ CÓDIGO NOVO CARREGADO!")
elif EnsembleWeights.DEFAULT_WITH_MARKET['poisson'] == 0.40:
    print("❌ CÓDIGO ANTIGO CARREGADO!")
else:
    print(f"⚠️ Valor inesperado: {EnsembleWeights.DEFAULT_WITH_MARKET['poisson']}")
