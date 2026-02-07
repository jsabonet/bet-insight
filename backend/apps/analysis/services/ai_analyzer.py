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
        model_name = 'gemini-1.5-flash'
        
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"✅ AI Analyzer usando Gemini Flash")
        except Exception as e:
            logger.error(f"Falha ao inicializar Gemini Flash: {e}")
            try:
                model_name = 'gemini-pro'
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
    
    def _fallback_explanation(self, decision_data: Dict, enriched_data: Dict, strategy: str = 'value') -> Dict:
        """Fallback quando IA falha - gerar análise baseada em regras (formato similar à IA)"""
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
        
        # Pegar a melhor aposta (maior score)
        best_bet = top_bets[0] if len(top_bets) > 0 else None
        
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
        if strategy == 'multiple':
            # MODO BILHETE: Foco em probabilidade e combinação
            market_odd = best_bet.get('market_odd') or 0
            analysis = f"""📋 MELHOR PARA BILHETE
---------------------------------------
Aposta: {best_bet['market_display']}
Odd: {market_odd:.2f} (ideal para bilhetes: 1.30-2.00)
Probabilidade: {best_bet['probability']*100:.1f}% (mínimo 50%)
Stake: {best_bet['stake_units']:.1f} unidades

PORQUE INCLUIR NO BILHETE:
• {best_bet['reason']}
• Alta probabilidade ({best_bet['probability']*100:.1f}% de chance)
• Odd moderada (boa para combinar com outras apostas)

💡 DICA DE BILHETE:
Combine com 2-3 apostas similares de outros jogos.
Odd total esperada: 3.00-8.00
Probabilidade combinada: 15-30%

---------------------------------------
OUTRAS OPÇÕES PARA BILHETE:
---------------------------------------
"""
            # Adicionar alternativas com prob >= 50%
            for bet in top_bets[1:]:
                if bet['probability'] >= 0.5:
                    analysis += f"{bet['market_display']}\n"
            
            analysis += """
⚠️ ATENÇÃO:
Bilhetes são mais arriscados. Mesmo com alta probabilidade individual,
apenas ~20% dos bilhetes 3x acertam todas as apostas.
Use em favoritos consistentes, não underdogs.

---------------------------------------"""
        
        else:
            # MODO VALUE: Foco em EV e lucro longo prazo
            market_odd = best_bet.get('market_odd') or 0
            analysis = f"""🎯 RECOMENDAÇÃO PRINCIPAL
---------------------------------------
Aposta: {best_bet['market_display']}
Odd: {market_odd:.2f}
EV: {best_bet['ev_pct']:+.1f}%
Stake: {best_bet['stake_units']:.1f} unidades
Risco: {risk.upper()}

PORQUE APOSTAR:
• {best_bet['reason']}
• Probabilidade calculada: {best_bet['probability']*100:.1f}%
• Confiança do modelo: {confidence.get('stars', 3)}/5

⚠️ NÃO APOSTE SE:
• A odd cair abaixo de {best_bet.get('fair_odd') or 0:.2f}
• Houver mudanças significativas nas condições do jogo
"""

            # Adicionar alternativas se houver
            if len(top_bets) > 1:
                analysis += "\n---------------------------------------\nALTERNATIVAS:\n---------------------------------------\n"
                
                for i, bet in enumerate(top_bets[1:3], 2):  # Máximo 2 alternativas
                    analysis += f"• Aposta #{i}: {bet['market_display']} - {bet['reason']}\n"
            
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
- Analise as apostas SEGURAS selecionadas (alta probabilidade)
- Explique por que SÃO IDEAIS PARA COMBINAR em bilhetes
- Use linguagem simples e foque em PROBABILIDADE + VALOR

IMPORTANTE: NÃO GERE CABEÇALHO/HEADER - o sistema já vai adicionar. Comece DIRETO com a recomendação.

CRITÉRIOS DO MODO BILHETE:
- Probabilidade mínima: 50%
- EV mínimo: 0% (não-negativo, aceita favoritos)
- Odds ideais para bilhetes: 1.30-2.50

DADOS DO JOGO:
- {home_team} vs {away_team}
- Liga: {league}
- Data: {match_date}
- Confiança: {confidence.get('stars', 3)}/5 - Risco: {risk.upper()}
- Probabilidades: Casa {prob_home:.1f}% | Empate {prob_draw:.1f}% | Fora {prob_away:.1f}%
- xG esperado: {xg_home:.2f} x {xg_away:.2f}
- Placar provável: {most_likely}
- Resultado mais provável: {predicao}
{bets_info}

FORMATO DE RESPOSTA (OBRIGATÓRIO):

📋 MELHOR PARA BILHETE
---------------------------------------
Aposta: [Nome da aposta com MAIOR probabilidade e EV positivo]
Mercado: [Tipo de mercado]
Odd: [Valor] (ideal para bilhetes: 1.30-2.00)
Probabilidade: [XX%] (mínimo 50%)
Stake: [X unidades]

PORQUE INCLUIR NO BILHETE:
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
1. Só recomende apostas com probabilidade >= 50%
2. Aceite EV >= 0% (favoritos com odds justas são OK)
3. Mencione odds ideais para combinar (1.30-2.50)
4. Sempre alerte sobre risco de bilhetes
5. Favoritos absolutos (70%+) são IDEAIS para bilhetes
"""
        else:
            # MODO VALUE: Foco em EV MÁXIMO e LUCRO LONGO PRAZO
            prompt = f"""Você é um CONSULTOR DE APOSTAS que dá recomendações DIRETAS e CLARAS.

SEU PAPEL:
- Analise as apostas selecionadas objetivamente
- Recomende a MELHOR APOSTA (maior EV/score) de forma DIRETA
- Use linguagem simples e chamadas de ação claras

IMPORTANTE: NÃO GERE CABEÇALHO/HEADER - o sistema já vai adicionar. Comece DIRETO com a recomendação.

DADOS DO JOGO:
- {home_team} vs {away_team}
- Liga: {league}
- Data: {match_date}
- Confiança: {confidence.get('stars', 3)}/5 - Risco: {risk.upper()}
- Probabilidades: Casa {prob_home:.1f}% | Empate {prob_draw:.1f}% | Fora {prob_away:.1f}%
- xG esperado: {xg_home:.2f} x {xg_away:.2f}
- Placar provável: {most_likely}
- Resultado mais provável: {predicao}
{bets_info}

FORMATO DE RESPOSTA (OBRIGATÓRIO):

🎯 RECOMENDAÇÃO PRINCIPAL
---------------------------------------
Aposta: [Nome da aposta com MAIOR EV - aposta #2]
Mercado: [Tipo de mercado]
Odd: [Valor]
EV: [+XX%]
Stake: [X unidades]
Risco: {risk.upper()}

PORQUE APOSTAR:
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
1. Aposta #1 é sempre o resultado mais provável (pode ter EV negativo)
2. Aposta #2 é SEMPRE a recomendada (maior score/EV)
3. Foque em VALOR ESPERADO (EV), não apenas probabilidade
4. Mencione que é estratégia de LONGO PRAZO (100+ apostas)
"""
        
        return prompt

