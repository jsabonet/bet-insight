"""
Analise detalhada dos erros de validacao para identificar padroes
"""
import json
import os
from collections import defaultdict
from datetime import datetime

# Encontrar arquivo mais recente
files = [f for f in os.listdir('.') if f.startswith('validation_results_')]
if not files:
    print("Nenhum arquivo de validacao encontrado")
    exit(1)

latest = sorted(files, reverse=True)[0]
print(f"\nAnalisando: {latest}\n")

with open(latest, 'r', encoding='utf-8') as f:
    data = json.load(f)

results = data['detailed_results']
summary = data['summary']

print("="*80)
print("ANALISE DETALHADA DE ERROS - IDENTIFICACAO DE PADROES")
print("="*80)

print(f"\nResumo Geral:")
print(f"  Total: {summary['total_matches']} partidas")
print(f"  Acertividade: {summary['accuracy']:.1f}%")
print(f"  Brier Score: {summary['brier_score']:.4f}")
print(f"  Log Loss: {summary['log_loss']:.4f}")

# 1. ANALISE POR TIPO DE RESULTADO
print("\n" + "="*80)
print("1. ACERTIVIDADE POR TIPO DE RESULTADO REAL")
print("="*80)

by_actual = defaultdict(lambda: {'total': 0, 'correct': 0})
for r in results:
    actual = r['actual']
    if actual == [1, 0, 0]:
        result_type = 'Vitoria Casa'
    elif actual == [0, 1, 0]:
        result_type = 'Empate'
    elif actual == [0, 0, 1]:
        result_type = 'Vitoria Fora'
    else:
        continue
    
    by_actual[result_type]['total'] += 1
    if r['correct']:
        by_actual[result_type]['correct'] += 1

for result_type in ['Vitoria Casa', 'Empate', 'Vitoria Fora']:
    stats = by_actual[result_type]
    if stats['total'] > 0:
        acc = stats['correct'] / stats['total'] * 100
        print(f"{result_type:15s}: {acc:5.1f}% ({stats['correct']:2d}/{stats['total']:2d})")

# 2. ANALISE POR PREDICAO
print("\n" + "="*80)
print("2. ACERTIVIDADE POR TIPO DE PREDICAO")
print("="*80)

by_pred = defaultdict(lambda: {'total': 0, 'correct': 0})
pred_map = {'home_win': 'Prever Casa', 'draw': 'Prever Empate', 'away_win': 'Prever Fora'}

for r in results:
    pred_label = pred_map.get(r['predicted'], 'Desconhecido')
    by_pred[pred_label]['total'] += 1
    if r['correct']:
        by_pred[pred_label]['correct'] += 1

for pred_type in ['Prever Casa', 'Prever Empate', 'Prever Fora']:
    stats = by_pred[pred_type]
    if stats['total'] > 0:
        acc = stats['correct'] / stats['total'] * 100
        print(f"{pred_type:15s}: {acc:5.1f}% ({stats['correct']:2d}/{stats['total']:2d})")

# 3. ANALISE POR LIGA
print("\n" + "="*80)
print("3. ACERTIVIDADE POR LIGA (TOP 10)")
print("="*80)

by_league = defaultdict(lambda: {'total': 0, 'correct': 0, 'brier': []})
for r in results:
    league = r['league']
    by_league[league]['total'] += 1
    if r['correct']:
        by_league[league]['correct'] += 1
    by_league[league]['brier'].append(r['brier'])

# Ordenar por quantidade
sorted_leagues = sorted(by_league.items(), key=lambda x: x[1]['total'], reverse=True)[:10]

for league, stats in sorted_leagues:
    acc = stats['correct'] / stats['total'] * 100
    avg_brier = sum(stats['brier']) / len(stats['brier'])
    print(f"{league:25s}: {acc:5.1f}% ({stats['correct']:2d}/{stats['total']:2d}) | Brier: {avg_brier:.3f}")

# 4. ANALISE POR NIVEL DE CONFIANCA
print("\n" + "="*80)
print("4. CALIBRACAO POR NIVEL DE CONFIANCA")
print("="*80)

confidence_ranges = [
    (0.33, 0.40, "Baixa (33-40%)"),
    (0.40, 0.50, "Media-Baixa (40-50%)"),
    (0.50, 0.60, "Media (50-60%)"),
    (0.60, 0.70, "Alta (60-70%)"),
    (0.70, 1.00, "Muito Alta (70%+)")
]

for min_conf, max_conf, label in confidence_ranges:
    in_range = []
    for r in results:
        probs = r['probs']
        if probs:
            max_prob = max(probs.get('home_win', 0), probs.get('draw', 0), probs.get('away_win', 0))
            if min_conf <= max_prob < max_conf:
                in_range.append(r)
    
    if in_range:
        correct = sum(1 for r in in_range if r['correct'])
        acc = correct / len(in_range) * 100
        avg_conf = sum(max(r['probs'].get('home_win', 0), r['probs'].get('draw', 0), r['probs'].get('away_win', 0)) for r in in_range) / len(in_range)
        print(f"{label:20s}: {acc:5.1f}% acerto | Conf media: {avg_conf*100:5.1f}% | {len(in_range):3d} partidas")

# 5. VIES CASA vs FORA
print("\n" + "="*80)
print("5. ANALISE DE VIES (CASA vs FORA)")
print("="*80)

home_predictions = sum(1 for r in results if r['predicted'] == 'home_win')
away_predictions = sum(1 for r in results if r['predicted'] == 'away_win')
draw_predictions = sum(1 for r in results if r['predicted'] == 'draw')

home_actual = sum(1 for r in results if r['actual'] == [1, 0, 0])
away_actual = sum(1 for r in results if r['actual'] == [0, 0, 1])
draw_actual = sum(1 for r in results if r['actual'] == [0, 1, 0])

total = len(results)

print(f"\nPREDICOES do Modelo:")
print(f"  Casa:   {home_predictions:3d} ({home_predictions/total*100:5.1f}%)")
print(f"  Empate: {draw_predictions:3d} ({draw_predictions/total*100:5.1f}%)")
print(f"  Fora:   {away_predictions:3d} ({away_predictions/total*100:5.1f}%)")

print(f"\nRESULTADOS Reais:")
print(f"  Casa:   {home_actual:3d} ({home_actual/total*100:5.1f}%)")
print(f"  Empate: {draw_actual:3d} ({draw_actual/total*100:5.1f}%)")
print(f"  Fora:   {away_actual:3d} ({away_actual/total*100:5.1f}%)")

print(f"\nDIFERENCAS (Modelo - Real):")
print(f"  Casa:   {(home_predictions/total - home_actual/total)*100:+6.1f} pontos")
print(f"  Empate: {(draw_predictions/total - draw_actual/total)*100:+6.1f} pontos")
print(f"  Fora:   {(away_predictions/total - away_actual/total)*100:+6.1f} pontos")

# 6. ERROS MAIS GRAVES
print("\n" + "="*80)
print("6. TOP 10 ERROS MAIS GRAVES (maior Brier Score)")
print("="*80)

worst_errors = sorted([r for r in results if not r['correct']], 
                     key=lambda x: x['brier'], reverse=True)[:10]

for i, r in enumerate(worst_errors, 1):
    pred_map_detail = {'home_win': 'Casa', 'draw': 'Empate', 'away_win': 'Fora'}
    actual_map = {str([1,0,0]): 'Casa', str([0,1,0]): 'Empate', str([0,0,1]): 'Fora'}
    
    pred = pred_map_detail.get(r['predicted'], '?')
    actual = actual_map.get(str(r['actual']), '?')
    
    print(f"{i:2d}. {r['home']:20s} {r['score']:5s} {r['away']:20s}")
    print(f"    Previsto: {pred} | Real: {actual} | Brier: {r['brier']:.3f} | Liga: {r['league']}")

# 7. SUGESTOES DE MELHORIA
print("\n" + "="*80)
print("7. DIAGNOSTICO E SUGESTOES")
print("="*80)

issues = []
suggestions = []

# Analisar acertividade por tipo
home_acc = by_actual['Vitoria Casa']['correct'] / by_actual['Vitoria Casa']['total'] * 100 if by_actual['Vitoria Casa']['total'] > 0 else 0
draw_acc = by_actual['Empate']['correct'] / by_actual['Empate']['total'] * 100 if by_actual['Empate']['total'] > 0 else 0
away_acc = by_actual['Vitoria Fora']['correct'] / by_actual['Vitoria Fora']['total'] * 100 if by_actual['Vitoria Fora']['total'] > 0 else 0

if draw_acc < 20:
    issues.append(f"Baixa acertividade em empates ({draw_acc:.1f}%)")
    suggestions.append("Aumentar peso para empates no modelo ou ajustar threshold")

if abs(home_predictions/total - home_actual/total) > 0.15:
    vies = "superestima" if home_predictions > home_actual else "subestima"
    issues.append(f"Modelo {vies} vitorias da casa")
    suggestions.append("Ajustar home advantage factor ou pesos de forma")

if summary['log_loss'] > 1.0:
    issues.append(f"Log Loss alto ({summary['log_loss']:.2f}) indica excesso de confianca")
    suggestions.append("Suavizar probabilidades (temperature scaling) ou ajustar pesos do ensemble")

# Verificar calibracao
for min_conf, max_conf, label in confidence_ranges:
    in_range = [r for r in results if r['probs'] and min_conf <= max(r['probs'].get('home_win', 0), r['probs'].get('draw', 0), r['probs'].get('away_win', 0)) < max_conf]
    if len(in_range) > 10:
        correct = sum(1 for r in in_range if r['correct'])
        acc = correct / len(in_range)
        avg_conf = sum(max(r['probs'].get('home_win', 0), r['probs'].get('draw', 0), r['probs'].get('away_win', 0)) for r in in_range) / len(in_range)
        if abs(acc - avg_conf) > 0.15:
            issues.append(f"Desalinhamento em {label}: {avg_conf*100:.1f}% confianca vs {acc*100:.1f}% acerto")
            suggestions.append(f"Recalibrar probabilidades na faixa {label}")

print("\nPROBLEMAS IDENTIFICADOS:")
for i, issue in enumerate(issues, 1):
    print(f"  {i}. {issue}")

print("\nSUGESTOES DE MELHORIA:")
for i, sugg in enumerate(suggestions, 1):
    print(f"  {i}. {sugg}")

# 8. PRIORIZACAO
print("\n" + "="*80)
print("8. ACOES PRIORITARIAS")
print("="*80)

priorities = []

if summary['accuracy'] < 40:
    priorities.append(("CRITICO", "Acertividade global abaixo de 40% - revisar features e pesos"))

if summary['log_loss'] > 1.2:
    priorities.append(("ALTA", "Implementar temperature scaling para reduzir excesso de confianca"))

if draw_acc < 15:
    priorities.append(("ALTA", "Melhorar predicao de empates - considerar features especificas"))

if abs(home_predictions/total - home_actual/total) > 0.20:
    priorities.append(("MEDIA", "Corrigir vies casa/fora - ajustar home advantage"))

priorities.append(("MEDIA", "Testar diferentes pesos no ensemble (atual: 60% Poisson, 40% Logistica)"))
priorities.append(("BAIXA", "Expandir validacao para incluir diferentes periodos da temporada"))

for priority, action in priorities:
    print(f"  [{priority:8s}] {action}")

print("\n" + "="*80 + "\n")
