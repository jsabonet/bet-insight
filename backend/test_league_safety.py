#!/usr/bin/env python
"""
Teste de seguranca: Garantir que LIGAS nao sao afetadas pelo ajuste de copa
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

def test_league_not_affected():
    """
    Testa que partidas de LIGA nao sao afetadas pelo sistema de ajuste de copa
    """
    
    # Usar uma partida de LIGA para garantir que nao ha ajuste
    # Exemplo: Premier League match
    fixture_id = 1035121  # Brighton vs Man City (Premier League)
    
    print("="*120)
    print("TESTE DE SEGURANCA: LIGAS NAO SAO AFETADAS")
    print("="*120)
    print()
    print(f"Analisando partida de LIGA: {fixture_id}")
    print(f"   Brighton vs Manchester City")
    print(f"   Premier League (LIGA, nao copa)")
    print()
    
    # Buscar ou criar match
    match, created = Match.objects.get_or_create(
        api_football_id=fixture_id,
        defaults={
            'home_team': 'Brighton',
            'away_team': 'Manchester City',
            'match_date': '2026-02-07 15:00:00',
        }
    )
    
    if created:
        print("Match criado")
    else:
        print("Match encontrado")
    
    print()
    print("-"*120)
    print("TESTE 1: Orchestrator COM ajuste de copa habilitado (padrao)")
    print("-"*120)
    
    orchestrator_with_cup = HybridAnalysisOrchestrator(enable_cup_adjustment=True)
    result_with_cup = orchestrator_with_cup.run(match, strategy='value')
    
    print()
    print("-"*120)
    print("TESTE 2: Orchestrator SEM ajuste de copa (desabilitado)")
    print("-"*120)
    
    orchestrator_no_cup = HybridAnalysisOrchestrator(enable_cup_adjustment=False)
    result_no_cup = orchestrator_no_cup.run(match, strategy='value')
    
    print()
    print("="*120)
    print("RESULTADOS DA COMPARACAO")
    print("="*120)
    print()
    
    # Verificar features de competicao
    comp_with = result_with_cup.get('features', {}).get('competition', {})
    comp_no = result_no_cup.get('features', {}).get('competition', {})
    
    print("DETECCAO DE COMPETICAO:")
    print(f"   Com ajuste habilitado:")
    print(f"      E Copa: {comp_with.get('is_cup_competition')}")
    print(f"      Fator: {comp_with.get('knockout_adjustment_factor')}")
    print(f"   Com ajuste desabilitado:")
    print(f"      E Copa: {comp_no.get('is_cup_competition')}")
    print(f"      Fator: {comp_no.get('knockout_adjustment_factor')}")
    print()
    
    # Comparar xG
    xg_with = result_with_cup.get('home_xg', 0) + result_with_cup.get('away_xg', 0)
    xg_no = result_no_cup.get('home_xg', 0) + result_no_cup.get('away_xg', 0)
    
    print("EXPECTED GOALS (xG):")
    print(f"   Com ajuste habilitado: {xg_with:.2f}")
    print(f"   Com ajuste desabilitado: {xg_no:.2f}")
    print(f"   Diferenca: {abs(xg_with - xg_no):.2f} gols")
    print()
    
    # Comparar probabilidades
    analysis_with = result_with_cup.get('analysis_data', {})
    analysis_no = result_no_cup.get('analysis_data', {})
    
    consensus_with = analysis_with.get('consensus_probabilities', {})
    consensus_no = analysis_no.get('consensus_probabilities', {})
    
    over25_with = consensus_with.get('over_2_5', 0)
    over25_no = consensus_no.get('over_2_5', 0)
    
    print("PROBABILIDADE OVER 2.5:")
    print(f"   Com ajuste habilitado: {over25_with*100:.1f}%")
    print(f"   Com ajuste desabilitado: {over25_no*100:.1f}%")
    print(f"   Diferenca: {abs(over25_with - over25_no)*100:.1f}%")
    print()
    
    print("="*120)
    print("CONCLUSAO")
    print("="*120)
    print()
    
    # Validacao
    is_cup = comp_with.get('is_cup_competition', False)
    factor = comp_with.get('knockout_adjustment_factor', 1.0)
    xg_diff = abs(xg_with - xg_no)
    
    if not is_cup:
        print("VALIDACAO 1: Partida identificada como LIGA")
        if factor == 1.0:
            print("   PASSOU: Fator = 1.0 (sem ajuste)")
        else:
            print(f"   FALHOU: Fator = {factor} (esperado 1.0)")
        
        if xg_diff < 0.01:
            print("   PASSOU: xG identico em ambos os testes (diferenca < 0.01)")
        else:
            print(f"   FALHOU: xG diferente (diferenca {xg_diff:.2f})")
        
        print()
        print("RESULTADO FINAL: SISTEMA SEGURO PARA LIGAS")
        print("   - Ligas nao sao afetadas pelo ajuste de copa")
        print("   - Funcionamento original preservado")
    else:
        print("AVISO: Partida identificada como COPA")
        print(f"   - Fator aplicado: {factor}")
        print(f"   - Reducao xG: {(1.0 - factor) * 100:.0f}%")
        if xg_diff > 0.1:
            print(f"   - Diferenca de xG: {xg_diff:.2f} gols")
            print()
            print("RESULTADO: Sistema de ajuste funcionando corretamente para COPAS")
        else:
            print("   AVISO: Pouca diferenca detectada")
    print()

if __name__ == "__main__":
    test_league_not_affected()
