"""
Análise completa da partida 1388503
Modo: MÚLTIPLAS APOSTAS (BILHETE)
Mostra TODOS os mercados analisados com probabilidades
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.analysis_orchestrator import HybridAnalysisOrchestrator
from apps.matches.models import Match

def test_match_1388503():
    """Análise completa da partida 1388503"""
    print("\n" + "="*100)
    print("ANÁLISE COMPLETA - PARTIDA 1388503")
    print("MODO: MÚLTIPLAS APOSTAS (BILHETE)")
    print("="*100)
    
    # Buscar partida pelo API Football ID
    try:
        match = Match.objects.get(api_football_id=1388503)
        print(f"\n🏟️  PARTIDA: {match.home_team.name} vs {match.away_team.name}")
        print(f"   Liga: {match.league.name}")
        print(f"   Data: {match.match_date}")
        print(f"   ID Interno: {match.id}")
    except Match.DoesNotExist:
        print(f"\n❌ Partida com API ID 1388503 não encontrada no banco!")
        print(f"   Verifique se a partida foi importada do API-Football")
        return
    
    orchestrator = HybridAnalysisOrchestrator()
    
    # Analisar partida no modo MÚLTIPLAS
    print("\n" + "-"*100)
    print("🔄 EXECUTANDO ANÁLISE... (modo: MULTIPLE)")
    print("-"*100)
    
    result = orchestrator.run(match, strategy='multiple')
    
    # Extrair dados
    analysis_data = result.get('analysis_data', {})
    consensus = analysis_data.get('consensus', {})
    poisson = analysis_data.get('poisson', {})
    ml_predictions = analysis_data.get('ml_predictions', {})
    
    # Informações básicas
    print("\n" + "="*100)
    print("📊 INFORMAÇÕES BÁSICAS")
    print("="*100)
    
    print(f"\n   Home xG: {result.get('home_xg', 0):.2f}")
    print(f"   Away xG: {result.get('away_xg', 0):.2f}")
    print(f"   Total xG: {result.get('home_xg', 0) + result.get('away_xg', 0):.2f}")
    
    print(f"\n   Home Win: {result.get('home_probability', 0):.1f}%")
    print(f"   Draw: {result.get('draw_probability', 0):.1f}%")
    print(f"   Away Win: {result.get('away_probability', 0):.1f}%")
    
    print(f"\n   Predição: {result.get('prediction_display', 'N/A')}")
    print(f"   Confiança: {result.get('confidence_display', 'N/A')}")
    
    # CONSENSUS - Todos os mercados
    print("\n" + "="*100)
    print("🎯 CONSENSUS - TODOS OS MERCADOS ANALISADOS")
    print("="*100)
    print(f"\n   Total de mercados: {len(consensus)}")
    print("\n   " + "-"*96)
    print(f"   {'MERCADO':<30} {'PROBABILIDADE':>15} {'CONFIDENCE':>15} {'TIPO':>30}")
    print("   " + "-"*96)
    
    # Ordenar por probabilidade
    for market, prob in sorted(consensus.items(), key=lambda x: x[1], reverse=True):
        # Determinar tipo de mercado
        if market in ['home_win', 'draw', 'away_win']:
            tipo = '1X2'
        elif 'over' in market or 'under' in market:
            tipo = 'Over/Under'
        elif 'btts' in market:
            tipo = 'BTTS'
        elif 'dc' in market or '12' in market:
            tipo = 'Double Chance'
        elif 'clean_sheet' in market:
            tipo = 'Clean Sheet'
        elif 'ht' in market:
            tipo = 'Half Time'
        elif 'ft' in market:
            tipo = 'Full Time'
        elif 'odd' in market or 'even' in market:
            tipo = 'Par/Ímpar'
        else:
            tipo = 'Outros'
        
        # Determinar nível de confiança
        if prob >= 0.75:
            confidence = '⭐⭐⭐ ALTA'
        elif prob >= 0.60:
            confidence = '⭐⭐ BOA'
        elif prob >= 0.45:
            confidence = '⭐ MODERADA'
        else:
            confidence = '⚪ BAIXA'
        
        print(f"   {market:<30} {prob:>14.1%} {confidence:>15} {tipo:>30}")
    
    # TOP BETS SELECIONADAS
    print("\n" + "="*100)
    print("🏆 TOP 3 APOSTAS SELECIONADAS (MODO MÚLTIPLAS)")
    print("="*100)
    
    top_bets = analysis_data.get('top_bets', [])
    if top_bets:
        for bet in top_bets:
            print(f"\n   #{bet.get('rank', '?')} {bet.get('market_display', 'Unknown')}")
            print(f"      Mercado Técnico: {bet.get('market_type', 'N/A')}")
            print(f"      Probabilidade: {bet.get('probability', 0):.1%}")
            print(f"      Context Score: {bet.get('context_score', 0):.1%}")
            print(f"      Selection Score: {bet.get('selection_score', 0):.3f}")
            print(f"      Odd: {bet.get('market_odd', 'N/A')}")
            print(f"      EV: {bet.get('expected_value', 0):+.1f}%")
            print(f"      Raciocínio: {bet.get('reasoning', 'N/A')[:150]}...")
    else:
        print("\n   ⚠️ Nenhuma aposta foi selecionada!")
    
    # POISSON - Probabilidades base
    print("\n" + "="*100)
    print("📐 POISSON - PROBABILIDADES BASE")
    print("="*100)
    
    poisson_probs = poisson.get('probabilities', {})
    print(f"\n   Total de mercados: {len(poisson_probs)}")
    print("\n   " + "-"*60)
    print(f"   {'MERCADO':<30} {'PROBABILIDADE':>25}")
    print("   " + "-"*60)
    
    for market, prob in sorted(poisson_probs.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"   {market:<30} {prob:>24.1%}")
    
    # ML PREDICTIONS
    if ml_predictions:
        print("\n" + "="*100)
        print("🤖 MACHINE LEARNING - PREVISÕES")
        print("="*100)
        
        print(f"\n   Total de mercados: {len(ml_predictions)}")
        print("\n   " + "-"*60)
        print(f"   {'MERCADO':<30} {'PROBABILIDADE':>25}")
        print("   " + "-"*60)
        
        for market, prob in sorted(ml_predictions.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"   {market:<30} {prob:>24.1%}")
    
    # MERCADOS COM ALTA PROBABILIDADE
    print("\n" + "="*100)
    print("🔥 MERCADOS COM ALTA PROBABILIDADE (≥60%)")
    print("="*100)
    
    high_prob = [(m, p) for m, p in consensus.items() if p >= 0.60]
    if high_prob:
        print(f"\n   Total: {len(high_prob)} mercados")
        print("\n   " + "-"*60)
        for market, prob in sorted(high_prob, key=lambda x: x[1], reverse=True):
            print(f"   {market:<30} {prob:>24.1%}")
    else:
        print("\n   ⚠️ Nenhum mercado com probabilidade ≥60%")
    
    # MERCADOS COM CONTEXTO APLICADO
    print("\n" + "="*100)
    print("🎯 MERCADOS COM INFLUÊNCIA CONTEXTUAL")
    print("="*100)
    
    enriched_data = analysis_data.get('enriched_data', {})
    context_markets = enriched_data.get('context_markets', {})
    
    if context_markets:
        print(f"\n   Total: {len(context_markets)} mercados com contexto")
        print("\n   " + "-"*80)
        print(f"   {'MERCADO':<30} {'BOOST':>15} {'PROB FINAL':>15} {'CONTEXTO':>15}")
        print("   " + "-"*80)
        
        for market, context_data in sorted(context_markets.items(), key=lambda x: x[1].get('context_score', 0), reverse=True)[:15]:
            boost = context_data.get('context_score', 1.0)
            prob_final = consensus.get(market, 0)
            context_type = context_data.get('context_type', 'NEUTRO')
            
            print(f"   {market:<30} {boost:>14.1%} {prob_final:>15.1%} {context_type:>15}")
    else:
        print("\n   ⚠️ Nenhum mercado com influência contextual aplicada")
    
    # REASONING
    print("\n" + "="*100)
    print("💡 ANÁLISE E RACIOCÍNIO")
    print("="*100)
    
    reasoning = result.get('reasoning', '')
    if reasoning:
        print(f"\n{reasoning}\n")
    else:
        print("\n   ⚠️ Nenhum raciocínio disponível")
    
    # KEY FACTORS
    key_factors = result.get('key_factors', [])
    if key_factors:
        print("\n" + "="*100)
        print("🔑 FATORES-CHAVE")
        print("="*100)
        for i, factor in enumerate(key_factors, 1):
            print(f"\n   {i}. {factor}")
    
    print("\n" + "="*100)
    print("✅ ANÁLISE COMPLETA CONCLUÍDA")
    print("="*100 + "\n")

if __name__ == '__main__':
    test_match_1388503()
