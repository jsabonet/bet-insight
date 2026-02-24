"""
Market Selector - Seleciona mercados baseado em contexto + probabilidades

Combina análise contextual do ContextAnalyzer com probabilidades dos modelos
para selecionar os 3 melhores mercados para apostar.

Date: 2026-02-14
Refatorado: Usa market_standards e odds_calculator
"""

import logging
from typing import Dict, List, Optional

from apps.analysis.config.market_standards import (
    normalize_market_name,
    get_market_display_name,
    get_market_category,
    is_derived_market
)
from apps.analysis.services.odds_calculator import OddsCalculator

logger = logging.getLogger(__name__)


class MarketSelector:
    """
    Seleciona top 3 mercados combinando contexto + probabilidades do modelo.
    
    Filosofia: Priorizar mercados que o CONTEXTO favorece E o modelo confirma.
    Evitar mercados com alta probabilidade mas contexto desfavorável.
    
    CORREÇÃO 14/02/2026:
    - Usa nomenclatura canônica (market_standards.py)
    - Calcula odds derivadas corretamente (odds_calculator.py)
    - Bloqueia EV para odds simuladas
    """
    
    def __init__(self):
        self.odds_calculator = OddsCalculator()
    
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
                    'selection_score': 0.836,  # contexto × prob = 0.95 × 0.88
                    'final_score': 0.836,  # DEPRECADO: mesmo que selection_score
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
        
        # Thresholds baseados em estratégia - AJUSTADOS (14/02/2026)
        # NOVA LÓGICA: Contexto neutro (<75%) = 1.0 (passa automaticamente)
        #              Contexto forte (≥75%) = valor real (pode ser filtrado se muito fraco)
        if strategy == 'multiple':
            min_probability = 0.45  # Bilhetes: apostas SEGURAS 45%
            min_context_score = 0.65  # Só afeta contextos fortes (≥75% passa, 65-74% rejeita se não for 1.0)
            min_selection_score = 0.30  # Score seleção MIN 30% (contexto × prob)
        else:  # 'value'
            min_probability = 0.45  # Value: mínimo 45% de chance
            min_context_score = 0.60  # Contexto razoável >= 60%
            min_selection_score = 0.27  # Score seleção MIN 27%
        
        logger.info(f"\n📋 Thresholds:")
        logger.info(f"   Min probability: {min_probability:.0%}")
        logger.info(f"   Min context score: {min_context_score:.0%} (contextos <75% → 1.0 = passa)")
        logger.info(f"   Min selection score: {min_selection_score:.0%}")
        if strategy == 'multiple':
            logger.info(f"   EV filter: DESATIVADO (irrelevante para acumuladores)")
        else:
            logger.info(f"   Min EV: -2% (value bet exige retorno positivo)")
        
        # Pegar consensus do modelo
        consensus = model_predictions.get('consensus', {})
        poisson_probs = model_predictions.get('poisson', {}).get('probabilities', {})
        
        # Normalizar nomes do Poisson (underscore → ponto)
        normalized_poisson = {}
        for key, value in poisson_probs.items():
            normalized_key = normalize_market_name(key)
            normalized_poisson[normalized_key] = value
        
        # Combinar consensus + poisson normalizado para ter todos os mercados
        all_probabilities = {**normalized_poisson, **consensus}
        
        logger.info(f"\n🔍 Analisando TODOS os mercados disponíveis: {len(all_probabilities)}")
        
        # Criar lookup de context scores do ContextAnalyzer (se disponível)
        context_scores_lookup = {}
        top_context_markets = context_analysis.get('top_markets', [])
        
        # Filtrar padrões não úteis (warnings)
        EXCLUDED_PATTERNS = {'bookmaker_margin_high', 'low_liquidity', 'odds_movement'}
        
        for m in top_context_markets:
            patterns = set(m.get('supporting_patterns', []))
            # Só usar se tem padrões úteis
            if patterns and not patterns.issubset(EXCLUDED_PATTERNS):
                market_key = normalize_market_name(m.get('market', '')) or m.get('market', '')
                context_scores_lookup[market_key] = {
                    'score': m.get('context_score', 0),
                    'patterns': m.get('supporting_patterns', [])
                }
        
        logger.info(f"   📊 Contexto útil disponível para {len(context_scores_lookup)} mercados")
        
        # Padrões gerais detectados
        detected_patterns = context_analysis.get('patterns', [])
        num_patterns = len(detected_patterns)
        
        # FILOSOFIA: Contexto só deve influenciar se for REALMENTE forte (≥75%)
        # Contexto fraco/neutro (< 75%) = sem boost = 1.0 (apenas probabilidade)
        # Isso evita contextos arbitrários/fracos distorcerem a seleção
        
        # Contar mercados com contexto FORTE vs FRACO
        strong_context_count = sum(1 for v in context_scores_lookup.values() if v['score'] >= 0.75)
        weak_context_count = len(context_scores_lookup) - strong_context_count
        
        logger.info(f"   🎯 Contexto FORTE (≥75%): {strong_context_count} mercados")
        logger.info(f"   ⚪ Contexto FRACO (<75%): {weak_context_count} mercados → tratados como neutros (1.0)")
        logger.info(f"   📊 {num_patterns} padrões gerais detectados")
        
        # DEBUG: Mostrar padrões detectados e suas confianças
        if detected_patterns:
            logger.info(f"\n   🔍 DEBUG - Padrões detectados:")
            for p in detected_patterns:
                logger.info(f"      • {p.get('name', 'Unknown')}: {p.get('confidence', 0):.0%} confiança")
                fav_markets = p.get('favorable_markets', [])[:5]
                logger.info(f"        Favorece: {', '.join(fav_markets)}")
            
            # Mostrar top markets com contexto FORTE
            strong_markets = [(m, s['score']) for m, s in context_scores_lookup.items() if s['score'] >= 0.75]
            if strong_markets:
                strong_markets.sort(key=lambda x: x[1], reverse=True)
                logger.info(f"\n   💪 Top mercados com contexto FORTE (≥75%):")
                for market, score in strong_markets[:5]:
                    logger.info(f"      {market}: {score:.0%}")
        else:
            logger.info(f"\n   ⚠️ DEBUG - Nenhum padrão contextual detectado!")
        
        # Preparar candidatos de TODOS os mercados
        candidates = []
        
        for market_key, probability in all_probabilities.items():
            # Ignorar probabilidades muito baixas
            if probability < 0.10:
                continue
            
            # Normalizar nome do mercado
            normalized_market = normalize_market_name(market_key) or market_key
            
            # Determinar context_score usando lógica FORTE vs NEUTRO
            if normalized_market in context_scores_lookup:
                context_info = context_scores_lookup[normalized_market]
                raw_score = context_info['score']
                
                if raw_score >= 0.75:
                    # Contexto FORTE: usar score real do ContextAnalyzer
                    context_score = raw_score
                    supporting_patterns = context_info['patterns']
                    context_type = "FORTE"
                else:
                    # Contexto FRACO: ignorar boost, usar 1.0 (probabilidade pura)
                    context_score = 1.0
                    supporting_patterns = ['Contexto fraco - seleção por probabilidade']
                    context_type = "FRACO→1.0"
            else:
                # Sem contexto específico: usar 1.0 (probabilidade pura)
                context_score = 1.0
                supporting_patterns = ['Sem contexto específico - seleção por probabilidade']
                context_type = "NEUTRO"
            
            candidates.append({
                'market': normalized_market,
                'context_score': context_score,
                'supporting_patterns': supporting_patterns,
                'probability': probability,
                'context_type': context_type  # Para debug
            })
            
        logger.info(f"   ✅ {len(candidates)} mercados candidatos criados\n")
        
        # Processar cada candidato e aplicar filtros
        approved_candidates = []
            
        for market_data in candidates:
            normalized_market = market_data['market']
            context_score = market_data['context_score']
            supporting_patterns = market_data['supporting_patterns']
            probability = market_data['probability']
            
            # Pegar odd do mercado
            # 🆕 CORREÇÃO: Usar OddsCalculator que suporta odds enriquecidas
            market_odd = self._get_market_odd(normalized_market, market_odds)
            
            # Verificar se é odd simulada
            odd_source = OddsCalculator.get_odd_source(market_odds, normalized_market) if isinstance(market_odds.get(normalized_market), dict) else None
            
            # Calcular EV (apenas para logging e filtragem, não para score)
            if market_odd and market_odd > 0 and probability > 0:
                fair_odd = 1 / probability
                ev_pct = ((market_odd / fair_odd) - 1) * 100
                
                # 🆕 CORREÇÃO: Bloquear EV para odds simuladas (sempre ~-5%)
                if odd_source == 'simulated':
                    ev_pct = -5.0
                    logger.debug(f"   ⚠️ {normalized_market}: Odd simulada → forçando EV = -5%")
            else:
                ev_pct = 0
            
            # 🆕 CORREÇÃO: Score SIMPLES para seleção (apenas contexto × probabilidade)
            # DecisionEngine calculará score final considerando EV, confiança, risco
            # EVITA multiplicação dupla/tripla do mesmo fator
            selection_score = context_score * probability
            
            logger.info(f"\n   Candidato: {normalized_market}")
            logger.info(f"      Contexto: {context_score:.0%}")
            logger.info(f"      Probabilidade: {probability:.0%}")
            logger.info(f"      Odd: {market_odd}")
            logger.info(f"      EV: {ev_pct:+.1f}%")
            logger.info(f"      Selection Score: {selection_score:.3f} (contexto × prob)")
            
            # FILTRO CRÍTICO: Rejeitar mercados SEM odd do mercado
            # Mercados sem odd real não podem ser apostados, independente da estratégia
            if not market_odd or market_odd <= 0:
                logger.info(f"      ❌ Rejeitado: sem odd disponível no mercado")
                continue
            
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
                    # Override específico: BTTS com prob alta e EV positivo pode passar com contexto ≥ 50%
                    if normalized_market in ('btts_yes', 'btts') and probability >= 0.65 and ev_pct >= 0 and context_score >= 0.50:
                        logger.info("      ✅ Override: BTTS com prob alta (≥65%), EV ≥ 0 e contexto ≥ 50%")
                    else:
                        logger.info(f"      ❌ Rejeitado: contexto {context_score:.0%} < {min_context_score:.0%}")
                        continue
            else:
                # MULTIPLE: Foco em PROBABILIDADE ALTA (acumuladores dependem disso)
                # EV é irrelevante - importa a chance de acertar todas as apostas
                # NOTA: Com nova lógica, context_score neutro = 1.0 (passa automaticamente)
                allow_override = (context_score >= 0.80 and 0.40 <= probability < min_probability)
                if probability < min_probability and not allow_override:
                    logger.info(f"      ❌ Rejeitado: probabilidade {probability:.0%} < {min_probability:.0%} (múltiplo exige alta prob)")
                    continue
                    
                # Context score: neutros (1.0) passam; fortes (≥0.75) verificados contra 0.65
                if context_score < min_context_score:
                    logger.info(f"      ❌ Rejeitado: contexto {context_score:.0%} < {min_context_score:.0%}")
                    continue
                
                if selection_score < min_selection_score:
                    logger.info(f"      ❌ Rejeitado: selection score {selection_score:.3f} < {min_selection_score:.3f}")
                    continue
                
                # ✅ CORREÇÃO 21/02: Para múltiplas, aceitar até EV -5% (será filtrado no gerador por EV 0%)
                # Market selector é mais permissivo; filtro final é no daily_bet_generator
                if ev_pct < -15.0:
                    logger.info(f"      ❌ Rejeitado: EV {ev_pct:+.1f}% muito negativo (threshold: -15%)")
                    continue
                elif ev_pct < 0:
                    logger.info(f"      ⚠️ Aviso: EV {ev_pct:+.1f}% negativo (aprovado por probabilidade alta)")
                
                # ✅ CORREÇÃO 24/02: Filtrar odds fora da faixa 1.30-2.00 para bilhetes múltiplos
                # Alinha com gerador automático (1.30-1.50) e AI Analyzer (1.30-2.00)
                # Odds muito baixas (<1.30): retorno péssimo mesmo com prob alta
                # Odds muito altas (>2.00): risco alto para combinações
                if market_odd < 1.30:
                    logger.info(f"      ❌ Rejeitado: odd {market_odd:.2f} < 1.30 (bilhetes requerem odds ≥ 1.30)")
                    continue
                elif market_odd > 2.00:
                    logger.info(f"      ❌ Rejeitado: odd {market_odd:.2f} > 2.00 (bilhetes requerem odds ≤ 2.00)")
                    continue
            
            # Gerar reasoning contextualizado
            reasoning = self._generate_reasoning(
                normalized_market,
                context_score,
                probability,
                supporting_patterns,
                context_analysis.get('patterns', []),
                model_predictions  # 🆕 NOVO: passar model_predictions para razões contextualizadas
            )
            
            logger.info(f"      ✅ Aprovado!")
            
            # Determinar tipo de contexto para display no frontend
            if context_score >= 0.99:
                context_type = "NEUTRO"  # Contexto <75% convertido para 1.0
            elif context_score >= 0.90:
                context_type = "MUITO_FORTE"
            elif context_score >= 0.80:
                context_type = "FORTE"
            elif context_score >= 0.75:
                context_type = "FAVORAVEL"
            else:
                context_type = "NEUTRO"  # Não deveria chegar aqui (contextos <0.75 viram 1.0)
            
            approved_candidates.append({
                'market': normalized_market,
                'market_display': get_market_display_name(normalized_market),
                'probability': probability,
                'context_score': context_score,
                'context_type': context_type,  # Para frontend exibir corretamente
                'selection_score': selection_score,  # Score simples (contexto × prob)
                'final_score': selection_score,  # DEPRECADO: manter compatibilidade com DecisionEngine
                'market_odd': market_odd,
                'fair_odd': 1 / probability if probability > 0 else 0,
                'ev_pct': ev_pct,
                'supporting_patterns': supporting_patterns,
                'reasoning': reasoning
            })
        
        logger.info(f"\n📊 Total de mercados aprovados após filtros: {len(approved_candidates)}")
        
        # Ordenar baseado em estratégia
        if strategy == 'value':
            # VALUE BET: Ordenar por EV% (maior value primeiro)
            approved_candidates.sort(key=lambda x: x['ev_pct'], reverse=True)
            logger.info(f"   Ordenação: EV% descendente (value bet)")
        else:
            # MULTIPLE: Ordenar por selection_score (probabilidade × contexto)
            # Se visitante for favorecido pelas odds, dar leve prioridade ao x2 sobre 12
            away_favored = False
            try:
                away_odd = market_odds.get('away_win') or market_odds.get('away')
                home_odd = market_odds.get('home_win') or market_odds.get('home')
                if away_odd and home_odd and away_odd < home_odd:
                    away_favored = True
            except Exception:
                away_favored = False

            if away_favored:
                for c in approved_candidates:
                    if c.get('market') == 'x2':
                        c['selection_score'] *= 1.05  # leve boost
            approved_candidates.sort(key=lambda x: x['selection_score'], reverse=True)
            logger.info(f"   Ordenação: Selection score descendente (múltiplo)")
        
        # Aplicar validação de qualidade EXTRA antes de selecionar top 3
        # ADICIONADO: 10/02/2026 - Proteção adicional contra apostas fracas
        validated_candidates = []
        rejected_count = 0
        
        logger.info(f"\n🔍 Validação de qualidade adicional ({strategy}):")
        for candidate in approved_candidates:
            is_valid, reason = self._validate_bet_quality(candidate, strategy)
            if is_valid:
                validated_candidates.append(candidate)
                logger.info(f"   ✅ {candidate['market_display']}: {reason}")
            else:
                rejected_count += 1
                logger.info(f"   ❌ {candidate['market_display']}: {reason}")
        
        if rejected_count > 0:
            logger.info(f"   📉 Rejeitados por validação extra: {rejected_count}/{len(approved_candidates)}")
        
        # NOVO: Remover apostas contraditórias antes de selecionar Top 3
        # (Ex: Under + Over, Casa + Fora no mesmo bilhete é impossível)
        conflict_free_candidates = self._remove_conflicting_markets(validated_candidates)
        
        # Pegar top 3 dos candidatos SEM CONFLITOS
        top_3 = conflict_free_candidates[:3]
        
        # Adicionar rank
        for i, bet in enumerate(top_3, 1):
            bet['rank'] = i
        
        logger.info("\n" + "-"*80)
        logger.info("🏆 Top 3 mercados selecionados:")
        for bet in top_3:
            logger.info(f"\n   #{bet['rank']} {bet['market_display']}")
            logger.info(f"      Prob: {bet['probability']:.0%} | Contexto: {bet['context_score']:.0%} | Score: {bet['selection_score']:.3f}")
            logger.info(f"      Odd: {bet['market_odd']} | EV: {bet['ev_pct']:+.1f}%")
            logger.info(f"      Razão: {bet['reasoning']}")
        logger.info("="*80 + "\n")
        
        return top_3
    
    def _markets_conflict(self, market1: str, market2: str) -> bool:
        """
        Detecta se dois mercados são contraditórios (mutuamente exclusivos).
        
        Args:
            market1: Nome do primeiro mercado (canônico)
            market2: Nome do segundo mercado (canônico)
            
        Returns:
            bool: True se os mercados conflitam, False caso contrário
        """
        # Normalizar para comparação
        m1 = market1.lower()
        m2 = market2.lower()
        
        # 1. Over vs Under (mesmo threshold)
        if 'over' in m1 and 'under' in m2:
            # Extrair threshold (ex: over_2.5 vs under_2.5)
            threshold1 = m1.replace('over_', '').replace('home_', '').replace('away_', '')
            threshold2 = m2.replace('under_', '').replace('home_', '').replace('away_', '')
            if threshold1 == threshold2:
                return True
        
        if 'under' in m1 and 'over' in m2:
            threshold1 = m1.replace('under_', '').replace('home_', '').replace('away_', '')
            threshold2 = m2.replace('over_', '').replace('home_', '').replace('away_', '')
            if threshold1 == threshold2:
                return True
        
        # 2. Casa vs Fora (mutuamente exclusivos)
        if (m1 == 'home_win' and m2 == 'away_win') or (m1 == 'away_win' and m2 == 'home_win'):
            return True
        
        # 3. BTTS Yes vs BTTS No
        if (m1 == 'btts_yes' and m2 == 'btts_no') or (m1 == 'btts_no' and m2 == 'btts_yes'):
            return True
        if (m1 == 'btts' and m2 == 'btts_no') or (m1 == 'btts_no' and m2 == 'btts'):
            return True
        
        # 4. 12 (Casa ou Fora) vs Empate - parcialmente conflitantes
        if (m1 == '12' and m2 == 'draw') or (m1 == 'draw' and m2 == '12'):
            return True
        
        # 5. Clean Sheet vs Gols sofridos
        if 'clean_sheet' in m1 and ('over_0.5' in m2 or 'over_1' in m2):
            # Ex: home_clean_sheet vs away_over_0.5
            if 'home_clean_sheet' in m1 and 'away_over' in m2:
                return True
            if 'away_clean_sheet' in m1 and 'home_over' in m2:
                return True
        
        if 'clean_sheet' in m2 and ('over_0.5' in m1 or 'over_1' in m1):
            if 'home_clean_sheet' in m2 and 'away_over' in m1:
                return True
            if 'away_clean_sheet' in m2 and 'home_over' in m1:
                return True
        
        return False
    
    def _remove_conflicting_markets(self, candidates: List[Dict]) -> List[Dict]:
        """
        Remove apostas contraditórias da lista de candidatos.
        Quando detecta conflito, mantém a aposta com MAIOR PROBABILIDADE.
        
        Args:
            candidates: Lista de candidatos ordenados por selection_score
            
        Returns:
            List[Dict]: Lista sem conflitos
        """
        if len(candidates) <= 1:
            return candidates
        
        logger.info(f"\n🔍 Verificando conflitos entre {len(candidates)} candidatos...")
        
        conflict_free = []
        removed_markets = []
        
        for candidate in candidates:
            has_conflict = False
            
            # Verificar se conflita com algum já selecionado
            for selected in conflict_free:
                if self._markets_conflict(candidate['market'], selected['market']):
                    has_conflict = True
                    removed_markets.append({
                        'market': candidate['market_display'],
                        'prob': candidate['probability'],
                        'conflicts_with': selected['market_display']
                    })
                    logger.info(f"   ⚠️ CONFLITO: {candidate['market_display']} ({candidate['probability']:.0%}) "
                              f"vs {selected['market_display']} ({selected['probability']:.0%})")
                    logger.info(f"      → Mantendo {selected['market_display']} (maior probabilidade)")
                    break
            
            if not has_conflict:
                conflict_free.append(candidate)
        
        if removed_markets:
            logger.info(f"\n📉 {len(removed_markets)} apostas removidas por conflito:")
            for rm in removed_markets:
                logger.info(f"   - {rm['market']} ({rm['prob']:.0%}) conflita com {rm['conflicts_with']}")
        else:
            logger.info(f"   ✅ Nenhum conflito detectado")
        
        return conflict_free
    
    def _get_market_odd(self, market: str, market_odds: Dict) -> Optional[float]:
        """
        Extrai odd do mercado do dicionário de odds.
        
        Suporta:
        - Dict enriquecido: {'home_win': {'value': 2.10, 'source': 'api'}}
        - Dict simples: {'home_win': 2.10}
        - Dict legado: {'home': 2.10, 'draw': 3.40} (converte para canônico)
        
        🆕 CORREÇÃO: Usa OddsCalculator para extrair valores
        """
        if not market_odds:
            return None
        
        # Tentar usar OddsCalculator primeiro (suporta dict enriquecido)
        odd = OddsCalculator.get_odd_value(market_odds, market)
        if odd and odd > 0:
            return odd
        
        # Fallback para dict legado (chaves antigas: 'home', 'draw', 'away')
        odd_key_mapping = {
            'home_win': ['home', 'odds_home', 'home_win'],
            'draw': ['draw', 'odds_draw'],
            'away_win': ['away', 'odds_away', 'away_win'],
            'btts_yes': ['btts_yes', 'odds_btts', 'btts'],
            'btts_no': ['btts_no'],
            'dnb_home': ['dnb_home'],
            'dnb_away': ['dnb_away'],
        }
        
        # Tentar chaves alternativas
        possible_keys = odd_key_mapping.get(market, [market])
        for key in possible_keys:
            odd = market_odds.get(key)
            if odd:
                if isinstance(odd, dict):
                    odd = odd.get('value')
                if odd and odd > 0:
                    return float(odd)
        
        # Para totals, tentar variações de formato
        if 'over' in market or 'under' in market:
            # over_2.5 → odds_over25, over25, over_2_5
            variants = [
                market,
                f"odds_{market.replace('.', '')}",
                market.replace('.', ''),
                market.replace('.', '_'),
            ]
            for variant in variants:
                odd = market_odds.get(variant)
                if odd:
                    if isinstance(odd, dict):
                        odd = odd.get('value')
                    if odd and odd > 0:
                        return float(odd)
        
        # Não encontrado - retornar None (evita odd genérica 2.00!)
        return None
    
    def _validate_bet_quality(self, bet: Dict, strategy: str) -> tuple[bool, str]:
        """
        Valida qualidade EXTRA de aposta antes de incluir no top 3.
        
        ADICIONADO: 10/02/2026 - Proteção adicional contra apostas de baixa qualidade
        PROBLEMA: Thresholds isolados não são suficientes - precisamos validação cruzada
        
        Validações por estratégia:
        - VALUE: Exige EV >= +5% E probabilidade >= 40% E contexto >= 50%
        - MULTIPLE: Exige probabilidade >= 45% E contexto >= 60% E selection_score >= 0.30
        
        Returns:
            tuple: (is_valid: bool, reason: str)
        """
        prob = bet.get('probability', 0)
        context = bet.get('context_score', 0)
        ev = bet.get('ev_pct', 0)
        selection_score = bet.get('selection_score', 0)
        
        if strategy == 'value':
            # VALUE BET: Exige EV real + probabilidade mínima
            # Override: permitir EV neutro quando contexto é muito forte e probabilidade alta
            if ev < 5.0:
                if ev >= 0 and context >= 0.85 and prob >= 0.60:
                    return True, "Override: contexto muito forte (≥85%) e prob alta (≥60%) com EV neutro"
                return False, f"EV muito baixo: {ev:.1f}% < 5.0%"
            if prob < 0.40:
                return False, f"Probabilidade insuficiente: {prob:.1%} < 40%"
            if context < 0.50:
                return False, f"Contexto fraco: {context:.1%} < 50%"
            
        else:  # 'multiple'
            # BILHETE MÚLTIPLO: Exige segurança, mas aceita override com contexto muito forte
            if not (context >= 0.80 and 0.40 <= prob < 0.45):
                if prob < 0.45:
                    return False, f"Probabilidade insuficiente: {prob:.1%} < 45%"
            if context < 0.60:
                return False, f"Contexto insuficiente: {context:.1%} < 60%"
            if selection_score < 0.30:
                return False, f"Selection score baixo: {selection_score:.3f} < 0.30"
        
        # Todas as validações passaram
        return True, "✅ Aposta aprovada"
    
    def _generate_reasoning(self,
                          market: str,
                          context_score: float,
                          probability: float,
                          supporting_patterns: List[str],
                          all_patterns: List[Dict],
                          model_predictions: Dict = None) -> str:
        """
        Gera raciocínio humano CONTEXTUALIZADO para a recomendação.
        
        Usa dados reais do modelo (xG, consenso, poisson) para explicações específicas.
        
        Args:
            market: Nome do mercado
            context_score: Score contextual
            probability: Probabilidade do modelo
            supporting_patterns: Padrões que suportam este mercado
            all_patterns: Todos os padrões detectados
            model_predictions: Predições dos modelos (consenso, xG, etc.)
            
        Returns:
            str: Raciocínio humanizado e contextualizado
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
            
            # Adicionar contexto de força (apenas se relevante)
            if context_score >= 0.90:
                strength = "contexto muito forte"
            elif context_score >= 0.80:
                strength = "contexto forte"
            elif context_score >= 0.75:
                strength = "contexto favorável"
            else:
                strength = None  # Contexto irrelevante (neutralizado para 1.0)
            
            # Adicionar probabilidade
            if probability >= 0.80:
                prob_str = "alta probabilidade"
            elif probability >= 0.65:
                prob_str = "boa probabilidade"
            else:
                prob_str = "probabilidade moderada"
            
            if strength:
                return f"{combined} ({strength}, {prob_str})"
            else:
                return f"{combined} ({prob_str})"
        
        # Fallback contextualizado usando dados do modelo
        if model_predictions:
            consensus = model_predictions.get('consensus', {})
            poisson = model_predictions.get('poisson', {})
            xg_data = poisson.get('expected_goals', {})
            xg_home = xg_data.get('home', 0)
            xg_away = xg_data.get('away', 0)
            xg_total = xg_home + xg_away
            
            # Gerar razão contextualizada baseada no mercado E nos dados reais
            if 'over' in market or 'under' in market:
                if xg_total > 2.8:
                    game_type = "ofensivo"
                elif xg_total < 2.0:
                    game_type = "defensivo"
                else:
                    game_type = "equilibrado"
                return f"Jogo {game_type} (xG: {xg_total:.1f}) com {probability*100:.0f}% de probabilidade"
            
            elif any(x in market for x in ['home_win', 'away_win', 'draw']):
                prob_home = consensus.get('home_win', 0)
                prob_away = consensus.get('away_win', 0)
                prob_draw = consensus.get('draw', 0)
                
                if max(prob_home, prob_away, prob_draw) > 0.45:
                    if 'home' in market:
                        return f"Casa favorita ({prob_home*100:.0f}%) com xG {xg_home:.1f} vs {xg_away:.1f}"
                    elif 'away' in market:
                        return f"Visitante favorito ({prob_away*100:.0f}%) com xG {xg_away:.1f} vs {xg_home:.1f}"
                    else:
                        return f"Jogo equilibrado ({prob_draw*100:.0f}%) favorece empate"
                else:
                    return f"Jogo equilibrado - nenhum favorito claro (xG: {xg_home:.1f} vs {xg_away:.1f})"
            
            elif 'btts' in market:
                if 'yes' in market or market == 'btts':
                    if xg_home >= 1.0 and xg_away >= 1.0:
                        return f"Ambos times ofensivos (xG: {xg_home:.1f} e {xg_away:.1f}) com {probability*100:.0f}% de ambos marcarem"
                    else:
                        return f"{probability*100:.0f}% de ambos marcarem baseado em padrões estatísticos"
                else:
                    return f"Jogo defensivo (xG total: {xg_total:.1f}) com {probability*100:.0f}% de um não marcar"
            
            elif 'double_chance' in market:
                return f"Cobertura para jogo equilibrado (xG: {xg_home:.1f} vs {xg_away:.1f}) com {probability*100:.0f}% de probabilidade"
            
            # Fallback genérico mas com xG
            return f"Probabilidade {probability*100:.0f}% baseada em xG {xg_home:.1f} vs {xg_away:.1f} e análise estatística"
        
        # Fallback sem model_predictions (muito raro)
        # IMPORTANTE: context_score = 1.0 pode ser contexto <75% convertido para neutral
        if 0.75 <= context_score < 0.99:
            # Contexto FORTE: mencionar no reasoning
            if context_score >= 0.90:
                strength = "contexto muito forte"
            elif context_score >= 0.80:
                strength = "contexto forte"
            else:
                strength = "contexto favorável"
            
            if probability >= 0.75:
                return f"{strength} ({context_score:.0%}) com alta probabilidade ({probability:.0%})"
            else:
                return f"{strength} ({context_score:.0%}) com {probability:.0%} de probabilidade"
        else:
            # Último fallback
            if probability >= 0.75:
                return f"Alta probabilidade ({probability:.0%}) baseada em análise estatística"
            elif probability >= 0.60:
                return f"Boa probabilidade ({probability:.0%}) com suporte dos modelos"
            else:
                return f"Probabilidade moderada ({probability:.0%}) baseada em modelos preditivos"
