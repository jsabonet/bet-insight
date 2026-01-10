"""
Management Command: Pré-cálculo de análises
Uso: python manage.py precompute_analyses --matches=50
"""

from django.core.management.base import BaseCommand
import asyncio
from apps.analysis.services.precompute_service import run_precompute


class Command(BaseCommand):
    help = 'Pré-calcula análises das top N partidas do dia para cache warm-up'

    def add_arguments(self, parser):
        parser.add_argument(
            '--matches',
            type=int,
            default=50,
            help='Número de partidas a pré-calcular (padrão: 50)'
        )

    def handle(self, *args, **options):
        max_matches = options['matches']
        
        self.stdout.write(
            self.style.WARNING(f'\n🔥 Iniciando pré-cálculo de {max_matches} partidas...\n')
        )
        
        # Executar pré-cálculo assíncrono
        stats = asyncio.run(run_precompute(max_matches))
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Pré-cálculo concluído!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   Computadas: {stats["computed"]}/{stats["total_matches"]}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   Erros: {stats["errors"]}')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   Tempo total: {stats["elapsed_seconds"]:.2f}s')
        )
        self.stdout.write(
            self.style.SUCCESS(f'   Tempo médio: {stats["avg_seconds_per_match"]:.2f}s/partida\n')
        )
