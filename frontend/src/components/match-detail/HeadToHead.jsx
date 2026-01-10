import React, { useMemo } from 'react';

const HeadToHead = ({ h2h, homeTeam, awayTeam }) => {
  if (!h2h || h2h.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Confrontos Diretos</h3>
        <p className="text-gray-500 dark:text-gray-400">Histórico de confrontos não disponível.</p>
      </div>
    );
  }

  // Calcular estatísticas
  const stats = useMemo(() => {
    let homeWins = 0;
    let awayWins = 0;
    let draws = 0;
    let homeGoals = 0;
    let awayGoals = 0;
    let homeWinsAtHome = 0;
    let awayWinsAway = 0;
    let homeGamesAtHome = 0;
    let awayGamesAway = 0;

    h2h.forEach((match) => {
      const homeGoalsInMatch = match.goals.home;
      const awayGoalsInMatch = match.goals.away;
      const isHomeTeamHome = match.teams.home.id === homeTeam?.id;

      if (homeGoalsInMatch > awayGoalsInMatch) {
        if (isHomeTeamHome) {
          homeWins++;
          homeWinsAtHome++;
        } else {
          awayWins++;
        }
      } else if (awayGoalsInMatch > homeGoalsInMatch) {
        if (isHomeTeamHome) {
          awayWins++;
          awayWinsAway++;
        } else {
          homeWins++;
        }
      } else {
        draws++;
      }

      if (isHomeTeamHome) {
        homeGoals += homeGoalsInMatch;
        awayGoals += awayGoalsInMatch;
        homeGamesAtHome++;
      } else {
        homeGoals += awayGoalsInMatch;
        awayGoals += homeGoalsInMatch;
        awayGamesAway++;
      }
    });

    const total = homeWins + draws + awayWins;
    const homeWinPercentage = total > 0 ? (homeWins / total) * 100 : 0;
    const drawPercentage = total > 0 ? (draws / total) * 100 : 0;
    const awayWinPercentage = total > 0 ? (awayWins / total) * 100 : 0;

    const homePerformanceAtHome = homeGamesAtHome > 0 ? (homeWinsAtHome / homeGamesAtHome) * 100 : 0;
    const awayPerformanceAway = awayGamesAway > 0 ? (awayWinsAway / awayGamesAway) * 100 : 0;

    return {
      homeWins,
      awayWins,
      draws,
      homeGoals,
      awayGoals,
      homeWinPercentage,
      drawPercentage,
      awayWinPercentage,
      homePerformanceAtHome,
      awayPerformanceAway,
    };
  }, [h2h, homeTeam, awayTeam]);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Confrontos Diretos (H2H)</h3>

      {/* Resumo Estatístico */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            {homeTeam?.logo && (
              <img src={homeTeam.logo} alt={homeTeam.name} className="w-8 h-8" />
            )}
            <span className="font-semibold text-lg text-gray-900 dark:text-white">{stats.homeWins}V</span>
          </div>
          <span className="text-gray-500 dark:text-gray-400 font-semibold text-lg">{stats.draws}E</span>
          <div className="flex items-center space-x-3">
            <span className="font-semibold text-lg text-gray-900 dark:text-white">{stats.awayWins}V</span>
            {awayTeam?.logo && (
              <img src={awayTeam.logo} alt={awayTeam.name} className="w-8 h-8" />
            )}
          </div>
        </div>

        {/* Barra de vitórias */}
        <div className="w-full h-8 rounded-full overflow-hidden flex mb-6">
          <div
            className="bg-blue-600 flex items-center justify-center text-white text-sm font-semibold transition-all"
            style={{ width: `${stats.homeWinPercentage}%` }}
          >
            {stats.homeWinPercentage > 15 && `${Math.round(stats.homeWinPercentage)}%`}
          </div>
          <div
            className="bg-gray-600 flex items-center justify-center text-white text-sm font-semibold transition-all"
            style={{ width: `${stats.drawPercentage}%` }}
          >
            {stats.drawPercentage > 15 && `${Math.round(stats.drawPercentage)}%`}
          </div>
          <div
            className="bg-red-600 flex items-center justify-center text-white text-sm font-semibold transition-all"
            style={{ width: `${stats.awayWinPercentage}%` }}
          >
            {stats.awayWinPercentage > 15 && `${Math.round(stats.awayWinPercentage)}%`}
          </div>
        </div>

        {/* Métricas de desempenho em casa/fora */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500 dark:text-gray-400">Desempenho em Casa</span>
              <span className="text-sm font-semibold text-gray-900 dark:text-white">{Math.round(stats.homePerformanceAtHome)}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-blue-600 h-full rounded-full transition-all"
                style={{ width: `${stats.homePerformanceAtHome}%` }}
              ></div>
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500 dark:text-gray-400">Desempenho Fora</span>
              <span className="text-sm font-semibold text-gray-900 dark:text-white">{Math.round(stats.awayPerformanceAway)}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-red-500 to-red-600 h-full rounded-full transition-all"
                style={{ width: `${stats.awayPerformanceAway}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Média de gols */}
        <div className="flex justify-around text-center">
          <div>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.homeGoals}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Gols {homeTeam?.name}</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-600 dark:text-gray-400">{stats.homeGoals + stats.awayGoals}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Total de Gols</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">{stats.awayGoals}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Gols {awayTeam?.name}</p>
          </div>
        </div>
      </div>

      {/* Histórico de Partidas */}
      <div className="space-y-3">
        <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-4">Histórico de Partidas</h4>
        {h2h.map((match, index) => {
          const matchDate = new Date(match.fixture.date);
          const homeScore = match.goals.home;
          const awayScore = match.goals.away;
          const isHomeWin = homeScore > awayScore;
          const isAwayWin = awayScore > homeScore;

          return (
            <div
              key={index}
              className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {matchDate.toLocaleDateString('pt-BR')}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">{match.league?.name}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 flex-1">
                  <img
                    src={match.teams.home.logo}
                    alt={match.teams.home.name}
                    className="w-6 h-6"
                  />
                  <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {match.teams.home.name}
                  </span>
                </div>
                <div className="flex items-center space-x-4 mx-4">
                  <span
                    className={`text-lg font-bold ${
                      isHomeWin ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'
                    }`}
                  >
                    {homeScore}
                  </span>
                  <span className="text-gray-400 dark:text-gray-500">-</span>
                  <span
                    className={`text-lg font-bold ${
                      isAwayWin ? 'text-green-600 dark:text-green-400' : 'text-gray-500 dark:text-gray-400'
                    }`}
                  >
                    {awayScore}
                  </span>
                </div>
                <div className="flex items-center space-x-3 flex-1 justify-end">
                  <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {match.teams.away.name}
                  </span>
                  <img
                    src={match.teams.away.logo}
                    alt={match.teams.away.name}
                    className="w-6 h-6"
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default HeadToHead;
