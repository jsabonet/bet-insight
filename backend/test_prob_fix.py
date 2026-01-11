"""
Test simple: Compara probabilidades calculadas antes e depois das correções
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.statistical_models import ModelEnsemble


print("\n" + "="*80)
print("TESTE RAPIDO: Probabilidades Antes vs Depois das Correcoes")
print("="*80)

# Criar modelo
model = ModelEnsemble()

# Features mínimas necessárias
features = {
    'strength_diff': 0.0,
    'form_diff': 0.0,
    'rest_advantage': 0,
    'motivation_diff': 0.0,
    'injury_diff': 0.0,
    'importance': {'match_importance': 5.0},
    'h2h_advantage': 0.0
}

# Cenário 1: Jogo equilibrado (Mallorca vs Rayo)
print("\nCENARIO 1: Jogo Equilibrado (1.2 vs 1.3 gols/jogo)")
print("-" * 80)
result = model.predict(
    home_strength=1.2,
    away_strength=1.3,
    features=features,
    weather_impact=0.0
)

print(f"Probabilidades:")
print(f"  Casa:   {result['consensus']['home_win']*100:.1f}%")
print(f"  Empate: {result['consensus']['draw']*100:.1f}%")
print(f"  Fora:   {result['consensus']['away_win']*100:.1f}%")

total = (result['consensus']['home_win'] + 
         result['consensus']['draw'] + 
         result['consensus']['away_win'])
print(f"\nSoma total: {total:.6f} (deve ser 1.000000)")

vies_casa = result['consensus']['home_win'] - result['consensus']['away_win']
print(f"Vies Casa vs Fora: {vies_casa*100:+.1f} pontos")

# Comparar com mercado
print(f"\nMercado Real: Casa 40.2% | Empate 27.6% | Fora 32.2%")
erro = (abs(result['consensus']['home_win'] - 0.402) +
        abs(result['consensus']['draw'] - 0.276) +
        abs(result['consensus']['away_win'] - 0.322))
print(f"Erro vs Mercado: {erro*100:.1f} pontos percentuais")

# Cenário 2: Favorito casa (Barcelona vs Getafe)
print("\n" + "="*80)
print("CENARIO 2: Favorito Casa (2.1 vs 0.9 gols/jogo)")
print("-" * 80)

features2 = {**features, 'strength_diff': 1.2}  # Casa muito mais forte
result2 = model.predict(
    home_strength=2.1,
    away_strength=0.9,
    features=features2,
    weather_impact=0.0
)

print(f"Probabilidades:")
print(f"  Casa:   {result2['consensus']['home_win']*100:.1f}%")
print(f"  Empate: {result2['consensus']['draw']*100:.1f}%")
print(f"  Fora:   {result2['consensus']['away_win']*100:.1f}%")

total2 = (result2['consensus']['home_win'] + 
          result2['consensus']['draw'] + 
          result2['consensus']['away_win'])
print(f"\nSoma total: {total2:.6f}")

print(f"\nMercado Real: Casa 72.4% | Empate 17.1% | Fora 10.5%")
erro2 = (abs(result2['consensus']['home_win'] - 0.724) +
         abs(result2['consensus']['draw'] - 0.171) +
         abs(result2['consensus']['away_win'] - 0.105))
print(f"Erro vs Mercado: {erro2*100:.1f} pontos percentuais")

# Cenário 3: Favorito fora (Getafe vs Barcelona)
print("\n" + "="*80)
print("CENARIO 3: Favorito Fora (0.9 vs 2.1 gols/jogo)")
print("-" * 80)

features3 = {**features, 'strength_diff': -1.2}  # Fora muito mais forte
result3 = model.predict(
    home_strength=0.9,
    away_strength=2.1,
    features=features3,
    weather_impact=0.0
)

print(f"Probabilidades:")
print(f"  Casa:   {result3['consensus']['home_win']*100:.1f}%")
print(f"  Empate: {result3['consensus']['draw']*100:.1f}%")
print(f"  Fora:   {result3['consensus']['away_win']*100:.1f}%")

total3 = (result3['consensus']['home_win'] + 
          result3['consensus']['draw'] + 
          result3['consensus']['away_win'])
print(f"\nSoma total: {total3:.6f}")

print(f"\nMercado Real: Casa 17.7% | Empate 23.2% | Fora 59.1%")
erro3 = (abs(result3['consensus']['home_win'] - 0.177) +
         abs(result3['consensus']['draw'] - 0.232) +
         abs(result3['consensus']['away_win'] - 0.591))
print(f"Erro vs Mercado: {erro3*100:.1f} pontos percentuais")

# RESUMO
print("\n" + "="*80)
print("RESUMO")
print("="*80)
erro_medio = (erro + erro2 + erro3) / 3
print(f"\nErro medio (3 cenarios): {erro_medio*100:.1f} pontos percentuais")

print(f"\nCORRECOES APLICADAS:")
print(f"  1. Removida dupla contagem de home advantage no Logistico")
print(f"  2. Adicionada normalizacao do consensus (soma = 1.0)")
print(f"  3. Validacao de odds justas (1.01 a 500.0)")

if erro_medio < 0.06:
    print(f"\n  => APROVADO: Erro medio < 6% (alinhado com mercado)")
else:
    print(f"\n  => PRECISA AJUSTE: Erro medio >= 6%")

print("="*80 + "\n")
