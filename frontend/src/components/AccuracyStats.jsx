import { TrendingUp, Target, CheckCircle, XCircle, Clock, Activity } from 'lucide-react';

export default function AccuracyStats({ stats }) {
  const {
    all_time = {},
    last_7_days = {},
    by_bet_type = {}
  } = stats;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Nossa Performance Real
        </h2>
        <p className="text-gray-600 dark:text-gray-400">
          Transparência total. Todos os resultados validados automaticamente.
        </p>
      </div>

      {/* Últimos 7 Dias - Destaque */}
      <div className="bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-xl p-6 border border-primary-200 dark:border-primary-800">
        <div className="flex items-center gap-2 mb-4">
          <Activity className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
            Últimos 7 Dias
          </h3>
        </div>
        
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Taxa de Acerto</p>
            <p className="text-3xl font-bold text-primary-600 dark:text-primary-400">
              {last_7_days.win_rate || '0%'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">ROI</p>
            <p className={`text-3xl font-bold ${
              parseFloat(last_7_days.roi) > 0 
                ? 'text-emerald-600 dark:text-emerald-400' 
                : parseFloat(last_7_days.roi) < 0
                ? 'text-red-600 dark:text-red-400'
                : 'text-gray-600 dark:text-gray-400'
            }`}>
              {last_7_days.roi || '0%'}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Total</p>
            <p className="text-3xl font-bold text-gray-900 dark:text-gray-100">
              {last_7_days.total || 0}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <span className="text-gray-700 dark:text-gray-300">
              {last_7_days.won || 0} ganhas
            </span>
          </div>
          <div className="flex items-center gap-2">
            <XCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
            <span className="text-gray-700 dark:text-gray-300">
              {last_7_days.lost || 0} perdidas
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            <span className="text-gray-700 dark:text-gray-300">
              {last_7_days.pending || 0} pendentes
            </span>
          </div>
        </div>
      </div>

      {/* Histórico Completo */}
      <div>
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
          Histórico Completo
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <p className="text-xs text-gray-500 dark:text-gray-400">Taxa de Acerto</p>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1">
              {all_time.win_rate || '0%'}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {all_time.won || 0} de {all_time.total || 0} apostas
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <p className="text-xs text-gray-500 dark:text-gray-400">ROI Total</p>
            </div>
            <p className={`text-2xl font-bold mb-1 ${
              parseFloat(all_time.roi) > 0 
                ? 'text-emerald-600 dark:text-emerald-400' 
                : parseFloat(all_time.roi) < 0
                ? 'text-red-600 dark:text-red-400'
                : 'text-gray-600 dark:text-gray-400'
            }`}>
              {all_time.roi || '0%'}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Retorno acumulado
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-purple-600 dark:text-purple-400" />
              <p className="text-xs text-gray-500 dark:text-gray-400">Total de Apostas</p>
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-1">
              {all_time.total || 0}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {all_time.won || 0} ganhas, {all_time.lost || 0} perdidas
            </p>
          </div>
        </div>
      </div>

      {/* Performance por Tipo */}
      {by_bet_type && (by_bet_type.multiple || by_bet_type.value) && (
        <div>
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
            Performance por Tipo
          </h3>
          
          <div className="space-y-4">
            {/* Bilhetes Múltiplos */}
            {by_bet_type.multiple && (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                      <Target className="w-4 h-4 text-purple-600 dark:text-purple-400" />
                    </div>
                    <h4 className="font-bold text-gray-900 dark:text-gray-100">
                      Bilhetes Múltiplos
                    </h4>
                  </div>
                  <span className="text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 px-2 py-1 rounded-lg font-medium">
                    {by_bet_type.multiple.total || 0} apostas
                  </span>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Acertos</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {by_bet_type.multiple.win_rate || '0%'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">ROI</p>
                    <p className={`text-lg font-bold ${
                      parseFloat(by_bet_type.multiple.roi) > 0 
                        ? 'text-emerald-600 dark:text-emerald-400' 
                        : 'text-red-600 dark:text-red-400'
                    }`}>
                      {by_bet_type.multiple.roi || '0%'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Resultado</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {by_bet_type.multiple.won || 0}/{by_bet_type.multiple.total || 0}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Value Bets */}
            {by_bet_type.value && (
              <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg flex items-center justify-center">
                      <TrendingUp className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                    </div>
                    <h4 className="font-bold text-gray-900 dark:text-gray-100">
                      Value Bets
                    </h4>
                  </div>
                  <span className="text-xs bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 px-2 py-1 rounded-lg font-medium">
                    {by_bet_type.value.total || 0} apostas
                  </span>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Acertos</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {by_bet_type.value.win_rate || '0%'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">ROI</p>
                    <p className={`text-lg font-bold ${
                      parseFloat(by_bet_type.value.roi) > 0 
                        ? 'text-emerald-600 dark:text-emerald-400' 
                        : 'text-red-600 dark:text-red-400'
                    }`}>
                      {by_bet_type.value.roi || '0%'}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Resultado</p>
                    <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                      {by_bet_type.value.won || 0}/{by_bet_type.value.total || 0}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Nota de Transparência */}
      <div className="bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 border border-blue-200 dark:border-blue-800">
        <p className="text-sm text-blue-900 dark:text-blue-300 leading-relaxed">
          <strong>💡 Transparência Total:</strong> Todos os resultados são validados automaticamente contra os resultados oficiais das partidas. 
          Nenhum dado é manipulado, editado ou excluído. Esta é a performance real do sistema.
        </p>
      </div>
    </div>
  );
}
