import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.statistical_models import PoissonBivariateModel

model = PoissonBivariateModel()

print("\nTestando Poisson Model...")
print("="*60)

pred = model.predict(
    home_attack=1.5,
    home_defense=1.0,
    away_attack=1.2,
    away_defense=1.0,
    league_home_advantage=1.15
)

print("\nTipo do retorno:", type(pred))
print("\nChaves:", pred.keys() if isinstance(pred, dict) else "Nao eh dict")

if isinstance(pred, dict):
    for key, value in pred.items():
        print(f"\n{key}:")
        if isinstance(value, dict):
            for k2, v2 in value.items():
                print(f"  {k2}: {v2}")
        else:
            print(f"  {value}")
