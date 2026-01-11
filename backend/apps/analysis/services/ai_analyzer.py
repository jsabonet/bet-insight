"""
ServiÃ§o de EXPLICAÃ‡ÃƒO com Google Gemini AI
A IA NÃƒO DECIDE - apenas EXPLICA decisÃµes jÃ¡ tomadas
Otimizado para: latÃªncia <5s, custo reduzido, credibilidade alta
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
    """ServiÃ§o de anÃ¡lise com IA (Google Gemini)"""
    
    def __init__(self):
        api_key = settings.GOOGLE_GEMINI_API_KEY
        if not api_key:
            logger.error("Chave da API do Gemini nÃ£o configurada.")
            # Inicializa um modelo nulo para evitar crashes; chamadas retornarÃ£o erro estruturado
            self.model = None
            return

        genai.configure(api_key=api_key)
        
        # MIGRAÃ‡ÃƒO PARA GEMINI FLASH (4x mais rÃ¡pido, 75% mais barato)
        model_name = 'gemini-2.0-flash-exp'
        
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"âœ… AI Analyzer usando Gemini Flash (rÃ¡pido e eficiente)")
        except Exception as e:
            logger.error(f"Falha ao inicializar Gemini Flash: {e}")
            # Fallback para modelo anterior
            try:
                model_name = 'gemini-pro'
                self.model = genai.GenerativeModel(model_name)
                logger.warning(f"âš ï¸ Usando fallback: {model_name}")
            except Exception as e2:
                logger.error(f"Falha total ao inicializar Gemini: {e2}")
                self.model = None
        
        logger.info(f"AI Analyzer inicializado com modelo: {model_name}")
    
    
    def explain_decision(self, decision_data: Dict, enriched_data: Dict) -> Dict:
        """
        IA APENAS EXPLICA decisÃµes prontas (NÃƒO decide)
        
        OTIMIZAÃ‡Ã•ES:
        - Cache por match_id + market (1 hora)
        - Timeout de 5 segundos
        - Fallback determinÃ­stico se falhar
        - Prompt enxuto (~500 tokens vs 1500 antes)
        
        Args:
            decision_data (dict): DecisÃ£o do DecisionEngine
            enriched_data (dict): Dados enriquecidos mÃ­nimos
        
        Returns:
            dict: {
                'success': bool,
                'analysis': str (HTML formatado),
                'summary': str (1 frase),
                'bullets': list (3-5 items),
                'risk_warning': str,
                'generation_time': float,
                'cached': bool
            }
        """
        try:
            # 1. CACHE: Verificar se jÃ¡ explicamos esta decisÃ£o
            cache_key = self._generate_cache_key(decision_data, enriched_data)
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"âœ… ExplicaÃ§Ã£o em CACHE (economia de custo)")
                cached_result['cached'] = True
                return cached_result
            
            if not self.model:
                return self._fallback_explanation(decision_data, enriched_data)
            
            # 2. PROMPT ENXUTO: Apenas dados essenciais
            prompt = self._build_minimal_prompt(decision_data, enriched_data)
            
            home_name = enriched_data.get('fixture_details', {}).get('home_team', {}).get('name', 'Casa')
            away_name = enriched_data.get('fixture_details', {}).get('away_team', {}).get('name', 'Fora')
            
            logger.info(f"ðŸ¤– IA Explicando: {home_name} vs {away_name}")
            
            # 3. TIMEOUT: MÃ¡ximo 5 segundos
            start_time = time.time()
            
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0,  # ZERO criatividade - seguir instruÃ§Ãµes
                        'max_output_tokens': 1500,
                        'top_p': 0.95,
                        'top_k': 40,
                        'candidate_count': 1
                    }
                )
                logger.info(f"âœ… Gemini respondeu em {time.time() - start_time:.2f}s")
                logger.info(f"ðŸ“ Resposta do Gemini: {len(response.text)} caracteres")
                logger.info(f"ðŸ“„ Primeiros 200 chars: {response.text[:200]}...")
            except Exception as e:
                logger.warning(f"âš ï¸ Timeout ou erro na IA ({time.time() - start_time:.2f}s): {e}")
                logger.warning(f"ðŸ”„ Ativando FALLBACK determinÃ­stico")
                return self._fallback_explanation(decision_data, enriched_data)
            
            generation_time = time.time() - start_time
            
            # 4. PARSE E VALIDAÃ‡ÃƒO: Garantir formato fixo
            parsed = parse_and_validate_response(response.text)
            if not parsed['valid']:
                logger.warning(f"âš ï¸ Resposta da IA fora do formato esperado")
                logger.warning(f"ðŸ“ Resposta recebida: {response.text[:500]}...")
                logger.warning(f"ðŸ”„ Ativando FALLBACK determinÃ­stico")
                return self._fallback_explanation(decision_data, enriched_data)
            
            # 5. FORMATAR PARA FRONTEND (compatibilidade)
            formatted_analysis = format_analysis_for_frontend(
                parsed['recommendation'],
                parsed['bullets'],
                parsed['risk_warning']
            )
            
            result = {
                'success': True,
                'analysis': formatted_analysis,  # Formato antigo para compatibilidade
                'reasoning': formatted_analysis,  # Campo que modal espera
                'recommendation': parsed['recommendation'],
                'bullets': parsed['bullets'],
                'risk_warning': parsed['risk_warning'],
                'generation_time': round(generation_time, 2),
                'cached': False,
                'tokens_used': len(prompt.split()) + len(response.text.split())
            }
            
            # 6. CACHE: Salvar por 1 hora
            cache.set(cache_key, result, 3600)
            
            logger.info(f"âœ… ExplicaÃ§Ã£o gerada em {generation_time:.2f}s (cached para 1h)")
            
            return result
            
        except google_exceptions.ResourceExhausted as e:
            logger.error(f"Quota da API Gemini excedida: {e}")
            return self._fallback_explanation(decision_data, enriched_data)
        except Exception as e:
            logger.error(f"Erro ao gerar explicaÃ§Ã£o: {e}")
            return self._fallback_explanation(decision_data, enriched_data)
    
    def _generate_cache_key(self, decision_data: Dict, enriched_data: Dict) -> str:
        """Gera chave de cache Ãºnica por partida + mercado"""
        fixture = enriched_data.get('fixture_details', {})
        home = fixture.get('home_team', {}).get('name', '')
        away = fixture.get('away_team', {}).get('name', '')
        date = fixture.get('date', '')
        
        recommendation = decision_data.get('recommendation', {})
        market = recommendation.get('market_display', '')
        pick = recommendation.get('pick', '')
        
        # Hash MD5 para cache key compacta
        key_str = f"{home}_{away}_{date}_{market}_{pick}"
        return f"ai_explanation:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _fallback_explanation(self, decision_data: Dict, enriched_data: Dict) -> Dict:
        """
        Fallback DETERMINÃSTICO DECISÃ“RIO quando IA falha
        MantÃ©m formato profissional: APOSTAR ou NÃƒO APOSTAR
        """
        recommendation = decision_data.get('recommendation', {})
        confidence = decision_data.get('confidence', {})
        risk = decision_data.get('risk', 'medium')
        value_bets = decision_data.get('value_bets', [])
        model_probs = decision_data.get('model_probabilities', {})
        poisson = model_probs.get('poisson', {})
        
        pick = recommendation.get('pick', 'N/A')
        prob = recommendation.get('probability', 0)
        market = recommendation.get('market_display', 'N/A')
        market_odd = recommendation.get('odd', 0)
        
        # Calcular fair odd e value
        fair_odd = round(1 / prob, 2) if prob > 0 else 0
        has_value = len(value_bets) > 0 and value_bets[0].get('value_pct', 0) > 2.0
        min_acceptable_odd = round(fair_odd * 0.95, 2)
        
        # DECISÃƒO CLARA
        decision = "APOSTAR" if has_value and market_odd >= min_acceptable_odd else "NÃƒO APOSTAR" if not has_value else "APOSTAR COM CAUTELA"
        
        # Formato DECISÃ“RIO
        recommendation_text = f"""ðŸ“Œ Mercado: {market}
ðŸ“Œ Pick: {pick}
ðŸ“Œ Odd mÃ­nima aceitÃ¡vel: {min_acceptable_odd}
ðŸ“Œ Fair odd calculada: {fair_odd}
ðŸ“Œ Existe valor? {"âœ… SIM" if has_value else "âŒ NÃƒO"}

âž¡ï¸ DECISÃƒO: {decision}"""
        
        bullets = [
            f"Modelo Poisson: xG {poisson.get('expected_goals_home', 0):.2f} x {poisson.get('expected_goals_away', 0):.2f}",
            f"Probabilidade calculada: {prob*100:.1f}% (Fair odd: {fair_odd})",
            f"Odd de mercado: {market_odd:.2f} {'(COM valor)' if has_value else '(SEM valor suficiente)'}"
        ]
        
        # Stake baseada no risco
        if risk == 'low':
            stake = "0.5-1 unidade"
        elif risk == 'medium':
            stake = "1-1.5 unidades"
        else:
            stake = "0.25-0.5 unidade"
        
        risk_warning = f"NÃ­vel de risco: {risk.upper()} | Stake recomendada: {stake}"
        
        # FORMATAÃ‡ÃƒO: CompatÃ­vel com frontend
        formatted = format_analysis_for_frontend(recommendation_text, bullets, risk_warning)
        
        return {
            'success': True,
            'analysis': formatted,
            'reasoning': formatted,  # Campo que modal espera
            'recommendation': recommendation_text,
            'bullets': bullets,
            'risk_warning': risk_warning,
            'generation_time': 0.0,
            'cached': False,
            'fallback': True
        }
    
    def _build_minimal_prompt(self, decision_data: Dict, enriched_data: Dict) -> str:
        """
        Prompt DECISÃ“RIO MULTI-MERCADO (PortuguÃªs) â€“ NÃ­vel trader
        
        Objetivo: gerar recomendaÃ§Ãµes ACIONÃVEIS em mÃºltiplos mercados
        (Over/Under, BTTS, Dupla Chance, 1X2), ordenadas por EV, com
        odd mÃ­nima, pontos de entrada e stake em unidades.
        """
        recommendation = decision_data.get('recommendation', {})
        confidence = decision_data.get('confidence', {})
        risk = decision_data.get('risk', 'medium')
        value_bets = decision_data.get('value_bets', [])
        model_probs = decision_data.get('model_probabilities', {})
        
        # Extrair dados corretamente da estrutura aninhada
        fixture = enriched_data.get('fixture_details', {})
        if isinstance(fixture, dict):
            # API-Football format: fixture.teams.home.name
            teams = fixture.get('teams', {})
            home_team = teams.get('home', {}).get('name', 'Casa') if teams else fixture.get('home_team', {}).get('name', 'Casa')
            away_team = teams.get('away', {}).get('name', 'Fora') if teams else fixture.get('away_team', {}).get('name', 'Fora')
            league_data = fixture.get('league', {})
            league = league_data.get('name', 'N/A') if league_data else 'N/A'
            fixture_data = fixture.get('fixture', {})
            match_date = fixture_data.get('date', 'N/A') if fixture_data else fixture.get('date', 'N/A')
        else:
            home_team = 'Casa'
            away_team = 'Fora'
            league = 'N/A'
            match_date = 'N/A'
        
        # Dados dos modelos
        poisson = model_probs.get('poisson', {})
        consensus = model_probs.get('consensus', {})
        xg_home = poisson.get('expected_goals_home', 0)
        xg_away = poisson.get('expected_goals_away', 0)
        most_likely = poisson.get('most_likely_score', 'N/A')
        
        # Contexto estratÃ©gico
        table_context = enriched_data.get('table_context', {})
        home_table = table_context.get('home', {})
        away_table = table_context.get('away', {})
        motivation = enriched_data.get('motivation', {})
        trends = enriched_data.get('trends', {})
        
        # Identificar se hÃ¡ value bet real
        has_value = len(value_bets) > 0 and value_bets[0].get('value_pct', 0) > 2.0
        primary_value = value_bets[0] if has_value else None
        
        # Calcular fair odd (inverso da probabilidade) para a pick principal
        fair_odd = round(1 / recommendation.get('probability', 0.5), 2) if recommendation.get('probability', 0) > 0 else 0
        market_odd = recommendation.get('odd', 0)
        
        # Determinar odd mÃ­nima aceitÃ¡vel (5% de margem)
        min_acceptable_odd = round(fair_odd * 0.95, 2)
        
        # Stake sugerida baseada em Kelly Criterion simplificado
        if risk == 'low':
            stake_units = "0.5-1 unidade"
        elif risk == 'medium':
            stake_units = "1-1.5 unidades"
        else:
            stake_units = "0.25-0.5 unidade"
        
        # Construir prompt multi-mercado em PortuguÃªs
        prompt = f"""
VocÃª Ã© um sistema profissional de apostas esportivas. Sua tarefa Ã© gerar UMA SAÃDA ÃšNICA, CLARA e ACIONÃVEL em PortuguÃªs (MoÃ§ambique), cobrindo mÃºltiplos mercados com melhor valor esperado (EV), ordenados por prioridade.

REGRAS:
- Sempre priorize mercados com maior EV (Over/Under, BTTS, Dupla Chance, 1X2)
- Para cada aposta, informe: Mercado, Pick, Odd disponÃ­vel, Odd justa (fair), Value %, Stake (em unidades), AÃ§Ã£o (apostar agora / sÃ³ se subir / nÃ£o apostar)
- Inclua pontos de entrada (odd mÃ­nima) e invalidaÃ§Ãµes (quando nÃ£o apostar)
- NÃƒO use HTML/Markdown. NÃƒO seja genÃ©rico. Seja especÃ­fico.

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
ðŸŽ¯ ANÃLISE COMPLETA DE APOSTAS
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

ðŸ† {home_team} vs {away_team}
ðŸ… {league}
ðŸ“… {match_date}
â­ ConfianÃ§a: {confidence.get('stars', 3)}/5 â€¢ Risco: {risk.upper()}

ðŸ“Š Probabilidades (consenso): Casa {consensus.get('home_win', 0)*100:.1f}% | Empate {consensus.get('draw', 0)*100:.1f}% | Fora {consensus.get('away_win', 0)*100:.1f}%
xG esperado: {xg_home:.2f} x {xg_away:.2f} â€¢ Placar provÃ¡vel: {most_likely}

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
ðŸ’° ONDE APOSTAR - MELHORES OPORTUNIDADES
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

Gere atÃ© 3 apostas (ðŸ¥‡, ðŸ¥ˆ, ðŸ¥‰), ordenadas por EV, com este formato:

ðŸ¥‡ APOSTA #1 - MAIOR VALOR (RECOMENDADA)
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ðŸ“Š Mercado: [nome do mercado]
ðŸŽ¯ Aposte em: [pick]
ðŸ’µ Odd disponÃ­vel: [odd]
ðŸ“ˆ Odd justa: [fair_odd]
âœ… Vantagem: [+EV%]
ðŸ’° Stake: {stake_units}

âž¡ï¸ O QUE FAZER:
âœ“ Aposte AGORA se odd â‰¥ [odd_mÃ­nima]
âœ— NÃƒO aposte se odd < [odd_mÃ­nima]

ðŸ“ PORQUÃŠ APOSTAR NISTO?
â€¢ [bullet 1]
â€¢ [bullet 2]
â€¢ [bullet 3]

Inclua tambÃ©m uma seÃ§Ã£o "â›” NÃƒO APOSTE AQUI - SEM VALOR" avaliando 1X2 se nÃ£o houver EV suficiente, explicando porquÃª evitar.

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
ðŸ“‹ RESUMO - O QUE FAZER
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Liste as apostas com odd mÃ­nima e stake.

â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
ðŸš¨ ATENÃ‡ÃƒO - QUANDO NÃƒO APOSTAR
â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
Liste invalidaÃ§Ãµes objetivas (odd abaixo do mÃ­nimo, mudanÃ§as de escalaÃ§Ã£o, etc.).
"""
        
        return prompt
    
    def _extract_confidence(self, text: str) -> int:
        """Extrair nÃ­vel de confianÃ§a da anÃ¡lise de forma robusta"""
        text_lower = text.lower()
        
        # PadrÃµes de busca (ordem: 5 -> 1 para pegar o maior primeiro)
        confidence_patterns = {
            5: ['5 estrelas', 'â˜…â˜…â˜…â˜…â˜…', '5/5', 'cinco estrelas', 'confianÃ§a: 5', 'nÃ­vel: 5', 
                'altÃ­ssima confianÃ§a', 'muito alta', 'excelente'],
            4: ['4 estrelas', 'â˜…â˜…â˜…â˜…', '4/5', 'quatro estrelas', 'confianÃ§a: 4', 'nÃ­vel: 4',
                'alta confianÃ§a', 'muito boa', 'Ã³tima'],
            3: ['3 estrelas', 'â˜…â˜…â˜…', '3/5', 'trÃªs estrelas', 'confianÃ§a: 3', 'nÃ­vel: 3',
                'mÃ©dia confianÃ§a', 'moderada', 'razoÃ¡vel', 'boa'],
            2: ['2 estrelas', 'â˜…â˜…', '2/5', 'duas estrelas', 'confianÃ§a: 2', 'nÃ­vel: 2',
                'baixa confianÃ§a', 'fraca', 'pouca'],
            1: ['1 estrela', 'â˜…', '1/5', 'uma estrela', 'confianÃ§a: 1', 'nÃ­vel: 1',
                'muito baixa', 'mÃ­nima', 'fraquÃ­ssima']
        }
        
        # Verificar padrÃµes na ordem 5->4->3->2->1
        for level in [5, 4, 3, 2, 1]:
            for pattern in confidence_patterns[level]:
                if pattern in text_lower:
                    return level
        
        # Se nenhum padrÃ£o encontrado, tentar detectar sentimento geral
        # Palavras indicativas de alta confianÃ§a
        high_confidence_words = ['certeza', 'definitivamente', 'claramente', 'Ã³bvio', 'forte']
        low_confidence_words = ['talvez', 'possivelmente', 'incerto', 'duvidoso', 'arriscado']
        
        high_count = sum(1 for word in high_confidence_words if word in text_lower)
        low_count = sum(1 for word in low_confidence_words if word in text_lower)
        
        if high_count > low_count:
            return 4  # Alta confianÃ§a implÃ­cita
        elif low_count > high_count:
            return 2  # Baixa confianÃ§a implÃ­cita
        
        # Default: confianÃ§a mÃ©dia
        return 3

