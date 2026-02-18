import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet
from django.utils import timezone
from datetime import timedelta

# Ver bilhetes criados hoje
today = timezone.now().date()
recent_bets = DailyBet.objects.filter(date=today).order_by('-created_at')

print(f"\n{'='*80}")
print(f"BILHETES GERADOS HOJE ({today.strftime('%d/%02/%Y')})")
print(f"{'='*80}\n")

if not recent_bets.exists():
    print("❌ Nenhum bilhete encontrado gerado hoje")
else:
    print(f"Total de bilhetes: {recent_bets.count()}\n")
    
    for i, bet in enumerate(recent_bets[:10], 1):  # Mostrar até 10
        print(f"{i}. Bilhete ID: {bet.id}")
        print(f"   Tipo: {bet.bet_type}")
        print(f"   Status: {bet.status}")
        print(f"   Data criação: {bet.created_at.strftime('%H:%M:%S')}")
        print(f"   Número de seleções: {len(bet.selections)}")
        if bet.selections:
            print("   Seleções:")
            for sel in bet.selections:
                match_name = f"{sel.get('match', {}).get('home_team', 'N/A')} vs {sel.get('match', {}).get('away_team', 'N/A')}"
                market = sel.get('market', 'N/A')
                print(f"      - {match_name}: {market}")
        print()

print(f"{'='*80}\n")
