"""
Analisa quais padroes o ContextAnalyzer esta detectando
e se fazem sentido com os resultados reais
"""

import os
import django
import json
from datetime import datetime
from collections import defaultdict, Counter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.statistical_models import PoissonBivariateModel
from apps.analysis.services.context_analyzer import ContextAnalyzer
from django.db.models import Q


def calculate_actual_result(home_score, away_score):
    """Retorna caracteristicas do resultado real."""
    total = home_score + away_score
    
    return {
        'total_goals': total,
        'is_balanced': abs(home_score - away_score) <= 1,
        'is_low_scoring': total < 2.5,
        'is_high_scoring': total > 2.5,
        'btts': home_score > 0 and away_score > 0,
        'result': 'home' if home_score > away_score else ('draw' if home_score == away_score else 'away'),
        'margin': abs(home_score - away_score)
    }


def main():
    print("="*80)
    print("ANALISE DE PADROES CONTEXTUAIS")
    print("="*80)
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}\n")
    
    # Buscar partidas
    matches = Match.objects.filter(
        Q(status='finished') | Q(status='FT')
    ).exclude(
        home_score__isnull=True
    ).exclude(
        away_score__isnull=True
    ).select_related('home_team', 'away_team', 'league')[:100]
    
    total = matches.count()
    print(f"Partidas: {total}\n")
    
    # Inicializar
    poisson = PoissonBivariateModel()
    context_analyzer = ContextAnalyzer()
    
    # Estatisticas
    pattern_stats = defaultdict(lambda: {
        'count': 0,
        'correct_predictions': {
            'low_scoring': 0,
            'high_scoring': 0,
            'btts_yes': 0,
            'btts_no': 0,
            'balanced': 0,
            'home_win': 0,
            'away_win': 0
        },
        'total_games': 0,
        'actual_characteristics': Counter()
    })
    
    all_patterns = Counter()
    confidence_levels = []
    
    print("Analisando padroes detectados...\n")
    
    for idx, match in enumerate(matches, 1):
        # Contexto generico
        match_context = {
            'importance': 'medium',
            'rest_context': {'advantage': 'equal'},
            'motivation': {'home': 'medium', 'away': 'medium'},
            'weather': None,
            'standings': {'home_position': 10, 'away_position': 10}
        }
        
        # Detectar padroes
        context_result = context_analyzer.analyze(match_context)
        patterns = context_result.get('patterns', [])
        
        # Resultado real
        actual = calculate_actual_result(match.home_score, match.away_score)
        
        # Estatisticas por padrao
        for pattern_data in patterns:
            pattern_name = pattern_data['name']
            confidence = pattern_data['confidence']
            favored_markets = pattern_data['favorable_markets']
            
            all_patterns[pattern_name] += 1
            confidence_levels.append(confidence)
            
            stats = pattern_stats[pattern_name]
            stats['count'] += 1
            stats['total_games'] += 1
            
            # Verificar se as previsoes do padrao estavam corretas
            if 'under_2.5' in favored_markets and actual['is_low_scoring']:
                stats['correct_predictions']['low_scoring'] += 1
            
            if 'over_2.5' in favored_markets and actual['is_high_scoring']:
                stats['correct_predictions']['high_scoring'] += 1
            
            if 'btts_yes' in favored_markets and actual['btts']:
                stats['correct_predictions']['btts_yes'] += 1
            
            if 'btts_no' in favored_markets and not actual['btts']:
                stats['correct_predictions']['btts_no'] += 1
            
            if 'draw' in favored_markets and actual['result'] == 'draw':
                stats['correct_predictions']['balanced'] += 1
            
            if 'home_win' in favored_markets and actual['result'] == 'home':
                stats['correct_predictions']['home_win'] += 1
            
            if 'away_win' in favored_markets and actual['result'] == 'away':
                stats['correct_predictions']['away_win'] += 1
            
            # Caracteristicas reais quando este padrao foi detectado
            stats['actual_characteristics']['low_scoring'] += 1 if actual['is_low_scoring'] else 0
            stats['actual_characteristics']['high_scoring'] += 1 if actual['is_high_scoring'] else 0
            stats['actual_characteristics']['btts'] += 1 if actual['btts'] else 0
            stats['actual_characteristics']['balanced'] += 1 if actual['is_balanced'] else 0
    
    # Resultados
    print("="*80)
    print("PADROES DETECTADOS")
    print("="*80)
    print(f"\nTotal de padroes diferentes: {len(all_patterns)}\n")
    
    for pattern, count in all_patterns.most_common():
        print(f"[{count:3d}x] {pattern}")
    
    print("\n" + "="*80)
    print("ANALISE POR PADRAO")
    print("="*80)
    
    for pattern_name in sorted(pattern_stats.keys()):
        stats = pattern_stats[pattern_name]
        print(f"\n{'='*80}")
        print(f"PADRAO: {pattern_name}")
        print(f"{'='*80}")
        print(f"Detectado em: {stats['count']} partidas")
        
        print(f"\nCaracteristicas REAIS quando este padrao foi detectado:")
        total_detections = stats['total_games']
        for char, count in stats['actual_characteristics'].items():
            pct = (count / total_detections * 100) if total_detections > 0 else 0
            print(f"  {char:20s}: {count:3d}/{total_detections} ({pct:5.1f}%)")
        
        print(f"\nPrevisoes CORRETAS do padrao:")
        correct_preds = stats['correct_predictions']
        total_correct = sum(correct_preds.values())
        print(f"  Total acertos: {total_correct}")
        for pred_type, count in correct_preds.items():
            if count > 0:
                print(f"  {pred_type:20s}: {count:3d} acertos")
    
    # Confianca media
    if confidence_levels:
        avg_confidence = sum(confidence_levels) / len(confidence_levels)
        print("\n" + "="*80)
        print(f"CONFIANCA MEDIA DOS PADROES: {avg_confidence:.1f}%")
        print("="*80)
    
    # Salvar
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_matches': total,
        'patterns_detected': dict(all_patterns),
        'avg_confidence': avg_confidence if confidence_levels else 0,
        'pattern_analysis': {
            pattern: {
                'count': stats['count'],
                'actual_characteristics': dict(stats['actual_characteristics']),
                'correct_predictions': dict(stats['correct_predictions'])
            }
            for pattern, stats in pattern_stats.items()
        }
    }
    
    fname = f'pattern_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SAVE] {fname}")
    
    # Conclusoes
    print("\n" + "="*80)
    print("CONCLUSOES")
    print("="*80)
    
    # Verificar se balanced_tight_game realmente identifica jogos equilibrados
    if 'balanced_tight_game' in pattern_stats:
        btg_stats = pattern_stats['balanced_tight_game']
        balanced_rate = (btg_stats['actual_characteristics']['balanced'] / btg_stats['total_games'] * 100)
        low_scoring_rate = (btg_stats['actual_characteristics']['low_scoring'] / btg_stats['total_games'] * 100)
        
        print(f"\n'balanced_tight_game' detectado {btg_stats['count']}x:")
        print(f"  Realmente equilibrado: {balanced_rate:.1f}%")
        print(f"  Realmente low scoring: {low_scoring_rate:.1f}%")
        
        if balanced_rate < 50:
            print("  [!] PROBLEMA: Nao esta detectando jogos equilibrados corretamente!")
        if low_scoring_rate < 50:
            print("  [!] PROBLEMA: Nao esta detectando low scoring corretamente!")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
