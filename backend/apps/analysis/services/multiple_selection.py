"""Shared ordering for eligible candidates in the multiple strategy."""

import math

from apps.analysis.config.supergiants import (
    is_home_over_market,
    is_protective_supergiant_market,
    is_supergiant_away,
    is_supergiant_match,
)


def eligible_multiple_candidates(
    candidates,
    match=None,
    min_probability=0.65,
    min_odd=1.30,
    max_odd=1.50,
    protective_min_odd=1.15,
):
    """Apply existing multiple candidate thresholds without changing candidates."""
    supergiant_match = is_supergiant_match(match)
    supergiant_away = is_supergiant_away(match)
    eligible = []

    for candidate in candidates or []:
        market = candidate.get('market', '')
        protective_market = is_protective_supergiant_market(market)
        if supergiant_match and not protective_market:
            continue
        if supergiant_away and is_home_over_market(market):
            continue

        probability = _number(candidate.get('probability'), 0.0)
        odd = _number(candidate.get('market_odd'), 0.0)
        candidate_min_odd = (
            protective_min_odd
            if supergiant_match and protective_market
            else min_odd
        )
        if (
            probability >= min_probability
            and candidate_min_odd <= odd <= max_odd
        ):
            eligible.append(candidate)

    return eligible


def rank_multiple_candidates(candidates):
    """Rank candidates by the existing integrated score without changing them."""
    return sorted(candidates or [], key=_multiple_candidate_key, reverse=True)


def _multiple_candidate_key(candidate):
    ranking_score = _number(candidate.get('ranking_score'))
    if ranking_score is None:
        ranking_score = _number(candidate.get('score'))
    if ranking_score is None:
        ranking_score = _number(candidate.get('selection_score'), 0.0)

    contextual_fit = _number(candidate.get('contextual_fit'), 1.0)
    probability = _number(candidate.get('probability'), 0.0)
    return ranking_score, contextual_fit, probability


def _number(value, default=None):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default