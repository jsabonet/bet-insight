"""
Teste de Acurácia do Sistema de Análise
Valida o HybridAnalysisOrchestrator com partidas finalizadas
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator


def test_accuracy(target_date=None, min_matches=1, max_matches=50, main_leagues_only=True):
    """
    Testa acurácia do sistema com partidas finalizadas
    
    Args:
        target_date: Data específica para buscar (datetime) ou None para ontem
        min_matches: Mínimo de partidas para validar
        max_matches: Máximo de partidas para testar
        main_leagues_only: Se True, busca apenas ligas principais
    """
    print(f"\n{'='*80}")
    print(f"🎯 TESTE DE ACURÁCIA - Sistema Híbrido")
    print(f"{'='*80}")
    
    # Se não especificado, buscar ontem
    if target_date is None:
        target_date = datetime.now() - timedelta(days=1)
    
    # Definir intervalo: do início ao fim do dia
    start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    print(f"📅 Buscando partidas de {start_of_day.strftime('%d/%m/%Y')}...")
    print(f"🎲 Alvo: {min_matches}-{max_matches} partidas")
    if main_leagues_only:
        print(f"🏆 Filtrando: Apenas ligas principais (sem amistosos)\n")
    else:
        print()
    
    # IDs das principais ligas (La Liga, Premier League, Serie A, Bundesliga, Ligue 1, etc)
    main_league_ids = [140, 39, 135, 78, 61, 94, 71, 88]  # Espanha, Inglaterra, Itália, Alemanha, França, Portugal, Brasil, Turquia
    
    # Query base
    query = Match.objects.filter(
        match_date__gte=start_of_day,
        match_date__lte=end_of_day,
        status__in=['FT', 'FINISHED', 'AET', 'PEN'],  # Finalizadas
        home_score__isnull=False,
        away_score__isnull=False
    )
    
    # Filtrar por ligas principais se solicitado
    if main_leagues_only:
        query = query.filter(league_id__in=main_league_ids)
    
    # Excluir amistosos (status Friendly ou league com "Friendly" no nome)
    query = query.exclude(league__name__icontains='friendly')
    
    matches = query.select_related('home_team', 'away_team', 'league').order_by('-match_date')[:max_matches]
    
    total = matches.count()
    
    if total < min_matches:
        print(f"❌ Apenas {total} partidas encontradas. Mínimo: {min_matches}")
        print(f"💡 Dica: Tente outra data ou desative filtro de ligas principais")
        return
    
    print(f"✅ {total} partidas encontradas\n")
    print(f"{'='*80}")
    print(f"INICIANDO ANÁLISES...")
    print(f"{'='*80}\n")
    
    # Estatísticas
    correct = 0
    total_analyzed = 0
    published = 0  # Quantas passaram no filtro
    published_correct = 0
    skipped = 0
    errors = 0
    
    orchestrator = HybridAnalysisOrchestrator()
    
    for i, match in enumerate(matches, 1):
        try:
            # Resultado real
            if match.home_score > match.away_score:
                actual = 'home'
            elif match.home_score < match.away_score:
                actual = 'away'
            else:
                actual = 'draw'
            
            # Análise
            result = orchestrator.run(match)
            
            if not result:
                print(f"❌ [{i}/{total}] Erro na análise: {match.home_team.name} vs {match.away_team.name}")
                errors += 1
                continue
            
            predicted = result.get('prediction')
            should_publish = result.get('should_publish', True)
            confidence = result.get('confidence', 0)
            home_prob = result.get('home_probability', 0)
            draw_prob = result.get('draw_probability', 0)
            away_prob = result.get('away_probability', 0)
            
            # Verificar se acertou
            is_correct = (predicted == actual)
            
            total_analyzed += 1
            if is_correct:
                correct += 1
            
            # Estatísticas de publicação (filtro de qualidade)
            if should_publish:
                published += 1
                if is_correct:
                    published_correct += 1
                status_emoji = "✅" if is_correct else "❌"
                print(f"{status_emoji} [{i}/{total}] {match.home_team.name} vs {match.away_team.name}")
                print(f"   Real: {actual.upper()} | Pred: {predicted.upper()} | Conf: {confidence}/5")
                print(f"   Probs: H {home_prob:.1f}% | D {draw_prob:.1f}% | A {away_prob:.1f}%")
            else:
                skipped += 1
                print(f"⏭️  [{i}/{total}] PULADO (baixa confiança) - {match.home_team.name} vs {match.away_team.name}")
                print(f"   Probs: H {home_prob:.1f}% | D {draw_prob:.1f}% | A {away_prob:.1f}%")
        
        except Exception as e:
            print(f"❌ [{i}/{total}] Erro: {str(e)}")
            errors += 1
            continue
    
    # Resultados finais
    print(f"\n{'='*80}")
    print(f"📊 RESULTADOS FINAIS")
    print(f"{'='*80}")
    print(f"Total de partidas: {total}")
    print(f"Analisadas com sucesso: {total_analyzed}")
    print(f"Erros: {errors}")
    print(f"\n{'─'*80}")
    print(f"📈 ACURÁCIA GERAL (todas as predições):")
    print(f"{'─'*80}")
    if total_analyzed > 0:
        accuracy = (correct / total_analyzed) * 100
        print(f"✅ Acertos: {correct}/{total_analyzed}")
        print(f"🎯 Acurácia: {accuracy:.2f}%")
    else:
        print(f"❌ Nenhuma partida analisada")
    
    print(f"\n{'─'*80}")
    print(f"⭐ ACURÁCIA FILTRADA (apenas predições publicadas):")
    print(f"{'─'*80}")
    if published > 0:
        published_accuracy = (published_correct / published) * 100
        coverage = (published / total_analyzed) * 100
        print(f"✅ Acertos: {published_correct}/{published}")
        print(f"🎯 Acurácia: {published_accuracy:.2f}%")
        print(f"📊 Cobertura: {coverage:.1f}% ({published} de {total_analyzed} partidas)")
        print(f"⏭️  Puladas: {skipped} (baixa confiança)")
    else:
        print(f"❌ Nenhuma predição publicada (todas abaixo do filtro)")
    
    print(f"\n{'='*80}")
    print(f"💡 INTERPRETAÇÃO:")
    print(f"{'='*80}")
    print(f"• Acurácia Geral: Todas as partidas (incluindo baixa confiança)")
    print(f"• Acurácia Filtrada: Apenas partidas de alta qualidade (prob ≥ 52% OU conf ≥ 0.75)")
    print(f"• Cobertura: % de partidas que passam no filtro de qualidade")
    print(f"• Meta: 55%+ de acurácia filtrada com 70%+ de cobertura")
    print(f"{'='*80}\n")


def test_accuracy_recent(days_back=30, min_matches=1, max_matches=50, main_leagues_only=True):
    """Testa acurácia com partidas recentes (últimos X dias)"""
    print(f"\n{'='*80}")
    print(f"🎯 TESTE DE ACURÁCIA - Sistema Híbrido")
    print(f"{'='*80}")
    print(f"📅 Buscando partidas dos últimos {days_back} dias...")
    print(f"🎲 Alvo: {min_matches}-{max_matches} partidas")
    if main_leagues_only:
        print(f"🏆 Filtrando: Apenas ligas principais (sem amistosos)\n")
    else:
        print()
    
    # IDs das principais ligas
    main_league_ids = [140, 39, 135, 78, 61, 94, 71, 88]
    
    cutoff_date = datetime.now() - timedelta(days=days_back)
    
    query = Match.objects.filter(
        match_date__gte=cutoff_date,
        status__in=['FT', 'FINISHED', 'AET', 'PEN'],
        home_score__isnull=False,
        away_score__isnull=False
    )
    
    if main_leagues_only:
        query = query.filter(league_id__in=main_league_ids)
    
    query = query.exclude(league__name__icontains='friendly')
    
    matches = query.select_related('home_team', 'away_team', 'league').order_by('-match_date')[:max_matches]
    
    total = matches.count()
    
    if total < min_matches:
        print(f"❌ Apenas {total} partidas encontradas. Mínimo: {min_matches}")
        print(f"💡 Dica: Aumente dias ou desative filtro de ligas")
        return
    
    print(f"✅ {total} partidas encontradas\n")
    
    # Processar o restante igual à função original
    print(f"{'='*80}")
    print(f"INICIANDO ANÁLISES...")
    print(f"{'='*80}\n")
    
    orchestrator = HybridAnalysisOrchestrator()
    
    results = []
    errors = 0
    
    for i, match in enumerate(matches, 1):
        try:
            # Determinar resultado real
            if match.home_score > match.away_score:
                actual = 'HOME'
            elif match.away_score > match.home_score:
                actual = 'AWAY'
            else:
                actual = 'DRAW'
            
            # Executar análise
            analysis = orchestrator.run(match)
            
            if not analysis:
                print(f"❌ [{i}/{total}] Falha ao analisar")
                errors += 1
                continue
            
            prediction = analysis.get('prediction', '').upper()
            confidence = analysis.get('confidence', 0)
            home_prob = analysis.get('home_probability', 0)
            draw_prob = analysis.get('draw_probability', 0)
            away_prob = analysis.get('away_probability', 0)
            should_publish = analysis.get('should_publish', False)
            
            # Mapear predição
            pred_map = {
                'HOME': 'HOME',
                'AWAY': 'AWAY',
                'DRAW': 'DRAW',
                'BTTS_YES': 'BTTS',
                'BTTS_NO': 'NO_BTTS',
                'OVER_2_5': 'OVER',
                'UNDER_2_5': 'UNDER'
            }
            predicted = pred_map.get(prediction, prediction)
            
            # Para mercados alternativos, considerar acerto se a predição probabilística estava correta
            if predicted not in ['HOME', 'AWAY', 'DRAW']:
                # Usar a maior probabilidade 1X2
                if home_prob > draw_prob and home_prob > away_prob:
                    predicted = 'HOME'
                elif away_prob > home_prob and away_prob > draw_prob:
                    predicted = 'AWAY'
                else:
                    predicted = 'DRAW'
            
            correct = (predicted == actual)
            
            results.append({
                'match': match,
                'actual': actual,
                'predicted': predicted,
                'correct': correct,
                'confidence': confidence,
                'home_prob': home_prob,
                'draw_prob': draw_prob,
                'away_prob': away_prob,
                'should_publish': should_publish
            })
            
            emoji = "✅" if correct else "❌"
            print(f"{emoji} [{i}/{total}] {match.home_team.name} vs {match.away_team.name}")
            print(f"   Real: {actual} | Pred: {predicted} | Conf: {confidence}/5")
            print(f"   Probs: H {home_prob:.1f}% | D {draw_prob:.1f}% | A {away_prob:.1f}%\n")
            
        except Exception as e:
            print(f"❌ [{i}/{total}] Erro: {str(e)}\n")
            errors += 1
    
    # Estatísticas finais
    print(f"{'='*80}")
    print(f"📊 RESULTADOS FINAIS")
    print(f"{'='*80}")
    print(f"Total de partidas: {total}")
    print(f"Analisadas com sucesso: {len(results)}")
    print(f"Erros: {errors}\n")
    
    if not results:
        print(f"❌ Nenhuma análise bem-sucedida")
        return
    
    total_analyzed = len(results)
    total_correct = sum(1 for r in results if r['correct'])
    published = sum(1 for r in results if r['should_publish'])
    published_correct = sum(1 for r in results if r['should_publish'] and r['correct'])
    skipped = total_analyzed - published
    
    print(f"{'─'*80}")
    print(f"📈 ACURÁCIA GERAL (todas as predições):")
    print(f"{'─'*80}")
    if total_analyzed > 0:
        accuracy = (total_correct / total_analyzed) * 100
        print(f"✅ Acertos: {total_correct}/{total_analyzed}")
        print(f"🎯 Acurácia: {accuracy:.2f}%")
    else:
        print(f"❌ Nenhuma partida analisada")
    
    print(f"\n{'─'*80}")
    print(f"⭐ ACURÁCIA FILTRADA (apenas predições publicadas):")
    print(f"{'─'*80}")
    if published > 0:
        published_accuracy = (published_correct / published) * 100
        coverage = (published / total_analyzed) * 100
        print(f"✅ Acertos: {published_correct}/{published}")
        print(f"🎯 Acurácia: {published_accuracy:.2f}%")
        print(f"📊 Cobertura: {coverage:.1f}% ({published} de {total_analyzed} partidas)")
        print(f"⏭️  Puladas: {skipped} (baixa confiança)")
    else:
        print(f"❌ Nenhuma predição publicada (todas abaixo do filtro)")
    
    print(f"\n{'='*80}")
    print(f"💡 INTERPRETAÇÃO:")
    print(f"{'='*80}")
    print(f"• Acurácia Geral: Todas as partidas (incluindo baixa confiança)")
    print(f"• Acurácia Filtrada: Apenas partidas de alta qualidade (prob ≥ 52% OU conf ≥ 0.75)")
    print(f"• Cobertura: % de partidas que passam no filtro de qualidade")
    print(f"• Meta: 55%+ de acurácia filtrada com 70%+ de cobertura")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Teste de Acurácia do Sistema')
    parser.add_argument('--date', type=str, help='Data específica (DD/MM/YYYY), "ontem" ou "recentes"')
    parser.add_argument('--min', type=int, default=1, help='Mínimo de partidas (padrão: 1)')
    parser.add_argument('--max', type=int, default=50, help='Máximo de partidas (padrão: 50)')
    parser.add_argument('--all-leagues', action='store_true', help='Incluir todas as ligas (sem filtro)')
    
    args = parser.parse_args()
    
    # Processar data
    target_date = None
    use_date_filter = True
    
    if args.date:
        if args.date.lower() == 'ontem':
            target_date = datetime.now() - timedelta(days=1)
        elif args.date.lower() == 'recentes':
            # Não usar filtro de data específica, buscar dos últimos 30 dias
            use_date_filter = False
            target_date = None
        else:
            try:
                target_date = datetime.strptime(args.date, '%d/%m/%Y')
            except ValueError:
                print(f"❌ Formato de data inválido. Use DD/MM/YYYY, 'ontem' ou 'recentes'")
                sys.exit(1)
    
    # Se usar filtro de data
    if use_date_filter and target_date:
        test_accuracy(
            target_date=target_date,
            min_matches=args.min,
            max_matches=args.max,
            main_leagues_only=not args.all_leagues
        )
    else:
        # Buscar partidas recentes (últimos 30 dias)
        test_accuracy_recent(
            days_back=30,
            min_matches=args.min,
            max_matches=args.max,
            main_leagues_only=not args.all_leagues
        )
