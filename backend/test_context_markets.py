#!/usr/bin/env python
"""
Teste para verificar quantos mercados o ContextAnalyzer retorna em top_markets
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.core.models import Fixture
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def test_context_markets():
    """Testa quantos mercados o ContextAnalyzer retorna"""
    
    # Pegar uma partida real
    try:
        fixture = Fixture.objects.get(id=1387895)  # Rennes vs PSG
    except Fixture.DoesNotExist:
        logger.error("❌ Partida 1387895 não encontrada no banco")
        return
    
    logger.info("\n" + "="*80)
    logger.info("📊 TESTE: Verificar mercados em ContextAnalyzer.top_markets")
    logger.info("="*80)
    logger.info(f"Partida: {fixture.home_team.name} vs {fixture.away_team.name}")
    
    # Criar ContextAnalyzer
    analyzer = ContextAnalyzer(fixture)
    
    # Executar análise
    context_result = analyzer.analyze()
    
    # Verificar top_markets
    top_markets = context_result.get('top_markets', [])
    patterns = context_result.get('patterns', [])
    
    logger.info(f"\n✅ Padrões detectados: {len(patterns)}")
    for pattern in patterns:
        logger.info(f"   - {pattern['name']}: {pattern['confidence']:.0%} confiança")
        market_weights = pattern.get('market_weights', {})
        logger.info(f"     Markets: {len(market_weights)} mercados com pesos")
        for market, weight in list(market_weights.items())[:5]:
            logger.info(f"       • {market}: {weight:.2f}")
        if len(market_weights) > 5:
            logger.info(f"       ... e mais {len(market_weights) - 5} mercados")
    
    logger.info(f"\n✅ Top Markets retornados: {len(top_markets)} mercados")
    logger.info("\nLista completa de mercados (top 20):")
    for i, market_data in enumerate(top_markets[:20], 1):
        logger.info(f"{i:2d}. {market_data['market']:15s} - Score: {market_data['context_score']:.3f} - Padrões: {', '.join(market_data['supporting_patterns'])}")
    
    if len(top_markets) > 20:
        logger.info(f"... e mais {len(top_markets) - 20} mercados")
    
    # Resumo
    logger.info("\n" + "="*80)
    logger.info("📋 RESUMO")
    logger.info("="*80)
    logger.info(f"Total de mercados em top_markets: {len(top_markets)}")
    
    # Verificar se todos os mercados enriquecidos estão presentes
    expected_markets = ['home_win', 'draw', 'away_win', '1x', 'x2', '12', 
                       'btts_yes', 'btts_no', 'over_2.5', 'under_2.5',
                       'over_3.5', 'under_3.5', 'home_dnb', 'away_dnb']
    
    markets_in_top = [m['market'] for m in top_markets]
    missing_markets = [m for m in expected_markets if m not in markets_in_top]
    
    if missing_markets:
        logger.warning(f"\n⚠️ Mercados esperados mas AUSENTES em top_markets:")
        for market in missing_markets:
            logger.warning(f"   - {market}")
    else:
        logger.info(f"\n✅ Todos os {len(expected_markets)} mercados esperados estão presentes!")
    
    logger.info("\n" + "="*80)

if __name__ == '__main__':
    test_context_markets()
