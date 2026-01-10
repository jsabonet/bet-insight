import { BarChart3, Target, Flag, AlertTriangle, TrendingUp } from 'lucide-react';

/**
 * MATCH STATISTICS - Estatísticas Detalhadas da Partida
 * Exibe dados como chutes, escanteios, faltas, cartões, etc.
 */
export default function MatchStatistics({ statistics, match }) {
  console.log('📊 MatchStatistics recebeu:', { 
    hasStatistics: !!statistics,
    statisticsLength: statistics?.length,
    hasMatch: !!match,
  });

  if (!statistics || statistics.length === 0) {
    return null;
  }

  // Obter nomes dos times
  const homeTeam = match?.home_team?.name || match?.home_team || 'Casa';
  const awayTeam = match?.away_team?.name || match?.away_team || 'Fora';

  // Processar estatísticas - API-Football retorna array com 2 objetos (um para cada time)
  const homeStats = statistics.find(s => s.team?.name === homeTeam) || statistics[0];
  const awayStats = statistics.find(s => s.team?.name === awayTeam) || statistics[1];

  if (!homeStats || !awayStats) {
    return null;
  }

  // Função auxiliar para obter valor de uma estatística
  const getStat = (stats, type) => {
    const stat = stats.statistics?.find(s => s.type === type);
    return stat?.value || 0;
  };

  // Função para formatar porcentagem
  const formatPercent = (value) => {
    if (!value) return '0%';
    if (typeof value === 'string' && value.includes('%')) return value;
    return `${value}%`;
  };

  // Função para obter valor numérico
  const getNumericValue = (value) => {
    if (!value) return 0;
    if (typeof value === 'string') {
      return parseInt(value.replace('%', '')) || 0;
    }
    return value;
  };

  // Estatísticas a exibir
  const stats = [
    {
      type: 'Posse de Bola',
      icon: '⚽',
      homeValue: getStat(homeStats, 'Ball Possession'),
      awayValue: getStat(awayStats, 'Ball Possession'),
      format: 'percent',
      color: 'blue'
    },
    {
      type: 'Chutes Totais',
      icon: '🎯',
      homeValue: getStat(homeStats, 'Total Shots'),
      awayValue: getStat(awayStats, 'Total Shots'),
      format: 'number',
      color: 'purple'
    },
    {
      type: 'Chutes ao Gol',
      icon: '🎯',
      homeValue: getStat(homeStats, 'Shots on Goal'),
      awayValue: getStat(awayStats, 'Shots on Goal'),
      format: 'number',
      color: 'green'
    },
    {
      type: 'Chutes para Fora',
      icon: '↗️',
      homeValue: getStat(homeStats, 'Shots off Goal'),
      awayValue: getStat(awayStats, 'Shots off Goal'),
      format: 'number',
      color: 'gray'
    },
    {
      type: 'Chutes Bloqueados',
      icon: '🛡️',
      homeValue: getStat(homeStats, 'Blocked Shots'),
      awayValue: getStat(awayStats, 'Blocked Shots'),
      format: 'number',
      color: 'orange'
    },
    {
      type: 'Escanteios',
      icon: '🚩',
      homeValue: getStat(homeStats, 'Corner Kicks'),
      awayValue: getStat(awayStats, 'Corner Kicks'),
      format: 'number',
      color: 'yellow'
    },
    {
      type: 'Impedimentos',
      icon: '🏴',
      homeValue: getStat(homeStats, 'Offsides'),
      awayValue: getStat(awayStats, 'Offsides'),
      format: 'number',
      color: 'red'
    },
    {
      type: 'Faltas',
      icon: '⚠️',
      homeValue: getStat(homeStats, 'Fouls'),
      awayValue: getStat(awayStats, 'Fouls'),
      format: 'number',
      color: 'amber'
    },
    {
      type: 'Cartões Amarelos',
      icon: '🟨',
      homeValue: getStat(homeStats, 'Yellow Cards'),
      awayValue: getStat(awayStats, 'Yellow Cards'),
      format: 'number',
      color: 'yellow'
    },
    {
      type: 'Cartões Vermelhos',
      icon: '🟥',
      homeValue: getStat(homeStats, 'Red Cards'),
      awayValue: getStat(awayStats, 'Red Cards'),
      format: 'number',
      color: 'red'
    },
    {
      type: 'Defesas do Goleiro',
      icon: '🧤',
      homeValue: getStat(homeStats, 'Goalkeeper Saves'),
      awayValue: getStat(awayStats, 'Goalkeeper Saves'),
      format: 'number',
      color: 'cyan'
    },
    {
      type: 'Passes Totais',
      icon: '🔄',
      homeValue: getStat(homeStats, 'Total passes'),
      awayValue: getStat(awayStats, 'Total passes'),
      format: 'number',
      color: 'indigo'
    },
    {
      type: 'Passes Certos',
      icon: '✅',
      homeValue: getStat(homeStats, 'Passes accurate'),
      awayValue: getStat(awayStats, 'Passes accurate'),
      format: 'number',
      color: 'green'
    },
    {
      type: 'Precisão de Passes',
      icon: '📊',
      homeValue: getStat(homeStats, 'Passes %'),
      awayValue: getStat(awayStats, 'Passes %'),
      format: 'percent',
      color: 'blue'
    }
  ];

  // Filtrar apenas estatísticas que têm valores
  const availableStats = stats.filter(s => 
    getNumericValue(s.homeValue) > 0 || getNumericValue(s.awayValue) > 0
  );

  if (availableStats.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Estatísticas da Partida</h2>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="space-y-5">
          {availableStats.map((stat, index) => {
            const homeVal = getNumericValue(stat.homeValue);
            const awayVal = getNumericValue(stat.awayValue);
            const total = homeVal + awayVal;
            
            // Calcular percentuais para as barras
            const homePercent = total > 0 ? (homeVal / total) * 100 : 0;
            const awayPercent = total > 0 ? (awayVal / total) * 100 : 0;

            return (
              <div key={index}>
                {/* Título da Estatística */}
                <div className="flex items-center justify-center mb-2">
                  <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    {stat.icon} {stat.type}
                  </span>
                </div>

                {/* Valores e Barras */}
                <div className="flex items-center gap-3">
                  {/* Valor Casa */}
                  <div className="text-right min-w-[60px]">
                    <span className="text-lg font-bold text-blue-600 dark:text-blue-400">
                      {stat.format === 'percent' ? formatPercent(stat.homeValue) : stat.homeValue || 0}
                    </span>
                  </div>

                  {/* Barras Horizontais */}
                  <div className="flex-1">
                    <div className="flex items-center h-4 gap-0.5">
                      {/* Barra Casa (da direita para esquerda) */}
                      <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-l-full h-full flex justify-end overflow-hidden">
                        <div 
                          className="bg-gradient-to-l from-blue-500 to-blue-600 h-full rounded-l-full transition-all duration-500 ease-out"
                          style={{ width: `${homePercent}%` }}
                        ></div>
                      </div>
                      
                      {/* Divisor */}
                      <div className="w-0.5 h-6 bg-gray-300 dark:bg-gray-600"></div>
                      
                      {/* Barra Fora (da esquerda para direita) */}
                      <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-r-full h-full overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-red-500 to-red-600 h-full rounded-r-full transition-all duration-500 ease-out"
                          style={{ width: `${awayPercent}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Labels dos Times */}
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-[10px] text-gray-500 dark:text-gray-500 truncate max-w-[45%]">
                        {homeTeam}
                      </span>
                      <span className="text-[10px] text-gray-500 dark:text-gray-500 truncate max-w-[45%]">
                        {awayTeam}
                      </span>
                    </div>
                  </div>

                  {/* Valor Fora */}
                  <div className="text-left min-w-[60px]">
                    <span className="text-lg font-bold text-red-600 dark:text-red-400">
                      {stat.format === 'percent' ? formatPercent(stat.awayValue) : stat.awayValue || 0}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Legenda */}
      <div className="flex items-center justify-center gap-6 text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-blue-600 rounded"></div>
          <span>{homeTeam}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gradient-to-r from-red-500 to-red-600 rounded"></div>
          <span>{awayTeam}</span>
        </div>
      </div>
    </div>
  );
}
