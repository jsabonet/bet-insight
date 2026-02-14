"""
Market Standards - Nomenclatura Canônica de Mercados

Define formato padrão único para todos os mercados de apostas,
resolvendo o problema de nomenclatura inconsistente entre módulos.

Date: 2026-02-14
"""

from typing import Dict, Optional, List


# Formato canônico: sempre lowercase, underscore, ponto em decimais
CANONICAL_MARKETS = {
    # 1X2
    'home_win': ['home_win', 'home', '1', 'home_victory', 'home_win_ft'],
    'draw': ['draw', 'x', 'tie', 'empate', 'draw_ft'],
    'away_win': ['away_win', 'away', '2', 'away_victory', 'away_win_ft'],
    
    # Double Chance
    '1x': ['1x', '1X', 'home_or_draw', 'home_draw', 'double_chance_1x'],
    '12': ['12', 'home_or_away', 'home_away', 'double_chance_12'],
    'x2': ['x2', 'X2', 'draw_or_away', 'draw_away', 'double_chance_x2'],
    
    # Over/Under (sempre com ponto)
    'over_0.5': ['over_0.5', 'over_0_5', 'over05', 'over_05'],
    'under_0.5': ['under_0.5', 'under_0_5', 'under05', 'under_05'],
    'over_1.5': ['over_1.5', 'over_1_5', 'over15', 'over_15', 'ou15_over'],
    'under_1.5': ['under_1.5', 'under_1_5', 'under15', 'under_15', 'ou15_under'],
    'over_2.5': ['over_2.5', 'over_2_5', 'over25', 'over_25', 'ou25_over'],
    'under_2.5': ['under_2.5', 'under_2_5', 'under25', 'under_25', 'ou25_under'],
    'over_3.5': ['over_3.5', 'over_3_5', 'over35', 'over_35', 'ou35_over'],
    'under_3.5': ['under_3.5', 'under_3_5', 'under35', 'under_35', 'ou35_under'],
    'over_4.5': ['over_4.5', 'over_4_5', 'over45', 'over_45'],
    'under_4.5': ['under_4.5', 'under_4_5', 'under45', 'under_45'],
    
    # Asian Lines
    'over_1.75': ['over_1.75', 'over_1_75'],
    'under_1.75': ['under_1.75', 'under_1_75'],
    'over_2.25': ['over_2.25', 'over_2_25'],
    'under_2.25': ['under_2.25', 'under_2_25'],
    'over_2.75': ['over_2.75', 'over_2_75'],
    'under_2.75': ['under_2.75', 'under_2_75'],
    'over_3.25': ['over_3.25', 'over_3_25'],
    'under_3.25': ['under_3.25', 'under_3_25'],
    
    # BTTS
    'btts_yes': ['btts_yes', 'btts', 'both_teams_score', 'gg'],
    'btts_no': ['btts_no', 'btts_not', 'no_btts', 'ng'],
    
    # Clean Sheets
    'home_clean_sheet': ['home_clean_sheet', 'home_cs', 'clean_sheet_home'],
    'away_clean_sheet': ['away_clean_sheet', 'away_cs', 'clean_sheet_away'],
    
    # Team Totals - Home
    'home_over_0.5': ['home_over_0.5', 'home_over_0_5'],
    'home_under_0.5': ['home_under_0.5', 'home_under_0_5'],
    'home_over_1.5': ['home_over_1.5', 'home_over_1_5'],
    'home_under_1.5': ['home_under_1.5', 'home_under_1_5'],
    'home_over_2.5': ['home_over_2.5', 'home_over_2_5'],
    'home_under_2.5': ['home_under_2.5', 'home_under_2_5'],
    
    # Team Totals - Away
    'away_over_0.5': ['away_over_0.5', 'away_over_0_5'],
    'away_under_0.5': ['away_under_0.5', 'away_under_0_5'],
    'away_over_1.5': ['away_over_1.5', 'away_over_1_5'],
    'away_under_1.5': ['away_under_1.5', 'away_under_1_5'],
    'away_over_2.5': ['away_over_2.5', 'away_over_2_5'],
    'away_under_2.5': ['away_under_2.5', 'away_under_2_5'],
    
    # Odd/Even
    'odd_goals': ['odd_goals', 'odd', 'impar'],
    'even_goals': ['even_goals', 'even', 'par'],
    
    # Winning Margin
    'home_by_1': ['home_by_1', 'home_margin_1'],
    'home_by_2plus': ['home_by_2plus', 'home_by_2+', 'home_margin_2+'],
    'away_by_1': ['away_by_1', 'away_margin_1'],
    'away_by_2plus': ['away_by_2plus', 'away_by_2+', 'away_margin_2+'],
    'any_by_1': ['any_by_1'],
    'any_by_2plus': ['any_by_2plus', 'any_by_2+'],
    
    # DNB (Draw No Bet)
    'dnb_home': ['dnb_home', 'home_dnb', 'draw_no_bet_home'],
    'dnb_away': ['dnb_away', 'away_dnb', 'draw_no_bet_away'],
    
    # Half Time
    'home_ht': ['home_ht', 'ht_home', 'home_win_ht'],
    'draw_ht': ['draw_ht', 'ht_draw', 'draw_halftime'],
    'away_ht': ['away_ht', 'ht_away', 'away_win_ht'],
    
    # Half Time / Full Time
    'ht_ft_1_1': ['ht_ft_1_1', 'htft_1_1'],
    'ht_ft_1_x': ['ht_ft_1_x', 'ht_ft_1_X', 'htft_1_x'],
    'ht_ft_1_2': ['ht_ft_1_2', 'htft_1_2'],
    'ht_ft_x_1': ['ht_ft_x_1', 'ht_ft_X_1', 'htft_x_1'],
    'ht_ft_x_x': ['ht_ft_x_x', 'ht_ft_X_X', 'htft_x_x'],
    'ht_ft_x_2': ['ht_ft_x_2', 'ht_ft_X_2', 'htft_x_2'],
    'ht_ft_2_1': ['ht_ft_2_1', 'htft_2_1'],
    'ht_ft_2_x': ['ht_ft_2_x', 'ht_ft_2_X', 'htft_2_x'],
    'ht_ft_2_2': ['ht_ft_2_2', 'htft_2_2'],
}


# Mapeamento reverso: qualquer alias → canônico
_ALIAS_TO_CANONICAL = {}
for canonical, aliases in CANONICAL_MARKETS.items():
    for alias in aliases:
        _ALIAS_TO_CANONICAL[alias.lower()] = canonical


# Nomes de exibição (Portuguese)
MARKET_DISPLAY_NAMES = {
    # 1X2
    'home_win': 'Vitória Casa',
    'draw': 'Empate',
    'away_win': 'Vitória Fora',
    
    # Double Chance
    '1x': 'Casa ou Empate',
    '12': 'Casa ou Fora',
    'x2': 'Empate ou Fora',
    
    # Over/Under
    'over_0.5': 'Over 0.5',
    'under_0.5': 'Under 0.5 (0-0)',
    'over_1.5': 'Over 1.5',
    'under_1.5': 'Under 1.5',
    'over_2.5': 'Over 2.5',
    'under_2.5': 'Under 2.5',
    'over_3.5': 'Over 3.5',
    'under_3.5': 'Under 3.5',
    'over_4.5': 'Over 4.5',
    'under_4.5': 'Under 4.5',
    
    # Asian Lines
    'over_1.75': 'Over 1.75',
    'under_1.75': 'Under 1.75',
    'over_2.25': 'Over 2.25',
    'under_2.25': 'Under 2.25',
    'over_2.75': 'Over 2.75',
    'under_2.75': 'Under 2.75',
    'over_3.25': 'Over 3.25',
    'under_3.25': 'Under 3.25',
    
    # BTTS
    'btts_yes': 'Ambos Marcam',
    'btts_no': 'Ambos Não Marcam',
    
    # Clean Sheets
    'home_clean_sheet': 'Casa Clean Sheet',
    'away_clean_sheet': 'Fora Clean Sheet',
    
    # Team Totals - Home
    'home_over_0.5': 'Casa Over 0.5',
    'home_under_0.5': 'Casa Under 0.5',
    'home_over_1.5': 'Casa Over 1.5',
    'home_under_1.5': 'Casa Under 1.5',
    'home_over_2.5': 'Casa Over 2.5',
    'home_under_2.5': 'Casa Under 2.5',
    
    # Team Totals - Away
    'away_over_0.5': 'Fora Over 0.5',
    'away_under_0.5': 'Fora Under 0.5',
    'away_over_1.5': 'Fora Over 1.5',
    'away_under_1.5': 'Fora Under 1.5',
    'away_over_2.5': 'Fora Over 2.5',
    'away_under_2.5': 'Fora Under 2.5',
    
    # Odd/Even
    'odd_goals': 'Gols Ímpares',
    'even_goals': 'Gols Pares',
    
    # Winning Margin
    'home_by_1': 'Casa por 1',
    'home_by_2plus': 'Casa por 2+',
    'away_by_1': 'Fora por 1',
    'away_by_2plus': 'Fora por 2+',
    'any_by_1': 'Qualquer por 1',
    'any_by_2plus': 'Qualquer por 2+',
    
    # DNB
    'dnb_home': 'Casa DNB',
    'dnb_away': 'Fora DNB',
    
    # Half Time
    'home_ht': 'Casa HT',
    'draw_ht': 'Empate HT',
    'away_ht': 'Fora HT',
    
    # Half Time / Full Time
    'ht_ft_1_1': 'HT/FT 1/1',
    'ht_ft_1_x': 'HT/FT 1/X',
    'ht_ft_1_2': 'HT/FT 1/2',
    'ht_ft_x_1': 'HT/FT X/1',
    'ht_ft_x_x': 'HT/FT X/X',
    'ht_ft_x_2': 'HT/FT X/2',
    'ht_ft_2_1': 'HT/FT 2/1',
    'ht_ft_2_x': 'HT/FT 2/X',
    'ht_ft_2_2': 'HT/FT 2/2',
}


# Categorias de mercados
MARKET_CATEGORIES = {
    '1x2': ['home_win', 'draw', 'away_win'],
    'double_chance': ['1x', '12', 'x2'],
    'totals': ['over_0.5', 'under_0.5', 'over_1.5', 'under_1.5', 'over_2.5', 'under_2.5', 
               'over_3.5', 'under_3.5', 'over_4.5', 'under_4.5'],
    'asian': ['over_1.75', 'under_1.75', 'over_2.25', 'under_2.25', 'over_2.75', 'under_2.75',
              'over_3.25', 'under_3.25'],
    'btts': ['btts_yes', 'btts_no'],
    'clean_sheets': ['home_clean_sheet', 'away_clean_sheet'],
    'team_totals': ['home_over_0.5', 'home_under_0.5', 'home_over_1.5', 'home_under_1.5',
                    'home_over_2.5', 'home_under_2.5', 'away_over_0.5', 'away_under_0.5',
                    'away_over_1.5', 'away_under_1.5', 'away_over_2.5', 'away_under_2.5'],
    'odd_even': ['odd_goals', 'even_goals'],
    'margin': ['home_by_1', 'home_by_2plus', 'away_by_1', 'away_by_2plus', 'any_by_1', 'any_by_2plus'],
    'dnb': ['dnb_home', 'dnb_away'],
    'halftime': ['home_ht', 'draw_ht', 'away_ht'],
    'htft': ['ht_ft_1_1', 'ht_ft_1_x', 'ht_ft_1_2', 'ht_ft_x_1', 'ht_ft_x_x', 
             'ht_ft_x_2', 'ht_ft_2_1', 'ht_ft_2_x', 'ht_ft_2_2'],
}


def normalize_market_name(market: str) -> Optional[str]:
    """
    Converte qualquer alias de mercado para o nome canônico.
    
    Args:
        market: Nome do mercado em qualquer formato
        
    Returns:
        str: Nome canônico padronizado, ou None se não reconhecido
        
    Examples:
        >>> normalize_market_name('over_2_5')
        'over_2.5'
        >>> normalize_market_name('1X')
        '1x'
        >>> normalize_market_name('btts')
        'btts_yes'
    """
    if not market:
        return None
    
    # Tentar busca direta (case-insensitive)
    canonical = _ALIAS_TO_CANONICAL.get(market.lower())
    if canonical:
        return canonical
    
    # Tentar variações comuns
    # Exemplo: "over25" → "over_2.5"
    market_lower = market.lower()
    
    # Variação com underscore
    if '_' not in market_lower and '.' not in market_lower:
        # Tentar adicionar ponto em totals
        if market_lower.startswith('over') or market_lower.startswith('under'):
            # over25 → over_2.5
            prefix = 'over' if market_lower.startswith('over') else 'under'
            number = market_lower.replace(prefix, '').replace('_', '')
            if number.isdigit() and len(number) >= 2:
                # Inserir ponto: 25 → 2.5
                number_with_dot = f"{number[0]}.{number[1:]}"
                variant = f"{prefix}_{number_with_dot}"
                canonical = _ALIAS_TO_CANONICAL.get(variant)
                if canonical:
                    return canonical
    
    # Não reconhecido
    return None


def get_market_display_name(market: str) -> str:
    """
    Retorna o nome de exibição do mercado.
    
    Args:
        market: Nome do mercado (pode ser alias ou canônico)
        
    Returns:
        str: Nome para exibição (em português)
    """
    canonical = normalize_market_name(market)
    if canonical:
        return MARKET_DISPLAY_NAMES.get(canonical, canonical)
    return market


def get_market_category(market: str) -> Optional[str]:
    """
    Retorna a categoria do mercado.
    
    Args:
        market: Nome do mercado (pode ser alias ou canônico)
        
    Returns:
        str: Categoria ('1x2', 'totals', 'btts', etc.) ou None
    """
    canonical = normalize_market_name(market)
    if not canonical:
        return None
    
    for category, markets in MARKET_CATEGORIES.items():
        if canonical in markets:
            return category
    
    return None


def get_markets_by_category(category: str) -> List[str]:
    """
    Retorna lista de mercados de uma categoria.
    
    Args:
        category: Nome da categoria ('1x2', 'totals', etc.)
        
    Returns:
        list: Lista de mercados canônicos
    """
    return MARKET_CATEGORIES.get(category, [])


def is_derived_market(market: str) -> bool:
    """
    Verifica se o mercado é derivado (calculado a partir de outros).
    
    Mercados derivados: Double Chance, DNB, Asian Lines
    Mercados base: 1X2, Over/Under inteiros, BTTS
    
    Args:
        market: Nome do mercado (pode ser alias ou canônico)
        
    Returns:
        bool: True se derivado, False se base
    """
    canonical = normalize_market_name(market)
    if not canonical:
        return False
    
    category = get_market_category(canonical)
    return category in ['double_chance', 'dnb', 'asian']
