"""
Decision Engine - Motor de Decisão
Combina modelos estatísticos e identifica value bets
"""
import logging
import numpy as np

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Motor de decisão que:
    1. Combina previsões de múltiplos modelos
    2. Detecta value bets (odds do mercado > odds justas)
    3. Calcula confiança da previsão
    4. Avalia risco
    5. Gera recomendação final
    """
    
    def should_publish_prediction(self, consensus, confidence, threshold_prob=0.52, threshold_conf=0.75):
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
            threshold_prob (float): Limite mínimo de probabilidade (default 0.52)
            threshold_conf (float): Limite mínimo de confidence score (default 0.75)
        
        Returns:
            dict: {
                'should_publish': bool,
                'reason': str,
                'max_probability': float,
                'confidence_score': float,
                'filter_passed': str  # 'probability', 'confidence', 'both', 'none'
            }
        """
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
        logger.info(f"   Decisão: {publish_status} ({reason})")
        
        return {
            'should_publish': should_publish,
            'reason': reason,
            'max_probability': max_prob,
            'confidence_score': conf_score,
            'filter_passed': filter_status
        }
    
    def make_decision(self, model_predictions, features, market_odds, strategy='value'):
        """
        Decisão final baseada em modelos + mercado
        
        Args:
            model_predictions (dict): Previsões dos modelos (Poisson + Logística)
            features (dict): Features engineered
            market_odds (dict): Odds do mercado
            strategy (str): 'value' (EV máximo) ou 'multiple' (prob alta + EV positivo)
        
        Returns:
            dict: {
                'recommendation': {...},
                'confidence': {...},
                'risk': str,
                'value_bets': [...],
                'fair_odds': {...},
                'strategy': str
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
        logger.info(f"   Home: {market_odds.get('home')}, Draw: {market_odds.get('draw')}, Away: {market_odds.get('away')}")
        logger.info(f"   Over 2.5: {market_odds.get('over_2_5')}, Under 2.5: {market_odds.get('under_2_5')}")
        
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
        
        # 6. SELEÇÃO OBJETIVA das top 3 apostas (SEM IA)
        logger.info(f"\n6️⃣ Selecionando top 3 apostas (decisão objetiva, estratégia={strategy})...")
        top_bets = self.select_top_bets(model_predictions, market_odds, confidence, risk, strategy=strategy)
        
        for bet in top_bets:
            logger.info(f"   #{bet['rank']}: {bet['pick']} ({bet['market_display']})")
            logger.info(f"      Prob: {bet['probability']*100:.1f}% | Odd: {bet['market_odd']} | EV: {bet['ev_pct']:.1f}% | Stake: {bet['stake_units']}u")
            logger.info(f"      Score: {bet['score']:.3f} | Razão: {bet['reason']}")
        
        logger.info(f"\n{'='*80}\n")
        
        # 7. Filtro de publicação (confiança)
        consensus = model_predictions.get('consensus', {})
        publish_filter = self.should_publish_prediction(consensus, confidence)
        
        return {
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
            if prob > 0.01:  # Mínimo 1% para evitar odds absurdas
                odd = 1 / prob
                # Limitar odds a valores realistas (1.01 a 500.0)
                fair_odds[market] = round(max(1.01, min(500.0, odd)), 2)
            else:
                fair_odds[market] = 500.0  # Limite máximo
        
        # Over/Under (múltiplas linhas) e BTTS (do Poisson)
        poisson_markets = [
            'over_1_5', 'under_1_5', 
            'over_2_5', 'under_2_5', 
            'over_3_5', 'under_3_5', 
            'btts',
            # Team Total Goals
            'home_over_05', 'home_over_15', 'home_over_25',
            'away_over_05', 'away_over_15', 'away_over_25',
            # Winning Margins
            'home_win_by_1', 'home_win_by_2plus',
            'away_win_by_1', 'away_win_by_2plus',
            # Odd/Even
            'odd_goals', 'even_goals'
        ]
        
        for market in poisson_markets:
            prob = poisson_probs.get(market, 0)
            if prob > 0.01:  # Mínimo 1%
                odd = 1 / prob
                fair_odds[market] = round(max(1.01, min(500.0, odd)), 2)
            else:
                fair_odds[market] = 500.0
        
        return fair_odds
    
    def _find_value_bets(self, model_predictions, market_odds):
        """
        Identifica value bets onde: odd_mercado > odd_justa * 1.05
        
        Value bet = quando mercado oferece odd melhor que a "justa"
        Margem de segurança: 5%
        """
        fair_odds = self._calculate_fair_odds(model_predictions)
        value_bets = []
        
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
            
            market_odd = market_odds.get(market_key) or 0
            
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
        if strength_diff > 0.5 or form_diff > 0.5:
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
        
        # Nível textual
        if confidence_score >= 0.80:
            level = 'very_high'
            level_pt = 'Muito Alta'
        elif confidence_score >= 0.65:
            level = 'high'
            level_pt = 'Alta'
        elif confidence_score >= 0.50:
            level = 'medium'
            level_pt = 'Média'
        else:
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
        btts_odd = market_odds.get('btts_yes', 0)  # ✅ Usar chave correta
        
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
        
        # PRIORIDADE 3: Resultado mais provável
        # AJUSTE: Favorecer empate se probabilidade >= 25% OU diferença entre casa/fora < 5%
        prob_home = consensus.get('home_win', 0)
        prob_draw = consensus.get('draw', 0)
        prob_away = consensus.get('away_win', 0)
        
        # Regra 1: Empate com probabilidade >= 25% (ajustado para capturar mais empates)
        if prob_draw >= 0.25:
            market_name = 'draw'
            probability = prob_draw
        # Regra 2: Empate técnico (diferença < 5% entre casa e fora)
        elif abs(prob_home - prob_away) < 0.05 and prob_draw >= 0.20:
            market_name = 'draw'
            probability = prob_draw
        # Regra 3: Resultado mais provável
        else:
            max_market = max(consensus.items(), key=lambda x: x[1])
            market_name = max_market[0]
            probability = max_market[1]
        
        # Buscar odd do mercado
        market_mapping = {
            'home_win': 'home',
            'draw': 'draw',
            'away_win': 'away'
        }
        
        odd = market_odds.get(market_mapping.get(market_name, 'home'), 0)  # ✅ Usar chaves corretas
        
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
        
        # 1X2
        for market, prob_key, odds_key in [
            ('home_win', 'home_win', 'home'),
            ('draw', 'draw', 'draw'),
            ('away_win', 'away_win', 'away')
        ]:
            prob = consensus.get(prob_key, 0)
            market_odd = market_odds.get(odds_key, 0)  # ✅ Usar chave direta
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
        
        # Over/Under 2.5
        for market, prob_key in [('over_2_5', 'over_2_5'), ('under_2_5', 'under_2_5')]:
            prob = poisson_probs.get(prob_key, 0)
            market_odd = market_odds.get(prob_key, 0)  # ✅ Usar chave direta
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
        
        # BTTS
        btts_prob = poisson_probs.get('btts', 0)
        btts_odd = market_odds.get('btts_yes', 0)  # ✅ Usar chave correta
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
        
        # NOTE: Over/Under 1.5 e 3.5 comentados - API não retorna essas odds
        # # Over/Under 1.5
        # for market, prob_key in [('over_1_5', 'over_1_5'), ('under_1_5', 'under_1_5')]:
        #     prob = poisson_probs.get(prob_key, 0)
        #     market_odd = market_odds.get('over_1_5' if 'over' in market else 'under_1_5', 0)
        #     fair_odd = fair_odds.get(market, 0)
        #     
        #     if prob >= 0.30 and market_odd > 0 and fair_odd > 0:
        #         ev_pct = ((market_odd / fair_odd) - 1) * 100
        #         score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
        #         
        #         candidates.append({
        #             'market': market,
        #             'market_display': self._format_market_name(market),
        #             'pick': self._format_pick(market),
        #             'probability': prob,
        #             'market_odd': market_odd,
        #             'fair_odd': fair_odd,
        #             'ev_pct': ev_pct,
        #             'score': score,
        #             'category': 'totals'
        #         })
        
        # # Over/Under 3.5
        # for market, prob_key in [('over_3_5', 'over_3_5'), ('under_3_5', 'under_3_5')]:
        #     prob = poisson_probs.get(prob_key, 0)
        #     market_odd = market_odds.get('over_3_5' if 'over' in market else 'under_3_5', 0)
        #     fair_odd = fair_odds.get(market, 0)
        #     
        #     if prob >= 0.30 and market_odd > 0 and fair_odd > 0:
        #         ev_pct = ((market_odd / fair_odd) - 1) * 100
        #         score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
        #         
        #         candidates.append({
        #             'market': market,
        #             'market_display': self._format_market_name(market),
        #             'pick': self._format_pick(market),
        #             'probability': prob,
        #             'market_odd': market_odd,
        #             'fair_odd': fair_odd,
        #             'ev_pct': ev_pct,
        #             'score': score,
        #             'category': 'totals'
        #         })
        
        # NOTE: Team Total Goals, Clean Sheets - API não retorna essas odds
        # # Team Total Goals - Casa
        # for market, prob_key in [('home_over_0_5', 'team_home_over_0_5'), ('home_over_1_5', 'team_home_over_1_5')]:
        #     prob = poisson_probs.get(prob_key, 0)
        #     market_odd = market_odds.get(market, 0)
        #     fair_odd = fair_odds.get(market, 0)
        #     
        #     if prob >= 0.30 and market_odd > 0 and fair_odd > 0:
        #         ev_pct = ((market_odd / fair_odd) - 1) * 100
        #         score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
        #         
        #         candidates.append({
        #             'market': market,
        #             'market_display': self._format_market_name(market),
        #             'pick': self._format_pick(market),
        #             'probability': prob,
        #             'market_odd': market_odd,
        #             'fair_odd': fair_odd,
        #             'ev_pct': ev_pct,
        #             'score': score,
        #             'category': 'team_totals'
        #         })
        # 
        # # Team Total Goals - Fora
        # for market, prob_key in [('away_over_0_5', 'team_away_over_0_5'), ('away_over_1_5', 'team_away_over_1_5')]:
        #     prob = poisson_probs.get(prob_key, 0)
        #     market_odd = market_odds.get(f'odds_{market}', 0)
        #     fair_odd = fair_odds.get(market, 0)
        #     
        #     if prob >= 0.30 and market_odd > 0 and fair_odd > 0:
        #         ev_pct = ((market_odd / fair_odd) - 1) * 100
        #         score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
        #         
        #         candidates.append({
        #             'market': market,
        #             'market_display': self._format_market_name(market),
        #             'pick': self._format_pick(market),
        #             'probability': prob,
        #             'market_odd': market_odd,
        #             'fair_odd': fair_odd,
        #             'ev_pct': ev_pct,
        #             'score': score,
        #             'category': 'team_totals'
        #         })
        
        # NOTE: Clean Sheets comentado - API não retorna essas odds
        # for market, prob_key in [('home_clean_sheet', 'clean_sheet_home'), ('away_clean_sheet', 'clean_sheet_away')]:
        #     prob = poisson_probs.get(prob_key, 0)
        #     market_odd = market_odds.get(market, 0)
        #     fair_odd = fair_odds.get(market, 0)
        #     
        #     if prob >= 0.15 and market_odd > 0 and fair_odd > 0:
        #         ev_pct = ((market_odd / fair_odd) - 1) * 100
        #         score = self._calculate_bet_score(prob, ev_pct, confidence, risk, strategy)
        #         
        #         candidates.append({
        #             'market': market,
        #             'market_display': self._format_market_name(market),
        #             'pick': self._format_pick(market),
        #             'probability': prob,
        #             'market_odd': market_odd,
        #             'fair_odd': fair_odd,
        #             'ev_pct': ev_pct,
        #             'score': score,
        #             'category': 'specials'
        #         })
        
        # DEBUG: Ver candidatos
        only_1x2 = [c for c in candidates if c['category'] == '1x2']
        candidates_info = [(c['pick'], c['probability']*100, c['score']) for c in only_1x2]
        logger.info(f"   Candidatos 1X2: {candidates_info}")
        logger.info(f"   Total de candidatos: {len(candidates)}")
        
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
            # MODO VALUE: Ordenar por score (prioriza EV), SEM forçar 1X2
            logger.info("   ⚡ Aplicando lógica VALUE: puro ranking por score (prioriza EV)")
            
            # Filtro adicional para VALUE: rejeitar EV muito negativo (< -5%)
            value_candidates = [c for c in valid_candidates if c['ev_pct'] >= -5]
            
            if not value_candidates:
                logger.warning("   ⚠️ Nenhuma aposta com EV aceitável (todas < -5%)")
                return []
            
            # Ordenar por score (EV domina)
            others = sorted(value_candidates, key=lambda x: x['score'], reverse=True)
            used_categories = set()
            
            logger.info("   Top 5 candidatos VALUE por score:")
            for i, c in enumerate(others[:5], 1):
                logger.info(f"      {i}. {c['market_display']} - Prob: {c['probability']*100:.1f}%, EV: {c['ev_pct']:+.1f}%, Score: {c['score']:.3f}")
            
        else:
            # MODO MULTIPLE: Top 3 por score (prob² domina), SEM forçar 1X2
            logger.info("   📋 Aplicando lógica MULTIPLE: puro ranking por score (prob² + EV)")
            
            # Ordenar TODOS os candidatos válidos por score
            others = sorted(valid_candidates, key=lambda x: x['score'], reverse=True)
            used_categories = set()
            
            logger.info("   Top 5 candidatos por score:")
            for i, c in enumerate(others[:5], 1):
                logger.info(f"      {i}. {c['market_display']} - Prob: {c['probability']*100:.1f}%, EV: {c['ev_pct']:+.1f}%, Score: {c['score']:.3f}")
        
        # #2 e #3: Próximos melhores (preferindo categorias diferentes)
        used_markets = set()  # ✅ Rastrear mercados já usados
        for candidate in others:
            if len(selected) >= 3:
                break
            
            # ✅ Evitar duplicatas de mercado
            if candidate['market'] in used_markets:
                continue
            
            # Preferir categorias diferentes quando possível
            if candidate['category'] not in used_categories or len([c for c in others if c['category'] not in used_categories]) == 0:
                stake_units = self._calculate_stake_units(
                    candidate['ev_pct'],
                    candidate['probability'],
                    confidence,
                    risk
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
        - VALUE: prob × (1 + EV/100) × conf_factor × risk_factor
        - MULTIPLE: prob² × (1 + EV/200) × conf_factor × risk_factor
        
        Modo VALUE:
        - Prioriza probabilidade linear
        - EV tem peso normal (100%)
        - Aceita qualquer probabilidade
        
        Modo MULTIPLE:
        - Prioriza probabilidade QUADRÁTICA (65%→42%, 30%→9%)
        - EV tem metade do peso (50%)
        - Filtro rígido: prob ≥ 50% E EV ≥ +5%
        """
        conf_factor = confidence.get('score', 0.5)
        
        risk_factor = {
            'low': 1.2,
            'medium': 1.0,
            'high': 0.7
        }.get(risk, 1.0)
        
        if strategy == 'multiple':
            # MODO BILHETE: Prioriza MUITO mais probabilidade
            prob_weight = probability ** 2  # Quadrático (65%→42%, 30%→9%)
            ev_weight = max(0.5, 1 + (ev_pct / 200))  # EV com metade do peso
            
            # FILTRO FLEXÍVEL PARA BILHETES:
            # - Favoritos absolutos (≥70%): aceita até EV -15% (foco total em probabilidade)
            # - Favoritos normais (≥60%): aceita até EV -10%
            # - Prováveis (≥50%): aceita até EV -5%
            # Bilhetes = combinar apostas PROVÁVEIS, não buscar value
            
            if probability >= 0.70:
                # Favorito absoluto: aceita grande perda de value (ex: Inter 76% @ 1.16)
                if ev_pct < -15:
                    logger.debug(f"   ❌ MULTIPLE: Rejeitado - prob={probability:.2f} (≥70%) mas EV={ev_pct:.1f}% < -15%")
                    return 0
            elif probability >= 0.60:
                # Favorito: aceita perda moderada
                if ev_pct < -10:
                    logger.debug(f"   ❌ MULTIPLE: Rejeitado - prob={probability:.2f} (≥60%) mas EV={ev_pct:.1f}% < -10%")
                    return 0
            elif probability >= 0.50:
                # Provável: aceita pequena perda
                if ev_pct < -5:
                    logger.debug(f"   ❌ MULTIPLE: Rejeitado - prob={probability:.2f} (≥50%) mas EV={ev_pct:.1f}% < -5%")
                    return 0
            else:
                # Menos de 50%: rejeita para bilhete
                logger.debug(f"   ❌ MULTIPLE: Rejeitado - prob={probability:.2f} < 50%")
                return 0
            
            logger.debug(f"   ✅ MULTIPLE: prob={probability:.2f}² = {prob_weight:.3f}, ev={ev_pct:.1f}% → ev_weight={ev_weight:.3f}")
        else:
            # MODO VALUE: Código original
            prob_weight = probability
            ev_weight = max(0.5, 1 + (ev_pct / 100))
            
            logger.debug(f"   ✅ VALUE: prob={probability:.2f} (linear), ev={ev_pct:.1f}% → ev_weight={ev_weight:.3f}")
        
        score = prob_weight * ev_weight * conf_factor * risk_factor
        logger.debug(f"   📊 Score final: {prob_weight:.3f} × {ev_weight:.3f} × {conf_factor:.3f} × {risk_factor:.3f} = {score:.3f}")
        
        return round(score, 3)
    
    def _calculate_stake_units(self, ev_pct, probability, confidence, risk):
        """
        Calcula stake OBJETIVO em unidades (0.5 a 2.0).
        
        Base: 1.0 unidade
        Ajustes:
        - EV alto: +0.5u
        - Confiança alta: +0.3u
        - Risco alto: -0.5u
        
        Limites rígidos:
        - LOW risk: max 2.0u
        - MEDIUM risk: max 1.5u
        - HIGH risk: max 0.5u
        """
        base_stake = 1.0
        
        # Ajuste por EV
        if ev_pct >= 10:
            base_stake += 0.5
        elif ev_pct >= 5:
            base_stake += 0.3
        elif ev_pct < -5:
            base_stake -= 0.3
        
        # Ajuste por confiança
        conf_score = confidence.get('score', 0.5)
        if conf_score >= 0.8:
            base_stake += 0.3
        elif conf_score < 0.5:
            base_stake -= 0.3
        
        # Limites por risco (CRÍTICO)
        max_stakes = {
            'low': 2.0,
            'medium': 1.5,
            'high': 0.5
        }
        
        max_stake = max_stakes.get(risk, 1.0)
        final_stake = min(base_stake, max_stake)
        final_stake = max(0.5, final_stake)  # Mínimo 0.5u
        
        return round(final_stake, 1)
    
    def _generate_bet_reason(self, candidate, confidence, risk):
        """Gera razão OBJETIVA para a aposta."""
        prob = candidate['probability'] * 100
        ev = candidate['ev_pct']
        
        if ev > 10:
            return f"Excelente value: {prob:.1f}% prob + {ev:.1f}% EV"
        elif ev > 5:
            return f"Bom value: {prob:.1f}% prob + {ev:.1f}% EV"
        elif ev > 0:
            return f"Resultado provável: {prob:.1f}% prob + {ev:.1f}% EV"
        elif prob >= 50:
            return f"Alta probabilidade: {prob:.1f}% (sem value significativo)"
        else:
            return f"Resultado possível: {prob:.1f}% prob (EV: {ev:.1f}%)"
    
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
