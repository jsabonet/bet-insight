const ASIAN_GOAL_LINE_PATTERN =
  /^(?:over|under)[_\s]+(?:1[.,_]75|2[.,_](?:25|75)|3[.,_]25)(?:\s+gols?)?$/i;

export function isUnsupportedAsianGoalMarket(market) {
  if (!market || typeof market !== 'object') return false;

  return [market.market, market.market_display, market.market_label, market.original_market].some(
    (value) => typeof value === 'string' && ASIAN_GOAL_LINE_PATTERN.test(value.trim())
  );
}
