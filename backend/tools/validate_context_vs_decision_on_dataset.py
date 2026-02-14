import json
import sys
from pathlib import Path

# Ensure Django app context services import work
sys.path.append(str(Path(__file__).resolve().parents[1]))

from apps.analysis.services.context_analyzer import ContextAnalyzer
from apps.analysis.services.statistical_models import ModelEnsemble
from apps.analysis.services.decision_engine import DecisionEngine


def undot_features(flat: dict) -> dict:
    """Convert dot-keyed flat features to nested dicts expected by analyzers."""
    nested = {}
    for k, v in flat.items():
        parts = k.split('.')
        d = nested
        for p in parts[:-1]:
            if p not in d or not isinstance(d[p], dict):
                d[p] = {}
            d = d[p]
        d[parts[-1]] = v
    return nested


def market_success(market: str, label_text: str, result: dict) -> bool:
    """Evaluate whether a recommended market was successful given match outcome.

    Supports: 'home', 'away', 'draw', 'X2', '1X', 'under_2.5', 'under_1.5',
    'under_3.5', 'btts_yes', 'btts_no', 'dnb_home', 'dnb_away'.
    """
    if market in ('home', 'home_win'):
        return label_text == 'home'
    if market in ('away', 'away_win'):
        return label_text == 'away'
    if market == 'draw':
        return label_text == 'draw'
    if market == 'X2':
        return label_text in ('draw', 'away')
    if market == '1X':
        return label_text in ('draw', 'home')

    # Draw No Bet markets: success only if side wins (draw is void, count as miss)
    if market == 'dnb_home':
        return label_text == 'home'
    if market == 'dnb_away':
        return label_text == 'away'

    # Totals: use total_goals
    total = result.get('total_goals')
    if market == 'under_2.5':
        return total is not None and total <= 2
    if market == 'under_1.5':
        return total is not None and total <= 1
    if market == 'under_3.5':
        return total is not None and total <= 3

    # BTTS: try explicit flag, else infer from goals
    if market in ('btts_yes', 'btts_no'):
        btts = result.get('btts')
        if btts is None:
            hg = result.get('home_goals')
            ag = result.get('away_goals')
            if hg is not None and ag is not None:
                btts = (hg > 0 and ag > 0)
        if btts is not None:
            return (btts is True) if market == 'btts_yes' else (btts is False)

    return False


def pick_context_market(context_analysis: dict) -> str | None:
    """Aggregate context pattern confidences into market scores and pick best market.

    Priority prefers 1x2/double-chance, then totals, then BTTS.
    """
    scores = {}
    patterns = context_analysis.get('patterns', []) if context_analysis else []
    for p in patterns:
        conf = p.get('confidence', 0)
        # Favorable markets list
        for m in p.get('favorable_markets', []) or []:
            scores[m] = scores.get(m, 0) + conf
        # Optional weighted markets
        weights = p.get('market_weights') or {}
        for m, w in weights.items():
            # combine confidence with provided weight
            scores[m] = max(scores.get(m, 0), conf * float(w))

    # If analyzer already provided aggregated scores
    top = context_analysis.get('top_markets') or {}
    if isinstance(top, dict):
        for m, s in top.items():
            scores[m] = max(scores.get(m, 0), s)
    elif isinstance(top, list):
        for item in top:
            if isinstance(item, dict):
                m = item.get('market') or item.get('name')
                s = (
                    item.get('context_score')
                    or item.get('score')
                    or item.get('value')
                    or item.get('context')
                )
                if m is not None and s is not None:
                    scores[m] = max(scores.get(m, 0), float(s))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                m, s = item[0], item[1]
                scores[m] = max(scores.get(m, 0), float(s))

    if not scores:
        return None

    priority = [
        'draw', 'X2', '1X', 'away', 'away_win', 'home', 'home_win',
        'under_2.5', 'under_3.5', 'under_1.5', 'btts_no', 'btts_yes',
        'dnb_away', 'dnb_home'
    ]
    # normalize keys for consistency
    norm_scores = {}
    for k, v in scores.items():
        kk = k
        if kk == 'home_win':
            kk = 'home'
        if kk == 'away_win':
            kk = 'away'
        norm_scores[kk] = v

    # pick highest available by priority
    for cand in priority:
        if cand in norm_scores:
            return cand
    # fallback to absolute max key
    return max(norm_scores.items(), key=lambda x: x[1])[0]


def main():
    # Resolve dataset path relative to backend root
    backend_root = Path(__file__).resolve().parents[1]
    dataset_path = backend_root / 'ml_training' / 'training_dataset_checkpoint.json'
    if not dataset_path.exists():
        print(f"ERROR: Dataset not found at {dataset_path}")
        sys.exit(1)

    data = json.loads(dataset_path.read_text(encoding='utf-8'))
    matches = data.get('data', [])
    total = len(matches)
    if total == 0:
        print("ERROR: No matches in dataset")
        sys.exit(1)

    ctx_hits = 0
    ctx_covered = 0  # matches where a context market was evaluable
    dec_hits = 0
    dec_covered = 0

    context_analyzer = ContextAnalyzer()
    ensemble = ModelEnsemble()
    decision_engine = DecisionEngine()

    for i, m in enumerate(matches, start=1):
        label_text = m.get('label_text')
        result = m.get('result', {})
        flat_features = m.get('features', {})
        features = undot_features(flat_features)

        # Context analysis
        try:
            context_analysis = context_analyzer.analyze(features)
        except Exception:
            context_analysis = {}

        ctx_market = pick_context_market(context_analysis)
        if ctx_market:
            ctx_covered += 1
            if market_success(ctx_market, label_text, result):
                ctx_hits += 1

        # Decision engine primary pick using ensemble
        try:
            home_strength = features.get('strength', {}).get('home_goals_per_game', 1.5)
            away_strength = features.get('strength', {}).get('away_goals_per_game', 1.3)
            weather_impact = features.get('weather', {}).get('goal_impact', 0.0)
            home_defense = features.get('strength', {}).get('home_conceded_per_game', 1.2)
            away_defense = features.get('strength', {}).get('away_conceded_per_game', 1.2)
            league_id = m.get('league_id')

            model_predictions = ensemble.predict(
                features,
                home_strength,
                away_strength,
                weather_impact,
                league_id=league_id,
                home_defense=home_defense,
                away_defense=away_defense,
            )

            decision = decision_engine.make_decision(
                model_predictions,
                features,
                market_odds=None,
                strategy='value',
                context_analysis=context_analysis,
            )

            pick = (decision.get('recommendation', {}) or {}).get('pick')
            # Map display to label
            if pick:
                dec_covered += 1
                if pick in ('Vitória Casa', 'Home Win'):
                    dec_label = 'home'
                elif pick in ('Vitória Fora', 'Away Win'):
                    dec_label = 'away'
                elif pick in ('Empate', 'Draw'):
                    dec_label = 'draw'
                else:
                    dec_label = None

                if dec_label and dec_label == label_text:
                    dec_hits += 1

        except Exception:
            # skip this match for decision coverage
            pass

    ctx_rate = (ctx_hits / ctx_covered) * 100 if ctx_covered else 0.0
    dec_rate = (dec_hits / dec_covered) * 100 if dec_covered else 0.0

    winner = 'ContextAnalyzer' if ctx_rate > dec_rate else 'DecisionEngine'

    print("=== Validation Summary ===")
    print(f"Dataset matches: {total}")
    print(f"ContextAnalyzer: covered={ctx_covered}, hits={ctx_hits}, accuracy={ctx_rate:.2f}%")
    print(f"DecisionEngine: covered={dec_covered}, hits={dec_hits}, accuracy={dec_rate:.2f}%")
    print(f"Winner: {winner}")


if __name__ == '__main__':
    main()
