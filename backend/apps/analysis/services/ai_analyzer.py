"""
Serviço de análise com Google Gemini AI
Gera análises preditivas e recomendações de apostas
"""
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from django.conf import settings
from typing import Dict
import logging
import json

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Serviço de análise com IA (Google Gemini)"""
    
    def __init__(self):
        api_key = settings.GOOGLE_GEMINI_API_KEY
        if not api_key:
            logger.error("Chave da API do Gemini não configurada.")
            # Inicializa um modelo nulo para evitar crashes; chamadas retornarão erro estruturado
            self.model = None
            return

        genai.configure(api_key=api_key)
        
        # MIGRAÇÃO PARA GEMINI FLASH (4x mais rápido, 75% mais barato)
        model_name = 'gemini-2.0-flash-exp'
        
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"✅ AI Analyzer usando Gemini Flash (rápido e eficiente)")
        except Exception as e:
            logger.error(f"Falha ao inicializar Gemini Flash: {e}")
            # Fallback para modelo anterior
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
        NOVA FUNÇÃO: IA apenas EXPLICA decisões prontas (não decide)
        
        Args:
            decision_data (dict): Decisão do DecisionEngine com:
                - recommendation: {...}
                - confidence: {...}
                - risk: str
                - value_bets: [...]
                - model_probabilities: {...}
            enriched_data (dict): Dados enriquecidos da partida
        
        Returns:
            dict: {
                'success': bool,
                'analysis': str (HTML formatado),
                'generation_time': float,
                'model': str
            }
        """
        try:
            if not self.model:
                return {
                    'success': False,
                    'error': 'API key do Gemini não configurada.',
                    'error_code': 'API_KEY_MISSING'
                }
            
            # Construir prompt CURTO focado em explicar
            prompt = self._build_explanation_prompt(decision_data, enriched_data)
            
            home_name = enriched_data.get('fixture_details', {}).get('home_team', {}).get('name', 'Casa')
            away_name = enriched_data.get('fixture_details', {}).get('away_team', {}).get('name', 'Fora')
            
            logger.info(f"🤖 IA Explicando decisão: {home_name} vs {away_name}")
            
            # Gerar com timeout curto e temperatura baixa
            import time
            start_time = time.time()
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.3,  # Baixa criatividade (mais factual)
                    'max_output_tokens': 1500,  # Limite menor
                    'top_p': 0.8,
                    'top_k': 40
                }
            )
            
            generation_time = time.time() - start_time
            
            logger.info(f"✅ Explicação gerada em {generation_time:.2f}s")
            
            return {
                'success': True,
                'analysis': response.text,
                'generation_time': round(generation_time, 2),
                'model': 'gemini-2.0-flash',
                'tokens_used': len(prompt.split()) + len(response.text.split())
            }
            
        except google_exceptions.ResourceExhausted as e:
            logger.error(f"Quota da API Gemini excedida: {e}")
            return {
                'success': False,
                'error': 'Limite diário de análises da API foi atingido.',
                'error_code': 'QUOTA_EXCEEDED',
                'http_status': 429
            }
        except Exception as e:
            logger.error(f"Erro ao gerar explicação: {e}")
            return {
                'success': False,
                'error': f'Erro ao gerar análise: {str(e)}',
                'error_code': 'GENERATION_ERROR'
            }
    
    def _build_explanation_prompt(self, decision_data, enriched_data):
        """
        Constrói prompt CURTO para IA explicar (não decidir)
        
        ANTES: 8.000 tokens (dados brutos)
        AGORA: ~1.500 tokens (decisões prontas)
        """
        recommendation = decision_data.get('recommendation', {})
        confidence = decision_data.get('confidence', {})
        risk = decision_data.get('risk', 'medium')
        value_bets = decision_data.get('value_bets', [])
        model_probs = decision_data.get('model_probabilities', {})
        
        fixture = enriched_data.get('fixture_details', {})
        home_team = fixture.get('home_team', {}).get('name', 'Casa')
        away_team = fixture.get('away_team', {}).get('name', 'Fora')
        
        poisson = model_probs.get('poisson', {})
        consensus = model_probs.get('consensus', {})
        
        prompt = f"""Você é um analista de apostas esportivas profissional. Explique a análise abaixo de forma clara e objetiva.

═══════════════════════════════════════
🏆 PARTIDA
═══════════════════════════════════════
{home_team} (Casa) vs {away_team} (Fora)

═══════════════════════════════════════
📊 DECISÃO DOS MODELOS ESTATÍSTICOS
═══════════════════════════════════════

**RECOMENDAÇÃO PRINCIPAL:**
{recommendation.get('market_display', 'N/A')} - {recommendation.get('pick', 'N/A')}

**PROBABILIDADE:** {recommendation.get('probability', 0)*100:.1f}%
**ODD MERCADO:** {recommendation.get('odd', 0):.2f}
**CONFIANÇA:** {'⭐' * confidence.get('stars', 3)} ({confidence.get('level_pt', 'Média')})
**RISCO:** {risk.upper()}

═══════════════════════════════════════
🔢 MODELO POISSON (DISTRIBUIÇÃO DE GOLS)
═══════════════════════════════════════

Gols esperados:
• Casa: {poisson.get('expected_goals_home', 0):.2f}
• Fora: {poisson.get('expected_goals_away', 0):.2f}

Placar mais provável: {poisson.get('most_likely_score', 'N/A')}

Probabilidades de resultado:
• Vitória Casa: {consensus.get('home_win', 0)*100:.1f}%
• Empate: {consensus.get('draw', 0)*100:.1f}%
• Vitória Fora: {consensus.get('away_win', 0)*100:.1f}%

Mercados adicionais:
• Over 2.5 gols: {poisson.get('probabilities', {}).get('over_2_5', 0)*100:.1f}%
• Ambos Marcam: {poisson.get('probabilities', {}).get('btts', 0)*100:.1f}%

═══════════════════════════════════════
💰 ANÁLISE DE VALUE
═══════════════════════════════════════
"""
        
        if value_bets:
            prompt += "✅ VALUE BETS IDENTIFICADOS:\n\n"
            for vb in value_bets[:3]:
                prompt += f"  • {vb['market_display']}: {vb['value_pct']:.1f}% de value\n"
                prompt += f"    Odd justa: {vb['fair_odd']:.2f} | Odd mercado: {vb['market_odd']:.2f}\n"
                prompt += f"    Sugestão: {vb['stake_suggestion']}\n\n"
        else:
            prompt += "⚠️ Nenhum value bet significativo identificado.\n"
            prompt += "Odds do mercado estão alinhadas com as probabilidades dos modelos.\n\n"
        
        prompt += f"""
═══════════════════════════════════════
📝 SUA TAREFA
═══════════════════════════════════════

Com base nesses DADOS OBJETIVOS DOS MODELOS, crie uma análise seguindo EXATAMENTE esta estrutura:

### 🎯 PREVISÃO DO MODELO

[Repita a recomendação de forma clara e direta]

### ⚡ POR QUE ESSA PREVISÃO?

[Explique em 3-4 bullets curtos os principais motivos baseados nos dados acima.
NÃO invente informações. Use APENAS os números fornecidos.]

### 📊 PROBABILIDADES

[Mostre as 3 probabilidades principais de forma visual com barras ou emojis]

### 💰 OPORTUNIDADES

[Se há value bets: explique qual e por quê
Se não há: explique que odds estão justas]

### ⚠️ GESTÃO DE RISCO

[Mencione o nível de risco ({risk}) e o que isso significa
Dê 1-2 conselhos de gestão de banca]

**IMPORTANTE:**
- NÃO invente dados ou estatísticas
- Use APENAS os números fornecidos acima
- Seja objetivo e profissional
- Máximo 400 palavras
- Formato HTML simples (<h3>, <p>, <ul>, <strong>)
"""
        
        return prompt
    
    def analyze_match(self, match_data: Dict) -> Dict:
        """
        Analisa uma partida e retorna predição
        
        match_data deve conter:
        - home_team: {'name': str, 'stats': dict}
        - away_team: {'name': str, 'stats': dict}
        - h2h: list de resultados anteriores
        - league: str
        - date: str
        """
        logger.info(f"\n{'🔵'*40}")
        logger.info(f"🤖 AI ANALYZER: Iniciando análise completa")
        logger.info(f"{'🔵'*40}\n")
        
        logger.info(f"📊 Dados recebidos:")
        logger.info(f"   Home Team: {match_data.get('home_team', {}).get('name', 'N/A')}")
        logger.info(f"   Away Team: {match_data.get('away_team', {}).get('name', 'N/A')}")
        logger.info(f"   League: {match_data.get('league', 'N/A')}")
        logger.info(f"   Date: {match_data.get('date', 'N/A')}")
        
        try:
            if not self.model:
                return {
                    'success': False,
                    'error': 'API key do Gemini não configurada.',
                    'error_code': 'API_KEY_MISSING',
                    'http_status': 400
                }
            prompt = self._build_analysis_prompt(match_data)
            logger.info(f"Analisando: {match_data.get('home_team', {}).get('name')} vs {match_data.get('away_team', {}).get('name')}")
            
            try:
                response = self.model.generate_content(prompt)
            except google_exceptions.ResourceExhausted as e:
                # Erro 429 - Quota excedida (rate limit)
                logger.error(f"Quota da API Gemini excedida: {e}")
                return {
                    'success': False,
                    'error': 'Limite diário de análises da API foi atingido. Tente novamente mais tarde.',
                    'error_code': 'QUOTA_EXCEEDED',
                    'details': str(e),
                    'http_status': 429
                }
            except google_exceptions.NotFound as e:
                logger.error(f"Modelo do Gemini não encontrado/sem suporte: {e}")
                return {
                    'success': False,
                    'error': 'Modelo do Gemini não encontrado ou sem suporte para generateContent.',
                    'error_code': 'MODEL_NOT_FOUND',
                    'details': str(e),
                    'http_status': 404
                }
            
            return {
                'success': True,
                'analysis': response.text,
                'confidence': self._extract_confidence(response.text)
            }
        except google_exceptions.InvalidArgument as e:
            # Erros de chave inválida/expirada retornam como InvalidArgument (400)
            logger.error(f"Erro na análise (API key inválida/expirada): {e}")
            return {
                'success': False,
                'error': 'API key do Gemini inválida ou expirada. Atualize a chave.',
                'error_code': 'API_KEY_INVALID',
                'details': str(e),
                'http_status': 400
            }
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            return {
                'success': False,
                'error': 'Falha ao gerar a análise. Tente novamente mais tarde.',
                'details': str(e),
                'http_status': 500
            }
    
    def _build_analysis_prompt(self, data: Dict) -> str:
        """Construir prompt para análise com dados enriquecidos"""
        # LOG DETALHADO: Ver exatamente o que está chegando
        logger.info("="*80)
        logger.info("🔍 DADOS RECEBIDOS PARA ANÁLISE:")
        logger.info(f"📋 Chaves disponíveis: {list(data.keys())}")
        logger.info(f"📊 Tem statistics? {bool(data.get('statistics'))}")
        logger.info(f"🎲 Tem predictions? {bool(data.get('predictions'))}")
        logger.info(f"⚽ Tem fixture_details? {bool(data.get('fixture_details'))}")
        logger.info(f"📜 Tem H2H? {bool(data.get('h2h'))}")
        logger.info(f"🔵 Tem Football-Data match? {bool(data.get('football_data_match'))}")
        logger.info(f"🆔 API ID usado? {data.get('api_id', 'NÃO')}")
        
        if data.get('statistics'):
            logger.info(f"📈 Estatísticas: {len(data['statistics'])} times")
        if data.get('predictions'):
            logger.info(f"🎯 Previsões encontradas: {list(data['predictions'].keys())[:5]}")
        if data.get('fixture_details'):
            logger.info(f"⚽ Fixture: {list(data['fixture_details'].keys())[:5]}")
        logger.info("="*80)
        
        home = data.get('home_team', {}).get('name', 'Time A')
        away = data.get('away_team', {}).get('name', 'Time B')
        league = data.get('league', 'Liga')
        date = data.get('date', 'Data não disponível')
        status = data.get('status', 'scheduled')
        venue = data.get('venue', 'Estádio não informado')
        
        prompt = f"""
Você é um especialista em análise de apostas de futebol com 20 anos de experiência. Analise esta partida em detalhes:

═══════════════════════════════════════
📊 INFORMAÇÕES DA PARTIDA
═══════════════════════════════════════
🏟️ **{home}** vs **{away}**
🏆 Liga: {league}
📅 Data: {date}
📍 Local: {venue}
⚽ Status: {status}
"""
        
        # Adicionar placar se disponível (partida em andamento ou finalizada)
        home_score = data.get('home_score')
        away_score = data.get('away_score')
        if home_score is not None and away_score is not None:
            prompt += f"\n🎯 Placar: {home} {home_score} x {away_score} {away}\n"
        
        # 🔥 NOVO: Adicionar dados enriquecidos
        table_context = data.get('table_context')
        if table_context:
            prompt += "\n═══════════════════════════════════════\n"
            prompt += "📊 POSIÇÃO NA TABELA\n"
            prompt += "═══════════════════════════════════════\n"
            home_table = table_context.get('home', {})
            away_table = table_context.get('away', {})
            prompt += f"🏠 {home}: {home_table.get('position')}º lugar, {home_table.get('points')} pts (Saldo: {home_table.get('goal_difference')})\n"
            prompt += f"   Forma: {home_table.get('form', 'N/A')} | Casa: {home_table.get('home_record', 'N/A')}\n"
            prompt += f"✈️ {away}: {away_table.get('position')}º lugar, {away_table.get('points')} pts (Saldo: {away_table.get('goal_difference')})\n"
            prompt += f"   Forma: {away_table.get('form', 'N/A')} | Fora: {away_table.get('away_record', 'N/A')}\n"
        
        # Adicionar lesões
        injuries = data.get('injuries')
        if injuries and (injuries.get('home') or injuries.get('away')):
            prompt += "\n═══════════════════════════════════════\n"
            prompt += "🚑 LESÕES E SUSPENSÕES\n"
            prompt += "═══════════════════════════════════════\n"
            home_injuries = injuries.get('home', [])
            away_injuries = injuries.get('away', [])
            if home_injuries:
                prompt += f"🏠 {home}: {len(home_injuries)} ausências\n"
                for injury in home_injuries[:3]:  # Top 3
                    prompt += f"   • {injury.get('player')} - {injury.get('reason')} ({injury.get('type')})\n"
            if away_injuries:
                prompt += f"✈️ {away}: {len(away_injuries)} ausências\n"
                for injury in away_injuries[:3]:  # Top 3
                    prompt += f"   • {injury.get('player')} - {injury.get('reason')} ({injury.get('type')})\n"
        
        # Adicionar odds
        odds = data.get('odds')
        if odds:
            prompt += "\n═══════════════════════════════════════\n"
            prompt += "💰 ODDS DAS CASAS DE APOSTAS\n"
            prompt += "═══════════════════════════════════════\n"
            prompt += f"🏠 Vitória {home}: {odds.get('home_win', 'N/A')}\n"
            prompt += f"🤝 Empate: {odds.get('draw', 'N/A')}\n"
            prompt += f"✈️ Vitória {away}: {odds.get('away_win', 'N/A')}\n"
            if odds.get('over_25'):
                prompt += f"📊 Over 2.5: {odds.get('over_25')} | Under 2.5: {odds.get('under_25')}\n"
            if odds.get('btts_yes'):
                prompt += f"⚽ Ambos Marcam: Sim {odds.get('btts_yes')} | Não {odds.get('btts_no')}\n"
            prompt += "\n💡 Use as odds para calibrar probabilidades e identificar onde o mercado está precificando valor.\n"
        
        # Adicionar estatísticas detalhadas dos times
        home_stats = data.get('home_stats')
        away_stats = data.get('away_stats')
        if home_stats or away_stats:
            prompt += "\n═══════════════════════════════════════\n"
            prompt += "📈 ESTATÍSTICAS DETALHADAS DOS TIMES\n"
            prompt += "═══════════════════════════════════════\n"
            if home_stats:
                prompt += f"🏠 {home} ({home_stats.get('games_played', 0)} jogos):\n"
                goals_avg = float(home_stats.get('goals_per_game_avg', 0) or 0)
                conceded_avg = float(home_stats.get('goals_conceded_avg', 0) or 0)
                prompt += f"   • Média gols marcados: {goals_avg:.2f}/jogo\n"
                prompt += f"   • Média gols sofridos: {conceded_avg:.2f}/jogo\n"
                prompt += f"   • Clean sheets: {home_stats.get('clean_sheets', 0)}\n"
                streak = home_stats.get('biggest_streak', {})
                prompt += f"   • Maior sequência: {streak.get('wins', 0)}V, {streak.get('draws', 0)}E, {streak.get('loses', 0)}D\n"
            if away_stats:
                prompt += f"✈️ {away} ({away_stats.get('games_played', 0)} jogos):\n"
                goals_avg = float(away_stats.get('goals_per_game_avg', 0) or 0)
                conceded_avg = float(away_stats.get('goals_conceded_avg', 0) or 0)
                prompt += f"   • Média gols marcados: {goals_avg:.2f}/jogo\n"
                prompt += f"   • Média gols sofridos: {conceded_avg:.2f}/jogo\n"
                prompt += f"   • Clean sheets: {away_stats.get('clean_sheets', 0)}\n"
                streak = away_stats.get('biggest_streak', {})
                prompt += f"   • Maior sequência: {streak.get('wins', 0)}V, {streak.get('draws', 0)}E, {streak.get('loses', 0)}D\n"
        
        # Adicionar contexto da temporada
        season_context = data.get('season_context')
        if season_context:
            prompt += "\n═══════════════════════════════════════\n"
            prompt += "📅 CONTEXTO DA TEMPORADA\n"
            prompt += "═══════════════════════════════════════\n"
            prompt += f"🏆 Temporada: {season_context.get('season')} | Rodada: {season_context.get('round')}\n"
            prompt += f"📍 Fase: {season_context.get('stage', 'mid').title()} (início, meio ou final)\n"
        
        # 🔥 NOVO: Adicionar tendências Over/Under e BTTS
        trends = data.get('trends')
        if trends and trends.get('home', {}).get('games_analyzed', 0) > 0:
            prompt += "\n═══════════════════════════════════════\n"
            prompt += "📊 TENDÊNCIAS DE MERCADO (Últimos 10 jogos)\n"
            prompt += "═══════════════════════════════════════\n"
            home_trends = trends.get('home', {})
            away_trends = trends.get('away', {})
            prompt += f"🏠 {home} ({home_trends.get('games_analyzed', 0)} jogos):\n"
            prompt += f"   • Over 2.5 gols: {home_trends.get('over_25_pct', 0):.0f}% dos jogos\n"
            prompt += f"   • Ambos Marcam (BTTS): {home_trends.get('btts_pct', 0):.0f}% dos jogos\n"
            prompt += f"✈️ {away} ({away_trends.get('games_analyzed', 0)} jogos):\n"
            prompt += f"   • Over 2.5 gols: {away_trends.get('over_25_pct', 0):.0f}% dos jogos\n"
            prompt += f"   • Ambos Marcam (BTTS): {away_trends.get('btts_pct', 0):.0f}% dos jogos\n"
            if 'combined_over_25_pct' in trends:
                prompt += f"\n💡 Probabilidade combinada Over 2.5: {trends['combined_over_25_pct']:.0f}%\n"
                prompt += f"💡 Probabilidade combinada BTTS: {trends['combined_btts_pct']:.0f}%\n"
        
        # 🔥 NOVO: Adicionar contexto de descanso
        rest_context = data.get('rest_context')
        if rest_context and rest_context.get('home_days_rest') is not None:
            prompt += "\n═══════════════════════════════════════\n"
            prompt += "⏱️ DESCANSO ENTRE JOGOS\n"
            prompt += "═══════════════════════════════════════\n"
            home_rest = rest_context.get('home_days_rest')
            away_rest = rest_context.get('away_days_rest')
            advantage = rest_context.get('advantage', 'equal')
            prompt += f"🏠 {home}: {home_rest} dias de descanso\n"
            prompt += f"✈️ {away}: {away_rest} dias de descanso\n"
            if advantage == 'home':
                prompt += f"📊 Vantagem física: {home} (mais descansado)\n"
            elif advantage == 'away':
                prompt += f"📊 Vantagem física: {away} (mais descansado)\n"
            else:
                prompt += "📊 Condições físicas equilibradas\n"
        
        # 🔥 NOVO: Adicionar análise de motivação
        motivation = data.get('motivation')
        if motivation and motivation.get('context') != 'Unknown':
            prompt += "\n═══════════════════════════════════════\n"
            prompt += "🎖️ MOTIVAÇÃO E CONTEXTO\n"
            prompt += "═══════════════════════════════════════\n"
            prompt += f"🔥 {motivation.get('context', 'Normal league match')}\n\n"
            home_level = motivation.get('home', 'medium')
            home_reason = motivation.get('home_reason', '')
            away_level = motivation.get('away', 'medium')
            away_reason = motivation.get('away_reason', '')
            
            stars = {'very_high': '⭐⭐⭐⭐⭐', 'high': '⭐⭐⭐⭐', 'medium': '⭐⭐⭐', 'low': '⭐⭐'}
            prompt += f"🏠 {home}: {stars.get(home_level, '⭐⭐⭐')} {home_level.upper()}\n"
            prompt += f"   Razão: {home_reason}\n"
            prompt += f"✈️ {away}: {stars.get(away_level, '⭐⭐⭐')} {away_level.upper()}\n"
            prompt += f"   Razão: {away_reason}\n"
        
        # Adicionar estatísticas da partida (ao vivo/finalizadas)
        statistics = data.get('statistics')
        if statistics and len(statistics) >= 2:
            prompt += "\n═══════════════════════════════════════\n"
            prompt += "📈 ESTATÍSTICAS DA PARTIDA (AO VIVO)\n"
            prompt += "═══════════════════════════════════════\n"
            
            home_stats = statistics[0].get('statistics', [])
            away_stats = statistics[1].get('statistics', [])
            
            prompt += f"📊 Comparativo {home} vs {away}:\n\n"
            for idx, stat in enumerate(home_stats):
                stat_type = stat.get('type')
                home_val = stat.get('value', 0) or 0
                away_val = away_stats[idx].get('value', 0) if idx < len(away_stats) else 0
                away_val = away_val or 0
                prompt += f"  • {stat_type}: {home_val} vs {away_val}\n"
        
        # Adicionar dados da fixture (detalhes gerais)
        fixture_details = data.get('fixture_details')
        # Adicionar dados da fixture (detalhes gerais)
        fixture_details = data.get('fixture_details')
        if fixture_details:
            # Informações extras do fixture (árbitro, eventos, etc.)
            fixture_info = fixture_details.get('fixture', {})
            referee = fixture_info.get('referee')
            if referee:
                prompt += f"\n👨‍⚖️ Árbitro: {referee}\n"
            
            # Eventos da partida (gols, cartões)
            events = fixture_details.get('events', [])
            if events:
                prompt += "\n⚽ Principais Eventos:\n"
                for event in events[:5]:  # Limitar a 5 eventos
                    time_elapsed = event.get('time', {}).get('elapsed', '?')
                    team = event.get('team', {}).get('name', 'N/A')
                    player = event.get('player', {}).get('name', 'N/A')
                    event_type = event.get('type', 'N/A')
                    prompt += f"  • {time_elapsed}' - {team}: {player} ({event_type})\n"
        
        # Adicionar H2H (histórico direto) da Football-Data.org
        h2h = data.get('h2h')
        if h2h and len(h2h) > 0:
            prompt += "\n═══════════════════════════════════════\n"
            prompt += "📜 HISTÓRICO DIRETO (H2H)\n"
            prompt += "═══════════════════════════════════════\n"
            prompt += f"Últimos {len(h2h)} confrontos entre {home} e {away}:\n\n"
            
            home_wins = 0
            away_wins = 0
            draws = 0
            
            for idx, match in enumerate(h2h[:5], 1):  # Limitar a 5 jogos mais recentes
                score = match.get('score', {})
                full_time = score.get('fullTime', {})
                home_score = full_time.get('home')
                away_score = full_time.get('away')
                
                if home_score is not None and away_score is not None:
                    # Determinar vencedor
                    if home_score > away_score:
                        home_wins += 1
                        result = "✅ Vitória Casa"
                    elif away_score > home_score:
                        away_wins += 1
                        result = "✅ Vitória Fora"
                    else:
                        draws += 1
                        result = "⚖️ Empate"
                    
                    match_date = match.get('utcDate', 'Data desconhecida')[:10]
                    home_team = match.get('homeTeam', {}).get('name', 'Casa')
                    away_team = match.get('awayTeam', {}).get('name', 'Fora')
                    prompt += f"  {idx}. {match_date}: {home_team} {home_score} x {away_score} {away_team} - {result}\n"
            
            # Resumo do H2H
            total = home_wins + away_wins + draws
            if total > 0:
                prompt += f"\n📊 Resumo H2H:\n"
                prompt += f"  • Vitórias Casa: {home_wins} ({(home_wins/total)*100:.1f}%)\n"
                prompt += f"  • Empates: {draws} ({(draws/total)*100:.1f}%)\n"
                prompt += f"  • Vitórias Fora: {away_wins} ({(away_wins/total)*100:.1f}%)\n"
        
        # Adicionar previsões/forma dos times
        predictions = data.get('predictions')
        if predictions:
            prompt += "\n═══════════════════════════════════════\n"
            prompt += "🎲 DADOS ESTATÍSTICOS E PREVISÕES\n"
            prompt += "═══════════════════════════════════════\n"
            
            # Forma dos times
            teams_data = predictions.get('teams', {})
            home_data = teams_data.get('home', {})
            away_data = teams_data.get('away', {})
            
            if home_data:
                prompt += f"\n🏠 {home}:\n"
                prompt += f"  • Forma: {home_data.get('last_5', {}).get('form', 'N/A')}\n"
                prompt += f"  • Ataque: {home_data.get('league', {}).get('goals', {}).get('for', {}).get('average', {}).get('total', 'N/A')} gols/jogo\n"
                prompt += f"  • Defesa: {home_data.get('league', {}).get('goals', {}).get('against', {}).get('average', {}).get('total', 'N/A')} gols sofridos/jogo\n"
            
            if away_data:
                prompt += f"\n✈️ {away}:\n"
                prompt += f"  • Forma: {away_data.get('last_5', {}).get('form', 'N/A')}\n"
                prompt += f"  • Ataque: {away_data.get('league', {}).get('goals', {}).get('for', {}).get('average', {}).get('total', 'N/A')} gols/jogo\n"
                prompt += f"  • Defesa: {away_data.get('league', {}).get('goals', {}).get('against', {}).get('average', {}).get('total', 'N/A')} gols sofridos/jogo\n"
            
            # Comparação de força
            comparison = predictions.get('comparison', {})
            if comparison:
                prompt += "\n⚖️ Comparação de Força:\n"
                for key, value in comparison.items():
                    prompt += f"  • {key.replace('_', ' ').title()}: {value.get('home', 'N/A')} vs {value.get('away', 'N/A')}\n"
        
        prompt += """

═══════════════════════════════════════
🎯 FORMATO DE RESPOSTA OBRIGATÓRIO
═══════════════════════════════════════

🚨 ATENÇÃO: Você é um motor de decisão profissional, não um chatbot.
👉 O usuário deve tomar a DECISÃO em até 3 SEGUNDOS com confiança total.

PRINCÍPIOS DE DESIGN:
✓ Hierarquia visual clara
✓ Escaneabilidade máxima
✓ Linguagem profissional e objetiva
✓ Sem exageros ou promessas irreais
✓ Foco em orientação baseada em dados

═══════════════════════════════════════
🔥 BLOCO 1 — DECISÃO IMEDIATA (HERO)
═══════════════════════════════════════
Este é o DESTAQUE PRINCIPAL. Leitura em menos de 5 segundos.

🎯 PREVISÃO DA IA

**[RESULTADO MAIS PROVÁVEL]**

📊 Probabilidade: [XX]%
⚽ Placar esperado: [X:X]

⭐ Confiança: [X] estrelas ([Alta | Média | Baixa])
⚠️ Risco: [Baixo | Médio | Alto]

Regras para este bloco:
- ZERO introduções ou enrolação
- Uma única previsão clara e direta
- Probabilidade em destaque (número grande)
- Estrelas de confiança sempre explicadas
- Micro-alerta de risco discreto mas visível
- Otimizado para leitura rápida em mobile

═══════════════════════════════════════
⚡ BLOCO 2 — FATORES-CHAVE DA DECISÃO
═══════════════════════════════════════
Máximo 3-4 bullets. Cada um deve ser persuasivo e escaneável.

⚡ POR QUE ESSA PREVISÃO?

✓ **Forma recente:** [Insight objetivo com dado numérico]
✓ **Confronto direto:** [Padrão histórico relevante]
✓ **Análise tática:** [Vantagem competitiva clara]
✓ **Modelo estatístico:** [Resultado da análise Poisson/xG se disponível]

Regras para este bloco:
- Cada bullet: 1 linha máxima
- Formato: **Fator:** Explicação objetiva
- Dados concretos sempre que possível
- Evite números excessivos em uma frase
- Destaque o fator antes da explicação
- Linguagem persuasiva mas profissional

═══════════════════════════════════════
📊 BLOCO 3 — PROBABILIDADES VISUAIS
═══════════════════════════════════════
Priorize entendimento instantâneo. Números grandes e comparáveis.

📊 PROBABILIDADES

🏠 **[TIME_CASA]:** [XX]%
🤝 **Empate:** [XX]%
✈️ **[TIME_FORA]:** [XX]%

---
💡 **Interpretação rápida:** [Uma frase explicando o cenário mais provável]

Regras para este bloco:
- Percentuais grandes e destacados
- Soma DEVE ser 100%
- Cores neutras e profissionais
- Adicione uma linha de interpretação rápida
- Facilite comparação visual entre cenários
- Mobile: empilhar verticalmente

═══════════════════════════════════════
📚 BLOCO 4 — ANÁLISE DETALHADA
═══════════════════════════════════════
Profundidade analítica para quem quer aprofundar. Estrutura colapsável.

**📋 RESUMO EXECUTIVO**
[2-3 frases com contexto essencial do jogo. Sempre visível, não colapsa.]

---

**1️⃣ ANÁLISE DE FORMA**

🏠 **Casa – [TIME_CASA]**
• Últimos 5 jogos: [Resumo com W-D-L]
• Desempenho em casa: [Estatística relevante]
• Momento atual: [Tendência clara]

✈️ **Fora – [TIME_FORA]**
• Últimos 5 jogos: [Resumo com W-D-L]
• Desempenho fora: [Estatística relevante]
• Momento atual: [Tendência clara]

---

**2️⃣ CONFRONTOS DIRETOS (H2H)**
• Histórico: [X vitórias casa, Y empates, Z vitórias fora nos últimos N jogos]
• Padrão identificado: [Tendência relevante]
• Contexto: [Informação que muda a leitura dos números]

---

**3️⃣ ANÁLISE TÁTICA E ESTATÍSTICA**
• **Ataque vs Defesa:** [Comparação de médias de gols]
• **Estilo de jogo:** [Como os estilos se complementam/conflitam]
• **Fator decisivo:** [O que pode definir o jogo]
• **xG e Poisson:** [Resultado de modelos estatísticos, se disponíveis]

Regras para este bloco:
- Resumo executivo sempre visível
- Restante pode ser colapsável no frontend
- Evite redundância entre seções
- Fluxo de leitura otimizado para mobile
- Mantenha profundidade sem perder clareza

═══════════════════════════════════════
💰 BLOCO 5 — RECOMENDAÇÃO FINAL
═══════════════════════════════════════
Acionável, coerente com os dados, sem imposição.

💰 RECOMENDAÇÃO

**Aposta sugerida:** [Mercado específico + seleção]
**Tipo:** [Conservadora | Equilibrada | Agressiva]

✅ **Justificativa:** [Por que esta aposta faz sentido com base nos dados apresentados]
⚠️ **Gestão de risco:** [Como minimizar perdas ou maximizar value]

💡 **Alternativa:** [Segunda melhor opção, se houver]

Regras para este bloco:
- Recomendação clara e específica
- Indicar perfil da aposta (conservadora/agressiva)
- Justificativa alinhada com análise
- Gestão de risco sem quebrar confiança
- Alternativa opcional para usuários avançados
- Linguagem orientadora, não impositiva

═══════════════════════════════════════
✍️ REGRAS DE FORMATAÇÃO (OBRIGATÓRIO)
═══════════════════════════════════════

✔ **Negrito (**texto**):**
- Nomes dos times
- Fatores-chave (Forma recente:, Ataque vs Defesa:)
- Resultados e recomendações
- Subtítulos importantes

✔ **Números e Percentuais:**
- Sempre que possível: 65%, 8 vitórias, 2.4 gols, 3:1
- Serão renderizados como badges visuais
- Priorize clareza sobre volume

✔ **Bullets (•):**
- Use para listas escaneáveis
- NUNCA parágrafo corrido para múltiplos pontos
- Máximo 4-5 bullets por seção

✔ **Emojis:**
- Apenas estruturais: 🎯 📊 ⚡ 💰 ⚠️ 🏠 ✈️
- NÃO use emojis decorativos
- Ajudam na hierarquia visual

✔ **Logos dos Times:**
- Sistema detecta automaticamente nomes dos times
- Renderiza logos inline
- Não precisa formatar

═══════════════════════════════════════
🚫 O QUE NÃO FAZER (PROIBIDO)
═══════════════════════════════════════

❌ NÃO comece com "Olá" ou introduções genéricas
❌ NÃO use linguagem promocional ou exagerada
❌ NÃO prometa resultados garantidos
❌ NÃO invente estatísticas ou dados
❌ NÃO escreva parágrafos longos no Bloco 1 ou 2
❌ NÃO pule blocos ou mude a ordem
❌ NÃO use "*" sozinho (sempre **)
❌ NÃO escreva como especialista explicando, escreva como motor de decisão

═══════════════════════════════════════
⭐ ESCALA DE CONFIANÇA (PADRONIZADA)
═══════════════════════════════════════

**5 estrelas** = Alta (70%+) - Dados completos, favorito claro
**4 estrelas** = Alta (60-69%) - Bons dados, leve favorito
**3 estrelas** = Média (50-59%) - Dados moderados, jogo equilibrado
**2 estrelas** = Baixa (40-49%) - Dados limitados, muita incerteza
**1 estrela** = Baixa (<40%) - Dados insuficientes, evitar aposta

⚠️ **ESCALA DE RISCO:**
- **Baixo:** Favorito óbvio, odds conservadoras
- **Médio:** Jogo competitivo, odds razoáveis
- **Alto:** Jogo imprevisível, odds arriscadas

═══════════════════════════════════════
🎯 CHECKLIST DE QUALIDADE FINAL
═══════════════════════════════════════

Antes de enviar, confirme:
✓ Bloco 1 pode ser lido em menos de 5 segundos
✓ Bloco 2 tem máximo 4 bullets, cada um com 1 linha
✓ Bloco 3 tem percentuais somando 100%
✓ Bloco 4 tem resumo executivo separado do restante
✓ Bloco 5 tem recomendação específica e acionável
✓ Nenhuma promessa irreal ou linguagem promocional
✓ Números em destaque (serão badges visuais)
✓ Linguagem profissional e clara
✓ Otimizado para mobile (leitura vertical)
✓ Hierarquia visual forte (títulos, bullets, destaques)

═══════════════════════════════════════
🏁 RESULTADO ESPERADO
═══════════════════════════════════════

✓ Motor de decisão profissional
✓ Decisão em 3 segundos
✓ Profundidade para quem quer aprofundar
✓ Confiança baseada em dados
✓ Experiência premium
✓ Funciona perfeitamente em mobile e desktop

👉 Priorize sempre: CLAREZA > CRIATIVIDADE
═══════════════════════════════════════
"""
        
        return prompt
    
    def _extract_confidence(self, text: str) -> int:
        """Extrair nível de confiança da análise de forma robusta"""
        text_lower = text.lower()
        
        # Padrões de busca (ordem: 5 -> 1 para pegar o maior primeiro)
        confidence_patterns = {
            5: ['5 estrelas', '★★★★★', '5/5', 'cinco estrelas', 'confiança: 5', 'nível: 5', 
                'altíssima confiança', 'muito alta', 'excelente'],
            4: ['4 estrelas', '★★★★', '4/5', 'quatro estrelas', 'confiança: 4', 'nível: 4',
                'alta confiança', 'muito boa', 'ótima'],
            3: ['3 estrelas', '★★★', '3/5', 'três estrelas', 'confiança: 3', 'nível: 3',
                'média confiança', 'moderada', 'razoável', 'boa'],
            2: ['2 estrelas', '★★', '2/5', 'duas estrelas', 'confiança: 2', 'nível: 2',
                'baixa confiança', 'fraca', 'pouca'],
            1: ['1 estrela', '★', '1/5', 'uma estrela', 'confiança: 1', 'nível: 1',
                'muito baixa', 'mínima', 'fraquíssima']
        }
        
        # Verificar padrões na ordem 5->4->3->2->1
        for level in [5, 4, 3, 2, 1]:
            for pattern in confidence_patterns[level]:
                if pattern in text_lower:
                    return level
        
        # Se nenhum padrão encontrado, tentar detectar sentimento geral
        # Palavras indicativas de alta confiança
        high_confidence_words = ['certeza', 'definitivamente', 'claramente', 'óbvio', 'forte']
        low_confidence_words = ['talvez', 'possivelmente', 'incerto', 'duvidoso', 'arriscado']
        
        high_count = sum(1 for word in high_confidence_words if word in text_lower)
        low_count = sum(1 for word in low_confidence_words if word in text_lower)
        
        if high_count > low_count:
            return 4  # Alta confiança implícita
        elif low_count > high_count:
            return 2  # Baixa confiança implícita
        
        # Default: confiança média
        return 3
