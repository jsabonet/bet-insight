"""
Comando Django para validar resultados de bilhetes pendentes

Uso:
    python manage.py validate_daily_bets
    
Este comando pode ser agendado para rodar periodicamente.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.analysis.models import DailyBet


class Command(BaseCommand):
    help = 'Valida resultados de apostas pendentes dos últimos 7 dias'

    def handle(self, *args, **options):
        self.stdout.write("=" * 100)
        self.stdout.write(self.style.SUCCESS('🔍 VALIDAÇÃO DE BILHETES AUTOMÁTICOS'))
        self.stdout.write("=" * 100)
        self.stdout.write(f"Timestamp: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        try:
            # Buscar apostas pendentes dos últimos 7 dias
            cutoff_date = timezone.now().date() - timedelta(days=7)
            
            pending_bets = DailyBet.objects.filter(
                status='pending',
                is_validated=False,
                date__gte=cutoff_date
            ).order_by('date')
            
            self.stdout.write(f"📊 Apostas pendentes encontradas: {pending_bets.count()}\n")
            
            if pending_bets.count() == 0:
                self.stdout.write(self.style.WARNING('ℹ️  Nenhuma aposta pendente para validar'))
                self.stdout.write("=" * 100 + "\n")
                return
            
            validated_count = 0
            still_pending_count = 0
            
            for bet in pending_bets:
                self.stdout.write(f"\n{'─' * 80}")
                self.stdout.write(f"Validando: {bet}")
                self.stdout.write(f"   Data: {bet.date.strftime('%d/%m/%Y')}")
                self.stdout.write(f"   Tipo: {bet.get_bet_type_display()}")
                
                # Validar resultado
                old_status = bet.status
                bet.validate_result()
                
                if bet.status != old_status:
                    bet.is_validated = True
                    bet.validated_at = timezone.now()
                    bet.save()
                    validated_count += 1
                    
                    status_emoji = {
                        'won': '✅',
                        'lost': '❌',
                        'partial': '⚠️',
                        'cancelled': '🚫'
                    }.get(bet.status, '❓')
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"   {status_emoji} Status atualizado: {old_status} → {bet.status}"
                    ))
                else:
                    still_pending_count += 1
                    self.stdout.write(self.style.WARNING(
                        f"   ⏳ Ainda pendente (jogos não finalizados)"
                    ))
            
            self.stdout.write("\n" + "=" * 100)
            self.stdout.write(self.style.SUCCESS('✅ VALIDAÇÃO CONCLUÍDA'))
            self.stdout.write("=" * 100)
            self.stdout.write(f"✅ Apostas validadas: {validated_count}")
            self.stdout.write(f"⏳ Ainda pendentes: {still_pending_count}")
            self.stdout.write("=" * 100 + "\n")
            
        except Exception as e:
            self.stdout.write("\n" + "=" * 100)
            self.stdout.write(self.style.ERROR('❌ ERRO NA VALIDAÇÃO'))
            self.stdout.write("=" * 100)
            self.stdout.write(self.style.ERROR(f"Erro: {str(e)}"))
            self.stdout.write("=" * 100 + "\n")
            raise
