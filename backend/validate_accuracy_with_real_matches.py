"""
VALIDAÇÃO DE ACERTIVIDADE - Teste com Partidas Finalizadas
============================================================
Este script busca partidas finalizadas e compara as previsões
do modelo com os resultados reais para calcular a taxa de acerto.
"""
import os
import sys
import django
from datetime import datetime, timedelta
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

print("\n" + "="*100)
print("🎯 VALIDAÇÃO DE ACERTIVIDADE - TESTE COM PARTIDAS FINALIZADAS")
print("="*100)

# Configurações
NUM_DAYS_BACK = 7  # Buscar partidas dos últimos 7 dias
MIN_MATCHES = 20   # Mínimo de partidas para validação
CONFIDENCE_LEVELS = [1, 2, 3, 4, 5]  # Níveis de confiança

# Ligas principais para testar
MAIN_LEAGUES = {
    39: "Premier League",
    140: "La Liga",
    61: "Ligue 1",
    78: "Bundesliga",
    135: "Serie A",
}

def get_finished_matches(api, days_back=7):
    """Busca partidas finalizadas dos últimos N dias"""
    print(f"\n📅 Buscando partidas finalizadas dos últimos {days_back} dias...")
    print("-"*100)
    
    all_finished = []
    
    for day_offset in range(days_back):
        date = (datetime.now() - timedelta(days=day_offset)).strftime('%Y-%m-%d')
        print(f"\n   📆 Data: {date}")
        
        result = api.get_fixtures_by_date(date)
        
        if result['success']:
            fixtures = result['fixtures']
            finished = [f for f in fixtures if f['fixture']['status']['short'] == 'FT']
            
            # Filtrar apenas ligas principais
            finished_main = [
                f for f in finished 
                if f['league']['id'] in MAIN_LEAGUES
            ]
            
            print(f"      ✅ Total: {len(fixtures)} | Finalizadas: {len(finished)} | Ligas principais: {len(finished_main)}")
            all_finished.extend(finished_main)
        else:
            print(f"      ❌ Erro: {result.get('error')}")
    
    print(f"\n📊 Total de partidas finalizadas encontradas: {len(all_finished)}")
    return all_finished


def get_match_result(home_score, away_score):
    """Determina o resultado da partida"""
    if home_score > away_score:
        return 'home'
    elif away_score > home_score:
        return 'away'
    return 'draw'


def get_model_prediction(consensus_probs):
    """Determina a previsão do modelo baseada nas probabilidades"""
    home_prob = consensus_probs.get('home_win', 0)
    draw_prob = consensus_probs.get('draw', 0)
    away_prob = consensus_probs.get('away_win', 0)
    
    max_prob = max(home_prob, draw_prob, away_prob)
    
    if max_prob == home_prob:
        return 'home', home_prob
    elif max_prob == away_prob:
        return 'away', away_prob
    return 'draw', draw_prob


def calculate_confidence_level(probability):
    """Calcula nível de confiança baseado na probabilidade"""
    if probability >= 0.70:
        return 5
    elif probability >= 0.60:
        return 4
    elif probability >= 0.50:
        return 3
    elif probability >= 0.40:
        return 2
    return 1


def validate_match(fixture, orchestrator):
    """Valida uma partida contra o modelo"""
    fixture_id = fixture['fixture']['id']
    home_team = fixture['teams']['home']['name']
    away_team = fixture['teams']['away']['name']
    league_name = fixture['league']['name']
    
    # Resultado real
    home_score = fixture['goals']['home']
    away_score = fixture['goals']['away']
    actual_result = get_match_result(home_score, away_score)
    
    print(f"\n   🏟️  {home_team} vs {away_team}")
    print(f"      Liga: {league_name}")
    print(f"      Placar: {home_score}-{away_score} | Resultado: {actual_result}")
    
    try:
        # Criar objeto Match temporário
        from apps.matches.models import Match, Team, League
        
        # Tentar buscar ou criar match
        try:
            match = Match.objects.get(api_football_id=fixture_id)
        except Match.DoesNotExist:
            # Criar temporariamente para análise
            match = Match(
                api_football_id=fixture_id,
                match_date=fixture['fixture']['date'],
                status=fixture['fixture']['status']['short']
            )
        
        # Executar análise
        result = orchestrator.run(match)
        
        if not result:
            print(f"      ❌ Análise falhou")
            return None
        
        # Extrair probabilidades
        consensus = result.get('model_probabilities', {}).get('consensus', {})
        
        if not consensus:
            print(f"      ❌ Consenso não disponível")
            return None
        
        # Previsão do modelo
        predicted_result, probability = get_model_prediction(consensus)
        confidence = calculate_confidence_level(probability)
        
        # Verificar acerto
        is_correct = (predicted_result == actual_result)
        
        print(f"      🤖 Previsão: {predicted_result} ({probability*100:.1f}%) | Confiança: {confidence}★")
        print(f"      {'✅ ACERTOU' if is_correct else '❌ ERROU'}")
        
        return {
            'fixture_id': fixture_id,
            'home_team': home_team,
            'away_team': away_team,
            'league': league_name,
            'actual_result': actual_result,
            'actual_score': f"{home_score}-{away_score}",
            'predicted_result': predicted_result,
            'probability': probability,
            'confidence': confidence,
            'is_correct': is_correct,
            'probabilities': {
                'home': consensus.get('home_win', 0),
                'draw': consensus.get('draw', 0),
                'away': consensus.get('away_win', 0)
            }
        }
        
    except Exception as e:
        print(f"      ❌ Erro: {str(e)}")
        return None


def generate_report(validations):
    """Gera relatório completo de acertividade"""
    if not validations:
        print("\n❌ Nenhuma validação disponível para relatório")
        return
    
    total = len(validations)
    correct = sum(1 for v in validations if v['is_correct'])
    accuracy = (correct / total * 100) if total > 0 else 0
    
    print("\n" + "="*100)
    print("📊 RELATÓRIO DE ACERTIVIDADE")
    print("="*100)
    
    print(f"\n📈 RESULTADOS GERAIS:")
    print(f"   Total de partidas analisadas: {total}")
    print(f"   Previsões corretas: {correct}")
    print(f"   Previsões incorretas: {total - correct}")
    print(f"   Taxa de acerto: {accuracy:.1f}%")
    
    # Análise por nível de confiança
    print(f"\n⭐ ACERTIVIDADE POR NÍVEL DE CONFIANÇA:")
    print("-"*100)
    
    for level in range(5, 0, -1):
        level_validations = [v for v in validations if v['confidence'] == level]
        level_total = len(level_validations)
        level_correct = sum(1 for v in level_validations if v['is_correct'])
        level_accuracy = (level_correct / level_total * 100) if level_total > 0 else 0
        
        stars = "⭐" * level
        print(f"   {stars} ({level}★): {level_correct}/{level_total} = {level_accuracy:.1f}%")
    
    # Análise por tipo de resultado
    print(f"\n🎯 ACERTIVIDADE POR TIPO DE RESULTADO:")
    print("-"*100)
    
    for result_type in ['home', 'draw', 'away']:
        type_validations = [v for v in validations if v['actual_result'] == result_type]
        type_total = len(type_validations)
        type_correct = sum(1 for v in type_validations if v['is_correct'])
        type_accuracy = (type_correct / type_total * 100) if type_total > 0 else 0
        
        label = {'home': 'Vitória Casa', 'draw': 'Empate', 'away': 'Vitória Fora'}[result_type]
        print(f"   {label}: {type_correct}/{type_total} = {type_accuracy:.1f}%")
    
    # Análise por liga
    print(f"\n🏆 ACERTIVIDADE POR LIGA:")
    print("-"*100)
    
    leagues = set(v['league'] for v in validations)
    for league in sorted(leagues):
        league_validations = [v for v in validations if v['league'] == league]
        league_total = len(league_validations)
        league_correct = sum(1 for v in league_validations if v['is_correct'])
        league_accuracy = (league_correct / league_total * 100) if league_total > 0 else 0
        
        print(f"   {league}: {league_correct}/{league_total} = {league_accuracy:.1f}%")
    
    # Análise de probabilidades médias
    print(f"\n📊 PROBABILIDADES MÉDIAS:")
    print("-"*100)
    
    correct_validations = [v for v in validations if v['is_correct']]
    incorrect_validations = [v for v in validations if not v['is_correct']]
    
    if correct_validations:
        avg_prob_correct = sum(v['probability'] for v in correct_validations) / len(correct_validations)
        print(f"   Previsões corretas: {avg_prob_correct*100:.1f}%")
    
    if incorrect_validations:
        avg_prob_incorrect = sum(v['probability'] for v in incorrect_validations) / len(incorrect_validations)
        print(f"   Previsões incorretas: {avg_prob_incorrect*100:.1f}%")
    
    # Comparação com mercado
    print(f"\n💰 COMPARAÇÃO COM ODDS DE MERCADO:")
    print("-"*100)
    
    # Calcular alinhamento com probabilidades do mercado
    market_alignments = []
    for v in validations:
        probs = v['probabilities']
        # Odds implícitas do mercado (estimativa conservadora)
        if v['actual_result'] == 'home':
            market_prob = 0.45  # ~2.20 odds
        elif v['actual_result'] == 'away':
            market_prob = 0.40  # ~2.50 odds
        else:
            market_prob = 0.30  # ~3.30 odds
        
        model_prob = probs[v['actual_result']]
        alignment = abs(model_prob - market_prob)
        market_alignments.append(alignment)
    
    avg_alignment = sum(market_alignments) / len(market_alignments) if market_alignments else 0
    print(f"   Erro médio vs mercado: {avg_alignment*100:.1f} pontos percentuais")
    
    # Avaliação final
    print(f"\n" + "="*100)
    print("🎯 AVALIAÇÃO FINAL:")
    print("="*100)
    
    if accuracy >= 60:
        print(f"   ✅ EXCELENTE: Taxa de acerto de {accuracy:.1f}% está acima da meta (60%)")
        print(f"   💚 O modelo está pronto para uso comercial")
    elif accuracy >= 55:
        print(f"   ⚠️  BOM: Taxa de acerto de {accuracy:.1f}% está próxima da meta")
        print(f"   💛 Recomenda-se calibração adicional antes do lançamento")
    elif accuracy >= 50:
        print(f"   ⚠️  REGULAR: Taxa de acerto de {accuracy:.1f}% precisa melhorar")
        print(f"   🟠 Necessário ajuste nos modelos estatísticos")
    else:
        print(f"   ❌ INSUFICIENTE: Taxa de acerto de {accuracy:.1f}% está abaixo do aceitável")
        print(f"   🔴 NÃO recomendado para uso comercial - revisar modelos")
    
    print("="*100 + "\n")
    
    return {
        'total': total,
        'correct': correct,
        'accuracy': accuracy,
        'by_confidence': {
            level: {
                'total': len([v for v in validations if v['confidence'] == level]),
                'correct': sum(1 for v in validations if v['confidence'] == level and v['is_correct']),
                'accuracy': (sum(1 for v in validations if v['confidence'] == level and v['is_correct']) / len([v for v in validations if v['confidence'] == level]) * 100) if len([v for v in validations if v['confidence'] == level]) > 0 else 0
            }
            for level in range(1, 6)
        },
        'by_result_type': {
            result_type: {
                'total': len([v for v in validations if v['actual_result'] == result_type]),
                'correct': sum(1 for v in validations if v['actual_result'] == result_type and v['is_correct']),
                'accuracy': (sum(1 for v in validations if v['actual_result'] == result_type and v['is_correct']) / len([v for v in validations if v['actual_result'] == result_type]) * 100) if len([v for v in validations if v['actual_result'] == result_type]) > 0 else 0
            }
            for result_type in ['home', 'draw', 'away']
        }
    }


def save_report(validations, summary):
    """Salva relatório em arquivo JSON"""
    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': summary,
        'validations': validations
    }
    
    filename = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Relatório salvo em: {filename}\n")


def main():
    """Função principal"""
    # Inicializar serviços
    api = FootballAPIService()
    orchestrator = HybridAnalysisOrchestrator()
    
    # Buscar partidas finalizadas
    finished_matches = get_finished_matches(api, NUM_DAYS_BACK)
    
    if len(finished_matches) < MIN_MATCHES:
        print(f"\n⚠️  AVISO: Apenas {len(finished_matches)} partidas encontradas (mínimo: {MIN_MATCHES})")
        print(f"   Considere aumentar NUM_DAYS_BACK ou aceitar amostra menor")
        
        if len(finished_matches) == 0:
            print(f"\n❌ Nenhuma partida disponível para validação")
            return
    
    # Limitar ao número máximo para evitar uso excessivo da API
    MAX_MATCHES = 30
    if len(finished_matches) > MAX_MATCHES:
        print(f"\n⚠️  Limitando análise a {MAX_MATCHES} partidas (das {len(finished_matches)} disponíveis)")
        finished_matches = finished_matches[:MAX_MATCHES]
    
    # Validar cada partida
    print(f"\n" + "="*100)
    print(f"🔄 VALIDANDO {len(finished_matches)} PARTIDAS...")
    print("="*100)
    
    validations = []
    for i, fixture in enumerate(finished_matches, 1):
        print(f"\n[{i}/{len(finished_matches)}]")
        validation = validate_match(fixture, orchestrator)
        if validation:
            validations.append(validation)
    
    # Gerar relatório
    if validations:
        summary = generate_report(validations)
        save_report(validations, summary)
    else:
        print("\n❌ Nenhuma validação bem-sucedida")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Validação interrompida pelo usuário")
    except Exception as e:
        print(f"\n\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
