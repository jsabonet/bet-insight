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
    
    def make_decision(self, model_predictions, features, market_odds):
        """
        Decisão final baseada em modelos + mercado
        
        Args:
            model_predictions (dict): Previsões dos modelos (Poisson + Logística)
            features (dict): Features engineered
            market_odds (dict): Odds do mercado
        
        Returns:
            dict: {
                'recommendation': {...},
                'confidence': {...},
                'risk': str,
                'value_bets': [...],
                'fair_odds': {...}
            }
        """
        logger.info(f"\n{'='*80}")
        logger.info("🎯 DECISION ENGINE - Gerando recomendação")
        logger.info(f"{'='*80}\n")
        
        logger.info("📊 Model Predictions recebidos:")
        logger.info(f"   Consensus: {model_predictions.get('consensus', {})}")
        logger.info(f"   Poisson xG: Home={model_predictions.get('poisson', {}).get('expected_goals', {}).get('home')}, Away={model_predictions.get('poisson', {}).get('expected_goals', {}).get('away')}")
        logger.info(f"   Weather Adjusted: {model_predictions.get('poisson', {}).get('weather_adjusted', False)}")
        
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
        logger.info(f"\n{'='*80}\n")
        
        return {
            'recommendation': recommendation,
            'confidence': confidence,
            'risk': risk,
            'value_bets': value_bets,
            'fair_odds': fair_odds,
            'model_probabilities': model_predictions
        }
    
    def _calculate_fair_odds(self, model_predictions):
        """
        Calcula odds justas (sem margem da casa)
        
        Odd justa = 1 / probabilidade
        """
        consensus = model_predictions.get('consensus', {})
        poisson_probs = model_predictions.get('poisson', {}).get('probabilities', {})
        
        fair_odds = {}
        
        # 1X2
        for market, prob in consensus.items():
            if prob > 0:
                fair_odds[market] = round(1 / prob, 2)
        
        # Over/Under e BTTS (do Poisson)
        for market in ['over_2_5', 'btts']:
            prob = poisson_probs.get(market, 0)
            if prob > 0:
                fair_odds[market] = round(1 / prob, 2)
        
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
            'home_win': 'odds_home',
            'draw': 'odds_draw',
            'away_win': 'odds_away',
            'over_2_5': 'odds_over_25',
            'btts': 'odds_btts_yes'
        }
        
        for model_market, fair_odd in fair_odds.items():
            market_key = market_mapping.get(model_market)
            if not market_key:
                continue
            
            market_odd = market_odds.get(market_key, 0)
            
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
            market.get('odds_home', 3.0),
            market.get('odds_draw', 3.0),
            market.get('odds_away', 3.0)
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
        
        Prioridade:
        1. Se há value bet com confiança alta → recomendar
        2. Senão, recomendar resultado mais provável
        """
        consensus = model_predictions.get('consensus', {})
        
        # Se há value bet com confiança suficiente
        if value_bets and confidence['score'] >= 0.65:
            best_value = value_bets[0]
            
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
        
        # Senão, recomendar resultado mais provável
        else:
            max_market = max(consensus.items(), key=lambda x: x[1])
            market_name = max_market[0]
            probability = max_market[1]
            
            # Buscar odd do mercado
            market_mapping = {
                'home_win': 'odds_home',
                'draw': 'odds_draw',
                'away_win': 'odds_away'
            }
            
            odd = market_odds.get(market_mapping.get(market_name, 'odds_home'), 0)
            
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
            'btts': 'Ambos Marcam',
            'btts_no': 'Ambos Não Marcam'
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
