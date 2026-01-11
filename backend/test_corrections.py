"""
Teste com dados reais da documentação
"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.statistical_models import ModelEnsemble

print("\n" + "="*80)
print("TESTE: Validação de Probabilidades após Correções")
print("="*80)

# Simular 3 cenários típicos
scenarios = [
    {
        'name': 'Favorito em Casa (ex: Man City vs Newcastle)',
        'home_strength': 2.5,
        'away_strength': 1.3,
        'market_odds': {'home_win': 1.35, 'draw': 5.5, 'away_win': 9.0}
    },
    {
        'name': 'Jogo Equilibrado (ex: Arsenal vs Chelsea)',
        'home_strength': 1.8,
        'away_strength': 1.7,
        'market_odds': {'home_win': 2.20, 'draw': 3.4, 'away_win': 3.3}
    },
    {
        'name': 'Favorito Fora (ex: Bournemouth vs Liverpool)',
        'home_strength': 1.1,
        'away_strength': 2.3,
        'market_odds': {'home_win': 5.5, 'draw': 4.2, 'away_win': 1.60}
    }
]

ensemble = ModelEnsemble()
total_error = 0
total_bias_diff = 0

for scenario in scenarios:
    print(f"\n{'-'*80}")
    print(f"Cenário: {scenario['name']}")
    print(f"{'-'*80}")
    
    # Features mínimas
    features = {
        'strength': {
            'home_goals_per_game': scenario['home_strength'],
            'away_goals_per_game': scenario['away_strength']
        },
        'weather': {'goal_impact': 0}
    }
    
    # Executar modelo
    result = ensemble.predict(
        features, 
        scenario['home_strength'], 
        scenario['away_strength'], 
        0
    )
    
    consensus = result['consensus']
    
    print(f"\nMODELO:")
    print(f"  Casa: {consensus['home_win']*100:.1f}%")
    print(f"  Empate: {consensus['draw']*100:.1f}%")
    print(f"  Fora: {consensus['away_win']*100:.1f}%")
    
    # Normalizar odds do mercado
    odds = scenario['market_odds']
    p_h = 1/odds['home_win']
    p_d = 1/odds['draw']
    p_a = 1/odds['away_win']
    total = p_h + p_d + p_a
    
    print(f"\nMERCADO (Normalizado):")
    print(f"  Casa: {(p_h/total)*100:.1f}%")
    print(f"  Empate: {(p_d/total)*100:.1f}%")
    print(f"  Fora: {(p_a/total)*100:.1f}%")
    
    # Calcular erro
    erro = abs(consensus['home_win'] - p_h/total) + \
           abs(consensus['draw'] - p_d/total) + \
           abs(consensus['away_win'] - p_a/total)
    
    print(f"\nERRO: {erro*100:.1f} pontos")
    
    # Viés casa/fora
    vies_modelo = consensus['home_win'] - consensus['away_win']
    vies_mercado = (p_h/total) - (p_a/total)
    diff = vies_modelo - vies_mercado
    
    print(f"\nVIÉS (Casa - Fora):")
    print(f"  Modelo: {vies_modelo*100:+.1f}pp")
    print(f"  Mercado: {vies_mercado*100:+.1f}pp")
    print(f"  Diferença: {diff*100:+.1f}pp")
    
    if abs(diff) < 0.05:
        print("  [OK] APROVADO (<5pp)")
    else:
        print(f"  [!] AJUSTE NECESSARIO ({abs(diff)*100:.1f}pp)")
    
    total_error += erro
    total_bias_diff += abs(diff)

print(f"\n" + "="*80)
print(f"RESULTADO GERAL")
print(f"="*80)
print(f"Erro Médio: {(total_error/len(scenarios))*100:.1f} pontos")
print(f"Diferença de Viés Média: {(total_bias_diff/len(scenarios))*100:.1f}pp")

if (total_bias_diff/len(scenarios)) < 0.05:
    print("\n[OK] SISTEMA APROVADO: Vies controlado!")
else:
    print(f"\n[!] SISTEMA PRECISA AJUSTES: Vies ainda elevado")
