"""
Validacao apenas do ContextAnalyzer e MarketSelector
Sem chamadas de API - usa dados locais e Poisson
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
    print("VALIDACAO SISTEMA COM CONTEXTUALIZACAO")
    print("Poisson + ContextAnalyzer + MarketSelector")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Buscar partidas finalizadas
    print("Buscando partidas finalizadas...")
    matches = Match.objects.filter(
        Q(status='finished') | Q(status='FT')
    ).exclude(
        home_score__isnull=True
    ).exclude(
        away_score__isnull=True
    ).select_related('home_team', 'away_team', 'league')[:100]
    
    total = matches.count()
    print(f"[OK] {total} partidas\n")
    
    if total == 0:
        print("[ERRO] Nenhuma partida encontrada")
        return
    
    print("Componentes:")
    print("  - PoissonBivariateModel (previsoes base)")
    print("  - ContextAnalyzer (deteccao de padroes)")
    print("  - MarketSelector (selecao contextual)")
    print("-" * 80)
    
    # Inicializar
    poisson = PoissonBivariateModel()
    context_analyzer = ContextAnalyzer()
    market_selector = MarketSelector()
    
    stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'probabilities': []})
    errors = []
    analyzed_count = 0
    
    for idx, match in enumerate(matches, 1):
        print(f"\n[{idx}/{total}] {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name}")
        
        try:
            # 1. Previsao Poisson
            pred = poisson.predict(
                home_strength=1.4,
                away_strength=1.2,
                home_defense=1.1,
                away_defense=1.1,
                weather_impact=0.0,
                league_id=None
            )
            
            probs_base = pred['probabilities']
            
            # 2. Contexto (generico - sem dados externos)
            match_context = {
                'importance': 'medium',
                'rest_context': {'advantage': 'equal'},
                'motivation': {'home': 'medium', 'away': 'medium'},
                'weather': None,
                'standings': {'home_position': 10, 'away_position': 10}
            }
            
            context_result = context_analyzer.analyze(match_context)
            
            # 3. Preparar mercados com probabilidades no formato esperado
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
                'poisson': {
                    'probabilities': probs_base
                }
            }
            
            # 4. Selecao Contextual (VALUE strategy)
            # Fornecer odds ligeiramente favoraveis para simular value bets
            generic_odds = {}
            for market in model_predictions['consensus'].keys():
                prob = model_predictions['consensus'][market]
                if prob > 0:
                    # Odd = 1.08 / probabilidade (8% acima da fair odd)
                    generic_odds[market] = 1.08 / prob
            
            selected = market_selector.select_top_markets(
                context_analysis=context_result,
                model_predictions=model_predictions,
                market_odds=generic_odds,
                strategy='value'
            )
            
            if len(selected) == 0:
                print("            [SKIP] Nenhum mercado selecionado")
                continue
            
            analyzed_count += 1
            
            # 5. Validar top 3 apostas selecionadas
            for bet in selected[:3]:
                market = bet.get('market')
                prob = bet.get('probability', 0)
                context_score = bet.get('context_score', 0)
                
                if not market or prob == 0:
                    continue
                
                # Calcular resultado real
                real = calculate_market_result(match.home_score, match.away_score, market)
                
                if real is None:
                    continue
                
                stats[market]['total'] += 1
                stats[market]['probabilities'].append(prob)
                
                if real:
                    stats[market]['correct'] += 1
                    print(f"            [OK] {market}: ACERTO (prob: {prob*100:.1f}%, ctx: {context_score*100:.0f}%)")
                else:
                    print(f"            [X] {market}: ERRO (prob: {prob*100:.1f}%, ctx: {context_score*100:.0f}%)")
            
        except Exception as e:
            error_msg = f"Match {match.id}: {str(e)[:100]}"
            print(f"            [ERRO] {error_msg}")
            errors.append(error_msg)
            continue
    
    # Resultados
    print("\n" + "="*80)
    print("RESULTADOS - SISTEMA COM CONTEXTUALIZACAO")
    print("="*80)
    
    total_pred = sum(s['total'] for s in stats.values())
    total_correct = sum(s['correct'] for s in stats.values())
    
    if total_pred > 0:
        accuracy = (total_correct / total_pred) * 100
    else:
        accuracy = 0
    
    print(f"\nACURACIA GERAL: {accuracy:.1f}%")
    print(f"Partidas analisadas: {analyzed_count}/{total}")
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
    
    # Salvar
    report = {
        'timestamp': datetime.now().isoformat(),
        'type': 'context_system',
        'components': ['PoissonBivariateModel', 'ContextAnalyzer', 'MarketSelector'],
        'strategy': 'value',
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
    
    fname = f'validation_context_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] {fname}")
    
    # Comparacao
    print("\n" + "="*80)
    print("COMPARACAO")
    print("="*80)
    print(f"Poisson Basico:            45.6%")
    print(f"Poisson + Contexto:        {accuracy:.1f}%")
    
    diff = accuracy - 45.6
    if diff > 0:
        print(f"\nRESULTADO: MELHORIA de +{diff:.1f} pontos percentuais")
        print("Contextualizacao AJUDOU o sistema")
    elif diff < 0:
        print(f"\nRESULTADO: PIORA de {diff:.1f} pontos percentuais")
        print("Contextualizacao PREJUDICOU o sistema")
    else:
        print("\nRESULTADO: SEM DIFERENCA")
    
    print("="*80)


if __name__ == '__main__':
    main()
