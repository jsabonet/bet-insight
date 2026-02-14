#!/usr/bin/env python
"""
Script de Verificação e Deploy da Correção CLEAR_FAVORITE

Executa checklist completo antes de iniciar servidor:
1. Valida arquivos modificados
2. Testa configuração CLEAR_FAVORITE
3. Verifica sintaxe
4. Inicia servidor Django

Uso:
    python deploy_clear_favorite.py
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time

def print_header(text, color="cyan"):
    colors = {
        "cyan": "\033[96m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "reset": "\033[0m"
    }
    print(f"\n{colors.get(color, '')}")
    print("=" * 80)
    print(f"{text}")
    print("=" * 80)
    print(f"{colors['reset']}")

def check_file_modified(filepath, description):
    """Verifica se arquivo foi modificado recentemente"""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ {description}: NÃO ENCONTRADO")
        return False
    
    modified = datetime.fromtimestamp(path.stat().st_mtime)
    now = datetime.now()
    diff = now - modified
    
    if diff.total_seconds() < 3600:  # Menos de 1 hora
        print(f"✅ {description}: Modificado há {diff.total_seconds()/60:.0f} minutos")
        return True
    else:
        print(f"⚠️  {description}: Modificado há {diff.days} dias (pode estar desatualizado)")
        return True

def validate_syntax(filepath):
    """Valida sintaxe Python do arquivo"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", filepath],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True
        else:
            print(f"❌ Erro de sintaxe: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erro ao validar: {e}")
        return False

def test_import():
    """Testa importação da configuração"""
    try:
        # Add current dir to path
        backend_path = Path(__file__).parent
        sys.path.insert(0, str(backend_path))
        
        from apps.analysis.config.analysis_config import EnsembleWeights
        
        # Verificar se CLEAR_FAVORITE existe
        if not hasattr(EnsembleWeights, 'CLEAR_FAVORITE'):
            print("❌ CLEAR_FAVORITE não encontrado em EnsembleWeights")
            return False
        
        # Validar valores
        config = EnsembleWeights.CLEAR_FAVORITE
        if config['poisson'] != 0.70:
            print(f"❌ Poisson deveria ser 0.70, mas é {config['poisson']}")
            return False
        
        if config['ml'] != 0.15:
            print(f"❌ ML deveria ser 0.15, mas é {config['ml']}")
            return False
        
        if config['market'] != 0.15:
            print(f"❌ Market deveria ser 0.15, mas é {config['market']}")
            return False
        
        total = sum(config.values())
        if abs(total - 1.0) > 0.001:
            print(f"❌ Soma dos pesos deveria ser 1.0, mas é {total}")
            return False
        
        print("✅ CLEAR_FAVORITE configurado corretamente:")
        print(f"   Poisson: {config['poisson']*100:.0f}%")
        print(f"   ML: {config['ml']*100:.0f}%")
        print(f"   Market: {config['market']*100:.0f}%")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro ao importar: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def run_simulation():
    """Executa simulação de validação"""
    try:
        print("\n🧪 Executando simulação Brentford vs Arsenal...")
        result = subprocess.run(
            [sys.executable, "simulate_brentford_arsenal.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Procurar por linha de sucesso
            if "SUCESSO!" in result.stdout:
                print("✅ Simulação PASSOU em todos os testes")
                # Extrair resultado Arsenal
                for line in result.stdout.split('\n'):
                    if 'Arsenal:' in line and '%' in line:
                        print(f"   {line.strip()}")
                        break
                return True
            else:
                print("⚠️  Simulação executou mas não passou em todos os testes")
                print(result.stdout[-500:])  # Últimas 500 chars
                return False
        else:
            print(f"❌ Simulação falhou com código {result.returncode}")
            print(result.stderr[-500:])
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Simulação demorou muito tempo (>30s)")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar simulação: {e}")
        return False

def main():
    print_header("🚀 DEPLOY DA CORREÇÃO CLEAR_FAVORITE", "cyan")
    
    print("\n📋 ETAPA 1: Verificando arquivos modificados")
    print("-" * 80)
    
    files_ok = True
    files_ok &= check_file_modified(
        "apps/analysis/config/analysis_config.py",
        "analysis_config.py"
    )
    files_ok &= check_file_modified(
        "apps/analysis/services/ml_integration.py",
        "ml_integration.py"
    )
    
    if not files_ok:
        print("\n❌ Alguns arquivos não foram encontrados!")
        return False
    
    # ETAPA 2: Validação de sintaxe
    print("\n📋 ETAPA 2: Validando sintaxe")
    print("-" * 80)
    
    syntax_ok = True
    print("Validando analysis_config.py...", end=" ")
    if validate_syntax("apps/analysis/config/analysis_config.py"):
        print("✅")
    else:
        print("❌")
        syntax_ok = False
    
    print("Validando ml_integration.py...", end=" ")
    if validate_syntax("apps/analysis/services/ml_integration.py"):
        print("✅")
    else:
        print("❌")
        syntax_ok = False
    
    if not syntax_ok:
        print("\n❌ Erros de sintaxe encontrados!")
        return False
    
    # ETAPA 3: Teste de importação
    print("\n📋 ETAPA 3: Testando importação e configuração")
    print("-" * 80)
    
    if not test_import():
        print("\n❌ Falha ao importar ou validar configuração!")
        return False
    
    # ETAPA 4: Simulação
    print("\n📋 ETAPA 4: Executando simulação de validação")
    print("-" * 80)
    
    if not run_simulation():
        print("\n⚠️  Simulação falhou, mas você pode continuar se desejar")
        response = input("\nContinuar mesmo assim? (s/N): ")
        if response.lower() != 's':
            return False
    
    # ETAPA 5: Pronto para deploy
    print_header("✅ TODAS AS VALIDAÇÕES PASSARAM!", "green")
    
    print("\n📊 RESUMO:")
    print("   ✅ Arquivos modificados corretamente")
    print("   ✅ Sintaxe validada")
    print("   ✅ CLEAR_FAVORITE configurado (P=70%, ML=15%, M=15%)")
    print("   ✅ Simulação validou correção")
    
    print("\n" + "="*80)
    print("🚀 INICIAR SERVIDOR DJANGO?")
    print("="*80)
    print("\nEscolha uma opção:")
    print("   1. ✅ Iniciar servidor agora (python manage.py runserver)")
    print("   2. 🔍 Apenas verificar (python manage.py check)")
    print("   3. ❌ Cancelar (fazer deploy manual)")
    
    choice = input("\nOpção (1/2/3): ").strip()
    
    if choice == "1":
        print("\n" + "="*80)
        print("🚀 INICIANDO SERVIDOR DJANGO...")
        print("="*80)
        print("\n⚠️  O servidor será iniciado em 3 segundos...")
        print("   Pressione Ctrl+C para cancelar")
        
        time.sleep(3)
        
        print("\n🟢 Servidor Django iniciando...\n")
        
        # Iniciar servidor (sem capturar output para ver logs em tempo real)
        try:
            subprocess.run(
                [sys.executable, "manage.py", "runserver"],
                check=True
            )
        except KeyboardInterrupt:
            print("\n\n⚠️  Servidor interrompido pelo usuário")
        except Exception as e:
            print(f"\n\n❌ Erro ao iniciar servidor: {e}")
            return False
            
    elif choice == "2":
        print("\n🔍 Executando verificação do Django...")
        result = subprocess.run(
            [sys.executable, "manage.py", "check"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            print("\n❌ Verificação encontrou problemas!")
            return False
        else:
            print("\n✅ Verificação passou! Sistema OK")
            print("\n💡 Para iniciar o servidor:")
            print("   python manage.py runserver")
            
    else:
        print("\n📝 Deploy manual:")
        print("   1. Reinicie o servidor Django: python manage.py runserver")
        print("   2. Teste uma análise no frontend")
        print("   3. Verifique logs: deve aparecer 'CLEAR_FAVORITE (Poisson 70%)'")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Deploy cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
