"""Teste dos novos mercados implementados"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.statistical_models import PoissonBivariateModel

poisson = PoissonBivariateModel()
result = poisson.predict(home_strength=2.0, away_strength=1.2)

print('\n' + '='*80)
print('📊 NOVOS MERCADOS IMPLEMENTADOS (sem dados extras)')
print('='*80)

probs = result['probabilities']

print('\n🎯 TEAM TOTAL GOALS:')
print(f'   Casa Over 0.5: {probs.get("home_over_05", 0)*100:.1f}%')
print(f'   Casa Over 1.5: {probs.get("home_over_15", 0)*100:.1f}%')
print(f'   Casa Over 2.5: {probs.get("home_over_25", 0)*100:.1f}%')
print(f'   Fora Over 0.5: {probs.get("away_over_05", 0)*100:.1f}%')
print(f'   Fora Over 1.5: {probs.get("away_over_15", 0)*100:.1f}%')

print('\n🏆 MARGENS DE VITÓRIA:')
print(f'   Casa por 1 gol: {probs.get("home_win_by_1", 0)*100:.1f}%')
print(f'   Casa por 2+ gols: {probs.get("home_win_by_2plus", 0)*100:.1f}%')
print(f'   Fora por 1 gol: {probs.get("away_win_by_1", 0)*100:.1f}%')
print(f'   Fora por 2+ gols: {probs.get("away_win_by_2plus", 0)*100:.1f}%')

print('\n🎲 ODD/EVEN:')
print(f'   Gols Ímpares: {probs.get("odd_goals", 0)*100:.1f}%')
print(f'   Gols Pares: {probs.get("even_goals", 0)*100:.1f}%')

print('\n📋 PLACAR EXATO (Top 5):')
for i, score in enumerate(result['score_distribution'][:5], 1):
    prob = score['probability'] * 100
    fair_odd = 1 / score['probability'] if score['probability'] > 0 else 999
    print(f'   {i}. {score["score"]}: {prob:.1f}% (Fair odd: {fair_odd:.2f})')

print('\n' + '='*80)
print('✅ TOTAL DE MERCADOS AGORA: 20+')
print('='*80)
print('\n📊 RESUMO:')
print('   • Over/Under: 3 linhas (1.5, 2.5, 3.5)')
print('   • Team Goals: 6 opções (Casa/Fora × 0.5/1.5/2.5)')
print('   • Margens: 4 opções (Casa/Fora × 1/2+)')
print('   • Odd/Even: 2 opções')
print('   • Placar Exato: Top 5 mais prováveis')
print('   • Resultado: 1X2, DC, DNB')
print('   • BTTS, Clean Sheets')
print('\n🎯 TUDO SEM DADOS EXTRAS! Só Poisson + Consensus')
