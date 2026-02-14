"""
Script de Validação de Acurácia - APENAS DADOS LOCAIS
Avalia a performance do sistema de análise usando partidas já finalizadas no banco de dados.
NÃO usa API externa - apenas dados já salvos localmente.
"""

import os
import django
import json
from datetime import datetime
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from django.db.models import Q


def calculate_market_result(home_score, away_score, market):
    """Calcula o resultado real de um mercado baseado no placar."""
    total_goals = home_score + away_score
    
    markets_results = {
        # 1X2
        'home_win': home_score > away_score,
        'draw': home_score == away_score,
        'away_win': away_score > home_score,
        
        # Over/Under
        'over_0.5': total_goals > 0.5,
        'under_0.5': total_goals < 0.5,
        'over_1.5': total_goals > 1.5,
        'under_1.5': total_goals < 1.5,
        'over_2.5': total_goals > 2.5,
        'under_2.5': total_goals < 2.5,
        'over_3.5': total_goals > 3.5,
        'under_3.5': total_goals < 3.5,
        'over_4.5': total_goals > 4.5,
        'under_4.5': total_goals < 4.5,
        
        # BTTS
        'btts_yes': home_score > 0 and away_score > 0,
        'btts_no': home_score == 0 or away_score == 0,
        
        # Double Chance
        '1X': home_score >= away_score,
        'X2': away_score >= home_score,
        '12': home_score != away_score,
        
        # Clean Sheets
        'home_clean_sheet': away_score == 0,
        'away_clean_sheet': home_score == 0,
        
        # Team Totals
        'home_over_0.5': home_score > 0.5,
        'home_over_1.5': home_score > 1.5,
        'home_over_2.5': home_score > 2.5,
        'away_over_0.5': away_score > 0.5,
        'away_over_1.5': away_score > 1.5,
        'away_over_2.5': away_score > 2.5,
        
        # Margins
        'home_win_by_1': (home_score - away_score) == 1,
        'home_win_by_2plus': (home_score - away_score) >= 2,
        'away_win_by_1': (away_score - home_score) == 1,
        'away_win_by_2plus': (away_score - home_score) >= 2,
        
        # Odd/Even
        'odd_goals': total_goals % 2 == 1,
        'even_goals': total_goals % 2 == 0,
    }
    
    return markets_results.get(market, None)


def validate_local_data():
    """Valida acurácia usando APENAS dados locais - sem chamar API."""
    
    print("="*80)
    print("VALIDACAO DE ACURACIA - DADOS LOCAIS")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Buscar partidas finalizadas COM placar salvo localmente
    print("Buscando partidas finalizadas no banco de dados local...")
    finished_matches = Match.objects.filter(
        Q(status='finished') | Q(status='FT')
    ).exclude(
        home_score__isnull=True
    ).exclude(
        away_score__isnull=True
    ).select_related('home_team', 'away_team', 'league').order_by('-match_date')[:50]  # TESTE RAPIDO: 50 partidas
    
    total_matches = finished_matches.count()
    print(f"[OK] {total_matches} partidas encontradas com resultados salvos localmente")
    print()
    
    if total_matches == 0:
        print("[ERRO] Nao ha partidas finalizadas com placar no banco de dados.")
        print("[DICA] Execute primeiro o comando de sincronizacao para baixar resultados.")
        return
    
    # Estatísticas
    market_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'predictions': []})
    total_predictions = 0
    total_correct = 0
    errors_log = []
    
    print("Iniciando validacao (usando dados ja salvos - SEM chamadas de API)...")
    print("-" * 80)
    
    for idx, match in enumerate(finished_matches, 1):
        try:
            print(f"\n[{idx}/{total_matches}] {match.home_team.name} {match.home_score}-{match.away_score} {match.away_team.name}")
            print(f"            Data: {match.match_date} | Liga: {match.league.name}")
            
            # IMPORTANTE: Usar dados JÁ SALVOS, não buscar da API
            # Simular análise com dados locais
            from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
            
            orchestrator = HybridAnalysisOrchestrator()
            
            # Executar análise (vai usar cache/dados locais quando disponível)
            try:
                result = orchestrator.run(match, strategy='value')
                
                if not result or 'top_bets' not in result:
                    print("            [WARN] Sem recomendacoes geradas")
                    continue
                
                top_bets = result['top_bets']
                
                # Validar cada aposta recomendada
                for bet in top_bets[:3]:  # Top 3 apostas
                    market = bet.get('market')
                    probability = bet.get('probability', 0)
                    
                    if not market:
                        continue
                    
                    # Calcular resultado real
                    real_result = calculate_market_result(
                        match.home_score,
                        match.away_score,
                        market
                    )
                    
                    if real_result is None:
                        continue
                    
                    # Registrar estatística
                    market_stats[market]['total'] += 1
                    market_stats[market]['predictions'].append({
                        'probability': probability,
                        'correct': real_result
                    })
                    
                    total_predictions += 1
                    
                    if real_result:
                        market_stats[market]['correct'] += 1
                        total_correct += 1
                        print(f"            [OK] {market}: ACERTOU (prob: {probability*100:.1f}%)")
                    else:
                        print(f"            [X] {market}: ERROU (prob: {probability*100:.1f}%)")
                
            except Exception as e:
                error_msg = f"Erro ao analisar partida {match.id}: {str(e)}"
                print(f"            [WARN] {error_msg}")
                errors_log.append(error_msg)
                continue
                
        except Exception as e:
            error_msg = f"Erro ao processar partida {match.id}: {str(e)}"
            print(f"[WARN] {error_msg}")
            errors_log.append(error_msg)
            continue
    
    # Resultados finais
    print("\n" + "="*80)
    print("RESULTADOS DA VALIDACAO")
    print("="*80)
    print(f"\nACURACIA GERAL: {(total_correct/total_predictions*100) if total_predictions > 0 else 0:.2f}%")
    print(f"   Total de previsoes: {total_predictions}")
    print(f"   Acertos: {total_correct}")
    print(f"   Erros: {total_predictions - total_correct}")
    
    print("\n" + "-"*80)
    print("ACURACIA POR MERCADO:")
    print("-"*80)
    
    # Ordenar por número de previsões
    sorted_markets = sorted(
        market_stats.items(),
        key=lambda x: x[1]['total'],
        reverse=True
    )
    
    for market, stats in sorted_markets:
        if stats['total'] == 0:
            continue
        
        accuracy = (stats['correct'] / stats['total']) * 100
        avg_prob = sum(p['probability'] for p in stats['predictions']) / len(stats['predictions']) * 100
        
        # Icone baseado na acuracia
        if accuracy >= 70:
            icon = "[++]"
        elif accuracy >= 50:
            icon = "[OK]"
        else:
            icon = "[--]"
        
        print(f"{icon} {market:20s} | Acuracia: {accuracy:5.1f}% | Previsoes: {stats['total']:3d} | Prob Media: {avg_prob:5.1f}%")
    
    # Salvar relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_matches_analyzed': total_matches,
        'total_predictions': total_predictions,
        'total_correct': total_correct,
        'overall_accuracy': (total_correct/total_predictions*100) if total_predictions > 0 else 0,
        'market_stats': {
            market: {
                'accuracy': (stats['correct']/stats['total']*100) if stats['total'] > 0 else 0,
                'total': stats['total'],
                'correct': stats['correct'],
                'avg_probability': sum(p['probability'] for p in stats['predictions']) / len(stats['predictions']) if stats['predictions'] else 0
            }
            for market, stats in market_stats.items()
        },
        'errors': errors_log
    }
    
    filename = f'validation_local_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] Relatorio salvo em: {filename}")
    print("\n" + "="*80)
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)


if __name__ == '__main__':
    validate_local_data()
