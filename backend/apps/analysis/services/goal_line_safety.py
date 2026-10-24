"""Helpers for selecting a one-step more conservative full-match goal line."""

import re

from apps.analysis.config.market_standards import normalize_market_name


_TOTAL_MARKET_PATTERN = re.compile(r'^(over|under)_(0\.5|1\.5|2\.5|3\.5|4\.5)$')
_GOAL_LINES = ('0.5', '1.5', '2.5', '3.5', '4.5')


def conservative_total_market(market):
    """Return the adjacent safer full-match goals line, or None for other markets."""
    normalized = normalize_market_name(str(market)) or str(market).lower()
    match = _TOTAL_MARKET_PATTERN.fullmatch(normalized)
    if not match:
        return None

    direction, line = match.groups()
    index = _GOAL_LINES.index(line)
    adjusted_index = index - 1 if direction == 'over' else index + 1
    if adjusted_index < 0 or adjusted_index >= len(_GOAL_LINES):
        return normalized
    return f'{direction}_{_GOAL_LINES[adjusted_index]}'


def normalized_probabilities(probabilities):
    """Return model probabilities keyed by canonical market names."""
    normalized = {}
    for market, probability in (probabilities or {}).items():
        canonical = normalize_market_name(str(market))
        if canonical:
            normalized[canonical] = probability
    return normalized


def goal_market_odd_entry(market, market_odds):
    """Find the raw odds entry for a canonical full-match goals market."""
    odds = market_odds or {}
    for key, value in odds.items():
        if normalize_market_name(str(key)) != market:
            continue
        return value
    return None


def goal_market_odd(market, market_odds):
    """Find the actual bookmaker odd for a canonical full-match goals market."""
    value = goal_market_odd_entry(market, market_odds)
    if isinstance(value, dict):
        value = value.get('value')
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if numeric > 0 else None


def line_adjustment_label(original_market, adjusted_market):
    """Human-readable explanation for a changed full-match goals line."""
    if not original_market or original_market == adjusted_market:
        return ''
    return f'{original_market.replace("_", " ").title()} → {adjusted_market.replace("_", " ").title()}'
