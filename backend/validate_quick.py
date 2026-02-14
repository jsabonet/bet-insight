"""
Validacao Rapida de Acuracia - SEM APIs externas
Usa apenas modelo Poisson com dados basicos do banco de dados.
"""

import os
import django
import json
from datetime import datetime
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.statistical_models import ModelEnsemble
from django.db.models import Q


def calculate_market_result(home_score, away_score, market):
    """Calcula o resultado real de um mercado baseado no placar."""
    total_goals = home_score + away_score
    
    markets = {
        'home_win': home_score > away_score,
        'draw': home_score == away_score,
        'away_win': away_score > home_score,
        'over_2.5': total_goals > 2.5,
        'under_2.5': total_goals < 2.5,
        'over_1.5': total_goals > 1.5,
        'under_1.5': total_goals <1.5,
        'btts_yes': home_score > 0 and away_score > 0,
        'btts_no': home_score == 0 or away_score == 0,
        '1X': home_score >= away_score,
        'X2': away_score >= home_score,
        '12': home_score != away_score,
    }
    
    return markets.get(market, None)


def validate_simple():
    """Validacao simples usando apenas Poisson."""
    
    print("="*80)
    print("VALIDACAO RAPIDA DE ACURACIA - MODELO POISSON")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Buscar partidas finalizadas
    print("Buscando partidas finalizadas...")
    matches = Match.objects.filter(
        Q(status='finished') | Q(status='FT')
    ).exclude(
        home_score__isnull=True
    ).exclude(
        away_score__isnull=True
    ).select_related('home_team', 'away_team', 'league')[:100]  # 100 partidas para teste rapido
    
    total = matches.count()
    print(f"[OK] {total} partidas encontradas\n")
    print("Iniciando analise...")
    print("-" * 80)
    
    # Estatisticas
    stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'probabilities': []})
    
    for idx, match in enumerate(matches, 1):
        print(f"\n[{idx}/{total}] {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name}")
        
        try:
            # Calcular probabilidades usando Poisson simples
            model = ModelEnsemble()
            
            # Usar forcas basicas (pode ajustar com stats reais se disponivel)
            home_attack = 1.5
            home_defense = 1.0  
            away_attack = 1.3
            away_defense = 1.0
            
            predictions = model.predict(
                home_attack=home_attack,
                home_defense=home_defense,
                away_attack=away_attack,
                away_defense=away_defense,
                market_odds={},
                features={}
            )
            
            consensus = predictions['consensus']
            poisson_probs = predictions['poisson']['probabilities']
            
            # Mercados para testar
            markets_to_test = {
                'home_win': consensus.get('home_win', 0),
                'draw': consensus.get('draw', 0),
                'away_win': consensus.get('away_win', 0),
                'over_2.5': poisson_probs.get('over_2.5', 0),
                'under_2.5': poisson_probs.get('under_2.5', 0),
                'btts_yes': poisson_probs.get('btts', 0),
                'btts_no': 1 - poisson_probs.get('btts', 0),
            }
            
            # Validar cada mercado
            for market, prob in markets_to_test.items():
                if prob == 0:
                    continue
                    
                real_result = calculate_market_result(match.home_score, match.away_score, market)
                
                if real_result is None:
                    continue
                
                stats[market]['total'] += 1
                stats[market]['probabilities'].append(prob)
                
                if real_result:
                    stats[market]['correct'] += 1
                    print(f"           [OK] {market}: ACERTO (prob: {prob*100:.1f}%)")
                else:
                    print(f"           [X] {market}: ERRO (prob: {prob*100:.1f}%)")
                    
        except Exception as e:
            print(f"            [ERRO] {str(e)}")
            continue
    
    # Resultados
    print("\n" + "="*80)
    print("RESULTADOS")
    print("="*80)
    
    total_pred = sum(s['total'] for s in stats.values())
    total_correct = sum(s['correct'] for s in stats.values())
    accuracy = (total_correct / total_pred * 100) if total_pred > 0 else 0
    
    print(f"\nACURACIA GERAL: {accuracy:.2f}%")
    print(f"Total previsoes: {total_pred}")
    print(f"Acertos: {total_correct}")
    print(f"Erros: {total_pred - total_correct}\n")
    
    print("-" * 80)
    print("ACURACIA POR MERCADO:")
    print("-" * 80)
    
    sorted_markets =sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True)
    
    for market, data in sorted_markets:
        if data['total'] == 0:
            continue
        
        acc = (data['correct'] / data['total']) * 100
        avg_prob = sum(data['probabilities']) / len(data['probabilities']) * 100
        
        icon = "[++]" if acc >= 60 else "[OK]" if acc >= 45 else "[--]"
        
        print(f"{icon} {market:15s} | Acuracia: {acc:5.1f}% | Previsoes: {data['total']:3d} | Prob Media: {avg_prob:.1f}%")
    
    # Salvar relatorio
    report = {
        'timestamp': datetime.now().isoformat(),
        'type': 'quick_validation_poisson_only',
        'matches_analyzed': total,
        'total_predictions': total_pred,
        'total_correct': total_correct,
        'overall_accuracy': accuracy,
        'market_stats': {
            market: {
                'accuracy': (data['correct']/data['total']*100) if data['total'] > 0 else 0,
                'total': data['total'],
                'correct': data['correct'],
                'avg_probability': sum(data['probabilities']) / len(data['probabilities']) if data['probabilities'] else 0
            }
            for market, data in stats.items()
        }
    }
    
    filename = f'validation_quick_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n[SAVE] Relatorio: {filename}")
    print("="*80)


if __name__ == '__main__':
    validate_simple()
