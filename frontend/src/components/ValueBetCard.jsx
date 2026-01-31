import { Zap, ExternalLink } from 'lucide-react';

// Função para formatar nomes de mercados
const formatMarket = (market) => {
  const marketLabels = {
    'home_win': 'Vitória do Time da Casa',
    'draw': 'Empate',
    'away_win': 'Vitória do Time Visitante',
    'double_chance_12': 'Casa ou Fora (Sem Empate)',
    'double_chance_1x': 'Casa Vence ou Empata',
    'double_chance_x2': 'Empate ou Fora Vence',
    'over_0_5': 'Pelo Menos 1 Gol no Jogo',
    'over_1_5': 'Pelo Menos 2 Gols no Jogo',
    'over_2_5': 'Pelo Menos 3 Gols no Jogo',
    'over_3_5': 'Pelo Menos 4 Gols no Jogo',
    'under_0_5': 'Sem Gols (0-0)',
    'under_1_5': 'No Máximo 1 Gol',
    'under_2_5': 'No Máximo 2 Gols',
    'under_3_5': 'No Máximo 3 Gols',
    'btts_yes': 'Ambos Times Marcam',
    'btts_no': 'Pelo Menos 1 Time Não Marca',
    'home_over_05': 'Casa Marca Pelo Menos 1 Gol',
    'home_over_15': 'Casa Marca Pelo Menos 2 Gols',
    'home_over_25': 'Casa Marca Pelo Menos 3 Gols',
    'away_over_05': 'Fora Marca Pelo Menos 1 Gol',
    'away_over_15': 'Fora Marca Pelo Menos 2 Gols',
    'away_over_25': 'Fora Marca Pelo Menos 3 Gols',
  };
  
  return marketLabels[market] || market.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

export default function ValueBetCard({ bet, onViewAnalysis }) {
  const {
    selections = [],
    total_odd = 0,
    expected_value = 0,
    status = 'pending'
  } = bet;

  const selection = selections[0];

  const getStatusBadge = (status) => {
    const badges = {
      'pending': { label: 'Pendente', className: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300' },
      'won': { label: 'Ganhou', className: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' },
      'lost': { label: 'Perdeu', className: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' }
    };
    return badges[status] || badges.pending;
  };

  const getEVLabel = (ev) => {
    if (ev >= 20) return 'Excelente';
    if (ev >= 10) return 'Bom';
    return 'Moderado';
  };

  const statusBadge = getStatusBadge(status);
  const evValue = parseFloat(expected_value);

  if (!selection) return null;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:border-emerald-300 dark:hover:border-emerald-700 transition-all">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg flex items-center justify-center">
              <Zap className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            </div>
            <span className={`px-2 py-1 rounded-lg text-xs font-bold ${
              evValue >= 20 
                ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' 
                : evValue >= 10
                ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                : 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
            }`}>
              EV +{evValue.toFixed(1)}%
            </span>
          </div>
          <span className={`px-2 py-1 rounded-lg text-xs font-medium ${statusBadge.className}`}>
            {statusBadge.label}
          </span>
        </div>
        <h3 className="font-bold text-sm text-gray-900 dark:text-gray-100">
          {selection.match || `${selection.home_team?.name || selection.home_team || ''} vs ${selection.away_team?.name || selection.away_team || ''}`}
        </h3>
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="mb-3">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Aposta</p>
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
            {formatMarket(selection.market_label || selection.market || 'Mercado')}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-3">
          <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-2">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">Odd</p>
            <p className="font-bold text-gray-900 dark:text-gray-100">
              {parseFloat(total_odd).toFixed(2)}
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-2">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">Prob.</p>
            <p className="font-bold text-gray-900 dark:text-gray-100">
              {(parseFloat(selection.probability) * 100).toFixed(0)}%
            </p>
          </div>
        </div>

        {onViewAnalysis && (
          <button
            onClick={() => onViewAnalysis(selection)}
            className="w-full flex items-center justify-center gap-2 py-2 text-sm font-medium text-emerald-600 dark:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 rounded-lg transition-colors"
          >
            Ver Análise Completa
            <ExternalLink className="w-3 h-3" />
          </button>
        )}
      </div>
    </div>
  );
}
