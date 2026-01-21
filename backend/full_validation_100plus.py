"""
Validacao expandida com 100+ partidas finalizadas
Gera relatorio completo de acertividade para confirmacao definitiva
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
from apps.analysis.services.match_enricher import MatchDataEnricher
from apps.analysis.services.feature_engineer import FeatureEngineer
from apps.analysis.services.statistical_models import ModelEnsemble
import numpy as np

# Funcoes auxiliares
def get_actual(home, away):
    if home > away: return [1, 0, 0]
    elif home < away: return [0, 0, 1]
    else: return [0, 1, 0]

def predict(probs):
    vals = [probs.get('home_win', 0), probs.get('draw', 0), probs.get('away_win', 0)]
    idx = vals.index(max(vals))
    return ['home_win', 'draw', 'away_win'][idx]

def correct(pred, actual):
    mapping = {'home_win': [1,0,0], 'draw': [0,1,0], 'away_win': [0,0,1]}
    return mapping[pred] == actual

def brier(probs, actual):
    p = [probs.get('home_win', 0), probs.get('draw', 0), probs.get('away_win', 0)]
    return np.mean([(p[i] - actual[i])**2 for i in range(3)])

def log_loss(probs, actual):
    p = [probs.get('home_win', 0), probs.get('draw', 0), probs.get('away_win', 0)]
    p = [max(min(x, 0.9999), 0.0001) for x in p]
    for i, a in enumerate(actual):
        if a == 1:
            return -np.log(p[i])
    return 0

print("\n" + "="*80)
print("VALIDACAO EXPANDIDA - 100+ PARTIDAS")
print("="*80 + "\n")

api = FootballAPIService()
enricher = MatchDataEnricher()
fe = FeatureEngineer()
ensemble = ModelEnsemble()

# Buscar partidas dos ultimos 7 dias
print("Coletando partidas finalizadas dos ultimos 7 dias...")
all_fixtures = []

for days_ago in range(7):
    date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    print(f"  {date}...", end=" ")
    
    try:
        result = api.get_fixtures_by_date(date)
        if result.get('success'):
            finished = [f for f in result['fixtures'] if f['fixture']['status']['short'] == 'FT']
            all_fixtures.extend(finished)
            print(f"{len(finished)} partidas")
        else:
            print("0 partidas")
    except Exception as e:
        print(f"Erro: {str(e)[:30]}")

print(f"\nTotal coletado: {len(all_fixtures)} partidas")

if len(all_fixtures) < 50:
    print("\nPoucas partidas encontradas. Expandindo busca para ultimos 14 dias...")
    
    for days_ago in range(7, 14):
        date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        print(f"  {date}...", end=" ")
        
        try:
            result = api.get_fixtures_by_date(date)
            if result.get('success'):
                finished = [f for f in result['fixtures'] if f['fixture']['status']['short'] == 'FT']
                all_fixtures.extend(finished)
                print(f"{len(finished)} partidas")
            else:
                print("0 partidas")
        except Exception as e:
            print(f"Erro: {str(e)[:30]}")
    
    print(f"\nTotal expandido: {len(all_fixtures)} partidas")

# Filtrar partidas duplicadas por ID
unique_fixtures = {}
for f in all_fixtures:
    fid = f['fixture']['id']
    if fid not in unique_fixtures:
        unique_fixtures[fid] = f

all_fixtures = list(unique_fixtures.values())
print(f"Partidas unicas: {len(all_fixtures)}")

# Limitar a 120 partidas (para nao gastar muitas requisicoes)
if len(all_fixtures) > 120:
    print(f"Limitando a 120 partidas mais recentes...")
    all_fixtures = sorted(all_fixtures, key=lambda x: x['fixture']['date'], reverse=True)[:120]

print(f"\nAnalisando {len(all_fixtures)} partidas...")
print("="*80 + "\n")

# Processar partidas
results = []
failed = []
processed = 0

for i, f in enumerate(all_fixtures, 1):
    fid = f['fixture']['id']
    home = f['teams']['home']['name']
    away = f['teams']['away']['name']
    h_score = f['goals']['home']
    a_score = f['goals']['away']
    league = f['league']['name']
    
    # Progresso a cada 10
    if i % 10 == 0 or i == 1:
        print(f"[{i}/{len(all_fixtures)}] Processando...")
    
    try:
        # Enriquecer
        enriched = enricher.enrich({'api_id': fid})
        
        # Features
        features = fe.engineer_all_features(enriched)
        
        # Modelo
        strength = features.get('strength', {})
        weather = features.get('weather', {})
        h_str = strength.get('home_goals_per_game', 1.2)
        a_str = strength.get('away_goals_per_game', 1.2)
        w_imp = weather.get('goal_impact', 0.0)
        
        model_result = ensemble.predict(features, h_str, a_str, w_imp)
        probs = model_result.get('consensus', {})
        
        if not probs or sum(probs.values()) == 0:
            failed.append({'id': fid, 'reason': 'sem_probabilidades'})
            continue
        
        actual = get_actual(h_score, a_score)
        pred = predict(probs)
        is_correct = correct(pred, actual)
        b = brier(probs, actual)
        ll = log_loss(probs, actual)
        
        results.append({
            'id': fid,
            'home': home,
            'away': away,
            'score': f"{h_score}-{a_score}",
            'league': league,
            'predicted': pred,
            'actual': actual,
            'correct': is_correct,
            'brier': b,
            'log_loss': ll,
            'probs': probs,
            'date': f['fixture']['date']
        })
        
        processed += 1
        
    except Exception as e:
        failed.append({'id': fid, 'reason': str(e)[:50]})

print(f"\n{'='*80}")
print("PROCESSAMENTO CONCLUIDO")
print("="*80)
print(f"Partidas analisadas: {processed}")
print(f"Falhas: {len(failed)}")
print(f"Taxa de sucesso: {processed/(processed+len(failed))*100:.1f}%\n")

if processed < 50:
    print("ERRO: Poucas partidas analisadas com sucesso")
    print("Nao e possivel gerar relatorio confiavel")
    sys.exit(1)

# Calcular metricas gerais
acc = sum(1 for r in results if r['correct']) / len(results) * 100
avg_brier = np.mean([r['brier'] for r in results])
avg_ll = np.mean([r['log_loss'] for r in results])

# Metricas por tipo de resultado
home_wins = [r for r in results if r['actual'] == [1,0,0]]
draws = [r for r in results if r['actual'] == [0,1,0]]
away_wins = [r for r in results if r['actual'] == [0,0,1]]

acc_home = sum(1 for r in home_wins if r['correct']) / len(home_wins) * 100 if home_wins else 0
acc_draw = sum(1 for r in draws if r['correct']) / len(draws) * 100 if draws else 0
acc_away = sum(1 for r in away_wins if r['correct']) / len(away_wins) * 100 if away_wins else 0

# Metricas por liga
leagues = {}
for r in results:
    lg = r['league']
    if lg not in leagues:
        leagues[lg] = []
    leagues[lg].append(r)

# Relatorio
print("="*80)
print("RELATORIO COMPLETO DE VALIDACAO")
print("="*80 + "\n")

print("METRICAS GERAIS")
print("-"*80)
print(f"Total de partidas:       {len(results)}")
print(f"Periodo:                 Ultimos 7-14 dias")
print(f"\nACERTIVIDADE GERAL:      {acc:.1f}%")
print(f"Brier Score (medio):     {avg_brier:.4f}")
print(f"Log Loss (medio):        {avg_ll:.4f}")
print(f"\nBaseline (aleatorio):    33.3%")
print(f"Melhoria sobre baseline: {(acc-33.3)/33.3*100:+.1f}%")

print("\n" + "-"*80)
print("ACERTIVIDADE POR TIPO DE RESULTADO")
print("-"*80)
print(f"Vitorias Casa:  {acc_home:.1f}% ({sum(1 for r in home_wins if r['correct'])}/{len(home_wins)})")
print(f"Empates:        {acc_draw:.1f}% ({sum(1 for r in draws if r['correct'])}/{len(draws)})")
print(f"Vitorias Fora:  {acc_away:.1f}% ({sum(1 for r in away_wins if r['correct'])}/{len(away_wins)})")

print("\n" + "-"*80)
print("DISTRIBUICAO DE RESULTADOS REAIS")
print("-"*80)
print(f"Vitorias Casa:  {len(home_wins)} ({len(home_wins)/len(results)*100:.1f}%)")
print(f"Empates:        {len(draws)} ({len(draws)/len(results)*100:.1f}%)")
print(f"Vitorias Fora:  {len(away_wins)} ({len(away_wins)/len(results)*100:.1f}%)")

# Top 5 ligas por volume
print("\n" + "-"*80)
print("TOP 10 LIGAS (por volume)")
print("-"*80)
sorted_leagues = sorted(leagues.items(), key=lambda x: len(x[1]), reverse=True)[:10]
for lg, matches in sorted_leagues:
    lg_acc = sum(1 for m in matches if m['correct']) / len(matches) * 100
    lg_brier = np.mean([m['brier'] for m in matches])
    print(f"{lg[:40]:40} | {len(matches):3} partidas | Acc: {lg_acc:5.1f}% | Brier: {lg_brier:.3f}")

# Calibracao por faixa de confianca
print("\n" + "-"*80)
print("CALIBRACAO (confianca vs acertividade)")
print("-"*80)

conf_ranges = [
    (0.33, 0.40, "Muito Baixa (33-40%)"),
    (0.40, 0.50, "Baixa (40-50%)"),
    (0.50, 0.60, "Media (50-60%)"),
    (0.60, 0.70, "Alta (60-70%)"),
    (0.70, 1.00, "Muito Alta (70%+)")
]

for min_c, max_c, label in conf_ranges:
    in_range = []
    for r in results:
        max_prob = max(r['probs']['home_win'], r['probs']['draw'], r['probs']['away_win'])
        if min_c <= max_prob < max_c:
            in_range.append(r)
    
    if in_range:
        range_acc = sum(1 for r in in_range if r['correct']) / len(in_range) * 100
        avg_conf = np.mean([max(r['probs']['home_win'], r['probs']['draw'], r['probs']['away_win']) for r in in_range])
        print(f"{label:20} | {len(in_range):3} partidas | Acc: {range_acc:5.1f}% | Conf media: {avg_conf*100:5.1f}%")

# Benchmarks
print("\n" + "="*80)
print("AVALIACAO FINAL")
print("="*80 + "\n")

criteria = []
warnings = []
issues = []

# Criterio 1: Acertividade
if acc >= 50:
    criteria.append(f"EXCELENTE: Acertividade de {acc:.1f}% (meta: 45%+)")
elif acc >= 45:
    criteria.append(f"BOM: Acertividade de {acc:.1f}% atinge meta minima")
elif acc >= 40:
    warnings.append(f"ATENCAO: Acertividade de {acc:.1f}% esta no limite (meta: 45%+)")
else:
    issues.append(f"INSUFICIENTE: Acertividade de {acc:.1f}% abaixo do aceitavel")

# Criterio 2: Brier Score
if avg_brier <= 0.20:
    criteria.append(f"EXCELENTE: Brier Score {avg_brier:.4f} (meta: <0.25)")
elif avg_brier <= 0.25:
    criteria.append(f"BOM: Brier Score {avg_brier:.4f} dentro da meta")
else:
    warnings.append(f"ATENCAO: Brier Score {avg_brier:.4f} acima da meta (0.25)")

# Criterio 3: Log Loss
if avg_ll <= 0.70:
    criteria.append(f"EXCELENTE: Log Loss {avg_ll:.4f} (meta: <1.00)")
elif avg_ll <= 1.00:
    criteria.append(f"BOM: Log Loss {avg_ll:.4f} dentro da meta")
else:
    warnings.append(f"ATENCAO: Log Loss {avg_ll:.4f} acima da meta (1.00)")

# Criterio 4: Amostra
if len(results) >= 100:
    criteria.append(f"EXCELENTE: Amostra robusta com {len(results)} partidas")
elif len(results) >= 50:
    warnings.append(f"ATENCAO: Amostra limitada com {len(results)} partidas (ideal: 100+)")
else:
    issues.append(f"INSUFICIENTE: Amostra de apenas {len(results)} partidas")

# Criterio 5: Taxa de sucesso
success_rate = processed / (processed + len(failed)) * 100
if success_rate >= 90:
    criteria.append(f"EXCELENTE: Taxa de processamento {success_rate:.1f}%")
elif success_rate >= 70:
    warnings.append(f"ATENCAO: Taxa de processamento {success_rate:.1f}% (ideal: 90%+)")
else:
    issues.append(f"PROBLEMA: Taxa de processamento baixa ({success_rate:.1f}%)")

# Mostrar resultados
print("PONTOS POSITIVOS:")
for c in criteria:
    print(f"  + {c}")

if warnings:
    print("\nPONTOS DE ATENCAO:")
    for w in warnings:
        print(f"  ! {w}")

if issues:
    print("\nPROBLEMAS CRITICOS:")
    for iss in issues:
        print(f"  X {iss}")

# Conclusao final
print("\n" + "="*80)
score = len(criteria) - len(issues)

if score >= 4 and len(issues) == 0:
    print("CONCLUSAO: APROVADO PARA LANCAMENTO COMERCIAL")
    print("\nO modelo demonstra:")
    print("- Acertividade consistente acima de 45%")
    print("- Excelente calibracao de probabilidades")
    print("- Performance superior em diversas ligas")
    print("\nRecomendacao: PRONTO para operacao comercial")
elif score >= 2 and len(issues) <= 1:
    print("CONCLUSAO: APROVADO COM RESSALVAS")
    print("\nO modelo apresenta bons resultados mas necessita:")
    print("- Monitoramento continuo de performance")
    print("- Ajustes incrementais conforme feedback")
    print("\nRecomendacao: Lancamento em fase BETA")
else:
    print("CONCLUSAO: NECESSITA MAIS DESENVOLVIMENTO")
    print("\nO modelo ainda nao atingiu criterios minimos")
    print("\nRecomendacao: Aprimoramento antes de lancamento")

print("="*80 + "\n")

# Salvar resultados detalhados
output_file = f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'summary': {
            'total_matches': len(results),
            'accuracy': acc,
            'brier_score': avg_brier,
            'log_loss': avg_ll,
            'processed': processed,
            'failed': len(failed)
        },
        'by_result_type': {
            'home_wins': {'count': len(home_wins), 'accuracy': acc_home},
            'draws': {'count': len(draws), 'accuracy': acc_draw},
            'away_wins': {'count': len(away_wins), 'accuracy': acc_away}
        },
        'detailed_results': results,
        'failed_matches': failed
    }, f, indent=2, ensure_ascii=False)

print(f"Resultados detalhados salvos em: {output_file}\n")
