"""
Teste de debug: Mapear probabilidades Poisson com odds da API
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.api_football_service import APIFootballService
from apps.analysis.services.statistical_models import PoissonBivariateModel
from apps.matches.models import Match

def main():
    print("\n" + "="*80)
    print("DEBUG: MAPEAMENTO PROBABILIDADES → ODDS")
    print("="*80 + "\n")
    
    # 1. Extrair odds da API
    api = APIFootballService()
    odds = api.fetch_odds(1388503)
    
    print(f"📌 ODDS EXTRAÍDAS DA API ({len(odds)} mercados):")
    print("\nDouble Chance:")
    for key in ['1x', '12', 'x2', '1X', '12', 'X2']:
        if key in odds:
            print(f"  ✅ '{key}': {odds[key]}")
        else:
            print(f"  ❌ '{key}': NÃO ENCONTRADO")
    
    print("\nTeam Totals - Home:")
    for key in ['home_over_1.5', 'home_under_1.5', 'home_over_2.5', 'home_under_2.5']:
        if key in odds:
            print(f"  ✅ '{key}': {odds[key]}")
        else:
            print(f"  ❌ '{key}': NÃO ENCONTRADO")
    
    # 2. Calcular probabilidades Poisson
    print("\n" + "="*80)
    print("📌 PROBABILIDADES CALCULADAS PELO POISSON:")
    print("="*80)
    
    poisson = PoissonBivariateModel()
    prediction = poisson.predict(
        home_strength=2.3,
        away_strength=1.1,
        league_id=78
    )
    probs = prediction['probabilities']
    
    print(f"\nTotal de probabilidades: {len(probs)}")
    print("\nDouble Chance:")
    for key in ['1x', '12', 'x2', '1X', '12', 'X2']:
        if key in probs:
            print(f"  ✅ '{key}': {probs[key]:.1%}")
        else:
            print(f"  ❌ '{key}': NÃO ENCONTRADO")
    
    print("\nTeam Totals - Home:")
    for key in ['home_over_1.5', 'home_under_1.5', 'home_over_2.5', 'home_under_2.5']:
        if key in probs:
            print(f"  ✅ '{key}': {probs[key]:.1%}")
        else:
            print(f"  ❌ '{key}': NÃO ENCONTRADO")
    
    # 3. Verificar correspondência
    print("\n" + "="*80)
    print("📌 VERIFICAÇÃO DE CORRESPONDÊNCIA (Prob ↔ Odd):")
    print("="*80 + "\n")
    
    match_count = 0
    mismatch_count = 0
    
    print("Mercados com MATCH (tem probabilidade E odd):")
    for market, prob in sorted(probs.items()):
        if market in odds:
            match_count += 1
            if match_count <= 10:  # Mostrar primeiros 10
                print(f"  ✅ {market:30s} Prob: {prob:6.1%}  Odd: {odds[market]:5.2f}")
    
    print(f"\n...total: {match_count} mercados com match\n")
    
    print("Mercados com MISMATCH (tem probabilidade MAS sem odd):")
    for market, prob in sorted(probs.items()):
        if market not in odds and prob > 0.5:  # Apenas prob > 50%
            mismatch_count += 1
            print(f"  ❌ {market:30s} Prob: {prob:6.1%}  Odd: AUSENTE")
    
    print(f"\n...total: {mismatch_count} mercados com alta prob mas sem odd")
    
    # 4. Resumo
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)
    print(f"  • Total probabilidades Poisson: {len(probs)}")
    print(f"  • Total odds extraídas API: {len(odds)}")
    print(f"  • Correspondências (prob + odd): {match_count}")
    print(f"  • Sem correspondência (prob alta sem odd): {mismatch_count}")
    print(f"  • Taxa de cobertura: {match_count/len(probs)*100:.1f}%")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
