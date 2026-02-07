"""
Market Selector - Seleciona mercados baseado em contexto + probabilidades

Combina análise contextual do ContextAnalyzer com probabilidades dos modelos
para selecionar os 3 melhores mercados para apostar.

Author: AI Assistant
Date: 2026-02-07
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MarketSelector:
    """
    Seleciona top 3 mercados combinando contexto + probabilidades do modelo.
    
    Filosofia: Priorizar mercados que o CONTEXTO favorece E o modelo confirma.
    Evitar mercados com alta probabilidade mas contexto desfavorável.
    """
    
    # Mapeamento de mercados do modelo para mercados padrão
    MARKET_MAPPING = {
        # 1X2
        'home_win': 'home_win',
        'draw': 'draw',
        'away_win': 'away_win',
        
        # Double Chance
        '1X': '1X',
        '12': '12',
        'X2': 'X2',
        'home_or_draw': '1X',
        'home_or_away': '12',
        'draw_or_away': 'X2',
        
        # Totals (com ponto)
        'over_0.5': 'over_0.5',
        'over_1.5': 'over_1.5',
        'over_2.5': 'over_2.5',
        'over_3.5': 'over_3.5',
        'over_4.5': 'over_4.5',
        'under_0.5': 'under_0.5',
        'under_1.5': 'under_1.5',
        'under_2.5': 'under_2.5',
        'under_3.5': 'under_3.5',
        'under_4.5': 'under_4.5',
        
        # Totals - Aliases do Poisson (com underscore)
        'over_0_5': 'over_0.5',
        'over_1_5': 'over_1.5',
        'over_2_5': 'over_2.5',
        'over_3_5': 'over_3.5',
        'over_4_5': 'over_4.5',
        'under_0_5': 'under_0.5',
        'under_1_5': 'under_1.5',
        'under_2_5': 'under_2.5',
        'under_3_5': 'under_3.5',
        'under_4_5': 'under_4.5',
        
        # Asian Lines
        'over_2.25': 'over_2.25',
        'under_2.25': 'under_2.25',
        'over_2.75': 'over_2.75',
        'under_2.75': 'under_2.75',
        'over_1.75': 'over_1.75',
        'under_1.75': 'under_1.75',
        'over_3.25': 'over_3.25',
        'under_3.25': 'under_3.25',
        
        # BTTS
        'btts_yes': 'btts_yes',
        'btts_no': 'btts_no',
        'btts': 'btts_yes',  # Alias
        
        # Clean Sheets
        'home_clean_sheet': 'home_clean_sheet',
        'away_clean_sheet': 'away_clean_sheet',
        'home_cs': 'home_clean_sheet',
        'away_cs': 'away_clean_sheet',
        
        # Team Totals - Home
        'home_over_0.5': 'home_over_0.5',
        'home_under_0.5': 'home_under_0.5',
        'home_over_1.5': 'home_over_1.5',
        'home_under_1.5': 'home_under_1.5',
        'home_over_2.5': 'home_over_2.5',
        'home_under_2.5': 'home_under_2.5',
        
        # Team Totals - Away
        'away_over_0.5': 'away_over_0.5',
        'away_under_0.5': 'away_under_0.5',
        'away_over_1.5': 'away_over_1.5',
        'away_under_1.5': 'away_under_1.5',
        'away_over_2.5': 'away_over_2.5',
        'away_under_2.5': 'away_under_2.5',
        
        # Odd/Even Total Goals
        'odd_goals': 'odd_goals',
        'even_goals': 'even_goals',
        'odd': 'odd_goals',
        'even': 'even_goals',
        
        # Winning Margin
        'home_by_1': 'home_by_1',
        'home_by_2plus': 'home_by_2plus',
        'away_by_1': 'away_by_1',
        'away_by_2plus': 'away_by_2plus',
        'any_by_1': 'any_by_1',
        'any_by_2plus': 'any_by_2plus',
        
        # DNB
        'dnb_home': 'dnb_home',
        'dnb_away': 'dnb_away',
        
        # Half Time
        'draw_ht': 'draw_ht',
        'home_ht': 'home_ht',
        'away_ht': 'away_ht',
        
        # Half Time / Full Time
        'ht_ft_1_1': 'ht_ft_1_1',
        'ht_ft_1_X': 'ht_ft_1_X',
        'ht_ft_1_2': 'ht_ft_1_2',
        'ht_ft_X_1': 'ht_ft_X_1',
        'ht_ft_X_X': 'ht_ft_X_X',
        'ht_ft_X_2': 'ht_ft_X_2',
        'ht_ft_2_1': 'ht_ft_2_1',
        'ht_ft_2_X': 'ht_ft_2_X',
        'ht_ft_2_2': 'ht_ft_2_2'
    }
    
    # Nomes de exibição
    MARKET_DISPLAY_NAMES = {
        # 1X2
        'home_win': 'Vitória Casa',
        'draw': 'Empate',
        'away_win': 'Vitória Fora',
        
        # Double Chance
        '1X': 'Casa ou Empate',
        '12': 'Casa ou Fora',
        'X2': 'Empate ou Fora',
        
        # Over/Under
        'over_0.5': 'Over 0.5',
        'under_0.5': 'Under 0.5 (0-0)',
        'over_1.5': 'Over 1.5',
        'under_1.5': 'Under 1.5',
        'over_2.5': 'Over 2.5',
        'under_2.5': 'Under 2.5',
        'over_3.5': 'Over 3.5',
        'under_3.5': 'Under 3.5',
        'over_4.5': 'Over 4.5',
        'under_4.5': 'Under 4.5',
        
        # Asian Lines
        'over_2.25': 'Over 2.25 (Asiático)',
        'under_2.25': 'Under 2.25 (Asiático)',
        'over_2.75': 'Over 2.75 (Asiático)',
        'under_2.75': 'Under 2.75 (Asiático)',
        'over_1.75': 'Over 1.75 (Asiático)',
        'under_1.75': 'Under 1.75 (Asiático)',
        'over_3.25': 'Over 3.25 (Asiático)',
        'under_3.25': 'Under 3.25 (Asiático)',
        
        # BTTS
        'btts_yes': 'Ambas Marcam',
        'btts_no': 'BTTS Não',
        
        # Clean Sheets
        'home_clean_sheet': 'Casa Clean Sheet',
        'away_clean_sheet': 'Fora Clean Sheet',
        
        # Team Totals Home
        'home_over_0.5': 'Casa Over 0.5',
        'home_under_0.5': 'Casa Não Marca',
        'home_over_1.5': 'Casa Over 1.5',
        'home_under_1.5': 'Casa Under 1.5',
        'home_over_2.5': 'Casa Over 2.5',
        'home_under_2.5': 'Casa Under 2.5',
        
        # Team Totals Away
        'away_over_0.5': 'Fora Over 0.5',
        'away_under_0.5': 'Fora Não Marca',
        'away_over_1.5': 'Fora Over 1.5',
        'away_under_1.5': 'Fora Under 1.5',
        'away_over_2.5': 'Fora Over 2.5',
        'away_under_2.5': 'Fora Under 2.5',
        
        # Odd/Even
        'odd_goals': 'Total Ímpar',
        'even_goals': 'Total Par',
        
        # Winning Margin
        'home_by_1': 'Casa por 1 Gol',
        'home_by_2plus': 'Casa por 2+ Gols',
        'away_by_1': 'Fora por 1 Gol',
        'away_by_2plus': 'Fora por 2+ Gols',
        'any_by_1': 'Qualquer por 1',
        'any_by_2plus': 'Qualquer por 2+',
        
        # DNB
        'dnb_home': 'DNB Casa',
        'dnb_away': 'DNB Fora',
        
        # Half Time
        'home_ht': 'Casa HT',
        'draw_ht': 'Empate HT',
        'away_ht': 'Fora HT',
        
        # HT/FT
        'ht_ft_1_1': 'Casa/Casa',
        'ht_ft_1_X': 'Casa/Empate',
        'ht_ft_1_2': 'Casa/Fora',
        'ht_ft_X_1': 'Empate/Casa',
        'ht_ft_X_X': 'Empate/Empate',
        'ht_ft_X_2': 'Empate/Fora',
        'ht_ft_2_1': 'Fora/Casa',
        'ht_ft_2_X': 'Fora/Empate',
        'ht_ft_2_2': 'Fora/Fora',
        'over_3.5': 'Over 3.5',
        'under_3.5': 'Under 3.5',
        'btts_yes': 'Ambos Marcam',
        'btts_no': 'Ambos Não Marcam',
        'dnb_home': 'Empate Anula Casa',
        'dnb_away': 'Empate Anula Fora',
        'draw_ht': 'Empate HT',
        'home_ht': 'Casa HT',
        'away_ht': 'Fora HT'
    }
    
    def __init__(self):
        """Inicializa o seletor de mercados."""
        pass
    
    def select_top_markets(self, 
                          context_analysis: Dict,
                          model_predictions: Dict,
                          market_odds: Dict,
                          strategy: str = 'value') -> List[Dict]:
        """
        Seleciona top 3 mercados baseado em contexto + modelo.
        
        Args:
            context_analysis: Output do ContextAnalyzer
            model_predictions: Predições do ensemble (consensus)
            market_odds: Odds do mercado
            strategy: 'value' ou 'multiple'
            
        Returns:
            List[Dict]: [
                {
                    'rank': 1,
                    'market': 'under_2.5',
                    'market_display': 'Under 2.5',
                    'probability': 0.88,
                    'context_score': 0.95,
                    'final_score': 0.92,
                    'market_odd': 1.95,
                    'ev_pct': 8.2,
                    'reasoning': 'Ambos desmotivados + histórico defensivo'
                }
            ]
        """
        logger.info("\n" + "="*80)
        logger.info("🎯 MARKET SELECTOR - Selecionando mercados contextuais")
        logger.info(f"   Estratégia: {strategy.upper()}")
        logger.info("="*80)
        
        # Thresholds baseados em estratégia
        if strategy == 'multiple':
            min_probability = 0.40  # Bilhetes: apostas >= 40%
            min_context_score = 0.30  # Contexto flexível (aceita qualquer contexto >= 30%)
            min_final_score = 0.28  # Score final flexível
        else:
            min_probability = 0.28  # Value: aceita menor prob se EV bom
            min_context_score = 0.40  # Contexto flexível (reduzido de 45%)
            min_final_score = 0.28  # Score final baixo
        
        logger.info(f"\n📋 Thresholds:")
        logger.info(f"   Min probability: {min_probability:.0%}")
        logger.info(f"   Min context score: {min_context_score:.0%}")
        logger.info(f"   Min final score: {min_final_score:.0%}")
        
        # Pegar consensus do modelo
        consensus = model_predictions.get('consensus', {})
        poisson_probs = model_predictions.get('poisson', {}).get('probabilities', {})
        
        # Normalizar nomes do Poisson (underscore → ponto)
        normalized_poisson = {}
        for key, value in poisson_probs.items():
            normalized_key = self.MARKET_MAPPING.get(key, key)
            normalized_poisson[normalized_key] = value
        
        # Combinar consensus + poisson normalizado para ter todos os mercados
        all_probabilities = {**normalized_poisson, **consensus}
        
        # Pegar top markets do contexto
        top_context_markets = context_analysis.get('top_markets', [])
        
        logger.info(f"\n🔍 Mercados favorecidos pelo contexto: {len(top_context_markets)}")
        for market_data in top_context_markets[:5]:
            logger.info(f"   {market_data['market']}: {market_data['context_score']:.0%} (suportado por: {', '.join(market_data['supporting_patterns'])})")
        
        # Preparar candidatos
        candidates = []
        
        for market_data in top_context_markets:
            market = market_data['market']
            context_score = market_data['context_score']
            supporting_patterns = market_data['supporting_patterns']
            
            # Normalizar nome do mercado
            normalized_market = self.MARKET_MAPPING.get(market, market)
            
            # Pegar probabilidade do modelo
            probability = all_probabilities.get(normalized_market, 0)
            
            # Se probabilidade muito baixa, tentar variações
            if probability < 0.10:
                # Tentar chaves alternativas
                alt_keys = [market, market.replace('_', ''), market + '_yes']
                for alt_key in alt_keys:
                    alt_prob = all_probabilities.get(alt_key, 0)
                    if alt_prob > probability:
                        probability = alt_prob
                        break
            
            # Pegar odd do mercado
            market_odd = self._get_market_odd(normalized_market, market_odds)
            
            # Calcular EV
            if market_odd and market_odd > 0 and probability > 0:
                fair_odd = 1 / probability
                ev_pct = ((market_odd / fair_odd) - 1) * 100
            else:
                ev_pct = 0
            
            # Calcular score final - DIFERENTE POR ESTRATÉGIA
            if strategy == 'value':
                # VALUE BET: Priorizar EV% acima de tudo
                # Score = EV × contexto × sqrt(probability)
                # √probability para penalizar menos probabilidades baixas se EV alto
                if ev_pct > 0:
                    final_score = (ev_pct / 100) * context_score * (probability ** 0.5)
                else:
                    final_score = 0  # EV negativo = descartado em value bet
            else:
                # MULTIPLE: Priorizar probabilidade + contexto
                # Score = probability × context × (1 + EV_bonus)
                ev_multiplier = 1 + max(0, ev_pct / 100) * 0.5  # EV positivo dá bonus de até 50%
                final_score = probability * context_score * ev_multiplier
            
            logger.info(f"\n   Candidato: {normalized_market}")
            logger.info(f"      Contexto: {context_score:.0%}")
            logger.info(f"      Probabilidade: {probability:.0%}")
            logger.info(f"      Odd: {market_odd}")
            logger.info(f"      EV: {ev_pct:+.1f}%")
            logger.info(f"      Score Final: {final_score:.3f}")
            
            # Filtros baseados em estratégia
            if strategy == 'value':
                # VALUE BET: EV positivo preferencial, mas aceita até -2% se contexto+prob fortes
                if ev_pct < -2.0:
                    logger.info(f"      ❌ Rejeitado: EV {ev_pct:+.1f}% < -2% (value bet limite)")
                    continue
                elif ev_pct <= 0 and (context_score < 0.90 or probability < 0.45):
                    logger.info(f"      ❌ Rejeitado: EV {ev_pct:+.1f}% negativo sem contexto forte")
                    continue
                    
                # Probabilidade mínima mais flexível
                if probability < min_probability:
                    logger.info(f"      ❌ Rejeitado: probabilidade {probability:.0%} < {min_probability:.0%}")
                    continue
                    
                # Contexto deve favorecer
                if context_score < min_context_score:
                    logger.info(f"      ❌ Rejeitado: contexto {context_score:.0%} < {min_context_score:.0%}")
                    continue
            else:
                # MULTIPLE: Probabilidade alta é obrigatória
                if probability < min_probability:
                    logger.info(f"      ❌ Rejeitado: probabilidade {probability:.0%} < {min_probability:.0%} (múltiplo exige alta prob)")
                    continue
                    
                if context_score < min_context_score:
                    logger.info(f"      ❌ Rejeitado: contexto {context_score:.0%} < {min_context_score:.0%}")
                    continue
                
                # MÚLTIPLO aceita EV levemente negativo (até -5%) se prob e contexto fortes
                if ev_pct < -5.0:
                    logger.info(f"      ❌ Rejeitado: EV {ev_pct:+.1f}% muito negativo (< -5%)")
                    continue
                    
                if final_score < min_final_score:
                    logger.info(f"      ❌ Rejeitado: score final {final_score:.3f} < {min_final_score:.3f}")
                    continue
            
            # Gerar reasoning
            reasoning = self._generate_reasoning(
                normalized_market,
                context_score,
                probability,
                supporting_patterns,
                context_analysis.get('patterns', [])
            )
            
            logger.info(f"      ✅ Aprovado!")
            
            candidates.append({
                'market': normalized_market,
                'market_display': self.MARKET_DISPLAY_NAMES.get(normalized_market, normalized_market.replace('_', ' ').title()),
                'probability': probability,
                'context_score': context_score,
                'final_score': final_score,
                'market_odd': market_odd,
                'fair_odd': 1 / probability if probability > 0 else 0,
                'ev_pct': ev_pct,
                'supporting_patterns': supporting_patterns,
                'reasoning': reasoning
            })
        
        # Ordenar baseado em estratégia
        if strategy == 'value':
            # VALUE BET: Ordenar por EV% (maior value primeiro)
            candidates.sort(key=lambda x: x['ev_pct'], reverse=True)
            logger.info(f"\n📊 Ordenação: EV% descendente (value bet)")
        else:
            # MULTIPLE: Ordenar por final_score (probabilidade × contexto)
            candidates.sort(key=lambda x: x['final_score'], reverse=True)
            logger.info(f"\n📊 Ordenação: Final score descendente (múltiplo)")
        
        # Pegar top 3
        top_3 = candidates[:3]
        
        # Adicionar rank
        for i, bet in enumerate(top_3, 1):
            bet['rank'] = i
        
        logger.info("\n" + "-"*80)
        logger.info("🏆 Top 3 mercados selecionados:")
        for bet in top_3:
            logger.info(f"\n   #{bet['rank']} {bet['market_display']}")
            logger.info(f"      Prob: {bet['probability']:.0%} | Contexto: {bet['context_score']:.0%} | Score: {bet['final_score']:.3f}")
            logger.info(f"      Odd: {bet['market_odd']} | EV: {bet['ev_pct']:+.1f}%")
            logger.info(f"      Razão: {bet['reasoning']}")
        logger.info("="*80 + "\n")
        
        return top_3
    
    def _get_market_odd(self, market: str, market_odds: Dict) -> Optional[float]:
        """
        Extrai odd do mercado do dicionário de odds.
        
        Market odds pode ter estrutura variada:
        - {'home': 2.10, 'draw': 3.40, 'away': 3.20}
        - {'over_2.5': 1.95, 'under_2.5': 1.85}
        - {'btts_yes': 1.75, 'btts_no': 2.05}
        """
        if not market_odds:
            return None
        
        # Mapeamento de mercados para chaves de odds
        odd_key_mapping = {
            'home_win': 'home',
            'draw': 'draw',
            'away_win': 'away',
            'btts_yes': 'btts_yes',
            'btts_no': 'btts_no',
            'dnb_home': 'dnb_home',
            'dnb_away': 'dnb_away'
        }
        
        # Tentar chave direta primeiro
        odd = market_odds.get(market)
        if odd and odd > 0:
            return odd
        
        # Tentar chave mapeada
        odd_key = odd_key_mapping.get(market, market)
        odd = market_odds.get(odd_key)
        if odd and odd > 0:
            return odd
        
        # Para totals, tentar com underline removido
        if 'over' in market or 'under' in market:
            simplified_key = market.replace('_', '')
            odd = market_odds.get(simplified_key)
            if odd and odd > 0:
                return odd
        
        # Odd padrão se não encontrado
        return 2.00
    
    def _generate_reasoning(self,
                          market: str,
                          context_score: float,
                          probability: float,
                          supporting_patterns: List[str],
                          all_patterns: List[Dict]) -> str:
        """
        Gera raciocínio humano para a recomendação.
        
        Args:
            market: Nome do mercado
            context_score: Score contextual
            probability: Probabilidade do modelo
            supporting_patterns: Padrões que suportam este mercado
            all_patterns: Todos os padrões detectados
            
        Returns:
            str: Raciocínio humanizado
        """
        # Pegar reasoning dos padrões
        pattern_reasonings = []
        for pattern_data in all_patterns:
            if pattern_data['name'] in supporting_patterns:
                # Tentar pegar reasoning, se não existir usar nome do padrão
                reasoning_text = pattern_data.get('reasoning', pattern_data.get('name', 'padrão detectado'))
                pattern_reasonings.append(reasoning_text)
        
        # Combinar reasonings
        if pattern_reasonings:
            combined = '; '.join(pattern_reasonings[:2])  # Max 2 padrões
            
            # Adicionar contexto de força
            if context_score >= 0.90:
                strength = "contexto muito forte"
            elif context_score >= 0.80:
                strength = "contexto forte"
            elif context_score >= 0.70:
                strength = "contexto razoável"
            else:
                strength = "contexto moderado"
            
            # Adicionar probabilidade
            if probability >= 0.80:
                prob_str = "alta probabilidade"
            elif probability >= 0.65:
                prob_str = "boa probabilidade"
            else:
                prob_str = "probabilidade moderada"
            
            return f"{combined} ({strength}, {prob_str})"
        
        # Fallback genérico
        return f"Contexto favorável ({context_score:.0%}) com {probability:.0%} de probabilidade"
