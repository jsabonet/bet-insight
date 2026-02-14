"""
Script simples para testar acurácia com base nas apostas JÁ validadas no banco de dados
Usa os DailyBets que já foram validados com resultados reais
"""
import os
import sys
import django
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet
from django.db.models import Q

print("\n" + "="*80)
print("🎯 TESTE DE ACURÁCIA - BANCO DE DADOS")
print("="*80)

# Buscar apostas dos últimos 30 dias que já foram validadas
date_30_days_ago = datetime.now().date() - timedelta(days=30)

# Apostas validadas (com resultado conhecido)
validated_bets = DailyBet.objects.filter(
    date__gte=date_30_days_ago,
    is_validated=True
).exclude(
    status='pending'
)

total = validated_bets.count()
won = validated_bets.filter(status='won').count()
lost = validated_bets.filter(status='lost').count()
void = validated_bets.filter(status='cancelled').count()
partial = validated_bets.filter(status='partial').count()

print(f"\n📊 APOSTAS VALIDADAS (últimos 30 dias):")
print(f"   Total: {total}")
print(f"   ✅ Ganhas: {won}")
print(f"   ❌ Perdidas: {lost}")
print(f"   🟡 Parciais: {partial}")
print(f"   ⚪ Canceladas: {void}")

if total > 0:
    accuracy = (won / total) * 100
    print(f"\n🎯 ACURÁCIA GERAL: {accuracy:.1f}%")
    
    # Por tipo de aposta
    print(f"\n📈 ACURÁCIA POR TIPO:")
    
    for bet_type_value in ['multiple', 'value']:
        bets_type = validated_bets.filter(bet_type=bet_type_value)
        total_type = bets_type.count()
        won_type = bets_type.filter(status='won').count()
        
        if total_type > 0:
            accuracy_type = (won_type / total_type) * 100
            type_label = 'Múltiplos' if bet_type_value == 'multiple' else 'Value'
            print(f"   {type_label:9s}: {won_type:2d}/{total_type:2d} = {accuracy_type:5.1f}%")
    
    # Por data (últimos 7 dias)
    print(f"\n📅 ACURÁCIA POR DIA (últimos 7 dias):")
    for days_ago in range(7):
        date = datetime.now().date() - timedelta(days=days_ago)
        bets_day = validated_bets.filter(date=date)
        total_day = bets_day.count()
        won_day = bets_day.filter(status='won').count()
        
        if total_day > 0:
            accuracy_day = (won_day / total_day) * 100
            print(f"   {date}: {won_day:2d}/{total_day:2d} = {accuracy_day:5.1f}%")
    
    # Calcular ROI
    print(f"\n💰 ROI:")
    total_stake = 0
    total_return = 0
    
    for bet in validated_bets:
        stake = bet.suggested_stake if bet.suggested_stake else 1.0  # Stake padrão 1 unidade
        total_stake += stake
        
        if bet.status == 'won':
            # Calcular retorno baseado na odd total
            total_return += stake * float(bet.total_odd)
    
    if total_stake > 0:
        roi = ((total_return - total_stake) / total_stake) * 100
        profit = total_return - total_stake
        
        print(f"   Total investido: {total_stake:.2f}")
        print(f"   Total retornado: {total_return:.2f}")
        print(f"   Lucro/Prejuízo: {profit:+.2f}")
        print(f"   ROI: {roi:+.1f}%")
        
        if roi > 0:
            print(f"\n   ✅ SISTEMA LUCRATIVO!")
        else:
            print(f"\n   ❌ SISTEMA COM PREJUÍZO!")
else:
    print("\n⚠️ Nenhuma aposta validada encontrada no banco de dados")
    print("   Execute: python manage.py validate_daily_bets")

print("\n" + "="*80)
print("✅ Análise concluída!")
print("="*80 + "\n")
