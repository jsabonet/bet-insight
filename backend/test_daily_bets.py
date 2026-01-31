"""
Teste Rápido do Sistema de Bilhetes Automáticos

Execute este script para testar a geração de bilhetes sem esperar pelo Celery Beat.
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.daily_bet_generator import DailyBetGenerator
from apps.analysis.models import DailyBet
from django.utils import timezone


def test_generation():
    """Testa geração de bilhetes"""
    print("=" * 100)
    print("🎯 TESTE DE GERAÇÃO DE BILHETES AUTOMÁTICOS")
    print("=" * 100)
    
    # Criar gerador
    generator = DailyBetGenerator()
    
    # Gerar apostas
    print("\n📅 Gerando apostas para hoje...")
    results = generator.generate_for_today()
    
    print(f"\n{'=' * 100}")
    print("✅ RESULTADO DA GERAÇÃO")
    print(f"{'=' * 100}")
    print(f"⚽ Partidas analisadas: {results['matches_analyzed']}")
    print(f"📋 Bilhetes múltiplos criados: {results['multiple_count']}")
    print(f"⚡ Value bets criadas: {results['value_count']}")
    print(f"🔌 Requisições API (estimado): {results['api_calls']}")
    print(f"💾 Cache hits (estimado): {results['cache_hits']}")
    print(f"{'=' * 100}\n")
    
    # Mostrar apostas criadas
    today = timezone.now().date()
    today_bets = DailyBet.objects.filter(date=today)
    
    if today_bets.exists():
        print(f"\n{'=' * 100}")
        print("📊 APOSTAS CRIADAS")
        print(f"{'=' * 100}\n")
        
        # Bilhetes múltiplos
        multiples = today_bets.filter(bet_type='multiple').order_by('-combined_probability')
        if multiples.exists():
            print("📋 BILHETES MÚLTIPLOS:\n")
            for i, bet in enumerate(multiples, 1):
                print(f"   Bilhete #{i} ({len(bet.selections)}x):")
                print(f"      Odd Total: {bet.total_odd:.2f}")
                print(f"      Prob. Combinada: {bet.combined_probability*100:.1f}%")
                print(f"      EV: {bet.expected_value:+.1f}%")
                print(f"      Stake sugerido: {bet.suggested_stake:.1f}u")
                print(f"      Apostas:")
                for sel in bet.selections[:3]:  # Mostrar primeiras 3
                    print(f"         • {sel['pick']} ({sel['market']}) @ {sel['odd']:.2f} - {sel['probability']*100:.0f}%")
                if len(bet.selections) > 3:
                    print(f"         ... (+{len(bet.selections)-3} apostas)")
                print()
        
        # Value bets
        values = today_bets.filter(bet_type='value').order_by('-expected_value')
        if values.exists():
            print("\n⚡ VALUE BETS:\n")
            for i, bet in enumerate(values, 1):
                sel = bet.selections[0]
                print(f"   Value Bet #{i}:")
                print(f"      {sel['match']}")
                print(f"      Aposta: {sel['pick']} ({sel['market']})")
                print(f"      Odd: {sel['odd']:.2f} | Prob: {sel['probability']*100:.0f}% | EV: +{sel['ev_pct']:.1f}%")
                print(f"      Stake: {bet.suggested_stake:.1f}u")
                print()
    else:
        print("\n⚠️  Nenhuma aposta foi gerada (talvez não haja partidas hoje)")
    
    print(f"\n{'=' * 100}")
    print("✅ TESTE CONCLUÍDO")
    print(f"{'=' * 100}\n")
    
    return results


def test_validation():
    """Testa validação de apostas"""
    print("=" * 100)
    print("🔍 TESTE DE VALIDAÇÃO DE APOSTAS")
    print("=" * 100)
    
    from apps.analysis.models import DailyBet
    
    # Buscar apostas pendentes
    pending = DailyBet.objects.filter(status='pending', is_validated=False)[:5]
    
    if not pending.exists():
        print("\n⚠️  Nenhuma aposta pendente encontrada")
        return
    
    print(f"\n📊 {pending.count()} apostas pendentes encontradas\n")
    
    validated_count = 0
    
    for bet in pending:
        print(f"Validando: {bet}")
        was_validated = bet.validate_result()
        
        if was_validated:
            validated_count += 1
            print(f"   ✅ Validado: {bet.get_status_display()}")
            print(f"   Resultado: {bet.actual_result}")
            print(f"   ROI: {bet.get_roi():.1f}%\n")
        else:
            print(f"   ⏳ Aguardando jogos finalizarem\n")
    
    print(f"\n✅ {validated_count} apostas validadas")
    print(f"⏳ {pending.count() - validated_count} ainda pendentes\n")


def show_stats():
    """Mostra estatísticas das apostas"""
    print("=" * 100)
    print("📊 ESTATÍSTICAS PÚBLICAS")
    print("=" * 100)
    
    from django.db.models import Avg, Count, Q
    from datetime import timedelta
    
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    # All time
    all_bets = DailyBet.objects.filter(is_validated=True)
    
    if not all_bets.exists():
        print("\n⚠️  Ainda não há apostas validadas")
        return
    
    total = all_bets.count()
    won = all_bets.filter(status='won').count()
    lost = all_bets.filter(status='lost').count()
    
    print(f"\n🌍 ALL TIME:")
    print(f"   Total: {total}")
    print(f"   Ganhas: {won} ({won/total*100:.1f}%)")
    print(f"   Perdidas: {lost} ({lost/total*100:.1f}%)")
    print(f"   Odd média: {all_bets.aggregate(avg=Avg('total_odd'))['avg']:.2f}")
    
    # Last 7 days
    last_7 = all_bets.filter(date__gte=last_7_days)
    if last_7.exists():
        print(f"\n📅 ÚLTIMOS 7 DIAS:")
        print(f"   Total: {last_7.count()}")
        print(f"   Win rate: {last_7.filter(status='won').count()/last_7.count()*100:.1f}%")
    
    # Por tipo
    print(f"\n📋 POR TIPO:")
    for bet_type in ['multiple', 'value']:
        type_bets = all_bets.filter(bet_type=bet_type)
        if type_bets.exists():
            type_won = type_bets.filter(status='won').count()
            print(f"   {bet_type.upper()}:")
            print(f"      Total: {type_bets.count()}")
            print(f"      Win rate: {type_won/type_bets.count()*100:.1f}%")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'generate':
            test_generation()
        elif command == 'validate':
            test_validation()
        elif command == 'stats':
            show_stats()
        else:
            print("Comandos disponíveis:")
            print("  python test_daily_bets.py generate  - Gera apostas para hoje")
            print("  python test_daily_bets.py validate  - Valida apostas pendentes")
            print("  python test_daily_bets.py stats     - Mostra estatísticas")
    else:
        # Executar todos os testes
        test_generation()
        print("\n" + "=" * 100 + "\n")
        test_validation()
        print("\n" + "=" * 100 + "\n")
        show_stats()
