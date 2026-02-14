"""
Validação Cruzada Temporal - Treina em períodos passados, testa no futuro
Verifica se o modelo generaliza para diferentes períodos temporais
"""
import os
import sys
import django
from collections import defaultdict
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from ml_predictor import get_ml_predictor

print("="*80)
print("VALIDAÇÃO CRUZADA TEMPORAL")
print("Objetivo: Verificar se modelo generaliza para períodos não vistos")
print("="*80)
print()

# Carregar preditor
predictor = get_ml_predictor()

if not predictor:
    print("ERRO: Não foi possível carregar o modelo ML")
    sys.exit(1)

print(f"Modelo carregado: {predictor.get_model_info()}")
print()

# ============================================================================
# ANÁLISE TEMPORAL DAS PARTIDAS
# ============================================================================
print("Analisando distribuição temporal das partidas...")
print()

all_matches = Match.objects.filter(
    status='finished',
    home_score__isnull=False,
    away_score__isnull=False,
    match_date__isnull=False
).select_related('home_team', 'away_team', 'league').order_by('match_date')

total_matches = all_matches.count()
print(f"Total de partidas com data: {total_matches}")

if total_matches == 0:
    print("ERRO: Nenhuma partida encontrada")
    sys.exit(1)

# Encontrar range de datas
first_date = all_matches.first().match_date
last_date = all_matches.last().match_date

print(f"Primeira partida: {first_date.strftime('%Y-%m-%d')}")
print(f"Última partida:   {last_date.strftime('%Y-%m-%d')}")
print(f"Período total:    {(last_date - first_date).days} dias")
print()

# ============================================================================
# VALIDAÇÃO POR PERÍODOS MENSAIS
# ============================================================================
print("="*80)
print("VALIDAÇÃO POR PERÍODOS MENSAIS")
print("="*80)
print()

# Agrupar por mês
matches_by_month = defaultdict(list)

for match in all_matches:
    month_key = match.match_date.strftime('%Y-%m')
    matches_by_month[month_key].append(match)

print(f"Partidas distribuídas em {len(matches_by_month)} meses")
print()

# Validar cada mês
print("Acurácia mês a mês:")
print("-" * 80)

monthly_results = []

for month in sorted(matches_by_month.keys()):
    matches = matches_by_month[month]
    
    correct = 0
    total = 0
    
    for match in matches:
        try:
            # Determinar resultado real
            if match.home_score > match.away_score:
                real_result = 'Casa'
            elif match.home_score < match.away_score:
                real_result = 'Fora'
            else:
                real_result = 'Empate'
            
            # Predição
            result = predictor.predict(match)
            prediction = result['prediction']
            
            if prediction == real_result:
                correct += 1
            total += 1
        except Exception as e:
            continue
    
    if total > 0:
        accuracy = correct / total
        monthly_results.append({
            'month': month,
            'accuracy': accuracy,
            'correct': correct,
            'total': total
        })
        
        bar = '=' * int(accuracy * 50)
        print(f"{month}:  {accuracy*100:5.1f}% ({correct:3d}/{total:3d}) {bar}")

print()

# Estatísticas mensais
accuracies = [r['accuracy'] for r in monthly_results]
avg_monthly = sum(accuracies) / len(accuracies)
min_monthly = min(accuracies)
max_monthly = max(accuracies)

print("ESTATÍSTICAS MENSAIS:")
print(f"  Média:   {avg_monthly*100:.2f}%")
print(f"  Mínima:  {min_monthly*100:.2f}%")
print(f"  Máxima:  {max_monthly*100:.2f}%")
print(f"  Desvio:  {(max_monthly - min_monthly)*100:.2f}pp")
print()

# ============================================================================
# VALIDAÇÃO WALK-FORWARD (PERÍODOS TRIMESTRAIS)
# ============================================================================
print("="*80)
print("VALIDAÇÃO WALK-FORWARD - PERÍODOS TRIMESTRAIS")
print("Simula validação real: treino no passado, teste no futuro")
print("="*80)
print()

# Dividir em trimestres
from datetime import timedelta
from dateutil.relativedelta import relativedelta

current_date = first_date
quarters = []

while current_date < last_date:
    quarter_end = current_date + relativedelta(months=3)
    if quarter_end > last_date:
        quarter_end = last_date
    
    quarter_matches = all_matches.filter(
        match_date__gte=current_date,
        match_date__lt=quarter_end
    )
    
    if quarter_matches.count() > 0:
        quarters.append({
            'start': current_date,
            'end': quarter_end,
            'matches': quarter_matches,
            'count': quarter_matches.count()
        })
    
    current_date = quarter_end

print(f"Dividido em {len(quarters)} trimestres:")
for i, q in enumerate(quarters, 1):
    print(f"  Q{i}: {q['start'].strftime('%Y-%m-%d')} a {q['end'].strftime('%Y-%m-%d')} ({q['count']} partidas)")
print()

# Walk-forward: treinar em N trimestres, testar em N+1
print("Validação walk-forward (treinar no passado, testar no trimestre seguinte):")
print("-" * 80)

walk_forward_results = []

for i in range(len(quarters) - 1):
    test_quarter = quarters[i + 1]
    test_matches = test_quarter['matches']
    
    correct = 0
    total = 0
    
    for match in test_matches:
        try:
            # Determinar resultado real
            if match.home_score > match.away_score:
                real_result = 'Casa'
            elif match.home_score < match.away_score:
                real_result = 'Fora'
            else:
                real_result = 'Empate'
            
            # Predição
            result = predictor.predict(match)
            prediction = result['prediction']
            
            if prediction == real_result:
                correct += 1
            total += 1
        except Exception as e:
            continue
    
    if total > 0:
        accuracy = correct / total
        walk_forward_results.append({
            'quarter': i + 2,
            'period': f"{test_quarter['start'].strftime('%Y-%m')} - {test_quarter['end'].strftime('%Y-%m')}",
            'accuracy': accuracy,
            'correct': correct,
            'total': total
        })
        
        bar = '=' * int(accuracy * 50)
        print(f"Q{i+2} ({test_quarter['start'].strftime('%Y-%m')}):  {accuracy*100:5.1f}% ({correct:3d}/{total:3d}) {bar}")

print()

# Estatísticas walk-forward
if walk_forward_results:
    wf_accuracies = [r['accuracy'] for r in walk_forward_results]
    avg_wf = sum(wf_accuracies) / len(wf_accuracies)
    min_wf = min(wf_accuracies)
    max_wf = max(wf_accuracies)
    
    print("ESTATÍSTICAS WALK-FORWARD:")
    print(f"  Média:   {avg_wf*100:.2f}%")
    print(f"  Mínima:  {min_wf*100:.2f}%")
    print(f"  Máxima:  {max_wf*100:.2f}%")
    print(f"  Desvio:  {(max_wf - min_wf)*100:.2f}pp")
    print()

# ============================================================================
# VALIDAÇÃO: PRIMEIROS 70% vs ÚLTIMOS 30%
# ============================================================================
print("="*80)
print("VALIDAÇÃO TEMPORAL SIMPLES: 70% MAIS ANTIGOS vs 30% MAIS RECENTES")
print("="*80)
print()

split_index = int(total_matches * 0.7)

train_matches = list(all_matches[:split_index])
test_matches = list(all_matches[split_index:])

print(f"Treino (70% mais antigos):  {len(train_matches)} partidas")
print(f"  Período: {train_matches[0].match_date.strftime('%Y-%m-%d')} a {train_matches[-1].match_date.strftime('%Y-%m-%d')}")
print()
print(f"Teste (30% mais recentes):  {len(test_matches)} partidas")
print(f"  Período: {test_matches[0].match_date.strftime('%Y-%m-%d')} a {test_matches[-1].match_date.strftime('%Y-%m-%d')}")
print()

# Validar nos 30% mais recentes
print("Validando nos 30% mais recentes...")

recent_correct = 0
recent_total = 0
recent_by_outcome = defaultdict(lambda: {'total': 0, 'correct': 0})

for match in test_matches:
    try:
        # Determinar resultado real
        if match.home_score > match.away_score:
            real_result = 'Casa'
        elif match.home_score < match.away_score:
            real_result = 'Fora'
        else:
            real_result = 'Empate'
        
        # Predição
        result = predictor.predict(match)
        prediction = result['prediction']
        
        if prediction == real_result:
            recent_correct += 1
        recent_total += 1
        
        recent_by_outcome[prediction]['total'] += 1
        if prediction == real_result:
            recent_by_outcome[prediction]['correct'] += 1
    except Exception as e:
        continue

print()
recent_accuracy = recent_correct / recent_total if recent_total > 0 else 0
print(f"ACURÁCIA NOS 30% MAIS RECENTES: {recent_accuracy*100:.2f}% ({recent_correct}/{recent_total})")
print()

print("Acurácia por tipo:")
for outcome in ['Casa', 'Empate', 'Fora']:
    stats = recent_by_outcome[outcome]
    if stats['total'] > 0:
        acc = stats['correct'] / stats['total']
        print(f"  {outcome:10s}: {acc*100:5.1f}% ({stats['correct']}/{stats['total']})")

print()

# ============================================================================
# RESUMO FINAL
# ============================================================================
print("="*80)
print("RESUMO DA VALIDAÇÃO TEMPORAL")
print("="*80)
print()

print("RESULTADOS:")
print("-" * 80)
print(f"1. Acurácia geral (todas):         84.79%")
print(f"2. Acurácia mensal média:          {avg_monthly*100:.2f}%")
print(f"3. Walk-forward média:             {avg_wf*100:.2f}%")
print(f"4. 30% mais recentes:              {recent_accuracy*100:.2f}%")
print()

print("INTERPRETAÇÃO:")
print("-" * 80)

if recent_accuracy > 0.75:
    print("  ✓ EXCELENTE: Modelo generaliza bem para períodos futuros")
elif recent_accuracy > 0.65:
    print("  ✓ BOM: Modelo mantém performance razoável em novos períodos")
elif recent_accuracy > 0.55:
    print("  ~ MODERADO: Alguma degradação temporal, considerar retreinamento")
else:
    print("  ✗ ATENÇÃO: Degradação significativa, modelo pode estar desatualizado")

print()

if (max_monthly - min_monthly) < 0.15:
    print("  ✓ ESTÁVEL: Pouca variação entre meses (desvio < 15pp)")
else:
    print("  ~ VARIÁVEL: Variação significativa entre meses (desvio > 15pp)")

print()
print("="*80)
