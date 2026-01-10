import React, { useMemo } from 'react';

const LeagueStandings = ({ standings, homeTeam, awayTeam }) => {
  if (!standings || standings.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Classificação</h3>
        <p className="text-gray-500 dark:text-gray-400">Classificação não disponível.</p>
      </div>
    );
  }

  // Extrair a tabela (normalmente standings[0].league.standings[0])
  const standingsTable = useMemo(() => {
    if (standings[0]?.league?.standings?.[0]) {
      return standings[0].league.standings[0];
    }
    return [];
  }, [standings]);

  const leagueName = standings[0]?.league?.name || 'Competição';
  const leagueLogo = standings[0]?.league?.logo;

  // Encontrar posições dos times
  const homeTeamStanding = standingsTable.find((s) => s.team.id === homeTeam?.id);
  const awayTeamStanding = standingsTable.find((s) => s.team.id === awayTeam?.id);

  // Renderizar linha da forma (últimos 5 jogos)
  const renderForm = (form) => {
    if (!form) return null;

    return (
      <div className="flex space-x-1">
        {form.split('').slice(-5).map((result, index) => {
          let bgColor = 'bg-gray-600';
          if (result === 'W') bgColor = 'bg-green-600';
          else if (result === 'L') bgColor = 'bg-red-600';
          else if (result === 'D') bgColor = 'bg-gray-500';

          return (
            <div
              key={index}
              className={`w-5 h-5 ${bgColor} rounded-full flex items-center justify-center text-white text-xs font-bold`}
              title={result === 'W' ? 'Vitória' : result === 'L' ? 'Derrota' : 'Empate'}
            >
              {result}
            </div>
          );
        })}
      </div>
    );
  };

  // Renderizar linha de time destacado
  const renderHighlightedRow = (teamStanding, isHome) => {
    if (!teamStanding) return null;

    return (
      <div
        className={`bg-gradient-to-r ${
          isHome ? 'from-blue-100 to-blue-200 dark:from-blue-600/20 dark:to-blue-900/20' : 'from-red-100 to-red-200 dark:from-red-600/20 dark:to-red-900/20'
        } border-l-4 ${isHome ? 'border-blue-500 dark:border-blue-500' : 'border-red-500 dark:border-red-500'} rounded-lg p-4 mb-4`}
      >
        <div className="grid grid-cols-12 gap-2 items-center text-sm">
          <div className="col-span-1 text-center font-bold text-xl text-gray-900 dark:text-white">{teamStanding.rank}º</div>
          <div className="col-span-5 flex items-center space-x-2">
            <img
              src={teamStanding.team.logo}
              alt={teamStanding.team.name}
              className="w-6 h-6"
            />
            <span className="font-semibold text-gray-900 dark:text-white truncate">{teamStanding.team.name}</span>
          </div>
          <div className="col-span-1 text-center font-bold text-gray-900 dark:text-white">{teamStanding.points}</div>
          <div className="col-span-2 text-center text-gray-600 dark:text-gray-400">
            {teamStanding.all.win}-{teamStanding.all.draw}-{teamStanding.all.lose}
          </div>
          <div className="col-span-1 text-center text-green-600 dark:text-green-400 font-semibold">
            {teamStanding.all.goals.for}
          </div>
          <div className="col-span-1 text-center text-red-600 dark:text-red-400 font-semibold">
            {teamStanding.all.goals.against}
          </div>
          <div className="col-span-1 text-center font-semibold text-gray-900 dark:text-white">
            {teamStanding.goalsDiff > 0 ? '+' : ''}
            {teamStanding.goalsDiff}
          </div>
        </div>
        <div className="mt-2 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-500 dark:text-gray-400">Forma:</span>
            {renderForm(teamStanding.form)}
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {teamStanding.all.played} jogos
          </span>
        </div>
      </div>
    );
  };

  // Renderizar tabela completa (limitada para mobile)
  const renderFullTable = () => {
    // Pegar top 5 e bottom 3
    const topTeams = standingsTable.slice(0, 5);
    const bottomTeams = standingsTable.slice(-3);

    // Verificar se os times da partida estão fora desses intervalos
    const homeRank = homeTeamStanding?.rank;
    const awayRank = awayTeamStanding?.rank;
    const showDivider = homeRank > 5 && homeRank < standingsTable.length - 2;

    return (
      <div className="hidden md:block overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300">
            <tr>
              <th className="p-2 text-left">#</th>
              <th className="p-2 text-left">Time</th>
              <th className="p-2 text-center">Pts</th>
              <th className="p-2 text-center">J</th>
              <th className="p-2 text-center">V</th>
              <th className="p-2 text-center">E</th>
              <th className="p-2 text-center">D</th>
              <th className="p-2 text-center">GP</th>
              <th className="p-2 text-center">GC</th>
              <th className="p-2 text-center">SG</th>
              <th className="p-2 text-left">Forma</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
            {topTeams.map((team) => {
              const isHomeTeam = team.team.id === homeTeam?.id;
              const isAwayTeam = team.team.id === awayTeam?.id;
              const isHighlighted = isHomeTeam || isAwayTeam;

              return (
                <tr
                  key={team.rank}
                  className={`${
                    isHighlighted
                      ? isHomeTeam
                        ? 'bg-blue-600/10 border-l-4 border-blue-500'
                        : 'bg-red-600/10 border-l-4 border-red-500'
                      : 'hover:bg-gray-700/50'
                  }`}
                >
                  <td className="p-2 font-bold">{team.rank}</td>
                  <td className="p-2">
                    <div className="flex items-center space-x-2">
                      <img src={team.team.logo} alt={team.team.name} className="w-5 h-5" />
                      <span className={isHighlighted ? 'font-semibold' : ''}>
                        {team.team.name}
                      </span>
                    </div>
                  </td>
                  <td className="p-2 text-center font-bold">{team.points}</td>
                  <td className="p-2 text-center">{team.all.played}</td>
                  <td className="p-2 text-center text-green-400">{team.all.win}</td>
                  <td className="p-2 text-center text-gray-400">{team.all.draw}</td>
                  <td className="p-2 text-center text-red-400">{team.all.lose}</td>
                  <td className="p-2 text-center">{team.all.goals.for}</td>
                  <td className="p-2 text-center">{team.all.goals.against}</td>
                  <td className="p-2 text-center">
                    {team.goalsDiff > 0 ? '+' : ''}
                    {team.goalsDiff}
                  </td>
                  <td className="p-2">{renderForm(team.form)}</td>
                </tr>
              );
            })}
            {showDivider && (
              <tr>
                <td colSpan="11" className="p-2 text-center text-gray-500 text-xs">
                  ...
                </td>
              </tr>
            )}
            {bottomTeams.map((team) => {
              const isHomeTeam = team.team.id === homeTeam?.id;
              const isAwayTeam = team.team.id === awayTeam?.id;
              const isHighlighted = isHomeTeam || isAwayTeam;

              return (
                <tr
                  key={team.rank}
                  className={`${
                    isHighlighted
                      ? isHomeTeam
                        ? 'bg-blue-600/10 border-l-4 border-blue-500'
                        : 'bg-red-600/10 border-l-4 border-red-500'
                      : 'hover:bg-gray-700/50'
                  }`}
                >
                  <td className="p-2 font-bold">{team.rank}</td>
                  <td className="p-2">
                    <div className="flex items-center space-x-2">
                      <img src={team.team.logo} alt={team.team.name} className="w-5 h-5" />
                      <span className={isHighlighted ? 'font-semibold' : ''}>
                        {team.team.name}
                      </span>
                    </div>
                  </td>
                  <td className="p-2 text-center font-bold">{team.points}</td>
                  <td className="p-2 text-center">{team.all.played}</td>
                  <td className="p-2 text-center text-green-400">{team.all.win}</td>
                  <td className="p-2 text-center text-gray-400">{team.all.draw}</td>
                  <td className="p-2 text-center text-red-400">{team.all.lose}</td>
                  <td className="p-2 text-center">{team.all.goals.for}</td>
                  <td className="p-2 text-center">{team.all.goals.against}</td>
                  <td className="p-2 text-center">
                    {team.goalsDiff > 0 ? '+' : ''}
                    {team.goalsDiff}
                  </td>
                  <td className="p-2">{renderForm(team.form)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6">
      <div className="flex items-center space-x-3 mb-6">
        {leagueLogo && <img src={leagueLogo} alt={leagueName} className="w-8 h-8" />}
        <h3 className="text-xl font-bold text-gray-900 dark:text-white">Classificação - {leagueName}</h3>
      </div>

      {/* Cards dos times (sempre visível) */}
      <div className="mb-6">
        {homeTeamStanding && renderHighlightedRow(homeTeamStanding, true)}
        {awayTeamStanding && renderHighlightedRow(awayTeamStanding, false)}
      </div>

      {/* Tabela completa (apenas desktop) */}
      {renderFullTable()}

      {/* Legenda mobile */}
      <div className="md:hidden mt-4 text-xs text-gray-500 dark:text-gray-400 space-y-1">
        <p>
          <span className="font-semibold">Pts:</span> Pontos •{' '}
          <span className="font-semibold">V-E-D:</span> Vitórias-Empates-Derrotas
        </p>
        <p>
          <span className="font-semibold">GP:</span> Gols Pró •{' '}
          <span className="font-semibold">GC:</span> Gols Contra •{' '}
          <span className="font-semibold">SG:</span> Saldo de Gols
        </p>
      </div>
    </div>
  );
};

export default LeagueStandings;
