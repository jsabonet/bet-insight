import { useState, useEffect } from 'react';
import { X, Star, Sparkles, TrendingUp, AlertCircle, Target, Trophy, Zap, ClipboardList, Loader2, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useStrategy } from '../context/StrategyContext';
import { TeamLogo } from '../utils/logos';

/**
 * AnalysisModal com Progressive Loading (3 ondas)
 * 
 * Onda 1 (instantâneo): Badge + Probabilidades + Confiança (do card/preview)
 * Onda 2 (2-4s): Top 3 apostas (modelos estatísticos)
 * Onda 3 (5-8s): Análise IA completa
 */
export default function AnalysisModalProgressive({ match, onClose, onAnalyze }) {
  const { user } = useAuth();
  const { strategy } = useStrategy();
  
  // Estados de loading por fase
  const [phase, setPhase] = useState(1); // 1, 2, 3
  const [statisticalData, setStatisticalData] = useState(null); // Onda 1 (preview)
  const [topBets, setTopBets] = useState(null); // Onda 2
  const [aiAnalysis, setAiAnalysis] = useState(null); // Onda 3
  const [error, setError] = useState(null);

  // Formatar probabilidade com 1 casa decimal
  const formatProb = (prob) => {
    if (!prob) return '0.0';
    const numProb = typeof prob === 'string' ? parseFloat(prob) : prob;
    return numProb.toFixed(1);
  };

  // Carregar dados progressivamente
  useEffect(() => {
    loadProgressiveData();
  }, [match.id, strategy]);

  const loadProgressiveData = async () => {
    try {
      // ONDA 1: Dados do preview (já disponíveis, instantâneo)
      setPhase(1);
      setStatisticalData(match.preview || null);

      // ONDA 2: Chamar análise completa (top_bets)
      setPhase(2);
      const analysisResult = await onAnalyze();
      
      if (analysisResult?.analysis_data) {
        setTopBets(analysisResult.analysis_data.decision?.top_bets || []);
      }

      // ONDA 3: Análise da IA (já vem junto)
      setPhase(3);
      setAiAnalysis(analysisResult?.analysis || null);

    } catch (err) {
      console.error('Erro no progressive loading:', err);
      setError(err.message);
    }
  };

  const homeName = match?.home_team?.name || match?.home_team || 'Casa';
  const awayName = match?.away_team?.name || match?.away_team || 'Fora';
  const consensus = statisticalData?.consensus || {};
  const confidence = statisticalData?.confidence || { stars: 3, level_pt: 'Média' };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto relative shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex justify-between items-center z-10">
          <div className="flex items-center gap-3">
            <Brain className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Análise Completa
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Match Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 flex-1">
              <TeamLogo team={homeName} className="w-12 h-12" />
              <div className="text-center">
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">vs</p>
                <p className="text-xs text-gray-400">{match.league?.name}</p>
              </div>
              <TeamLogo team={awayName} className="w-12 h-12" />
            </div>
          </div>

          {/* ============ ONDA 1: Dados Instantâneos ============ */}
          {phase >= 1 && (
            <div className="space-y-4 animate-fade-in">
              {/* Strategy Badge */}
              <div className="flex justify-center">
                {strategy === 'multiple' ? (
                  <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-400 to-purple-500 text-white rounded-full shadow-lg">
                    <ClipboardList className="w-4 h-4" />
                    <span className="font-bold text-sm">Análise para Bilhetes</span>
                  </div>
                ) : (
                  <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-gray-900 rounded-full shadow-lg">
                    <Zap className="w-4 h-4" />
                    <span className="font-bold text-sm">Análise Simples (Value)</span>
                  </div>
                )}
              </div>

              {/* Probabilidades */}
              <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  PROBABILIDADES
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  <div className="text-center">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">🏠 Casa</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {formatProb(consensus.home_win * 100)}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">🤝 Empate</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {formatProb(consensus.draw * 100)}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">✈️ Fora</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {formatProb(consensus.away_win * 100)}%
                    </p>
                  </div>
                </div>
              </div>

              {/* Confiança */}
              <div className="flex items-center justify-center gap-2">
                <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                <span className="text-lg font-semibold text-gray-900 dark:text-white">
                  {confidence.stars}/5 - {confidence.level_pt}
                </span>
              </div>
            </div>
          )}

          {/* ============ ONDA 2: Top 3 Apostas (Loading) ============ */}
          {phase === 2 && !topBets && (
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-8 text-center space-y-4 animate-pulse">
              <Loader2 className="w-8 h-8 text-purple-600 animate-spin mx-auto" />
              <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">
                Calculando melhores apostas...
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Analisando {strategy === 'multiple' ? 'probabilidades altas' : 'melhor value'}
              </p>
            </div>
          )}

          {/* ============ ONDA 2: Top 3 Apostas (Carregado) ============ */}
          {topBets && topBets.length > 0 && (
            <div className="space-y-3 animate-fade-in">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                <Trophy className="w-4 h-4" />
                TOP 3 APOSTAS
              </h3>
              {topBets.map((bet, idx) => (
                <div
                  key={idx}
                  className="bg-white dark:bg-gray-700 border-2 border-gray-200 dark:border-gray-600 rounded-lg p-4 hover:border-purple-400 dark:hover:border-purple-500 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                        #{bet.rank}
                      </span>
                      <div>
                        <p className="font-bold text-gray-900 dark:text-white">
                          {bet.market_display}
                        </p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {bet.pick}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-gray-900 dark:text-white">
                        {bet.market_odd.toFixed(2)}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">odd</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="bg-blue-50 dark:bg-blue-900/20 rounded px-2 py-1">
                      <p className="text-gray-600 dark:text-gray-400">Prob</p>
                      <p className="font-bold text-blue-600 dark:text-blue-400">
                        {formatProb(bet.probability * 100)}%
                      </p>
                    </div>
                    <div className={`rounded px-2 py-1 ${
                      bet.ev_pct >= 0 
                        ? 'bg-green-50 dark:bg-green-900/20' 
                        : 'bg-red-50 dark:bg-red-900/20'
                    }`}>
                      <p className="text-gray-600 dark:text-gray-400">EV</p>
                      <p className={`font-bold ${
                        bet.ev_pct >= 0 
                          ? 'text-green-600 dark:text-green-400' 
                          : 'text-red-600 dark:text-red-400'
                      }`}>
                        {bet.ev_pct >= 0 ? '+' : ''}{bet.ev_pct.toFixed(1)}%
                      </p>
                    </div>
                    <div className="bg-purple-50 dark:bg-purple-900/20 rounded px-2 py-1">
                      <p className="text-gray-600 dark:text-gray-400">Stake</p>
                      <p className="font-bold text-purple-600 dark:text-purple-400">
                        {bet.stake_units}u
                      </p>
                    </div>
                  </div>
                  
                  <p className="text-xs text-gray-600 dark:text-gray-400 mt-2 italic">
                    {bet.reason}
                  </p>
                </div>
              ))}
            </div>
          )}

          {/* ============ ONDA 3: Análise IA (Loading) ============ */}
          {phase === 3 && !aiAnalysis && (
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg p-8 text-center space-y-4 animate-pulse">
              <Sparkles className="w-8 h-8 text-purple-600 animate-bounce mx-auto" />
              <p className="text-sm text-gray-600 dark:text-gray-300 font-medium">
                Gerando análise com IA...
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Contextualizando estatísticas e tendências
              </p>
            </div>
          )}

          {/* ============ ONDA 3: Análise IA (Carregado) ============ */}
          {aiAnalysis && (
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg p-6 space-y-4 animate-fade-in">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                  ANÁLISE CONTEXTUAL
                </h3>
              </div>
              
              <div className="prose prose-sm dark:prose-invert max-w-none">
                <div className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {aiAnalysis}
                </div>
              </div>
            </div>
          )}

          {/* Erro */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-800 dark:text-red-200">
                  Erro ao carregar análise
                </p>
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                  {error}
                </p>
              </div>
            </div>
          )}

          {/* Loading Completo */}
          {phase === 3 && aiAnalysis && (
            <div className="flex items-center justify-center gap-2 text-green-600 dark:text-green-400 animate-fade-in">
              <CheckCircle2 className="w-5 h-5" />
              <span className="text-sm font-medium">Análise completa</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
