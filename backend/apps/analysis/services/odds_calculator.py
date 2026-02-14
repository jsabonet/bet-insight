"""
Odds Calculator - Cálculo de Odds para Mercados Derivados

Calcula odds de mercados derivados (DC, DNB, Asian Lines) a partir de odds base,
resolvendo o problema de usar odds genéricas (2.00) para mercados sem odds reais.

Date: 2026-02-14
"""

import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class OddsCalculator:
    """
    Calcula odds de mercados derivados usando fórmulas matemáticas corretas.
    
    Mercados Base (devem vir da API):
    - 1X2 (home_win, draw, away_win)
    - Over/Under inteiros (0.5, 1.5, 2.5, 3.5, 4.5)
    - BTTS (btts_yes, btts_no)
    
    Mercados Derivados (calculados):
    - Double Chance (1x, 12, x2)
    - Draw No Bet (dnb_home, dnb_away)
    - Asian Lines (1.75, 2.25, 2.75, 3.25)
    """
    
    def __init__(self, bookmaker_margin: float = 1.05):
        """
        Args:
            bookmaker_margin: Margem típica da bookmaker (1.05 = 5%)
        """
        self.bookmaker_margin = bookmaker_margin
    
    def calculate_all_derived_odds(self, base_odds: Dict[str, float]) -> Dict[str, Dict]:
        """
        Calcula todas as odds derivadas possíveis a partir das odds base.
        
        Args:
            base_odds: Dict com odds base {market: odd_value}
                      Formato canônico: {'home_win': 2.10, 'draw': 3.40, 'away_win': 1.36}
        
        Returns:
            Dict: Odds derivadas com metadados
            {
                '1x': {'value': 1.28, 'source': 'calculated', 'from': ['home_win', 'draw']},
                'dnb_home': {'value': 1.65, 'source': 'calculated', 'from': ['home_win', 'draw']},
                ...
            }
        """
        derived_odds = {}
        
        # Double Chance
        dc_odds = self.calculate_double_chance(base_odds)
        derived_odds.update(dc_odds)
        
        # Draw No Bet
        dnb_odds = self.calculate_draw_no_bet(base_odds)
        derived_odds.update(dnb_odds)
        
        # Asian Lines
        asian_odds = self.calculate_asian_lines(base_odds)
        derived_odds.update(asian_odds)
        
        return derived_odds
    
    def calculate_double_chance(self, base_odds: Dict[str, float]) -> Dict[str, Dict]:
        """
        Calcula odds de Double Chance.
        
        Fórmula: Odd_DC = 1 / (1/Odd_A + 1/Odd_B)
        
        Exemplo:
        - Home: 2.10, Draw: 3.40
        - 1X = 1 / (1/2.10 + 1/3.40) = 1 / (0.476 + 0.294) = 1 / 0.770 = 1.30
        
        Args:
            base_odds: Dict com home_win, draw, away_win
            
        Returns:
            Dict com odds de DC: {'1x': {...}, '12': {...}, 'x2': {...}}
        """
        dc_odds = {}
        
        home_odd = base_odds.get('home_win')
        draw_odd = base_odds.get('draw')
        away_odd = base_odds.get('away_win')
        
        # 1X (Home ou Draw)
        if home_odd and draw_odd and home_odd > 0 and draw_odd > 0:
            implied_prob = 1/home_odd + 1/draw_odd
            dc_1x = round(1 / implied_prob, 2)
            dc_odds['1x'] = {
                'value': dc_1x,
                'source': 'calculated',
                'from': ['home_win', 'draw'],
                'formula': f"1 / (1/{home_odd:.2f} + 1/{draw_odd:.2f})"
            }
        
        # 12 (Home ou Away)
        if home_odd and away_odd and home_odd > 0 and away_odd > 0:
            implied_prob = 1/home_odd + 1/away_odd
            dc_12 = round(1 / implied_prob, 2)
            dc_odds['12'] = {
                'value': dc_12,
                'source': 'calculated',
                'from': ['home_win', 'away_win'],
                'formula': f"1 / (1/{home_odd:.2f} + 1/{away_odd:.2f})"
            }
        
        # X2 (Draw ou Away)
        if draw_odd and away_odd and draw_odd > 0 and away_odd > 0:
            implied_prob = 1/draw_odd + 1/away_odd
            dc_x2 = round(1 / implied_prob, 2)
            dc_odds['x2'] = {
                'value': dc_x2,
                'source': 'calculated',
                'from': ['draw', 'away_win'],
                'formula': f"1 / (1/{draw_odd:.2f} + 1/{away_odd:.2f})"
            }
        
        return dc_odds
    
    def calculate_draw_no_bet(self, base_odds: Dict[str, float]) -> Dict[str, Dict]:
        """
        Calcula odds de Draw No Bet (empate devolve stake).
        
        Fórmula aproximada: Odd_DNB = Odd_Win × (1 + stake_return_factor)
        
        Método exato:
        - DNB Home = ajustar Home odd considerando que Draw retorna stake
        - Probabilidade efetiva = P(Home) / (P(Home) + P(Away))
        - Odd DNB = 1 / P_efetiva com margin
        
        Args:
            base_odds: Dict com home_win, draw, away_win
            
        Returns:
            Dict com odds DNB: {'dnb_home': {...}, 'dnb_away': {...}}
        """
        dnb_odds = {}
        
        home_odd = base_odds.get('home_win')
        draw_odd = base_odds.get('draw')
        away_odd = base_odds.get('away_win')
        
        if not (home_odd and draw_odd and away_odd):
            return dnb_odds
        
        # DNB Home
        if home_odd > 0 and away_odd > 0:
            # Probabilidade efetiva: Home win no universo sem empate
            p_home = 1 / home_odd
            p_away = 1 / away_odd
            p_total = p_home + p_away  # Ignorar draw
            
            if p_total > 0:
                p_dnb_home = p_home / p_total
                # Aplicar margin bookmaker
                dnb_home_fair = 1 / p_dnb_home
                dnb_home = round(dnb_home_fair / self.bookmaker_margin, 2)
                
                dnb_odds['dnb_home'] = {
                    'value': dnb_home,
                    'source': 'calculated',
                    'from': ['home_win', 'away_win', 'draw'],
                    'formula': f"(1/{home_odd:.2f}) / ((1/{home_odd:.2f}) + (1/{away_odd:.2f}))"
                }
        
        # DNB Away
        if home_odd > 0 and away_odd > 0:
            p_home = 1 / home_odd
            p_away = 1 / away_odd
            p_total = p_home + p_away
            
            if p_total > 0:
                p_dnb_away = p_away / p_total
                dnb_away_fair = 1 / p_dnb_away
                dnb_away = round(dnb_away_fair / self.bookmaker_margin, 2)
                
                dnb_odds['dnb_away'] = {
                    'value': dnb_away,
                    'source': 'calculated',
                    'from': ['home_win', 'away_win', 'draw'],
                    'formula': f"(1/{away_odd:.2f}) / ((1/{home_odd:.2f}) + (1/{away_odd:.2f}))"
                }
        
        return dnb_odds
    
    def calculate_asian_lines(self, base_odds: Dict[str, float]) -> Dict[str, Dict]:
        """
        Calcula odds de Asian Handicap (linhas quebradas).
        
        Asian Lines combinam duas apostas:
        - Over 2.25 = 50% Over 2.0 + 50% Over 2.5
        - Over 2.75 = 50% Over 2.5 + 50% Over 3.0
        
        Fórmula: Odd_Asian = 2 / (1/Odd_Lower + 1/Odd_Upper)
        
        Args:
            base_odds: Dict com over/under inteiros
            
        Returns:
            Dict com odds Asian: {'over_1.75': {...}, 'under_2.25': {...}, ...}
        """
        asian_odds = {}
        
        # Definir combinações
        asian_combinations = {
            'over_1.75': ('over_1.5', 'over_2.5'),   # Média de 1.5 e 2.0, mas usamos 2.5 como proxy
            'under_1.75': ('under_1.5', 'under_2.5'),
            'over_2.25': ('over_2.5', 'over_2.5'),   # Idealmente seria 2.0 e 2.5
            'under_2.25': ('under_2.5', 'under_2.5'),
            'over_2.75': ('over_2.5', 'over_3.5'),
            'under_2.75': ('under_2.5', 'under_3.5'),
            'over_3.25': ('over_3.5', 'over_3.5'),   # Idealmente seria 3.0 e 3.5
            'under_3.25': ('under_3.5', 'under_3.5'),
        }
        
        for asian_market, (lower, upper) in asian_combinations.items():
            lower_odd = base_odds.get(lower)
            upper_odd = base_odds.get(upper)
            
            if lower_odd and upper_odd and lower_odd > 0 and upper_odd > 0:
                # Média harmônica das duas odds
                asian_odd = round(2 / (1/lower_odd + 1/upper_odd), 2)
                
                asian_odds[asian_market] = {
                    'value': asian_odd,
                    'source': 'calculated',
                    'from': [lower, upper],
                    'formula': f"2 / (1/{lower_odd:.2f} + 1/{upper_odd:.2f})"
                }
        
        return asian_odds
    
    def calculate_simulated_odds(self, probabilities: Dict[str, float]) -> Dict[str, Dict]:
        """
        Simula odds a partir de probabilidades quando não há odds reais.
        
        Aplica margin bookmaker às probabilidades do modelo.
        IMPORTANTE: Estas odds são marcadas como 'simulated' e não devem
        ser usadas para cálculo de EV (sempre resultarão em EV ≈ -margin).
        
        Args:
            probabilities: Dict {market: probability}
                          Exemplo: {'home_win': 0.42, 'draw': 0.30, 'away_win': 0.28}
        
        Returns:
            Dict: Odds simuladas com metadados
            {
                'home_win': {'value': 2.27, 'source': 'simulated', 'is_simulated': True},
                ...
            }
        """
        simulated_odds = {}
        
        for market, prob in probabilities.items():
            if prob > 0:
                fair_odd = 1 / prob
                simulated_odd = round(fair_odd / self.bookmaker_margin, 2)
                
                simulated_odds[market] = {
                    'value': simulated_odd,
                    'source': 'simulated',
                    'is_simulated': True,
                    'confidence': 0.3,  # Baixa confiança
                    'warning': 'Odds simuladas não devem ser usadas para cálculo de EV'
                }
        
        return simulated_odds
    
    def enrich_odds_dict(self, base_odds: Dict[str, float]) -> Dict[str, Dict]:
        """
        Enriquece dicionário de odds simples com metadados e odds derivadas.
        
        Args:
            base_odds: Dict simples {market: odd_value}
                      Exemplo: {'home_win': 2.10, 'draw': 3.40, 'away_win': 1.36}
        
        Returns:
            Dict enriquecido:
            {
                'home_win': {'value': 2.10, 'source': 'api', 'bookmaker': 'bet365'},
                '1x': {'value': 1.28, 'source': 'calculated', 'from': ['home_win', 'draw']},
                ...
            }
        """
        enriched = {}
        
        # Marcar odds base como vindas da API
        for market, odd_value in base_odds.items():
            if odd_value and odd_value > 0:
                enriched[market] = {
                    'value': odd_value,
                    'source': 'api',
                    'is_simulated': False
                }
        
        # Calcular e adicionar odds derivadas
        derived = self.calculate_all_derived_odds(base_odds)
        enriched.update(derived)
        
        return enriched
    
    @staticmethod
    def get_odd_value(odds_dict: Dict, market: str) -> Optional[float]:
        """
        Extrai valor da odd de um dict enriquecido.
        
        Args:
            odds_dict: Dict enriquecido ou simples
            market: Nome do mercado (canônico)
        
        Returns:
            float: Valor da odd, ou None se não existe
        """
        odd_data = odds_dict.get(market)
        
        if odd_data is None:
            return None
        
        # Dict enriquecido
        if isinstance(odd_data, dict):
            return odd_data.get('value')
        
        # Dict simples (backward compatibility)
        if isinstance(odd_data, (int, float)):
            return float(odd_data)
        
        return None
    
    @staticmethod
    def get_odd_source(odds_dict: Dict, market: str) -> Optional[str]:
        """
        Retorna a fonte da odd (api, calculated, simulated).
        
        Args:
            odds_dict: Dict enriquecido
            market: Nome do mercado (canônico)
        
        Returns:
            str: 'api', 'calculated', 'simulated', ou None
        """
        odd_data = odds_dict.get(market)
        
        if isinstance(odd_data, dict):
            return odd_data.get('source')
        
        return None
    
    @staticmethod
    def is_simulated(odds_dict: Dict, market: str) -> bool:
        """
        Verifica se a odd é simulada.
        
        Args:
            odds_dict: Dict enriquecido
            market: Nome do mercado (canônico)
        
        Returns:
            bool: True se simulada, False caso contrário
        """
        odd_data = odds_dict.get(market)
        
        if isinstance(odd_data, dict):
            return odd_data.get('is_simulated', False)
        
        return False


def calculate_derived_odds(base_odds: Dict[str, float]) -> Dict[str, float]:
    """
    Função utilitária para cálculo rápido de odds derivadas (formato simples).
    
    Args:
        base_odds: {'home_win': 2.10, 'draw': 3.40, 'away_win': 1.36}
    
    Returns:
        {'1x': 1.28, '12': 1.52, 'x2': 1.18, 'dnb_home': 1.65, 'dnb_away': 1.08, ...}
    """
    calculator = OddsCalculator()
    enriched = calculator.calculate_all_derived_odds(base_odds)
    
    # Converter para formato simples
    simple = {}
    for market, data in enriched.items():
        simple[market] = data['value']
    
    return simple
