
from __future__ import annotations

import hashlib
import json
import logging
import re
from datetime import date, datetime, timedelta

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from apps.analysis.models import DailyBet, SocialProofTicket

from .match_result_sync import (
    build_results_map,
    extract_fixture_id,
    format_score,
    sync_results_for_date,
)

logger = logging.getLogger(__name__)

KIND_SIMULATION = 'simulation'

VALID_KINDS = {KIND_SIMULATION}

DEFAULT_STAKE_AMOUNT = 10.0
MIN_STAKE_AMOUNT = 5.0
MAX_SIMULATION_LEGS = 5
MAX_SIMULATION_ODD = 20.0
MIN_SIMULATION_LEGS = 2

DISCLOSURES = {
    KIND_SIMULATION: (
        'SIMULAÇÃO PÓS-JOGO: bilhete composto depois de os resultados serem '
        'conhecidos, apenas para demonstração. Não é uma previsão nem um '
        'boletim de aposta. 18+ · Jogue com responsabilidade.'
    ),
}

MARKET_LABELS = {
    'home_win': 'Vitória do Time da Casa',
    'draw': 'Empate',
    'away_win': 'Vitória do Time Visitante',
    'double_chance_1x': 'Casa ou Empate',
    'double_chance_x2': 'Empate ou Fora',
    'double_chance_12': 'Casa ou Fora',
    'btts_yes': 'Ambos Marcam',
    'btts_no': 'Ambos Não Marcam',
    'over_0.5': 'Over 0.5 Gol',
    'over_1.5': 'Over 1.5 Gol',
    'over_2.5': 'Over 2.5 Gol',
    'over_3.5': 'Over 3.5 Gol',
    'under_1.5': 'Under 1.5 Gol',
    'under_2.5': 'Under 2.5 Gol',
    'under_3.5': 'Under 3.5 Gol',
    'home_over_0.5': 'Casa Marca',
    'away_over_0.5': 'Fora Marca',
}


def _as_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    if 'T' in text:
        parsed = parse_datetime(text)
        if parsed is not None:
            return parsed.date()
    return parse_date(text[:10])


def _parse_kickoff(value) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        parsed = parse_datetime(str(value))
        if parsed is None:
            return None
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def market_label(market: str | None) -> str:
    if not market:
        return 'Mercado'
    key = market.strip().lower()
    if key in MARKET_LABELS:
        return MARKET_LABELS[key]
    if key.startswith('over_'):
        return f"Over {key.split('_', 1)[1]} Gol"
    if key.startswith('under_'):
        return f"Under {key.split('_', 1)[1]} Gol"
    return key.replace('_', ' ').title()


def _safe_float(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_stake_amount(value, default: float | None = DEFAULT_STAKE_AMOUNT) -> float:
    """
    Converte o valor da aposta (em MT) para float >= MIN_STAKE_AMOUNT.

    ``None``/vazio devolve ``default`` (ou levanta ValueError quando não há
    default). Valores abaixo do mínimo são rejeitados para não gerar bilhetes
    com stakes irrealistas.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        if default is None:
            raise ValueError('Informe o valor da aposta.')
        return float(default)

    try:
        amount = float(str(value).strip().replace(',', '.'))
    except (TypeError, ValueError):
        raise ValueError('Valor da aposta inválido.')

    if amount < MIN_STAKE_AMOUNT:
        raise ValueError(
            f'O valor da aposta deve ser de pelo menos MT {MIN_STAKE_AMOUNT:g}.'
        )

    return round(amount, 2)


def _leg_payload(selection: dict) -> dict | None:
    fixture_id = extract_fixture_id(selection)
    odd = _safe_float(selection.get('odd'))
    probability = _safe_float(selection.get('probability'))
    if fixture_id is None or odd <= 1.0:
        return None

    return {
        'fixture_id': fixture_id,
        'match': selection.get('match') or '',
        'league': selection.get('league') or '',
        'kickoff': selection.get('date'),
        'market': selection.get('market'),
        'market_label': market_label(selection.get('market')),
        'pick': selection.get('pick') or market_label(selection.get('market')),
        'odd': round(odd, 2),
        'probability': round(probability, 4),
        'result': selection.get('result'),
        'final_score': selection.get('final_score') or '',
    }


def _split_match(match) -> tuple[str, str]:
    """Divide 'Casa vs Fora' em duas equipas."""
    text = str(match or '').strip()
    parts = re.split(r'\s+vs\.?\s+', text, maxsplit=1, flags=re.IGNORECASE)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return text, ''


def _real_market_odd(fixture_id, market: str) -> float | None:
    """
    Odd real de mercado (API-Football) para o mercado escolhido.

    Devolve None quando a odd não está disponível — nesse caso a perna é
    descartada, para nunca apresentar probabilidades inventadas.
    """
    if fixture_id is None:
        return None
    try:
        from .api_football_service import APIFootballService

        odds = APIFootballService().fetch_odds(fixture_id) or {}
    except Exception as exc:  # pragma: no cover - falha de rede/API
        logger.warning('Não foi possível obter odds reais do fixture %s: %s', fixture_id, exc)
        return None

    try:
        value = float(odds.get(market))
    except (TypeError, ValueError):
        return None

    return value if value > 1.0 else None


def _simulation_leg_from_result(info: dict) -> dict | None:
    """Constrói uma perna de simulação a partir de um resultado finalizado."""
    home = info.get('home_score')
    away = info.get('away_score')
    if home is None or away is None:
        return None

    home_name, away_name = _split_match(info.get('match'))

    if home > away:
        market = 'home_win'
        pick = home_name or 'Casa'
    elif away > home:
        market = 'away_win'
        pick = away_name or 'Fora'
    else:
        market = 'draw'
        pick = 'Empate'

    odd = _real_market_odd(info.get('fixture_id'), market)
    if odd is None:
        return None

    return {
        'fixture_id': info.get('fixture_id'),
        'match': info.get('match') or '',
        'league': info.get('league') or '',
        'kickoff': info.get('kickoff'),
        'market': market,
        'market_label': market_label(market),
        'pick': pick,
        'odd': round(odd, 2),
        'probability': round(1.0 / odd, 4),
        'result': 'won',
        'final_score': format_score(info),
    }


def _candidate_hash(target_date, kind: str, legs: list[dict]) -> str:
    payload = {
        'date': target_date.isoformat(),
        'kind': kind,
        'legs': [
            {
                'fixture_id': leg.get('fixture_id'),
                'market': leg.get('market'),
                'kickoff': leg.get('kickoff'),
            }
            for leg in legs
        ],
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def _build_candidate(target_date, kind: str, legs: list[dict], source_bet_ids) -> dict:
    total_odd = 1.0
    combined_probability = 1.0
    for leg in legs:
        total_odd *= leg['odd']
        combined_probability *= leg['probability']

    total_odd = round(total_odd, 2)
    combined_probability = round(combined_probability, 6)
    stake_amount = DEFAULT_STAKE_AMOUNT

    return {
        'date': target_date.isoformat(),
        'kind': kind,
        'kind_display': dict(SocialProofTicket.KIND_CHOICES).get(kind, kind),
        'headline': f"Simulação ({len(legs)})",
        'legs': legs,
        'legs_count': len(legs),
        'total_odd': total_odd,
        'combined_probability': combined_probability,
        'stake_units': stake_amount,
        'potential_return_units': round(stake_amount * total_odd, 2),
        'source_bet_ids': sorted(set(source_bet_ids)),
        'disclosure': DISCLOSURES[kind],
        'snapshot_hash': _candidate_hash(target_date, kind, legs),
        'eligible': True,
        'rejection_reasons': [],
    }


class SocialProofBuilder:
    """Gera candidatos e cria snapshots imutáveis de prova social."""

    @classmethod
    def settle_bets(cls, target_date, results_map=None, allow_api: bool = False) -> int:
        """
        Valida bilhetes pendentes da data antes de montar candidatos.

        Quando ``results_map`` é fornecido (por exemplo, logo após uma
        sincronização com a API-Football), não são feitas chamadas externas.
        Devolve o número de bilhetes efetivamente validados.
        """
        pending = list(
            DailyBet.objects.filter(
                date=target_date,
                is_validated=False,
                status='pending',
            )
        )
        if not pending:
            return 0

        if results_map is None:
            selections = []
            for bet in pending:
                selections.extend(bet.selections or [])
            results_map = build_results_map(
                selections, fallback_date=target_date, allow_api=allow_api
            )

        if not results_map:
            return 0

        validated = 0
        for bet in pending:
            try:
                if bet.validate_result(results_map=results_map):
                    validated += 1
            except Exception:
                logger.exception("Falha ao validar bilhete %s", bet.id)

        return validated

    @classmethod
    def candidates(cls, target_date, kind: str) -> list[dict]:
        if kind not in VALID_KINDS:
            raise ValueError(f"Tipo de prova social inválido: {kind}")

        target = _as_date(target_date) or timezone.localdate()
        cls.settle_bets(target)

        # Simulação pós-jogo: prefere seleções reais já geradas (com odds
        # pré-jogo). Se não houver, compõe o bilhete a partir de partidas
        # finalizadas usando as odds reais dessas partidas.
        candidates = cls._simulation_candidates(target)
        if candidates:
            return candidates
        return cls._simulation_candidates_from_finished(target)

    @classmethod
    def _simulation_candidates(cls, target_date) -> list[dict]:
        """Compõe uma simulação a partir de seleções reais que ganharam."""
        bets = DailyBet.objects.filter(date=target_date)
        best_by_fixture: dict[int, dict] = {}

        for bet in bets:
            for selection in bet.selections or []:
                if selection.get('result') != 'won':
                    continue

                leg = _leg_payload(selection)
                if leg is None:
                    continue

                kickoff = _parse_kickoff(selection.get('date'))
                if kickoff is None or bet.created_at >= kickoff:
                    continue

                leg['_source_bet_id'] = bet.id
                current = best_by_fixture.get(leg['fixture_id'])
                if current is None or leg['probability'] > current['probability']:
                    best_by_fixture[leg['fixture_id']] = leg

        ordered = sorted(
            best_by_fixture.values(),
            key=lambda leg: (leg['probability'], leg['odd']),
            reverse=True,
        )

        chosen = []
        total_odd = 1.0
        for leg in ordered:
            if len(chosen) >= MAX_SIMULATION_LEGS:
                break
            if total_odd * leg['odd'] > MAX_SIMULATION_ODD:
                continue
            chosen.append(leg)
            total_odd *= leg['odd']

        if not chosen or len(chosen) < MIN_SIMULATION_LEGS:
            return []

        source_bet_ids = [leg.pop('_source_bet_id') for leg in chosen]
        return [_build_candidate(target_date, KIND_SIMULATION, chosen, source_bet_ids)]

    @classmethod
    def _simulation_candidates_from_finished(cls, target_date) -> list[dict]:
        """
        Fallback de simulação: compõe um bilhete a partir de partidas já
        finalizadas, sem exigir bilhetes verificados ou seleções pré-jogo.
        """
        finished: list[dict] = []

        # Sincroniza os resultados da data alvo e do dia anterior (jogos
        # que começam tarde podem terminar após a meia-noite local).
        for day in (target_date, target_date - timedelta(days=1)):
            results_map = sync_results_for_date(day) or {}
            for info in results_map.values():
                if info.get('status') != 'finished':
                    continue
                if info.get('home_score') is None or info.get('away_score') is None:
                    continue
                fixture_id = info.get('fixture_id')
                if fixture_id is None:
                    continue
                if any(leg['fixture_id'] == fixture_id for leg in finished):
                    continue
                finished.append(info)

        if not finished:
            return []

        legs: list[dict] = []
        for info in finished:
            leg = _simulation_leg_from_result(info)
            if leg is None:
                continue
            if len(legs) >= MAX_SIMULATION_LEGS:
                break
            legs.append(leg)

        if len(legs) < MIN_SIMULATION_LEGS:
            return []

        return [_build_candidate(target_date, KIND_SIMULATION, legs, [])]

    @classmethod
    def create_ticket(
        cls,
        target_date,
        kind: str,
        user=None,
        snapshot_hash: str | None = None,
        source_bet_ids: list | None = None,
        stake_units=None,
    ):
        """
        Cria (ou devolve) o snapshot correspondente a um candidato.

        Args:
            stake_units: valor da aposta em MT (>= 5), aplicado 1:1 no bilhete.
                Quando omitido usa o valor padrão do candidato.

        Returns:
            tuple[SocialProofTicket, bool]: instância e se foi criada agora.
        """
        target = _as_date(target_date) or timezone.localdate()
        stake_explicit = stake_units is not None and str(stake_units).strip() != ''
        stake = normalize_stake_amount(stake_units)
        candidates = cls.candidates(target, kind)

        if not candidates:
            raise ValueError(
                'Nenhum candidato elegível. Confirme que os resultados já foram '
                'sincronizados e que existem partidas finalizadas para a data.'
            )

        selected = None
        if snapshot_hash:
            selected = next(
                (c for c in candidates if c['snapshot_hash'] == snapshot_hash), None
            )
        elif source_bet_ids:
            wanted = {int(i) for i in source_bet_ids if str(i).isdigit()}
            selected = next(
                (c for c in candidates if wanted.intersection(c['source_bet_ids'])), None
            )

        if selected is None:
            selected = candidates[0]

        defaults = {
            'legs': selected['legs'],
            'source_bet_ids': selected['source_bet_ids'],
            'total_odd': selected['total_odd'],
            'combined_probability': selected['combined_probability'],
            'stake_units': stake,
            'disclosure': selected['disclosure'],
            'created_by': user,
            'meta': {
                'headline': selected['headline'],
                'generated_at': timezone.now().isoformat(),
                'stake_units': stake,
            },
        }

        ticket, created = SocialProofTicket.objects.get_or_create(
            date=target,
            kind=kind,
            snapshot_hash=selected['snapshot_hash'],
            defaults=defaults,
        )

        if created:
            logger.info(
                "Snapshot de prova social criado: %s (%s, %s pernas, MT %s)",
                ticket.ticket_code,
                kind,
                len(selected['legs']),
                stake,
            )
        elif stake_explicit:
            # O admin indicou um valor ao gerar: aplica-o ao snapshot existente.
            ticket = cls.update_stake(ticket, stake)

        return ticket, created

    @classmethod
    def update_stake(cls, ticket, stake_units) -> SocialProofTicket:
        """Grava o valor da aposta (MT) escolhido pelo admin no snapshot."""
        stake = normalize_stake_amount(stake_units)
        if float(ticket.stake_units or 0) == stake:
            return ticket

        ticket.stake_units = stake
        meta = dict(ticket.meta or {})
        meta['stake_units'] = stake
        ticket.meta = meta
        ticket.save(update_fields=['stake_units', 'meta'])
        return ticket
