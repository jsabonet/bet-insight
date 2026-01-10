import React from 'react';

const TeamForm = ({ homeTeam, awayTeam, homeLastMatches, awayLastMatches }) => {
  if ((!homeLastMatches || homeLastMatches.length === 0) && (!awayLastMatches || awayLastMatches.length === 0)) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Últimos Jogos</h3>
        <p className="text-gray-500 dark:text-gray-400">Histórico de jogos não disponível.</p>
      </div>
    );
  }

  const calculateForm = (matches, teamId) => {
    let wins = 0;
    let draws = 0;
    let losses = 0;
    let goalsFor = 0;
    let goalsAgainst = 0;

    matches.forEach((match) => {
      const isHome = match.teams.home.id === teamId;
      const teamGoals = isHome ? match.goals.home : match.goals.away;
      const opponentGoals = isHome ? match.goals.away : match.goals.home;

      goalsFor += teamGoals;
      goalsAgainst += opponentGoals;

      if (teamGoals > opponentGoals) wins++;
      else if (teamGoals < opponentGoals) losses++;
      else draws++;
    });

    const total = matches.length;
    const winPercentage = total > 0 ? (wins / total) * 100 : 0;
    const drawPercentage = total > 0 ? (draws / total) * 100 : 0;
    const lossPercentage = total > 0 ? (losses / total) * 100 : 0;

    return { wins, draws, losses, winPercentage, drawPercentage, lossPercentage, goalsFor, goalsAgainst };
  };

  const homeForm = homeLastMatches && homeLastMatches.length > 0 ? calculateForm(homeLastMatches, homeTeam?.id) : null;
  const awayForm = awayLastMatches && awayLastMatches.length > 0 ? calculateForm(awayLastMatches, awayTeam?.id) : null;

  const renderMatchHistory = (matches, team) => {
    if (!matches || matches.length === 0) return null;

    return (
      <div className="space-y-3">
        {matches.map((match, index) => {
          const matchDate = new Date(match.fixture.date);
          const isHome = match.teams.home.id === team.id;
          const teamScore = isHome ? match.goals.home : match.goals.away;
          const opponentScore = isHome ? match.goals.away : match.goals.home;
          const opponent = isHome ? match.teams.away : match.teams.home;
          
          const isWin = teamScore > opponentScore;
          const isDraw = teamScore === opponentScore;
          const isLoss = teamScore < opponentScore;

          let resultColor = 'bg-gray-600';
          let resultText = 'E';
          if (isWin) {
            resultColor = 'bg-green-600';
            resultText = 'V';
          } else if (isLoss) {
            resultColor = 'bg-red-600';
            resultText = 'D';
          }

          return (
            <div
              key={index}
              className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              {/* Data e Liga - sempre em linha */}
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                  {matchDate.toLocaleDateString('pt-BR')}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400 truncate text-right">
                  {match.league?.name}
                </span>
              </div>
              
              {/* Adversário - sempre em uma linha completa */}
              <div className="flex items-center space-x-2 mb-2">
                <img
                  src={opponent.logo}
                  alt={opponent.name}
                  className="w-6 h-6 flex-shrink-0"
                />
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {isHome ? 'vs' : '@'} {opponent.name}
                </span>
              </div>
              
              {/* Placar e Resultado - sempre juntos e visíveis */}
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-gray-900 dark:text-white">
                  Placar: {teamScore} - {opponentScore}
                </span>
                <span
                  className={`${resultColor} text-white text-xs font-bold w-8 h-8 rounded-full flex items-center justify-center`}
                >
                  {resultText}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">Últimos 5 Jogos</h3>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Time da Casa */}
        {homeForm && (
          <div>
            <div className="flex items-center space-x-3 mb-4">
              {homeTeam?.logo && (
                <img src={homeTeam.logo} alt={homeTeam.name} className="w-8 h-8" />
              )}
              <h4 className="font-semibold text-lg text-gray-900 dark:text-white">{homeTeam?.name}</h4>
            </div>

            {/* Estatísticas */}
            <div className="mb-4 space-y-3">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-500 dark:text-gray-400">Performance</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {homeForm.wins}V - {homeForm.draws}E - {homeForm.losses}D
                </span>
              </div>

              {/* Barra de performance */}
              <div className="w-full h-6 rounded-full overflow-hidden flex">
                <div
                  className="bg-green-600 flex items-center justify-center text-white text-xs font-semibold transition-all"
                  style={{ width: `${homeForm.winPercentage}%` }}
                  title={`Vitórias: ${Math.round(homeForm.winPercentage)}%`}
                >
                  {homeForm.winPercentage > 15 && `${Math.round(homeForm.winPercentage)}%`}
                </div>
                <div
                  className="bg-gray-600 flex items-center justify-center text-white text-xs font-semibold transition-all"
                  style={{ width: `${homeForm.drawPercentage}%` }}
                  title={`Empates: ${Math.round(homeForm.drawPercentage)}%`}
                >
                  {homeForm.drawPercentage > 15 && `${Math.round(homeForm.drawPercentage)}%`}
                </div>
                <div
                  className="bg-red-600 flex items-center justify-center text-white text-xs font-semibold transition-all"
                  style={{ width: `${homeForm.lossPercentage}%` }}
                  title={`Derrotas: ${Math.round(homeForm.lossPercentage)}%`}
                >
                  {homeForm.lossPercentage > 15 && `${Math.round(homeForm.lossPercentage)}%`}
                </div>
              </div>

              {/* Gols */}
              <div className="flex justify-between text-sm pt-2">
                <div>
                  <span className="text-green-600 dark:text-green-400 font-bold">{homeForm.goalsFor}</span>
                  <span className="text-gray-500 dark:text-gray-400 ml-1">Gols Feitos</span>
                </div>
                <div>
                  <span className="text-red-600 dark:text-red-400 font-bold">{homeForm.goalsAgainst}</span>
                  <span className="text-gray-500 dark:text-gray-400 ml-1">Gols Sofridos</span>
                </div>
              </div>
            </div>

            {/* Histórico */}
            {renderMatchHistory(homeLastMatches, homeTeam)}
          </div>
        )}

        {/* Time Visitante */}
        {awayForm && (
          <div>
            <div className="flex items-center space-x-3 mb-4">
              {awayTeam?.logo && (
                <img src={awayTeam.logo} alt={awayTeam.name} className="w-8 h-8" />
              )}
              <h4 className="font-semibold text-lg text-gray-900 dark:text-white">{awayTeam?.name}</h4>
            </div>

            {/* Estatísticas */}
            <div className="mb-4 space-y-3">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-500 dark:text-gray-400">Performance</span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {awayForm.wins}V - {awayForm.draws}E - {awayForm.losses}D
                </span>
              </div>

              {/* Barra de performance */}
              <div className="w-full h-6 rounded-full overflow-hidden flex">
                <div
                  className="bg-green-600 flex items-center justify-center text-white text-xs font-semibold transition-all"
                  style={{ width: `${awayForm.winPercentage}%` }}
                  title={`Vitórias: ${Math.round(awayForm.winPercentage)}%`}
                >
                  {awayForm.winPercentage > 15 && `${Math.round(awayForm.winPercentage)}%`}
                </div>
                <div
                  className="bg-gray-600 flex items-center justify-center text-white text-xs font-semibold transition-all"
                  style={{ width: `${awayForm.drawPercentage}%` }}
                  title={`Empates: ${Math.round(awayForm.drawPercentage)}%`}
                >
                  {awayForm.drawPercentage > 15 && `${Math.round(awayForm.drawPercentage)}%`}
                </div>
                <div
                  className="bg-red-600 flex items-center justify-center text-white text-xs font-semibold transition-all"
                  style={{ width: `${awayForm.lossPercentage}%` }}
                  title={`Derrotas: ${Math.round(awayForm.lossPercentage)}%`}
                >
                  {awayForm.lossPercentage > 15 && `${Math.round(awayForm.lossPercentage)}%`}
                </div>
              </div>

              {/* Gols */}
              <div className="flex justify-between text-sm pt-2">
                <div>
                  <span className="text-green-600 dark:text-green-400 font-bold">{awayForm.goalsFor}</span>
                  <span className="text-gray-500 dark:text-gray-400 ml-1">Gols Feitos</span>
                </div>
                <div>
                  <span className="text-red-600 dark:text-red-400 font-bold">{awayForm.goalsAgainst}</span>
                  <span className="text-gray-500 dark:text-gray-400 ml-1">Gols Sofridos</span>
                </div>
              </div>
            </div>

            {/* Histórico */}
            {renderMatchHistory(awayLastMatches, awayTeam)}
          </div>
        )}
      </div>
    </div>
  );
};

export default TeamForm;
