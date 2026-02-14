"""
Management command para limpar todos os caches do sistema
Útil após implementar correções que afetam probabilidades/análises
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.analysis.services.cache_service import _cache as analysis_cache


class Command(BaseCommand):
    help = 'Limpa todos os caches do sistema (Django + Analysis)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--analysis-only',
            action='store_true',
            help='Limpar apenas cache de análises (não Django cache)',
        )
        parser.add_argument(
            '--django-only',
            action='store_true',
            help='Limpar apenas Django cache (não Analysis cache)',
        )

    def handle(self, *args, **options):
        self.stdout.write("")
        self.stdout.write("="*80)
        self.stdout.write(self.style.WARNING("🧹 LIMPEZA DE CACHE"))
        self.stdout.write("="*80)
        self.stdout.write("")

        analysis_only = options.get('analysis_only', False)
        django_only = options.get('django_only', False)

        # Se não especificou nenhum, limpar ambos
        if not analysis_only and not django_only:
            analysis_only = True
            django_only = True

        # 1. Limpar Django Cache
        if django_only:
            self.stdout.write("📦 Limpando Django Cache (LocMemCache)...")
            try:
                # Obter stats antes de limpar
                cache_info = cache._cache if hasattr(cache, '_cache') else {}
                num_keys = len(cache_info) if isinstance(cache_info, dict) else 'N/A'
                
                self.stdout.write(f"   Entradas antes: {num_keys}")
                
                # Limpar
                cache.clear()
                
                self.stdout.write(self.style.SUCCESS("   ✅ Django Cache limpo!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))

        # 2. Limpar Analysis Cache
        if analysis_only:
            self.stdout.write("")
            self.stdout.write("📊 Limpando Analysis Cache (custom)...")
            try:
                # Stats antes
                stats = analysis_cache.stats()
                self.stdout.write(f"   Entradas antes: {stats.get('size', 0)}")
                self.stdout.write(f"   Hits: {stats.get('hits', 0)}")
                self.stdout.write(f"   Misses: {stats.get('misses', 0)}")
                
                # Limpar
                analysis_cache.clear()
                
                self.stdout.write(self.style.SUCCESS("   ✅ Analysis Cache limpo!"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))

        self.stdout.write("")
        self.stdout.write("="*80)
        self.stdout.write(self.style.SUCCESS("✅ CACHE LIMPO COM SUCESSO!"))
        self.stdout.write("="*80)
        self.stdout.write("")
        self.stdout.write(self.style.WARNING("⚠️  PRÓXIMOS PASSOS:"))
        self.stdout.write("   1. Reinicie o servidor Django se ainda não fez")
        self.stdout.write("   2. Faça nova análise (não abra análise antiga)")
        self.stdout.write("   3. Verifique probabilidades corretas")
        self.stdout.write("")
        self.stdout.write("💡 Para apenas limpar cache (sem reiniciar servidor):")
        self.stdout.write("   python manage.py clear_cache")
        self.stdout.write("")
