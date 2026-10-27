"""
Comando Django para gerar bilhetes múltiplos diários manualmente

Uso:
    python manage.py generate_daily_bets
    
Este comando pode ser agendado com Task Scheduler do Windows para rodar automaticamente.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.analysis.services.daily_bet_generator import DailyBetGenerator


class Command(BaseCommand):
    help = 'Gera bilhetes múltiplos para as partidas de hoje'

    def handle(self, *args, **options):
        self.stdout.write("=" * 100)
        self.stdout.write(self.style.SUCCESS('🎯 GERAÇÃO DE BILHETES AUTOMÁTICOS'))
        self.stdout.write("=" * 100)
        self.stdout.write(f"Timestamp: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        
        try:
            generator = DailyBetGenerator()
            results = generator.generate_for_today()
            if results.get('total_bets', 0) > 0:
                from apps.notifications.tasks import enqueue_premium_daily_bets_push
                enqueue_premium_daily_bets_push(
                    timezone.localdate(),
                    results.get('multiple_count', 0),
                    results.get('value_count', 0),
                )
            
            self.stdout.write("\n" + "=" * 100)
            self.stdout.write(self.style.SUCCESS('✅ GERAÇÃO CONCLUÍDA COM SUCESSO'))
            self.stdout.write("=" * 100)
            self.stdout.write(f"📋 Bilhetes múltiplos: {results['multiple_count']}")
            self.stdout.write(f"⚡ Value bets: {results['value_count']}")
            self.stdout.write(f"⚽ Partidas analisadas: {results['matches_analyzed']}")
            self.stdout.write(f"🔌 Requisições API (estimado): {results['api_calls']}")
            self.stdout.write("=" * 100 + "\n")
            
            if results['matches_analyzed'] == 0:
                self.stdout.write(self.style.WARNING('⚠️  Nenhuma partida encontrada para hoje'))
            elif results['multiple_count'] == 0 and results['value_count'] == 0:
                self.stdout.write(self.style.WARNING('⚠️  Nenhum bilhete gerado (critérios não atendidos)'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✨ {results["multiple_count"] + results["value_count"]} apostas geradas!'))
            
        except Exception as e:
            self.stdout.write("\n" + "=" * 100)
            self.stdout.write(self.style.ERROR('❌ ERRO NA GERAÇÃO'))
            self.stdout.write("=" * 100)
            self.stdout.write(self.style.ERROR(f"Erro: {str(e)}"))
            self.stdout.write("=" * 100 + "\n")
            raise
