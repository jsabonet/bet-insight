"""
Context Analyzer - Detecta padrões contextuais nas 109 features

Analisa features para identificar cenários específicos que favorecem
determinados mercados de apostas.

Author: AI Assistant
Date: 2026-02-07
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ContextAnalyzer:
    """
    Analisa contexto do jogo para identificar padrões que favorecem mercados específicos.
    
    Padrões detectados:
    1. low_motivation_both - Ambos desmotivados
    2. asymmetric_motivation - Favorito desmotivado vs underdog motivado
    3. defensive_fatigue_game - Defesas comprometidas por fadiga/lesões
    4. open_game - Jogo aberto com ambos ataques produtivos
    5. derby_context - Derby/rivalidade
    6. upset_potential - Potencial de zebra
    7. critical_injuries - Lesões críticas
    8. balanced_tight_game - Jogo equilibrado (força e motivação similares) - CAPTURA 60-70% DOS JOGOS
    """
    
    def __init__(self):
        """Inicializa o analisador de contexto."""
        self.patterns_detected = []
        self.market_scores = {}
    
    def analyze(self, features: Dict) -> Dict:
        """
        Analisa features e retorna padrões detectados + mercados favorecidos.
        
        Args:
            features (Dict): 109 features do FeatureEngineer
            
        Returns:
            Dict: {
                'patterns': [
                    {
                        'name': 'asymmetric_motivation',
                        'confidence': 0.85,
                        'favorable_markets': ['draw_ht', 'under_2.5'],
                        'reasoning': 'Favorito desmotivado vs underdog motivado'
                    }
                ],
                'top_markets': [
                    {'market': 'under_2.5', 'context_score': 0.95},
                    {'market': 'draw_ht', 'context_score': 0.85}
                ]
            }
        """
        logger.info("\n" + "="*80)
        logger.info("🔍 CONTEXT ANALYZER - Detectando padrões contextuais")
        logger.info("="*80)
        
        self.patterns_detected = []
        self.market_scores = {}
        
        # Detectar cada padrão
        patterns = [
            self._detect_low_motivation_both(features),
            self._detect_asymmetric_motivation(features),
            self._detect_defensive_fatigue_game(features),
            self._detect_open_game(features),
            self._detect_derby_context(features),
            self._detect_upset_potential(features),
            self._detect_critical_injuries(features),
            self._detect_balanced_tight_game(features)  # NOVO: para jogos equilibrados
        ]
        
        # Filtrar padrões detectados
        for pattern in patterns:
            if pattern and pattern.get('detected'):
                self.patterns_detected.append(pattern)
                logger.info(f"\n✅ Padrão detectado: {pattern['name']}")
                logger.info(f"   Confiança: {pattern['confidence']:.0%}")
                logger.info(f"   Mercados favorecidos: {', '.join(pattern['favorable_markets'])}")
                logger.info(f"   Raciocínio: {pattern['reasoning']}")
        
        # Consolidar scores dos mercados
        top_markets = self._consolidate_favorable_markets()
        
        logger.info("\n" + "-"*80)
        logger.info("📊 Top mercados por contexto:")
        for market_data in top_markets[:5]:
            logger.info(f"   {market_data['market']}: {market_data['context_score']:.0%}")
        logger.info("="*80 + "\n")
        
        return {
            'patterns': self.patterns_detected,
            'top_markets': top_markets
        }
    
    def _detect_low_motivation_both(self, features: Dict) -> Optional[Dict]:
        """
        Detecta quando AMBOS os times estão desmotivados.
        
        Cenário: Times sem objetivos claros (meio da tabela, já classificados, etc.)
        Favorece: Under totals, Draw, Draw HT
        """
        motivation = features.get('motivation', {})
        # Normalizar valores (escala 0-10 -> 0-1)
        motivation_home = motivation.get('home_motivation', 5) / 10.0
        motivation_away = motivation.get('away_motivation', 5) / 10.0
        
        # Threshold: ambos < 0.4
        if motivation_home < 0.4 and motivation_away < 0.4:
            avg_motivation = (motivation_home + motivation_away) / 2
            confidence = 1 - avg_motivation  # Quanto menor motivação, maior confiança
            
            return {
                'name': 'low_motivation_both',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['under_2.5', 'under_1.5', 'draw', 'draw_ht', '1X', 'X2', 'under_0.5', 'even_goals'],
                'market_weights': {
                    'under_2.5': 0.95,
                    'under_1.5': 0.75,
                    'under_0.5': 0.40,  # NOVO: 0-0 possível
                    'draw': 0.70,
                    'draw_ht': 0.80,
                    '1X': 0.65,  # NOVO: Double Chance
                    'X2': 0.65,  # NOVO: Double Chance
                    'even_goals': 0.60  # NOVO: Jogos mortos tendem a placares pares
                },
                'reasoning': f'Ambos desmotivados (casa:{motivation_home:.0%}, fora:{motivation_away:.0%}) - jogo morno esperado'
            }
        
        return None
    
    def _detect_asymmetric_motivation(self, features: Dict) -> Optional[Dict]:
        """
        Detecta favorito desmotivado vs underdog motivado.
        
        Cenário: Time forte sem motivação vs time fraco lutando
        Favorece: Draw HT, DNB underdog, Under totals, Draw
        """
        motivation = features.get('motivation', {})
        motivation_home = motivation.get('home_motivation', 5) / 10.0
        motivation_away = motivation.get('away_motivation', 5) / 10.0
        
        strength = features.get('strength', {})
        # Usar goals_per_game que já vem em escala correta
        strength_home = min(strength.get('home_goals_per_game', 1.2) / 2.5, 1.0)
        strength_away = min(strength.get('away_goals_per_game', 1.2) / 2.5, 1.0)
        strength_diff = abs(strength_home - strength_away)
        
        # Identificar favorito
        favorite_is_home = strength_home > strength_away
        favorite_motivation = motivation_home if favorite_is_home else motivation_away
        underdog_motivation = motivation_away if favorite_is_home else motivation_home
        
        # Threshold: diferença de força >= 0.15 E favorito desmotivado E underdog motivado
        if strength_diff >= 0.15 and favorite_motivation < 0.4 and underdog_motivation > 0.6:
            motivation_gap = underdog_motivation - favorite_motivation
            confidence = 0.70 + (motivation_gap * 0.3)  # Max 1.0
            
            underdog_market = 'dnb_away' if favorite_is_home else 'dnb_home'
            
            return {
                'name': 'asymmetric_motivation',
                'detected': True,
                'confidence': min(confidence, 1.0),
                'favorable_markets': ['draw_ht', underdog_market, 'under_2.5', 'draw', '1X' if favorite_is_home else 'X2', 'home_clean_sheet' if not favorite_is_home else 'away_clean_sheet'],
                'market_weights': {
                    'draw_ht': 0.90,
                    underdog_market: 0.80,
                    'under_2.5': 0.85,
                    'draw': 0.75,
                    '1X' if favorite_is_home else 'X2': 0.70,  # NOVO: Proteção no underdog
                    'home_clean_sheet' if not favorite_is_home else 'away_clean_sheet': 0.65  # NOVO: Underdog forte defensivamente
                },
                'reasoning': f'Favorito desmotivado ({favorite_motivation:.0%}) vs underdog motivado ({underdog_motivation:.0%}) - upset provável'
            }
        
        return None
    
    def _detect_defensive_fatigue_game(self, features: Dict) -> Optional[Dict]:
        """
        Detecta defesas comprometidas por fadiga ou lesões.
        
        Cenário: Lesões defensivas + jogos próximos
        Favorece: Under totals (paradoxo: defesas ruins = jogo travado)
        """
        injuries = features.get('injuries_suspensions', {})
        injuries_home_def = injuries.get('home_defensive_impact', 0)
        injuries_away_def = injuries.get('away_defensive_impact', 0)
        
        context = features.get('context', {})
        days_rest_home = context.get('days_since_last_match_home', 7)
        days_rest_away = context.get('days_since_last_match_away', 7)
        
        # Problemas defensivos?
        defensive_problems = (injuries_home_def > 0.5 or injuries_away_def > 0.5)
        
        # Alta fadiga?
        high_fatigue = (days_rest_home < 3 or days_rest_away < 3)
        
        if defensive_problems and high_fatigue:
            # Quanto maior o problema, maior a confiança
            problem_severity = max(injuries_home_def, injuries_away_def)
            fatigue_severity = 1 - (min(days_rest_home, days_rest_away) / 7)
            confidence = (problem_severity + fatigue_severity) / 2
            
            return {
                'name': 'defensive_fatigue_game',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['under_2.5', 'under_3.5', 'under_1.5'],
                'market_weights': {
                    'under_2.5': 0.85,
                    'under_3.5': 0.75,
                    'under_1.5': 0.70
                },
                'reasoning': f'Defesas comprometidas (lesões:{max(injuries_home_def, injuries_away_def):.0%}) + fadiga ({min(days_rest_home, days_rest_away)} dias) - jogo travado'
            }
        
        return None
    
    def _detect_open_game(self, features: Dict) -> Optional[Dict]:
        """
        Detecta jogo aberto com ambos ataques produtivos.
        
        Cenário: Times ofensivos, histórico de muitos gols
        Favorece: Over totals, BTTS
        """
        form = features.get('form', {})
        goals_home_avg = form.get('home_goals_scored_avg_l5', 0)
        goals_away_avg = form.get('away_goals_scored_avg_l5', 0)
        
        statistics = features.get('statistics', {})
        btts_percentage = statistics.get('btts_percentage_overall', 0)
        
        h2h = features.get('h2h', {})
        h2h_avg_goals = h2h.get('avg_goals_per_match', 0)
        
        # Threshold: ambos marcam bem (> 1.5 gols/jogo)
        if goals_home_avg > 1.5 and goals_away_avg > 1.5:
            # Confiança aumenta com BTTS histórico e H2H ofensivo
            base_confidence = 0.70
            btts_boost = btts_percentage * 0.15
            h2h_boost = min(h2h_avg_goals / 3.5, 0.15)  # Max 0.15
            
            confidence = min(base_confidence + btts_boost + h2h_boost, 1.0)
            
            return {
                'name': 'open_game',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['over_2.5', 'btts_yes', 'over_1.5', 'over_3.5'],
                'market_weights': {
                    'over_2.5': 0.90,
                    'btts_yes': 0.95,
                    'over_1.5': 0.85,
                    'over_3.5': 0.70
                },
                'reasoning': f'Ambos ataques produtivos (casa:{goals_home_avg:.1f}, fora:{goals_away_avg:.1f} gols/jogo) - jogo aberto esperado'
            }
        
        return None
    
    def _detect_derby_context(self, features: Dict) -> Optional[Dict]:
        """
        Detecta derby ou rivalidade.
        
        Cenário: Clássicos, derbies locais
        Favorece: BTTS, Over, Cards
        """
        context = features.get('context', {})
        is_derby = context.get('is_derby', False)
        
        h2h = features.get('h2h', {})
        h2h_btts = h2h.get('btts_percentage', 0)
        h2h_avg_goals = h2h.get('avg_goals_per_match', 0)
        
        # Derby explícito OU histórico muito ofensivo
        is_derby_like = is_derby or (h2h_btts > 0.70 and h2h_avg_goals > 2.5)
        
        if is_derby_like:
            # Confiança baseada em histórico
            confidence = 0.85 if is_derby else min(0.70 + (h2h_btts * 0.2), 0.90)
            
            return {
                'name': 'derby_context',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['btts_yes', 'over_2.5', 'over_1.5'],
                'market_weights': {
                    'btts_yes': 0.95,
                    'over_2.5': 0.90,
                    'over_1.5': 0.85
                },
                'reasoning': f'Derby/rivalidade (H2H: {h2h_btts:.0%} BTTS, {h2h_avg_goals:.1f} gols/jogo) - jogo emocional com gols'
            }
        
        return None
    
    def _detect_upset_potential(self, features: Dict) -> Optional[Dict]:
        """
        Detecta potencial de zebra (underdog em excelente forma).
        
        Cenário: Grande diferença de força MAS underdog performando bem
        Favorece: Draw, DNB underdog, Under totals
        """
        strength = features.get('strength', {})
        strength_home = strength.get('home', 0.5)
        strength_away = strength.get('away', 0.5)
        strength_diff = abs(strength_home - strength_away)
        
        form = features.get('form', {})
        form_home = form.get('home_form_l5', 0.5)
        form_away = form.get('away_form_l5', 0.5)
        
        # Identificar underdog
        favorite_is_home = strength_home > strength_away
        underdog_form = form_away if favorite_is_home else form_home
        
        # Threshold: grande diferença de força (>= 0.25) MAS underdog em forma (> 0.65)
        if strength_diff >= 0.25 and underdog_form > 0.65:
            confidence = 0.65 + (underdog_form - 0.65) * 0.5  # Max 0.825
            
            underdog_market = 'dnb_away' if favorite_is_home else 'dnb_home'
            
            return {
                'name': 'upset_potential',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['draw', underdog_market, 'under_2.5', 'draw_ht'],
                'market_weights': {
                    'draw': 0.85,
                    underdog_market: 0.80,
                    'under_2.5': 0.75,
                    'draw_ht': 0.80
                },
                'reasoning': f'Underdog em forma excelente ({underdog_form:.0%}) contra favorito - zebra possível'
            }
        
        return None
    
    def _detect_critical_injuries(self, features: Dict) -> Optional[Dict]:
        """
        Detecta lesões críticas que comprometem um time.
        
        Cenário: Time com muitas lesões importantes
        Favorece: Under totals, Draw, Opositor
        """
        injuries = features.get('injuries_suspensions', {})
        injuries_home_total = injuries.get('home_total_impact', 0)
        injuries_away_total = injuries.get('away_total_impact', 0)
        
        # Threshold: impacto > 0.7 em algum time
        max_impact = max(injuries_home_total, injuries_away_total)
        
        if max_impact > 0.7:
            affected_team = 'casa' if injuries_home_total > injuries_away_total else 'fora'
            healthy_team_market = 'dnb_away' if injuries_home_total > injuries_away_total else 'dnb_home'
            
            confidence = 0.70 + (max_impact - 0.7) * 0.5  # Max 0.85
            
            return {
                'name': 'critical_injuries',
                'detected': True,
                'confidence': min(confidence, 0.95),
                'favorable_markets': ['under_2.5', 'draw', healthy_team_market],
                'market_weights': {
                    'under_2.5': 0.85,
                    'draw': 0.80,
                    healthy_team_market: 0.75
                },
                'reasoning': f'Lesões críticas {affected_team} ({max_impact:.0%} impacto) - desempenho comprometido'
            }
        
        return None
    
    def _detect_balanced_tight_game(self, features: Dict) -> Optional[Dict]:
        """
        Detecta jogo equilibrado entre times similares.
        
        Cenário: Força similar, motivação similar, sem fatores extremos
        Este é o padrão DEFAULT quando outros não se aplicam - a maioria dos jogos
        
        NOVO: Retorna scores para TODOS os 9 mercados principais
        """
        strength = features.get('strength', {})
        # Normalizar gols/jogo para 0-1 (assumindo range 0-2.5)
        strength_home = min(strength.get('home_goals_per_game', 1.2) / 2.5, 1.0)
        strength_away = min(strength.get('away_goals_per_game', 1.2) / 2.5, 1.0)
        
        strength_diff = abs(strength_home - strength_away)
        
        motivation = features.get('motivation', {})
        # Normalizar motivation (escala 0-10 -> 0-1)
        motivation_home = motivation.get('home_motivation', 5) / 10.0
        motivation_away = motivation.get('away_motivation', 5) / 10.0
        motivation_diff = abs(motivation_home - motivation_away)
        
        context = features.get('context', {})
        home_advantage = context.get('home_advantage_strength', 0.55)
        
        # Threshold: Força similar (diff < 0.25) E motivação similar (diff < 0.35)
        if strength_diff < 0.25 and motivation_diff < 0.35:
            # Confiança baseada em quão equilibrado está
            balance_score = 1.0 - (strength_diff + motivation_diff) / 2
            confidence = 0.50 + (balance_score * 0.30)  # Range: 0.50-0.80
            
            # Calcular total esperado
            avg_strength = (strength_home + strength_away) / 2
            expected_goals = avg_strength * 2.5  # Se avg=0.6, então ~1.5 gols esperados
            
            # NOVO: Scores para TODOS os 9 mercados principais
            market_weights = {}
            
            # 1. Draw e Draw HT - sempre favorecidos em jogo equilibrado
            market_weights['draw'] = 0.85
            market_weights['draw_ht'] = 0.80
            
            # 2. Totals - baseado em expected goals
            if expected_goals < 2.0:  # Jogo muito fechado
                market_weights['under_2.5'] = 1.00
                market_weights['under_1.5'] = 0.70
                market_weights['over_2.5'] = 0.15
                market_weights['over_1.5'] = 0.35
            elif expected_goals < 2.3:  # Jogo equilibrado baixo
                market_weights['under_2.5'] = 0.85
                market_weights['under_1.5'] = 0.55
                market_weights['over_2.5'] = 0.25
                market_weights['over_1.5'] = 0.50
            elif expected_goals < 2.7:  # Jogo equilibrado médio
                market_weights['under_2.5'] = 0.50
                market_weights['under_1.5'] = 0.30
                market_weights['over_2.5'] = 0.60
                market_weights['over_1.5'] = 0.75
            else:  # Jogo equilibrado alto scoring
                market_weights['under_2.5'] = 0.25
                market_weights['under_1.5'] = 0.15
                market_weights['over_2.5'] = 0.85
                market_weights['over_1.5'] = 0.90
            
            # 3. BTTS - baseado em expected goals
            if expected_goals < 2.0:
                market_weights['btts_no'] = 0.82
                market_weights['btts_yes'] = 0.25
            elif expected_goals < 2.5:
                market_weights['btts_no'] = 0.60
                market_weights['btts_yes'] = 0.50
            else:
                market_weights['btts_no'] = 0.30
                market_weights['btts_yes'] = 0.80
            
            # 4. 1X2 - levemente favorecido mas equilibrado
            # Em jogo equilibrado, nenhum time é muito favorito
            if home_advantage > 0.58:  # Casa levemente favorecida
                market_weights['home_win'] = 0.55
                market_weights['away_win'] = 0.35
            elif home_advantage < 0.52:  # Visitante levemente favorecido
                market_weights['home_win'] = 0.35
                market_weights['away_win'] = 0.55
            else:  # Completamente equilibrado
                market_weights['home_win'] = 0.45
                market_weights['away_win'] = 0.45
            
            # Mercados favorecidos (top 4 para reasoning)
            favorable_markets = sorted(market_weights.keys(), key=lambda x: market_weights[x], reverse=True)[:4]
            
            reasoning_parts = []
            reasoning_parts.append(f'Jogo equilibrado (força: {strength_diff:.2f}, motivação: {motivation_diff:.2f})')
            reasoning_parts.append(f'Expected goals: {expected_goals:.1f}')
            if expected_goals < 2.3:
                reasoning_parts.append('baixo scoring favorece under e btts_no')
            else:
                reasoning_parts.append('médio scoring favorece over e btts_yes')
            
            return {
                'name': 'balanced_tight_game',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': favorable_markets,  # Top 4 para display
                'market_weights': market_weights,  # TODOS os 9+ mercados com scores
                'reasoning': ' | '.join(reasoning_parts)
            }
        
        return None
    
    def _consolidate_favorable_markets(self) -> List[Dict]:
        """
        Consolida todos os padrões e retorna ranking de mercados.
        
        Lógica:
        1. Para cada padrão, pegar mercados favorecidos e seus pesos
        2. Multiplicar peso × confiança do padrão
        3. Somar scores de mercados que aparecem em múltiplos padrões
        4. Ordenar por score final
        
        Returns:
            List[Dict]: [
                {'market': 'under_2.5', 'context_score': 0.95, 'supporting_patterns': ['low_motivation_both', 'defensive_fatigue']},
                ...
            ]
        """
        market_scores = {}
        market_patterns = {}
        
        for pattern in self.patterns_detected:
            pattern_confidence = pattern['confidence']
            market_weights = pattern.get('market_weights', {})
            
            for market, weight in market_weights.items():
                # Score = peso do padrão × confiança do padrão
                score = weight * pattern_confidence
                
                # Acumular scores
                if market not in market_scores:
                    market_scores[market] = 0
                    market_patterns[market] = []
                
                market_scores[market] += score
                market_patterns[market].append(pattern['name'])
        
        # Normalizar scores (max 1.0)
        if market_scores:
            max_score = max(market_scores.values())
            if max_score > 0:
                for market in market_scores:
                    market_scores[market] = min(market_scores[market] / max_score, 1.0)
        
        # Criar lista ordenada
        ranked_markets = [
            {
                'market': market,
                'context_score': score,
                'supporting_patterns': market_patterns[market]
            }
            for market, score in market_scores.items()
        ]
        
        # Ordenar por score descendente
        ranked_markets.sort(key=lambda x: x['context_score'], reverse=True)
        
        return ranked_markets
