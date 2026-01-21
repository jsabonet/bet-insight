"""
Importa partidas finalizadas da API e testa acurácia
Busca partidas recentes, salva no banco, analisa e compara com resultados reais
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match, Team, League
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from apps.analysis.services.api_football_service import APIFootballService


def import_finished_matches(days_back=3, max_matches=10, main_leagues_only=True):
    """
    Importa partidas finalizadas da API-Football
    
    Args:
        days_back: Quantos dias atrás buscar
        max_matches: Máximo de partidas para importar
        main_leagues_only: Se True, busca apenas ligas principais
    """
    print(f"\n{'='*80}")
    print(f"📥 IMPORTANDO PARTIDAS FINALIZADAS DA API")
    print(f"{'='*80}")
    
    api = APIFootballService()
    
    # IDs das ligas ATIVAS em Janeiro 2026
    # Copas Estaduais Brasil, Ligas Asiáticas, Copa Africana, América do Sul
    active_league_ids = [
        520,   # Copa do Acre (Brasil)
        525,   # Campeonato Paulista (Brasil)
        524,   # Campeonato Carioca (Brasil)
        526,   # Campeonato Mineiro (Brasil)
        527,   # Campeonato Gaúcho (Brasil)
        531,   # Campeonato Catarinense (Brasil)
        169,   # Saudi Pro League (Arábia Saudita)
        113,   # J1 League (Japão) - preparação
        253,   # Major League Soccer (EUA) - preparação
        307,   # A-League (Austrália)
        271,   # Primera División (Argentina)
        373,   # AFCON - Copa Africana
    ]
    
    if main_leagues_only:
        print(f"🏆 Ligas ATIVAS: Copas Estaduais Brasil, Arábia Saudita, Austrália, Argentina, Copa Africana")
        league_ids = active_league_ids
    else:
        print(f"🌍 Todas as ligas")
        league_ids = None
    
    imported_count = 0
    matches_imported = []
    
    # Buscar partidas dos últimos dias
    for day_offset in range(days_back):
        if imported_count >= max_matches:
            break
            
        target_date = datetime.now() - timedelta(days=day_offset + 1)
        date_str = target_date.strftime('%Y-%m-%d')
        
        print(f"\n📅 Buscando partidas de {target_date.strftime('%d/%m/%Y')}...")
        
        if league_ids:
            # Buscar em cada liga principal
            for league_id in league_ids:
                if imported_count >= max_matches:
                    break
                
                try:
                    # Buscar fixtures da liga naquela data
                    fixtures_data = api.get_fixtures_by_date(date_str, league_id=league_id)
                    
                    if not fixtures_data or 'response' not in fixtures_data:
                        continue
                    
                    for fixture_data in fixtures_data['response']:
                        if imported_count >= max_matches:
                            break
                        
                        # Verificar se está finalizada
                        status = fixture_data['fixture']['status']['short']
                        if status not in ['FT', 'AET', 'PEN']:
                            continue
                        
                        # Verificar se tem placar
                        home_score = fixture_data['goals']['home']
                        away_score = fixture_data['goals']['away']
                        if home_score is None or away_score is None:
                            continue
                        
                        # Criar/atualizar partida no banco
                        match = import_single_match(fixture_data, api)
                        if match:
                            matches_imported.append(match)
                            imported_count += 1
                            print(f"   ✅ {match.home_team.name} {home_score}-{away_score} {match.away_team.name}")
                
                except Exception as e:
                    print(f"   ⚠️ Erro na liga {league_id}: {e}")
                    continue
        else:
            # Buscar todas as partidas daquela data
            try:
                fixtures_data = api.get_fixtures_by_date(date_str)
                
                if fixtures_data and 'response' in fixtures_data:
                    for fixture_data in fixtures_data['response']:
                        if imported_count >= max_matches:
                            break
                        
                        status = fixture_data['fixture']['status']['short']
                        if status not in ['FT', 'AET', 'PEN']:
                            continue
                        
                        home_score = fixture_data['goals']['home']
                        away_score = fixture_data['goals']['away']
                        if home_score is None or away_score is None:
                            continue
                        
                        match = import_single_match(fixture_data, api)
                        if match:
                            matches_imported.append(match)
                            imported_count += 1
                            print(f"   ✅ {match.home_team.name} {home_score}-{away_score} {match.away_team.name}")
            
            except Exception as e:
                print(f"   ⚠️ Erro: {e}")
                continue
    
    print(f"\n{'='*80}")
    print(f"✅ {imported_count} partidas importadas")
    print(f"{'='*80}\n")
    
    return matches_imported


def import_single_match(fixture_data, api):
    """Importa uma única partida para o banco de dados"""
    try:
        fixture_id = fixture_data['fixture']['id']
        
        # Verificar se já existe (usando api_football_id)
        if Match.objects.filter(api_football_id=fixture_id).exists():
            return Match.objects.get(api_football_id=fixture_id)
        
        # Criar/buscar times
        home_team_id = fixture_data['teams']['home']['id']
        away_team_id = fixture_data['teams']['away']['id']
        
        home_team, _ = Team.objects.get_or_create(
            api_id=home_team_id,
            defaults={
                'name': fixture_data['teams']['home']['name'],
                'logo': fixture_data['teams']['home']['logo']
            }
        )
        
        away_team, _ = Team.objects.get_or_create(
            api_id=away_team_id,
            defaults={
                'name': fixture_data['teams']['away']['name'],
                'logo': fixture_data['teams']['away']['logo']
            }
        )
        
        # Criar/buscar liga
        league_id = fixture_data['league']['id']
        league, _ = League.objects.get_or_create(
            api_id=league_id,
            defaults={
                'name': fixture_data['league']['name'],
                'country': fixture_data['league']['country'],
                'logo': fixture_data['league']['logo'],
                'season': fixture_data['league']['season']
            }
        )
        
        # Criar partida
        match_date = datetime.fromisoformat(fixture_data['fixture']['date'].replace('Z', '+00:00'))
        
        match = Match.objects.create(
            api_football_id=fixture_id,
            home_team=home_team,
            away_team=away_team,
            league=league,
            match_date=match_date,
            status=fixture_data['fixture']['status']['short'],
            home_score=fixture_data['goals']['home'],
            away_score=fixture_data['goals']['away'],
            round=fixture_data['league'].get('round')
        )
        
        return match
    
    except Exception as e:
        print(f"   ❌ Erro ao importar partida: {e}")
        return None


def analyze_and_compare(matches):
    """
    Analisa partidas e compara com resultados reais
    
    Args:
        matches: Lista de objetos Match para analisar
    """
    print(f"\n{'='*80}")
    print(f"🔍 ANALISANDO E COMPARANDO COM RESULTADOS REAIS")
    print(f"{'='*80}\n")
    
    orchestrator = HybridAnalysisOrchestrator()
    
    results = {
        'total': 0,
        'analyzed': 0,
        'errors': 0,
        'correct_all': 0,
        'correct_filtered': 0,
        'filtered_count': 0,
        'skipped_low_confidence': 0,
        'details': []
    }
    
    for match in matches:
        results['total'] += 1
        
        print(f"[{results['total']}/{len(matches)}] {match.home_team.name} vs {match.away_team.name}")
        try:
            # Executar análise (método correto: run)
            analysis = orchestrator.run(match)
            
            if not analysis or 'prediction' not in analysis:
                print(f"   ❌ Análise falhou\n")
                results['errors'] += 1
                continue
            
            results['analyzed'] += 1
            
            # Extrair predição
            prediction = analysis.get('prediction')  # 'home', 'draw', 'away'
            confidence_int = analysis.get('confidence', 3)
            confidence_score = confidence_int / 5.0  # Converter para 0-1
            
            # Probabilidades
            prob_home = analysis.get('home_probability', 0) / 100
            prob_draw = analysis.get('draw_probability', 0) / 100
            prob_away = analysis.get('away_probability', 0) / 100
            
            # Determinar resultado real
            if match.home_score > match.away_score:
                actual = 'HOME'
            elif match.home_score < match.away_score:
                actual = 'AWAY'
            else:
                actual = 'DRAW'
            
            # Converter predição (run retorna 'home', 'draw', 'away')
            pred_map = {
                'home': 'HOME',
                'draw': 'DRAW',
                'away': 'AWAY'
            }
            predicted = pred_map.get(prediction, prediction.upper() if prediction else 'UNKNOWN')
            
            # Verificar se passou no filtro de publicação
            max_prob = max(prob_home, prob_draw, prob_away)
            should_publish = max_prob >= 0.52 or confidence_score >= 0.75
            
            if should_publish:
                results['filtered_count'] += 1
            else:
                results['skipped_low_confidence'] += 1
            
            # Verificar acerto (apenas para 1X2)
            is_correct = predicted == actual
            
            if is_correct:
                results['correct_all'] += 1
                if should_publish:
                    results['correct_filtered'] += 1
            
            # Exibir resultado
            status = "✅" if is_correct else "❌"
            conf_stars = "⭐" * confidence_int
            
            print(f"   {status} Real: {actual} | Pred: {predicted} | Conf: {conf_stars} ({confidence_score:.2f})")
            print(f"   📊 Probs: H {prob_home*100:.1f}% | D {prob_draw*100:.1f}% | A {prob_away*100:.1f}%")
            print(f"   🎲 Placar: {match.home_score}-{match.away_score}")
            print()
            
            results['details'].append({
                'match': f"{match.home_team.name} vs {match.away_team.name}",
                'score': f"{match.home_score}-{match.away_score}",
                'actual': actual,
                'predicted': predicted,
                'correct': is_correct,
                'confidence': confidence_score,
                'published': should_publish,
                'probabilities': {
                    'home_win': prob_home,
                    'draw': prob_draw,
                    'away_win': prob_away
                }
            })
        
        except Exception as e:
            print(f"   ❌ Erro: {e}\n")
            results['errors'] += 1
            continue
    
    # Exibir resumo
    print(f"\n{'='*80}")
    print(f"📊 RESULTADOS FINAIS")
    print(f"{'='*80}")
    print(f"Total de partidas: {results['total']}")
    print(f"Analisadas com sucesso: {results['analyzed']}")
    print(f"Erros: {results['errors']}")
    
    if results['analyzed'] > 0:
        acc_all = (results['correct_all'] / results['analyzed']) * 100
        
        print(f"\n{'-'*80}")
        print(f"📈 ACURÁCIA GERAL (todas as predições):")
        print(f"{'-'*80}")
        print(f"✅ Acertos: {results['correct_all']}/{results['analyzed']}")
        print(f"🎯 Acurácia: {acc_all:.2f}%")
        
        if results['filtered_count'] > 0:
            acc_filtered = (results['correct_filtered'] / results['filtered_count']) * 100
            coverage = (results['filtered_count'] / results['analyzed']) * 100
            
            print(f"\n{'-'*80}")
            print(f"⭐ ACURÁCIA FILTRADA (apenas predições publicadas):")
            print(f"{'-'*80}")
            print(f"✅ Acertos: {results['correct_filtered']}/{results['filtered_count']}")
            print(f"🎯 Acurácia: {acc_filtered:.2f}%")
            print(f"📊 Cobertura: {coverage:.1f}% ({results['filtered_count']} de {results['analyzed']} partidas)")
            print(f"⏭️  Puladas: {results['skipped_low_confidence']} (baixa confiança)")
        
        print(f"\n{'='*80}")
        print(f"• Acurácia Geral: Todas as partidas (incluindo baixa confiança)")
        print(f"• Acurácia Filtrada: Apenas partidas de alta qualidade (prob ≥ 52% OU conf ≥ 0.75)")
        print(f"• Cobertura: % de partidas que passam no filtro de qualidade")
        print(f"• Meta: 55%+ de acurácia filtrada com 70%+ de cobertura")
        print(f"{'='*80}")
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Importa partidas e testa acurácia')
    parser.add_argument('--days', type=int, default=3, help='Dias atrás para buscar (padrão: 3)')
    parser.add_argument('--max', type=int, default=10, help='Máximo de partidas (padrão: 10)')
    parser.add_argument('--all-leagues', action='store_true', help='Incluir todas as ligas (não apenas principais)')
    
    args = parser.parse_args()
    
    # 1. Importar partidas finalizadas da API
    matches = import_finished_matches(
        days_back=args.days,
        max_matches=args.max,
        main_leagues_only=not args.all_leagues
    )
    
    if not matches:
        print("❌ Nenhuma partida importada. Tente aumentar --days ou usar --all-leagues")
        sys.exit(1)
    
    # 2. Analisar e comparar com resultados reais
    results = analyze_and_compare(matches)
    
    if results['analyzed'] == 0:
        print("❌ Nenhuma partida foi analisada com sucesso")
        sys.exit(1)
    
    # 3. Verificar meta de 55%
    if results['filtered_count'] > 0:
        acc = (results['correct_filtered'] / results['filtered_count']) * 100
        if acc >= 55:
            print(f"\n🎉 META ATINGIDA! Acurácia filtrada: {acc:.2f}% ≥ 55%")
        else:
            print(f"\n⚠️ Abaixo da meta. Acurácia filtrada: {acc:.2f}% < 55%")
