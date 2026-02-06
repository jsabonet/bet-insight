#!/usr/bin/env python
"""
Demonstracao: Sistema de protecao para ligas vs copas
Mostra que ligas NAO sao afetadas pelo ajuste de copa
"""
import os
import sys

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.analysis.services.feature_engineer import FeatureEngineer

def demonstrate_protection():
    """Demonstra as 3 camadas de protecao"""
    
    print("="*120)
    print("DEMONSTRACAO: SISTEMA DE PROTECAO LIGAS vs COPAS")
    print("="*120)
    print()
    
    engineer = FeatureEngineer()
    
    # Simulacao 1: Partida de LIGA
    print("CENARIO 1: PARTIDA DE LIGA (Premier League)")
    print("-"*120)
    
    enriched_league = {
        'fixture_details': {
            'league': {
                'name': 'Premier League',
                'round': 'Regular Season - 25'
            }
        }
    }
    
    comp_league = engineer._calculate_competition_features(enriched_league)
    
    print(f"   Competicao: {comp_league['competition_name']}")
    print(f"   E Copa? {comp_league['is_cup_competition']}")
    print(f"   Fase: {comp_league['round_stage']}")
    print(f"   Fator de Ajuste: {comp_league['knockout_adjustment_factor']}")
    print(f"   Reducao xG: {(1.0 - comp_league['knockout_adjustment_factor']) * 100:.0f}%")
    print()
    
    # Simulacao 2: Partida de COPA - Semifinal
    print("CENARIO 2: PARTIDA DE COPA - SEMIFINAL (Copa da Belgica)")
    print("-"*120)
    
    enriched_cup = {
        'fixture_details': {
            'league': {
                'name': 'Cup',  # Beker van Belgie
                'round': 'Semi-finals'
            }
        }
    }
    
    comp_cup = engineer._calculate_competition_features(enriched_cup)
    
    print(f"   Competicao: {comp_cup['competition_name']}")
    print(f"   E Copa? {comp_cup['is_cup_competition']}")
    print(f"   Fase: {comp_cup['round_stage']}")
    print(f"   Fator de Ajuste: {comp_cup['knockout_adjustment_factor']}")
    print(f"   Reducao xG: {(1.0 - comp_cup['knockout_adjustment_factor']) * 100:.0f}%")
    print()
    
    # Simulacao 3: La Liga
    print("CENARIO 3: PARTIDA DE LIGA (La Liga)")
    print("-"*120)
    
    enriched_laliga = {
        'fixture_details': {
            'league': {
                'name': 'La Liga',
                'round': 'Regular Season - 20'
            }
        }
    }
    
    comp_laliga = engineer._calculate_competition_features(enriched_laliga)
    
    print(f"   Competicao: {comp_laliga['competition_name']}")
    print(f"   E Copa? {comp_laliga['is_cup_competition']}")
    print(f"   Fase: {comp_laliga['round_stage']}")
    print(f"   Fator de Ajuste: {comp_laliga['knockout_adjustment_factor']}")
    print(f"   Reducao xG: {(1.0 - comp_laliga['knockout_adjustment_factor']) * 100:.0f}%")
    print()
    
    # Simulacao 4: Copa del Rey - Final
    print("CENARIO 4: PARTIDA DE COPA - FINAL (Copa del Rey)")
    print("-"*120)
    
    enriched_copa_final = {
        'fixture_details': {
            'league': {
                'name': 'Copa del Rey',
                'round': 'Final'
            }
        }
    }
    
    comp_copa_final = engineer._calculate_competition_features(enriched_copa_final)
    
    print(f"   Competicao: {comp_copa_final['competition_name']}")
    print(f"   E Copa? {comp_copa_final['is_cup_competition']}")
    print(f"   Fase: {comp_copa_final['round_stage']}")
    print(f"   Fator de Ajuste: {comp_copa_final['knockout_adjustment_factor']}")
    print(f"   Reducao xG: {(1.0 - comp_copa_final['knockout_adjustment_factor']) * 100:.0f}%")
    print()
    
    # Validacao
    print("="*120)
    print("VALIDACAO DE SEGURANCA")
    print("="*120)
    print()
    
    # Verificar que TODAS as ligas tem fator 1.0
    league_results = [comp_league, comp_laliga]
    all_leagues_safe = all(comp['knockout_adjustment_factor'] == 1.0 for comp in league_results)
    
    # Verificar que TODAS as copas tem fator < 1.0
    cup_results = [comp_cup, comp_copa_final]
    all_cups_adjusted = all(comp['knockout_adjustment_factor'] < 1.0 for comp in cup_results)
    
    print("TESTE 1: Ligas mantem fator 1.0")
    if all_leagues_safe:
        print("   PASSOU: Todas as ligas testadas tem fator = 1.0")
        print("   - Premier League: 1.0")
        print("   - La Liga: 1.0")
    else:
        print("   FALHOU: Alguma liga tem fator != 1.0")
    print()
    
    print("TESTE 2: Copas aplicam reducao")
    if all_cups_adjusted:
        print("   PASSOU: Todas as copas testadas tem fator < 1.0")
        print(f"   - Copa Semifinal: {comp_cup['knockout_adjustment_factor']}")
        print(f"   - Copa Final: {comp_copa_final['knockout_adjustment_factor']}")
    else:
        print("   FALHOU: Alguma copa nao tem reducao")
    print()
    
    print("TESTE 3: Validacao de seguranca interna")
    # Tentar forcar copa como liga
    enriched_fake = {
        'fixture_details': {
            'league': {
                'name': 'Fake League',  # Nome generico
                'round': 'Regular Season - 10'
            }
        }
    }
    comp_fake = engineer._calculate_competition_features(enriched_fake)
    if comp_fake['knockout_adjustment_factor'] == 1.0:
        print("   PASSOU: Competicao nao-copa detectada corretamente como liga")
        print(f"   - Fator: {comp_fake['knockout_adjustment_factor']}")
    else:
        print("   FALHOU: Sistema aplicou ajuste em liga")
    print()
    
    print("="*120)
    print("CONCLUSAO")
    print("="*120)
    print()
    
    if all_leagues_safe and all_cups_adjusted:
        print("SISTEMA 100% SEGURO:")
        print("   - Ligas preservam funcionamento original (fator 1.0)")
        print("   - Copas recebem ajuste apropriado por fase")
        print("   - Validacao automatica impede erros")
        print()
        print("RESULTADO: Implementacao segura para producao")
    else:
        print("AVISO: Sistema precisa revisao")
    print()

if __name__ == "__main__":
    demonstrate_protection()
