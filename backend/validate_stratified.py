"""
Validação Estratificada do Modelo ML por Liga
Testa acurácia em cada competição separadamente para identificar
pontos fortes e fracos do sistema de predição
"""
import os
import sys
import django
from datetime import datetime
from collections import defaultdict

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

# Configuração das ligas para validação
LEAGUES_TO_VALIDATE = {
    # Top 5 Ligas Europeias
    'Premier League': 39,
    'La Liga': 140,
    'Bundesliga': 78,
    'Serie A': 135,
    'Ligue 1': 61,
    
    # Competições Europeias
    'Champions League': 2,
    'Europa League': 3,
    
    # 2ª Divisões
    'Championship': 40,
    'La Liga 2': 141,
    'Serie B': 136,
    'Bundesliga 2': 79,
    'Ligue 2': 62,
    
    # Outras Ligas
    'Eredivisie': 88,
    'Primeira Liga': 94,
    'Super Lig': 203,
    'Brasileirão': 71,
    'Liga MX': 262,
    'MLS': 253,
}


def validate_league(league_name, league_id, max_matches=150):
    """
    Valida modelo em uma liga específica
    
    Returns:
        dict com métricas de performance
    """
    print(f"\n{'='*80}")
    print(f"Validando: {league_name} (ID: {league_id})")
    print(f"{'='*80}")
    
    # Buscar partidas finalizadas da liga
    matches = Match.objects.filter(
        league__api_football_id=league_id,
        status='finished',
        home_score__isnull=False,
        away_score__isnull=False
    ).order_by('-match_date')[:max_matches]
    
    total = matches.count()
    if total == 0:
        print(f"❌ Nenhuma partida encontrada para {league_name}")
        return None
    
    print(f"✅ {total} partidas encontradas")
    print(f"🔄 Iniciando validação...")
    
    orchestrator = HybridAnalysisOrchestrator()
    
    results = {
        'total': 0,
        'correct': 0,
        'home_predictions': 0,
        'draw_predictions': 0,
        'away_predictions': 0,
        'home_correct': 0,
        'draw_correct': 0,
        'away_correct': 0,
        'actual_home': 0,
        'actual_draw': 0,
        'actual_away': 0,
        'errors': 0,
        'avg_confidence': 0,
        'confidence_sum': 0,
    }
    
    for i, match in enumerate(matches, 1):
        try:
            # Resultado real
            if match.home_score > match.away_score:
                actual = 'home'
                results['actual_home'] += 1
            elif match.away_score > match.home_score:
                actual = 'away'
                results['actual_away'] += 1
            else:
                actual = 'draw'
                results['actual_draw'] += 1
            
            # Executar análise RÁPIDA (sem AI)
            # 1) Enriquecer dados
            match_data = {'api_id': match.api_football_id}
            enriched = orchestrator.enricher.enrich(match_data)
            
            # 2) Feature engineering
            features = orchestrator.fe.engineer_all_features(enriched)
            
            # 3) Ensemble ML (SEM AI)
            strength = features.get('strength', {})
            weather = features.get('weather', {})
            home_strength = strength.get('home_goals_per_game', 1.2)
            away_strength = strength.get('away_goals_per_game', 1.2)
            weather_impact = weather.get('goal_impact', 0.0)
            league_id = match.league.api_football_id if match.league else None
            
            ensemble_result = orchestrator.ensemble.predict(
                features, home_strength, away_strength, weather_impact, league_id
            )
            
            if not ensemble_result:
                results['errors'] += 1
                continue
            
            # Extrair previsão
            consensus = ensemble_result.get('consensus', {})
            home_prob = consensus.get('home_win', 0) * 100
            draw_prob = consensus.get('draw', 0) * 100
            away_prob = consensus.get('away_win', 0) * 100
            
            # Determinar previsão (maior probabilidade)
            if home_prob > draw_prob and home_prob > away_prob:
                predicted = 'home'
                results['home_predictions'] += 1
                confidence = home_prob
            elif away_prob > draw_prob and away_prob > home_prob:
                predicted = 'away'
                results['away_predictions'] += 1
                confidence = away_prob
            else:
                predicted = 'draw'
                results['draw_predictions'] += 1
                confidence = draw_prob
            
            results['confidence_sum'] += confidence
            results['total'] += 1
            
            # Verificar acerto
            if predicted == actual:
                results['correct'] += 1
                
                if predicted == 'home':
                    results['home_correct'] += 1
                elif predicted == 'draw':
                    results['draw_correct'] += 1
                else:
                    results['away_correct'] += 1
            
            # Progresso
            if i % 25 == 0:
                current_acc = (results['correct'] / results['total'] * 100) if results['total'] > 0 else 0
                print(f"   Progresso: {i}/{total} | Acurácia atual: {current_acc:.1f}%")
        
        except Exception as e:
            print(f"   ⚠️ Erro na partida {match.id}: {str(e)}")
            results['errors'] += 1
            continue
    
    # Calcular métricas finais
    if results['total'] > 0:
        results['accuracy'] = (results['correct'] / results['total']) * 100
        results['avg_confidence'] = results['confidence_sum'] / results['total']
        
        # Precisão por tipo de resultado
        results['home_precision'] = (results['home_correct'] / results['home_predictions'] * 100) if results['home_predictions'] > 0 else 0
        results['draw_precision'] = (results['draw_correct'] / results['draw_predictions'] * 100) if results['draw_predictions'] > 0 else 0
        results['away_precision'] = (results['away_correct'] / results['away_predictions'] * 100) if results['away_predictions'] > 0 else 0
        
        # Recall por tipo de resultado
        results['home_recall'] = (results['home_correct'] / results['actual_home'] * 100) if results['actual_home'] > 0 else 0
        results['draw_recall'] = (results['draw_correct'] / results['actual_draw'] * 100) if results['actual_draw'] > 0 else 0
        results['away_recall'] = (results['away_correct'] / results['actual_away'] * 100) if results['actual_away'] > 0 else 0
    
    # Exibir resultados
    print(f"\n📈 RESULTADOS - {league_name}:")
    print(f"   Partidas analisadas: {results['total']}")
    print(f"   Acertos: {results['correct']}")
    print(f"   Erros análise: {results['errors']}")
    print(f"   ✅ ACURÁCIA: {results.get('accuracy', 0):.1f}%")
    print(f"   📊 Confiança média: {results.get('avg_confidence', 0):.1f}%")
    
    print(f"\n   Distribuição de previsões:")
    print(f"      Casa: {results['home_predictions']} ({results.get('home_precision', 0):.1f}% precisão)")
    print(f"      Empate: {results['draw_predictions']} ({results.get('draw_precision', 0):.1f}% precisão)")
    print(f"      Fora: {results['away_predictions']} ({results.get('away_precision', 0):.1f}% precisão)")
    
    return results


def main():
    """
    Executa validação estratificada completa
    """
    print("\n" + "="*80)
    print("VALIDACAO ESTRATIFICADA DO MODELO ML")
    print("="*80)
    print(f"\nIniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total de ligas: {len(LEAGUES_TO_VALIDATE)}")
    
    input("\nPressione ENTER para iniciar validacao...")
    
    all_results = {}
    category_results = {
        'Top 5': [],
        'Europeias': [],
        '2ª Divisões': [],
        'Outras': []
    }
    
    # Validar cada liga
    for league_name, league_id in LEAGUES_TO_VALIDATE.items():
        result = validate_league(league_name, league_id)
        
        if result:
            all_results[league_name] = result
            
            # Categorizar
            if league_name in ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1']:
                category_results['Top 5'].append((league_name, result))
            elif league_name in ['Champions League', 'Europa League']:
                category_results['Europeias'].append((league_name, result))
            elif league_name in ['Championship', 'La Liga 2', 'Serie B', 'Bundesliga 2', 'Ligue 2']:
                category_results['2ª Divisões'].append((league_name, result))
            else:
                category_results['Outras'].append((league_name, result))
    
    # Relatório Final
    print("\n" + "="*80)
    print("📊 RELATÓRIO FINAL - VALIDAÇÃO ESTRATIFICADA")
    print("="*80)
    
    # Estatísticas globais
    total_matches = sum(r['total'] for r in all_results.values())
    total_correct = sum(r['correct'] for r in all_results.values())
    global_accuracy = (total_correct / total_matches * 100) if total_matches > 0 else 0
    
    print(f"\n🌍 ESTATÍSTICAS GLOBAIS:")
    print(f"   Total de partidas: {total_matches}")
    print(f"   Total de acertos: {total_correct}")
    print(f"   ✅ ACURÁCIA GLOBAL: {global_accuracy:.2f}%")
    
    # Por categoria
    for category, leagues in category_results.items():
        if not leagues:
            continue
        
        print(f"\n{'='*80}")
        print(f"🏆 {category.upper()}")
        print(f"{'='*80}")
        
        cat_total = sum(r['total'] for _, r in leagues)
        cat_correct = sum(r['correct'] for _, r in leagues)
        cat_accuracy = (cat_correct / cat_total * 100) if cat_total > 0 else 0
        
        print(f"\n📊 Acurácia média: {cat_accuracy:.1f}%")
        print(f"\nDetalhamento por liga:")
        
        # Ordenar por acurácia
        leagues.sort(key=lambda x: x[1].get('accuracy', 0), reverse=True)
        
        for league_name, result in leagues:
            acc = result.get('accuracy', 0)
            conf = result.get('avg_confidence', 0)
            
            # Emoji de performance
            if acc >= 70:
                emoji = "🟢"
            elif acc >= 60:
                emoji = "🟡"
            else:
                emoji = "🔴"
            
            print(f"   {emoji} {league_name:20s}: {acc:5.1f}% (conf: {conf:.1f}%) | {result['total']} partidas")
    
    # Top 5 e Bottom 5
    print(f"\n{'='*80}")
    print("🏅 TOP 5 MELHORES LIGAS")
    print(f"{'='*80}")
    
    sorted_leagues = sorted(all_results.items(), key=lambda x: x[1].get('accuracy', 0), reverse=True)
    
    for i, (league_name, result) in enumerate(sorted_leagues[:5], 1):
        acc = result.get('accuracy', 0)
        print(f"   {i}. {league_name:20s}: {acc:.1f}%")
    
    print(f"\n{'='*80}")
    print("⚠️ BOTTOM 5 LIGAS (PRECISAM ATENÇÃO)")
    print(f"{'='*80}")
    
    for i, (league_name, result) in enumerate(sorted_leagues[-5:], 1):
        acc = result.get('accuracy', 0)
        print(f"   {i}. {league_name:20s}: {acc:.1f}%")
    
    # Insights
    print(f"\n{'='*80}")
    print("💡 INSIGHTS")
    print(f"{'='*80}")
    
    # Liga mais fácil
    best_league, best_result = sorted_leagues[0]
    print(f"\n✅ Melhor performance: {best_league} ({best_result.get('accuracy', 0):.1f}%)")
    
    # Liga mais difícil
    worst_league, worst_result = sorted_leagues[-1]
    print(f"❌ Pior performance: {worst_league} ({worst_result.get('accuracy', 0):.1f}%)")
    
    # Diferença entre melhor e pior
    diff = best_result.get('accuracy', 0) - worst_result.get('accuracy', 0)
    print(f"📊 Variação: {diff:.1f}% (indica necessidade de calibração por liga)")
    
    # Conclusão
    print(f"\n{'='*80}")
    print("🎯 CONCLUSÃO")
    print(f"{'='*80}")
    
    if global_accuracy >= 65:
        print("✅ Sistema PRONTO para produção!")
        print(f"   Acurácia global de {global_accuracy:.1f}% supera mercado (52-55%)")
    elif global_accuracy >= 60:
        print("🟡 Sistema BOM, mas recomenda-se calibração adicional")
    else:
        print("🔴 Sistema precisa de melhorias antes de produção")
    
    print(f"\n{'='*80}")
    print(f"Finalizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
