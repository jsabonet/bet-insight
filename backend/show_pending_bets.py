"""Examinar apostas pendentes em detalhe"""
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet
import json

print('\n' + '='*80)
print('📋 DETALHES DAS APOSTAS PENDENTES')
print('='*80)

bets = DailyBet.objects.filter(is_validated=False).order_by('-date')

for i, bet in enumerate(bets, 1):
    print(f'\n[{i}] Aposta: {bet.date} - {bet.bet_type.upper()}')
    print(f'    Status: {bet.status}')
    print(f'    Odd Total: {bet.total_odd}')
    print(f'    Probabilidade: {bet.combined_probability:.1%}')
    print(f'    EV: {bet.expected_value:+.1f}%')
    print(f'    Stake Sugerido: {bet.suggested_stake} unidades')
    
    print(f'\n    Seleções ({len(bet.selections)}):')
    for j, sel in enumerate(bet.selections, 1):
        print(f"      [{j}] {sel.get('match', 'N/A')}")
        print(f"          Liga: {sel.get('league', 'N/A')}")
        print(f"          Data: {sel.get('date', 'N/A')}")
        print(f"          Mercado: {sel.get('market', 'N/A')}")
        print(f"          Pick: {sel.get('pick', 'N/A')}")
        print(f"          Odd: {sel.get('odd', 'N/A')}")
        print(f"          Probabilidade: {sel.get('probability', 0):.1%}")
        print(f"          ID Partida: {sel.get('match_id', 'N/A')}")
        
        # Verificar se tem resultado
        result = sel.get('result')
        if result:
            print(f"          ✅ Resultado: {result}")
        else:
            print(f"          ⏳ Aguardando resultado")

print('\n' + '='*80)
print(f'Total: {bets.count()} apostas pendentes')
print('='*80 + '\n')
