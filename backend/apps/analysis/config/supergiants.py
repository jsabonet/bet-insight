"""Curated API-Football IDs for clubs commonly treated as elite opponents.

This is an operational shortlist, not an official or permanent ranking.
Review it periodically as clubs and competition coverage change.
"""

import re


SUPERGIANT_TEAM_IDS = frozenset({
    # England
    33,  # Manchester United
    40,  # Liverpool
    42,  # Arsenal
    47,  # Tottenham
    49,  # Chelsea
    50,  # Manchester City
    # Spain
    529,  # Barcelona
    530,  # Atletico Madrid
    541,  # Real Madrid
    # Germany
    157,  # Bayern Munich
    165,  # Borussia Dortmund
    168,  # Bayer Leverkusen
    173,  # RB Leipzig
    # Italy
    489,  # AC Milan
    492,  # Napoli
    496,  # Juventus
    505,  # Inter Milan
    # France
    85,  # Paris Saint-Germain
    # Portugal
    211,  # Benfica
    212,  # Porto
    228,  # Sporting CP
    # Netherlands
    194,  # Ajax
    197,  # PSV
    209,  # Feyenoord
    # South America
    127,  # Flamengo
    121,  # Palmeiras
    1064,  # Boca Juniors
    1065,  # River Plate
    # Saudi Arabia
    2931,  # Al-Hilal
})

SUPERGIANT_PROTECTIVE_MARKETS = frozenset({
    '1x',
    'x2',
    'double_chance_1x',
    'double_chance_x2',
    'under_3.5',
    'under_4.5',
    'under_3_5',
    'under_4_5',
})


def _team_api_id(team):
    if team is None:
        return None
    value = (
        getattr(team, 'api_football_id')
        if hasattr(team, 'api_football_id')
        else getattr(team, 'id', None)
    )
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def is_supergiant_team(team):
    return _team_api_id(team) in SUPERGIANT_TEAM_IDS


def is_supergiant_match(match):
    return bool(
        match
        and (
            is_supergiant_team(getattr(match, 'home_team', None))
            or is_supergiant_team(getattr(match, 'away_team', None))
        )
    )


def is_supergiant_away(match):
    return bool(match and is_supergiant_team(getattr(match, 'away_team', None)))


def is_protective_supergiant_market(market):
    normalized = str(market or '').strip().lower()
    if normalized in SUPERGIANT_PROTECTIVE_MARKETS:
        return True

    compact = normalized.replace('.', '_')
    if compact in SUPERGIANT_PROTECTIVE_MARKETS:
        return True

    return bool(re.fullmatch(r'double_chance_(1x|x2)', compact))


def is_home_over_market(market):
    normalized = str(market or '').strip().lower().replace('.', '_')
    return bool(re.match(r'^home_(?:team_)?over(?:_|$)', normalized))
