import { X, Star, Sparkles, TrendingUp, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function AnalysisModal({ match, analysis, onClose }) {
  const { user } = useAuth();

  if (!analysis) return null;

  const renderStars = (confidence) => {
    return (
      <div className="flex items-center gap-1">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`w-5 h-5 ${
              i < confidence
                ? 'fill-yellow-400 text-yellow-400'
                : 'text-gray-300 dark:text-gray-600'
            }`}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden animate-slide-up">
        {/* Header */}
        <div className="relative bg-gradient-to-br from-primary-600 via-primary-700 to-accent-600 p-6">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 rounded-full bg-white/20 hover:bg-white/30 text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="flex items-center gap-3 mb-3">
            <div className="p-3 rounded-2xl bg-white/20 backdrop-blur-sm">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Análise com IA</h2>
              <p className="text-primary-100 text-sm">Powered by Google Gemini</p>
            </div>
          </div>

          {match && (
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 mt-4">
              <div className="flex items-center justify-between text-white">
                <div className="text-center flex-1">
                  <p className="font-bold text-lg">{match.home_team?.name || match.home_team}</p>
                </div>
                <div className="px-4 py-1 bg-white/20 rounded-lg font-bold">VS</div>
                <div className="text-center flex-1">
                  <p className="font-bold text-lg">{match.away_team?.name || match.away_team}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          {/* Confidence Level */}
          <div className="mb-6 p-4 bg-gradient-to-r from-yellow-50 to-amber-50 dark:from-gray-700 dark:to-gray-600 rounded-2xl border border-yellow-200 dark:border-gray-500">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Nível de Confiança
              </span>
              {renderStars(analysis.confidence)}
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              {analysis.confidence >= 4
                ? 'Alta confiança - Recomendação forte'
                : analysis.confidence >= 3
                ? 'Confiança moderada - Análise equilibrada'
                : 'Confiança baixa - Aposte com cautela'}
            </p>
          </div>

          {/* Analysis Text */}
          <div className="prose dark:prose-invert max-w-none">
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-2xl p-6 border border-gray-100 dark:border-gray-600">
              <div className="flex items-start gap-3 mb-4">
                <TrendingUp className="w-5 h-5 text-primary-600 dark:text-primary-400 mt-1 flex-shrink-0" />
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-3">
                    Análise Detalhada
                  </h3>
                  <div className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                    {analysis.analysis}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Remaining Analyses (for free users) */}
          {user && !user.is_premium && analysis.remaining_analyses !== undefined && (
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-2xl border border-blue-200 dark:border-blue-800">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-semibold text-blue-900 dark:text-blue-300">
                    Análises Restantes Hoje
                  </p>
                  <p className="text-sm text-blue-700 dark:text-blue-400 mt-1">
                    Você tem <span className="font-bold">{analysis.remaining_analyses}</span> análise
                    {analysis.remaining_analyses !== 1 ? 's' : ''} restante
                    {analysis.remaining_analyses !== 1 ? 's' : ''}.
                  </p>
                  {analysis.remaining_analyses === 0 && (
                    <button className="mt-3 w-full py-2 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-semibold hover:from-primary-700 hover:to-primary-800 transition-all">
                      Assinar Premium - Análises Ilimitadas
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Disclaimer */}
          <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700/30 rounded-xl border border-gray-200 dark:border-gray-600">
            <p className="text-xs text-gray-600 dark:text-gray-400 text-center">
              ⚠️ Esta análise é gerada por inteligência artificial e serve apenas como orientação.
              Aposte com responsabilidade e considere múltiplas fontes de informação.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
