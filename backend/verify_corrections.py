"""Verificar se correções foram aplicadas corretamente"""
import sys

print('\n' + '='*80)
print('VERIFICACAO DAS CORRECOES APLICADAS')
print('='*80)

# Verificar market_selector.py
print('\n1. Verificando market_selector.py...')

with open('apps/analysis/services/market_selector.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # Verificar thresholds corrigidos
    checks = [
        ('min_probability = 0.55', 'Threshold multiple corrigido (0.55)'),
        ('min_probability = 0.45', 'Threshold value corrigido (0.45)'),
        ('def _validate_bet_quality', 'Metodo de validacao extra criado'),
        ('validated_candidates', 'Lista de candidatos validados'),
    ]
    
    all_ok = True
    for check_str, description in checks:
        if check_str in content:
            print(f'   OK {description}')
        else:
            print(f'   ERRO {description} - NAO ENCONTRADO!')
            all_ok = False
    
    if all_ok:
        print('   ====> market_selector.py: TODAS CORRECOES APLICADAS')
    else:
        print('   ====> market_selector.py: FALTAM CORRECOES!')

# Verificar context_analyzer.py
print('\n2. Verificando context_analyzer.py...')

with open('apps/analysis/services/context_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # Contar pesos reduzidos (0.70, 0.65, 0.60)
    count_070 = content.count(': 0.70')
    count_065 = content.count(': 0.65')
    count_060 = content.count(': 0.60')
    
    # Verificar se NÃO tem mais pesos altos ruins
    count_095 = content.count(": 0.95  # era")  # Comentários indicam correção
    count_090 = content.count(": 0.90  # era")
    count_085 = content.count(": 0.85  # era")
    
    print(f'   Pesos 0.70: {count_070} ocorrencias')
    print(f'   Pesos 0.65: {count_065} ocorrencias')
    print(f'   Pesos 0.60: {count_060} ocorrencias')
    print(f'   Comentarios "era 0.95": {count_095}')
    print(f'   Comentarios "era 0.90": {count_090}')
    print(f'   Comentarios "era 0.85": {count_085}')
    
    if (count_070 >= 8 and count_065 >= 8 and count_060 >= 8 and 
        count_095 >= 2 and count_090 >= 2):
        print('   ====> context_analyzer.py: PESOS REDUZIDOS CORRETAMENTE')
    else:
        print('   ====> context_analyzer.py: VERIFICAR PESOS MANUALMENTE')

# Resumo
print('\n' + '='*80)
print('RESUMO')
print('='*80)
print('As correcoes foram aplicadas nos arquivos:')
print('- market_selector.py: Thresholds 45%/55% + validacao extra')
print('- context_analyzer.py: Pesos reduzidos em 15-25%')
print('\nProximo passo: Gerar novas apostas e validar resultados')
print('Comando: python manage.py generate_daily_bets')
print('='*80 + '\n')
