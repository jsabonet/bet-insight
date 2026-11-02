"""Shared eligibility and ordering for multiple-strategy candidates."""

import math


def eligible_multiple_candidates(
    candidates,
    match=None,
    min_probability=0.65,
    min_ev_pct=0.0,
):
    """Require a valid price, minimum hit probability, and non-negative EV.

    ``match`` remains accepted for compatibility; club classification does not
    change market eligibility.
    """
    eligible = []

    for candidate in candidates or []:
        probability = _number(candidate.get('probability'))
        odd = _number(candidate.get('market_odd'))
        ev_pct = _number(candidate.get('ev_pct'))
        if (
            probability is not None
            and 0.0 < probability <= 1.0
            and odd is not None
            and odd > 1.0
            and ev_pct is not None
            and probability >= min_probability
            and ev_pct >= min_ev_pct
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