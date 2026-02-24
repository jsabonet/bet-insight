"""
Serviço de EXPLICAÇÃO com Google Gemini AI
A IA NÃO DECIDE - apenas EXPLICA decisões já tomadas
Otimizado para: latência <5s, custo reduzido, credibilidade alta
"""
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from django.conf import settings
from django.core.cache import cache
from typing import Dict, Optional
import logging
import json
import time
import hashlib
from .ai_helpers import parse_and_validate_response, format_analysis_for_frontend

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Serviço de análise com IA (Google Gemini)"""
    
    def __init__(self):
        api_key = settings.GOOGLE_GEMINI_API_KEY
        if not api_key:
            logger.error("Chave da API do Gemini não configurada.")
            self.model = None
            return

        genai.configure(api_key=api_key)
        model_name = 'gemini-1.5-flash-latest'
        
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"✅ AI Analyzer usando Gemini Flash Latest")
        except Exception as e:
            logger.error(f"Falha ao inicializar Gemini Flash: {e}")
            try:
                model_name = 'gemini-1.5-pro-latest'
                self.model = genai.GenerativeModel(model_name)
                logger.warning(f"⚠️ Usando fallback: {model_name}")
            except Exception as e2:
                logger.error(f"Falha total ao inicializar Gemini: {e2}")
                self.model = None
        
        logger.info(f"AI Analyzer inicializado com modelo: {model_name}")
    
    
    def explain_decision(self, decision_data: Dict, enriched_data: Dict, strategy: str = 'value') -> Dict:
        """
        IA APENAS EXPLICA decisões prontas (NÃO decide)
        Retorna análise multi-mercado em português com formato híbrido
        
        Args:
            decision_data: Dados das decisões já tomadas
            enriched_data: Dados enriquecidos do jogo
            strategy: 'value' ou 'multiple' - adapta o prompt
        """
        try:
            # 1. CACHE (incluir strategy no cache key)
            cache_key = f"{self._generate_cache_key(decision_data, enriched_data)}_{strategy}"
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"✅ Explicação em CACHE (estratégia={strategy})")
                cached_result['cached'] = True
                return cached_result
            
            if not self.model:
                return self._fallback_explanation(decision_data, enriched_data, strategy=strategy)
            
            # 2. PROMPT (adaptar por estratégia)
            prompt = self._build_prompt(decision_data, enriched_data, strategy=strategy)
            
            home_name = enriched_data.get('fixture_details', {}).get('teams', {}).get('home', {}).get('name', 'Casa')
            away_name = enriched_data.get('fixture_details', {}).get('teams', {}).get('away', {}).get('name', 'Fora')
            
            logger.info(f"🤖 IA Explicando: {home_name} vs {away_name}")
            
            start_time = time.time()
            
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0,
                        'max_output_tokens': 2500,
                        'top_p': 0.95,
                        'top_k': 40,
                    }
                )
                logger.info(f"✅ Gemini respondeu em {time.time() - start_time:.2f}s")
                logger.info(f"📝 Resposta: {len(response.text)} chars")
            except Exception as e:
                logger.warning(f"⚠️ Erro na IA: {e}")
                return self._fallback_explanation(decision_data, enriched_data, strategy=strategy)
            
            generation_time = time.time() - start_time
            
            # 3. Gerar header padronizado + resposta da IA
            ai_response = response.text.strip()
            formatted_analysis = f"{ai_response}"
            
            result = {
                'success': True,
                'analysis': formatted_analysis,
                'reasoning': formatted_analysis,
                'generation_time': round(generation_time, 2),
                'cached': False,
            }
            
            # 5. CACHE por 1 hora
            cache.set(cache_key, result, 3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar explicação: {e}")
            return self._fallback_explanation(decision_data, enriched_data, strategy=strategy)
    
    def _generate_cache_key(self, decision_data: Dict, enriched_data: Dict) -> str:
        """Gera chave de cache única"""
        return self._generate_cache_key_internal(decision_data, enriched_data)
        
    def _generate_header(self, decision_data: Dict, enriched_data: Dict) -> str:
        """Gera cabeçalho padronizado da análise"""
        fixture = enriched_data.get('fixture_details', {})
        teams = fixture.get('teams', {})
        home_team = teams.get('home', {}).get('name', 'Casa') if teams else 'Casa'
        away_team = teams.get('away', {}).get('name', 'Fora') if teams else 'Fora'
        league_data = fixture.get('league', {})
        league = league_data.get('name', 'N/A') if league_data else 'N/A'
        fixture_data = fixture.get('fixture', {})
        raw_date = fixture_data.get('date', 'N/A') if fixture_data else 'N/A'
        
        confidence = decision_data.get('confidence', {})
        consensus = decision_data.get('model_probabilities', {}).get('consensus', {})
        
        # Format date
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
            match_date = dt.strftime('%d/%m/%Y %H:%M')
        except:
            match_date = raw_date
        
        # Determinar predição baseada no consensus (maior probabilidade)
        prob_home = consensus.get('home_win', 0)
        prob_draw = consensus.get('draw', 0)
        prob_away = consensus.get('away_win', 0)
        
        # Usar mesma lógica do prompt: comparações AND
        if prob_home > prob_draw and prob_home > prob_away:
            predicao = "Casa"
        elif prob_away > prob_home and prob_away > prob_draw:
            predicao = "Fora"
        else:
            predicao = "Empate"
        
        
    def _generate_cache_key_internal(self, decision_data: Dict, enriched_data: Dict) -> str:
        """Método auxiliar para gerar chave de cache"""
        fixture = enriched_data.get('fixture_details', {})
        teams = fixture.get('teams', {})
        home = teams.get('home', {}).get('name', '') if teams else ''
        away = teams.get('away', {}).get('name', '') if teams else ''
        date = fixture.get('fixture', {}).get('date', '') if fixture.get('fixture') else ''
        
        recommendation = decision_data.get('recommendation', {})
        pick = recommendation.get('pick', '')
        
        key_str = f"{home}_{away}_{date}_{pick}"
        return f"ai_explanation:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _select_best_bet_by_context(self, top_bets: list, enriched_data: Dict, strategy: str = 'value') -> Dict:
        """
        Analisa o contexto COMPLETO da partida e escolhe a aposta que melhor se encaixa.
        
        Agora considera 50+ variáveis contextuais:
        - xG e probabilidades (BÁSICO)
        - Forma/Momentum (CRÍTICO para apostas)
        - Lesões críticas (afeta mercados específicos)
        - Motivação assimétrica (six-pointers, jogos decisivos)
        - Fadiga (afeta estilo de jogo)
        - H2H (padrões históricos)
        - Tipo de competição (copa vs liga)
        - Clima (afeta gols)
        - Context Patterns do ContextAnalyzer
        - ELO differential (força real)
        - Statistics (corners, cartões, precisão de passes)
        """
        if not top_bets:
            return None
        
        # 1. DADOS BÁSICOS (xG e probabilidades)
        fixture = enriched_data.get('fixture_details', {})
        model_probs = enriched_data.get('model_probabilities', {})
        poisson = model_probs.get('poisson', {})
        consensus = model_probs.get('consensus', {})
        expected_goals = poisson.get('expected_goals', {})
        poisson_probs = poisson.get('probabilities', {})
        
        xg_home = expected_goals.get('home', 1.2)
        xg_away = expected_goals.get('away', 1.0)
        xg_total = xg_home + xg_away
        xg_diff = abs(xg_home - xg_away)
        
        prob_home = consensus.get('home_win', 0)
        prob_draw = consensus.get('draw', 0)
        prob_away = consensus.get('away_win', 0)
        prob_over_25 = poisson_probs.get('over_2_5', 0)
        prob_btts = poisson_probs.get('btts', 0)
        
        # 2. FEATURES AVANÇADAS (extrair do enriched_data se disponível)
        features_summary = enriched_data.get('features_summary', {})
        strength = features_summary.get('strength', {})
        form = features_summary.get('form', {})
        statistics = features_summary.get('statistics', {})
        context_features = features_summary.get('context', {})
        weather = features_summary.get('weather', {})
        h2h = features_summary.get('h2h', {})
        match_importance = features_summary.get('match_importance', {})
        injuries = features_summary.get('injuries_suspensions', {})
        motivation = features_summary.get('motivation', {})
        elo = features_summary.get('elo', {})
        competition = features_summary.get('competition', {})
        
        # 3. CONTEXT ANALYZER PATTERNS (padrões detectados)
        context_analysis = enriched_data.get('context_analysis', {})
        detected_patterns = context_analysis.get('patterns', [])
        pattern_names = [p['name'] for p in detected_patterns if p.get('confidence', 0) > 0.5]
        
        # 4. IDENTIFICAR CONTEXTO EXPANDIDO
        context = {
            # BÁSICO (xG)
            'favorito_claro': xg_diff > 0.5,
            'equilibrado': xg_diff < 0.3,
            'ofensivo': xg_total > 2.8,
            'defensivo': xg_total < 2.0,
            'btts_provavel': xg_home > 1.0 and xg_away > 1.0 and prob_btts > 0.45,
            'dominancia_home': xg_home > xg_away + 0.5,
            'dominancia_away': xg_away > xg_home + 0.5,
            
            # FORMA/MOMENTUM (crítico!)
            'home_hot_streak': form.get('home_momentum_last_5', 0) > 0.6,
            'away_hot_streak': form.get('away_momentum_last_5', 0) > 0.6,
            'home_cold_streak': form.get('home_momentum_last_5', 0) < 0.3,
            'away_cold_streak': form.get('away_momentum_last_5', 0) < 0.3,
            'form_assymetric': abs(form.get('home_momentum_last_5', 0.5) - form.get('away_momentum_last_5', 0.5)) > 0.4,
            
            # LESÕES (afeta mercados)
            'home_critical_injuries': injuries.get('home_key_players_missing', 0) >= 2,
            'away_critical_injuries': injuries.get('away_key_players_missing', 0) >= 2,
            'both_weakened': injuries.get('home_key_players_missing', 0) >= 1 and injuries.get('away_key_players_missing', 0) >= 1,
            
            # MOTIVAÇÃO
            'six_pointer': 'six_pointer' in pattern_names or match_importance.get('is_six_pointer', False),
            'home_must_win': motivation.get('home_motivation_score', 0.5) > 0.8,
            'away_must_win': motivation.get('away_motivation_score', 0.5) > 0.8,
            'motivation_assymetric': 'asymmetric_motivation' in pattern_names,
            'low_motivation_both': 'low_motivation_both' in pattern_names,
            
            # FADIGA
            'home_fatigued': context_features.get('home_days_rest', 7) < 3,
            'away_fatigued': context_features.get('away_days_rest', 7) < 3,
            'both_fatigued': context_features.get('home_days_rest', 7) < 3 and context_features.get('away_days_rest', 7) < 3,
            'both_rested': context_features.get('home_days_rest', 7) >= 5 and context_features.get('away_days_rest', 7) >= 5,
            'fatigue_asymmetric': abs(context_features.get('home_days_rest', 7) - context_features.get('away_days_rest', 7)) >= 3,
            
            # H2H
            'h2h_high_scoring': h2h.get('avg_total_goals_h2h', 0) > 3.0,
            'h2h_low_scoring': h2h.get('avg_total_goals_h2h', 0) < 2.0,
            'h2h_home_dominance': h2h.get('home_win_rate_h2h', 0.33) > 0.6,
            'h2h_away_dominance': h2h.get('away_win_rate_h2h', 0.33) > 0.6,
            'h2h_draws_frequent': h2h.get('draw_rate_h2h', 0.25) > 0.4,
            
            # TIPO DE COMPETIÇÃO
            'is_cup': competition.get('is_cup_competition', False),
            'is_knockout': competition.get('is_knockout_stage', False),
            
            # CLIMA
            'bad_weather': weather.get('goal_impact', 0) < -0.2,  # Clima reduz gols
            'good_weather': weather.get('goal_impact', 0) > 0.1,  # Clima aumenta gols
            
            # STATISTICS AVANÇADAS
            'home_set_pieces_strong': statistics.get('home_corner_advantage', 0) > 2.0,
            'away_set_pieces_strong': statistics.get('away_corner_advantage', 0) > 2.0,
            'high_cards_expected': statistics.get('cards_per_game_both', 0) > 4.0,
            
            # ELO (força real)
            'elo_gap_large': elo.get('elo_diff_home_minus_away', 0) > 200,  # Home muito mais forte
            'elo_gap_negative': elo.get('elo_diff_home_minus_away', 0) < -200,  # Away muito mais forte
            
            # CONTEXT PATTERNS
            'derby': 'derby_context' in pattern_names,
            'upset_potential': 'upset_potential' in pattern_names,
            'open_game_pattern': 'open_game' in pattern_names,
            'defensive_fatigue': 'defensive_fatigue_game' in pattern_names,
            'balanced_tight': 'balanced_tight_game' in pattern_names,
        }
        
        # LOG contexto expandido
        active_contexts = [k for k, v in context.items() if v]
        logger.info(f"🎯 Contexto EXPANDIDO da partida ({len(active_contexts)} fatores ativos):")
        logger.info(f"   {', '.join(active_contexts[:10])}")
        if len(active_contexts) > 10:
            logger.info(f"   ... e mais {len(active_contexts) - 10} fatores")
        
        # Avaliar cada aposta em relação ao contexto expandido
        best_fit_bet = None
        best_fit_score = -1
        
        for bet in top_bets:
            fit_score = self._calculate_contextual_fit_score(bet, context, enriched_data, strategy)
            logger.info(f"   {bet['market_display']}: fit_score={fit_score:.2f}")
            
            if fit_score > best_fit_score:
                best_fit_score = fit_score
                best_fit_bet = bet
        
        logger.info(f"✅ Melhor aposta contextual: {best_fit_bet['market_display']} (fit={best_fit_score:.2f})")
        return best_fit_bet
    
    def _calculate_contextual_fit_score(self, bet: Dict, context: Dict, enriched_data: Dict, strategy: str) -> float:
        """
        Calcula o score de adequação da aposta ao contexto EXPANDIDO.
        Agora considera 50+ variáveis contextuais para seleção precisa.
        """
        market = bet.get('market', '').lower()
        pick = bet.get('pick', '').lower()
        probability = bet.get('probability', 0)
        ev_pct = bet.get('ev_pct', 0)
        
        # Score base: combinação de probabilidade e EV
        if strategy == 'multiple':
            base_score = probability * 70 + max(0, ev_pct) * 0.3
        else:
            base_score = probability * 40 + max(0, ev_pct) * 0.6
        
        # Multiplicadores contextuais (baseados em TODOS os contextos)
        multiplier = 1.0
        
        # ==================== MATCH WINNER / RESULTADO FINAL ====================
        if 'match winner' in market or 'match result' in market:
            if 'home' in pick or '1' == pick:
                # Vitória Casa
                if context['favorito_claro'] and context['dominancia_home']:
                    multiplier *= 1.4  # Favorito claro em casa
                if context['home_hot_streak']:
                    multiplier *= 1.3  # Casa em boa forma
                if context['away_cold_streak'] or context['away_critical_injuries']:
                    multiplier *= 1.2  # Visitante enfraquecido
                if context['h2h_home_dominance']:
                    multiplier *= 1.2  # Histórico favorável
                if context['home_must_win'] and not context['away_must_win']:
                    multiplier *= 1.15  # Motivação superior
                if context['elo_gap_large']:
                    multiplier *= 1.2  # ELO muito superior
                    
            elif 'away' in pick or '2' == pick:
                # Vitória Fora
                if context['favorito_claro'] and context['dominancia_away']:
                    multiplier *= 1.4
                if context['away_hot_streak']:
                    multiplier *= 1.3
                if context['home_cold_streak'] or context['home_critical_injuries']:
                    multiplier *= 1.2
                if context['h2h_away_dominance']:
                    multiplier *= 1.2
                if context['away_must_win'] and not context['home_must_win']:
                    multiplier *= 1.15
                if context['elo_gap_negative']:
                    multiplier *= 1.2
                    
            elif 'draw' in pick or 'x' == pick:
                # Empate
                if context['equilibrado']:
                    multiplier *= 1.4  # Jogo equilibrado
                if context['balanced_tight']:
                    multiplier *= 1.3  # Padrão de jogo apertado
                if context['h2h_draws_frequent']:
                    multiplier *= 1.3  # H2H com muitos empates
                if context['low_motivation_both']:
                    multiplier *= 1.25  # Ambos desmotivados
                if context['is_cup'] or context['is_knockout']:
                    multiplier *= 1.2  # Copas tendem a empates
                if context['both_weakened']:
                    multiplier *= 1.15  # Ambos com lesões
                if context['derby']:
                    multiplier *= 1.2  # Derbys tendem a empates
        
        # ==================== OVER/UNDER GOLS ====================
        elif 'goals over/under' in market or 'over' in pick or 'under' in pick:
            if 'over' in pick:
                # Over
                if context['ofensivo']:
                    multiplier *= 1.5  # Jogo ofensivo
                if context['open_game_pattern']:
                    multiplier *= 1.4  # Padrão de jogo aberto
                if context['defensive_fatigue']:
                    multiplier *= 1.4  # Defesas fatigadas
                if context['both_weakened']:
                    multiplier *= 1.3  # Defesas enfraquecidas por lesões
                if context['h2h_high_scoring']:
                    multiplier *= 1.3  # H2H com muitos gols
                if context['home_hot_streak'] and context['away_hot_streak']:
                    multiplier *= 1.25  # Ambos atacando bem
                if context['good_weather']:
                    multiplier *= 1.15  # Clima favorável a gols
                if context['derby'] and not context['is_cup']:
                    multiplier *= 1.2  # Derbys de liga tendem a ser abertos
                    
                # Penalizações para Over
                if context['defensivo']:
                    multiplier *= 0.6  # Jogo defensivo
                if context['is_cup'] or context['is_knockout']:
                    multiplier *= 0.75  # Copas mais fechadas
                if context['bad_weather']:
                    multiplier *= 0.8  # Clima ruim reduz gols
                if context['both_rested'] and context['equilibrado']:
                    multiplier *= 0.85  # Times descansados jogam mais fechado
                    
            elif 'under' in pick:
                # Under
                if context['defensivo']:
                    multiplier *= 1.5  # Jogo defensivo
                if context['is_cup'] or context['is_knockout']:
                    multiplier *= 1.4  # Copas tendem a Under
                if context['h2h_low_scoring']:
                    multiplier *= 1.3  # H2H com poucos gols
                if context['balanced_tight']:
                    multiplier *= 1.3  # Jogo apertado
                if context['bad_weather']:
                    multiplier *= 1.25  # Clima ruim
                if context['motivation_assymetric'] and not context['six_pointer']:
                    multiplier *= 1.2  # Motivação desigual sem importância
                if context['both_fatigued']:
                    multiplier *= 1.15  # Ambos cansados jogam devagar (mas não tanto quanto fadiga defensiva)
                    
                # Penalizações para Under
                if context['ofensivo']:
                    multiplier *= 0.6
                if context['open_game_pattern']:
                    multiplier *= 0.7
                if context['defensive_fatigue']:
                    multiplier *= 0.6  # Defesas fatigadas = mais gols
        
        # ==================== BOTH TEAMS TO SCORE (BTTS) ====================
        elif 'both teams score' in market or 'btts' in market:
            if 'yes' in pick:
                # BTTS Yes
                if context['btts_provavel']:
                    multiplier *= 1.6  # Ambos com chances de marcar
                if context['open_game_pattern']:
                    multiplier *= 1.4
                if context['six_pointer']:
                    multiplier *= 1.3  # Jogos decisivos = ambos atacam
                if context['h2h_high_scoring']:
                    multiplier *= 1.3
                if context['form_assymetric'] and context['equilibrado']:
                    multiplier *= 1.2  # Formas diferentes mas jogo equilibrado
                if context['defensive_fatigue']:
                    multiplier *= 1.3
                if context['both_weakened']:
                    multiplier *= 1.25
                    
                # Penalizações para BTTS Yes
                if context['favorito_claro'] or context['dominancia_home'] or context['dominancia_away']:
                    multiplier *= 0.7  # Uma equipe domina = menos chances de BTTS
                if context['is_cup'] or context['is_knockout']:
                    multiplier *= 0.75
                if context['home_critical_injuries'] or context['away_critical_injuries']:
                    # Se só um tem lesões críticas (não ambos), reduz BTTS
                    if not context['both_weakened']:
                        multiplier *= 0.8
                        
            elif 'no' in pick:
                # BTTS No
                if context['favorito_claro']:
                    multiplier *= 1.4  # Favorito pode não sofrer
                if context['is_cup'] or context['is_knockout']:
                    multiplier *= 1.3
                if context['h2h_low_scoring']:
                    multiplier *= 1.25
                if context['balanced_tight'] and context['low_motivation_both']:
                    multiplier *= 1.3  # Jogo sem graça
        
        # ==================== DOUBLE CHANCE ====================
        elif 'double chance' in market:
            if context['equilibrado']:
                multiplier *= 1.4  # Ideal para jogos equilibrados
            if context['balanced_tight']:
                multiplier *= 1.3
            if context['upset_potential']:
                multiplier *= 1.3  # Boa para cobrir zebra
            if context['is_cup']:
                multiplier *= 1.2  # Copas mais imprevisíveis
            if context['derby']:
                multiplier *= 1.2  # Derbys imprevisíveis
                
            # Penalizações
            if context['favorito_claro']:
                multiplier *= 0.85  # Menos value quando há favorito
        
        # ==================== DRAW NO BET ====================
        elif 'draw no bet' in market:
            if context['equilibrado'] and (context['favorito_claro'] == False):
                multiplier *= 1.3  # Pequeno favorito em jogo equilibrado
            if context['favorito_claro']:
                multiplier *= 1.2  # OK para favoritos
            if context['form_assymetric']:
                multiplier *= 1.15  # Forma assimétrica favorece um lado
            if context['h2h_draws_frequent']:
                multiplier *= 0.8  # Histórico de empates reduz value
        
        # ==================== ASIAN HANDICAP ====================
        elif 'asian handicap' in market or 'handicap' in market:
            if context['favorito_claro']:
                multiplier *= 1.3  # Bom para favoritos cobrirem handicap
            if context['elo_gap_large'] or context['elo_gap_negative']:
                multiplier *= 1.25  # Gap ELO grande
            if context['form_assymetric']:
                multiplier *= 1.2  # Forma muito diferente
            if context['home_critical_injuries'] or context['away_critical_injuries']:
                multiplier *= 1.15  # Lesões afetam margem
        
        # ==================== GOALS HOME/AWAY ====================
        elif 'home' in market or 'away' in market:
            if ('home' in market and context['dominancia_home']) or \
               ('away' in market and context['dominancia_away']):
                multiplier *= 1.4  # Dominância clara
            if 'home' in market and context['home_hot_streak']:
                multiplier *= 1.3
            if 'away' in market and context['away_hot_streak']:
                multiplier *= 1.3
            if 'home' in market and context['home_set_pieces_strong']:
                multiplier *= 1.2  # Forte em bolas paradas
            if 'away' in market and context['away_set_pieces_strong']:
                multiplier *= 1.2
        
        # ==================== CORNERS ====================
        elif 'corner' in market:
            if context['favorito_claro']:
                multiplier *= 1.3  # Favoritos tendem a ter mais corners
            if context['home_set_pieces_strong'] or context['away_set_pieces_strong']:
                multiplier *= 1.25  # Times fortes em bolas paradas
            if context['open_game_pattern']:
                multiplier *= 1.2  # Jogos abertos = mais corners
        
        # ==================== CARDS ====================
        elif 'card' in market or 'yellow' in market or 'red' in market:
            if context['high_cards_expected']:
                multiplier *= 1.4  # Estatísticas indicam muitos cartões
            if context['derby']:
                multiplier *= 1.35  # Derbys = mais cartões
            if context['six_pointer']:
                multiplier *= 1.3  # Jogos decisivos = jogo duro
            if context['is_cup'] or context['is_knockout']:
                multiplier *= 1.25  # Copas = mais cartões
        
        # ==================== HALFTIME MARKETS ====================
        elif 'halftime' in market or 'ht' in market:
            if context['favorito_claro']:
                multiplier *= 1.2  # Favoritos começam forte
            if context['home_must_win'] or context['away_must_win']:
                multiplier *= 1.15  # Must-win = início agressivo
            if context['balanced_tight']:
                multiplier *= 0.85  # Jogos apertados = HT mais difícil de prever
        
        final_score = base_score * multiplier
        
        return final_score
    
    def _get_context_explanation(self, enriched_data: Dict) -> str:
        """
        Gera explicação EXPANDIDA do contexto da partida baseada em 50+ variáveis.
        Agora muito mais descritiva e precisa.
        """
        fixture = enriched_data.get('fixture_details', {})
        model_probs = enriched_data.get('model_probabilities', {})
        poisson = model_probs.get('poisson', {})
        expected_goals = poisson.get('expected_goals', {})
        
        xg_home = expected_goals.get('home', 1.2)
        xg_away = expected_goals.get('away', 1.0)
        xg_total = xg_home + xg_away
        xg_diff = abs(xg_home - xg_away)
        
        # Features avançadas
        features_summary = enriched_data.get('features_summary', {})
        form = features_summary.get('form', {})
        injuries = features_summary.get('injuries_suspensions', {})
        motivation = features_summary.get('motivation', {})
        competition = features_summary.get('competition', {})
        h2h = features_summary.get('h2h', {})
        weather = features_summary.get('weather', {})
        context_features = features_summary.get('context', {})
        
        # Context patterns
        context_analysis = enriched_data.get('context_analysis', {})
        detected_patterns = context_analysis.get('patterns', [])
        pattern_names = [p['name'] for p in detected_patterns if p.get('confidence', 0) > 0.5]
        
        # Obter probabilidades do consensus para melhor classificação
        consensus = model_probs.get('consensus', {})
        home_prob = consensus.get('home_win', 0.33)
        away_prob = consensus.get('away_win', 0.33)
        prob_diff = abs(home_prob - away_prob)
        
        # Construir descrição contextual rica
        context_parts = []
        
        # 1. xG e resultado esperado (considerar AMBOS xG e probabilidades)
        # ✅ CORREÇÃO 24/02: Usar consensus para determinar favorito, não apenas xG
        # xG pode ser enganoso (1.7 vs 1.9 parece equilibrado mas prob pode ser 60% vs 20%)
        if prob_diff > 0.20:  # Diferença de probabilidade > 20% = favorito claro
            if home_prob > away_prob:
                context_parts.append(f"Favorito CLARO em casa (prob: {home_prob*100:.0f}% vs {away_prob*100:.0f}%, xG: {xg_home:.1f} vs {xg_away:.1f})")
            else:
                context_parts.append(f"Favorito CLARO visitante (prob: {away_prob*100:.0f}% vs {home_prob*100:.0f}%, xG: {xg_away:.1f} vs {xg_home:.1f})")
        elif xg_diff < 0.3 and prob_diff < 0.15:  # Ambos equilibrados
            context_parts.append(f"Jogo EQUILIBRADO (xG: {xg_home:.1f} vs {xg_away:.1f}, prob similar)")
        
        # 2. Expectativa de gols
        if xg_total > 2.8:
            context_parts.append(f"Jogo OFENSIVO ({xg_total:.1f} gols esperados)")
        elif xg_total < 2.0:
            context_parts.append(f"Jogo DEFENSIVO ({xg_total:.1f} gols esperados)")
        
        # 3. Forma/Momentum (CRÍTICO)
        home_momentum = form.get('home_momentum_last_5', 0.5)
        away_momentum = form.get('away_momentum_last_5', 0.5)
        if home_momentum > 0.65:
            context_parts.append(f"Casa em ÓTIMA forma ({home_momentum*100:.0f}%)")
        elif home_momentum < 0.35:
            context_parts.append(f"Casa em MÁ forma ({home_momentum*100:.0f}%)")
        if away_momentum > 0.65:
            context_parts.append(f"Visitante em ÓTIMA forma ({away_momentum*100:.0f}%)")
        elif away_momentum < 0.35:
            context_parts.append(f"Visitante em MÁ forma ({away_momentum*100:.0f}%)")
        
        # 4. Lesões críticas
        home_injuries = injuries.get('home_key_players_missing', 0)
        away_injuries = injuries.get('away_key_players_missing', 0)
        if home_injuries >= 2:
            context_parts.append(f"Casa com {home_injuries} lesões CRÍTICAS")
        if away_injuries >= 2:
            context_parts.append(f"Visitante com {away_injuries} lesões CRÍTICAS")
        
        # 5. Motivação
        home_motivation = motivation.get('home_motivation_score', 0.5)
        away_motivation = motivation.get('away_motivation_score', 0.5)
        if abs(home_motivation - away_motivation) > 0.3:
            if home_motivation > away_motivation:
                context_parts.append(f"Casa MUITO mais motivada")
            else:
                context_parts.append(f"Visitante MUITO mais motivado")
        
        # 6. Six-pointer ou jogo decisivo
        if 'six_pointer' in pattern_names:
            context_parts.append("Jogo DECISIVO (six-pointer)")
        elif motivation.get('home_motivation_score', 0.5) > 0.8 or motivation.get('away_motivation_score', 0.5) > 0.8:
            context_parts.append("Jogo de ALTA importância")
        
        # 7. Fadiga
        home_rest = context_features.get('home_days_rest', 7)
        away_rest = context_features.get('away_days_rest', 7)
        if home_rest < 3:
            context_parts.append(f"Casa FATIGADA ({home_rest} dias descanso)")
        if away_rest < 3:
            context_parts.append(f"Visitante FATIGADO ({away_rest} dias descanso)")
        
        # 8. H2H patterns
        h2h_avg_goals = h2h.get('avg_total_goals_h2h', 0)
        if h2h_avg_goals > 3.0:
            context_parts.append(f"H2H com MUITOS gols ({h2h_avg_goals:.1f} média)")
        elif h2h_avg_goals > 0 and h2h_avg_goals < 2.0:
            context_parts.append(f"H2H com POUCOS gols ({h2h_avg_goals:.1f} média)")
        
        # 9. Tipo de competição
        comp_name = competition.get('competition_name', '')
        if competition.get('is_cup_competition'):
            if competition.get('is_knockout_stage'):
                context_parts.append(f"{comp_name} - eliminatória (táticas mais cautelosas)")
            else:
                # Fase de grupos pode ser de copa nacional ou liga internacional
                if 'champions' in comp_name.lower() or 'europa' in comp_name.lower() or 'libertadores' in comp_name.lower():
                    context_parts.append(f"{comp_name} - fase de grupos")
                else:
                    context_parts.append(f"Copa - fase de grupos")
        
        # 10. Clima
        weather_impact = weather.get('goal_impact', 0)
        if weather_impact < -0.2:
            context_parts.append(f"Clima RUIM afetando gols")
        elif weather_impact > 0.1:
            context_parts.append(f"Clima FAVORÁVEL a gols")
        
        # 11. Patterns importantes
        if 'derby_context' in pattern_names:
            context_parts.append("DERBY/Rivalidade")
        if 'upset_potential' in pattern_names:
            context_parts.append("POTENCIAL de zebra")
        if 'open_game' in pattern_names:
            context_parts.append("Padrão de jogo ABERTO")
        if 'defensive_fatigue_game' in pattern_names:
            context_parts.append("Defesas FATIGADAS")
        
        # Combinar descrições
        if context_parts:
            return " | ".join(context_parts[:5])  # Máximo 5 fatores principais
        else:
            return f"Jogo padrão (xG: {xg_home:.1f} vs {xg_away:.1f})"
    
    def _fallback_explanation(self, decision_data: Dict, enriched_data: Dict, strategy: str = 'value') -> Dict:
        """Fallback quando IA falha - gerar análise baseada em regras COM SELEÇÃO CONTEXTUAL"""
        logger.warning(f"⚠️ IA não disponível - usando fallback baseado em regras (estratégia={strategy})")
        
        # Extrair dados necessários
        top_bets = decision_data.get('top_bets', [])
        confidence = decision_data.get('confidence', {})
        risk = decision_data.get('risk', 'medium')
        model_probs = decision_data.get('model_probabilities', {})
        consensus = model_probs.get('consensus', {})
        
        if not top_bets:
            return {
                'success': False,
                'analysis': None,
                'reasoning': None,
                'generation_time': 0.0,
                'cached': False,
                'fallback': True
            }
        
        # 🎯 SELEÇÃO CONTEXTUAL: escolher a melhor aposta baseada no contexto
        best_bet = self._select_best_bet_by_context(top_bets, enriched_data, strategy)
        
        if not best_bet:
            best_bet = top_bets[0]  # Fallback: primeira aposta
        
        if not best_bet:
            return {
                'success': False,
                'analysis': None,
                'reasoning': None,
                'generation_time': 0.0,
                'cached': False,
                'fallback': True
            }
        
        # Gerar análise adaptada à estratégia
        # Obter explicação do contexto
        context_explanation = self._get_context_explanation(enriched_data)
        
        if strategy == 'multiple':
            # MODO BILHETE: Foco em probabilidade e combinação
            # ✅ CORREÇÃO 22/02: Filtrar apostas adequadas para bilhetes (odds 1.30-2.00, prob ≥65%)
            MIN_ODD_MULTIPLE = 1.30
            MAX_ODD_MULTIPLE = 2.00
            MIN_PROB_MULTIPLE = 0.65
            
            suitable_bets = [
                bet for bet in top_bets 
                if (bet.get('market_odd') or 0) >= MIN_ODD_MULTIPLE 
                and (bet.get('market_odd') or 0) <= MAX_ODD_MULTIPLE
                and bet.get('probability', 0) >= MIN_PROB_MULTIPLE
            ]
            
            if not suitable_bets:
                # Fallback: relaxar critérios se não houver apostas adequadas
                logger.warning("⚠️ Nenhuma aposta adequada para bilhete (odds 1.30-2.00, prob ≥65%). Relaxando para prob ≥50%")
                suitable_bets = [
                    bet for bet in top_bets 
                    if (bet.get('market_odd') or 0) >= MIN_ODD_MULTIPLE 
                    and (bet.get('market_odd') or 0) <= MAX_ODD_MULTIPLE
                    and bet.get('probability', 0) >= 0.50
                ]
            
            if not suitable_bets:
                # Último fallback: usar a melhor disponível mas marcar como inadequada
                logger.warning("⚠️ Nenhuma aposta com odds adequadas. Usando melhor disponível (pode não ser ideal para bilhete)")
                suitable_bets = [best_bet]
            
            # 🎯 SELEÇÃO CONTEXTUAL: Re-selecionar dentro das suitable_bets
            best_bet_contextual = self._select_best_bet_by_context(suitable_bets, enriched_data, strategy)
            if best_bet_contextual:
                best_bet = best_bet_contextual
            else:
                best_bet = suitable_bets[0]
            
            market_odd = best_bet.get('market_odd') or 0
            
            analysis = f"""📋 MELHOR PARA BILHETE (SELEÇÃO CONTEXTUAL)
---------------------------------------
🎯 CONTEXTO: {context_explanation}

Aposta: {best_bet['market_display']}
Odd: {market_odd:.2f} (ideal para bilhetes: 1.30-2.00)
Probabilidade: {best_bet['probability']*100:.1f}% (mínimo 65%)
Stake: {best_bet['stake_units']:.1f} unidades

PORQUE ESTA APOSTA FOI ESCOLHIDA:
• {best_bet['reason']}
• Alta probabilidade ({best_bet['probability']*100:.1f}% de chance)
• Odd moderada (boa para combinar com outras apostas)
• SE ENCAIXA PERFEITAMENTE no contexto da partida

💡 DICA DE BILHETE:
Combine com 2-3 apostas similares de outros jogos.
Odd total esperada: 3.00-8.00
Probabilidade combinada: 15-30%

---------------------------------------
OUTRAS OPÇÕES PARA BILHETE:
---------------------------------------
"""
            # Adicionar alternativas adequadas para bilhetes
            for bet in suitable_bets[1:3]:  # Máximo 2 alternativas
                analysis += f"• {bet['market_display']} (Prob: {bet['probability']*100:.0f}%, Odd: {bet.get('market_odd', 0):.2f})\n"
            
            analysis += """
⚠️ ATENÇÃO:
Bilhetes são mais arriscados. Mesmo com alta probabilidade individual,
apenas ~20% dos bilhetes 3x acertam todas as apostas.
Use em favoritos consistentes, não underdogs.

---------------------------------------"""
        
        else:
            # MODO VALUE: Foco em EV e lucro longo prazo
            market_odd = best_bet.get('market_odd') or 0
            analysis = f"""🎯 RECOMENDAÇÃO PRINCIPAL (SELEÇÃO CONTEXTUAL)
---------------------------------------
🎯 CONTEXTO: {context_explanation}

Aposta: {best_bet['market_display']}
Odd: {market_odd:.2f}
EV: {best_bet['ev_pct']:+.1f}%
Stake: {best_bet['stake_units']:.1f} unidades
Risco: {risk.upper()}

PORQUE ESTA APOSTA FOI ESCOLHIDA:
• {best_bet['reason']}
• Probabilidade calculada: {best_bet['probability']*100:.1f}%
• Confiança do modelo: {confidence.get('stars', 3)}/5
• SE ENCAIXA PERFEITAMENTE no contexto da partida

⚠️ NÃO APOSTE SE:
• A odd cair abaixo de {best_bet.get('fair_odd') or 0:.2f}
• Houver mudanças significativas nas condições do jogo
"""

            # Adicionar alternativas se houver
            if len(top_bets) > 1:
                analysis += "\n---------------------------------------\nALTERNATIVAS:\n---------------------------------------\n"
                
                other_bets = [b for b in top_bets if b != best_bet][:2]  # Máximo 2 alternativas
                for i, bet in enumerate(other_bets, 2):
                    analysis += f"• Opção #{i}: {bet['market_display']} (EV: {bet['ev_pct']:+.1f}%, Prob: {bet['probability']*100:.0f}%)\n"
            
            analysis += "\n---------------------------------------"
        
        return {
            'success': True,
            'analysis': analysis,
            'reasoning': analysis,
            'generation_time': 0.0,
            'cached': False,
            'fallback': True
        }
    
    def _build_prompt(self, decision_data: Dict, enriched_data: Dict, strategy: str = 'value') -> str:
        """
        Prompt para IA APENAS EXPLICAR decisões prontas.
        A IA NÃO decide, apenas interpreta e contextualiza.
        
        Args:
            strategy: 'value' (maximizar EV) ou 'multiple' (alta prob para bilhetes)
        """
        confidence = decision_data.get('confidence', {})
        risk = decision_data.get('risk', 'medium')
        model_probs = decision_data.get('model_probabilities', {})
        top_bets = decision_data.get('top_bets', [])  # DECISÕES JÁ TOMADAS
        
        # Extrair dados
        fixture = enriched_data.get('fixture_details', {})
        teams = fixture.get('teams', {})
        home_team = teams.get('home', {}).get('name', 'Casa') if teams else 'Casa'
        away_team = teams.get('away', {}).get('name', 'Fora') if teams else 'Fora'
        league_data = fixture.get('league', {})
        league = league_data.get('name', 'N/A') if league_data else 'N/A'
        fixture_data = fixture.get('fixture', {})
        raw_date = fixture_data.get('date', 'N/A') if fixture_data else 'N/A'
        
        # Format date
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
            match_date = dt.strftime('%d/%m/%Y %H:%M')
        except:
            match_date = raw_date
        
        poisson = model_probs.get('poisson', {})
        consensus = model_probs.get('consensus', {})
        
        # Extrair xG
        expected_goals = poisson.get('expected_goals', {})
        xg_home = expected_goals.get('home', 1.2)
        xg_away = expected_goals.get('away', 1.0)
        most_likely = poisson.get('most_likely_score', '1-1')
        
        if xg_home == 0 and xg_away == 0:
            logger.warning(f"⚠️ xG zerado! Fallback para 1.2 x 1.0")
            xg_home, xg_away = 1.2, 1.0
        
        prob_home = consensus.get('home_win', 0) * 100
        prob_draw = consensus.get('draw', 0) * 100
        prob_away = consensus.get('away_win', 0) * 100
        
        # Determinar predição
        if prob_home > prob_draw and prob_home > prob_away:
            predicao = "Casa"
        elif prob_away > prob_home and prob_away > prob_draw:
            predicao = "Fora"
        else:
            predicao = "Empate"
        
        # Formatar TOP BETS decididas
        bets_info = "\nAPOSTAS RECOMENDADAS (JA SELECIONADAS - APENAS EXPLIQUE):\n"
        for bet in top_bets:
            market_odd = bet.get('market_odd') or 0
            fair_odd = bet.get('fair_odd') or 0
            bets_info += f"\n{bet['rank']}. {bet['market_display']} - {bet['pick']}\n"
            bets_info += f"   Probabilidade: {bet['probability']*100:.1f}%\n"
            bets_info += f"   Odd mercado: {market_odd:.2f} | Fair: {fair_odd:.2f}\n"
            bets_info += f"   EV: {bet['ev_pct']:+.1f}%\n"
            bets_info += f"   Stake: {bet['stake_units']} unidade(s)\n"
            bets_info += f"   Razao: {bet['reason']}\n"
        
        # Probabilidades extras
        poisson_probs = poisson.get('probabilities', {})
        bets_info += "\nPROBABILIDADES ADICIONAIS (para contexto):\n"
        bets_info += f"   Over 1.5: {poisson_probs.get('over_1_5', 0)*100:.1f}%\n"
        bets_info += f"   Over 2.5: {poisson_probs.get('over_2_5', 0)*100:.1f}%\n"
        bets_info += f"   Over 3.5: {poisson_probs.get('over_3_5', 0)*100:.1f}%\n"
        bets_info += f"   BTTS: {poisson_probs.get('btts', 0)*100:.1f}%\n"
        
        # ✅ PROMPTS DIFERENTES POR ESTRATÉGIA
        if strategy == 'multiple':
            # MODO BILHETE: Foco em PROBABILIDADE e COMBINAÇÃO
            prompt = f"""Você é um CONSULTOR DE BILHETES MÚLTIPLOS que ajuda usuários a combinar apostas seguras.

SEU PAPEL:
- ANALISE O CONTEXTO DA PARTIDA (favorito claro? equilibrado? ofensivo? defensivo?)
- Das 3 apostas fornecidas, ESCOLHA A MELHOR baseada no contexto
- Explique por que essa aposta SE ENCAIXA PERFEITAMENTE no contexto
- Use linguagem simples e foque em PROBABILIDADE + CONTEXTO

IMPORTANTE: NÃO GERE CABEÇALHO/HEADER - o sistema já vai adicionar. Comece DIRETO com a recomendação.

CRITÉRIOS DO MODO BILHETE:
- Probabilidade mínima: 50%
- EV mínimo: 0% (não-negativo, aceita favoritos)
- Odds ideais para bilhetes: 1.30-2.50

CONTEXTO DA PARTIDA:
- {home_team} vs {away_team}
- Liga: {league}
- Data: {match_date}
- Confiança: {confidence.get('stars', 3)}/5 - Risco: {risk.upper()}
- Probabilidades: Casa {prob_home:.1f}% | Empate {prob_draw:.1f}% | Fora {prob_away:.1f}%
- xG esperado: {xg_home:.2f} x {xg_away:.2f}
- Diferença xG: {abs(xg_home - xg_away):.2f} (>0.5 = favorito claro, <0.3 = equilibrado)
- Total gols esperados: {xg_home + xg_away:.2f} (>2.8 = ofensivo, <2.0 = defensivo)
- Placar provável: {most_likely}
- Resultado mais provável: {predicao}
{bets_info}

ANÁLISE CONTEXTUAL OBRIGATÓRIA:
1. Identifique o contexto: Favorito claro? Equilibrado? Ofensivo? Defensivo?
2. Para CADA uma das 3 apostas, avalie: "Esta aposta se encaixa neste contexto?"
3. ESCOLHA a aposta que MELHOR se encaixa
4. EXPLIQUE claramente por que essa aposta é a melhor para ESTE contexto específico

Exemplos de fit contextual:
- Match Winner: Melhor quando há favorito claro (xG diff > 0.5)
- Over/Under: Over bom para jogos ofensivos (xG total > 2.8), Under para defensivos (< 2.0)
- BTTS: Melhor quando ambos têm xG > 1.0
- Double Chance: Melhor para jogos equilibrados (xG diff < 0.3)

FORMATO DE RESPOSTA (OBRIGATÓRIO):

📋 MELHOR PARA BILHETE (SELEÇÃO CONTEXTUAL)
- Placar provável: {most_likely}
- Resultado mais provável: {predicao}
{bets_info}

FORMATO DE RESPOSTA (OBRIGATÓRIO):

📋 MELHOR PARA BILHETE
---------------------------------------
🎯 CONTEXTO: [Descreva o contexto: "Partida com favorito claro" / "Jogo equilibrado" / "Jogo ofensivo" / "Jogo defensivo"]

Aposta: [Nome da aposta escolhida - a que MELHOR se encaixa no contexto]
Mercado: [Tipo de mercado]
Odd: [Valor] (ideal para bilhetes: 1.30-2.00)
Probabilidade: [XX%] (mínimo 50%)
Stake: [X unidades]

PORQUE ESTA APOSTA FOI ESCOLHIDA:
• [Explicação de por que SE ENCAIXA no contexto específico desta partida]
• Alta probabilidade (50% ou mais)
• EV não-negativo (não perde value)
• Odd moderada (boa para combinar 1.30-2.50)

💡 DICA DE BILHETE:
Combine com 2-3 apostas similares de outros jogos.
Odd total esperada: 3.00-8.00
Probabilidade combinada: 15-30%

---------------------------------------
OUTRAS OPÇÕES PARA BILHETE:
---------------------------------------
[Liste outras apostas com prob >= 50% e EV >= 0%]

⚠️ ATENÇÃO:
Bilhetes são mais arriscados. Mesmo com alta probabilidade individual,
apenas ~20% dos bilhetes 3x acertam todas as apostas.
Use em favoritos consistentes, não underdogs.

---------------------------------------

REGRAS CRÍTICAS:
1. ANÁLISE CONTEXTUAL é obrigatória - explique o contexto da partida
2. ESCOLHA a aposta que MELHOR se encaixa no contexto (não apenas a primeira da lista)
3. Só recomende apostas com probabilidade >= 50%
4. Aceite EV >= 0% (favoritos com odds justas são OK)
5. Mencione odds ideais para combinar (1.30-2.50)
6. Sempre alerte sobre risco de bilhetes
7. Favoritos absolutos (70%+) são IDEAIS para bilhetes
"""
        else:
            # MODO VALUE: Foco em EV MÁXIMO e LUCRO LONGO PRAZO
            prompt = f"""Você é um CONSULTOR DE APOSTAS que dá recomendações DIRETAS e CLARAS.

SEU PAPEL:
- ANALISE O CONTEXTO DA PARTIDA (favorito claro? equilibrado? ofensivo? defensivo?)
- Das 3 apostas fornecidas, ESCOLHA A MELHOR baseada no contexto e EV
- Explique por que essa aposta SE ENCAIXA PERFEITAMENTE no contexto
- Use linguagem simples e chamadas de ação claras

IMPORTANTE: NÃO GERE CABEÇALHO/HEADER - o sistema já vai adicionar. Comece DIRETO com a recomendação.

CONTEXTO DA PARTIDA:
- {home_team} vs {away_team}
- Liga: {league}
- Data: {match_date}
- Confiança: {confidence.get('stars', 3)}/5 - Risco: {risk.upper()}
- Probabilidades: Casa {prob_home:.1f}% | Empate {prob_draw:.1f}% | Fora {prob_away:.1f}%
- xG esperado: {xg_home:.2f} x {xg_away:.2f}
- Diferença xG: {abs(xg_home - xg_away):.2f} (>0.5 = favorito claro, <0.3 = equilibrado)
- Total gols esperados: {xg_home + xg_away:.2f} (>2.8 = ofensivo, <2.0 = defensivo)
- Placar provável: {most_likely}
- Resultado mais provável: {predicao}
{bets_info}

ANÁLISE CONTEXTUAL OBRIGATÓRIA:
1. Identifique o contexto: Favorito claro? Equilibrado? Ofensivo? Defensivo?
2. Para CADA uma das 3 apostas, avalie: "Esta aposta se encaixa neste contexto?"
3. ESCOLHA a aposta que MELHOR se encaixa (pode não ser necessariamente a #1)
4. EXPLIQUE claramente por que essa aposta é a melhor para ESTE contexto específico

Exemplos de fit contextual:
- Match Winner: Melhor quando há favorito claro (xG diff > 0.5)
- Over/Under: Over bom para jogos ofensivos (xG total > 2.8), Under para defensivos (< 2.0)
- BTTS: Melhor quando ambos têm xG > 1.0
- Double Chance: Melhor para jogos equilibrados (xG diff < 0.3)

FORMATO DE RESPOSTA (OBRIGATÓRIO):

🎯 RECOMENDAÇÃO PRINCIPAL (SELEÇÃO CONTEXTUAL)
---------------------------------------
🎯 CONTEXTO: [Descreva o contexto: "Partida com favorito claro" / "Jogo equilibrado" / "Jogo ofensivo" / "Jogo defensivo"]

Aposta: [Nome da aposta escolhida - a que MELHOR se encaixa no contexto]
Mercado: [Tipo de mercado]
Odd: [Valor]
EV: [+XX%]
Stake: [X unidades]
Risco: {risk.upper()}

PORQUE ESTA APOSTA FOI ESCOLHIDA:
• [Explicação de por que SE ENCAIXA no contexto específico desta partida]
• EV positivo alto (+15% ou mais)
• Odd sobrevalorizada pelo mercado
• Probabilidade real: [XX%] vs odd paga: [YY%]

⚠️ NÃO APOSTE SE:
• A odd cair abaixo de [odd mínima]
• Houver lesões de última hora

---------------------------------------
ALTERNATIVAS (opcional - só se houver apostas com EV positivo):
---------------------------------------
Se preferir menos risco:
• Aposta #1: [Nome] - [Razão rápida]

Se quiser mais value:
• Aposta #3: [Nome] - [Razão rápida]

---------------------------------------

REGRAS CRÍTICAS:
1. ANÁLISE CONTEXTUAL é obrigatória - explique o contexto da partida
2. ESCOLHA a aposta que MELHOR se encaixa no contexto (não apenas a mais provável ou maior EV bruto)
3. Aposta #1 é sempre o resultado mais provável (pode ter EV negativo)
3. Foque em VALOR ESPERADO (EV), não apenas probabilidade
4. Mencione que é estratégia de LONGO PRAZO (100+ apostas)
"""
        
        return prompt

