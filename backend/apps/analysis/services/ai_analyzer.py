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
        # Selecionar um modelo suportado dinamicamente via list_models
        model_name = None
        try:
            available = list(genai.list_models())
            supported = [m for m in available if hasattr(m, 'supported_generation_methods') and ('generateContent' in m.supported_generation_methods)]
            # Ordenar preferência: gemini-2.5 > gemini-1.5 > gemini-1.0 > gemini-pro
            def score(m):
                n = getattr(m, 'name', getattr(m, 'model', '')).lower()
                if 'gemini-2.5' in n:
                    return 0
                if 'gemini-1.5' in n:
                    return 1
                if 'gemini-1.0' in n:
                    return 2
                if 'gemini-pro' in n:
                    return 3
                return 4
            supported.sort(key=score)
            chosen = supported[0] if supported else None
            if chosen:
                chosen_name = getattr(chosen, 'name', getattr(chosen, 'model', None)) or 'gemini-pro'
                # Aceitar tanto 'models/...' quanto nome simples
                if isinstance(chosen_name, str) and chosen_name.startswith('models/'):
                    chosen_name = chosen_name.replace('models/', '')
                self.model = genai.GenerativeModel(chosen_name)
                model_name = chosen_name
            else:
                logger.error("Nenhum modelo com suporte a generateContent disponível para esta chave/API.")
                self.model = None
        except Exception as e:
            logger.error(f"Falha ao listar modelos do Gemini: {e}")
            self.model = None
        
        logger.info(f"AI Analyzer inicializado com modelo: {model_name}")
    
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
        """Construir prompt para análise"""
        home = data.get('home_team', {}).get('name', 'Time A')
        away = data.get('away_team', {}).get('name', 'Time B')
        league = data.get('league', 'Liga')
        
        return f"""
Você é um especialista em análise de apostas de futebol. Analise esta partida:

**PARTIDA:** {home} vs {away}
**LIGA:** {league}

Forneça:
1. Análise tática (pontos fortes/fracos)
2. Probabilidades: Vitória Casa / Empate / Vitória Fora
3. Previsão de gols (Over/Under 2.5)
4. Recomendação de aposta principal
5. Nível de confiança (1-5 estrelas)

Seja objetivo e baseie-se em lógica futebolística.
Responda em português de Moçambique.
"""
    
    def _extract_confidence(self, text: str) -> int:
        """Extrair nível de confiança da análise"""
        if '5 estrelas' in text.lower() or '★★★★★' in text:
            return 5
        elif '4 estrelas' in text.lower() or '★★★★' in text:
            return 4
        elif '3 estrelas' in text.lower() or '★★★' in text:
            return 3
        elif '2 estrelas' in text.lower() or '★★' in text:
            return 2
        return 1
