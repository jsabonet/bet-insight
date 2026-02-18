import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import DailyBet

# Ontem = 16 de fevereiro de 2026
yesterday = date.today() - timedelta(days=1)

print(f"\n{'='*80}")
print(f"BILHETES MÚLTIPLOS GERADOS EM {yesterday.strftime('%d/%m/%Y')}")
print(f"{'='*80}\n")

# Buscar todos os bilhetes múltiplos de ontem
multiples = DailyBet.objects.filter(
    date=yesterday,
    bet_type='multiple'
).order_by('-created_at')

if not multiples.exists():
    print(f"❌ Nenhum bilhete múltiplo encontrado para {yesterday.strftime('%d/%m/%Y')}")
else:
    print(f"✅ {multiples.count()} bilhete(s) múltiplo(s) encontrado(s)\n")
    
    for i, bet in enumerate(multiples, 1):
        print(f"{'─'*80}")
        print(f"BILHETE #{i} - ID: {bet.id}")
        print(f"{'─'*80}")
        print(f"📅 Data: {bet.date.strftime('%d/%m/%Y')}")
        print(f"🎯 Tipo: {bet.get_bet_type_display()}")
        print(f"📊 Status: {bet.get_status_display()}")
        print(f"💰 Odd Total: {bet.total_odd:.2f}")
        print(f"🎲 Probabilidade Combinada: {bet.combined_probability:.2f}%")
        print(f"📈 Expected Value: {bet.expected_value:.2f}%")
        print(f"💵 Stake Sugerido: {bet.suggested_stake:.1f}u")
        print(f"✅ Validado: {'Sim' if bet.is_validated else 'Não'}")
        if bet.validated_at:
            print(f"📅 Validado em: {bet.validated_at.strftime('%d/%m/%Y %H:%M')}")
        print(f"🕐 Criado em: {bet.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Exibir seleções
        if bet.selections:
            print(f"\n🎯 SELEÇÕES ({len(bet.selections)}):")
            for idx, sel in enumerate(bet.selections, 1):
                match = sel.get('match', {})
                # Match pode ser string ou dict
                if isinstance(match, str):
                    match_name = match
                    home = 'Casa'
                    away = 'Fora'
                    league = 'N/A'
                else:
                    home = match.get('home_team', 'Casa')
                    away = match.get('away_team', 'Fora')
                    league = match.get('league', 'N/A')
                    match_name = f"{home} vs {away}"
                
                market = sel.get('market', 'N/A')
                market_display = sel.get('market_display', market)
                odd = sel.get('odd', 0)
                probability = sel.get('probability', 0)
                
                print(f"\n   {idx}. {match_name}")
                if not isinstance(match, str):
                    print(f"      Liga: {league}")
                print(f"      Mercado: {market_display}")
                print(f"      Odd: {odd:.2f}")
                print(f"      Probabilidade: {probability:.1f}%")
                
                if bet.is_validated:
                    result = sel.get('result', 'pending')
                    result_emoji = '✅' if result == 'won' else ('❌' if result == 'lost' else '⏳')
                    print(f"      Resultado: {result_emoji} {result}")
        
        # ROI se validado
        if bet.is_validated:
            roi = bet.get_roi()
            print(f"\n💹 ROI: {roi:+.2f}%")
        
        print()

print(f"{'='*80}\n")
