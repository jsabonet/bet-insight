import { Target, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { formatMarketLabel } from '../utils/marketLabels';

export default function MultipleTicketCard({ ticket, onViewDetails }) {
  const navigate = useNavigate();
  
  const {
    selections = [],
    total_odd = 0,
    combined_probability = 0,
    expected_value = 0,
    status = 'pending'
  } = ticket;

  const getStatusBadge = (status) => {
    const badges = {
      'pending': { label: 'Pendente', className: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300' },
      'won': { label: 'Ganhou', className: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' },
      'lost': { label: 'Perdeu', className: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' },
      'partial': { label: 'Parcial', className: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400' }
    };
    return badges[status] || badges.pending;
  };

  const statusBadge = getStatusBadge(status);
  const selectionCount = selections.length;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden hover:border-purple-300 dark:hover:border-purple-700 transition-all">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
              <Target className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="font-bold text-gray-900 dark:text-gray-100">
              Múltiplo {selectionCount}x
            </h3>
          </div>
          <span className={`px-2 py-1 rounded-lg text-xs font-medium ${statusBadge.className}`}>
            {statusBadge.label}
          </span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3 px-4 py-3 bg-gray-50 dark:bg-gray-900/50">
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">Odd Total</p>
          <p className="font-bold text-gray-900 dark:text-gray-100">
            {parseFloat(total_odd).toFixed(2)}
          </p>
        </div>
        <div className="border-x border-gray-200 dark:border-gray-700 px-3">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">Probabilidade</p>
          <p className="font-bold text-gray-900 dark:text-gray-100">
            {(parseFloat(combined_probability) * 100).toFixed(0)}%
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-0.5">EV</p>
          <p className={`font-bold ${parseFloat(expected_value) >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-red-600 dark:text-red-400'}`}>
            {parseFloat(expected_value) >= 0 ? '+' : ''}{parseFloat(expected_value).toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Selections */}
      <div className="p-4 space-y-2">
        {selections.map((selection, index) => {
          const hasMatchId = selection.match_id || selection.fixture_id;
          const isClickable = hasMatchId;
          
          return (
            <div 
              key={index}
              onClick={() => isClickable && navigate(`/match/${hasMatchId}`)}
              className={`group flex items-center gap-3 p-2.5 bg-gray-50 dark:bg-gray-900/50 rounded-lg ${
                isClickable ? 'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800/70 transition-colors' : ''
              }`}
            >
              <div className="flex-shrink-0 w-5 h-5 bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 rounded-full flex items-center justify-center text-[10px] font-bold">
                {index + 1}
              </div>
              <div className="flex-1 min-w-0">
                <p className={`font-medium text-xs text-gray-900 dark:text-gray-100 truncate ${isClickable ? 'group-hover:text-purple-600 dark:group-hover:text-purple-400' : ''}`}>
                  {selection.match || `${selection.home_team?.name || selection.home_team || ''} vs ${selection.away_team?.name || selection.away_team || ''}`}
                </p>
                <p className="text-[11px] text-gray-500 dark:text-gray-400 truncate">
                  {formatMarketLabel(selection.market, selection.market_label)}
                </p>
                {selection.original_market && selection.line_adjustment && (
                  <p className="text-[10px] text-amber-700 dark:text-amber-400">
                    Linha ajustada: {formatMarketLabel(selection.original_market)} → {formatMarketLabel(selection.market)}
                  </p>
                )}
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <div className="text-right">
                  <p className="font-bold text-xs text-gray-900 dark:text-gray-100">
                    {parseFloat(selection.odd).toFixed(2)}
                  </p>
                  <p className="text-[10px] text-gray-500 dark:text-gray-400">
                    {(parseFloat(selection.probability) * 100).toFixed(0)}%
                  </p>
                </div>
                {isClickable && (
                  <ExternalLink className="w-3.5 h-3.5 text-gray-400 dark:text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
                {selection.result && (
                  <span className="text-sm">
                    {selection.result === 'won' ? '✅' : '❌'}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
