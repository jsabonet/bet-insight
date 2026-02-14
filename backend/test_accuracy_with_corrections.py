"""
Teste de acurácia com partidas reais finalizadas
Usa as correções aplicadas em market_selector.py e context_analyzer.py
"""
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import json
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

print('\n' + '='*80)
print('🎯 TESTE DE ACURÁCIA - COM CORREÇÕES APLICADAS')
print('='*80)
print('📊 Testando thresholds corrigidos:')
print('   • Value: min_probability 45% (antes: 28%)')
print('   • Multiple: min_probability 55% (antes: 40%)')
print('   • Pesos dos padrões reduzidos em 15-25%')
print('='*80)

# Carregar partidas finalizadas
with open('finished_matches_for_testing.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

orchestrator = HybridAnalysisOrchestrator()

# Estatísticas
total_processed = 0
predictions_made = 0
correct_predictions = 0
no_predictions = 0
errors = 0

results = []

for i, match_data in enumerate(matches, 1):
    print(f'\n[{i}/{len(matches)}] {match_data["home_team"]} vs {match_data["away_team"]}')
    print(f'   Liga: {match_data["league"]}')
    print(f'   Resultado: {match_data["home_score"]}-{match_data["away_score"]}', end='')
    
    # Determinar resultado
    if match_data['home_score'] > match_data['away_score']:
        actual_result = 'home_win'
        print(' (Vitória Casa)')
    elif match_data['away_score'] > match_data['home_score']:
        actual_result = 'away_win'
        print(' (Vitória Fora)')
    else:
        actual_result = 'draw'
        print(' (Empate)')
    
    try:
        # Executar análise COM AS CORREÇÕES
        analysis = orchestrator.execute(
            fixture_id=match_data['fixture_id'],
            strategy='value'  # Testar com strategy value
        )
        
        total_processed += 1
        
        if analysis.get('success'):
            # Verificar se há mercados recomendados
            top_markets = analysis.get('decision', {}).get('top_markets', [])
            
            if top_markets and len(top_markets) > 0:
                # Pegar predição de 1X2 baseada nas probabilidades
                consensus = analysis.get('probabilities', {}).get('consensus', {})
                
                if consensus:
                    home_prob = consensus.get('home_win', 0)
                    draw_prob = consensus.get('draw', 0)
                    away_prob = consensus.get('away_win', 0)
                    
                    # Predição = maior probabilidade
                    max_prob = max(home_prob, draw_prob, away_prob)
                    
                    if home_prob == max_prob:
                        predicted_result = 'home_win'
                    elif draw_prob == max_prob:
                        predicted_result = 'draw'
                    else:
                        predicted_result = 'away_win'
                    
                    predictions_made += 1
                    
                    # Verificar se acertou
                    is_correct = (predicted_result == actual_result)
                    
                    if is_correct:
                        correct_predictions += 1
                        print(f'   ✅ ACERTOU! Previu: {predicted_result} ({max_prob:.1%})')
                    else:
                        print(f'   ❌ ERROU! Previu: {predicted_result} ({max_prob:.1%}), Era: {actual_result}')
                    
                    # Mostrar mercados recomendados
                    print(f'   📊 Top markets ({len(top_markets)}):')
                    for market in top_markets[:2]:
                        print(f'      • {market.get("market_display", "N/A")}: {market.get("probability", 0):.1%} (odd: {market.get("market_odd", "N/A")})')
                    
                    results.append({
                        'match': f'{match_data["home_team"]} vs {match_data["away_team"]}',
                        'actual': actual_result,
                        'predicted': predicted_result,
                        'correct': is_correct,
                        'max_prob': max_prob,
                        'markets_count': len(top_markets)
                    })
                else:
                    no_predictions += 1
                    print(f'   ⚠️ Sem probabilidades consensus')
            else:
                no_predictions += 1
                print(f'   ⚠️ Nenhum mercado recomendado (thresholds muito altos = BOM!)')
        else:
            errors += 1
            print(f'   ❌ Erro na análise: {analysis.get("error")}')
            
    except Exception as e:
        errors += 1
        print(f'   ❌ Exceção: {str(e)[:100]}')

# Resultados finais
print('\n' + '='*80)
print('📊 RESULTADOS FINAIS')
print('='*80)
print(f'Total processado: {total_processed}')
print(f'Previsões feitas: {predictions_made}')
print(f'Sem previsão (thresholds altos): {no_predictions}')
print(f'Erros: {errors}')

if predictions_made > 0:
    accuracy = (correct_predictions / predictions_made) * 100
    print(f'\n🎯 ACURÁCIA: {correct_predictions}/{predictions_made} = {accuracy:.1f}%')
    
    if accuracy >= 55:
        print('\n✅ EXCELENTE! Acurácia >= 55% (meta atingida)')
    elif accuracy >= 50:
        print('\n🟡 BOM! Acurácia >= 50% (perto da meta)')
    else:
        print('\n❌ BAIXO! Acurácia < 50% (precisa ajustar)')
else:
    print('\n⚠️ Nenhuma previsão foi feita')
    print('   Isso pode significar que os thresholds estão muito altos')
    print('   ou que as partidas não tinham dados suficientes')

print('='*80 + '\n')

# Salvar resultados
with open('accuracy_test_results.json', 'w', encoding='utf-8') as f:
    json.dump({
        'total_processed': total_processed,
        'predictions_made': predictions_made,
        'correct_predictions': correct_predictions,
        'no_predictions': no_predictions,
        'errors': errors,
        'accuracy': (correct_predictions / predictions_made * 100) if predictions_made > 0 else 0,
        'details': results
    }, f, indent=2, ensure_ascii=False)

print('💾 Resultados salvos em: accuracy_test_results.json\n')
