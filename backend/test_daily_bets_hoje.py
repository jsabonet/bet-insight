import os
import sys
import django
from datetime import datetime

# Setup Django
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.daily_bet_generator import DailyBetGenerator

print("\n" + "=" * 80)
print(f"🧪 TESTE: Buscar partidas APENAS DE HOJE")
print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %A')}")
print("=" * 80 + "\n")

generator = DailyBetGenerator()

# Testar com 1 dia (padrão - apenas hoje)
print("🔍 Executando: generate_for_today() - sem parâmetro (padrão = 1 dia)\n")
results = generator.generate_for_today()

print("\n" + "=" * 80)
print("📊 RESULTADO")
print("=" * 80)
print(f"Partidas encontradas e analisadas: {results.get('matches_analyzed', 0)}")
print(f"Múltiplos gerados: {results.get('multiple_count', 0)}")
print(f"Value bets geradas: {results.get('value_count', 0)}")
print(f"Total de apostas: {results.get('total_bets', 0)}")
print("=" * 80 + "\n")
