"""
Decision Engine - Motor de Decisão
Combina modelos estatísticos e identifica value bets
"""
import logging
import numpy as np
from typing import Dict
from .market_selector import MarketSelector  # NOVO
from apps.analysis.config import DecisionThresholds, ContextPolicy

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Motor de decisão que:
    1. Combina previsões de múltiplos modelos
    2. Detecta value bets (odds do mercado > odds justas)
    3. Calcula confiança da previsão
    4. Avalia risco
    5. Gera recomendação final
    6. NOVO: Usa análise contextual para selecionar mercados apropriados
    """
    
    def __init__(self):
        """Inicializa o Decision Engine com MarketSelector."""
        self.market_selector = MarketSelector()
    
    def should_publish_prediction(self, consensus, confidence, threshold_prob=None, threshold_conf=None, context_analysis=None):
        """
        Decide se a predição deve ser publicada baseado em filtros de qualidade.
        
        Estratégia RECALIBRADA: Trade volume por acurácia (ajustado após validação)
        - Publicar apenas quando há SINAL FORTE
        - Evitar jogos equilibrados (alta incerteza)
        
        Critérios RECALIBRADOS (OU lógico):
        1. Máxima probabilidade ≥ 52% (reduzido de 55% para mais cobertura)
        2. Confidence score ≥ 0.75 (aumentado de 0.70 = apenas very_high)
        
        Args:
            consensus (dict): Probabilidades 1X2
            confidence (dict): Objeto de confiança com 'score' e 'stars'
            threshold_prob (float): Limite mínimo de probabilidade (default: DecisionThresholds.MIN_PROBABILITY)
            threshold_conf (float): Limite mínimo de confidence score (default: DecisionThresholds.MIN_CONFIDENCE)
        
        Returns:
            dict: {
                'should_publish': bool,
                'reason': str,
                'max_probability': float,
                'confidence_score': float,
                'filter_passed': str  # 'probability', 'confidence', 'both', 'none'
            }
        """
        # Usar valores da configuração centralizada se não especificados
        if threshold_prob is None:
            threshold_prob = DecisionThresholds.MIN_PROBABILITY
        if threshold_conf is None:
            threshold_conf = DecisionThresholds.MIN_CONFIDENCE
        
        max_prob = max(consensus.values()) if consensus else 0.33
        conf_score = confidence.get('score', 0.5)
        
        # Verificar critérios
        prob_passed = max_prob >= threshold_prob
        conf_passed = conf_score >= threshold_conf
        
        # Decisão (OU lógico)
        should_publish = prob_passed or conf_passed
        
        # Determinar razão
        if prob_passed and conf_passed:
            filter_status = 'both'
            reason = f"Alta probabilidade ({max_prob*100:.1f}%) E alta confiança ({conf_score:.2f})"
        elif prob_passed:
            filter_status = 'probability'
            reason = f"Alta probabilidade ({max_prob*100:.1f}%)"
        elif conf_passed:
            filter_status = 'confidence'
            reason = f"Alta confiança ({conf_score:.2f})"
        else:
            filter_status = 'none'
            reason = f"Jogo equilibrado (prob={max_prob*100:.1f}%, conf={conf_score:.2f})"
        
        logger.info(f"\n📢 FILTRO DE PUBLICAÇÃO:")
        check_prob = '✅' if prob_passed else '❌'
        check_conf = '✅' if conf_passed else '❌'
        logger.info(f"   Max Probabilidade: {max_prob*100:.1f}% (limite: {threshold_prob*100:.0f}%) {check_prob}")
        logger.info(f"   Confidence Score: {conf_score:.2f} (limite: {threshold_conf:.2f}) {check_conf}")
        publish_status = '✅ PUBLICAR' if should_publish else '❌ PULAR'
        # Context override: permitir publicação se contexto for muito forte
        if ContextPolicy.CONTEXT_PRIORITY_ENABLED and context_analysis:
            patterns = context_analysis.get('patterns', [])
            # média simples dos 'confidence' dos padrões
            if patterns:
                avg_ctx = sum(p.get('confidence', 0.0) for p in patterns) / max(len(patterns), 1)
            else:
                avg_ctx = 0.0
            if not should_publish and avg_ctx >= ContextPolicy.CONTEXT_PUBLISH_OVERRIDE_MIN_CONTEXT:
                should_publish = True
                reason += f"; override por contexto forte ({avg_ctx:.2f})"
                filter_status = 'context_override'
        logger.info(f"   Decisão: {publish_status} ({reason})")
        
        return {
            'should_publish': should_publish,
            'reason': reason,
            'max_probability': max_prob,
            'confidence_score': conf_score,
            'filter_passed': filter_status
        }
    
    def make_decision(self, model_predictions, features, market_odds, strategy='value', context_analysis=None):
        """
        Decisão final baseada em modelos + mercado + contexto
        
        Args:
            model_predictions (dict): Previsões dos modelos (Poisson + Logística)
            features (dict): Features engineered
            market_odds (dict): Odds do mercado
            strategy (str): 'value' (EV máximo) ou 'multiple' (prob alta + EV positivo)
            context_analysis (dict): Análise contextual do ContextAnalyzer (NOVO)
        
        Returns:
            dict: {
                'recommendation': {...},
                'confidence': {...},
                'risk': str,
                'value_bets': [...],
                'fair_odds': {...},
                'strategy': str,
                'top_bets': [...]  # Selecionados por contexto se disponível
            }
        """
        logger.info(f"\n{'='*80}")
        
        # Garantir que strategy é string
        if not isinstance(strategy, str):
            logger.warning(f"⚠️ Strategy não é string: {type(strategy)} - usando 'value'")
            strategy = 'value'
        
        logger.info(f"🎯 DECISION ENGINE - Gerando recomendação (Estratégia: {strategy.upper()})")
        logger.info(f"{'='*80}\n")
        
        logger.info("📊 Model Predictions recebidos:")
        logger.info(f"   Consensus: {model_predictions.get('consensus', {})}")
        logger.info(f"   Poisson xG: Home={model_predictions.get('poisson', {}).get('expected_goals', {}).get('home')}, Away={model_predictions.get('poisson', {}).get('expected_goals', {}).get('away')}")
        logger.info(f"   Weather Adjusted: {model_predictions.get('poisson', {}).get('weather_adjusted', False)}")
        
        # ✅ Garantir que market_odds seja um dict
        if market_odds is None:
            market_odds = {}
        
        logger.info("\n💰 Market Odds:")
        def _odds_fallback(odds: Dict, keys: list):
            for k in keys:
                v = odds.get(k)
                if v:
                    return v
            return None
        home_o = _odds_fallback(market_odds, ['home', 'home_win'])
        draw_o = _odds_fallback(market_odds, ['draw'])
        away_o = _odds_fallback(market_odds, ['away', 'away_win'])
        over25_o = _odds_fallback(market_odds, ['over_2_5','over_25'])
        under25_o = _odds_fallback(market_odds, ['under_2_5','under_25'])
        logger.info(f"   Home: {home_o}, Draw: {draw_o}, Away: {away_o}")
        logger.info(f"   Over 2.5: {over25_o}, Under 2.5: {under25_o}")
        
        # 1. Calcular odds justas dos modelos
        logger.info("\n1️⃣ Calculando odds justas...")
        fair_odds = self._calculate_fair_odds(model_predictions)
        logger.info(f"   ✅ Fair odds: {fair_odds}")
        
        # 2. Identificar value bets
        logger.info("\n2️⃣ Identificando value bets...")
        value_bets = self._find_value_bets(model_predictions, market_odds)
        logger.info(f"   ✅ {len(value_bets)} value bets encontrados")
        for vb in value_bets:
            logger.info(f"      - {vb['market']}: Fair {vb['fair_odd']} vs Market {vb['market_odd']} = {vb['edge']*100:.1f}% edge")
        
        # 3. Calcular confiança
        logger.info("\n3️⃣ Calculando confiança...")
        confidence = self._calculate_confidence(model_predictions, features)
        logger.info(f"   ✅ Confiança: {confidence['stars']}/5 ({confidence['level']}, score={confidence['score']:.2f})")
        
        # 4. Avaliar risco
        logger.info("\n4️⃣ Avaliando risco...")
        risk = self._assess_risk(model_predictions, features, market_odds)
        logger.info(f"   ✅ Risco: {risk}")
        
        # 5. Gerar recomendação principal
        logger.info("\n5️⃣ Gerando recomendação final...")
        recommendation = self._generate_recommendation(
            value_bets, 
            confidence, 
            risk, 
            model_predictions,
            market_odds
        )
        
        logger.info(f"   ✅ Recomendação: {recommendation['pick']} ({recommendation['market']})")
        logger.info(f"      Probabilidade: {recommendation['probability']*100:.1f}%")
        logger.info(f"      Odd: {recommendation['odd']}")
        
        # 6. SELEÇÃO OBJETIVA das top 3 apostas
        logger.info(f"\n6️⃣ Selecionando top 3 apostas...")
        logger.info(f"   Estratégia: {strategy.upper()}")
        logger.info(f"   Contexto disponível: {'SIM' if context_analysis else 'NÃO'}")
        
        # ✅ SEMPRE usar seleção contextual via MarketSelector (mesmo sem padrões detectados)
        # O MarketSelector agora lida com contexto vazio e faz seleção ampla de mercados
        logger.info(f"   🎯 Usando seleção CONTEXTUAL via MarketSelector (SEMPRE)")
        top_bets = self._select_contextual_bets(
            context_analysis or {'patterns': [], 'favorable_markets': []},  # Passar contexto vazio se None
            model_predictions,
            market_odds,
            confidence,
            risk,
            strategy
        )
        
        for bet in top_bets:
            logger.info(f"   #{bet['rank']}: {bet['pick']} ({bet['market_display']})")
            logger.info(f"      Prob: {bet['probability']*100:.1f}% | Odd: {bet['market_odd']} | EV: {bet['ev_pct']:.1f}% | Stake: {bet['stake_units']}u")
            logger.info(f"      Score: {bet['score']:.3f} | Razão: {bet['reason']}")
        
        logger.info(f"\n{'='*80}\n")
        
        # 7. Filtro de publicação (confiança)
        consensus = model_predictions.get('consensus', {})
        publish_filter = self.should_publish_prediction(consensus, confidence, context_analysis=context_analysis)
        
        result = {
            'recommendation': recommendation,
            'confidence': confidence,
            'risk': risk,
            'value_bets': value_bets,
            'fair_odds': fair_odds,
            'model_probabilities': model_predictions,
            'publish_filter': publish_filter,  # Dados do filtro de confiança
            'top_bets': top_bets,  # Top 3 apostas decididas objetivamente
            'strategy': strategy  # ✅ NOVO: Retornar estratégia usada
        }

        # Context-priority optional override of main recommendation
        if ContextPolicy.CONTEXT_PRIORITY_ENABLED and top_bets:
            best_ctx = top_bets[0]
            score = best_ctx.get('score', 0)
            final_score = best_ctx.get('final_score', 0)
            ev_pct = best_ctx.get('ev_pct', 0)
            
            logger.info(f"\n🔍 CONTEXT OVERRIDE CHECK:")
            logger.info(f"   Best context bet: {best_ctx.get('market_display')}")
            logger.info(f"   score: {score:.3f} (threshold: {ContextPolicy.CONTEXT_RECOMMENDATION_MIN_SCORE})")
            logger.info(f"   final_score: {final_score:.3f} (threshold: {ContextPolicy.CONTEXT_RECOMMENDATION_MIN_SCORE})")
            logger.info(f"   ev_pct: {ev_pct:+.1f}% (threshold: {ContextPolicy.CONTEXT_RECOMMENDATION_MIN_EV_VALUE}%)")
            logger.info(f"   strategy: {strategy}")
            
            meets_score = score >= ContextPolicy.CONTEXT_RECOMMENDATION_MIN_SCORE or final_score >= ContextPolicy.CONTEXT_RECOMMENDATION_MIN_SCORE
            meets_ev = (strategy == 'multiple') or (ev_pct >= ContextPolicy.CONTEXT_RECOMMENDATION_MIN_EV_VALUE)
            
            logger.info(f"   meets_score: {meets_score}, meets_ev: {meets_ev}")
            
            if meets_score and meets_ev:
                logger.info(f"   ✅ OVERRIDE ATIVADO - Contexto sobrepõe recomendação principal!")
                result['recommendation'] = {
                    'market': best_ctx['market'],
                    'market_display': best_ctx['market_display'],
                    'pick': best_ctx['pick'],
                    'probability': best_ctx['probability'],
                    'odd': best_ctx['market_odd'],
                    'fair_odd': best_ctx.get('fair_odd'),
                    'value_pct': best_ctx.get('ev_pct'),
                    'reason': 'context_priority',
                    'reason_pt': 'Override por contexto forte'
                }
                if ContextPolicy.INCLUDE_RECOMMENDATION_SOURCE:
                    result['recommendation_source'] = 'context'
            else:
                logger.info(f"   ❌ Override NÃO ativado - mantendo recomendação do modelo")

        return result
    
    def _calculate_fair_odds(self, model_predictions):
        """
        Calcula odds justas (sem margem da casa)
        
        Odd justa = 1 / probabilidade
        Com validação para evitar odds absurdas
        """
        consensus = model_predictions.get('consensus', {})
        poisson_probs = model_predictions.get('poisson', {}).get('probabilities', {})
        
        fair_odds = {}
        
        # 1X2
        for market, prob in consensus.items():
            if prob > DecisionThresholds.MIN_PROB_FOR_ODDS:
                odd = 1 / prob
                # Limitar odds a valores realistas
                fair_odds[market] = round(max(1.01, min(DecisionThresholds.MAX_FAIR_ODD, odd)), 2)
            else:
                fair_odds[market] = DecisionThresholds.MAX_FAIR_ODD  # Limite máximo
        
        # Over/Under (múltiplas linhas) e BTTS (do Poisson)
        poisson_markets = [
            'over_1.5', 'under_1.5', 
            'over_2.5', 'under_2.5', 
            'over_3.5', 'under_3.5', 
            'btts',
            # Team Total Goals
            'home_over_0.5', 'home_over_1.5', 'home_over_2.5',
            'away_over_0.5', 'away_over_1.5', 'away_over_2.5',
            # Winning Margins
            'home_win_by_1', 'home_win_by_2plus',
            'away_win_by_1', 'away_win_by_2plus',
            # Odd/Even
            'odd_goals', 'even_goals'
        ]
        
        for market in poisson_markets:
            prob = poisson_probs.get(market, 0)
            if prob > DecisionThresholds.MIN_PROB_FOR_ODDS:
                odd = 1 / prob
                fair_odds[market] = round(max(1.01, min(DecisionThresholds.MAX_FAIR_ODD, odd)), 2)
            else:
                fair_odds[market] = DecisionThresholds.MAX_FAIR_ODD
        
        return fair_odds
    
    def _find_value_bets(self, model_predictions, market_odds):
        """
        Identifica value bets onde: odd_mercado > odd_justa * 1.05
        
        Value bet = quando mercado oferece odd melhor que a "justa"
        Margem de segurança: 5%
        """
        fair_odds = self._calculate_fair_odds(model_predictions)
        value_bets = []
        
        # Normaliza entrada de odds do mercado (suporta dict enriquecido)
        def _extract_odd(odd):
            """Retorna valor numérico da odd; suporta dict {'value': x} e números."""
            if odd is None:
                return 0.0
            if isinstance(odd, dict):
                v = odd.get('value')
                try:
                    return float(v) if v is not None else 0.0
                except (TypeError, ValueError):
                    return 0.0
            try:
                return float(odd)
            except (TypeError, ValueError):
                return 0.0
        
        # Verifica se a odd é simulada
        def _is_simulated(odd):
            return isinstance(odd, dict) and bool(odd.get('is_simulated'))
        
        # Mapear nomes de mercados
        market_mapping = {
            'home_win': 'home',
            'draw': 'draw',
            'away_win': 'away',
            'over_2_5': 'over_2_5',
            'under_2_5': 'under_2_5',
            'btts': 'btts_yes'
        }
        
        for model_market, fair_odd in fair_odds.items():
            market_key = market_mapping.get(model_market)
            if not market_key:
                continue
            
            raw_odd = market_odds.get(market_key)
            # Ignorar odds simuladas em value bets
            if _is_simulated(raw_odd):
                continue
            market_odd = _extract_odd(raw_odd)
            
            if market_odd == 0 or fair_odd == 0:
                continue
            
            # Margem de segurança: 5%
            if market_odd >= fair_odd * 1.05:
                value_pct = ((market_odd / fair_odd) - 1) * 100
                edge = value_pct / 100
                
                # Probabilidade implícita
                model_prob = 1 / fair_odd if fair_odd > 0 else 0
                
                value_bets.append({
                    'market': model_market,
                    'market_display': self._format_market_name(model_market),
                    'model_probability': round(model_prob, 3),
                    'fair_odd': fair_odd,
                    'market_odd': market_odd,
                    'value_pct': round(value_pct, 1),
                    'edge': round(edge, 3),
                    'stake_suggestion': self._suggest_stake(value_pct, model_prob)
                })
        
        # Ordenar por value
        value_bets.sort(key=lambda x: x['value_pct'], reverse=True)
        
        if value_bets:
            logger.info(f"  💰 {len(value_bets)} value bets encontrados")
            for vb in value_bets[:3]:  # Top 3
                logger.info(f"    • {vb['market_display']}: {vb['value_pct']:.1f}% value")
        
        return value_bets
    
    def _calculate_confidence(self, model_predictions, features):
        """
        Calcula confiança da previsão baseado em:
        1. Consenso entre modelos (Poisson vs Logística)
        2. Qualidade dos dados
        3. Força das features
        """
        poisson_probs = model_predictions.get('poisson', {}).get('probabilities', {})
        logistic_probs = model_predictions.get('logistic', {})
        consensus = model_predictions.get('consensus', {})
        
        confidence_factors = []
        
        # 1. CONSENSO entre modelos
        # Se Poisson e Logística concordam = maior confiança
        if poisson_probs and logistic_probs:
            poisson_home = poisson_probs.get('home_win', 0.33)
            logistic_home = logistic_probs.get('home_win', 0.33)
            
            consensus_score = 1 - abs(poisson_home - logistic_home)
            confidence_factors.append(('consensus', consensus_score))
        else:
            confidence_factors.append(('consensus', 0.6))
        
        # 2. FORÇA DO DIFERENCIAL
        strength = features.get('strength', {})
        form = features.get('form', {})
        
        strength_diff = abs(strength.get('strength_differential', 0))
        form_diff = abs(form.get('form_differential', 0))
        
        # Quanto maior o diferencial, maior a confiança
        if strength_diff > DecisionThresholds.SIGNIFICANT_STRENGTH_DIFF or form_diff > DecisionThresholds.SIGNIFICANT_FORM_DIFF:
            confidence_factors.append(('differential', 0.9))
        elif strength_diff > 0.3 or form_diff > 0.3:
            confidence_factors.append(('differential', 0.7))
        else:
            confidence_factors.append(('differential', 0.5))
        
        # 3. PROBABILIDADE DOMINANTE
        # Se um resultado tem probabilidade muito maior que outros = mais confiança
        max_prob = max(consensus.values()) if consensus else 0.33
        
        if max_prob > 0.60:
            confidence_factors.append(('dominance', 1.0))
        elif max_prob > 0.50:
            confidence_factors.append(('dominance', 0.8))
        else:
            confidence_factors.append(('dominance', 0.6))
        
        # Calcular score final (média ponderada)
        weights = {'consensus': 0.4, 'differential': 0.3, 'dominance': 0.3}
        
        confidence_score = sum(
            score * weights.get(factor, 1.0) 
            for factor, score in confidence_factors
        )
        
        # Converter para estrelas (1-5)
        stars = max(1, min(5, int(confidence_score * 5) + 1))
        
        # Nível textual baseado em DecisionThresholds
        # Nota: MIN_CONFIDENCE = 0.75 é para PUBLICAÇÃO, não para classificação de confiança
        # Aqui usamos thresholds diferentes para classificar níveis
        if confidence_score >= 0.80:  # Muito alta
            level = 'very_high'
            level_pt = 'Muito Alta'
        elif confidence_score >= 0.65:  # Alta
            level = 'high'
            level_pt = 'Alta'
        elif confidence_score >= 0.50:  # Média
            level = 'medium'
            level_pt = 'Média'
        else:  # Baixa
            level = 'low'
            level_pt = 'Baixa'
        
        return {
            'score': round(confidence_score, 2),
            'stars': stars,
            'level': level,
            'level_pt': level_pt,
            'factors': dict(confidence_factors)
        }
    
    def _assess_risk(self, model_predictions, features, market_odds):
        """
        Avalia risco baseado em:
        1. Incerteza do modelo (entropia)
        2. Volatilidade (lesões, fadiga)
        3. Odds (baixa odd = baixo risco percebido)
        """
        consensus = model_predictions.get('consensus', {})
        context = features.get('context', {})
        
        risk_factors = []
        
        # 1. ENTROPIA (incerteza)
        # Se probabilidades são muito equilibradas = alto risco
        probs = list(consensus.values())
        if probs:
            entropy = -sum(p * np.log(p + 1e-10) for p in probs if p > 0)
            normalized_entropy = entropy / np.log(3)  # Normalizar por máximo (log(3))
            
            risk_factors.append(normalized_entropy * 0.4)
        
        # 2. FADIGA
        if context.get('home_is_fatigued') or context.get('away_is_fatigued'):
            risk_factors.append(0.3)
        
        # 3. ODDS DO MERCADO
        # Odds baixas = mercado acha seguro
        market = features.get('market', {})
        min_odd = min(
            market.get('home', 3.0),
            market.get('draw', 3.0),
            market.get('away', 3.0)
        )
        
        if min_odd < 1.5:
            risk_factors.append(0.2)  # Baixo risco
        elif min_odd > 3.0:
            risk_factors.append(0.8)  # Alto risco
        else:
            risk_factors.append(0.5)
        
        # Média dos fatores
        avg_risk = sum(risk_factors) / len(risk_factors) if risk_factors else 0.5
        
        if avg_risk < 0.4:
            return 'low'
        elif avg_risk < 0.7:
            return 'medium'
        else:
            return 'high'
    
    def _generate_recommendation(self, value_bets, confidence, risk, 
                                 model_predictions, market_odds):
        """
        Gera recomendação final
        
        Prioridade RECALIBRADA (após validação):
        1. BTTS se probabilidade >= 65% (melhor mercado: 61.67% accuracy)
        2. Value bet com confiança alta
        3. Resultado mais provável
        """
        consensus = model_predictions.get('consensus', {})
        poisson_probs = model_predictions.get('poisson', {}).get('probabilities', {})
        
        # PRIORIDADE 1: BTTS com alta probabilidade (melhor mercado histórico)
        btts_prob = poisson_probs.get('btts', 0)
        # ✅ Extrair valor numérico de odd enriquecida
        btts_odd_raw = market_odds.get('btts_yes', 0)
        btts_odd = btts_odd_raw.get('value', 0) if isinstance(btts_odd_raw, dict) else (float(btts_odd_raw) if btts_odd_raw else 0)
        
        if btts_prob >= 0.65 and btts_odd > 0:
            # BTTS mostrou 61.67% accuracy - priorizar quando confiança alta
            return {
                'market': 'btts',
                'market_display': 'Ambos Marcam',
                'pick': 'Sim',
                'probability': btts_prob,
                'odd': btts_odd,
                'reason': 'btts_priority',
                'reason_pt': f'BTTS com {btts_prob*100:.1f}% probabilidade (histórico: 61.67% acurácia)'
            }
        
        # PRIORIDADE 2: Value bet com confiança suficiente
        # MUDANÇA: Priorizar value bet APENAS se probabilidade >= 30%
        # (evitar recomendar apostas improváveis só pelo EV alto)
        if value_bets and confidence['score'] >= 0.65:
            best_value = value_bets[0]
            
            # ✅ Só priorizar value bet se probabilidade razoável (>= 30%)
            if best_value['model_probability'] >= 0.30:
                return {
                    'market': best_value['market'],
                    'market_display': best_value['market_display'],
                    'pick': self._format_pick(best_value['market']),
                    'probability': best_value['model_probability'],
                    'odd': best_value['market_odd'],
                    'fair_odd': best_value['fair_odd'],
                    'value_pct': best_value['value_pct'],
                    'stake_suggestion': best_value['stake_suggestion'],
                    'reason': 'value_bet',
                    'reason_pt': f"Value bet com {best_value['value_pct']:.1f}% de edge"
                }
            # Se value bet tem probabilidade baixa, cair para resultado mais provável (continua abaixo)
        
        # PRIORIDADE 3: Resultado mais provável (SEM VIÉS)
        # CORREÇÃO: Usar threshold realista baseado em validação (36% accuracy → 55%+ esperado)
        prob_home = consensus.get('home_win', 0)
        prob_draw = consensus.get('draw', 0)
        prob_away = consensus.get('away_win', 0)
        
        # Análise: Distribuição real de resultados é ~30% Casa, ~42% Empate, ~30% Fora
        # Sistema estava prevendo Empate 72% das vezes (threshold 25% era muito baixo)
        
        # SEMPRE escolher resultado com MAIOR probabilidade (sem viés)
        # Análise mostrou: probabilidades médias são Casa 42%, Empate 26%, Fora 31%
        # Mas em empates reais, empate raramente é máximo (fica 23-30%)
        
        # Estratégia: Escolher máximo DIRETO, sem threshold artificial
        max_market = max(consensus.items(), key=lambda x: x[1])
        market_name = max_market[0]
        probability = max_market[1]
        
        # Sem overrides - deixar probabilidades decidirem naturalmente
        
        # Buscar odd do mercado
        market_mapping = {
            'home_win': 'home',
            'draw': 'draw',
            'away_win': 'away'
        }
        
        # ✅ Extrair valor numérico de odd enriquecida
        odd_raw = market_odds.get(market_mapping.get(market_name, 'home'), 0)
        odd = odd_raw.get('value', 0) if isinstance(odd_raw, dict) else (float(odd_raw) if odd_raw else 0)
        
        return {
            'market': market_name,
            'market_display': self._format_market_name(market_name),
            'pick': self._format_pick(market_name),
            'probability': probability,
            'odd': odd,
            'reason': 'most_likely',
                'reason_pt': 'Resultado mais provável segundo modelos'
            }
    
    def _format_market_name(self, market):
        """Formata nome do mercado para display"""
        names = {
            'home_win': 'Vitória Casa',
            'draw': 'Empate',
            'away_win': 'Vitória Fora',
            'over_2_5': 'Over 2.5 gols',
            'under_2_5': 'Under 2.5 gols',
            'over_1_5': 'Over 1.5 gols',
            'under_1_5': 'Under 1.5 gols',
            'over_3_5': 'Over 3.5 gols',
            'under_3_5': 'Under 3.5 gols',
            'btts': 'Ambos Marcam',
            'btts_no': 'Ambos Não Marcam',
            'home_over_0_5': 'Casa Over 0.5',
            'home_over_1_5': 'Casa Over 1.5',
            'away_over_0_5': 'Fora Over 0.5',
            'away_over_1_5': 'Fora Over 1.5',
            'home_clean_sheet': 'Casa Clean Sheet',
            'away_clean_sheet': 'Fora Clean Sheet',
        }
        return names.get(market, market)
    
    def _format_pick(self, market):
        """Formata pick para display (será substituído pelo nome do time)"""
        if market == 'home_win':
            return 'Casa'
        elif market == 'away_win':
            return 'Fora'
        else:
            return self._format_market_name(market)
    
    def select_top_bets(self, model_predictions, market_odds, confidence, risk, strategy='value'):
        """
        DECISÃO OBJETIVA das top 3 apostas (SEM IA).
        
        Args:
            strategy (str): 'value' (EV máximo) ou 'multiple' (prob alta + EV positivo)
        
        Critérios (em ordem de prioridade):
        - VALUE: #1 = mais provável 1X2, #2 e #3 = melhor score (priorizando EV)
        - MULTIPLE: Top 3 por score (priorizando probabilidade >= 50%), SEM forçar 1X2
        
        Returns:
            list: [
                {
                    'rank': 1,
                    'market': 'away_win',
                    'market_display': 'Vitória Fora',
                    'pick': 'Tottenham',
                    'probability': 0.406,
                    'market_odd': 2.46,
                    'fair_odd': 2.46,
                    'ev_pct': 0.0,
                    'stake_units': 1.0,
                    'score': 0.85,
                    'reason': 'Resultado mais provável com boa confiança'
                },
                ...
            ]
        """
        logger.info(f"\n📊 SELECT_TOP_BETS - Estratégia: {strategy.upper()}")
        if strategy == 'multiple':
            logger.info(f"   🎯 Modo: BILHETES - prob² domina, filtro progressivo (70%: -15%, 60%: -10%, 50%: -5%)")
        else:
            logger.info(f"   ⚡ Modo: APOSTAS SIMPLES - EV domina, aceita qualquer prob com EV ≥ -5%")
        
        consensus = model_predictions.get('consensus', {})
        poisson_probs = model_predictions.get('poisson', {}).get('probabilities', {})
        fair_odds = self._calculate_fair_odds(model_predictions)
        
        # ✅ Garantir que market_odds seja dict (não None)
        if market_odds is None:
            market_odds = {}
            logger.warning("⚠️ market_odds is None - convertido para {} vazio")
        
        logger.info(f"🔍 DEBUG select_top_bets - market_odds type: {type(market_odds)}, value: {market_odds}")
        logger.info(f"🔍 DEBUG select_top_bets - consensus: {consensus}")
        
        # Preparar candidatos
        candidates = []
        
        # Helper to fetch odds with fallback keys (suporta dict enriquecido)
        def _get_odd(odds_dict, keys):
            """Extrai valor numérico de odd, suportando dict {'value': x} ou número direto."""
            for k in keys:
                v = odds_dict.get(k)
                if v is not None:
                    # Se for dict enriquecido, extrair 'value'
                    if isinstance(v, dict):
                        numeric = v.get('value')
                        if numeric is not None:
                            try:
                                return float(numeric)
                            except (TypeError, ValueError):
                                continue
                    # Se for número direto
                    else:
                        try:
                            return float(v)
                        except (TypeError, ValueError):
                            continue
            return 0

        # 1X2 (support alt keys like 'home_win'/'away_win')
        for market, prob_key, odds_keys in [
            ('home_win', 'home_win', ['home', 'home_win']),
            ('draw', 'draw', ['draw']),
            ('away_win', 'away_win', ['away', 'away_win'])
        ]:
            prob = consensus.get(prob_key, 0)
            market_odd = _get_odd(market_odds, odds_keys)
            fair_odd = fair_odds.get(market, 0)
            
            logger.info(f"🔍 Candidato {market}: prob={prob:.3f}, market_odd={market_odd}, fair_odd={fair_odd:.2f}")
            
            # ✅ Verificar se market_odd não é None antes de comparar
            if prob >= 0.15 and market_odd is not None and market_odd > 0 and fair_odd > 0:  # Reduzido de 30% para 15%
                ev_pct = ((market_odd / fair_odd) - 1) * 100
                score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                
                logger.debug(f"   Candidato {market}: prob={prob:.2f}, EV={ev_pct:+.1f}%, score={score:.3f} (strategy={strategy})")
                
                candidates.append({
                    'market': market,
                    'market_display': self._format_market_name(market),
                    'pick': self._format_pick(market),
                    'probability': prob,
                    'market_odd': market_odd,
                    'fair_odd': fair_odd,
                    'ev_pct': ev_pct,
                    'score': score,
                    'category': '1x2'
                })
        
        # Over/Under 2.5 (support 'over_2_5' and 'over_25' etc.)
        for market, prob_key, alt_keys in [
            ('over_2_5', 'over_2.5', ['over_2_5', 'over_25']),  # ✅ FIX: Use 'over_2.5' (dot) to match Poisson output
            ('under_2_5', 'under_2.5', ['under_2_5', 'under_25'])
        ]:
            prob = poisson_probs.get(prob_key, 0)
            market_odd = _get_odd(market_odds, alt_keys)
            fair_odd = fair_odds.get(market, 0)
            
            logger.info(f"DEBUG Over/Under 2.5: market={market}, prob={prob:.2f}, market_odd={market_odd}, fair_odd={fair_odd}")
            
            # ✅ Verificar se market_odd não é None antes de comparar
            if prob >= 0.30 and market_odd is not None and market_odd > 0 and fair_odd > 0:
                ev_pct = ((market_odd / fair_odd) - 1) * 100
                score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                
                logger.debug(f"   Candidato {market}: prob={prob:.2f}, EV={ev_pct:+.1f}%, score={score:.3f} (strategy={strategy})")
                
                candidates.append({
                    'market': market,
                    'market_display': self._format_market_name(market),
                    'pick': self._format_pick(market),
                    'probability': prob,
                    'market_odd': market_odd,
                    'fair_odd': fair_odd,
                    'ev_pct': ev_pct,
                    'score': score,
                    'category': 'totals'
                })
        
        # Over/Under 0.5 (muito alto/baixo score)
        for market, prob_key, alt_keys in [('over_0_5', 'over_0.5', ['over_0_5', 'over_05']), ('under_0_5', 'under_0.5', ['under_0_5', 'under_05'])]:
            prob = poisson_probs.get(prob_key, 0)
            market_odd = _get_odd(market_odds, alt_keys)
            fair_odd = fair_odds.get(market, 0)
            if prob >= 0.85 and market_odd is not None and market_odd > 0 and fair_odd > 0:  # Muito provável
                ev_pct = ((market_odd / fair_odd) - 1) * 100
                score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                candidates.append({
                    'market': market,
                    'market_display': f"{'Over' if 'over' in market else 'Under'} 0.5 gols",
                    'pick': 'Sim' if 'over' in market else 'Não',
                    'probability': prob,
                    'market_odd': market_odd,
                    'fair_odd': fair_odd,
                    'ev_pct': ev_pct,
                    'score': score,
                    'category': 'totals'
                })
        
        # Over/Under 4.5 (jogos com muitos gols)
        for market, prob_key, alt_keys in [('over_4_5', 'over_4.5', ['over_4_5', 'over_45']), ('under_4_5', 'under_4.5', ['under_4_5', 'under_45'])]:
            prob = poisson_probs.get(prob_key, 0)
            market_odd = _get_odd(market_odds, alt_keys)
            fair_odd = fair_odds.get(market, 0)
            if prob >= 0.15 and market_odd is not None and market_odd > 0 and fair_odd > 0:  # Threshold baixo
                ev_pct = ((market_odd / fair_odd) - 1) * 100
                score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                candidates.append({
                    'market': market,
                    'market_display': f"{'Over' if 'over' in market else 'Under'} 4.5 gols",
                    'pick': 'Sim' if 'over' in market else 'Não',
                    'probability': prob,
                    'market_odd': market_odd,
                    'fair_odd': fair_odd,
                    'ev_pct': ev_pct,
                    'score': score,
                    'category': 'totals'
                })
        
        # Asian Lines (1.75, 2.25, 2.75, 3.25)
        for market, prob_key, alt_keys in [
            ('over_1_75', 'over_1.75', ['over_1_75', 'over_175']), ('under_1_75', 'under_1.75', ['under_1_75', 'under_175']),
            ('over_2_25', 'over_2.25', ['over_2_25', 'over_225']), ('under_2_25', 'under_2.25', ['under_2_25', 'under_225']),
            ('over_2_75', 'over_2.75', ['over_2_75', 'over_275']), ('under_2_75', 'under_2.75', ['under_2_75', 'under_275']),
            ('over_3_25', 'over_3.25', ['over_3_25', 'over_325']), ('under_3_25', 'under_3.25', ['under_3_25', 'under_325'])
        ]:
            prob = poisson_probs.get(prob_key, 0)
            market_odd = _get_odd(market_odds, alt_keys)
            fair_odd = fair_odds.get(market, 0)
            if prob >= 0.25 and market_odd is not None and market_odd > 0 and fair_odd > 0:
                ev_pct = ((market_odd / fair_odd) - 1) * 100
                score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                candidates.append({
                    'market': market,
                    'market_display': f"{'Over' if 'over' in market else 'Under'} {prob_key.split('_')[1]} gols",
                    'pick': 'Sim' if 'over' in market else 'Não',
                    'probability': prob,
                    'market_odd': market_odd,
                    'fair_odd': fair_odd,
                    'ev_pct': ev_pct,
                    'score': score,
                    'category': 'asian_lines'
                })
        
        # BTTS Yes
        btts_prob = poisson_probs.get('btts', 0)
        btts_odd = _get_odd(market_odds, ['btts_yes', 'btts'])  # ✅ Usar helper com fallback
        btts_fair = fair_odds.get('btts', 0)
        
        if btts_prob >= 0.30 and btts_odd > 0 and btts_fair > 0:
            ev_pct = ((btts_odd / btts_fair) - 1) * 100
            score = self._calculate_bet_score(btts_prob, ev_pct, confidence, risk, strategy)
            
            logger.debug(f"   Candidato btts: prob={btts_prob:.2f}, EV={ev_pct:+.1f}%, score={score:.3f} (strategy={strategy})")
            
            candidates.append({
                'market': 'btts',
                'market_display': 'Ambos Marcam',
                'pick': 'Sim',
                'probability': btts_prob,
                'market_odd': btts_odd,
                'fair_odd': btts_fair,
                'ev_pct': ev_pct,
                'score': score,
                'category': 'btts'
            })
        
        # BTTS No (ambos não marcam)
        btts_no_prob = poisson_probs.get('btts_no', 1 - btts_prob)  # Inverso de BTTS
        btts_no_odd = _get_odd(market_odds, ['btts_no'])
        btts_no_fair = (1 / btts_no_prob) * 1.05 if btts_no_prob > 0 else 0
        if btts_no_odd == 0:  # Fallback
            btts_no_odd = btts_no_fair
        
        if btts_no_prob >= 0.30 and btts_no_odd > 0 and btts_no_fair > 0:
            ev_pct = ((btts_no_odd / btts_no_fair) - 1) * 100
            score = self._calculate_bet_score(btts_no_prob, ev_pct, confidence, risk, strategy)
            candidates.append({
                'market': 'btts_no',
                'market_display': 'Ambos Não Marcam',
                'pick': 'Sim',
                'probability': btts_no_prob,
                'market_odd': btts_no_odd,
                'fair_odd': btts_no_fair,
                'ev_pct': ev_pct,
                'score': score,
                'category': 'btts'
            })
        
        # Clean Sheets
        for market_key, prob_key, display in [
            ('home_clean_sheet', 'home_clean_sheet', 'Casa Clean Sheet'),
            ('away_clean_sheet', 'away_clean_sheet', 'Fora Clean Sheet')
        ]:
            prob = poisson_probs.get(prob_key, 0)
            fair_odd = (1 / prob) * 1.05 if prob > 0 else 0
            market_odd = _get_odd(market_odds, [market_key])
            if market_odd == 0:
                market_odd = fair_odd
            
            if prob >= 0.25 and fair_odd > 0:  # Clean sheets com 25%+
                ev_pct = ((market_odd / fair_odd) - 1) * 100 if market_odd > 0 else 0
                score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                candidates.append({
                    'market': market_key,
                    'market_display': display,
                    'pick': 'Sim',
                    'probability': prob,
                    'market_odd': market_odd if market_odd > 0 else fair_odd,
                    'fair_odd': fair_odd,
                    'ev_pct': ev_pct,
                    'score': score,
                    'category': 'clean_sheet'
                })
        
        # Margens de Vitória
        for market_key, prob_key, display in [
            ('home_by_1', 'home_by_1', 'Casa por 1 gol'),
            ('home_by_2plus', 'home_by_2plus', 'Casa por 2+ gols'),
            ('away_by_1', 'away_by_1', 'Fora por 1 gol'),
            ('away_by_2plus', 'away_by_2plus', 'Fora por 2+ gols')
        ]:
            prob = poisson_probs.get(prob_key, 0)
            fair_odd = (1 / prob) * 1.05 if prob > 0 else 0
            market_odd = _get_odd(market_odds, [market_key])
            if market_odd == 0:
                market_odd = fair_odd
            
            if prob >= 0.15 and fair_odd > 0:  # Margens com 15%+
                ev_pct = ((market_odd / fair_odd) - 1) * 100 if market_odd > 0 else 0
                score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                candidates.append({
                    'market': market_key,
                    'market_display': display,
                    'pick': 'Sim',
                    'probability': prob,
                    'market_odd': market_odd if market_odd > 0 else fair_odd,
                    'fair_odd': fair_odd,
                    'ev_pct': ev_pct,
                    'score': score,
                    'category': 'winning_margin'
                })
        
        # Odd/Even Goals
        for market_key, prob_key, display in [
            ('odd_goals', 'odd_goals', 'Gols Ímpares'),
            ('even_goals', 'even_goals', 'Gols Pares')
        ]:
            prob = poisson_probs.get(prob_key, 0)
            fair_odd = (1 / prob) * 1.05 if prob > 0 else 0
            market_odd = _get_odd(market_odds, [market_key])
            if market_odd == 0:
                market_odd = fair_odd
            
            if prob >= 0.40 and fair_odd > 0:  # Só incluir se razoavelmente provável
                ev_pct = ((market_odd / fair_odd) - 1) * 100 if market_odd > 0 else 0
                score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                candidates.append({
                    'market': market_key,
                    'market_display': display,
                    'pick': 'Sim',
                    'probability': prob,
                    'market_odd': market_odd if market_odd > 0 else fair_odd,
                    'fair_odd': fair_odd,
                    'ev_pct': ev_pct,
                    'score': score,
                    'category': 'specials'
                })
        
        # NOVOS MERCADOS: Over/Under 1.5, 3.5, Dupla Chance
        # Over/Under 1.5 (support alt keys 'over_15')
        for market, prob_key, alt_keys in [('over_1_5', 'over_1.5', ['over_1_5', 'over_15']), ('under_1_5', 'under_1.5', ['under_1_5', 'under_15'])]:  # ✅ FIX: Use dots
            prob = poisson_probs.get(prob_key, 0)
            market_odd = _get_odd(market_odds, alt_keys)
            fair_odd = fair_odds.get(market, 0)
            
            # Threshold 25% para VALUE, 35% seria rejeitado por MULTIPLE de qualquer forma
            if prob >= 0.25 and market_odd is not None and market_odd > 0 and fair_odd > 0:
                ev_pct = ((market_odd / fair_odd) - 1) * 100
                score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                
                logger.debug(f"   Candidato {market}: prob={prob:.2f}, EV={ev_pct:+.1f}%, score={score:.3f}")
                
                candidates.append({
                    'market': market,
                    'market_display': f"{'Over' if 'over' in market else 'Under'} 1.5 gols",
                    'pick': 'Sim' if 'over' in market else 'Não',
                    'probability': prob,
                    'market_odd': market_odd,
                    'fair_odd': fair_odd,
                    'ev_pct': ev_pct,
                    'score': score,
                    'category': 'totals'
                })
        
        # Over/Under 3.5 (support alt keys 'over_35')
        for market, prob_key, alt_keys in [('over_3_5', 'over_3.5', ['over_3_5', 'over_35']), ('under_3_5', 'under_3.5', ['under_3_5', 'under_35'])]:  # ✅ FIX: Use dots
            prob = poisson_probs.get(prob_key, 0)
            market_odd = _get_odd(market_odds, alt_keys)
            fair_odd = fair_odds.get(market, 0)
            
            # Threshold 20% para VALUE (jogos ofensivos), MULTIPLE vai filtrar naturalmente
            if prob >= 0.20 and market_odd is not None and market_odd > 0 and fair_odd > 0:
                ev_pct = ((market_odd / fair_odd) - 1) * 100
                score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                
                logger.debug(f"   Candidato {market}: prob={prob:.2f}, EV={ev_pct:+.1f}%, score={score:.3f}")
                
                candidates.append({
                    'market': market,
                    'market_display': f"{'Over' if 'over' in market else 'Under'} 3.5 gols",
                    'pick': 'Sim' if 'over' in market else 'Não',
                    'probability': prob,
                    'market_odd': market_odd,
                    'fair_odd': fair_odd,
                    'ev_pct': ev_pct,
                    'score': score,
                    'category': 'totals'
                })
        
        # Dupla Chance (usar odds de mercado quando disponíveis; suportar chaves alternativas)
        prob_1x = consensus.get('home_win', 0) + consensus.get('draw', 0)
        prob_12 = consensus.get('home_win', 0) + consensus.get('away_win', 0)
        prob_x2 = consensus.get('draw', 0) + consensus.get('away_win', 0)
        
        # Mapear chaves alternativas presentes no OddsCalculator ("1x", "12", "x2")
        dc_alt_keys = {
            'double_chance_1x': ['double_chance_1x', '1x'],
            'double_chance_12': ['double_chance_12', '12'],
            'double_chance_x2': ['double_chance_x2', 'x2']
        }

        for market_key, display, prob in [
            ('double_chance_1x', 'Casa ou Empate (1X)', prob_1x),
            ('double_chance_12', 'Casa ou Fora (12)', prob_12),
            ('double_chance_x2', 'Empate ou Fora (X2)', prob_x2)
        ]:
            if prob >= 0.60:  # Dupla chance só faz sentido com alta probabilidade
                fair_odd = (1 / prob) * 1.05 if prob > 0 else 0
                # Tentar buscar odd usando chaves alternativas (compatível com OddsCalculator)
                alt_keys = dc_alt_keys.get(market_key, [market_key])
                market_odd = _get_odd(market_odds, alt_keys)
                if market_odd == 0:  # Fallback para fair_odd se não tiver no mercado
                    market_odd = fair_odd
                
                if fair_odd > 0:
                    ev_pct = ((market_odd / fair_odd) - 1) * 100
                    score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                    
                    logger.debug(f"   Candidato {market_key}: prob={prob:.2f}, EV={ev_pct:+.1f}%, score={score:.3f}")
                    
                    candidates.append({
                        'market': market_key,
                        'market_display': display,
                        'pick': 'Sim',
                        'probability': prob,
                        'market_odd': market_odd,
                        'fair_odd': fair_odd,
                        'ev_pct': ev_pct,
                        'score': score,
                        'category': 'double_chance'
                    })
        
        # Team Total Goals (usando fair odds se disponível) - Expandido para incluir 2.5
        for market_key, prob_key, display in [
            ('home_over_05', 'home_over_0.5', 'Casa Over 0.5'),  # ✅ FIX: Use dots
            ('home_over_15', 'home_over_1.5', 'Casa Over 1.5'),
            ('home_over_25', 'home_over_2.5', 'Casa Over 2.5'),  # ✅ NOVO
            ('away_over_05', 'away_over_0.5', 'Fora Over 0.5'),
            ('away_over_15', 'away_over_1.5', 'Fora Over 1.5'),
            ('away_over_25', 'away_over_2.5', 'Fora Over 2.5')   # ✅ NOVO
        ]:
            prob = poisson_probs.get(prob_key, 0)
            fair_odd = fair_odds.get(market_key, 0)
            market_odd = _get_odd(market_odds, [market_key])  # ✅ Usar helper
            if market_odd == 0:  # Fallback para fair_odd
                market_odd = fair_odd if fair_odd > 0 else 0
            
            # Threshold ajustado: Over 0.5 >= 50%, Over 1.5/2.5 >= 30%
            min_prob = 0.50 if '0.5' in prob_key else 0.30
            if prob >= min_prob and fair_odd > 0:
                ev_pct = ((market_odd / fair_odd) - 1) * 100 if market_odd > 0 else 0
                score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
                
                logger.debug(f"   Candidato {market_key}: prob={prob:.2f}, EV={ev_pct:+.1f}%, score={score:.3f}")
                
                candidates.append({
                    'market': market_key,
                    'market_display': display,
                    'pick': 'Sim',
                    'probability': prob,
                    'market_odd': market_odd if market_odd > 0 else fair_odd,
                    'fair_odd': fair_odd,
                    'ev_pct': ev_pct,
                    'score': score,
                    'category': 'team_goals'
                })
        #             'pick': self._format_pick(market),
        #             'probability': prob,
        #             'market_odd': market_odd,
        #             'fair_odd': fair_odd,
        #             'ev_pct': ev_pct,
        #             'score': score,
        #             'category': 'specials'
        #         })
        
        # DEBUG: Ver candidatos e detectar viés por categoria
        only_1x2 = [c for c in candidates if c['category'] == '1x2']
        only_totals = [c for c in candidates if c['category'] == 'totals']
        only_btts = [c for c in candidates if c['category'] == 'btts']
        only_dc = [c for c in candidates if c['category'] == 'double_chance']
        only_team = [c for c in candidates if c['category'] == 'team_goals']
        
        logger.info(f"   📊 ANÁLISE DE CANDIDATOS POR CATEGORIA:")
        logger.info(f"      1X2: {len(only_1x2)} candidatos" + (f" (avg prob: {sum(c['probability'] for c in only_1x2) / len(only_1x2) * 100:.1f}%)" if only_1x2 else ""))
        logger.info(f"      Totals: {len(only_totals)} candidatos" + (f" (avg prob: {sum(c['probability'] for c in only_totals) / len(only_totals) * 100:.1f}%)" if only_totals else ""))
        logger.info(f"      BTTS: {len(only_btts)} candidatos" + (f" (avg prob: {sum(c['probability'] for c in only_btts) / len(only_btts) * 100:.1f}%)" if only_btts else ""))
        logger.info(f"      Double Chance: {len(only_dc)} candidatos" + (f" (avg prob: {sum(c['probability'] for c in only_dc) / len(only_dc) * 100:.1f}%)" if only_dc else ""))
        logger.info(f"      Team Goals: {len(only_team)} candidatos" + (f" (avg prob: {sum(c['probability'] for c in only_team) / len(only_team) * 100:.1f}%)" if only_team else ""))
        logger.info(f"   Total de candidatos: {len(candidates)}")
        
        # Ajustes para estratégia MULTIPLE: preferir odds entre 1.30 e 2.00 e X2 quando visitante favorito
        if strategy == 'multiple':
            away_favored = consensus.get('away_win', 0) > consensus.get('home_win', 0)
            for c in candidates:
                # Excluir odds fora da faixa ideal para bilhetes múltiplos
                if c['category'] in ('totals', 'btts'):
                    if c['market_odd'] is None or c['market_odd'] < 1.30 or c['market_odd'] > 2.10:
                        c['score'] = 0
                # Boost para X2 quando fora é favorito
                if c['category'] == 'double_chance' and c['market'] == 'double_chance_x2' and away_favored:
                    c['score'] *= 1.15

        # Filtrar candidatos com score > 0 (já aplica filtro do strategy)
        valid_candidates = [c for c in candidates if c['score'] > 0]
        
        # Log candidatos rejeitados para debug
        rejected = [c for c in candidates if c['score'] == 0]
        if rejected:
            logger.info(f"   ⚠️ {len(rejected)} candidatos rejeitados (score=0):")
            for c in rejected[:5]:  # Mostrar até 5 rejeitados
                logger.info(f"      ❌ {c['market_display']}: prob={c['probability']*100:.1f}%, EV={c['ev_pct']:+.1f}%")
        
        logger.info(f"   Candidatos válidos (score > 0): {len(valid_candidates)}")
        
        if not valid_candidates:
            logger.warning("   ⚠️ Nenhum candidato válido encontrado!")
            return []
        
        # ESTRATÉGIA DIFERENCIADA
        selected = []
        
        if strategy == 'value':
            # MODO VALUE: Priorizar VALUE REAL (EV positivo ou neutro)
            logger.info("   ⚡ Aplicando lógica VALUE: priorizando EV positivo/neutro (value betting)")
            
            # MUDANÇA CRÍTICA: VALUE deve buscar apostas com value REAL (EV ≥ 0%)
            # Só aceitar EV negativo se não houver opções com EV positivo
            positive_ev = [c for c in valid_candidates if c['ev_pct'] >= 0]
            neutral_ev = [c for c in valid_candidates if c['ev_pct'] >= -2]
            all_candidates = [c for c in valid_candidates if c['ev_pct'] >= -5]
            
            if positive_ev:
                # Ideal: apostas com value real
                value_candidates = positive_ev
                logger.info(f"   ✅ {len(positive_ev)} apostas com EV positivo encontradas - usando apenas estas")
            elif neutral_ev:
                # Aceitável: apostas neutras
                value_candidates = neutral_ev
                logger.warning(f"   ⚠️ Nenhuma aposta com EV positivo - usando {len(neutral_ev)} apostas com EV neutro (≥ -2%)")
            elif all_candidates:
                # Último recurso: apostas com EV até -5%
                value_candidates = all_candidates
                logger.warning(f"   ⚠️ Nenhuma aposta com EV positivo/neutro - usando {len(all_candidates)} apostas com EV ≥ -5%")
            else:
                logger.warning("   ⚠️ Nenhuma aposta com EV aceitável (todas < -5%)")
                return []
            
            # Ordenar por score (EV domina)
            others = sorted(value_candidates, key=lambda x: x['score'], reverse=True)
            used_categories = set()
            
            logger.info("   Top 5 candidatos VALUE por score:")
            for i, c in enumerate(others[:5], 1):
                logger.info(f"      {i}. [{c['category']}] {c['market_display']} - Prob: {c['probability']*100:.1f}%, EV: {c['ev_pct']:+.1f}%, Score: {c['score']:.3f}")
            
        else:
            # MODO MULTIPLE: Top 3 por score (prob^1.5 domina), SEM forçar 1X2
            logger.info("   📋 Aplicando lógica MULTIPLE: puro ranking por score (prob^1.5 + EV)")
            
            # Ordenar TODOS os candidatos válidos por score
            others = sorted(valid_candidates, key=lambda x: x['score'], reverse=True)
            used_categories = set()
            
            logger.info("   Top 5 candidatos por score:")
            for i, c in enumerate(others[:5], 1):
                logger.info(f"      {i}. [{c['category']}] {c['market_display']} - Prob: {c['probability']*100:.1f}%, EV: {c['ev_pct']:+.1f}%, Score: {c['score']:.3f}")
        
        # Top 3 (mantendo foco nas melhores apostas)
        used_markets = set()  # ✅ Rastrear mercados já usados
        for candidate in others:
            if len(selected) >= 3:  # Top 3 apostas
                break
            
            # ✅ Evitar duplicatas de mercado
            if candidate['market'] in used_markets:
                continue
            
            # Preferir categorias diferentes quando possível
            if candidate['category'] not in used_categories or len([c for c in others if c['category'] not in used_categories]) == 0:
                stake_units = self._calculate_stake_units(
                    candidate['ev_pct'],
                    candidate['probability']
                )
                
                selected.append({
                    'rank': len(selected) + 1,
                    'market': candidate['market'],
                    'market_display': candidate['market_display'],
                    'pick': candidate['pick'],
                    'probability': candidate['probability'],
                    'market_odd': candidate['market_odd'],
                    'fair_odd': candidate['fair_odd'],
                    'ev_pct': candidate['ev_pct'],
                    'stake_units': stake_units,
                    'score': candidate['score'],
                    'reason': self._generate_bet_reason(candidate, confidence, risk)
                })
                
                used_categories.add(candidate['category'])
                used_markets.add(candidate['market'])  # ✅ Marcar mercado como usado
        
        logger.info(f"\n   ✅ Top {len(selected)} selecionadas:")
        for bet in selected:
            logger.info(f"      #{bet['rank']}: {bet['market_display']} - {bet['pick']}")
            logger.info(f"         Prob: {bet['probability']*100:.1f}%, Odd: {bet['market_odd']}, EV: {bet['ev_pct']:+.1f}%, Score: {bet['score']:.3f}")
        
        return selected
    
    def _calculate_bet_score(self, probability, ev_pct, confidence, risk, strategy='value'):
        """
        Score OBJETIVO para ranking de apostas.
        
        Formula adaptada por estratégia:
        - VALUE: prob × ev_weight × conf × risk
          * EV < 0: ev_weight = max(0.3, 1 + EV/20) - penalização severa
          * EV ≥ 0: ev_weight = 1 + EV/30 - amplificação forte
        - MULTIPLE: prob^1.5 × (1 + EV/200) × conf × risk
        
        Modo VALUE:
        - Probabilidade linear (sem penalização)
        - EV DOMINANTE:
          * EV negativo: peso 5x maior (-2% → -10% de impacto vs -2% original)
          * EV positivo: peso 3x maior (+30% → +100% de impacto vs +30% original)
        - Objetivo: Apostas com EV +20% superam favoritos 85% com EV -2%
        
        Modo MULTIPLE:
        - Probabilidade QUADRÁTICA elevada a 1.5 (65%→52%, 30%→16%)
        - EV tem metade do peso (dividido por 200)
        - Objetivo: Favoritos 70% superam underdogs 40% mesmo com EV maior
        
        Exemplos MODE VALUE (conf=1.0, risk=1.0):
        - Under 2.5: prob=52.3%, EV=+23% → score = 0.523 × 1.767 = 0.924 ✅
        - 1X: prob=86.6%, EV=-2% → score = 0.866 × 0.9 = 0.779
        - Casa Over 0.5: prob=83.2%, EV=-3% → score = 0.832 × 0.85 = 0.707
        
        Resultado: Under 2.5 (+23% EV) vence favoritos com EV negativo!
        """
        conf_factor = confidence.get('score', 0.5)
        
        risk_factor = {
            'low': 1.2,
            'medium': 1.0,
            'high': 0.7
        }.get(risk, 1.0)
        
        if strategy == 'multiple':
            # MODO BILHETE: Prioriza APENAS probabilidade (EV é irrelevante para acumuladores)
            # Quanto maior a probabilidade, maior o peso (prob^1.5)
            prob_weight = probability ** 1.5  
            
            # EV não é usado como filtro - apenas como informação
            # Acumuladores dependem de acertar TODAS as apostas, não de maximizar valor individual
            ev_weight = 1.0  # EV não afeta o score
            
            # Apenas logar warning se EV muito negativo (informativo)
            if ev_pct < -15:
                logger.debug(f"   ⚠️ MULTIPLE: EV={ev_pct:.1f}% muito negativo (mas aprovado por probabilidade)")
            
            logger.debug(f"   ✅ MULTIPLE: prob={probability:.2f}^1.5 = {prob_weight:.3f}, EV IGNORADO (irrelevante para múltiplos)")
        else:
            # MODO VALUE: EV DOMINA - penaliza drasticamente EV negativo
            prob_weight = probability
            
            if ev_pct < 0:
                # EV negativo: penalização severa (peso 5x maior)
                # -2% → 0.9, -5% → 0.75, -10% → 0.5
                ev_weight = max(0.3, 1 + (ev_pct / 20))
            else:
                # EV positivo: amplificação forte (peso 3x maior)
                # +5% → 1.17, +10% → 1.33, +20% → 1.67, +30% → 2.0
                ev_weight = 1 + (ev_pct / 30)
            
            logger.debug(f"   ✅ VALUE: prob={probability:.2f} (linear), ev={ev_pct:.1f}% → ev_weight={ev_weight:.3f} ({'PENALIZADO' if ev_pct < 0 else 'AMPLIFICADO'})")
        
        score = prob_weight * ev_weight * conf_factor * risk_factor
        logger.debug(f"   📊 Score final: {prob_weight:.3f} × {ev_weight:.3f} × {conf_factor:.3f} × {risk_factor:.3f} = {score:.3f}")
        
        return round(score, 3)
    
    def _calculate_ranking_score(self, selection_score, ev_pct, confidence, risk, strategy='value', probability=None):
        """
        NOVO (10/02/2026): Calcula ranking_score final SEM multiplicar probabilidade novamente.
        
        PROBLEMA CORRIGIDO: MarketSelector já calculou selection_score = context × probability.
        DecisionEngine NÃO deve recalcular probabilidade - isso causava prob² ou prob^2.5.
        
        Args:
            selection_score: Score já calculado por MarketSelector (context × prob)
            ev_pct: Expected Value percentual
            confidence: Dict de confiança
            risk: Nível de risco
            strategy: 'value' ou 'multiple'
            probability: Opcional, para logging
        
        Returns:
            float: ranking_score = selection_score × ev_weight × conf × risk
        
        Formula:
        - ranking_score = selection_score × ev_weight × confidence × risk
        - ev_weight depende de strategy:
          * VALUE: EV dominante (penaliza -EV 5x, amplifica +EV 3x)
          * MULTIPLE: EV ignorado (ev_weight = 1.0) - irrelevante para acumuladores
        
        Exemplo:
        - selection_score = 0.60 (MarketSelector: context 80% × prob 75% = 0.60)
        - ev_pct = +10%
        - VALUE: ev_weight = 1.33 → ranking = 0.60 × 1.33 = 0.80
        - MULTIPLE: ev_weight = 1.0 → ranking = 0.60 × 1.0 = 0.60 (EV ignorado)
        """
        conf_factor = confidence.get('score', 0.5)
        risk_factor = {
            'low': 1.2,
            'medium': 1.0,
            'high': 0.7
        }.get(risk, 1.0)
        
        # Calcular ev_weight baseado na estratégia
        if strategy == 'multiple':
            # BILHETE: EV é IRRELEVANTE - foco apenas na probabilidade
            ev_weight = 1.0  # EV não afeta o ranking
        else:
            # VALUE: EV domina
            if ev_pct < 0:
                ev_weight = max(0.3, 1 + (ev_pct / 20))  # Penalização severa
            else:
                ev_weight = 1 + (ev_pct / 30)  # Amplificação forte
        
        ranking_score = selection_score * ev_weight * conf_factor * risk_factor
        
        prob_display = f" (prob={probability:.0%})" if probability else ""
        ev_display = " (EV ignorado)" if strategy == 'multiple' else f" × ev_weight={ev_weight:.3f}"
        logger.debug(f"   📊 Ranking: selection={selection_score:.3f}{prob_display}{ev_display} × conf={conf_factor:.3f} × risk={risk_factor:.3f} = {ranking_score:.3f}")
        
        return round(ranking_score, 3)
    
    def _generate_bet_reason(self, candidate, confidence, risk):
        """Gera razão OBJETIVA para a aposta."""
        prob = candidate['probability'] * 100
        ev = candidate['ev_pct']
        
        # SEMPRE mostrar o EV real para transparência
        if ev > 10:
            return f"Excelente value: {prob:.1f}% prob + {ev:+.1f}% EV"
        elif ev > 5:
            return f"Bom value: {prob:.1f}% prob + {ev:+.1f}% EV"
        elif ev > 0:
            return f"Resultado provável: {prob:.1f}% prob + {ev:+.1f}% EV"
        elif ev > -5:
            # EV negativo pequeno (0% a -5%): mostrar valor real
            return f"Alta probabilidade: {prob:.1f}% (EV: {ev:+.1f}%)"
        else:
            # EV muito negativo (< -5%): mostrar valor real
            return f"Resultado possível: {prob:.1f}% prob (EV: {ev:+.1f}%)"
    
    def _suggest_stake(self, value_pct, probability):
        """
        Sugere tamanho da aposta usando Kelly Criterion simplificado
        
        Kelly = (edge / (odd - 1)) * bankroll
        Mas usamos Kelly fracionário (1/4 Kelly para segurança)
        """
        if value_pct <= 0:
            return "Não apostar"
        
        # Converter value_pct em edge
        edge = value_pct / 100
        
        # Kelly fracionário conservador
        if edge > 0.20:  # Value muito alto (>20%)
            return "3-5% do bankroll"
        elif edge > 0.10:  # Value alto (10-20%)
            return "2-3% do bankroll"
        elif edge > 0.05:  # Value moderado (5-10%)
            return "1-2% do bankroll"
        else:  # Value baixo (<5%)
            return "0.5-1% do bankroll"
    
    def _select_contextual_bets(self, context_analysis, model_predictions, market_odds, 
                               confidence, risk, strategy):
        """
        Seleciona top 3 apostas usando análise contextual.
        
        NOVO: Usa MarketSelector para escolher mercados que o contexto favorece.
        
        Args:
            context_analysis: Padrões contextuais detectados
            model_predictions: Probabilidades dos modelos
            market_odds: Odds do mercado
            confidence: Confiança da análise
            risk: Nível de risco
            strategy: 'value' ou 'multiple'
            
        Returns:
            list: Top 3 apostas contextuais
        """
        logger.info("\n🎯 Seleção Contextual de Mercados")
        logger.info(f"   Padrões detectados: {len(context_analysis.get('patterns', []))}")
        
        # Usar MarketSelector para escolher mercados
        selected_markets = self.market_selector.select_top_markets(
            context_analysis,
            model_predictions,
            market_odds,
            strategy
        )
        
        # Formatar para output padrão do DecisionEngine
        top_bets = []
        for i, market_data in enumerate(selected_markets, 1):
            # NOVO (10/02/2026): Calcular ranking_score usando selection_score do MarketSelector
            # CORREÇÃO: Não recalcular probabilidade (MarketSelector já fez isso)
            selection_score = market_data.get('selection_score', market_data.get('final_score', 0))
            
            # Calcular ranking_score aplicando EV, confidence e risk ao selection_score
            ranking_score = self._calculate_ranking_score(
                selection_score=selection_score,
                ev_pct=market_data['ev_pct'],
                confidence=confidence,
                risk=risk,
                strategy=strategy,
                probability=market_data['probability']
            )
            
            # Calcular stake baseado em EV
            if market_data['ev_pct'] > 0:
                stake_suggestion = self._suggest_stake(market_data['ev_pct'], market_data['probability'])
            else:
                stake_suggestion = "Não recomendado (EV negativo)"
            
            # Determinar pick baseado no mercado
            pick = self._format_pick_for_market(market_data['market'])
            
            bet = {
                'rank': i,
                'market': market_data['market'],
                'market_display': market_data['market_display'],
                'pick': pick,
                'probability': market_data['probability'],
                'market_odd': market_data['market_odd'],
                'fair_odd': market_data['fair_odd'],
                'ev_pct': market_data['ev_pct'],
                'stake_units': self._calculate_stake_units(market_data['ev_pct'], market_data['probability']),
                'selection_score': selection_score,  # Score de seleção (contexto × prob)
                'ranking_score': ranking_score,  # Score final de ranking (selection × ev × conf × risk)
                'score': ranking_score,  # Compatibilidade com código existente
                'reason': market_data['reasoning'],  # Reasoning contextual do MarketSelector
                'context_score': market_data.get('context_score', 0),
                'context_type': market_data.get('context_type', 'NEUTRO')  # Para frontend exibir corretamente
            }
            
            top_bets.append(bet)
        
        logger.info(f"\n✅ {len(top_bets)} apostas contextuais selecionadas")
        
        return top_bets
    
    def _format_pick_for_market(self, market):
        """Formata o pick baseado no tipo de mercado."""
        if market == 'home_win':
            return 'Casa'
        elif market == 'away_win':
            return 'Fora'
        elif market == 'draw':
            return 'Empate'
        elif 'over' in market:
            return 'Over'
        elif 'under' in market:
            return 'Under'
        elif 'btts_yes' in market:
            return 'Ambos Marcam'
        elif 'btts_no' in market:
            return 'Nenhum ou Apenas Um Marca'
        elif 'dnb_home' in market:
            return 'Casa (Empate Anula)'
        elif 'dnb_away' in market:
            return 'Fora (Empate Anula)'
        elif 'draw_ht' in market:
            return 'Empate HT'
        else:
            return market.replace('_', ' ').title()
    
    def _calculate_stake_units(self, ev_pct, probability):
        """
        Calcula stake em unidades baseado em EV e probabilidade.
        
        Usa Kelly Criterion fracionário (1/4 Kelly).
        """
        if ev_pct <= 0:
            return 0.5  # Stake mínimo se EV negativo
        
        # Converter EV% em decimal
        edge = ev_pct / 100
        
        # Kelly: (edge × probability - (1 - probability)) / edge
        # Simplificado: edge × 4 (1/4 Kelly)
        kelly_fraction = edge * 4
        
        # Limitar entre 0.5 e 3.0 unidades
        stake = max(0.5, min(kelly_fraction, 3.0))
        
        return round(stake, 1)

