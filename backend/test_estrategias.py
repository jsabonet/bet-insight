"""
Teste de Diferenciação de Estratégias: VALUE vs MÚLTIPLO
Simula análise completa do jogo Freiburg vs Bremen
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.matches.models import Match
from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator

def print_separator(title="", char="="):
    """Imprime separador formatado"""
    print(f"\n{char*80}")
    if title:
        print(f"{title}")
        print(f"{char*80}")

def print_analysis_result(result, strategy_name):
    """Imprime resultado da análise de forma formatada"""
    print_separator(f"RESULTADO - {strategy_name}")
    
    # Probabilidades
    probs = result.get('probabilities', {})
    print(f"\nProbabilidades:")
    print(f"   Casa: {probs.get('home_win', 0):.1%}")
    print(f"   Empate: {probs.get('draw', 0):.1%}")
    print(f"   Fora: {probs.get('away_win', 0):.1%}")
    
    # Top Bets
    top_bets = result.get('top_bets', [])
    print(f"\nTop {len(top_bets)} Apostas:")
    
    if top_bets:
        for bet in top_bets[:3]:
            print(f"\n   #{bet.get('rank', '?')} {bet.get('market_display', 'N/A')}")
            print(f"      Probabilidade: {bet.get('probability', 0):.1%}")
            print(f"      Odd: {bet.get('market_odd', 'N/A')}")
            print(f"      EV: {bet.get('ev_pct', 0):+.1f}%")
            print(f"      Stake: {bet.get('stake_units', 0):.1f}u")
            reason = bet.get('reason', 'N/A')
            if len(reason) > 80:
                reason = reason[:77] + "..."
            print(f"      Razao: {reason}")
    else:
        print("   (Nenhuma aposta gerada)")
    
    # Recomendação
    rec = result.get('recommendation', {})
    if rec:
        print(f"\nRecomendacao Principal:")
        print(f"   {rec.get('market_display', 'N/A')}")
        print(f"   Probabilidade: {rec.get('probability', 0):.1%}")
        print(f"   Odd: {rec.get('odd', 'N/A')}")
        print(f"   EV: {rec.get('ev', 0):+.1f}%")
    
    return top_bets

def main():
    """Função principal de teste"""
    print_separator("TESTE DE DIFERENCIACAO DE ESTRATEGIAS")
    
    # Buscar jogo
    try:
        match = Match.objects.get(id=3115)  # Freiburg vs Bremen
        print(f"\nJogo: {match.home_team.name} vs {match.away_team.name}")
        print(f"Data: {match.match_date}")
        print(f"Liga: {match.league.name if match.league else 'N/A'}")
    except Match.DoesNotExist:
        print("\nJogo nao encontrado (ID: 3115)")
        print("Buscando qualquer jogo disponivel...")
        match = Match.objects.filter(api_football_id__isnull=False).first()
        if not match:
            print("Nenhum jogo disponivel no banco de dados")
            return
        print(f"\nUsando: {match.home_team.name} vs {match.away_team.name}")
    
    # Criar orchestrator
    orchestrator = HybridAnalysisOrchestrator()
    
    # TESTE 1: VALUE BET
    print_separator("EXECUTANDO ANALISE 1/2: VALUE BET", "-")
    print("Processando...")
    
    try:
        result_value = orchestrator.run(match, strategy='value')
        top_bets_value = print_analysis_result(result_value, "VALUE BET")
    except Exception as e:
        print(f"\nERRO na analise VALUE: {e}")
        import traceback
        traceback.print_exc()
        top_bets_value = []
    
    # TESTE 2: MÚLTIPLO
    print_separator("EXECUTANDO ANALISE 2/2: MULTIPLO", "-")
    print("Processando...")
    
    try:
        result_multiple = orchestrator.run(match, strategy='multiple')
        top_bets_multiple = print_analysis_result(result_multiple, "MULTIPLO")
    except Exception as e:
        print(f"\nERRO na analise MULTIPLO: {e}")
        import traceback
        traceback.print_exc()
        top_bets_multiple = []
    
    # COMPARAÇÃO
    print_separator("COMPARACAO ENTRE ESTRATEGIAS")
    
    if top_bets_value and top_bets_multiple:
        value_top = top_bets_value[0]
        multiple_top = top_bets_multiple[0]
        
        print(f"\nTop #1 de cada estrategia:")
        print(f"\n   VALUE BET:")
        print(f"      Mercado: {value_top.get('market_display', 'N/A')}")
        print(f"      Probabilidade: {value_top.get('probability', 0):.1%}")
        print(f"      EV: {value_top.get('ev_pct', 0):+.1f}%")
        print(f"      Score: {value_top.get('score', 0):.3f}")
        
        print(f"\n   MULTIPLO:")
        print(f"      Mercado: {multiple_top.get('market_display', 'N/A')}")
        print(f"      Probabilidade: {multiple_top.get('probability', 0):.1%}")
        print(f"      EV: {multiple_top.get('ev_pct', 0):+.1f}%")
        print(f"      Score: {multiple_top.get('score', 0):.3f}")
        
        print(f"\n{'='*80}")
        
        # Verificar diferenciação
        if value_top.get('market_display') != multiple_top.get('market_display'):
            print(f"ESTRATEGIAS DIFERENCIADAS!")
            print(f"   VALUE priorizou: {value_top.get('market_display')} (EV {value_top.get('ev_pct', 0):+.1f}%)")
            print(f"   MULTIPLO priorizou: {multiple_top.get('market_display')} (Prob {multiple_top.get('probability', 0):.1%})")
        else:
            print(f"Mesma recomendacao nos dois modos:")
            print(f"   {value_top.get('market_display')}")
            print(f"   (Pode acontecer quando o mesmo mercado tem melhor EV E melhor probabilidade)")
        
        print(f"{'='*80}")
    else:
        print("\nNao foi possivel comparar (apostas nao geradas)")
        print(f"{'='*80}")

if __name__ == '__main__':
    main()
