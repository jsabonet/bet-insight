"""
Context Analyzer - Detecta padrões contextuais nas 109 features

Analisa features para identificar cenários específicos que favorecem
determinados mercados de apostas.

Author: AI Assistant
Date: 2026-02-07
"""

import logging
from typing import Dict, List, Optional
from apps.analysis.config import ContextConfidence, ContextMarketWeights

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
            self._detect_knockout_upset(features),           # NOVO: Copa + favorito vulnerável
            self._detect_motivated_favorite_vs_defensive_wall(features),  # NOVO: Favorito vs defesa sólida
            self._detect_must_win_high_importance(features),  # NOVO: Must-win / six-pointer
            self._detect_congested_schedule_both(features),    # NOVO: Congestionamento severo
            self._detect_bogey_team_effect(features),          # NOVO: Efeito H2H "bogey team"
            self._detect_bookmaker_margin_high(features),      # NOVO: Margem alta do bookmaker (cautela)
            self._detect_post_heavy_defeat_volatility(features), # NOVO: Volatilidade pós-derrota pesada
            self._detect_set_pieces_advantage(features),       # NOVO: Vantagem em bolas paradas
            self._detect_asymmetric_motivation(features),
            self._detect_asymmetric_fatigue(features),       # NOVO: Fadiga assimétrica
            self._detect_defensive_fatigue_game(features),
            self._detect_open_game(features),
            self._detect_derby_context(features),
            self._detect_upset_potential(features),
            self._detect_critical_injuries(features),
            self._detect_balanced_tight_game(features)      # Último: catch-all
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

    def _detect_must_win_high_importance(self, features: Dict) -> Optional[Dict]:
        """
        Detecta jogo de altíssima importância (must‑win / six‑pointer).

        Sinais:
        - match_importance.match_importance >= 8.5
        - season_progress >= 0.70 (fase final)

        Favorece: Jogo cauteloso no início e menor risco
        Mercados: under_2.5, draw_ht, 1X/X2, under_3.5
        """
        imp = features.get('match_importance', {})
        match_imp = float(imp.get('match_importance', 6.0))
        season_prog = float(imp.get('season_progress', 0.5))

        if match_imp >= 8.5 and season_prog >= 0.70:
            # Confiança cresce com importância e progresso
            confidence = min(0.60 + (match_imp - 8.5) * 0.05 + (season_prog - 0.70) * 0.4, 0.90)

            market_weights = {
                'under_2.5': 0.85,
                'under_3.5': 0.75,
                'draw_ht': 0.80,
                '1x': 0.70,
                'x2': 0.70
            }

            return {
                'name': 'must_win_high_importance',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['under_2.5', 'draw_ht', '1x', 'x2', 'under_3.5'],
                'market_weights': market_weights,
                'reasoning': f"Jogo de altíssima importância (score={match_imp:.1f}/10, season {season_prog*100:.0f}%) — tendência a cautela, menos riscos"
            }

        return None

    def _detect_congested_schedule_both(self, features: Dict) -> Optional[Dict]:
        """
        Detecta congestionamento severo de agenda para ambos.

        Sinais:
        - home_rest_days <= 3 e away_rest_days <= 3
        - |rest_advantage| <= 1 (ambos igualmente cansados)

        Mercados: under_2.5, under_3.5, draw_ht, btts_no
        """
        ctx = features.get('context', {})
        home_rest = int(ctx.get('home_rest_days', 7))
        away_rest = int(ctx.get('away_rest_days', 7))
        rest_adv = int(ctx.get('rest_advantage', 0))

        if home_rest <= 3 and away_rest <= 3 and abs(rest_adv) <= 1:
            fatigue_level = max(0, 3 - min(home_rest, away_rest)) / 3.0  # 0-1
            confidence = min(0.65 + fatigue_level * 0.20, 0.85)

            market_weights = {
                'under_2.5': 0.80,
                'under_3.5': 0.75,
                'draw_ht': 0.75,
                'btts_no': 0.65
            }

            return {
                'name': 'congested_schedule_both',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['under_2.5', 'under_3.5', 'draw_ht', 'btts_no'],
                'market_weights': market_weights,
                'reasoning': f"Agenda congestionada para ambos (resto casa {home_rest}d, fora {away_rest}d) — ritmo baixo, menos gols"
            }

        return None

    def _detect_bogey_team_effect(self, features: Dict) -> Optional[Dict]:
        """
        Detecta efeito "bogey team" no H2H (um lado domina historicamente).

        Sinais:
        - h2h_games >= 5
        - h2h_home_win_rate >= 0.70 (casa domina) OU <= 0.30 (fora domina)

        Mercados: DNB pró dominante, dupla chance pró dominante, draw
        """
        h2h = features.get('h2h', {})
        games = int(h2h.get('h2h_games', 0))
        home_win_rate = float(h2h.get('h2h_home_win_rate', 0))

        if games >= 5 and (home_win_rate >= 0.70 or home_win_rate <= 0.30):
            home_dominates = home_win_rate >= 0.70
            dominant_dnb = 'dnb_home' if home_dominates else 'dnb_away'
            dominant_dc = '1x' if home_dominates else 'x2'

            # Confiança proporcional ao desbalanceamento
            imbalance = abs(home_win_rate - 0.50)
            confidence = min(0.60 + imbalance * 0.6, 0.90)

            market_weights = {
                dominant_dnb: 0.85,
                dominant_dc: 0.80,
                'draw': 0.65
            }

            return {
                'name': 'bogey_team_effect',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': [dominant_dnb, dominant_dc, 'draw'],
                'market_weights': market_weights,
                'reasoning': f"H2H desbalanceado ({games} jogos, taxa casa {home_win_rate*100:.0f}%) — favorecer lado dominante"
            }

        return None

    def _detect_bookmaker_margin_high(self, features: Dict) -> Optional[Dict]:
        """
        Detecta margem alta do bookmaker — recomenda mercados mais seguros.

        Sinais:
        - market.bookmaker_margin >= 0.07

        Mercados: double chance (1X/X2), under 2.5 (menos variância)
        """
        market = features.get('market', {})
        margin = float(market.get('bookmaker_margin', 0.0))

        if margin >= 0.07:
            confidence = min(0.55 + (margin - 0.07) * 2.0, 0.80)
            market_weights = {
                '1x': 0.75,
                'x2': 0.75,
                'under_2.5': 0.70
            }

            return {
                'name': 'bookmaker_margin_high',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['1x', 'x2', 'under_2.5'],
                'market_weights': market_weights,
                'reasoning': f"Margem bookmaker alta ({margin*100:.1f}%) — preferir mercados de menor risco"
            }

        return None

    def _detect_post_heavy_defeat_volatility(self, features: Dict) -> Optional[Dict]:
        """
        Detecta volatilidade pós-derrota pesada (queda de momentum).

        Sinais:
        - home_momentum <= -1.5 ou away_momentum <= -1.5
        - diferença de momentum >= 1.0

        Mercados: btts_yes (jogo caótico), draw, margens ±1
        """
        form = features.get('form', {})
        hm = float(form.get('home_momentum', 0))
        am = float(form.get('away_momentum', 0))
        diff = abs(hm - am)

        if (hm <= -1.5 or am <= -1.5) and diff >= 1.0:
            confidence = min(0.60 + (diff - 1.0) * 0.15, 0.85)
            market_weights = {
                'btts_yes': 0.80,
                'draw': 0.70,
                'home_by_1': 0.60,
                'away_by_1': 0.60
            }
            return {
                'name': 'post_heavy_defeat_volatility',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['btts_yes', 'draw', 'home_by_1', 'away_by_1'],
                'market_weights': market_weights,
                'reasoning': f"Queda de momentum (casa {hm:+.2f}, fora {am:+.2f}) — maior imprevisibilidade e gols de ambos"
            }

        return None

    def _detect_set_pieces_advantage(self, features: Dict) -> Optional[Dict]:
        """
        Detecta vantagem em bolas paradas (corners/clean sheets) sugerindo mercados de gols do time.

        Sinais:
        - Diferença de corners_per_game >= 2.0
        - clean_sheet_rate alto no time dominante sugere vitória por margem pequena

        Mercados: home_over_05/away_over_05, home_over_15/away_over_15, home_by_1/away_by_1
        """
        stats = features.get('statistics', {})
        hc = float(stats.get('home_corners_per_game', 0))
        ac = float(stats.get('away_corners_per_game', 0))
        hcs = float(stats.get('home_clean_sheet_rate', 0))
        acs = float(stats.get('away_clean_sheet_rate', 0))

        diff = hc - ac
        if abs(diff) >= 2.0:
            home_dominates = diff > 0
            tg_over_05 = 'home_over_05' if home_dominates else 'away_over_05'
            tg_over_15 = 'home_over_15' if home_dominates else 'away_over_15'
            win_by_1 = 'home_by_1' if home_dominates else 'away_by_1'

            # Confiança aumenta com diferença e clean sheets
            cs_boost = (hcs if home_dominates else acs) * 0.2
            confidence = min(0.60 + (abs(diff) - 2.0) * 0.10 + cs_boost, 0.85)

            market_weights = {
                tg_over_05: 0.80,
                tg_over_15: 0.70,
                win_by_1: 0.65
            }

            return {
                'name': 'set_pieces_advantage',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': [tg_over_05, tg_over_15, win_by_1],
                'market_weights': market_weights,
                'reasoning': f"Vantagem em bolas paradas (corners diff {diff:+.1f}/jogo, clean sheets {'casa' if home_dominates else 'fora'} { (hcs if home_dominates else acs)*100:.0f}% ) — tendência a gol do lado dominante"
            }

        return None
    
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
                'favorable_markets': ['under_2.5', 'under_1.5', 'draw', 'draw_ht', '1x', 'x2', 'under_0.5', 'even_goals'],
                'market_weights': ContextMarketWeights.LOW_MOTIVATION_BOTH,
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
        
        # Threshold REDUZIDO: 0.15 força OU (0.10 força + copa)
        # Motivação: gap >= 0.20 (era implícito 0.20, agora explícito)
        competition = features.get('competition', {})
        is_cup = competition.get('is_cup_competition', False)
        
        # Threshold dinâmico
        strength_threshold = 0.10 if is_cup else 0.15
        motivation_gap = underdog_motivation - favorite_motivation
        
        # Detectar se há assimetria relevante
        has_strength_diff = strength_diff >= strength_threshold
        has_motivation_gap = motivation_gap >= 0.20  # Explícito: 20pp de diferença
        
        # Threshold dinâmico para motivação do favorito (mais permissivo em copas)
        favorite_motivation_threshold = 0.75 if is_cup else 0.50
        
        if has_strength_diff and favorite_motivation < favorite_motivation_threshold and has_motivation_gap:
            # Boost de confiança se for copa (contexto emocional amplifica)
            confidence = ContextConfidence.ASYMMETRIC_MOTIVATION_BASE + (motivation_gap * ContextConfidence.ASYMMETRIC_MOTIVATION_BOOST)
            if is_cup:
                confidence = min(confidence * 1.15, 1.0)  # +15% em copas
            
            underdog_market = 'dnb_away' if favorite_is_home else 'dnb_home'
            double_chance_market = '1x' if favorite_is_home else 'x2'
            clean_sheet_market = 'home_clean_sheet' if not favorite_is_home else 'away_clean_sheet'
            
            # Usar pesos base e adicionar dinâmicos
            market_weights = ContextMarketWeights.ASYMMETRIC_MOTIVATION.copy()
            market_weights[underdog_market] = ContextMarketWeights.DNB_WEIGHT
            market_weights[double_chance_market] = ContextMarketWeights.DOUBLE_CHANCE_WEIGHT
            market_weights[clean_sheet_market] = ContextMarketWeights.CLEAN_SHEET_WEIGHT
            
            return {
                'name': 'asymmetric_motivation',
                'detected': True,
                'confidence': min(confidence, 1.0),
                'favorable_markets': ['draw_ht', underdog_market, 'under_2.5', 'draw', double_chance_market, clean_sheet_market],
                'market_weights': market_weights,
                'reasoning': f'Favorito desmotivado ({favorite_motivation:.0%}) vs underdog motivado ({underdog_motivation:.0%}){" [COPA]" if is_cup else ""} - upset provável'
            }
        
        return None
    
    def _detect_knockout_upset(self, features: Dict) -> Optional[Dict]:
        """NOVO: Detecta potencial zebra em jogos eliminatórios.
        
        Cenário: Copa/Knockout + favorito técnico vulnerável (cansado, desmotivado, lesões)
        Favorece: Double chance underdog, Draw, Under (jogo cauteloso), BTTS
        """
        competition = features.get('competition', {})
        is_cup = competition.get('is_cup_competition', False)
        is_knockout = competition.get('is_knockout_stage', False)
        
        if not (is_cup and is_knockout):
            return None
        
        # Identificar favorito e vulnerabilidades
        strength = features.get('strength', {})
        strength_home = min(strength.get('home_goals_per_game', 1.2) / 2.5, 1.0)
        strength_away = min(strength.get('away_goals_per_game', 1.2) / 2.5, 1.0)
        strength_diff = abs(strength_home - strength_away)
        
        # Só ativa se houver favorito claro (diff >= 0.15)
        if strength_diff < 0.15:
            return None
        
        favorite_is_home = strength_home > strength_away
        
        # Vulnerabilidades do favorito
        context = features.get('context', {})
        motivation = features.get('motivation', {})
        injuries = features.get('injuries_suspensions', {})
        
        rest_home = context.get('home_rest_days', 7)
        rest_away = context.get('away_rest_days', 7)
        motivation_home = motivation.get('home_motivation', 5) / 10.0
        motivation_away = motivation.get('away_motivation', 5) / 10.0
        injury_home = injuries.get('home_injury_impact', 0)
        injury_away = injuries.get('away_injury_impact', 0)
        
        # Calcular vulnerabilidade do favorito (0-1)
        if favorite_is_home:
            favorite_rest = rest_home
            favorite_motivation = motivation_home
            favorite_injuries = injury_home
        else:
            favorite_rest = rest_away
            favorite_motivation = motivation_away
            favorite_injuries = injury_away
        
        vulnerability_score = 0.0
        vulnerability_reasons = []
        
        # Fadiga (< 4 dias)
        if favorite_rest < 4:
            fatigue_impact = (4 - favorite_rest) / 4  # 0-1
            vulnerability_score += fatigue_impact * 0.35
            vulnerability_reasons.append(f'{favorite_rest}d descanso')
        
        # Motivação baixa para copa (< 0.75)
        if favorite_motivation < 0.75:
            motivation_impact = (0.75 - favorite_motivation) / 0.75
            vulnerability_score += motivation_impact * 0.30
            vulnerability_reasons.append(f'motivação {favorite_motivation:.0%}')
        
        # Lesões (> 0.2 já conta)
        if favorite_injuries > 0.2:
            vulnerability_score += favorite_injuries * 0.35
            vulnerability_reasons.append(f'lesões {favorite_injuries:.0%}')
        
        # Threshold REDUZIDO: vulnerabilidade >= 0.20 (era 0.35, depois 0.25)
        # Em copas, vulnerabilidade moderada já é suficiente
        if vulnerability_score >= 0.20:
            confidence = min(0.65 + (vulnerability_score * 0.30), 0.95)
            
            underdog_market = 'X2' if favorite_is_home else '1X'
            
            return {
                'name': 'knockout_upset',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['draw', underdog_market, 'under_2.5', 'btts_yes', 'draw_ht'],
                'market_weights': {
                    'draw': 0.90,
                    underdog_market: 0.85,
                    'under_2.5': 0.75,  # Jogos eliminatórios tendem a ser cautelosos
                    'btts_yes': 0.70,   # Ambos tentam marcar
                    'draw_ht': 0.80,    # Primeiro tempo cauteloso
                    'under_3.5': 0.70
                },
                'reasoning': f'Copa eliminatória + favorito vulnerável ({" + ".join(vulnerability_reasons)}) - upset provável'
            }
        
        return None
    
    def _detect_motivated_favorite_vs_defensive_wall(self, features: Dict) -> Optional[Dict]:
        """NOVO: Detecta favorito motivado enfrentando defesa sólida em casa.
        
        Cenário: 
        - Favorito altamente motivado (líder/título) mas vulnerável defensivamente
        - vs Underdog com defesa de ferro jogando em casa
        - Força diferencial moderada (não é massacre)
        
        Características:
        - Favorito motivation >= 9.0 e odds < 2.5
        - Underdog defense_strength < 1.3 (muito forte)
        - Favorito defense_strength > 1.8 (vulnerável)
        - Strength diferencial < 0.65 (jogo competitivo)
        
        Mercados favorecidos:
        - BTTS Yes: Ambos podem marcar (favorito ataca, underdog marca em casa)
        - Under 3.5: Defesa sólida fecha jogo
        - Draw ou X2: Underdog segura favorito
        - Under 2.5: Jogo travado (moderado)
        
        Exemplo: Brentford (1.07 def) vs Arsenal (2.14 def, líder 10/10 motiv, odd 1.66)
        """
        # DEBUG: Verificar se método é chamado
        logger.info("🔍 DEBUG: Checking motivated_favorite_vs_defensive_wall pattern")
        
        strength = features.get('strength', {})
        motivation = features.get('motivation', {})
        market = features.get('market', {})
        
        # Extrair dados
        home_defense = strength.get('home_defense_strength', 1.5)
        away_defense = strength.get('away_defense_strength', 1.5)
        home_motivation = float(motivation.get('home_motivation', 5.0))
        away_motivation = float(motivation.get('away_motivation', 5.0))
        strength_diff = abs(strength.get('strength_differential', 0.0))
        
        # Odds para identificar favorito
        odds_home = market.get('odds_home', 3.0)
        odds_away = market.get('odds_away', 3.0)
        
        # Identificar favorito (odd menor)
        favorite_is_home = odds_home < odds_away
        favorite_odds = odds_home if favorite_is_home else odds_away
        favorite_motivation = home_motivation if favorite_is_home else away_motivation
        favorite_defense = home_defense if favorite_is_home else away_defense
        underdog_defense = away_defense if favorite_is_home else home_defense
        
        # CONDIÇÕES:
        # 1. Favorito motivado e não é odd muito alta
        if favorite_motivation < 9.0 or favorite_odds >= 2.5:
            logger.debug(f"defensive_wall SKIP: motivation={favorite_motivation:.1f} or odds={favorite_odds:.2f}")
            return None
        
        # 2. Underdog defesa sólida (< 1.3 gols sofridos/jogo)
        if underdog_defense >= 1.3:
            logger.debug(f"defensive_wall SKIP: underdog_defense={underdog_defense:.2f} >= 1.3")
            return None
        
        # 3. Favorito vulnerável defensively (> 1.8)
        if favorite_defense <= 1.8:
            logger.info(f"❌ defensive_wall SKIP: favorite_defense={favorite_defense:.2f} <= 1.8")
            return None
        
        # 4. Força diferencial moderada (< 0.65)
        if strength_diff >= 0.65:
            logger.debug(f"defensive_wall SKIP: strength_diff={strength_diff:.2f} >= 0.65")
            return None
        
        # 5. Underdog deve estar em casa (defesa ainda mais forte)
        if favorite_is_home:
            logger.debug(f"defensive_wall SKIP: favorite_is_home=True")
            return None
        
        logger.info(f"✅ defensive_wall DETECTED! All conditions passed")
        
        # Calcular confiança baseado em quão extremos são os valores
        confidence = 0.65
        
        # Boost se defesa underdog muito forte
        if underdog_defense < 1.1:
            confidence += 0.10
        
        # Boost se favorito muito vulnerável
        if favorite_defense > 2.0:
            confidence += 0.08
        
        # Boost se motivação muito alta
        if favorite_motivation >= 9.5:
            confidence += 0.07
        
        confidence = min(confidence, 0.90)
        
        # Contexto para raciocínio
        fav_team = "casa" if favorite_is_home else "fora"
        und_team = "fora" if favorite_is_home else "casa"
        
        return {
            'name': 'motivated_favorite_vs_defensive_wall',
            'detected': True,
            'confidence': confidence,
            'favorable_markets': ['btts_yes', 'under_3.5', 'draw', 'x2' if not favorite_is_home else '1x', 'under_2.5'],
            'market_weights': {
                'btts_yes': 0.90,      # Muito provável ambos marcarem
                'under_3.5': 0.85,     # Defesa sólida limita gols
                'draw': 0.75,          # Underdog segura favorito
                'x2': 0.80 if not favorite_is_home else 0.0,
                '1x': 0.80 if favorite_is_home else 0.0,
                'under_2.5': 0.65,     # Moderado - pode ter 2 ou 3 gols
                'draw_ht': 0.70,       # Primeiro tempo cauteloso
                'over_2.5': 0.35,      # Reduzir peso de Over
                'over_3.5': 0.20       # Muito improvável
            },
            'reasoning': f'Favorito {fav_team} motivado ({favorite_motivation:.1f}/10, odd {favorite_odds:.2f}) mas vulnerável (def {favorite_defense:.2f}) vs defesa sólida {und_team} ({underdog_defense:.2f}) - BTTS provável, poucos gols'
        }
    
    def _detect_asymmetric_fatigue(self, features: Dict) -> Optional[Dict]:
        """NOVO: Detecta fadiga assimétrica (um cansado, outro descansado).
        
        Cenário: Grande diferença de descanso (>4 dias)
        Favorece: Time descansado, Over se ambos atacam, Under se defensivo
        """
        context = features.get('context', {})
        rest_home = context.get('home_rest_days', 7)
        rest_away = context.get('away_rest_days', 7)
        rest_diff = abs(rest_home - rest_away)
        
        # Threshold: diferença >= 4 dias
        if rest_diff < 4:
            return None
        
        # Identificar quem descansou mais
        rested_is_home = rest_home > rest_away
        rested_days = rest_home if rested_is_home else rest_away
        fatigued_days = rest_away if rested_is_home else rest_home
        
        # Confiança aumenta com diferença
        confidence = min(0.60 + (rest_diff - 4) * 0.05, 0.85)
        
        # Mercados favorecidos dependem de quem está descansado
        rested_market = 'home_win' if rested_is_home else 'away_win'
        rested_dc = '1X' if rested_is_home else 'X2'
        fatigued_under_goals = 'away_under_0.5' if rested_is_home else 'home_under_0.5'
        
        return {
            'name': 'asymmetric_fatigue',
            'detected': True,
            'confidence': confidence,
            'favorable_markets': [rested_market, rested_dc, 'btts_no', fatigued_under_goals],
            'market_weights': {
                rested_market: 0.80,
                rested_dc: 0.85,
                'btts_no': 0.75,  # Time cansado pode não marcar
                fatigued_under_goals: 0.70,
                'under_2.5': 0.65  # Jogo pode ser travado
            },
            'reasoning': f'Fadiga assimétrica: {"casa" if rested_is_home else "fora"} descansou {rested_days}d vs {fatigued_days}d - vantagem time descansado'
        }
    
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
                'market_weights': ContextMarketWeights.DEFENSIVE_FATIGUE_GAME,
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
            base_confidence = ContextConfidence.OPEN_GAME_BASE
            btts_boost = btts_percentage * ContextConfidence.OPEN_GAME_BTTS_BOOST
            h2h_boost = min(h2h_avg_goals / 3.5, ContextConfidence.OPEN_GAME_H2H_BOOST_MAX)
            
            confidence = min(base_confidence + btts_boost + h2h_boost, 1.0)
            
            return {
                'name': 'open_game',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['over_2.5', 'btts_yes', 'over_1.5', 'over_3.5'],
                'market_weights': ContextMarketWeights.OPEN_GAME,
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
            confidence = ContextConfidence.DERBY_BOOST_IF_DERBY if is_derby else min(
                ContextConfidence.DERBY_BASE + (h2h_btts * 0.2), 
                ContextConfidence.DERBY_BOOST_MAX
            )
            
            return {
                'name': 'derby_context',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['btts_yes', 'over_2.5', 'over_1.5'],
                'market_weights': ContextMarketWeights.DERBY_CONTEXT,
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
            confidence = ContextConfidence.UPSET_POTENTIAL_BASE + (underdog_form - 0.65) * ContextConfidence.UPSET_POTENTIAL_MULTIPLIER
            confidence = min(confidence, ContextConfidence.UPSET_POTENTIAL_MAX)
            
            underdog_market = 'dnb_away' if favorite_is_home else 'dnb_home'
            
            # Usar pesos base e adicionar dinâmico
            market_weights = ContextMarketWeights.UPSET_POTENTIAL.copy()
            market_weights[underdog_market] = ContextMarketWeights.DNB_WEIGHT
            
            return {
                'name': 'upset_potential',
                'detected': True,
                'confidence': confidence,
                'favorable_markets': ['draw', underdog_market, 'under_2.5', 'draw_ht'],
                'market_weights': market_weights,
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
            
            confidence = ContextConfidence.CRITICAL_INJURIES_BASE + (max_impact - 0.7) * ContextConfidence.CRITICAL_INJURIES_MULTIPLIER
            confidence = min(confidence, ContextConfidence.CRITICAL_INJURIES_MAX)
            
            # Usar pesos base e adicionar dinâmico
            market_weights = ContextMarketWeights.CRITICAL_INJURIES.copy()
            market_weights[healthy_team_market] = ContextMarketWeights.DNB_WEIGHT
            
            return {
                'name': 'critical_injuries',
                'detected': True,
                'confidence': min(confidence, 0.95),
                'favorable_markets': ['under_2.5', 'draw', healthy_team_market],
                'market_weights': market_weights,
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
        
        # Threshold MAIS RESTRITIVO: em copas, NÃO classificar facilmente como equilibrado
        # Força < 0.20 (era 0.25) E motivação < 0.25 (era 0.35)
        # Em copas: thresholds ainda menores (copas têm mais emoção/assimetria)
        competition = features.get('competition', {})
        is_cup = competition.get('is_cup_competition', False)
        
        strength_threshold = 0.15 if is_cup else 0.20
        motivation_threshold = 0.20 if is_cup else 0.25
        
        # Threshold: Força similar E motivação similar
        if strength_diff < strength_threshold and motivation_diff < motivation_threshold:
            # Confiança baseada em quão equilibrado está
            balance_score = 1.0 - (strength_diff + motivation_diff) / 2
            confidence = 0.50 + (balance_score * 0.30)  # Range: 0.50-0.80
            
            # Calcular total esperado
            avg_strength = (strength_home + strength_away) / 2
            expected_goals = avg_strength * 2.5  # Se avg=0.6, então ~1.5 gols esperados
            
            # Iniciar com pesos base
            market_weights = ContextMarketWeights.BALANCED_BASE.copy()
            
            # 2. Totals e BTTS - baseado em expected goals
            if expected_goals < 2.0:  # Jogo muito fechado
                market_weights.update(ContextMarketWeights.BALANCED_VERY_LOW)
            elif expected_goals < 2.3:  # Jogo equilibrado baixo
                market_weights.update(ContextMarketWeights.BALANCED_LOW)
            elif expected_goals < 2.7:  # Jogo equilibrado médio
                market_weights.update(ContextMarketWeights.BALANCED_MEDIUM)
            else:  # Jogo equilibrado alto scoring
                market_weights.update(ContextMarketWeights.BALANCED_HIGH)
            
            # 4. 1X2 - levemente favorecido mas equilibrado
            if home_advantage > 0.58:  # Casa levemente favorecida
                market_weights.update(ContextMarketWeights.BALANCED_HOME_FAVORED)
            elif home_advantage < 0.52:  # Visitante levemente favorecido
                market_weights.update(ContextMarketWeights.BALANCED_AWAY_FAVORED)
            else:  # Completamente equilibrado
                market_weights.update(ContextMarketWeights.BALANCED_NEUTRAL)
            
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
        4. NOVO: Incluir TODOS os mercados canônicos (context_score = 0 para não relevantes)
        5. Ordenar por score final
        
        Returns:
            List[Dict]: [
                {'market': 'under_2.5', 'context_score': 0.95, 'supporting_patterns': ['low_motivation_both', 'defensive_fatigue']},
                {'market': 'home_win', 'context_score': 0.0, 'supporting_patterns': []},  # Sem contexto
                ...
            ]
        """
        from apps.analysis.config.market_standards import CANONICAL_MARKETS
        
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
        
        # 🆕 INCLUIR TODOS OS MERCADOS CANÔNICOS (com context_score = 0 se não têm weights)
        all_canonical = list(CANONICAL_MARKETS.keys())
        for market in all_canonical:
            if market not in market_scores:
                market_scores[market] = 0.0
                market_patterns[market] = []
        
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
