import { Users, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

/**
 * ESCALAÇÕES (LINEUPS)
 * Exibe campo de futebol com formações táticas, jogadores e substitutos
 */
export default function Lineups({ lineups, match }) {
  const [selectedTeam, setSelectedTeam] = useState('home');
  const [showSubstitutes, setShowSubstitutes] = useState(false);

  if (!lineups || lineups.length === 0) {
    return (
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-700 rounded-xl p-6 text-center">
        <Users className="w-12 h-12 text-yellow-600 dark:text-yellow-400 mx-auto mb-3" />
        <p className="text-sm text-yellow-800 dark:text-yellow-300 font-semibold">
          Escalações não disponíveis
        </p>
        <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
          As escalações oficiais serão divulgadas próximo ao início da partida
        </p>
      </div>
    );
  }

  const homeLineup = lineups[0] || {};
  const awayLineup = lineups[1] || {};
  const currentLineup = selectedTeam === 'home' ? homeLineup : awayLineup;

  // Extrair formação (ex: "4-3-3")
  const formation = currentLineup.formation || '4-4-2';
  const teamName = currentLineup.team?.name || '';
  const teamLogo = currentLineup.team?.logo || '';
  const coach = currentLineup.coach?.name || 'N/A';

  // Separar titulares e reservas
  const startXI = currentLineup.startXI || [];
  const substitutes = currentLineup.substitutes || [];

  // Converter formação em array (ex: [4, 3, 3])
  const formationArray = formation.split('-').map(Number);

  // Organizar jogadores por linha (defesa, meio, ataque)
  const getPlayersByLine = () => {
    const lines = [];
    let playerIndex = 1; // Começa do 1 (goleiro já adicionado)

    // Linha 1: Goleiro
    const goalkeeper = startXI.find(p => p.player.pos === 'G');
    if (goalkeeper) {
      lines.push([goalkeeper]);
    }

    // Linhas restantes baseadas na formação
    formationArray.forEach(lineCount => {
      const linePlayers = [];
      for (let i = 0; i < lineCount; i++) {
        if (startXI[playerIndex]) {
          linePlayers.push(startXI[playerIndex]);
          playerIndex++;
        }
      }
      lines.push(linePlayers);
    });

    return lines.reverse(); // Inverter para mostrar atacantes no topo
  };

  const playerLines = getPlayersByLine();

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Users className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Escalações</h2>
      </div>

      {/* Seletor de Time */}
      <div className="grid grid-cols-2 gap-3 bg-gray-100 dark:bg-gray-800 p-2 rounded-xl">
        <button
          onClick={() => setSelectedTeam('home')}
          className={`flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-semibold transition-all ${
            selectedTeam === 'home'
              ? 'bg-white dark:bg-gray-700 shadow-md text-gray-900 dark:text-white'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700/50'
          }`}
        >
          <img src={homeLineup.team?.logo} alt={homeLineup.team?.name} className="w-6 h-6" />
          <span className="text-sm">{homeLineup.team?.name}</span>
        </button>
        <button
          onClick={() => setSelectedTeam('away')}
          className={`flex items-center justify-center gap-2 py-3 px-4 rounded-lg font-semibold transition-all ${
            selectedTeam === 'away'
              ? 'bg-white dark:bg-gray-700 shadow-md text-gray-900 dark:text-white'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700/50'
          }`}
        >
          <img src={awayLineup.team?.logo} alt={awayLineup.team?.name} className="w-6 h-6" />
          <span className="text-sm">{awayLineup.team?.name}</span>
        </button>
      </div>

      {/* Informações do Time */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-gray-800 dark:to-gray-700 rounded-xl p-4 border border-green-100 dark:border-gray-600">
        <div className="flex items-center gap-3 mb-2">
          <img src={teamLogo} alt={teamName} className="w-10 h-10" />
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white">{teamName}</h3>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Formação: <span className="font-bold text-green-700 dark:text-green-400">{formation}</span>
            </p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          <div className="flex items-center gap-2 text-xs text-gray-700 dark:text-gray-300">
            <span>👔 Treinador:</span>
            <span className="font-semibold">{coach}</span>
          </div>
          {match?.referee && (
            <div className="flex items-center gap-2 text-xs text-gray-700 dark:text-gray-300">
              <span>🧑‍⚖️ Árbitro:</span>
              <span className="font-semibold">{match.referee.split(',')[0]}</span>
            </div>
          )}
        </div>
      </div>

      {/* Campo de Futebol */}
      <div className="relative bg-gradient-to-b from-green-600 to-green-700 rounded-2xl p-6 overflow-hidden">
        {/* Linhas do Campo */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute inset-x-0 top-0 h-20 border-2 border-white rounded-t-2xl"></div>
          <div className="absolute inset-x-0 bottom-0 h-20 border-2 border-white rounded-b-2xl"></div>
          <div className="absolute inset-x-0 top-1/2 h-0.5 bg-white -translate-y-1/2"></div>
          <div className="absolute left-1/2 top-1/2 w-20 h-20 border-2 border-white rounded-full -translate-x-1/2 -translate-y-1/2"></div>
        </div>

        {/* Jogadores */}
        <div className="relative space-y-8">
          {playerLines.map((line, lineIndex) => (
            <div key={lineIndex} className="flex justify-around items-center gap-2">
              {line.map((playerData, playerIndex) => {
                const player = playerData.player;
                return (
                  <div
                    key={playerIndex}
                    className="flex flex-col items-center group"
                  >
                    {/* Foto do Jogador */}
                    <div className="relative">
                      <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 shadow-lg overflow-hidden border-2 border-white group-hover:scale-110 transition-transform">
                        <img
                          src={player.photo || `https://ui-avatars.com/api/?name=${encodeURIComponent(player.name)}&background=4F46E5&color=ffffff&bold=true&size=128`}
                          alt={player.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(player.name)}&background=4F46E5&color=ffffff&bold=true&size=128`;
                          }}
                        />
                      </div>
                      {/* Número da Camisa */}
                      <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold shadow-md border-2 border-white">
                        {player.number || '?'}
                      </div>
                    </div>
                    
                    {/* Nome do Jogador */}
                    <div className="mt-2 text-center">
                      <p className="text-xs font-bold text-white shadow-text px-2 py-1 bg-black/40 rounded-md backdrop-blur-sm">
                        {player.name?.split(' ').pop() || player.name}
                      </p>
                      <p className="text-[10px] text-white/80 mt-0.5">
                        {player.pos}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Substitutos */}
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <button
          onClick={() => setShowSubstitutes(!showSubstitutes)}
          className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
        >
          <div className="flex items-center gap-2">
            <Users className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            <span className="font-semibold text-gray-900 dark:text-white">
              Substitutos ({substitutes.length})
            </span>
          </div>
          {showSubstitutes ? (
            <ChevronUp className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          )}
        </button>

        {showSubstitutes && (
          <div className="p-4 pt-0 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {substitutes.map((sub, index) => {
              const player = sub.player;
              return (
                <div
                  key={index}
                  className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="relative flex-shrink-0">
                    <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-gray-200 dark:border-gray-600 bg-gradient-to-br from-indigo-500 to-blue-600">
                      <img
                        src={player.photo || `https://ui-avatars.com/api/?name=${encodeURIComponent(player.name)}&background=4F46E5&color=ffffff&bold=true&size=80`}
                        alt={player.name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(player.name)}&background=4F46E5&color=ffffff&bold=true&size=80`;
                        }}
                      />
                    </div>
                    <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-blue-600 text-white rounded-full flex items-center justify-center text-[10px] font-bold border-2 border-white dark:border-gray-800">
                      {player.number || '?'}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                      {player.name}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400">
                      {player.pos}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
