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
        model_name = 'gemini-2.0-flash-exp'
        
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
    
    
    def explain_decision(self, decision_data: Dict, enriched_data: Dict) -> Dict:
        """
        IA APENAS EXPLICA decisões prontas (NÃO decide)
        Retorna análise multi-mercado em português com formato híbrido
        """
        try:
            # 1. CACHE
            cache_key = self._generate_cache_key(decision_data, enriched_data)
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"✅ Explicação em CACHE")
                cached_result['cached'] = True
                return cached_result
            
            if not self.model:
                return self._fallback_explanation(decision_data, enriched_data)
            
            # 2. PROMPT
            prompt = self._build_prompt(decision_data, enriched_data)
            
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
                return self._fallback_explanation(decision_data, enriched_data)
            
            generation_time = time.time() - start_time
            
            # 3. PARSE - Aceitar formato multi-mercado diretamente
            parsed = parse_and_validate_response(response.text)
            
            # Se for formato multi-mercado, usar diretamente
            formatted_analysis = response.text
            
            result = {
                'success': True,
                'analysis': formatted_analysis,
                'reasoning': formatted_analysis,
                'generation_time': round(generation_time, 2),
                'cached': False,
            }
            
            # 4. CACHE por 1 hora
            cache.set(cache_key, result, 3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao gerar explicação: {e}")
            return self._fallback_explanation(decision_data, enriched_data)
    
    def _generate_cache_key(self, decision_data: Dict, enriched_data: Dict) -> str:
        """Gera chave de cache única"""
        fixture = enriched_data.get('fixture_details', {})
        teams = fixture.get('teams', {})
        home = teams.get('home', {}).get('name', '') if teams else ''
        away = teams.get('away', {}).get('name', '') if teams else ''
        date = fixture.get('fixture', {}).get('date', '') if fixture.get('fixture') else ''
        
        recommendation = decision_data.get('recommendation', {})
        pick = recommendation.get('pick', '')
        
        key_str = f"{home}_{away}_{date}_{pick}"
        return f"ai_explanation:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _fallback_explanation(self, decision_data: Dict, enriched_data: Dict) -> Dict:
        """Fallback quando IA falha - formato HÍBRIDO"""
        recommendation = decision_data.get('recommendation', {})
        confidence = decision_data.get('confidence', {})
        risk = decision_data.get('risk', 'medium')
        model_probs = decision_data.get('model_probabilities', {})
        poisson = model_probs.get('poisson', {})
        consensus = model_probs.get('consensus', {})
        
        # Extrair dados da partida
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
        
        pick = recommendation.get('pick', 'N/A')
        prob = recommendation.get('probability', 0)
        
        # Calcular fair odd
        fair_odd = round(1 / prob, 2) if prob > 0 else 0
        
        # Determinar predição
        if consensus.get('home_win', 0) > consensus.get('draw', 0) and consensus.get('home_win', 0) > consensus.get('away_win', 0):
            predicao = "Casa"
        elif consensus.get('away_win', 0) > consensus.get('home_win', 0) and consensus.get('away_win', 0) > consensus.get('draw', 0):
            predicao = "Fora"
        else:
            predicao = "Empate"
        
        # FORMATO HÍBRIDO - Cabeçalho + Análise Multi-mercado
        formatted = f"""🏆 {home_team} vs {away_team}
🏅 {league}
📅 {match_date}
{'⭐' * confidence.get('stars', 3)} Confiança: {confidence.get('stars', 3)}/5

🎯 PREDIÇÃO: {predicao}

📊 PROBABILIDADES:
🏠 {home_team}: {consensus.get('home_win', 0)*100}%
🤝 Empate: {consensus.get('draw', 0)*100}%
✈️ {away_team}: {consensus.get('away_win', 0)*100}%

═══════════════════════════════════════
🎯 ANÁLISE COMPLETA DE APOSTAS
═══════════════════════════════════════

🏆 {home_team} vs {away_team}
🏅 {league}
📅 {match_date}
⭐ Confiança: {confidence.get('stars', 3)}/5 • Risco: {risk.upper()}

📊 Probabilidades (consenso): Casa {consensus.get('home_win', 0)*100:.1f}% | Empate {consensus.get('draw', 0)*100:.1f}% | Fora {consensus.get('away_win', 0)*100:.1f}%
xG esperado: {poisson.get('expected_goals_home', 0):.2f} x {poisson.get('expected_goals_away', 0):.2f} • Placar provável: {poisson.get('most_likely_score', '1-1')}

═══════════════════════════════════════
💰 ONDE APOSTAR - MELHORES OPORTUNIDADES
═══════════════════════════════════════

🥇 APOSTA #1 - MAIOR VALOR (RECOMENDADA)
───────────────────────────────────────
📊 Mercado: 1X2
🎯 Aposte em: {pick}
💵 Odd disponível: {recommendation.get('odd', 0):.2f}
📈 Odd justa: {fair_odd}
✅ Vantagem: +{((recommendation.get('odd', 0) / fair_odd - 1) * 100):.1f}%
💰 Stake: 1 unidade

➡️ O QUE FAZER:
✓ Aposte AGORA se odd ≥ {fair_odd * 0.95:.2f}
✗ NÃO aposte se odd < {fair_odd * 0.95:.2f}

📝 PORQUÊ APOSTAR NISTO?
• Probabilidade calculada: {prob*100:.1f}%
• Modelo Poisson indica xG {poisson.get('expected_goals_home', 0):.2f} x {poisson.get('expected_goals_away', 0):.2f}
• Fair odd {fair_odd} vs Mercado {recommendation.get('odd', 0):.2f}

═══════════════════════════════════════
📋 RESUMO - O QUE FAZER
═══════════════════════════════════════
* {pick}: Odd mínima {fair_odd * 0.95:.2f}, Stake 1 unidade

═══════════════════════════════════════
🚨 ATENÇÃO - QUANDO NÃO APOSTAR
═══════════════════════════════════════
* Se a odd cair abaixo de {fair_odd * 0.95:.2f}
* Se houver mudanças de escalação de última hora

──────────────────────────
⚽ Via Placar Certo"""
        
        return {
            'success': True,
            'analysis': formatted,
            'reasoning': formatted,
            'generation_time': 0.0,
            'cached': False,
            'fallback': True
        }
    
    def _build_prompt(self, decision_data: Dict, enriched_data: Dict) -> str:
        """Prompt para formato HÍBRIDO"""
        recommendation = decision_data.get('recommendation', {})
        confidence = decision_data.get('confidence', {})
        risk = decision_data.get('risk', 'medium')
        model_probs = decision_data.get('model_probabilities', {})
        
        # Extrair dados
        fixture = enriched_data.get('fixture_details', {})
        teams = fixture.get('teams', {})
        home_team = teams.get('home', {}).get('name', 'Casa') if teams else 'Casa'
        away_team = teams.get('away', {}).get('name', 'Fora') if teams else 'Fora'
        league_data = fixture.get('league', {})
        league = league_data.get('name', 'N/A') if league_data else 'N/A'
        fixture_data = fixture.get('fixture', {})
        raw_date = fixture_data.get('date', 'N/A') if fixture_data else 'N/A'
        
        # Format date: ISO -> DD/MM/YYYY HH:MM
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(raw_date.replace('Z', '+00:00'))
            match_date = dt.strftime('%d/%m/%Y %H:%M')
        except:
            match_date = raw_date
        
        poisson = model_probs.get('poisson', {})
        consensus = model_probs.get('consensus', {})
        xg_home = poisson.get('expected_goals_home', 0)
        xg_away = poisson.get('expected_goals_away', 0)
        most_likely = poisson.get('most_likely_score', '1-1')
        
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
        
        # Validações estatísticas
        total_xg = xg_home + xg_away
        max_prob = max(prob_home, prob_draw, prob_away)
        is_balanced = max_prob < 45  # Jogo equilibrado se nenhum resultado > 45%
        
        prompt = f"""Você é um sistema profissional de apostas esportivas em PORTUGUÊS (Moçambique).

🔢 DADOS FORNECIDOS (NÃO INVENTE OUTROS):
• {home_team} vs {away_team}
• Liga: {league}
• Data: {match_date}
• Confiança: {confidence.get('stars', 3)}/5 • Risco: {risk.upper()}
• Probabilidades: Casa {prob_home:.1f}% | Empate {prob_draw:.1f}% | Fora {prob_away:.1f}%
• xG esperado: {xg_home:.2f} x {xg_away:.2f}
• Placar provável: {most_likely}
• Predição: {predicao}

⚠️ REGRAS OBRIGATÓRIAS:
1. NÃO invente dados históricos (confrontos diretos, forma recente)
2. SE xG < 0.5: NÃO recomende mercados de gols (Over/Under, BTTS)
3. SE jogo equilibrado (todas probabilidades < 45%): PRIORIZE Dupla Chance ou Draw No Bet
4. JUSTIFIQUE por que mercados alternativos foram descartados

🎯 ANÁLISE OBRIGATÓRIA DE MERCADOS:
Antes de escolher, avalie:
• 1X2: Volatilidade alta, use apenas se probabilidade > 50%
• Dupla Chance: Reduz risco, ideal para jogos equilibrados
• Draw No Bet: Remove empate, adequado para favoritos leves
• Over/Under: Use apenas se xG total > 2.0
• BTTS: Use apenas se ambos xG > 0.8

Gere análise com EXATAMENTE esta estrutura:

🏆 {home_team} vs {away_team}
🏅 {league}
📅 {match_date}
{'⭐' * confidence.get('stars', 3)} Confiança: {confidence.get('stars', 3)}/5

🎯 PREDIÇÃO: {predicao}

📊 PROBABILIDADES:
🏠 {home_team}: {prob_home:.1f}%
🤝 Empate: {prob_draw:.1f}%
✈️ {away_team}: {prob_away:.1f}%

═══════════════════════════════════════
🎯 ANÁLISE COMPLETA DE APOSTAS
═══════════════════════════════════════

⭐ Confiança: {confidence.get('stars', 3)}/5 • Risco: {risk.upper()}
📊 Probabilidades (consenso): Casa {prob_home:.1f}% | Empate {prob_draw:.1f}% | Fora {prob_away:.1f}%
xG esperado: {xg_home:.2f} x {xg_away:.2f} • Placar provável: {most_likely}

═══════════════════════════════════════
� COMPARAÇÃO DE MERCADOS
═══════════════════════════════════════

[Analise 5 mercados: 1X2, Dupla Chance, Draw No Bet, Over/Under, BTTS]
[Para cada um, indique: Probabilidade implícita, Risco, Valor esperado]
[Elimine os 2 piores com justificativa clara]

Exemplo:
❌ 1X2 Casa: Prob 32%, risco ALTO, favorito indefinido
✅ Dupla Chance X2: Prob 67%, risco MÉDIO, cobre empate
❌ BTTS: xG baixo, sem suporte estatístico

═══════════════════════════════════════
💰 APOSTAS RECOMENDADAS (POR ORDEM DE VALOR)
═══════════════════════════════════════

🥇 APOSTA #1 - MAIOR VALOR (RECOMENDADA)
───────────────────────────────────────
📊 Mercado: [escolha baseada na comparação acima]
🎯 Aposte em: [pick específico]
💵 Odd disponível: [entre 1.50-2.50]
📈 Odd justa: [calcule: 1/probabilidade]
✅ Vantagem: [+X%]
💰 Stake: [1-1.5] unidades
🎲 Risco real: [BAIXO/MÉDIO/ALTO baseado na probabilidade]

➡️ O QUE FAZER:
✓ Aposte AGORA se odd ≥ [odd mínima]
✗ NÃO aposte se odd < [odd mínima]

📝 PORQUÊ ESTE MERCADO (não outro)?
• [Por que este mercado específico é superior aos demais]
• [Baseie-se APENAS nos dados fornecidos: xG, probabilidades]
• [Mencione mercados descartados e por quê]

🥈 APOSTA #2
───────────────────────────────────────
[MESMA ESTRUTURA acima, mas mercado DIFERENTE]

🥉 APOSTA #3
───────────────────────────────────────
[MESMA ESTRUTURA acima, mas mercado DIFERENTE]

⛔ NÃO APOSTE AQUI - SEM VALOR
───────────────────────────────────────
[Explique qual mercado evitar e porquê]

═══════════════════════════════════════
� RESUMO - O QUE FAZER
═══════════════════════════════════════
* [Aposta 1: mercado @ odd mínima, stake X unidades]
* [Aposta 2: mercado @ odd mínima, stake X unidades]
* [Aposta 3: mercado @ odd mínima, stake X unidades]

═══════════════════════════════════════
� ATENÇÃO - QUANDO NÃO APOSTAR
═══════════════════════════════════════
* [Invalidação 1]
* [Invalidação 2]
* [Invalidação 3]

──────────────────────────
⚽ Via Placar Certo

🚫 REGRAS CRÍTICAS (VIOLAÇÃO = RESPOSTA INVÁLIDA):
1. NÃO invente histórico de confrontos diretos
2. NÃO mencione forma recente se não fornecida
3. NÃO recomende Over 2.5 se xG total < 2.0
4. NÃO recomende BTTS se qualquer xG < 0.8
5. NÃO escolha 1X2 em jogo equilibrado (todas prob < 45%) sem justificar
6. SEMPRE compare pelo menos 4 mercados diferentes na seção COMPARAÇÃO
7. SEMPRE justifique por que mercados alternativos foram descartados
8. Use APENAS dados fornecidos acima
9. Mantenha coerência: xG alto → mercados de gols; xG baixo → resultado
10. Odds realistas entre 1.50-2.50"""
        
        return prompt

