"""
Thresholds calibrados por mercado baseado em validação real
Fonte: validate_ml_all_markets.py - 71.92% overall em 2,950 partidas

PRINCÍPIO: Quanto menor a acurácia, maior o threshold necessário
para filtrar predições de baixa qualidade.

Acurácia vs Threshold:
- >85%: threshold 0.50 (padrão) - alta precisão, pode confiar
- 70-85%: threshold 0.55 - boa precisão, exigir mais confiança
- 60-70%: threshold 0.60 - precisão moderada, filtrar mais
- 50-60%: threshold 0.65 - baixa precisão, muito conservador
- <50%: DESABILITAR - pior que aleatório

Resultados da Validação (Top/Bottom):
TOP 10 (>80%):
  1. over_0.5: 92.6%
  2. under_0.5: 92.6%
  3. away_over_2.5: 86.7%
  4. over_4.5: 85.1%
  5. away_by_2+: 85.1%
  
BOTTOM 10 (<55%):
  1. odd_goals: 51.5%
  2. even_goals: 51.5%
  3. over_2.5: 52.5%
  4. under_2.5: 52.5%
  5. btts_yes: 54.2%
"""

# Thresholds por mercado (prob mínima para predição)
MARKET_THRESHOLDS = {
    # ===== 1X2 (76.36% categoria) =====
    'home_win': 0.55,       # 76.6%
    'draw': 0.55,           # 73.5%
    'away_win': 0.55,       # 78.9%
    
    # ===== Double Chance (79.10% categoria) =====
    '1X': 0.52,             # 83.1%
    '12': 0.55,             # 73.5%
    'X2': 0.52,             # 80.7%
    
    # ===== Over/Under Standard (75.09% categoria) =====
    'over_0.5': 0.50,       # 92.6% ⭐ EXCELENTE
    'under_0.5': 0.50,      # 92.6% ⭐ EXCELENTE
    'over_1.5': 0.55,       # 76.1%
    'under_1.5': 0.55,      # 76.1%
    'over_2.5': 0.65,       # 52.5% ⚠️ DIFÍCIL
    'under_2.5': 0.65,      # 52.5% ⚠️ DIFÍCIL
    'over_3.5': 0.58,       # 69.1%
    'under_3.5': 0.58,      # 69.1%
    'over_4.5': 0.50,       # 85.1% ⭐ EXCELENTE
    'under_4.5': 0.50,      # 85.1% ⭐ EXCELENTE
    
    # ===== Asian Lines (62.59% categoria) =====
    'over_1.75': 0.58,      # 76.1%
    'under_1.75': 0.58,     # 76.1%
    'over_2.25': 0.65,      # 52.5% ⚠️ DIFÍCIL
    'under_2.25': 0.65,     # 52.5% ⚠️ DIFÍCIL
    'over_2.75': 0.65,      # 52.6% ⚠️ DIFÍCIL
    'under_2.75': 0.65,     # 52.6% ⚠️ DIFÍCIL
    'over_3.25': 0.58,      # 69.1%
    'under_3.25': 0.58,     # 69.1%
    
    # ===== BTTS (54.17% categoria) =====
    'btts_yes': 0.68,       # 54.2% ⚠️ MUITO DIFÍCIL
    'btts_no': 0.68,        # 54.2% ⚠️ MUITO DIFÍCIL
    
    # ===== Clean Sheets (73.29% categoria) =====
    'home_clean_sheet': 0.58,  # 69.5%
    'away_clean_sheet': 0.55,  # 77.1%
    
    # ===== Team Totals (75.66% categoria) =====
    'home_over_0.5': 0.55,  # 77.1%
    'home_under_0.5': 0.55, # 77.1%
    'home_over_1.5': 0.58,  # 69.0%
    'home_under_1.5': 0.58, # 69.0%
    'home_over_2.5': 0.55,  # 79.2%
    'home_under_2.5': 0.55, # 79.2%
    'away_over_0.5': 0.58,  # 69.5%
    'away_under_0.5': 0.58, # 69.5%
    'away_over_1.5': 0.58,  # 72.5%
    'away_under_1.5': 0.58, # 72.5%
    'away_over_2.5': 0.50,  # 86.7% ⭐ EXCELENTE
    'away_under_2.5': 0.50, # 86.7% ⭐ EXCELENTE
    
    # ===== Margins (81.14% categoria) =====
    'home_by_1': 0.55,      # 78.0%
    'home_by_2+': 0.55,     # 76.8%
    'away_by_1': 0.52,      # 84.7%
    'away_by_2+': 0.50,     # 85.1% ⭐ EXCELENTE
    
    # ===== Odd/Even (51.46% categoria) =====
    'odd_goals': None,      # 51.5% ❌ DESABILITADO (aleatório)
    'even_goals': None,     # 51.5% ❌ DESABILITADO (aleatório)
}

# Acurácia validada por mercado (para referência)
MARKET_ACCURACY = {
    'over_0.5': 0.926,
    'under_0.5': 0.926,
    'away_over_2.5': 0.867,
    'away_under_2.5': 0.867,
    'over_4.5': 0.851,
    'under_4.5': 0.851,
    'away_by_2+': 0.851,
    'away_by_1': 0.847,
    '1X': 0.831,
    'X2': 0.807,
    'home_win': 0.766,
    'away_win': 0.789,
    'draw': 0.735,
    '12': 0.735,
    'over_1.5': 0.761,
    'under_1.5': 0.761,
    'btts_yes': 0.542,
    'btts_no': 0.542,
    'over_2.5': 0.525,
    'under_2.5': 0.525,
    'odd_goals': 0.515,
    'even_goals': 0.515,
}

def get_threshold(market_name: str) -> float:
    """
    Retorna threshold calibrado para um mercado.
    
    Args:
        market_name: Nome do mercado (ex: 'over_2.5', 'btts_yes')
        
    Returns:
        Threshold (0.5-0.7) ou None se mercado desabilitado
    """
    # Normalizar nome do mercado
    market_normalized = market_name.lower().replace(' ', '_')
    
    # Buscar threshold
    threshold = MARKET_THRESHOLDS.get(market_normalized, 0.55)  # Default: 0.55
    
    return threshold

def is_market_enabled(market_name: str) -> bool:
    """
    Verifica se mercado está habilitado (não desabilitado por baixa acurácia).
    
    Args:
        market_name: Nome do mercado
        
    Returns:
        True se habilitado, False se desabilitado
    """
    threshold = get_threshold(market_name)
    return threshold is not None

def get_market_quality(market_name: str) -> str:
    """
    Retorna classificação de qualidade do mercado.
    
    Returns:
        'excellent' (>85%), 'good' (70-85%), 'moderate' (60-70%),
        'poor' (50-60%), 'disabled' (<50%)
    """
    accuracy = MARKET_ACCURACY.get(market_name.lower().replace(' ', '_'))
    
    if accuracy is None or accuracy < 0.50:
        return 'disabled'
    elif accuracy >= 0.85:
        return 'excellent'
    elif accuracy >= 0.70:
        return 'good'
    elif accuracy >= 0.60:
        return 'moderate'
    else:
        return 'poor'

def filter_predictions_by_threshold(predictions: dict) -> dict:
    """
    Filtra predições aplicando thresholds calibrados.
    
    Args:
        predictions: Dict com {market_name: probability}
        
    Returns:
        Dict filtrado apenas com predições que passam no threshold
    """
    filtered = {}
    
    for market, prob in predictions.items():
        threshold = get_threshold(market)
        
        # Pular se mercado desabilitado
        if threshold is None:
            continue
        
        # Incluir apenas se probabilidade >= threshold
        if prob >= threshold:
            filtered[market] = prob
    
    return filtered

# Metadata de validação
VALIDATION_METADATA = {
    'total_matches': 2950,
    'validation_date': '2026-02-12',
    'overall_accuracy': 0.7192,
    'total_predictions': 135700,
    'correct_predictions': 97596,
    'best_category': 'Margins (81.14%)',
    'worst_category': 'Odd/Even (51.46%)',
}
