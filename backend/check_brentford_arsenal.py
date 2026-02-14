"""
Verificar probabilidades do sistema para Brentford vs Arsenal
"""

print('='*80)
print('🔍 PROBABILIDADES DO SISTEMA: Brentford vs Arsenal')
print('='*80)

print('\n📊 DADOS DA PARTIDA:')
print('   Casa: Brentford')
print('   Fora: Arsenal')
print('\n💰 PROBABILIDADES REAIS (Mercado):')
print('   Brentford: 19.4%')
print('   Empate:    22.4%')
print('   Arsenal:   58.2%')

# Simular pesos do ensemble
configs = [
    ('COM Market (P=60% ML=25% M=15%)', {'poisson': 0.60, 'ml': 0.25, 'market': 0.15}),
    ('SEM Market (P=65% ML=35%)', {'poisson': 0.65, 'ml': 0.35, 'market': 0.0})
]

# Probabilidades dos modelos individuais
poisson_probs = {'home': 0.146, 'draw': 0.236, 'away': 0.618}
ml_probs = {'home': 0.33, 'draw': 0.34, 'away': 0.33}
market_probs = {'home': 0.194, 'draw': 0.224, 'away': 0.582}

print('\n' + '='*80)
print('🎯 PREVISÕES DOS MODELOS INDIVIDUAIS:')
print('='*80)
print(f'\n   Poisson: {poisson_probs["home"]*100:.1f}% | {poisson_probs["draw"]*100:.1f}% | {poisson_probs["away"]*100:.1f}%')
print(f'   ML:      {ml_probs["home"]*100:.1f}% | {ml_probs["draw"]*100:.1f}% | {ml_probs["away"]*100:.1f}%')
print(f'   Market:  {market_probs["home"]*100:.1f}% | {market_probs["draw"]*100:.1f}% | {market_probs["away"]*100:.1f}%')

for config_name, weights in configs:
    print(f'\n' + '='*80)
    print(f'⚖️ ENSEMBLE: {config_name}')
    print('='*80)
    
    # Calcular ensemble
    home = (poisson_probs['home'] * weights['poisson'] + 
            ml_probs['home'] * weights['ml'] + 
            market_probs['home'] * weights['market'])
    draw = (poisson_probs['draw'] * weights['poisson'] + 
            ml_probs['draw'] * weights['ml'] + 
            market_probs['draw'] * weights['market'])
    away = (poisson_probs['away'] * weights['poisson'] + 
            ml_probs['away'] * weights['ml'] + 
            market_probs['away'] * weights['market'])
    
    # Normalizar
    total = home + draw + away
    home /= total
    draw /= total
    away /= total
    
    print(f'\n   🎯 RESULTADO:')
    print(f'   Brentford: {home*100:.1f}%')
    print(f'   Empate:    {draw*100:.1f}%')
    print(f'   Arsenal:   {away*100:.1f}%')
    
    # Comparar com mercado
    erro_home = abs(home - market_probs['home'])
    erro_draw = abs(draw - market_probs['draw'])
    erro_away = abs(away - market_probs['away'])
    erro_total = (erro_home + erro_draw + erro_away) / 3
    
    print(f'\n   📊 Erro vs Mercado: {erro_total*100:.2f}%')
    
    # Verificar se está equilibrado
    max_prob = max(home, draw, away)
    min_prob = min(home, draw, away)
    spread = max_prob - min_prob
    
    if spread < 0.10:
        print(f'   ⚠️ PROBABILIDADES EQUILIBRADAS (spread: {spread*100:.1f}%)')
        print(f'   Isso NÃO está correto para esta partida!')
    else:
        print(f'   ✅ Favorito claro identificado (spread: {spread*100:.1f}%)')

print('\n' + '='*80)
print('💡 DIAGNÓSTICO')
print('='*80)
print('\nSe você está vendo ~33% cada (equilibrado):')
print('➡️ Sistema está usando config SEM Market (P=65% ML=35%)')
print('   ML prevê 33% cada → domina o resultado')
print()
print('O que deve estar acontecendo:')
print('1. Odds de mercado NÃO chegaram do backend')
print('2. Sistema usou fallback sem market')
print('3. ML (conservador) nivela tudo pra ~33%')
print()
print('Solução: Garantir que odds de mercado cheguem!')
print('='*80)
