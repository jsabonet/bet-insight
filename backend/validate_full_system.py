"""
Validacao do Sistema COMPLETO com ContextAnalyzer e MarketSelector
Compara com acuracia do Poisson basico
"""

import os
import django
import json
from datetime import datetime
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
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
    print("VALIDACAO SISTEMA COMPLETO - COM CONTEXTUALIZACAO")
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
    ).select_related('home_team', 'away_team', 'league')[:50]  # 50 partidas
    
    total = matches.count()
    print(f"[OK] {total} partidas\n")
    
    if total == 0:
        print("[ERRO] Nenhuma partida encontrada")
        return
    
    print("Analisando com sistema completo...")
    print("(Isso pode demorar - inclui ML, contexto, etc)")
    print("-" * 80)
    
    stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'probabilities': []})
    orchestrator = HybridAnalysisOrchestrator()
    errors = []
    analyzed_count = 0
    
    for idx, match in enumerate(matches, 1):
        print(f"\n[{idx}/{total}] {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name}")
        
        try:
            # Usar sistema completo com VALUE strategy
            result = orchestrator.run(match, strategy='value')
            
            if not result or 'top_bets' not in result:
                print("            [SKIP] Sem recomendacoes")
                errors.append(f"Match {match.id}: Sem top_bets")
                continue
            
            top_bets = result.get('top_bets', [])
            
            if len(top_bets) == 0:
                print("            [SKIP] Lista vazia")
                errors.append(f"Match {match.id}: top_bets vazio")
                continue
            
            analyzed_count += 1
            
            # Validar cada aposta recomendada
            for bet in top_bets[:3]:  # Top 3 apostas
                market = bet.get('market')
                prob = bet.get('probability', 0)
                
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
                    print(f"            [OK] {market}: ACERTO (prob: {prob*100:.1f}%)")
                else:
                    print(f"            [X] {market}: ERRO (prob: {prob*100:.1f}%)")
            
        except Exception as e:
            error_msg = f"Match {match.id}: {str(e)[:100]}"
            print(f"            [ERRO] {error_msg}")
            errors.append(error_msg)
            continue
    
    # Resultados
    print("\n" + "="*80)
    print("RESULTADOS - SISTEMA COMPLETO")
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
        'type': 'full_system_with_context',
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
        'errors': errors[:20]  # Primeiros 20 erros
    }
    
    fname = f'validation_full_context_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] {fname}")
    
    # Comparacao
    print("\n" + "="*80)
    print("COMPARACAO COM POISSON BASICO")
    print("="*80)
    print(f"Poisson Basico:      45.6%")
    print(f"Sistema Completo:    {accuracy:.1f}%")
    
    diff = accuracy - 45.6
    if diff > 0:
        print(f"MELHORIA: +{diff:.1f} pontos percentuais")
    elif diff < 0:
        print(f"PIORA: {diff:.1f} pontos percentuais")
    else:
        print("IGUAL")
    
    print("="*80)


if __name__ == '__main__':
    main()
