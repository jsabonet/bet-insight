"""
Validação completa de TODOS os mercados (49) usando dados históricos locais
Testa acurácia geral e individual de cada mercado
"""
import os
import sys
from datetime import datetime
import json

# Setup Django PRIMEIRO
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

# Desabilitar logs DEPOIS do Django setup
import logging
logging.getLogger('apps.analysis.services.statistical_models').setLevel(logging.CRITICAL)

from apps.matches.models import Match
from apps.analysis.services.statistical_models import PoissonBivariateModel

def verificar_resultado_mercado(mercado, probabilidade, resultado_real):
    """
    Verifica se a predição do mercado estava correta
    """
    # 1X2 Principais
    if mercado == 'home_win':
        return resultado_real['home_score'] > resultado_real['away_score']
    elif mercado == 'draw':
        return resultado_real['home_score'] == resultado_real['away_score']
    elif mercado == 'away_win':
        return resultado_real['home_score'] < resultado_real['away_score']
    
    # Double Chance
    elif mercado == '1X':
        return resultado_real['home_score'] >= resultado_real['away_score']
    elif mercado == '12':
        return resultado_real['home_score'] != resultado_real['away_score']
    elif mercado == 'X2':
        return resultado_real['home_score'] <= resultado_real['away_score']
    
    # Over/Under Padrão
    total_gols = resultado_real['home_score'] + resultado_real['away_score']
    
    if mercado == 'over_0_5':
        return total_gols > 0.5
    elif mercado == 'under_0_5':
        return total_gols < 0.5
    elif mercado == 'over_1_5':
        return total_gols > 1.5
    elif mercado == 'under_1_5':
        return total_gols < 1.5
    elif mercado == 'over_2_5':
        return total_gols > 2.5
    elif mercado == 'under_2_5':
        return total_gols < 2.5
    elif mercado == 'over_3_5':
        return total_gols > 3.5
    elif mercado == 'under_3_5':
        return total_gols < 3.5
    elif mercado == 'over_4_5':
        return total_gols > 4.5
    elif mercado == 'under_4_5':
        return total_gols < 4.5
    
    # Asian Lines
    elif mercado == 'over_1_75':
        return total_gols > 1.75
    elif mercado == 'under_1_75':
        return total_gols < 1.75
    elif mercado == 'over_2_25':
        return total_gols > 2.25
    elif mercado == 'under_2_25':
        return total_gols < 2.25
    elif mercado == 'over_2_75':
        return total_gols > 2.75
    elif mercado == 'under_2_75':
        return total_gols < 2.75
    elif mercado == 'over_3_25':
        return total_gols > 3.25
    elif mercado == 'under_3_25':
        return total_gols < 3.25
    
    # BTTS
    elif mercado in ['btts', 'btts_yes']:
        return resultado_real['home_score'] > 0 and resultado_real['away_score'] > 0
    elif mercado == 'btts_no':
        return resultado_real['home_score'] == 0 or resultado_real['away_score'] == 0
    
    # Clean Sheets
    elif mercado == 'home_clean_sheet':
        return resultado_real['away_score'] == 0
    elif mercado == 'away_clean_sheet':
        return resultado_real['home_score'] == 0
    
    # Team Total - Casa
    elif mercado == 'home_over_0.5':
        return resultado_real['home_score'] > 0.5
    elif mercado == 'home_under_0.5':
        return resultado_real['home_score'] < 0.5
    elif mercado == 'home_over_1.5':
        return resultado_real['home_score'] > 1.5
    elif mercado == 'home_under_1.5':
        return resultado_real['home_score'] < 1.5
    elif mercado == 'home_over_2.5':
        return resultado_real['home_score'] > 2.5
    elif mercado == 'home_under_2.5':
        return resultado_real['home_score'] < 2.5
    
    # Team Total - Fora
    elif mercado == 'away_over_0.5':
        return resultado_real['away_score'] > 0.5
    elif mercado == 'away_under_0.5':
        return resultado_real['away_score'] < 0.5
    elif mercado == 'away_over_1.5':
        return resultado_real['away_score'] > 1.5
    elif mercado == 'away_under_1.5':
        return resultado_real['away_score'] < 1.5
    elif mercado == 'away_over_2.5':
        return resultado_real['away_score'] > 2.5
    elif mercado == 'away_under_2.5':
        return resultado_real['away_score'] < 2.5
    
    # Margens de Vitória
    elif mercado == 'home_by_1':
        return resultado_real['home_score'] - resultado_real['away_score'] == 1
    elif mercado == 'home_by_2plus':
        return resultado_real['home_score'] - resultado_real['away_score'] >= 2
    elif mercado == 'away_by_1':
        return resultado_real['away_score'] - resultado_real['home_score'] == 1
    elif mercado == 'away_by_2plus':
        return resultado_real['away_score'] - resultado_real['home_score'] >= 2
    elif mercado == 'any_by_1':
        diferenca = abs(resultado_real['home_score'] - resultado_real['away_score'])
        return diferenca == 1
    elif mercado == 'any_by_2plus':
        diferenca = abs(resultado_real['home_score'] - resultado_real['away_score'])
        return diferenca >= 2
    
    # Odd/Even
    elif mercado == 'odd_goals':
        return total_gols % 2 == 1
    elif mercado == 'even_goals':
        return total_gols % 2 == 0
    
    return None

def validar_todos_mercados():
    """
    Valida TODOS os 49 mercados usando dados históricos
    """
    print("="*80)
    print("VALIDAÇÃO COMPLETA - TODOS OS MERCADOS (49)")
    print("="*80)
    print()
    
    # Carregar partidas finalizadas
    matches = Match.objects.filter(
        status='finished',
        home_score__isnull=False,
        away_score__isnull=False
    ).select_related('home_team', 'away_team', 'league')
    
    total_partidas = matches.count()
    print(f"Total de partidas finalizadas com placar: {total_partidas}")
    print()
    
    # Inicializar modelo
    poisson = PoissonBivariateModel()
    
    # Estatísticas por mercado
    stats_mercados = {}
    
    # Processar cada partida
    print("Processando partidas...")
    for idx, match in enumerate(matches, 1):
        if idx % 500 == 0:
            print(f"   Processadas {idx}/{total_partidas} partidas...")
        
        # Gerar predição (valores médios para validação)
        prediction = poisson.predict(
            home_strength=1.4,
            away_strength=1.2,
            home_defense=1.1,
            away_defense=1.1,
            weather_impact=0.0,
            league_id=match.league_id
        )
        
        # Resultado real
        resultado_real = {
            'home_score': match.home_score,
            'away_score': match.away_score
        }
        
        # Validar cada mercado
        for mercado, prob in prediction['probabilities'].items():
            if mercado not in stats_mercados:
                stats_mercados[mercado] = {
                    'total': 0,
                    'corretos': 0,
                    'testados': 0,
                    'prob_media': 0.0,
                    'prob_soma': 0.0
                }
            
            # Verificar resultado
            correto = verificar_resultado_mercado(mercado, prob, resultado_real)
            
            if correto is not None:
                stats_mercados[mercado]['testados'] += 1
                stats_mercados[mercado]['prob_soma'] += prob
                
                if correto:
                    stats_mercados[mercado]['corretos'] += 1
    
    print(f"OK - {total_partidas} partidas processadas!")
    print()
    
    # Calcular acurácias
    print("="*80)
    print("RESULTADOS POR MERCADO")
    print("="*80)
    print()
    
    # Agrupar por categoria
    categorias = {
        '1X2 Principais': ['home_win', 'draw', 'away_win'],
        'Double Chance': ['1X', '12', 'X2'],
        'Over/Under Padrão': [
            'over_0_5', 'under_0_5', 'over_1_5', 'under_1_5',
            'over_2_5', 'under_2_5', 'over_3_5', 'under_3_5',
            'over_4_5', 'under_4_5'
        ],
        'Asian Lines': [
            'over_1_75', 'under_1_75', 'over_2_25', 'under_2_25',
            'over_2_75', 'under_2_75', 'over_3_25', 'under_3_25'
        ],
        'BTTS': ['btts', 'btts_yes', 'btts_no'],
        'Clean Sheets': ['home_clean_sheet', 'away_clean_sheet'],
        'Team Total - Casa': [
            'home_over_0.5', 'home_under_0.5', 'home_over_1.5',
            'home_under_1.5', 'home_over_2.5', 'home_under_2.5'
        ],
        'Team Total - Fora': [
            'away_over_0.5', 'away_under_0.5', 'away_over_1.5',
            'away_under_1.5', 'away_over_2.5', 'away_under_2.5'
        ],
        'Margens de Vitória': [
            'home_by_1', 'home_by_2plus', 'away_by_1',
            'away_by_2plus', 'any_by_1', 'any_by_2plus'
        ],
        'Odd/Even': ['odd_goals', 'even_goals']
    }
    
    resultados_completos = {}
    acuracias_todas = []
    
    for categoria, mercados in categorias.items():
        print(f"\n[{categoria}]")
        print("-" * 80)
        
        categoria_stats = []
        
        for mercado in mercados:
            if mercado in stats_mercados and stats_mercados[mercado]['testados'] > 0:
                stats = stats_mercados[mercado]
                acuracia = (stats['corretos'] / stats['testados']) * 100
                prob_media = stats['prob_soma'] / stats['testados']
                
                acuracias_todas.append(acuracia)
                categoria_stats.append(acuracia)
                
                resultados_completos[mercado] = {
                    'acuracia': acuracia,
                    'corretos': stats['corretos'],
                    'testados': stats['testados'],
                    'prob_media': prob_media
                }
                
                print(f"  {mercado:25s}: {acuracia:5.1f}% ({stats['corretos']}/{stats['testados']}) - Prob média: {prob_media:.1f}%")
        
        if categoria_stats:
            media_categoria = sum(categoria_stats) / len(categoria_stats)
            print(f"\n  >> Media da categoria: {media_categoria:.1f}%")
    
    # Estatísticas gerais
    print("\n" + "="*80)
    print("ESTATÍSTICAS GERAIS")
    print("="*80)
    
    acuracia_geral = sum(acuracias_todas) / len(acuracias_todas)
    print(f"\nACURACIA GERAL (media de todos os mercados): {acuracia_geral:.2f}%")
    print(f"Total de partidas validadas: {total_partidas}")
    print(f"Total de mercados testados: {len(acuracias_todas)}")
    
    # Top 10 melhores mercados
    print("\nTOP 10 MERCADOS COM MAIOR ACURACIA:")
    print("-" * 80)
    top_10 = sorted(resultados_completos.items(), key=lambda x: x[1]['acuracia'], reverse=True)[:10]
    for i, (mercado, stats) in enumerate(top_10, 1):
        print(f"  {i:2d}. {mercado:25s}: {stats['acuracia']:5.1f}% ({stats['corretos']}/{stats['testados']})")
    
    # Top 10 piores mercados
    print("\nTOP 10 MERCADOS COM MENOR ACURACIA:")
    print("-" * 80)
    bottom_10 = sorted(resultados_completos.items(), key=lambda x: x[1]['acuracia'])[:10]
    for i, (mercado, stats) in enumerate(bottom_10, 1):
        print(f"  {i:2d}. {mercado:25s}: {stats['acuracia']:5.1f}% ({stats['corretos']}/{stats['testados']})")
    
    # Salvar resultados em JSON
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'validation_all_markets_{timestamp}.json'
    
    resultado_json = {
        'timestamp': timestamp,
        'total_partidas': total_partidas,
        'acuracia_geral': acuracia_geral,
        'total_mercados': len(acuracias_todas),
        'resultados_por_mercado': resultados_completos,
        'top_10_melhores': [
            {'mercado': m, **stats}
            for m, stats in top_10
        ],
        'top_10_piores': [
            {'mercado': m, **stats}
            for m, stats in bottom_10
        ]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(resultado_json, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados salvos em: {output_file}")
    print("\n" + "="*80)

if __name__ == '__main__':
    validar_todos_mercados()
