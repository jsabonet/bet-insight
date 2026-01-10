import { Target, BarChart3 } from 'lucide-react';

/**
 * GOLS & POISSON
 * Exibe xG, distribuição de placares e probabilidades
 * Dados pré-calculados pelo PoissonBivariateModel
 */
export default function GoalsAndPoisson({ analysis }) {
  if (!analysis?.analysis_data?.poisson) return null;

  const { poisson } = analysis.analysis_data;
  const xG = poisson.expected_goals || {};
  const probs = poisson.probabilities || {};
  const scoreDistribution = poisson.score_distribution || [];

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Análise de Gols (Poisson)</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Expected Goals */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-gray-800 dark:to-gray-700 rounded-xl p-5 border border-green-200 dark:border-gray-600">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-green-600 dark:text-green-400" />
            <h3 className="font-bold text-gray-900 dark:text-white">Expected Goals (xG)</h3>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Casa</div>
              <div className="text-3xl font-black text-green-600 dark:text-green-400">
                {xG.home?.toFixed(2) || '—'}
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">Fora</div>
              <div className="text-3xl font-black text-blue-600 dark:text-blue-400">
                {xG.away?.toFixed(2) || '—'}
              </div>
            </div>
          </div>

          {poisson.weather_adjusted && (
            <div className="mt-3 text-xs text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 rounded-lg px-2 py-1 text-center">
              ⚠️ Ajustado por condições climáticas
            </div>
          )}
        </div>

        {/* Probabilidades de Mercado */}
        <div className="bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-gray-800 dark:to-gray-700 rounded-xl p-5 border border-blue-200 dark:border-gray-600">
          <h3 className="font-bold text-gray-900 dark:text-white mb-4">Mercados de Gols</h3>
          
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-300">Over 2.5</span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {probs.over_2_5 ? `${(probs.over_2_5 * 100).toFixed(1)}%` : '—'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">Under 2.5</span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {probs.under_2_5 ? `${(probs.under_2_5 * 100).toFixed(1)}%` : '—'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">Ambas Marcam</span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {probs.btts ? `${(probs.btts * 100).toFixed(1)}%` : '—'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">Casa não sofre</span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {probs.home_clean_sheet ? `${(probs.home_clean_sheet * 100).toFixed(1)}%` : '—'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-700 dark:text-gray-300">Fora não sofre</span>
              <span className="text-sm font-bold text-gray-900 dark:text-white">
                {probs.away_clean_sheet ? `${(probs.away_clean_sheet * 100).toFixed(1)}%` : '—'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Distribuição de Placares - Top 6 */}
      {scoreDistribution.length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700">
          <h3 className="font-bold text-gray-900 dark:text-white mb-4">Placares Mais Prováveis</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {scoreDistribution.slice(0, 6).map((score, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 rounded-lg p-3 text-center border border-gray-300 dark:border-gray-600"
              >
                <div className="text-2xl font-black text-gray-900 dark:text-white mb-1">
                  {score.score}
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">
                  {(score.probability * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
