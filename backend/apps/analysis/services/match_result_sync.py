"""
Sincronização de resultados oficiais e resolução de seleções.

Os bilhetes gerados guardam o ID do fixture da API-Football, que não é
necessariamente o mesmo ID local de Match. Este módulo centraliza:

1. Atualização de Match (status e placar) a partir da API-Football.
2. Construção de um mapa ``fixture_id -> resultado`` usado na validação.
3. Avaliação do mercado de uma seleção contra o resultado real.
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime, timedelta

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from apps.matches.models import Match
from apps.matches.services.football_api import FootballAPIService

logger = logging.getLogger(__name__)

FINISHED_STATUSES = {'FT', 'AET', 'PEN'}
CANCELLED_STATUSES = {'CANC', 'ABD', 'AWD', 'WO'}
POSTPONED_STATUSES = {'PST'}
SCHEDULED_STATUSES = {'NS', 'TBD'}

STATUS_MAP = {
    **{s: 'finished' for s in FINISHED_STATUSES},
    **{s: 'cancelled' for s in CANCELLED_STATUSES},
    **{s: 'postponed' for s in POSTPONED_STATUSES},
    **{s: 'scheduled' for s in SCHEDULED_STATUSES},
}

MARKET_ALIASES = {
    '1x': 'double_chance_1x',
    'x2': 'double_chance_x2',
    '12': 'double_chance_12',
    'home': 'home_win',
    'away': 'away_win',
    'x': 'draw',
}


def normalize_status(short_status: str | None) -> str:
    """Converte o status curto da API-Football para o status interno."""
    if not short_status:
        return 'scheduled'
    short_status = str(short_status).upper()
    if short_status in STATUS_MAP:
        return STATUS_MAP[short_status]
    if short_status in {'1H', 'HT', '2H', 'ET', 'BT', 'P', 'SUSP', 'INT', 'LIVE'}:
        return 'live'
    return 'scheduled'


def _as_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return timezone.localtime(value).date() if timezone.is_aware(value) else value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    if 'T' in text:
        parsed = parse_datetime(text)
        if parsed is not None:
            if timezone.is_aware(parsed):
                return timezone.localtime(parsed).date()
            return parsed.date()
    return parse_date(text[:10])


def extract_fixture_id(selection: dict) -> int | None:
    """
    Extrai o ID do fixture de uma seleção.

    ``fixture_id``/``api_fixture_id`` têm prioridade. ``match_id`` é mantido
    como fallback porque os bilhetes antigos foram gravados com o ID da API
    nesse campo.
    """
    for key in ('fixture_id', 'api_fixture_id', 'match_id'):
        value = (selection or {}).get(key)
        if value in (None, ''):
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            continue
    return None


def normalize_market(market: str | None) -> str:
    key = (market or '').strip().lower()
    if not key:
        return ''
    if key in MARKET_ALIASES:
        return MARKET_ALIASES[key]

    from apps.analysis.config.market_standards import normalize_market_name

    canonical = normalize_market_name(key)
    if canonical:
        return canonical

    # Variantes escritas à mão, ex.: "over2_5" ou "under1-5"
    match = re.match(r'^(over|under)[_-]?(\d+)[._-]?(\d+)?$', key)
    if match:
        whole, fraction = match.group(2), match.group(3)
        return f"{match.group(1)}_{whole}.{fraction}" if fraction else f"{match.group(1)}_{whole}"

    return key


def evaluate_market_result(
    market: str,
    match_result: str | None,
    home_score: int | None,
    away_score: int | None,
) -> str | None:
    """
    Avalia uma seleção contra o resultado final.

    Retorna ``'won'``, ``'lost'`` ou ``None`` quando o mercado não é suportado.
    """
    market = normalize_market(market)
    home_score = home_score or 0
    away_score = away_score or 0
    total_goals = home_score + away_score

    if match_result is None:
        return None

    if market == 'home_win':
        return 'won' if match_result == 'home' else 'lost'
    if market == 'away_win':
        return 'won' if match_result == 'away' else 'lost'
    if market == 'draw':
        return 'won' if match_result == 'draw' else 'lost'
    if market == 'double_chance_1x':
        return 'won' if match_result in ('home', 'draw') else 'lost'
    if market == 'double_chance_x2':
        return 'won' if match_result in ('draw', 'away') else 'lost'
    if market == 'double_chance_12':
        return 'won' if match_result in ('home', 'away') else 'lost'

    if market.startswith('over_'):
        try:
            threshold = float(market.split('_', 1)[1])
        except (IndexError, ValueError):
            return None
        return 'won' if total_goals > threshold else 'lost'
    if market.startswith('under_'):
        try:
            threshold = float(market.split('_', 1)[1])
        except (IndexError, ValueError):
            return None
        return 'won' if total_goals < threshold else 'lost'
    if market == 'btts_yes':
        return 'won' if home_score > 0 and away_score > 0 else 'lost'
    if market == 'btts_no':
        return 'won' if home_score == 0 or away_score == 0 else 'lost'

    if market.startswith('home_over_'):
        try:
            threshold = float(market.rsplit('_', 1)[1])
        except (IndexError, ValueError):
            return None
        return 'won' if home_score > threshold else 'lost'
    if market.startswith('home_under_'):
        try:
            threshold = float(market.rsplit('_', 1)[1])
        except (IndexError, ValueError):
            return None
        return 'won' if home_score < threshold else 'lost'
    if market.startswith('away_over_'):
        try:
            threshold = float(market.rsplit('_', 1)[1])
        except (IndexError, ValueError):
            return None
        return 'won' if away_score > threshold else 'lost'
    if market.startswith('away_under_'):
        try:
            threshold = float(market.rsplit('_', 1)[1])
        except (IndexError, ValueError):
            return None
        return 'won' if away_score < threshold else 'lost'

    if market == 'home_clean_sheet':
        return 'won' if away_score == 0 else 'lost'
    if market == 'away_clean_sheet':
        return 'won' if home_score == 0 else 'lost'
    if market == 'odd_goals':
        return 'won' if total_goals % 2 == 1 else 'lost'
    if market == 'even_goals':
        return 'won' if total_goals % 2 == 0 else 'lost'

    home_margin = home_score - away_score
    away_margin = away_score - home_score
    if market == 'home_by_1':
        return 'won' if home_margin == 1 else 'lost'
    if market == 'home_by_2plus':
        return 'won' if home_margin >= 2 else 'lost'
    if market == 'away_by_1':
        return 'won' if away_margin == 1 else 'lost'
    if market == 'away_by_2plus':
        return 'won' if away_margin >= 2 else 'lost'
    if market == 'any_by_1':
        return 'won' if abs(home_margin) == 1 else 'lost'
    if market == 'any_by_2plus':
        return 'won' if abs(home_margin) >= 2 else 'lost'

    return None


def _result_from_match(match: Match) -> dict:
    return {
        'fixture_id': match.api_football_id,
        'status': match.status,
        'home_score': match.home_score,
        'away_score': match.away_score,
        'kickoff': match.match_date.isoformat() if match.match_date else None,
        'league': match.league.name if match.league_id else '',
        'match': f"{match.home_team.name} vs {match.away_team.name}",
    }


def _result_from_fixture(fixture: dict) -> dict | None:
    try:
        fixture_id = fixture['fixture']['id']
    except (KeyError, TypeError):
        return None

    short_status = (fixture.get('fixture', {}).get('status') or {}).get('short')
    goals = fixture.get('goals') or {}
    teams = fixture.get('teams') or {}
    league = fixture.get('league') or {}

    return {
        'fixture_id': fixture_id,
        'status': normalize_status(short_status),
        'short_status': short_status,
        'home_score': goals.get('home'),
        'away_score': goals.get('away'),
        'kickoff': (fixture.get('fixture') or {}).get('date'),
        'league': league.get('name', ''),
        'match': (
            f"{(teams.get('home') or {}).get('name', '')} vs "
            f"{(teams.get('away') or {}).get('name', '')}"
        ).strip(),
    }


def validate_match_analyses(match: Match) -> None:
    """Persist result evaluations for every analysis of a completed match."""
    if match.get_result() is None:
        return

    for analysis in match.analyses.all():
        analysis.validate_result()


def sync_results_for_date(target_date) -> dict[str, dict]:
    """
    Busca os fixtures de uma data e atualiza os Match existentes.

    Devolve ``{str(fixture_id): resultado}`` independentemente de o fixture
    existir na base de dados local.
    """
    target = _as_date(target_date) or timezone.localdate()
    date_str = target.isoformat()

    response = FootballAPIService().get_fixtures_by_date(date_str)
    if not response or not response.get('success'):
        logger.warning("Falha ao sincronizar resultados de %s: %s", date_str, response)
        return {}

    results: dict[str, dict] = {}
    updated = 0

    for fixture in response.get('fixtures', []):
        info = _result_from_fixture(fixture)
        if not info:
            continue
        results[str(info['fixture_id'])] = info

        match = Match.objects.filter(api_football_id=info['fixture_id']).first()
        if not match:
            continue

        fields = []
        if match.status != info['status']:
            match.status = info['status']
            fields.append('status')
        if info['home_score'] is not None and match.home_score != info['home_score']:
            match.home_score = info['home_score']
            fields.append('home_score')
        if info['away_score'] is not None and match.away_score != info['away_score']:
            match.away_score = info['away_score']
            fields.append('away_score')

        if fields:
            match.save(update_fields=fields)
            updated += 1

        if (
            info['status'] == 'finished'
            and info['home_score'] is not None
            and info['away_score'] is not None
        ):
            validate_match_analyses(match)

    logger.info(
        "Sincronização %s: %s fixtures, %s partidas locais atualizadas",
        date_str,
        len(results),
        updated,
    )
    return results


def build_results_map(selections, fallback_date=None, allow_api: bool = True) -> dict[str, dict]:
    """
    Constrói o mapa de resultados necessário para validar uma lista de seleções.

    Primeiro usa a base de dados local; se ``allow_api`` for verdadeiro, busca
    na API as datas que ainda tenham fixtures sem resultado local.
    """
    selections = list(selections or [])
    fixture_ids = {extract_fixture_id(s) for s in selections}
    fixture_ids.discard(None)

    results: dict[str, dict] = {}

    if fixture_ids:
        for match in Match.objects.filter(api_football_id__in=fixture_ids).select_related(
            'league', 'home_team', 'away_team'
        ):
            results[str(match.api_football_id)] = _result_from_match(match)

    if not allow_api or len(results) >= len(fixture_ids):
        return results

    dates = set()
    for selection in selections:
        fixture_id = extract_fixture_id(selection)
        if fixture_id is None or str(fixture_id) in results:
            continue
        parsed = _as_date(selection.get('date'))
        if parsed:
            dates.add(parsed)

    if not dates and fallback_date:
        dates.add(_as_date(fallback_date))

    # Também tenta o dia anterior: jogos que começam tarde podem terminar
    # depois da meia-noite local.
    if dates:
        dates.update(d - timedelta(days=1) for d in list(dates))

    for date_value in sorted(d for d in dates if d):
        api_results = sync_results_for_date(date_value)
        for key, value in api_results.items():
            results.setdefault(key, value)

    return results


def get_result_info(results: dict[str, dict], selection: dict) -> dict | None:
    fixture_id = extract_fixture_id(selection)
    if fixture_id is None:
        return None
    return results.get(str(fixture_id))


def format_score(info: dict | None) -> str:
    if not info:
        return ''
    home = info.get('home_score')
    away = info.get('away_score')
    if home is None or away is None:
        return ''
    return f"{home}-{away}"
