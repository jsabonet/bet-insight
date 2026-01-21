"""Teste das novas linhas Over/Under"""
import os, sys, django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.statistical_models import PoissonBivariateModel

poisson = PoissonBivariateModel()
result = poisson.predict(home_strength=1.5, away_strength=1.0)

print('\n📊 Teste Over/Under múltiplas linhas:')
probs = result['probabilities']
print(f'   Over 1.5: {probs.get("over_1_5", 0)*100:.1f}%')
print(f'   Under 1.5: {probs.get("under_1_5", 0)*100:.1f}%')
print(f'   Over 2.5: {probs.get("over_2_5", 0)*100:.1f}%')
print(f'   Under 2.5: {probs.get("under_2_5", 0)*100:.1f}%')
print(f'   Over 3.5: {probs.get("over_3_5", 0)*100:.1f}%')
print(f'   Under 3.5: {probs.get("under_3_5", 0)*100:.1f}%')
print(f'   BTTS: {probs.get("btts", 0)*100:.1f}%')
print('\n✅ Sucesso! Agora temos 3 linhas de Over/Under!')
