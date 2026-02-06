#!/usr/bin/env python
"""
Teste do ajuste automatico para competicoes de copa
Compara Anderlecht vs Antwerp COM e SEM ajuste
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

def test_cup_adjustment():
    """Testa o jogo Anderlecht vs Antwerp com ajuste de copa"""
    
    # Match ID: 1508602 (Anderlecht vs Antwerp - Semifinal Copa da Belgica)
    fixture_id = 1508602
    
    print("="*120)
    print("TESTE: AJUSTE AUTOMATICO PARA COMPETICOES DE COPA")
    print("="*120)
    print()
    print(f"Analisando partida: {fixture_id}")
    print(f"   Anderlecht vs Antwerp")
    print(f"   Semifinal - Copa da Belgica (Beker van Belgie)")
    print(f"   Resultado Real: 0-1 (1 gol total)")
    print()
    
    # Buscar ou criar match
    match, created = Match.objects.get_or_create(
        api_football_id=fixture_id,
        defaults={
            'home_team': 'Anderlecht',
            'away_team': 'Antwerp',
            'match_date': '2026-02-05 20:00:00',
        }
    )
    
    if created:
        print("Match criado")
    else:
        print("Match encontrado")
    
    # Executar analise
    print()
    print("Executando analise com orchestrator...")
    print("-"*120)
    
    orchestrator = HybridAnalysisOrchestrator()
    result = orchestrator.run(match, strategy='value')
    
    print("-"*120)
    print()
    
    # Exibir resultados
    print("="*120)
    print("RESULTADOS DA ANALISE")
    print("="*120)
    print()
    
    # Verificar se foi detectada como copa
    features_all = result.get('features', {})
    if 'competition' in features_all:
        comp = features_all['competition']
        print("DETECCAO DE COMPETICAO:")
        print(f"   E Copa: {comp.get('is_cup_competition')}")
        print(f"   Nome: {comp.get('competition_name')}")
        print(f"   Fase: {comp.get('round_stage')}")
        print(f"   Fator de Ajuste: {comp.get('knockout_adjustment_factor')}")
        print()
    
    # xG Previsto
    print("EXPECTED GOALS (xG):")
    print(f"   Casa: {result.get('home_xg', 0):.2f}")
    print(f"   Fora: {result.get('away_xg', 0):.2f}")
    print(f"   Total: {result.get('home_xg', 0) + result.get('away_xg', 0):.2f}")
    print()
    
    # Comparacao com resultado real
    real_total = 1  # 0-1
    predicted_total = result.get('home_xg', 0) + result.get('away_xg', 0)
    error = abs(predicted_total - real_total)
    
    print("COMPARACAO COM RESULTADO REAL:")
    print(f"   xG Previsto: {predicted_total:.2f} gols")
    print(f"   Gols Reais: {real_total} gols")
    print(f"   Erro: {error:.2f} gols ({error/max(real_total, 0.1)*100:.1f}%)")
    print()
    
    # Over 2.5
    analysis_data = result.get('analysis_data', {})
    consensus = analysis_data.get('consensus_probabilities', {})
    over25_prob = consensus.get('over_2_5', 0)
    
    print("OVER 2.5 GOALS:")
    print(f"   Probabilidade: {over25_prob*100:.1f}%")
    print(f"   Resultado Real: NAO (apenas 1 gol)")
    
    if over25_prob > 0.5:
        print(f"   ERRO: SISTEMA previu Over com {over25_prob*100:.1f}%")
    else:
        print(f"   ACERTO: SISTEMA previu Under com {(1-over25_prob)*100:.1f}%")
    print()
    
    # Top Bets
    top_bets = result.get('top_bets', [])
    print("TOP 3 APOSTAS RECOMENDADAS:")
    for i, bet in enumerate(top_bets[:3], 1):
        print(f"   #{i}: {bet.get('market_display')} - {bet.get('probability', 0)*100:.1f}% (EV: {bet.get('ev_pct', 0):+.1f}%)")
    print()
    
    print("="*120)
    print("CONCLUSAO")
    print("="*120)
    print()
    
    # Avaliacao final
    error_threshold = 1.5
    original_error = 3.10  # Erro sem ajuste
    
    if error < error_threshold:
        improvement_pct = ((original_error - error) / original_error * 100)
        print("AJUSTE FUNCIONOU: Erro reduzido significativamente")
        print(f"   Erro anterior (sem ajuste): {original_error:.2f} gols")
        print(f"   Erro atual (com ajuste): {error:.2f} gols")
        print(f"   Melhoria: {improvement_pct:.1f}%")
    else:
        print("AJUSTE INSUFICIENTE: Erro ainda alto")
        print(f"   Erro: {error:.2f} gols")
        print("   Sugestao: Aumentar fator de reducao para semifinais")
    print()

if __name__ == "__main__":
    test_cup_adjustment()
