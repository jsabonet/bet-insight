import { DollarSign, TrendingUp, AlertCircle, Target, BarChart3, Percent, Sparkles, Award, Activity } from 'lucide-react';
import { TeamLogo } from '../../utils/logos';

/**
 * VALUE BETS & ODDS - VERSÃO EXPANDIDA E PROFISSIONAL
 * Exibe todos os mercados de apostas com estatísticas completas
 * Design premium similar às melhores casas de apostas
 */
export default function ValueBetsSection({ analysis, match }) {
  if (!analysis?.analysis_data) return null;

  const { fair_odds, market_odds, value_bets, poisson, consensus, recommendation, confidence, risk } = analysis.analysis_data;

  // Probabilidades implícitas do mercado
  const calcImpliedProb = (odd) => odd > 0 ? (1 / odd) * 100 : 0;
  const calcMargin = (odds) => {
    const sum = odds.reduce((acc, odd) => acc + (odd > 0 ? 1/odd : 0), 0);
    return ((sum - 1) * 100).toFixed(2);
  };

  // Mapeamento de keys de mercado para odds
  // fair_odds usa: home_win, draw, away_win
  // market_odds usa: odds_home, odds_draw, odds_away
  const mapKeyToOddKey = (key) => {
    const mapping = {
      'home_win': 'odds_home',
      'draw': 'odds_draw',
      'away_win': 'odds_away',
      'over_2_5': 'odds_over_25',
      'under_2_5': 'odds_under_25',
      'btts_yes': 'odds_btts_yes',
      'btts_no': 'odds_btts_no',
    };
    return mapping[key] || `odds_${key}`;
  };

  // Expected Goals (definir primeiro para usar nos cálculos)
  const homeXG = poisson?.expected_goals?.home;
  const awayXG = poisson?.expected_goals?.away;
  const totalXG = homeXG && awayXG ? homeXG + awayXG : null;

  // MERCADOS PRINCIPAIS
  const mainMarkets = [
    { 
      key: 'home_win', 
      label: 'Vitória Casa', 
      icon: '🏠',
      teamLogo: match?.home_team,
      color: 'emerald',
      modelProb: consensus?.home_win ? (consensus.home_win * 100).toFixed(1) : null
    },
    { 
      key: 'draw', 
      label: 'Empate', 
      icon: '⚖️',
      color: 'gray',
      modelProb: consensus?.draw ? (consensus.draw * 100).toFixed(1) : null
    },
    { 
      key: 'away_win', 
      label: 'Vitória Fora', 
      icon: '✈️',
      teamLogo: match?.away_team,
      color: 'blue',
      modelProb: consensus?.away_win ? (consensus.away_win * 100).toFixed(1) : null
    }
  ];

  // CHANCE DUPLA - Calculada a partir do consensus
  const doubleChanceMarkets = consensus ? [
    {
      key: 'double_1X',
      label: '1X (Casa ou Empate)',
      icon: '🏠⚖️',
      teamLogos: [match?.home_team, null],
      modelProb: ((consensus.home_win + consensus.draw) * 100).toFixed(1)
    },
    {
      key: 'double_X2',
      label: 'X2 (Empate ou Fora)',
      icon: '⚖️✈️',
      teamLogos: [null, match?.away_team],
      modelProb: ((consensus.draw + consensus.away_win) * 100).toFixed(1)
    },
    {
      key: 'double_12',
      label: '12 (Casa ou Fora)',
      icon: '🏠✈️',
      teamLogos: [match?.home_team, match?.away_team],
      modelProb: ((consensus.home_win + consensus.away_win) * 100).toFixed(1)
    }
  ] : [];

  // TOTAL DE GOLS - Múltiplos totais
  const totalGoalsMarkets = poisson?.probabilities ? [
    {
      key: 'over_0_5',
      label: 'Over 0.5',
      icon: '⚽',
      modelProb: ((1 - (poisson.probabilities.home_clean_sheet * poisson.probabilities.away_clean_sheet)) * 100).toFixed(1)
    },
    {
      key: 'under_0_5',
      label: 'Under 0.5',
      icon: '🚫',
      modelProb: ((poisson.probabilities.home_clean_sheet * poisson.probabilities.away_clean_sheet) * 100).toFixed(1)
    },
    {
      key: 'over_1_5',
      label: 'Over 1.5',
      icon: '⚽⚽',
      modelProb: totalXG ? (totalXG > 1.8 ? '70.0' : totalXG > 1.2 ? '55.0' : '30.0') : null
    },
    {
      key: 'under_1_5',
      label: 'Under 1.5',
      icon: '🚫',
      modelProb: totalXG ? (totalXG < 1.2 ? '70.0' : totalXG < 1.8 ? '45.0' : '30.0') : null
    },
    {
      key: 'over_2_5',
      oddKey: 'odds_over_25',
      label: 'Over 2.5',
      icon: '⚽⚽⚽',
      modelProb: (poisson.probabilities.over_2_5 * 100).toFixed(1)
    },
    {
      key: 'under_2_5',
      oddKey: 'odds_under_25',
      label: 'Under 2.5',
      icon: '🚫',
      modelProb: (poisson.probabilities.under_2_5 * 100).toFixed(1)
    },
    {
      key: 'over_3_5',
      label: 'Over 3.5',
      icon: '⚽⚽⚽⚽',
      modelProb: totalXG ? (totalXG > 3.5 ? '50.0' : totalXG > 3.0 ? '35.0' : '15.0') : null
    },
    {
      key: 'under_3_5',
      label: 'Under 3.5',
      icon: '🚫',
      modelProb: totalXG ? (totalXG < 3.0 ? '85.0' : totalXG < 3.5 ? '65.0' : '50.0') : null
    }
  ] : [];

  // AMBAS MARCAM & VARIAÇÕES
  const bttsMarkets = poisson?.probabilities ? [
    {
      key: 'btts_yes',
      oddKey: 'odds_btts_yes',
      label: 'Ambas Marcam - Sim',
      icon: '🎯',
      modelProb: (poisson.probabilities.btts * 100).toFixed(1)
    },
    {
      key: 'btts_no',
      oddKey: 'odds_btts_no',
      label: 'Ambas Marcam - Não',
      icon: '🚫',
      modelProb: ((1 - poisson.probabilities.btts) * 100).toFixed(1)
    },
    {
      key: 'home_clean_sheet',
      label: 'Casa Não Sofre',
      icon: '🛡️',
      modelProb: (poisson.probabilities.home_clean_sheet * 100).toFixed(1)
    },
    {
      key: 'away_clean_sheet',
      label: 'Fora Não Sofre',
      icon: '🛡️',
      modelProb: (poisson.probabilities.away_clean_sheet * 100).toFixed(1)
    }
  ] : [];

  // ÍMPAR/PAR
  const oddEvenMarkets = totalXG ? [
    {
      key: 'odd',
      label: 'Total Gols Ímpar',
      icon: '🔢',
      modelProb: '50.0' // Aproximação
    },
    {
      key: 'even',
      label: 'Total Gols Par',
      icon: '🔢',
      modelProb: '50.0' // Aproximação
    }
  ] : [];

  // 1ª PARTE - Baseado em aproximações
  const firstHalfMarkets = consensus ? [
    {
      key: 'ht_home',
      label: '1ª Parte - Casa',
      icon: '⏱️🏠',
      teamLogo: match?.home_team,
      modelProb: (consensus.home_win * 0.6 * 100).toFixed(1) // 60% da probabilidade total
    },
    {
      key: 'ht_draw',
      label: '1ª Parte - Empate',
      icon: '⏱️⚖️',
      modelProb: ((consensus.draw + 0.2) * 100).toFixed(1) // Empate mais provável no HT
    },
    {
      key: 'ht_away',
      label: '1ª Parte - Fora',
      icon: '⏱️✈️',
      teamLogo: match?.away_team,
      modelProb: (consensus.away_win * 0.6 * 100).toFixed(1)
    }
  ] : [];

  // MERCADOS DE GOLS (simplificado para seção específica)
  const goalMarkets = poisson?.probabilities ? [
    { 
      key: 'btts', 
      oddKey: 'odds_btts_yes',
      label: 'Ambos Marcam', 
      icon: '🎯',
      modelProb: (poisson.probabilities.btts * 100).toFixed(1)
    }
  ] : [];

  // Margem da casa (overround)
  const marketMargin = market_odds?.odds_home && market_odds?.odds_draw && market_odds?.odds_away
    ? calcMargin([market_odds.odds_home, market_odds.odds_draw, market_odds.odds_away])
    : null;

  return (
    <div className="space-y-5">
      {/* Header Premium com Gradiente */}
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-green-500/10 to-emerald-500/10 dark:from-green-500/5 dark:to-emerald-500/5 rounded-xl blur-xl"></div>
        <div className="relative flex items-center justify-between bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-4 border border-green-200/50 dark:border-green-700/30">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500 rounded-lg">
              <DollarSign className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-white">Mercados & Odds</h2>
              <p className="text-xs text-gray-600 dark:text-gray-400">Análise completa de todas as apostas</p>
            </div>
          </div>
          {confidence && (
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-white/80 dark:bg-gray-800/80 rounded-lg border border-gray-200 dark:border-gray-700">
              <Activity className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                {confidence.stars}/5 ★
              </span>
            </div>
          )}
        </div>
      </div>

      {/* ESTATÍSTICAS GERAIS */}
      {(homeXG || marketMargin) && (
        <div className="space-y-3 sm:space-y-4">
          {/* Expected Goals - Largura Total */}
          {homeXG && awayXG && (
            <div className="group relative overflow-hidden bg-gradient-to-br from-emerald-500 to-green-600 dark:from-emerald-600 dark:to-green-700 rounded-xl p-5 sm:p-6 border border-emerald-400/50 dark:border-emerald-700/50 shadow-lg hover:shadow-xl transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-white/90" />
                    <div className="text-sm text-white/90 font-semibold uppercase tracking-wide">Expected Goals (xG)</div>
                  </div>
                  <div className="text-xs text-white/80 bg-white/10 px-3 py-1.5 rounded-full backdrop-blur-sm">
                    Total: <span className="font-bold">{totalXG.toFixed(2)}</span> gols
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="text-center">
                    <div className="text-xs text-white/70 mb-1">Casa</div>
                    <div className="text-4xl sm:text-5xl font-black text-white">
                      {homeXG.toFixed(2)}
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-center">
                    <div className="text-3xl sm:text-4xl font-black text-white/60">-</div>
                  </div>
                  
                  <div className="text-center">
                    <div className="text-xs text-white/70 mb-1">Fora</div>
                    <div className="text-4xl sm:text-5xl font-black text-white">
                      {awayXG.toFixed(2)}
                    </div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs text-white/90">
                    <span className="font-medium">Proporção de gols esperados</span>
                    <span>{((homeXG / (homeXG + awayXG)) * 100).toFixed(0)}% - {((awayXG / (homeXG + awayXG)) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="h-2 bg-white/20 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-white/80 rounded-full transition-all duration-500 shadow-lg"
                      style={{ width: `${(homeXG / (homeXG + awayXG)) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Margem e Clima - Grid Menor */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          {marketMargin && (
            <div className="group relative overflow-hidden bg-gradient-to-br from-purple-500 to-violet-600 dark:from-purple-600 dark:to-violet-700 rounded-xl p-4 border border-purple-400/50 dark:border-purple-700/50 shadow-lg hover:shadow-xl transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative">
                <div className="flex items-center gap-2 mb-2">
                  <Percent className="w-4 h-4 text-white/90" />
                  <div className="text-xs text-white/90 font-semibold uppercase tracking-wide">Margem Casa</div>
                </div>
                <div className="text-3xl font-black text-white mb-1">
                  {marketMargin}<span className="text-xl">%</span>
                </div>
                <div className="text-xs text-white/80 mt-2">
                  Overround do bookmaker
                </div>
                <div className="mt-2 text-xs text-white/70">
                  {parseFloat(marketMargin) < 5 ? '🟢 Margem baixa' : parseFloat(marketMargin) < 8 ? '🟡 Margem normal' : '🔴 Margem alta'}
                </div>
              </div>
            </div>
          )}

          {poisson?.weather_adjusted && (
            <div className="group relative overflow-hidden bg-gradient-to-br from-sky-500 to-blue-600 dark:from-sky-600 dark:to-blue-700 rounded-xl p-4 border border-sky-400/50 dark:border-sky-700/50 shadow-lg hover:shadow-xl transition-all duration-300">
              <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative">
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles className="w-4 h-4 text-white/90" />
                  <div className="text-xs text-white/90 font-semibold uppercase tracking-wide">Clima Ajustado</div>
                </div>
                <div className="text-3xl font-black text-white mb-1">
                  ✓ Ativo
                </div>
                <div className="text-xs text-white/80 mt-2">
                  Previsões ajustadas ao clima
                </div>
                <div className="mt-2 flex items-center gap-1 text-xs text-white/70">
                  <Award className="w-3 h-3" />
                  Maior precisão garantida
                </div>
              </div>
            </div>
          )}
          </div>
        </div>
      )}

      {/* RESULTADO FINAL (1X2) */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-all duration-300">
        <div className="flex items-center gap-2 mb-5">
          <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg">
            <Target className="w-4 h-4 text-white" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white text-base">Resultado Final (1X2)</h3>
          {value_bets && value_bets.length > 0 && (
            <span className="ml-auto text-xs font-bold text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30 px-2 py-1 rounded-full">
              {value_bets.filter(vb => ['home_win', 'draw', 'away_win'].includes(vb.market)).length} Values
            </span>
          )}
        </div>
        
        <div className="space-y-3">
          {mainMarkets.map(({ key, label, icon, teamLogo, color, modelProb }) => {
            const fair = fair_odds?.[key];
            const oddKey = mapKeyToOddKey(key);
            const market = market_odds?.[oddKey];
            
            if (!fair && !market) return null;

            const hasValue = market && fair && market > fair * 1.05;
            const impliedProb = market ? calcImpliedProb(market) : null;
            const valueEdge = market && fair ? (((market / fair) - 1) * 100).toFixed(1) : null;

            return (
              <div
                key={key}
                className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    {teamLogo ? (
                      <TeamLogo team={teamLogo} size="sm" />
                    ) : (
                      <span className="text-xl">{icon}</span>
                    )}
                    <h3 className="font-bold text-gray-900 dark:text-white">{label}</h3>
                  </div>
                  {hasValue && (
                    <span className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-medium px-2 py-1 rounded">
                      +{valueEdge}%
                    </span>
                  )}
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-300">Odd Justa</span>
                    <span className="text-sm font-bold text-gray-900 dark:text-white">
                      {fair?.toFixed(2) || '—'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-300">Odd Mercado</span>
                    <span className="text-sm font-bold text-gray-900 dark:text-white">
                      {market?.toFixed(2) || '—'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-300">Prob. Modelo</span>
                    <span className="text-sm font-bold text-blue-600 dark:text-blue-400">
                      {modelProb ? `${modelProb}%` : '—'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-300">Prob. Implícita</span>
                    <span className="text-sm font-bold text-purple-600 dark:text-purple-400">
                      {impliedProb ? `${impliedProb.toFixed(1)}%` : '—'}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* CHANCE DUPLA */}
      {doubleChanceMarkets.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">⚖️</span>
            <h3 className="font-bold text-gray-900 dark:text-white">Chance Dupla</h3>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {doubleChanceMarkets.map(({ key, label, icon, teamLogos, modelProb }) => (
              <div
                key={key}
                className="bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-lg p-4 border border-gray-300 dark:border-gray-600"
              >
                <div className="text-center">
                  {teamLogos ? (
                    <div className="flex items-center justify-center gap-2 mb-2">
                      {teamLogos[0] ? (
                        <TeamLogo team={teamLogos[0]} size="sm" />
                      ) : (
                        <span className="text-lg">⚖️</span>
                      )}
                      <span className="text-sm font-bold text-gray-400">+</span>
                      {teamLogos[1] ? (
                        <TeamLogo team={teamLogos[1]} size="sm" />
                      ) : (
                        <span className="text-lg">⚖️</span>
                      )}
                    </div>
                  ) : (
                    <div className="text-xl mb-2">{icon}</div>
                  )}
                  <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">{label}</div>
                  <div className="text-lg font-bold text-gray-900 dark:text-white">
                    {modelProb}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TOTAL DE GOLS (Over/Under) */}
      {totalGoalsMarkets.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">⚽</span>
            <h3 className="font-bold text-gray-900 dark:text-white">Total de Gols (Over/Under)</h3>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {totalGoalsMarkets.map(({ key, label, icon, modelProb }) => (
              <div
                key={key}
                className="bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-lg p-3 text-center border border-gray-300 dark:border-gray-600"
              >
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{label}</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {modelProb}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AMBAS MARCAM & CLEAN SHEETS */}
      {bttsMarkets.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">🎯</span>
            <h3 className="font-bold text-gray-900 dark:text-white">Ambas Marcam & Clean Sheets</h3>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {bttsMarkets.map(({ key, label, icon, modelProb }) => (
              <div
                key={key}
                className="bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-lg p-3 text-center border border-gray-300 dark:border-gray-600"
              >
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{label}</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {modelProb}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ÍMPAR/PAR */}
      {oddEvenMarkets.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">🔢</span>
            <h3 className="font-bold text-gray-900 dark:text-white">Total de Gols - Ímpar/Par</h3>
          </div>
          
          <div className="grid grid-cols-2 gap-3">
            {oddEvenMarkets.map(({ key, label, icon, modelProb }) => (
              <div
                key={key}
                className="bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-lg p-3 text-center border border-gray-300 dark:border-gray-600"
              >
                <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{label}</div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {modelProb}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 1ª PARTE (MEIO TEMPO) */}
      {firstHalfMarkets.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">⏱️</span>
            <h3 className="font-bold text-gray-900 dark:text-white">Resultado 1ª Parte (Meio Tempo)</h3>
            <span className="ml-auto text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
              Estimativa
            </span>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {firstHalfMarkets.map(({ key, label, icon, teamLogo, modelProb }) => (
              <div
                key={key}
                className="bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-lg p-3 text-center border border-gray-300 dark:border-gray-600"
              >
                <div className="flex items-center justify-center gap-2 mb-1">
                  {teamLogo && <TeamLogo team={teamLogo} size="sm" />}
                  <div className="text-xs text-gray-600 dark:text-gray-400">{label}</div>
                </div>
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {modelProb}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* PLACARES PROVÁVEIS (do Poisson) */}
      {poisson?.most_likely_scores && poisson.most_likely_scores.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <span className="text-xl">📊</span>
              <h3 className="font-bold text-gray-900 dark:text-white">Placares Mais Prováveis</h3>
            </div>
            <span className="text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
              Top {poisson.most_likely_scores.slice(0, 10).length}
            </span>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {poisson.most_likely_scores.slice(0, 9).map((score, idx) => {
              const isTop = idx < 3;
              return (
                <div
                  key={idx}
                  className={`rounded-lg p-3 text-center border ${
                    isTop
                      ? 'bg-gradient-to-br from-green-50 to-emerald-50 dark:from-gray-800 dark:to-gray-700 border-green-200 dark:border-gray-600'
                      : 'bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 border-gray-300 dark:border-gray-600'
                  }`}
                >
                  <div className="text-sm font-bold text-gray-900 dark:text-white mb-1">
                    {score.score}
                  </div>
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    {(score.probability * 100).toFixed(1)}%
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* VALUE BETS DETECTADOS */}
      {value_bets && value_bets.length > 0 && (
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-5 border-2 border-green-400 dark:border-green-700">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
            <h3 className="font-bold text-green-700 dark:text-green-400">
              🎯 {value_bets.length} Oportunidade{value_bets.length > 1 ? 's' : ''} de Value Detectada{value_bets.length > 1 ? 's' : ''}
            </h3>
          </div>

          <div className="space-y-3">
            {value_bets.map((vb, index) => (
              <div
                key={index}
                className="bg-white dark:bg-gray-800 rounded-lg p-4 border-2 border-green-300 dark:border-green-800"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-bold text-gray-900 dark:text-white mb-1 text-lg">
                      {vb.market_display}
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Probabilidade do modelo: {(vb.model_probability * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div className="bg-green-500 text-white rounded-lg px-3 py-2">
                    <div className="text-xs font-medium">VALUE</div>
                    <div className="text-xl font-black">
                      +{vb.value_pct?.toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm mb-3">
                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded p-2">
                    <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Odd Justa</div>
                    <div className="text-lg font-bold text-gray-900 dark:text-white">{vb.fair_odd?.toFixed(2)}</div>
                  </div>
                  <div className="bg-green-100 dark:bg-green-900/30 rounded p-2">
                    <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Odd Mercado</div>
                    <div className="text-lg font-bold text-green-600 dark:text-green-400">{vb.market_odd?.toFixed(2)}</div>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded p-2">
                    <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Edge</div>
                    <div className="text-lg font-bold text-blue-600 dark:text-blue-400">{(vb.edge * 100).toFixed(1)}%</div>
                  </div>
                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded p-2">
                    <div className="text-xs text-gray-500 dark:text-gray-400 mb-1">Prob. Implícita</div>
                    <div className="text-lg font-bold text-purple-600 dark:text-purple-400">
                      {calcImpliedProb(vb.market_odd).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="bg-green-50 dark:bg-green-900/30 rounded-lg p-3 border border-green-200 dark:border-green-800">
                  <div className="flex items-start gap-2">
                    <span className="text-lg">💡</span>
                    <div>
                      <div className="text-xs font-semibold text-green-700 dark:text-green-400 mb-1">
                        Sugestão de Stake
                      </div>
                      <div className="text-sm text-gray-700 dark:text-gray-300">
                        {vb.stake_suggestion}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SEM VALUE BETS */}
      {(!value_bets || value_bets.length === 0) && (
        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-gray-400 dark:text-gray-500" />
            <div>
              <div className="font-medium text-gray-700 dark:text-gray-300">
                Nenhuma oportunidade de value detectada
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                As odds do mercado estão alinhadas com nossas previsões. Aguarde melhores oportunidades.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ANÁLISE DE RISCO & CONFIANÇA */}
      {confidence && (
        <div className="relative overflow-hidden bg-gradient-to-br from-slate-50 via-gray-50 to-slate-50 dark:from-slate-900/30 dark:via-gray-900/30 dark:to-slate-900/30 rounded-xl p-5 border border-slate-200 dark:border-slate-700 shadow-sm">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-purple-500/5 dark:from-blue-500/3 dark:to-purple-500/3"></div>
          
          <div className="relative flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-gradient-to-br from-slate-600 to-gray-700 rounded-lg">
                <Activity className="w-4 h-4 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900 dark:text-white text-base">Análise de Risco & Confiança</h3>
            </div>
            <div className="flex items-center gap-1.5 bg-gradient-to-r from-yellow-400 to-amber-500 px-3 py-1.5 rounded-lg shadow-md">
              {[...Array(5)].map((_, i) => (
                <span
                  key={i}
                  className={`text-lg transition-all duration-300 ${
                    i < confidence.stars
                      ? 'text-white scale-110'
                      : 'text-white/30 scale-95'
                  }`}
                >
                  ★
                </span>
              ))}
            </div>
          </div>
          
          <div className="relative grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <div className="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide">Nível</div>
              </div>
              <div className="font-bold text-lg text-gray-900 dark:text-white">
                {confidence.level}
              </div>
              <div className="mt-2 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-500"
                  style={{ width: `${(confidence.stars / 5) * 100}%` }}
                ></div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                <BarChart3 className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                <div className="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide">Score</div>
              </div>
              <div className="font-bold text-lg text-gray-900 dark:text-white">
                {confidence.score?.toFixed(2) || 'N/A'}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Precisão do modelo
              </div>
            </div>
            
            <div className={`rounded-xl p-4 shadow-sm border-2 ${
              risk === 'low' ? 'bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-green-400 dark:border-green-700' :
              risk === 'medium' ? 'bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 border-yellow-400 dark:border-yellow-700' :
              'bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20 border-red-400 dark:border-red-700'
            }`}>
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className={`w-4 h-4 ${
                  risk === 'low' ? 'text-green-600 dark:text-green-400' :
                  risk === 'medium' ? 'text-yellow-600 dark:text-yellow-400' :
                  'text-red-600 dark:text-red-400'
                }`} />
                <div className="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase tracking-wide">Risco</div>
              </div>
              <div className={`font-bold text-lg ${
                risk === 'low' ? 'text-green-700 dark:text-green-400' :
                risk === 'medium' ? 'text-yellow-700 dark:text-yellow-400' :
                'text-red-700 dark:text-red-400'
              }`}>
                {risk === 'low' ? '🟢 Baixo' :
                 risk === 'medium' ? '🟡 Médio' :
                 '🔴 Alto'}
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                {risk === 'low' ? 'Boa oportunidade' :
                 risk === 'medium' ? 'Cautela recomendada' :
                 'Alto risco de perda'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
