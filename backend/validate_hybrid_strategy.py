"""
Validacao da Estrategia Hibrida
Usa contexto SÓ quando realmente forte, caso contrario usa Poisson
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
from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.analysis.services.market_selector import MarketSelector
from apps.analysis.services.hybrid_strategy import HybridStrategy
from django.db.models import Q


def calculate_market_result(home_score, away_score, market):
    """Calcula o resultado real baseado no placar."""
    total = home_score + away_score
    
    results = {
        'home_win': home_score > away_score,
        'draw': home_score == away_score,
        'away_win': away_score > home_score,
        'over_2.5': total > 2.5,
        'under_2.5': total < 2.5,
        'over_1.5': total > 1.5,
        'under_1.5': total < 1.5,
        'btts_yes': home_score > 0 and away_score > 0,
        'btts_no': home_score == 0 or away_score == 0,
        '1X': home_score >= away_score,
        'X2': away_score >= home_score,
        '12': home_score != away_score,
    }
    
    return results.get(market)


def main():
    print("="*80)
    print("VALIDACAO ESTRATEGIA HIBRIDA")
    print("Contexto SÓ quando forte, caso contrario Poisson")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Buscar partidas
    matches = Match.objects.filter(
        Q(status='finished') | Q(status='FT')
    ).exclude(
        home_score__isnull=True
    ).exclude(
        away_score__isnull=True
    ).select_related('home_team', 'away_team', 'league')[:100]
    
    total = matches.count()
    print(f"[OK] {total} partidas\n")
    
    # Inicializar
    poisson = PoissonBivariateModel()
    context_analyzer = ContextAnalyzer()
    market_selector = MarketSelector()
    hybrid_strategy = HybridStrategy()
    
    stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'probabilities': []})
    errors = []
    analyzed_count = 0
    context_used_count = 0
    
    print("Estrategia: Usar contexto SÓ se confianca >= 90% E dados reais")
    print("-" * 80)
    
    for idx, match in enumerate(matches, 1):
        print(f"\n[{idx}/{total}] {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name}")
        
        try:
            # 1. Previsao Poisson base
            pred = poisson.predict(
                home_strength=1.4,
                away_strength=1.2,
                home_defense=1.1,
                away_defense=1.1,
                weather_impact=0.0,
                league_id=None
            )
            
            probs_base = pred['probabilities']
            
            # 2. Contexto (generico)
            match_context = {
                'importance': 'medium',
                'rest_context': {'advantage': 'equal'},
                'motivation': {'home': 'medium', 'away': 'medium'},
                'weather': None,
                'standings': {'home_position': 10, 'away_position': 10}
            }
            
            context_result = context_analyzer.analyze(match_context)
            
            # 3. DECISAO HIBRIDA - usar contexto ou nao?
            decision = hybrid_strategy.should_use_context(context_result, match_context)
            
            # 4. Selecionar mercados com base na decisao
            if decision['use_context']:
                # Usar contextualizacao
                context_used_count += 1
                
                model_predictions = {
                    'consensus': {
                        'home_win': probs_base.get('home_win', 0),
                        'draw': probs_base.get('draw', 0),
                        'away_win': probs_base.get('away_win', 0),
                        'over_2.5': probs_base.get('over_2_5', 0),
                        'under_2.5': probs_base.get('under_2_5', 0),
                        'over_1.5': probs_base.get('over_1_5', 0),
                        'btts_yes': probs_base.get('btts', 0),
                        'btts_no': 1 - probs_base.get('btts', 0),
                    },
                    'poisson': {'probabilities': probs_base}
                }
                
                generic_odds = {}
                for market in model_predictions['consensus'].keys():
                    prob = model_predictions['consensus'][market]
                    if prob > 0:
                        generic_odds[market] = 1.08 / prob
                
                selected = market_selector.select_top_markets(
                    context_analysis=context_result,
                    model_predictions=model_predictions,
                    market_odds=generic_odds,
                    strategy='value'
                )
            else:
                # Usar Poisson puro - selecionar top 3 mercados por probabilidade
                markets_ranked = sorted(
                    [
                        ('home_win', probs_base.get('home_win', 0)),
                        ('draw', probs_base.get('draw', 0)),
                        ('away_win', probs_base.get('away_win', 0)),
                        ('over_2.5', probs_base.get('over_2_5', 0)),
                        ('under_2.5', probs_base.get('under_2_5', 0)),
                        ('btts', probs_base.get('btts', 0)),
                    ],
                    key=lambda x: x[1],
                    reverse=True
                )[:3]  # Top 3
                
                # Filtrar apenas prob > 30%
                selected = [
                    {'market': m, 'probability': p, 'context_score': 0}
                    for m, p in markets_ranked
                    if p > 0.30
                ]
            
            if len(selected) == 0:
                print("            [SKIP] Nenhum mercado selecionado")
                continue
            
            analyzed_count += 1
            
            # 5. Validar apostas
            for bet in selected[:3]:
                market = bet.get('market')
                prob = bet.get('probability', 0)
                context_score = bet.get('context_score', 0)
                
                if not market or prob == 0:
                    continue
                
                # Normalizar nome do mercado se necessario
                if market == 'btts':
                    market = 'btts_yes'
                
                real = calculate_market_result(match.home_score, match.away_score, market)
                
                if real is None:
                    continue
                
                stats[market]['total'] += 1
                stats[market]['probabilities'].append(prob)
                
                method = "CTX" if decision['use_context'] else "BASE"
                
                if real:
                    stats[market]['correct'] += 1
                    print(f"            [OK] {market}: ACERTO (prob: {prob*100:.1f}%, {method})")
                else:
                    print(f"            [X] {market}: ERRO (prob: {prob*100:.1f}%, {method})")
            
        except Exception as e:
            error_msg = f"Match {match.id}: {str(e)[:100]}"
            print(f"            [ERRO] {error_msg}")
            errors.append(error_msg)
            continue
    
    # Resultados
    print("\n" + "="*80)
    print("RESULTADOS - ESTRATEGIA HIBRIDA")
    print("="*80)
    
    total_pred = sum(s['total'] for s in stats.values())
    total_correct = sum(s['correct'] for s in stats.values())
    
    if total_pred > 0:
        accuracy = (total_correct / total_pred) * 100
    else:
        accuracy = 0
    
    print(f"\nACURACIA GERAL: {accuracy:.1f}%")
    print(f"Partidas analisadas: {analyzed_count}/{total}")
    print(f"Contexto usado: {context_used_count}/{analyzed_count} ({context_used_count/analyzed_count*100:.1f}%)")
    print(f"Total previsoes: {total_pred}")
    print(f"Acertos: {total_correct}")
    print(f"Erros: {total_pred - total_correct}\n")
    
    print("-" * 80)
    print("Por Mercado:")
    print("-" * 80)
    
    sorted_markets = sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True)
    
    for market, data in sorted_markets:
        if data['total'] == 0:
            continue
        
        acc = (data['correct'] / data['total']) * 100
        avg_prob = sum(data['probabilities']) / len(data['probabilities']) * 100
        
        icon = "[++]" if acc >= 55 else "[OK]" if acc >= 45 else "[--]"
        
        print(f"{icon} {market:15s} | {acc:5.1f}% | {data['total']:3d} prev | Prob Media: {avg_prob:.1f}%")
    
    # Estatisticas da estrategia
    strategy_stats = hybrid_strategy.get_stats()
    
    print("\n" + "="*80)
    print("ESTATISTICAS DA ESTRATEGIA")
    print("="*80)
    print(f"Total decisoes: {strategy_stats['total_decisions']}")
    print(f"Usou contexto: {strategy_stats['used_context']} ({strategy_stats['context_percentage']:.1f}%)")
    print(f"Usou base (Poisson): {strategy_stats['used_base']} ({100-strategy_stats['context_percentage']:.1f}%)")
    
    # Salvar
    report = {
        'timestamp': datetime.now().isoformat(),
        'type': 'hybrid_strategy',
        'strategy_stats': strategy_stats,
        'matches_total': total,
        'matches_analyzed': analyzed_count,
        'accuracy': accuracy,
        'total_predictions': total_pred,
        'total_correct': total_correct,
        'markets': {
            m: {
                'accuracy': (d['correct']/d['total']*100) if d['total'] > 0 else 0,
                'total': d['total'],
                'correct': d['correct'],
                'avg_probability': sum(d['probabilities']) / len(d['probabilities']) if d['probabilities'] else 0
            }
            for m, d in stats.items()
        },
        'errors': errors[:20]
    }
    
    fname = f'validation_hybrid_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] {fname}")
    
    # Comparacao
    print("\n" + "="*80)
    print("COMPARACAO FINAL")
    print("="*80)
    print(f"Poisson Basico:           45.6%")
    print(f"Poisson + Contexto:       43.5%")
    print(f"HIBRIDA (adaptativa):     {accuracy:.1f}%")
    
    diff_vs_base = accuracy - 45.6
    diff_vs_context = accuracy - 43.5
    
    print(f"\nvs Baseline: {'+' if diff_vs_base > 0 else ''}{diff_vs_base:.1f} pontos")
    print(f"vs Contexto: {'+' if diff_vs_context > 0 else ''}{diff_vs_context:.1f} pontos")
    
    if accuracy >= 45.6:
        print("\n[OK] HIBRIDA igual ou melhor que baseline!")
    else:
        print(f"\n[WARN] HIBRIDA {45.6-accuracy:.1f} pontos abaixo do baseline")
    
    print("="*80)


if __name__ == '__main__':
    main()
