#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    
    # FORÇAR LIMPEZA DE CACHE DE IMPORTS
    if 'runserver' in sys.argv:
        print("\n" + "=" * 80)
        print("[STARTUP] LIMPANDO CACHE DE IMPORTS ANTES DE INICIAR DJANGO...")
        print("=" * 80)
        
        # Remover módulos analysis do cache
        modules_to_remove = [k for k in sys.modules.keys() if 'apps.analysis' in k]
        for mod in modules_to_remove:
            print(f"   Removendo: {mod}")
            del sys.modules[mod]
        print(f"[OK] {len(modules_to_remove)} módulos removidos do cache\n")
        
        # Agora importar e verificar
        from apps.analysis.config.analysis_config import EnsembleWeights
        print("[CHECK] VERIFICACAO IMEDIATA - Valores carregados:")
        print(f"   DEFAULT_WITH_MARKET poisson: {EnsembleWeights.DEFAULT_WITH_MARKET['poisson']}")
        print(f"   CLEAR_FAVORITE poisson: {EnsembleWeights.CLEAR_FAVORITE['poisson']}")
        
        if EnsembleWeights.DEFAULT_WITH_MARKET['poisson'] == 0.60:
            print("   [OK] manage.py CARREGOU CODIGO NOVO!\n")
        else:
            print(f"   [ERRO] manage.py CARREGOU CODIGO ERRADO: {EnsembleWeights.DEFAULT_WITH_MARKET['poisson']}\n")
        print("=" * 80 + "\n")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
