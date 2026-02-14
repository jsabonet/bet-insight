"""Check apostas no banco"""
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet
from datetime import datetime, timedelta

date_30_days = datetime.now().date() - timedelta(days=30)

total = DailyBet.objects.filter(date__gte=date_30_days).count()
pending = DailyBet.objects.filter(date__gte=date_30_days, is_validated=False).count()
validated = DailyBet.objects.filter(date__gte=date_30_days, is_validated=True).count()

print(f'\n📊 APOSTAS DOS ÚLTIMOS 30 DIAS:')
print(f'   Total: {total}')
print(f'   Validadas: {validated}')
print(f'   Pendentes: {pending}\n')

# Mostrar últimas 5 apostas
if total > 0:
    print('📋 ÚLTIMAS 5 APOSTAS:')
    for bet in DailyBet.objects.all().order_by('-date')[:5]:
        print(f'   {bet.date} - {bet.bet_type} - {bet.status} - {len(bet.selections)} seleções')
