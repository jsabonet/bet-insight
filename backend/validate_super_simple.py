"""
Validacao MUITO Simples - Apenas Poisson direto
Sem ML, sem Features complexas, somente estatisticas basicas
"""

import os
import django
import json
from datetime import datetime
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.statistical_models import PoissonBivariateModel
from django.db.models import Q


def calculate_market_result(home_score, away_score, market):
    """Calcula o resultado real de um mercado."""
    total = home_score + away_score
    
    results = {
        'home_win': home_score > away_score,
        'draw': home_score == away_score,
        'away_win': away_score > home_score,
        'over_2.5': total > 2.5,
        'under_2.5': total < 2.5,
        'over_1.5': total > 1.5,
        'under_1.5': total < 1.5,
        'btts': home_score > 0 and away_score > 0,
    }
    
    return results.get(market)


def main():
    print("="*80)
    print("VALIDACAO SIMPLES - POISSON BASICO")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Buscar partidas
    print("Buscando partidas finalizadas...")
    matches = Match.objects.filter(
        Q(status='finished') | Q(status='FT')
    ).exclude(
        home_score__isnull=True
    ).exclude(
        away_score__isnull=True
    ).select_related('home_team', 'away_team')[:100]
    
    total = matches.count()
    print(f"[OK] {total} partidas\n")
    
    if total == 0:
        print("[ERRO] Nenhuma partida finalizadafound")
        return
    
    print("Analisando...")
    print("-" * 80)
    
    stats = defaultdict(lambda: {'correct': 0, 'total': 0})
    model = PoissonBivariateModel()
    
    for idx, match in enumerate(matches, 1):
        if idx % 10 == 0:
            print(f"[{idx}/{total}] Processando...")
        
        try:
            # Calcular com Poisson
            # Usar forcas genericas pois nao temos stats detalhados
            pred = model.predict(
                home_strength=1.4,
                away_strength=1.2,
                home_defense=1.1,
                away_defense=1.1,
                weather_impact=0.0,
                league_id=None
            )
            
            probs = pred['probabilities']
            
            # Testar principais mercados
            markets_test = {
                'home_win': probs['home_win'],
                'draw': probs['draw'],
                'away_win': probs['away_win'],
                'over_2.5': probs.get('over_2_5', 0),
                'under_2.5': probs.get('under_2_5', 0),
                'btts': probs.get('btts', 0),
            }
            
            for market, prob in markets_test.items():
                if prob > 0.3:  # Soanalisar mercados com prob > 30%
                    real = calculate_market_result(match.home_score, match.away_score, market)
                    
                    if real is not None:
                        stats[market]['total'] += 1
                        if real:
                            stats[market]['correct'] += 1
                            
        except Exception as e:
            continue
    
    # Resultados
    print("\n" + "="*80)
    print("RESULTADOS")
    print("="*80)
    
    total_pred = sum(s['total'] for s in stats.values())
    total_correct = sum(s['correct'] for s in stats.values())
    
    if total_pred > 0:
        accuracy = (total_correct / total_pred) * 100
    else:
        accuracy = 0
    
    print(f"\nACURACIA GERAL: {accuracy:.1f}%")
    print(f"Previsoes: {total_pred}")
    print(f"Acertos: {total_correct}\n")
    
    print("-" * 80)
    print("Por Mercado:")
    print("-" * 80)
    
    for market in sorted(stats.keys()):
        data = stats[market]
        if data['total'] > 0:
            acc = (data['correct'] / data['total']) * 100
            icon = "[++]" if acc >= 55 else "[OK]" if acc >= 45 else "[--]"
            print(f"{icon} {market:12s} | {acc:5.1f}% | {data['total']:3d} previsoes")
    
    # Salvar
    report = {
        'timestamp': datetime.now().isoformat(),
        'accuracy': accuracy,
        'total_predictions': total_pred,
        'total_correct': total_correct,
        'markets': {
            m: {
                'accuracy': (d['correct']/d['total']*100) if d['total'] > 0 else 0,
                'total': d['total'],
                'correct': d['correct']
            }
            for m, d in stats.items()
        }
    }
    
    fname =f'validation_simple_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(fname, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[SAVE] {fname}")
    print("="*80)


if __name__ == '__main__':
    main()
