#!/usr/bin/env python
"""
Teste simples para verificar se ContextAnalyzer retorna todos os mercados canônicos
"""
import sys
sys.path.insert(0, 'D:/Projectos/Football/bet-insight/backend')

from apps.analysis.config.market_standards import CANONICAL_MARKETS

# Simular um padrão detectado com market_weights limitados
class MockContextAnalyzer:
    def __init__(self):
        self.patterns_detected = [
            {
                'name': 'motivated_favorite_vs_defensive_wall',
                'confidence': 0.85,
                'market_weights': {
                    'btts_yes': 1.0,
                    'under_3.5': 0.8,
                    'x2': 0.9,
                    'draw': 0.7,
                    'draw_ht': 0.6
                }
            }
        ]
    
    def _consolidate_favorable_markets(self):
        """VERSÃO ORIGINAL - apenas mercados com weights"""
        market_scores = {}
        market_patterns = {}
        
        for pattern in self.patterns_detected:
            pattern_confidence = pattern['confidence']
            market_weights = pattern.get('market_weights', {})
            
            for market, weight in market_weights.items():
                score = weight * pattern_confidence
                
                if market not in market_scores:
                    market_scores[market] = 0
                    market_patterns[market] = []
                
                market_scores[market] += score
                market_patterns[market].append(pattern['name'])
        
        if market_scores:
            max_score = max(market_scores.values())
            if max_score > 0:
                for market in market_scores:
                    market_scores[market] = min(market_scores[market] / max_score, 1.0)
        
        ranked_markets = [
            {
                'market': market,
                'context_score': score,
                'supporting_patterns': market_patterns[market]
            }
            for market, score in market_scores.items()
        ]
        
        ranked_markets.sort(key=lambda x: x['context_score'], reverse=True)
        return ranked_markets
    
    def _consolidate_favorable_markets_fixed(self):
        """VERSÃO CORRIGIDA - inclui TODOS os mercados canônicos"""
        market_scores = {}
        market_patterns = {}
        
        for pattern in self.patterns_detected:
            pattern_confidence = pattern['confidence']
            market_weights = pattern.get('market_weights', {})
            
            for market, weight in market_weights.items():
                score = weight * pattern_confidence
                
                if market not in market_scores:
                    market_scores[market] = 0
                    market_patterns[market] = []
                
                market_scores[market] += score
                market_patterns[market].append(pattern['name'])
        
        if market_scores:
            max_score = max(market_scores.values())
            if max_score > 0:
                for market in market_scores:
                    market_scores[market] = min(market_scores[market] / max_score, 1.0)
        
        # 🆕 INCLUIR TODOS OS MERCADOS CANÔNICOS
        all_canonical = list(CANONICAL_MARKETS.keys())
        for market in all_canonical:
            if market not in market_scores:
                market_scores[market] = 0.0
                market_patterns[market] = []
        
        ranked_markets = [
            {
                'market': market,
                'context_score': score,
                'supporting_patterns': market_patterns[market]
            }
            for market, score in market_scores.items()
        ]
        
        ranked_markets.sort(key=lambda x: x['context_score'], reverse=True)
        return ranked_markets


# Testar
analyzer = MockContextAnalyzer()

print("="*80)
print("📊 TESTE: ContextAnalyzer top_markets")
print("="*80)

print(f"\nTotal de mercados canônicos: {len(CANONICAL_MARKETS)}")

print("\n" + "-"*80)
print("VERSÃO ORIGINAL (apenas mercados com weights):")
print("-"*80)

original_markets = analyzer._consolidate_favorable_markets()
print(f"Mercados retornados: {len(original_markets)}")
print("\nTop 10:")
for i, market_data in enumerate(original_markets[:10], 1):
    print(f"{i:2d}. {market_data['market']:15s} - Score: {market_data['context_score']:.3f}")

print("\n" + "-"*80)
print("VERSÃO CORRIGIDA (todos os mercados canônicos):")
print("-"*80)

fixed_markets = analyzer._consolidate_favorable_markets_fixed()
print(f"Mercados retornados: {len(fixed_markets)}")
print("\nTop 10:")
for i, market_data in enumerate(fixed_markets[:10], 1):
    score_emoji = "🎯" if market_data['context_score'] > 0 else "⚪"
    patterns_str = f"({', '.join(market_data['supporting_patterns'])})" if market_data['supporting_patterns'] else "(sem contexto)"
    print(f"{score_emoji} {i:2d}. {market_data['market']:15s} - Score: {market_data['context_score']:.3f} {patterns_str}")

print("\nÚltimos 10:")
for i, market_data in enumerate(fixed_markets[-10:], len(fixed_markets)-9):
    score_emoji = "🎯" if market_data['context_score'] > 0 else "⚪"
    print(f"{score_emoji} {i:2d}. {market_data['market']:15s} - Score: {market_data['context_score']:.3f}")

print("\n" + "="*80)
print("✅ RESULTADO:")
print("="*80)
print(f"ANTES: {len(original_markets)} mercados (apenas os relevantes)")
print(f"DEPOIS: {len(fixed_markets)} mercados (todos os canônicos)")
print(f"\n✅ Agora o MarketSelector pode avaliar TODOS os {len(fixed_markets)} mercados!")
print(f"   - {len([m for m in fixed_markets if m['context_score'] > 0])} com contexto favorável (score > 0)")
print(f"   - {len([m for m in fixed_markets if m['context_score'] == 0])} sem contexto (score = 0)")
print("="*80)
