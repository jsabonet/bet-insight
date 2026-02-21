#!/usr/bin/env python
"""Verificar apostas elegíveis já no banco"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet, Analysis
from django.utils import timezone

today = timezone.now().date()

print("\n" + "="*60)
print("VERIFICAÇÃO - Bilhetes Gerados Hoje")
print("="*60)

# Verificar bilhetes gerados hoje
bets = DailyBet.objects.filter(date=today).order_by('-total_odd')

print(f"\n💰 Bilhetes gerados hoje: {bets.count()}")

if bets:
    multiples = bets.filter(bet_type='multiple')
    values = bets.filter(bet_type='value')
    
    print(f"   Múltiplas: {multiples.count()}")
    print(f"   Value: {values.count()}")
    
    print(f"\n🎯 Top 5 Bilhetes (ordenados por odd):")
    for i, bet in enumerate(bets[:5], 1):
        prob_pct = bet.combined_probability * 100 if bet.combined_probability else 0
        print(f"   {i}. {bet.bet_type.upper():8} | Odd: {bet.total_odd:6.2f} | EV: {bet.expected_value:+6.1f}% | Prob: {prob_pct:5.1f}% | Stake: {bet.suggested_stake}u")
else:
    print("   ⚠️ Nenhum bilhete criado ainda")

print("\n" + "="*60)
print("💡 Resumo: Se tem mercados elegíveis mas 0 bilhetes,")
print("   significa que os filtros combinados estão muito restritivos.")
print("="*60)
