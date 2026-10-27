const MARKET_LABELS = {
  home_win: 'Vitória da equipa da casa',
  draw: 'Empate',
  away_win: 'Vitória da equipa visitante',
  '1x': 'Equipa da casa vence ou empata',
  '12': 'Vitória de uma das equipas (sem empate)',
  x2: 'Equipa visitante vence ou empata',
  over_0_5: 'Over 0.5 golos no jogo',
  under_0_5: 'Under 0.5 golos no jogo',
  over_1_5: 'Over 1.5 golos no jogo',
  under_1_5: 'Under 1.5 golos no jogo',
  over_2_5: 'Over 2.5 golos no jogo',
  under_2_5: 'Under 2.5 golos no jogo',
  over_3_5: 'Over 3.5 golos no jogo',
  under_3_5: 'Under 3.5 golos no jogo',
  over_4_5: 'Over 4.5 golos no jogo',
  under_4_5: 'Under 4.5 golos no jogo',
  btts_yes: 'Ambas as equipas marcam',
  btts_no: 'Pelo menos uma equipa não marca',
  home_clean_sheet: 'Equipa da casa não sofre golos',
  away_clean_sheet: 'Equipa visitante não sofre golos',
  home_over_0_5: 'Casa Over 0.5',
  home_under_0_5: 'Casa Under 0.5',
  home_over_1_5: 'Casa Over 1.5',
  home_under_1_5: 'Casa Under 1.5',
  home_over_2_5: 'Casa Over 2.5',
  home_under_2_5: 'Casa Under 2.5',
  away_over_0_5: 'Fora Over 0.5',
  away_under_0_5: 'Fora Under 0.5',
  away_over_1_5: 'Fora Over 1.5',
  away_under_1_5: 'Fora Under 1.5',
  away_over_2_5: 'Fora Over 2.5',
  away_under_2_5: 'Fora Under 2.5',
  odd_goals: 'Número total de golos ímpar',
  even_goals: 'Número total de golos par',
  home_by_1: 'Equipa da casa vence por exatamente 1 golo',
  home_by_2plus: 'Equipa da casa vence por 2 ou mais golos',
  away_by_1: 'Equipa visitante vence por exatamente 1 golo',
  away_by_2plus: 'Equipa visitante vence por 2 ou mais golos',
  any_by_1: 'Vitória por exatamente 1 golo',
  any_by_2plus: 'Vitória por 2 ou mais golos',
  dnb_home: 'Vitória da equipa da casa (empate anula)',
  dnb_away: 'Vitória da equipa visitante (empate anula)',
  home_ht: 'Equipa da casa vence ao intervalo',
  draw_ht: 'Empate ao intervalo',
  away_ht: 'Equipa visitante vence ao intervalo',
  ht_ft_1_1: 'Casa ao intervalo / casa no final',
  ht_ft_1_x: 'Casa ao intervalo / empate no final',
  ht_ft_1_2: 'Casa ao intervalo / visitante no final',
  ht_ft_x_1: 'Empate ao intervalo / casa no final',
  ht_ft_x_x: 'Empate ao intervalo / empate no final',
  ht_ft_x_2: 'Empate ao intervalo / visitante no final',
  ht_ft_2_1: 'Visitante ao intervalo / casa no final',
  ht_ft_2_x: 'Visitante ao intervalo / empate no final',
  ht_ft_2_2: 'Visitante ao intervalo / visitante no final',
};

const MARKET_ALIASES = {
  home: 'home_win',
  home_victory: 'home_win',
  home_win_ft: 'home_win',
  away: 'away_win',
  away_victory: 'away_win',
  away_win_ft: 'away_win',
  tie: 'draw',
  x: 'draw',
  draw_ft: 'draw',
  double_chance_1x: '1x',
  double_chance_12: '12',
  double_chance_x2: 'x2',
  home_or_draw: '1x',
  home_draw: '1x',
  home_or_away: '12',
  home_away: '12',
  draw_or_away: 'x2',
  draw_away: 'x2',
  btts: 'btts_yes',
  both_teams_score: 'btts_yes',
  both_teams_to_score: 'btts_yes',
  both_teams_to_score_yes: 'btts_yes',
  both_teams_to_score_no: 'btts_no',
  btts_not: 'btts_no',
  no_btts: 'btts_no',
  draw_no_bet_home: 'dnb_home',
  draw_no_bet_away: 'dnb_away',
  home_dnb: 'dnb_home',
  away_dnb: 'dnb_away',
  home_cs: 'home_clean_sheet',
  clean_sheet_home: 'home_clean_sheet',
  away_cs: 'away_clean_sheet',
  clean_sheet_away: 'away_clean_sheet',
  home_over05: 'home_over_0_5',
  home_over15: 'home_over_1_5',
  home_over25: 'home_over_2_5',
  home_under05: 'home_under_0_5',
  home_under15: 'home_under_1_5',
  home_under25: 'home_under_2_5',
  away_over05: 'away_over_0_5',
  away_over15: 'away_over_1_5',
  away_over25: 'away_over_2_5',
  away_under05: 'away_under_0_5',
  away_under15: 'away_under_1_5',
  away_under25: 'away_under_2_5',
  home_team_over_0_5: 'home_over_0_5',
  home_team_over_1_5: 'home_over_1_5',
  home_team_over_2_5: 'home_over_2_5',
  home_team_under_0_5: 'home_under_0_5',
  home_team_under_1_5: 'home_under_1_5',
  home_team_under_2_5: 'home_under_2_5',
  away_team_over_0_5: 'away_over_0_5',
  away_team_over_1_5: 'away_over_1_5',
  away_team_over_2_5: 'away_over_2_5',
  away_team_under_0_5: 'away_under_0_5',
  away_team_under_1_5: 'away_under_1_5',
  away_team_under_2_5: 'away_under_2_5',
};

const LEGACY_LABELS = {
  'vitória do time da casa': 'home_win',
  'vitória da casa': 'home_win',
  'vitória do time visitante': 'away_win',
  'vitória fora': 'away_win',
  'casa ou empate': '1x',
  'casa vence ou empata': '1x',
  'casa ou fora': '12',
  'empate ou fora': 'x2',
  'ambos marcam': 'btts_yes',
  'ambos times marcam': 'btts_yes',
  'ambas as equipas marcam': 'btts_yes',
  'ambos não marcam': 'btts_no',
  'ambos times não marcam': 'btts_no',
  'mais de 0,5 golos no jogo': 'over_0_5',
  'mais de 1,5 golos no jogo': 'over_1_5',
  'mais de 2,5 golos no jogo': 'over_2_5',
  'mais de 3,5 golos no jogo': 'over_3_5',
  'menos de 0,5 golos no jogo': 'under_0_5',
  'menos de 1,5 golos no jogo': 'under_1_5',
  'menos de 2,5 golos no jogo': 'under_2_5',
  'menos de 3,5 golos no jogo': 'under_3_5',
};

function normalizeMarketKey(value) {
  const key = String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[.-]/g, '_')
    .replace(/\s+/g, '_')
    .replace(/_+/g, '_');
  return MARKET_ALIASES[key] || key;
}

export function formatMarketLabel(market, marketLabel) {
  const candidates = [market, marketLabel].filter(Boolean);

  for (const candidate of candidates) {
    const key = normalizeMarketKey(candidate);
    if (MARKET_LABELS[key]) return MARKET_LABELS[key];

    const legacyLabelKey = String(candidate).trim().toLowerCase().replace(/\s+/g, ' ');
    const legacyMarket = LEGACY_LABELS[legacyLabelKey];
    if (legacyMarket && MARKET_LABELS[legacyMarket]) {
      return MARKET_LABELS[legacyMarket];
    }

    const totalMatch = key.match(/^(over|under)_(\d+)_(\d+)(?:_gol(?:o|os)?)?$/);
    if (totalMatch) {
      const [, direction, whole, fraction] = totalMatch;
      const threshold = Number(`${whole}.${fraction}`);
      return `${direction === 'over' ? 'Over' : 'Under'} ${threshold} golos no jogo`;
    }

    const textualTotalMatch = legacyLabelKey.match(
      /^(over|under)\s+(\d+(?:[.,]\d+)?)(?:\s+(?:gol(?:o|os)?|goals?))?$/,
    );
    if (textualTotalMatch) {
      const [, direction, rawThreshold] = textualTotalMatch;
      const threshold = rawThreshold.replace(',', '.');
      return `${direction === 'over' ? 'Over' : 'Under'} ${threshold} golos no jogo`;
    }
  }

  const fallback = String(marketLabel || market || 'Mercado').trim();
  return fallback.replace(/_/g, ' ').replace(/\s+/g, ' ');
}
