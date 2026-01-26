"""
Validação usando HybridAnalysisOrchestrator (ARQUITETURA COMPLETA)
Testa a arquitetura híbrida real implementada no projeto
"""
import os
import sys
import django
from datetime import datetime, timedelta
from pathlib import Path
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.services.football_api import FootballAPIService
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from apps.matches.models import Match, League, Team

def get_actual(home, away):
    if home > away: return [1, 0, 0]
    elif home < away: return [0, 0, 1]
    else: return [0, 1, 0]

def get_predicted_from_result(analysis_result):
    """Extrai predição 1X2 para validação.
    Se a recomendação do orchestrator não for 1X2 (ex: Over 2.5),
    usamos o consenso 1X2 dos modelos para avaliar acerto do resultado.
    """
    # Preferir consenso 1X2
    consensus = analysis_result.get('analysis_data', {}).get('consensus', {})
    if consensus:
        probs_1x2 = {
            'home_win': consensus.get('home_win', 0.0),
            'draw': consensus.get('draw', 0.0),
            'away_win': consensus.get('away_win', 0.0)
        }
        # Resultado com maior probabilidade
        market = max(probs_1x2.items(), key=lambda x: x[1])[0]
        map_1x2 = {
            'home_win': [1,0,0],
            'draw': [0,1,0],
            'away_win': [0,0,1]
        }
        return map_1x2.get(market, [1,0,0])

    # Fallback: usar campo 'prediction' somente se for 1X2
    prediction = analysis_result.get('prediction')
    mapping = {'home': [1,0,0], 'draw': [0,1,0], 'away': [0,0,1]}
    return mapping.get(prediction, [1,0,0])

def calculate_metrics(probs_dict, actual):
    """Calcula Brier Score e Log Loss"""
    probs = [
        probs_dict.get('home_win', 0) / 100 if isinstance(probs_dict.get('home_win', 0), (int, float)) and probs_dict.get('home_win', 0) > 1 else probs_dict.get('home_win', 0),
        probs_dict.get('draw', 0) / 100 if isinstance(probs_dict.get('draw', 0), (int, float)) and probs_dict.get('draw', 0) > 1 else probs_dict.get('draw', 0),
        probs_dict.get('away_win', 0) / 100 if isinstance(probs_dict.get('away_win', 0), (int, float)) and probs_dict.get('away_win', 0) > 1 else probs_dict.get('away_win', 0)
    ]
    
    # Normalizar se necessário
    total = sum(probs)
    if total > 0:
        probs = [p/total for p in probs]
    
    # Brier Score
    brier = np.mean([(probs[i] - actual[i])**2 for i in range(3)])
    
    # Log Loss
    probs = [max(min(x, 0.9999), 0.0001) for x in probs]
    log_loss_val = 0
    for i, a in enumerate(actual):
        if a == 1:
            log_loss_val = -np.log(probs[i])
            break
    
    return brier, log_loss_val

def is_market_hit(market, h_score, a_score):
    """Avalia acerto de um mercado dado o placar real."""
    h = h_score or 0
    a = a_score or 0
    total_goals = h + a
    
    # 1X2
    if market == 'home_win':
        return h > a
    if market == 'draw':
        return h == a
    if market == 'away_win':
        return h < a
    
    # Over/Under
    if market == 'over_1_5':
        return total_goals >= 2
    if market == 'under_1_5':
        return total_goals <= 1
    if market == 'over_2_5':
        return total_goals >= 3
    if market == 'under_2_5':
        return total_goals <= 2
    if market == 'over_3_5':
        return total_goals >= 4
    if market == 'under_3_5':
        return total_goals <= 3
    
    # BTTS
    if market == 'btts':
        return h > 0 and a > 0
    if market == 'btts_no':
        return h == 0 or a == 0
    
    # Double Chance
    if market == 'double_chance_1x':
        return h >= a  # Casa vence OU empate
    if market == 'double_chance_12':
        return h != a  # Casa vence OU fora vence (não empata)
    if market == 'double_chance_x2':
        return h <= a  # Empate OU fora vence
    
    # Team Goals
    if market == 'home_over_05':
        return h >= 1
    if market == 'home_over_15':
        return h >= 2
    if market == 'home_over_25':
        return h >= 3
    if market == 'away_over_05':
        return a >= 1
    if market == 'away_over_15':
        return a >= 2
    if market == 'away_over_25':
        return a >= 3
    
    return False

print("\n" + "="*80)
print("VALIDAÇÃO COM ARQUITETURA HÍBRIDA COMPLETA")
print("Usando HybridAnalysisOrchestrator (enricher + FE + ensemble + decision + AI)")
print("="*80 + "\n")

orchestrator = HybridAnalysisOrchestrator()

# MUDANÇA: Ler do dataset local em vez da API
print("Carregando dataset histórico (training_dataset.json)...")
dataset_path = Path(__file__).parent / 'ml_training' / 'training_dataset.json'

try:
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    print(f"✅ Dataset carregado: {len(dataset['data'])} partidas")
    
    # Converter dataset para formato esperado (similar à API)
    all_fixtures = []
    for match_data in dataset['data']:
        # Construir estrutura similar à retornada pela API
        fixture = {
            'fixture': {
                'id': match_data['fixture_id'],
                'date': match_data['date'],
                'status': {'short': 'FT'},
            },
            'teams': {
                'home': {'name': match_data['teams']['home']},
                'away': {'name': match_data['teams']['away']}
            },
            'goals': {
                'home': match_data['result']['home_goals'],
                'away': match_data['result']['away_goals']
            },
            'league': {
                'id': match_data['league_id'],
                'name': match_data['league'],
                'country': 'Unknown',
                'type': 'League'
            }
        }
        all_fixtures.append(fixture)
    
    print(f"Conversão concluída: {len(all_fixtures)} partidas convertidas")
    
except FileNotFoundError:
    print(f"❌ Dataset não encontrado em: {dataset_path}")
    print("Execute primeiro: python ml_training/collect_historical_data.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao carregar dataset: {e}")
    sys.exit(1)

# Não limitar a quantidade - usar TODAS as partidas do dataset para validação robusta
print(f"\nAnalisando {len(all_fixtures)} partidas com ARQUITETURA COMPLETA...")
print("(Usando dataset histórico em vez de API)")

# Processar partidas
results = []
failed = []
processed = 0
total_fixtures = len(all_fixtures)

for i, fixture_data in enumerate(all_fixtures, 1):
    fid = fixture_data['fixture']['id']
    home_name = fixture_data['teams']['home']['name']
    away_name = fixture_data['teams']['away']['name']
    h_score = fixture_data['goals']['home']
    a_score = fixture_data['goals']['away']
    league_name = fixture_data['league']['name']
    
    # Mostrar progresso a cada partida
    percentage = (i / total_fixtures) * 100
    print(f"\r[{i}/{total_fixtures}] ({percentage:.1f}%) Processando: {home_name} vs {away_name}...", end="", flush=True)
    
    try:
        # Criar objetos temporários para análise (usar filter().first() para evitar duplicatas)
        league = League.objects.filter(name=league_name).first()
        if not league:
            league, _ = League.objects.get_or_create(
                name=league_name,
                defaults={'country': fixture_data['league']['country']}
            )
        
        # Usar filter().first() para evitar erro com times duplicados
        home_team = Team.objects.filter(name=home_name).first()
        if not home_team:
            home_team, _ = Team.objects.get_or_create(
                name=home_name,
                defaults={'country': fixture_data['teams']['home'].get('country', 'Unknown')}
            )
        
        away_team = Team.objects.filter(name=away_name).first()
        if not away_team:
            away_team, _ = Team.objects.get_or_create(
                name=away_name,
                defaults={'country': fixture_data['teams']['away'].get('country', 'Unknown')}
            )
        
        match_date = datetime.fromisoformat(fixture_data['fixture']['date'].replace('Z', '+00:00'))
        
        # Criar Match temporário
        match = Match(
            api_football_id=fid,
            league=league,
            home_team=home_team,
            away_team=away_team,
            match_date=match_date,
            status='FT',
            home_score=h_score,
            away_score=a_score
        )
        
        # USAR ORCHESTRATOR COMPLETO
        analysis_result = orchestrator.run(match)
        
        # Extrair dados
        consensus = analysis_result['analysis_data']['consensus']
        prediction = analysis_result['prediction']
        confidence = analysis_result['confidence']
        value_bets = analysis_result['analysis_data'].get('value_bets', [])
        fair_odds = analysis_result['analysis_data']['fair_odds']
        
        # Comparar com resultado real
        actual = get_actual(h_score, a_score)
        predicted = get_predicted_from_result(analysis_result)
        is_correct = (predicted == actual)
        
        # Métricas
        brier, log_loss_val = calculate_metrics(consensus, actual)
        
        results.append({
            'id': fid,
            'home': home_name,
            'away': away_name,
            'score': f"{h_score}-{a_score}",
            'league': league_name,
            'predicted': prediction,
            'predicted_vector': predicted,
            'actual': actual,
            'correct': is_correct,
            'correct_1x2': is_correct,  # Adicionar para análise final
            'brier': brier,
            'log_loss': log_loss_val,
            'consensus': consensus,
            'confidence': confidence,
            'value_bets': value_bets,
            'fair_odds': fair_odds,
            'recommended_market': analysis_result.get('analysis_data', {}).get('recommendation', {}).get('market'),
            'recommended_correct': is_market_hit(analysis_result.get('analysis_data', {}).get('recommendation', {}).get('market', ''), h_score, a_score),
            'should_publish': analysis_result.get('should_publish', True),  # NOVO: Flag de filtro
            'publish_reason': analysis_result.get('analysis_data', {}).get('publish_filter', {}).get('reason', 'N/A'),
            'date': fixture_data['fixture']['date']
        })
        
        processed += 1
        
    except Exception as e:
        error_msg = str(e)[:100]
        print(f"  [X] Erro na partida {fid}: {error_msg}")  # Removido emoji para compatibilidade Windows
        failed.append({
            'id': fid,
            'home': home_name,
            'away': away_name,
            'reason': error_msg
        })

print(f"\n{'='*80}")
print("PROCESSAMENTO CONCLUÍDO")
print("="*80)
print(f"Partidas analisadas: {processed}")
print(f"Falhas: {len(failed)}")
print(f"Taxa de sucesso: {processed/(processed+len(failed))*100:.1f}%\n")

if processed < 20:
    print("⚠️ AVISO: Poucas partidas analisadas com sucesso")
    if processed > 0:
        print("Continuando com dados disponíveis...\n")
    else:
        print("ERRO: Nenhuma partida analisada com sucesso")
        sys.exit(1)

# Calcular métricas gerais
accuracy = sum(1 for r in results if r['correct']) / len(results) * 100
avg_brier = np.mean([r['brier'] for r in results])
avg_log_loss = np.mean([r['log_loss'] for r in results])

# Métricas FILTRADAS (apenas high-quality predictions - should_publish=True)
filtered_results = [r for r in results if r.get('should_publish', True)]
if filtered_results:
    filtered_accuracy = sum(1 for r in filtered_results if r['correct']) / len(filtered_results) * 100
    filtered_brier = np.mean([r['brier'] for r in filtered_results])
    filtered_log_loss = np.mean([r['log_loss'] for r in filtered_results])
    coverage = len(filtered_results) / len(results) * 100
else:
    filtered_accuracy = 0
    filtered_brier = 0
    filtered_log_loss = 0
    coverage = 0

# Métricas por confiança
by_confidence = {}
for r in results:
    conf = r['confidence']
    if conf not in by_confidence:
        by_confidence[conf] = {'total': 0, 'correct': 0}
    by_confidence[conf]['total'] += 1
    if r['correct']:
        by_confidence[conf]['correct'] += 1

# Value bets encontrados
total_value_bets = sum(len(r['value_bets']) for r in results)

# Métricas multi-mercado (EXPANDIDO: todos os mercados implementados)
market_metrics = {
    '1x2': {
        'total': len(results),
        'correct': sum(1 for r in results if r['correct'])
    },
    # Over/Under 1.5
    'over_1_5': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('over_1_5', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    'under_1_5': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('under_1_5', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    # Over/Under 2.5
    'over_2_5': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('over_2_5', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    'under_2_5': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('under_2_5', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    # Over/Under 3.5
    'over_3_5': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('over_3_5', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    'under_3_5': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('under_3_5', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    # BTTS
    'btts': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('btts', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    'btts_no': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('btts_no', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    # Double Chance
    'double_chance_1x': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('double_chance_1x', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    'double_chance_12': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('double_chance_12', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    'double_chance_x2': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('double_chance_x2', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    # Team Goals
    'home_over_05': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('home_over_05', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    'home_over_15': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('home_over_15', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    'away_over_05': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('away_over_05', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    'away_over_15': {
        'total': len(results),
        'correct': sum(1 for r in results if is_market_hit('away_over_15', int(r['score'].split('-')[0]), int(r['score'].split('-')[1])))
    },
    # Pick recomendado
    'recommended_pick': {
        'total': len([r for r in results if r.get('recommended_market')]),
        'correct': sum(1 for r in results if r.get('recommended_market') and r.get('recommended_correct'))
    }
}

# Salvar resultados
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
output_file = f'validation_orchestrator_{timestamp}.json'

output_data = {
    'metadata': {
        'timestamp': timestamp,
        'architecture': 'HybridAnalysisOrchestrator (COMPLETA)',
        'components': ['MatchDataEnricher', 'FeatureEngineer', 'ModelEnsemble', 'DecisionEngine', 'AIAnalyzer'],
        'total_matches': len(all_fixtures),
        'processed': processed,
        'failed': len(failed)
    },
    'summary': {
        'total_matches': processed,
        'accuracy': accuracy,
        'brier_score': avg_brier,
        'log_loss': avg_log_loss,
        'value_bets_found': total_value_bets,
        'by_confidence': {str(k): v for k, v in by_confidence.items()},
        'filtered_metrics': {  # NOVO: Métricas apenas de high-quality predictions
            'total_filtered': len(filtered_results),
            'coverage': round(coverage, 1),
            'accuracy': round(filtered_accuracy, 2),
            'brier_score': round(filtered_brier, 4),
            'log_loss': round(filtered_log_loss, 4)
        }
    },
    'market_metrics': {
        # 1X2
        '1x2_accuracy': round(market_metrics['1x2']['correct'] / max(1, market_metrics['1x2']['total']) * 100, 2),
        # Over/Under
        'over_15_accuracy': round(market_metrics['over_1_5']['correct'] / max(1, market_metrics['over_1_5']['total']) * 100, 2),
        'under_15_accuracy': round(market_metrics['under_1_5']['correct'] / max(1, market_metrics['under_1_5']['total']) * 100, 2),
        'over_25_accuracy': round(market_metrics['over_2_5']['correct'] / max(1, market_metrics['over_2_5']['total']) * 100, 2),
        'under_25_accuracy': round(market_metrics['under_2_5']['correct'] / max(1, market_metrics['under_2_5']['total']) * 100, 2),
        'over_35_accuracy': round(market_metrics['over_3_5']['correct'] / max(1, market_metrics['over_3_5']['total']) * 100, 2),
        'under_35_accuracy': round(market_metrics['under_3_5']['correct'] / max(1, market_metrics['under_3_5']['total']) * 100, 2),
        # BTTS
        'btts_accuracy': round(market_metrics['btts']['correct'] / max(1, market_metrics['btts']['total']) * 100, 2),
        'btts_no_accuracy': round(market_metrics['btts_no']['correct'] / max(1, market_metrics['btts_no']['total']) * 100, 2),
        # Double Chance
        'double_chance_1x_accuracy': round(market_metrics['double_chance_1x']['correct'] / max(1, market_metrics['double_chance_1x']['total']) * 100, 2),
        'double_chance_12_accuracy': round(market_metrics['double_chance_12']['correct'] / max(1, market_metrics['double_chance_12']['total']) * 100, 2),
        'double_chance_x2_accuracy': round(market_metrics['double_chance_x2']['correct'] / max(1, market_metrics['double_chance_x2']['total']) * 100, 2),
        # Team Goals
        'home_over_05_accuracy': round(market_metrics['home_over_05']['correct'] / max(1, market_metrics['home_over_05']['total']) * 100, 2),
        'home_over_15_accuracy': round(market_metrics['home_over_15']['correct'] / max(1, market_metrics['home_over_15']['total']) * 100, 2),
        'away_over_05_accuracy': round(market_metrics['away_over_05']['correct'] / max(1, market_metrics['away_over_05']['total']) * 100, 2),
        'away_over_15_accuracy': round(market_metrics['away_over_15']['correct'] / max(1, market_metrics['away_over_15']['total']) * 100, 2),
        # Recomendação
        'recommended_pick_accuracy': round(market_metrics['recommended_pick']['correct'] / max(1, market_metrics['recommended_pick']['total']) * 100, 2)
    },
    'detailed_results': results,
    'failed_matches': failed
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print("="*80)
print("RESULTADOS FINAIS (ARQUITETURA COMPLETA)")
print("="*80)
print(f"Total de partidas: {processed}")
print(f"Acurácia: {accuracy:.2f}%")
print(f"Brier Score: {avg_brier:.4f}")
print(f"Log Loss: {avg_log_loss:.4f}")
print(f"Value Bets encontrados: {total_value_bets}")
print()
print("Acurácia por nível de confiança:")
for conf in sorted(by_confidence.keys()):
    data = by_confidence[conf]
    acc = (data['correct'] / data['total'] * 100) if data['total'] > 0 else 0
    print(f"  Confiança {conf}/5: {acc:.1f}% ({data['correct']}/{data['total']})")
print()
print("="*80)
print("MÉTRICAS FILTRADAS (High-Quality Predictions Only)")
print("="*80)
print(f"Previsões filtradas: {len(filtered_results)}/{len(results)} ({coverage:.1f}% coverage)")
print(f"Acurácia filtrada: {filtered_accuracy:.2f}% (vs {accuracy:.2f}% geral)")
print(f"Brier Score filtrado: {filtered_brier:.4f} (vs {avg_brier:.4f} geral)")
print(f"Log Loss filtrado: {filtered_log_loss:.4f} (vs {avg_log_loss:.4f} geral)")
print(f"\nGanho de acurácia: {filtered_accuracy - accuracy:+.2f}% (trade-off: -{100-coverage:.1f}% volume)")
print()
print("Métricas por mercado:")
print("\n📊 1X2:")
print(f"  Consenso 1X2: {market_metrics['1x2']['correct']}/{market_metrics['1x2']['total']} ({market_metrics['1x2']['correct']/max(1,market_metrics['1x2']['total'])*100:.2f}%)")

print("\n📈 Over/Under 1.5:")
print(f"  Over 1.5: {market_metrics['over_1_5']['correct']}/{market_metrics['over_1_5']['total']} ({market_metrics['over_1_5']['correct']/max(1,market_metrics['over_1_5']['total'])*100:.2f}%)")
print(f"  Under 1.5: {market_metrics['under_1_5']['correct']}/{market_metrics['under_1_5']['total']} ({market_metrics['under_1_5']['correct']/max(1,market_metrics['under_1_5']['total'])*100:.2f}%)")

print("\n📈 Over/Under 2.5:")
print(f"  Over 2.5: {market_metrics['over_2_5']['correct']}/{market_metrics['over_2_5']['total']} ({market_metrics['over_2_5']['correct']/max(1,market_metrics['over_2_5']['total'])*100:.2f}%)")
print(f"  Under 2.5: {market_metrics['under_2_5']['correct']}/{market_metrics['under_2_5']['total']} ({market_metrics['under_2_5']['correct']/max(1,market_metrics['under_2_5']['total'])*100:.2f}%)")

print("\n📈 Over/Under 3.5:")
print(f"  Over 3.5: {market_metrics['over_3_5']['correct']}/{market_metrics['over_3_5']['total']} ({market_metrics['over_3_5']['correct']/max(1,market_metrics['over_3_5']['total'])*100:.2f}%)")
print(f"  Under 3.5: {market_metrics['under_3_5']['correct']}/{market_metrics['under_3_5']['total']} ({market_metrics['under_3_5']['correct']/max(1,market_metrics['under_3_5']['total'])*100:.2f}%)")

print("\n⚽ BTTS (Ambas Marcam):")
print(f"  BTTS Sim: {market_metrics['btts']['correct']}/{market_metrics['btts']['total']} ({market_metrics['btts']['correct']/max(1,market_metrics['btts']['total'])*100:.2f}%)")
print(f"  BTTS Não: {market_metrics['btts_no']['correct']}/{market_metrics['btts_no']['total']} ({market_metrics['btts_no']['correct']/max(1,market_metrics['btts_no']['total'])*100:.2f}%)")

print("\n🎲 Double Chance:")
print(f"  1X (Casa/Empate): {market_metrics['double_chance_1x']['correct']}/{market_metrics['double_chance_1x']['total']} ({market_metrics['double_chance_1x']['correct']/max(1,market_metrics['double_chance_1x']['total'])*100:.2f}%)")
print(f"  12 (Casa/Fora): {market_metrics['double_chance_12']['correct']}/{market_metrics['double_chance_12']['total']} ({market_metrics['double_chance_12']['correct']/max(1,market_metrics['double_chance_12']['total'])*100:.2f}%)")
print(f"  X2 (Empate/Fora): {market_metrics['double_chance_x2']['correct']}/{market_metrics['double_chance_x2']['total']} ({market_metrics['double_chance_x2']['correct']/max(1,market_metrics['double_chance_x2']['total'])*100:.2f}%)")

print("\n🏠 Team Goals Casa:")
print(f"  Casa Over 0.5: {market_metrics['home_over_05']['correct']}/{market_metrics['home_over_05']['total']} ({market_metrics['home_over_05']['correct']/max(1,market_metrics['home_over_05']['total'])*100:.2f}%)")
print(f"  Casa Over 1.5: {market_metrics['home_over_15']['correct']}/{market_metrics['home_over_15']['total']} ({market_metrics['home_over_15']['correct']/max(1,market_metrics['home_over_15']['total'])*100:.2f}%)")

print("\n✈️ Team Goals Fora:")
print(f"  Fora Over 0.5: {market_metrics['away_over_05']['correct']}/{market_metrics['away_over_05']['total']} ({market_metrics['away_over_05']['correct']/max(1,market_metrics['away_over_05']['total'])*100:.2f}%)")
print(f"  Fora Over 1.5: {market_metrics['away_over_15']['correct']}/{market_metrics['away_over_15']['total']} ({market_metrics['away_over_15']['correct']/max(1,market_metrics['away_over_15']['total'])*100:.2f}%)")

print("\n🎯 Recomendação:")
print(f"  Pick recomendado: {market_metrics['recommended_pick']['correct']}/{market_metrics['recommended_pick']['total']} ({market_metrics['recommended_pick']['correct']/max(1,market_metrics['recommended_pick']['total'])*100:.2f}%)")
print()
print(f"Resultados salvos em: {output_file}")
print("="*80)
