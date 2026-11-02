"""Shadow tracking and conservative evidence checks for DailyBet candidates."""

import logging
import math
from collections import defaultdict
from datetime import datetime

from django.db import connection
from django.utils import timezone

from apps.analysis.models import DailyBetCandidate
from .match_result_sync import (
    build_results_map,
    evaluate_market_result,
    get_result_info,
    normalize_market,
)

logger = logging.getLogger(__name__)

MIN_EVIDENCE_SAMPLES = 100
EVIDENCE_Z_SCORE = 1.96
PROBABILITY_BUCKET_WIDTH = 0.05


def probability_bucket(probability):
    """Return a stable five-percentage-point bucket for a valid probability."""
    try:
        value = float(probability)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(value) or not 0 < value <= 1:
        return None
    lower = min(math.floor((value + 1e-12) / PROBABILITY_BUCKET_WIDTH) * PROBABILITY_BUCKET_WIDTH, 0.95)
    upper = min(lower + PROBABILITY_BUCKET_WIDTH, 1.0)
    return f'{lower:.2f}-{upper:.2f}'


def prediction_date(value):
    """Return a fixture kickoff's local calendar date."""
    kickoff = _parse_datetime(value)
    if kickoff is None:
        return None
    return timezone.localtime(kickoff).date() if timezone.is_aware(kickoff) else kickoff.date()


def shadow_table_available():
    """Return whether the optional shadow schema is installed."""
    return DailyBetCandidate._meta.db_table in connection.introspection.table_names()


def record_shadow_candidates(analyses):
    """Persist each pre-match MULTIPLE candidate once, before ticket generation."""
    if not shadow_table_available():
        logger.error(
            'DailyBet shadow storage is unavailable because table %s is missing; '
            'apply migration analysis.0010_dailybetcandidate. Ticket generation will continue.',
            DailyBetCandidate._meta.db_table,
        )
        return 0

    created = 0
    for analysis in analyses:
        result = analysis.get('multiple_result')
        if not result:
            continue

        payload = result.get('analysis_data') or {}
        top_bets = payload.get('top_bets') or []
        decision = payload.get('decision') or payload
        confidence = decision.get('confidence') or payload.get('confidence') or {}
        risk = decision.get('risk', payload.get('risk', 'high'))
        consensus = payload.get('consensus') or {}
        features = result.get('features') or payload.get('features_summary') or {}
        form = features.get('form') or {}

        rejection = None
        draw_probability = _finite_number(consensus.get('draw')) or 0
        home_form = _finite_number(form.get('home_weighted_form'))
        away_form = _finite_number(form.get('away_weighted_form'))
        if draw_probability > 0.35:
            rejection = 'Empate estimado acima do limite de 35%'
        elif (
            home_form is not None
            and away_form is not None
            and home_form < 1.5
            and away_form < 1.5
        ):
            rejection = 'Ambas as equipas abaixo do limiar de forma'
        elif (_finite_number(confidence.get('stars')) or 0) < 4:
            rejection = 'Confiança inferior a 4 estrelas'
        elif risk not in ('low', 'medium'):
            rejection = f'Risco não permitido: {risk}'

        fixture_id = analysis.get('fixture_id')
        kickoff = _parse_datetime(analysis.get('match_date'))
        if fixture_id is None or kickoff is None:
            logger.warning(
                'Skipping shadow candidates with missing fixture id or kickoff: %s',
                fixture_id,
            )
            continue
        candidate_date = prediction_date(kickoff)
        model_snapshot = _model_snapshot(payload)
        quality_score = analysis.get('quality_score')
        complete_features = (
            payload.get('features_summary', {}).get('complete', {})
            if isinstance(payload.get('features_summary'), dict) else {}
        )
        availability = (
            complete_features.get('_metadata', {}).get('data_availability', {})
            if isinstance(complete_features, dict) else {}
        )
        data_completeness = (
            sum(bool(value) for value in availability.values()) / len(availability) * 100
            if availability else None
        )

        for candidate in top_bets:
            market = normalize_market(candidate.get('market'))
            bucket = probability_bucket(candidate.get('probability'))
            if not market or bucket is None:
                continue

            probability = float(candidate['probability'])
            odd = _finite_number(candidate.get('market_odd'))
            ev_pct = _finite_number(candidate.get('ev_pct'))
            selection_rejection = rejection
            if selection_rejection is None:
                if probability < 0.65:
                    selection_rejection = 'Probabilidade estimada inferior a 65%'
                elif odd is None or odd <= 1:
                    selection_rejection = 'Odd inválida ou indisponível'
                elif ev_pct is None or ev_pct < 0:
                    selection_rejection = 'EV estimado negativo ou indisponível'

            defaults = {
                'league_id': analysis.get('league_id'),
                'league_name': analysis.get('league_name', ''),
                'match_name': f"{analysis.get('home_team', '')} vs {analysis.get('away_team', '')}",
                'pick': str(candidate.get('pick', '')),
                'probability': probability,
                'probability_bucket': bucket,
                'odd': odd,
                'ev_pct': ev_pct,
                'ranking_score': _finite_number(
                    candidate.get('ranking_score', candidate.get('score'))
                ),
                'data_quality_score': _finite_number(quality_score),
                'data_completeness_pct': data_completeness,
                'selection_eligible': selection_rejection is None,
                'exclusion_reason': selection_rejection or 'Elegível para avaliação operacional; observação shadow em curso',
                'source_snapshot': {
                    'candidate': _json_safe(candidate),
                    'analysis': model_snapshot,
                },
            }
            _, was_created = DailyBetCandidate.objects.get_or_create(
                date=candidate_date,
                fixture_id=fixture_id,
                market=market,
                defaults=defaults,
            )
            created += int(was_created)
    return created


def market_evidence(market, probability, before_date, shadow_available=None):
    """Evaluate prior eligible shadow predictions in the same market/probability bin."""
    normalized_market = normalize_market(market)
    bucket = probability_bucket(probability)
    if shadow_available is None:
        shadow_available = shadow_table_available()
    if not shadow_available:
        logger.error(
            'DailyBet shadow evidence is unavailable because table %s is missing; '
            'apply migration analysis.0010_dailybetcandidate.',
            DailyBetCandidate._meta.db_table,
        )
        return {
            'sample_size': 0,
            'wins': 0,
            'win_rate': None,
            'win_rate_lower_95': None,
            'break_even_probability': None,
            'roi_pct': None,
            'sample_sufficient': False,
            'evidence_passed': False,
            'reason': 'Armazenamento shadow indisponível: migration pendente',
            'probability_bucket': bucket,
        }

    rows = list(
        DailyBetCandidate.objects.filter(
            market=normalized_market,
            probability_bucket=bucket,
            selection_eligible=True,
            outcome__in=('won', 'lost'),
            date__lt=before_date,
            odd__gt=1,
        ).values_list('outcome', 'odd')
    ) if normalized_market and bucket else []

    sample_size = len(rows)
    wins = sum(outcome == 'won' for outcome, _ in rows)
    win_rate = wins / sample_size if sample_size else None
    mean_break_even = (
        sum(1 / odd for _, odd in rows) / sample_size if sample_size else None
    )
    roi_pct = (
        (sum(odd if outcome == 'won' else 0 for outcome, odd in rows) - sample_size)
        / sample_size * 100
        if sample_size else None
    )
    lower_bound = wilson_lower_bound(wins, sample_size)
    sample_sufficient = sample_size >= MIN_EVIDENCE_SAMPLES
    evidence_passed = bool(
        sample_sufficient
        and lower_bound is not None
        and mean_break_even is not None
        and lower_bound > mean_break_even
        and roi_pct is not None
        and roi_pct > 0
    )

    if not sample_sufficient:
        reason = f'Evidência insuficiente: {sample_size}/{MIN_EVIDENCE_SAMPLES} previsões liquidadas'
    elif lower_bound <= mean_break_even:
        reason = 'Limite inferior de acerto a 95% não supera o break-even médio'
    elif roi_pct <= 0:
        reason = 'ROI histórico shadow não positivo'
    else:
        reason = 'Critérios históricos de acerto e ROI cumpridos'

    return {
        'sample_size': sample_size,
        'wins': wins,
        'win_rate': win_rate,
        'win_rate_lower_95': lower_bound,
        'break_even_probability': mean_break_even,
        'roi_pct': roi_pct,
        'sample_sufficient': sample_sufficient,
        'evidence_passed': evidence_passed,
        'reason': reason,
        'probability_bucket': bucket,
    }


def wilson_lower_bound(successes, sample_size, z=EVIDENCE_Z_SCORE):
    """Wilson score interval lower bound for a binomial success rate."""
    if sample_size <= 0:
        return None
    rate = successes / sample_size
    denominator = 1 + z * z / sample_size
    center = rate + z * z / (2 * sample_size)
    margin = z * math.sqrt(
        (rate * (1 - rate) + z * z / (4 * sample_size)) / sample_size
    )
    return (center - margin) / denominator


def settle_shadow_candidates(since_date=None):
    """Settle matured shadow predictions from official match results."""
    if not shadow_table_available():
        logger.error(
            'Cannot settle DailyBet shadow predictions because table %s is missing; '
            'apply migration analysis.0010_dailybetcandidate.',
            DailyBetCandidate._meta.db_table,
        )
        return 0

    queryset = DailyBetCandidate.objects.filter(
        outcome='pending',
        date__lte=timezone.localdate(),
    )
    if since_date is not None:
        queryset = queryset.filter(date__gte=since_date)
    candidates = list(queryset)
    if not candidates:
        return 0

    selections = [
        {'fixture_id': candidate.fixture_id, 'date': candidate.date.isoformat()}
        for candidate in candidates
    ]
    results = build_results_map(selections, allow_api=True)
    settled = 0

    for candidate in candidates:
        info = get_result_info(results, {'fixture_id': candidate.fixture_id})
        if not info:
            continue

        status = info.get('status')
        if status == 'cancelled':
            candidate.outcome = 'cancelled'
        elif status != 'finished':
            continue
        else:
            home_score = info.get('home_score')
            away_score = info.get('away_score')
            if home_score is None or away_score is None:
                continue
            match_result = (
                'home' if home_score > away_score
                else 'away' if away_score > home_score
                else 'draw'
            )
            outcome = evaluate_market_result(
                candidate.market, match_result, home_score, away_score
            )
            candidate.outcome = outcome or 'unsupported'
            candidate.actual_result = match_result
            candidate.home_score = home_score
            candidate.away_score = away_score

        candidate.settled_at = timezone.now()
        candidate.save(update_fields=[
            'outcome', 'actual_result', 'home_score', 'away_score', 'settled_at'
        ])
        settled += 1
    return settled


def shadow_performance_report():
    """Return settled eligible shadow performance by market and league."""
    if not shadow_table_available():
        logger.error(
            'Cannot report DailyBet shadow performance because table %s is missing; '
            'apply migration analysis.0010_dailybetcandidate.',
            DailyBetCandidate._meta.db_table,
        )
        return []

    rows = DailyBetCandidate.objects.filter(
        selection_eligible=True,
        outcome__in=('won', 'lost'),
    ).values(
        'market', 'league_id', 'league_name', 'probability', 'odd', 'outcome'
    )
    groups = defaultdict(list)
    for row in rows:
        groups[(row['market'], None, 'Todas as ligas')].append(row)
        groups[(row['market'], row['league_id'], row['league_name'])].append(row)

    report = []
    for (market, league_id, league_name), samples in groups.items():
        count = len(samples)
        wins = sum(sample['outcome'] == 'won' for sample in samples)
        model_brier = sum(
            (sample['probability'] - int(sample['outcome'] == 'won')) ** 2
            for sample in samples
        ) / count
        market_brier = sum(
            (1 / sample['odd'] - int(sample['outcome'] == 'won')) ** 2
            for sample in samples if sample['odd'] and sample['odd'] > 1
        ) / count
        returns = sum(
            sample['odd'] if sample['outcome'] == 'won' else 0
            for sample in samples
        )
        stake = sum(bool(sample['odd'] and sample['odd'] > 1) for sample in samples)
        mean_probability = sum(sample['probability'] for sample in samples) / count
        mean_market_probability = (
            sum(1 / sample['odd'] for sample in samples if sample['odd'] and sample['odd'] > 1)
            / stake if stake else None
        )
        roi_pct = (returns - stake) / stake * 100 if stake else None
        report.append({
            'market': market,
            'league_id': league_id,
            'league': league_name,
            'sample_size': count,
            'win_rate': wins / count,
            'mean_model_probability': mean_probability,
            'mean_market_implied_probability': mean_market_probability,
            'model_brier_score': model_brier,
            'market_brier_score': market_brier,
            'roi_pct': roi_pct,
            'evidence_minimum': MIN_EVIDENCE_SAMPLES,
            'evidence_sufficient': count >= MIN_EVIDENCE_SAMPLES,
        })
    return sorted(report, key=lambda row: (row['sample_size'], row['market']), reverse=True)


def _parse_datetime(value):
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


def _finite_number(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _model_snapshot(payload):
    keys = (
        'consensus', 'poisson', 'model_predictions', 'fair_odds', 'recommendation',
        'confidence', 'risk', 'market_odds', 'features_summary', 'context_analysis',
        'context_decision',
    )
    return _json_safe({key: payload[key] for key in keys if key in payload})


def _json_safe(value):
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if hasattr(value, 'tolist'):
        return _json_safe(value.tolist())
    if hasattr(value, 'item'):
        return _json_safe(value.item())
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)
