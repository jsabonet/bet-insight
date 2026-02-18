import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.daily_bet_generator import DailyBetGenerator

print("\n" + "="*80)
print("TESTE DO SISTEMA HIBRIDO DE GERACAO DE BILHETES")
print("="*80 + "\n")

generator = DailyBetGenerator()

print("Executando geracao com modo: HYBRID")
print("="*80)

results = generator.generate_for_today(days_ahead=1, mode='hybrid')

print("\n" + "="*80)
print("RESULTADOS DO TESTE - MODO HYBRID")
print("="*80)
print(f"Modo de busca utilizado: {results.get('search_mode', 'N/A')}")
print(f"Total de fixtures encontradas: {results.get('total_fixtures_found', 0)}")
print(f"Fixtures agendadas para analise: {results.get('scheduled_fixtures', 0)}")
print(f"Partidas analisadas: {results.get('matches_analyzed', 0)}")
print(f"Bilhetes multiplos gerados: {results.get('multiple_count', 0)}")
print(f"Apostas de valor geradas: {results.get('value_count', 0)}")
print(f"Total de apostas: {results.get('total_bets', 0)}")
print(f"Chamadas API: {results.get('api_calls', 0)}")
print(f"Cache hits: {results.get('cache_hits', 0)}")
print("="*80 + "\n")
