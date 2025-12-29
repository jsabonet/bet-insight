import json


class AIAnalyzer:
    """Serviço de análise com IA (simulado por enquanto)"""
    
    def __init__(self):
        # TODO: Integrar com Google Gemini API quando disponível
        pass
    
    def analyze_match(self, match_data):
        """
        Analisa uma partida e retorna predição
        
        match_data deve conter:
        - home_team: {'name': str, 'stats': dict}
        - away_team: {'name': str, 'stats': dict}
        - h2h: list de resultados anteriores
        - league: str
        - date: str
        """
        
        # Por enquanto, retorna análise simulada
        # Na Fase 6, será integrado com Google Gemini
        
        return self._get_simulated_analysis(match_data)
    
    def _get_simulated_analysis(self, data):
        """Análise simulada para testes"""
        import random
        
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
