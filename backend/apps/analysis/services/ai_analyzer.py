"""
Serviço de análise com Google Gemini AI
Gera análises preditivas e recomendações de apostas
"""
import google.generativeai as genai
from django.conf import settings
from typing import Dict
import logging
import json

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Serviço de análise com IA (Google Gemini)"""
    
    def __init__(self):
        genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
        # Detectar modelo disponível automaticamente
        models = genai.list_models()
        available = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        model_name = available[0].replace('models/', '') if available else 'gemini-2.5-flash'
        self.model = genai.GenerativeModel(model_name)
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
            prompt = self._build_analysis_prompt(match_data)
            logger.info(f"Analisando: {match_data.get('home_team', {}).get('name')} vs {match_data.get('away_team', {}).get('name')}")
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'analysis': response.text,
                'confidence': self._extract_confidence(response.text)
            }
        except Exception as e:
            logger.error(f"Erro na análise: {e}")
            return {'success': False, 'error': str(e)}
    
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
        
        # Gerar probabilidades aleatórias mas realistas
        base = random.uniform(30, 50)
        home_prob = round(base, 1)
        away_prob = round(100 - base - random.uniform(20, 30), 1)
        draw_prob = round(100 - home_prob - away_prob, 1)
        
        # Determinar predição baseada nas probabilidades
        probs = {'home': home_prob, 'away': away_prob, 'draw': draw_prob}
        prediction = max(probs, key=probs.get)
        
        # Confiança baseada na diferença de probabilidade
        max_prob = max(probs.values())
        if max_prob > 50:
            confidence = 4
        elif max_prob > 45:
            confidence = 3
        else:
            confidence = 2
        
        home_team = data['home_team']['name']
        away_team = data['away_team']['name']
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'home_probability': home_prob,
            'draw_probability': draw_prob,
            'away_probability': away_prob,
            'home_xg': round(random.uniform(0.8, 2.5), 1),
            'away_xg': round(random.uniform(0.8, 2.5), 1),
            'reasoning': f'Análise baseada em estatísticas recentes. {home_team} enfrenta {away_team} em confronto equilibrado. Considerando forma atual, histórico e fator casa.',
            'key_factors': [
                f'Forma recente favorece {home_team if prediction == "home" else away_team}',
                'Histórico direto equilibrado',
                'Fator casa pode ser decisivo'
            ],
            'analysis_breakdown': {
                'form': {'home': round(random.uniform(50, 80), 1), 'away': round(random.uniform(50, 80), 1)},
                'home_away': {'advantage': 65},
                'h2h': {'score': round(random.uniform(40, 60), 1)},
                'stats': {'home': round(random.uniform(50, 75), 1), 'away': round(random.uniform(50, 75), 1)}
            }
        }
    
    def _parse_response(self, response_text):
        """Parsear resposta da IA"""
        try:
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0]
            
            result = json.loads(response_text.strip())
            
            required = ['prediction', 'confidence', 'home_probability', 
                       'draw_probability', 'away_probability', 'reasoning']
            
            for field in required:
                if field not in result:
                    raise ValueError(f"Campo {field} ausente")
            
            return result
            
        except Exception as e:
            print(f"Erro ao parsear resposta: {e}")
            return self._get_default_analysis()
    
    def _get_default_analysis(self):
        """Análise padrão em caso de erro"""
        return {
            'prediction': 'draw',
            'confidence': 2,
            'home_probability': 33.3,
            'draw_probability': 33.3,
            'away_probability': 33.4,
            'home_xg': 1.5,
            'away_xg': 1.5,
            'reasoning': 'Análise indisponível. Dados insuficientes.',
            'key_factors': ['Análise em modo seguro'],
            'analysis_breakdown': {}
        }
