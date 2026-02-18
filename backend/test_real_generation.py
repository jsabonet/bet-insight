import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.daily_bet_generator import DailyBetGenerator
from apps.matches.models import Match

print("\n" + "="*80)
print("🧪 TESTE: GERAÇÃO REAL DE BILHETES COM NOVOS THRESHOLDS")
print("="*80 + "\n")

# Verificar partidas disponíveis para hoje/amanhã
tomorrow = datetime.now() + timedelta(days=1)
matches_count = Match.objects.filter(
    match_date__date=tomorrow.date(),
    status__in=['scheduled', 'not_started']
).count()

print(f"📅 Data alvo: {tomorrow.strftime('%d/%m/%Y')}")
print(f"🏟️  Partidas disponíveis: {matches_count}\n")

if matches_count == 0:
    print("⚠️  Nenhuma partida disponível para amanhã.")
    print("   Execute: python manage.py generate_daily_bets --mode=hybrid")
    exit(0)

print("="*80)
print("🚀 INICIANDO GERAÇÃO DE BILHETES...")
print("="*80 + "\n")

generator = DailyBetGenerator()

try:
    results = generator.generate_for_today(days_ahead=1, mode='hybrid')
    
    print("\n" + "="*80)
    print("📊 RESULTADOS DA GERAÇÃO:")
    print("="*80 + "\n")
    
    print(f"   Partidas Analisadas: {results.get('matches_analyzed', 0)}")
    print(f"   Bilhetes Múltiplos Criados: {results.get('multiple_count', 0)}")
    print(f"   Value Bets Criadas: {results.get('value_count', 0)}")
    print(f"   Total de Apostas: {results.get('multiple_count', 0) + results.get('value_count', 0)}")
    
    if 'errors' in results and results['errors']:
        print(f"\n   ⚠️  Erros: {len(results['errors'])}")
        for error in results['errors'][:3]:
            print(f"      • {error}")
    
    # Buscar bilhetes gerados
    from apps.bets.models import Ticket
    
    today_tickets = Ticket.objects.filter(
        created_at__date=datetime.now().date(),
        ticket_type__in=['MULTIPLE_3X', 'MULTIPLE_5X', 'MULTIPLE_7X']
    ).order_by('-created_at')
    
    if today_tickets.exists():
        print("\n" + "="*80)
        print("🎫 BILHETES GERADOS HOJE:")
        print("="*80 + "\n")
        
        for ticket in today_tickets[:10]:
            bets = ticket.bets.all()
            num_bets = bets.count()
            
            # Calcular probabilidade combinada
            combined_prob = 1.0
            for bet in bets:
                prob = bet.bet_data.get('probability', 0)
                combined_prob *= prob
            
            combined_odd = ticket.total_odd
            
            print(f"   {'='*76}")
            print(f"   🎯 Bilhete {ticket.ticket_type} (ID: {ticket.id})")
            print(f"   {'='*76}")
            print(f"      Odd Total: {combined_odd:.2f}")
            print(f"      Prob Combinada: {combined_prob*100:.2f}%")
            print(f"      Status: {'✅ ATIVO' if ticket.status == 'active' else ticket.status.upper()}")
            print(f"      Apostas: {num_bets}")
            print()
            
            # Listar apostas
            for i, bet in enumerate(bets, 1):
                match_info = bet.bet_data.get('match', {})
                prob = bet.bet_data.get('probability', 0)
                odd = bet.bet_data.get('odd', 0)
                market = bet.bet_data.get('market', '')
                selection = bet.bet_data.get('selection', '')
                confidence = bet.bet_data.get('confidence', {})
                risk = bet.bet_data.get('risk', '')
                draw_prob = bet.bet_data.get('draw_probability', 0)
                
                home = match_info.get('home_team', 'N/A')
                away = match_info.get('away_team', 'N/A')
                
                print(f"      {i}. {home} vs {away}")
                print(f"         Aposta: {market} - {selection}")
                print(f"         Prob: {prob*100:.2f}% | Odd: {odd:.2f}")
                print(f"         Confidence: {confidence.get('stars', 0)}⭐ ({confidence.get('level', 'N/A')})")
                print(f"         Risco: {risk} | Empate: {draw_prob*100:.1f}%")
                print()
            
            # Validação dos thresholds
            print(f"      📋 VALIDAÇÃO:")
            if ticket.ticket_type == 'MULTIPLE_3X':
                min_prob = 0.80
                min_combined = 0.50
            elif ticket.ticket_type == 'MULTIPLE_5X':
                min_prob = 0.87
                min_combined = 0.50
            else:
                min_prob = 0.91
                min_combined = 0.50
            
            # Check individual probs
            all_pass = True
            for bet in bets:
                prob = bet.bet_data.get('probability', 0)
                if prob < min_prob:
                    all_pass = False
                    print(f"         ❌ Aposta com prob {prob*100:.1f}% < {min_prob*100:.0f}%")
            
            if all_pass:
                print(f"         ✅ Todas as apostas ≥ {min_prob*100:.0f}%")
            
            # Check combined prob
            if combined_prob >= min_combined:
                print(f"         ✅ Prob combinada {combined_prob*100:.2f}% ≥ {min_combined*100:.0f}%")
            else:
                print(f"         ❌ Prob combinada {combined_prob*100:.2f}% < {min_combined*100:.0f}%")
            
            # Check draw probabilities
            high_draw = [bet for bet in bets if bet.bet_data.get('draw_probability', 0) > 0.35]
            if high_draw:
                print(f"         ⚠️  {len(high_draw)} aposta(s) com empate > 35%")
            else:
                print(f"         ✅ Todas com empate < 35%")
            
            # Check confidence
            low_conf = [bet for bet in bets if bet.bet_data.get('confidence', {}).get('stars', 0) < 4]
            if low_conf:
                print(f"         ⚠️  {len(low_conf)} aposta(s) com confidence < 4 estrelas")
            else:
                print(f"         ✅ Todas com confidence ≥ 4 estrelas")
            
            print()
    
    else:
        print("\n   ℹ️  Nenhum bilhete múltiplo foi gerado hoje.")
        print("      Isso pode significar:")
        print("      • Novos thresholds são muito restritivos")
        print("      • Não há apostas que atendam os critérios")
        print("      • Sistema funcionando corretamente ao rejeitar apostas ruins")
    
    print("\n" + "="*80)
    print("💡 INTERPRETAÇÃO DOS RESULTADOS:")
    print("="*80 + "\n")
    
    if today_tickets.exists():
        print("   ✅ Sistema está gerando bilhetes com os novos thresholds")
        print("   📊 Verifique se as probabilidades combinadas estão ≥50%")
        print("   🎯 Confira se jogos arriscados foram excluídos")
    else:
        print("   ⚠️  Nenhum bilhete gerado - thresholds podem estar muito altos")
        print("   📉 Considere ajustar ligeiramente se necessário")
        print("   ✅ Ou sistema está corretamente rejeitando apostas ruins")
    
    print("\n" + "="*80 + "\n")

except Exception as e:
    print(f"\n❌ ERRO durante a geração: {e}")
    import traceback
    traceback.print_exc()
