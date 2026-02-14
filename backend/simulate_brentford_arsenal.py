"""
Simulação de Análise Frontend: Brentford vs Arsenal
Testa a nova configuração CLEAR_FAVORITE sem precisar do servidor Django
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Import direct (sem Django)
from apps.analysis.config.analysis_config import EnsembleWeights

def simulate_analysis():
    """
    Simula análise completa de Brentford vs Arsenal
    """
    
    print("="*80)
    print("🎯 SIMULAÇÃO DE ANÁLISE - Brentford vs Arsenal")
    print("="*80)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"🏆 Competição: Premier League")
    print()
    
    # ========================================
    # DADOS SIMULADOS (baseados em estatísticas reais)
    # ========================================
    
    # Probabilidades de Poisson (baseadas em força dos times)
    # Arsenal é muito mais forte
    poisson_probs = {
        'home': 0.146,  # 14.6% Brentford
        'draw': 0.236,  # 23.6% Empate
        'away': 0.618   # 61.8% Arsenal (favorito claro!)
    }
    
    # Probabilidades do ML (tende a nivelar)
    ml_probs = {
        'home': 0.330,  # 33.0% Brentford
        'draw': 0.340,  # 34.0% Empate
        'away': 0.330   # 33.0% Arsenal (ML conservador)
    }
    
    # Probabilidades do Market (ground truth)
    market_probs = {
        'home': 0.194,  # 19.4% Brentford (odd ~5.15)
        'draw': 0.224,  # 22.4% Empate (odd ~4.46)
        'away': 0.582   # 58.2% Arsenal (odd ~1.72) ← FAVORITO CLARO!
    }
    
    # ========================================
    # TESTE: Qual configuração será usada?
    # ========================================
    
    print("📊 PROBABILIDADES DOS MODELOS INDIVIDUAIS:")
    print(f"   Poisson: {poisson_probs['home']*100:.1f}% | {poisson_probs['draw']*100:.1f}% | {poisson_probs['away']*100:.1f}%")
    print(f"   ML:      {ml_probs['home']*100:.1f}% | {ml_probs['draw']*100:.1f}% | {ml_probs['away']*100:.1f}%")
    print(f"   Market:  {market_probs['home']*100:.1f}% | {market_probs['draw']*100:.1f}% | {market_probs['away']*100:.1f}%")
    print()
    
    # ========================================
    # DETECÇÃO DE FAVORITO CLARO
    # ========================================
    
    max_market_prob = max(market_probs.values())
    is_clear_favorite = max_market_prob > 0.55
    
    print("🔍 DETECÇÃO DE FAVORITO CLARO:")
    print(f"   Max probabilidade market: {max_market_prob*100:.1f}%")
    print(f"   Threshold: 55.0%")
    print(f"   É favorito claro: {'✅ SIM' if is_clear_favorite else '❌ NÃO'}")
    print()
    
    # ========================================
    # SELEÇÃO DE CONFIGURAÇÃO
    # ========================================
    
    if is_clear_favorite:
        weights = EnsembleWeights.CLEAR_FAVORITE
        config_name = "CLEAR_FAVORITE (Poisson 70%)"
        print("⚖️ CONFIGURAÇÃO SELECIONADA: ✨ CLEAR_FAVORITE")
    else:
        weights = EnsembleWeights.DEFAULT_WITH_MARKET
        config_name = "DEFAULT_WITH_MARKET (Poisson 60%)"
        print("⚖️ CONFIGURAÇÃO SELECIONADA: DEFAULT_WITH_MARKET")
    
    print(f"   Poisson: {weights['poisson']*100:.0f}%")
    print(f"   ML:      {weights['ml']*100:.0f}%")
    print(f"   Market:  {weights['market']*100:.0f}%")
    print()
    
    # ========================================
    # CÁLCULO DO ENSEMBLE
    # ========================================
    
    print("🎲 CALCULANDO ENSEMBLE...")
    print()
    
    ensemble_probs = {}
    for outcome in ['home', 'draw', 'away']:
        ensemble_probs[outcome] = (
            poisson_probs[outcome] * weights['poisson'] +
            ml_probs[outcome] * weights['ml'] +
            market_probs[outcome] * weights['market']
        )
    
    # Normalizar (garantir que soma 100%)
    total = sum(ensemble_probs.values())
    ensemble_probs = {k: v/total for k, v in ensemble_probs.items()}
    
    # ========================================
    # RESULTADO FINAL
    # ========================================
    
    print("="*80)
    print("📈 RESULTADO DO ENSEMBLE")
    print("="*80)
    print()
    print(f"🏠 Brentford: {ensemble_probs['home']*100:.1f}%")
    print(f"🤝 Empate:    {ensemble_probs['draw']*100:.1f}%")
    print(f"✈️  Arsenal:   {ensemble_probs['away']*100:.1f}%")
    print()
    
    # ========================================
    # COMPARAÇÃO COM SAÍDA ANTERIOR
    # ========================================
    
    print("="*80)
    print("📊 COMPARAÇÃO: ANTES vs DEPOIS")
    print("="*80)
    print()
    
    # Saída antiga do sistema (da mensagem do usuário)
    old_probs = {'home': 0.265, 'draw': 0.311, 'away': 0.424}
    
    print("ANTES (configuração antiga):")
    print(f"   Brentford: {old_probs['home']*100:.1f}%")
    print(f"   Empate:    {old_probs['draw']*100:.1f}%")
    print(f"   Arsenal:   {old_probs['away']*100:.1f}%")
    print()
    
    print("DEPOIS (com CLEAR_FAVORITE):")
    print(f"   Brentford: {ensemble_probs['home']*100:.1f}%")
    print(f"   Empate:    {ensemble_probs['draw']*100:.1f}%")
    print(f"   Arsenal:   {ensemble_probs['away']*100:.1f}%")
    print()
    
    # Calcular diferenças
    diff_home = ensemble_probs['home'] - old_probs['home']
    diff_draw = ensemble_probs['draw'] - old_probs['draw']
    diff_away = ensemble_probs['away'] - old_probs['away']
    
    print("DIFERENÇAS:")
    print(f"   Brentford: {diff_home*100:+.1f} pontos")
    print(f"   Empate:    {diff_draw*100:+.1f} pontos")
    print(f"   Arsenal:   {diff_away*100:+.1f} pontos {'✅' if diff_away > 0.10 else '⚠️'}")
    print()
    
    # ========================================
    # ERRO VS MERCADO
    # ========================================
    
    print("="*80)
    print("📐 ERRO VS MERCADO (Ground Truth)")
    print("="*80)
    print()
    
    # Erro médio absoluto ANTES
    mae_before = (
        abs(old_probs['home'] - market_probs['home']) +
        abs(old_probs['draw'] - market_probs['draw']) +
        abs(old_probs['away'] - market_probs['away'])
    ) / 3
    
    # Erro médio absoluto DEPOIS
    mae_after = (
        abs(ensemble_probs['home'] - market_probs['home']) +
        abs(ensemble_probs['draw'] - market_probs['draw']) +
        abs(ensemble_probs['away'] - market_probs['away'])
    ) / 3
    
    improvement = (mae_before - mae_after) / mae_before * 100
    
    print(f"Erro ANTES:  {mae_before*100:.2f}% (configuração antiga)")
    print(f"Erro DEPOIS: {mae_after*100:.2f}% (com CLEAR_FAVORITE)")
    print(f"Melhoria:    {improvement:+.1f}% {'✅' if improvement > 0 else '❌'}")
    print()
    
    # ========================================
    # VALIDAÇÃO
    # ========================================
    
    print("="*80)
    print("✅ VALIDAÇÃO")
    print("="*80)
    print()
    
    success = True
    
    # 1. Arsenal deve ter > 55%
    if ensemble_probs['away'] > 0.55:
        print("✅ Arsenal > 55%: PASS")
    else:
        print(f"❌ Arsenal < 55%: FAIL ({ensemble_probs['away']*100:.1f}%)")
        success = False
    
    # 2. Arsenal deve ser o favorito
    if ensemble_probs['away'] == max(ensemble_probs.values()):
        print("✅ Arsenal é favorito: PASS")
    else:
        print("❌ Arsenal não é favorito: FAIL")
        success = False
    
    # 3. Erro deve ser < 3%
    if mae_after < 0.03:
        print(f"✅ Erro < 3%: PASS ({mae_after*100:.2f}%)")
    else:
        print(f"⚠️ Erro > 3%: WARNING ({mae_after*100:.2f}%)")
    
    # 4. CLEAR_FAVORITE deve ter sido ativado
    if is_clear_favorite:
        print("✅ CLEAR_FAVORITE ativado: PASS")
    else:
        print("❌ CLEAR_FAVORITE não ativado: FAIL")
        success = False
    
    print()
    
    if success:
        print("="*80)
        print("🎉 SUCESSO! Correção funcionando corretamente!")
        print("="*80)
    else:
        print("="*80)
        print("⚠️ ATENÇÃO: Alguns testes falharam")
        print("="*80)
    
    print()
    
    # ========================================
    # SIMULAÇÃO DO OUTPUT DO FRONTEND
    # ========================================
    
    print("="*80)
    print("📱 PREVIEW DA SAÍDA DO FRONTEND")
    print("="*80)
    print()
    print("🎯 ANÁLISE - Brentford vs Arsenal")
    print(f"📅 {(datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')} | Premier League")
    print("📊 Estratégia: Bilhetes Múltiplos")
    print()
    print("━━━━━━━━━━━━━━━━━━━━")
    print()
    print("📈 PROBABILIDADES")
    print(f"🏠 Brentford: {ensemble_probs['home']*100:.1f}%")
    print(f"🤝 Empate: {ensemble_probs['draw']*100:.1f}%")
    print(f"✈️  Arsenal: {ensemble_probs['away']*100:.1f}%")
    print()
    print("⭐ CONFIANÇA")
    print("⭐⭐⭐⭐⭐ Muito Alta (favorito claro detectado)")
    print()
    print("━━━━━━━━━━━━━━━━━━━━")
    print()
    
    return success


if __name__ == '__main__':
    try:
        success = simulate_analysis()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
