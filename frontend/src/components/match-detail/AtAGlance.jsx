import { Target, TrendingUp, AlertTriangle, Star, Trophy, CheckCircle, HelpCircle } from 'lucide-react';
import { useState } from 'react';

/**
 * AT A GLANCE - Visão Geral Rápida
 * Hierarquia visual aprimorada com Hero Card em destaque
 */
export default function AtAGlance({ analysis, match }) {
  const [showRiskInfo, setShowRiskInfo] = useState(false);
  
  console.log('🔍 AtAGlance recebeu:', { 
    hasAnalysis: !!analysis,
    hasAnalysisData: !!analysis?.analysis_data,
    hasMatch: !!match,
    analysisDataKeys: analysis?.analysis_data ? Object.keys(analysis.analysis_data) : []
  });

  if (!analysis) {
    console.warn('⚠️ AtAGlance: análise não definida');
    return null;
  }

  // Se não tem analysis_data, criar estrutura básica a partir dos dados disponíveis
  const analysisData = analysis.analysis_data || {};
  const enrichedData = analysis.enriched_data || {};
  
  const { consensus, poisson, recommendation, confidence, risk } = analysisData;
  
  // Nomes dos times
  const homeTeam = match?.home_team?.name || match?.home_team || 'Casa';
  const awayTeam = match?.away_team?.name || match?.away_team || 'Fora';
  
  // Probabilidades (já do backend)
  const homeProb = consensus?.home_win ? (consensus.home_win * 100) : 0;
  const drawProb = consensus?.draw ? (consensus.draw * 100) : 0;
  const awayProb = consensus?.away_win ? (consensus.away_win * 100) : 0;
  
  // Placar mais provável
  const mostLikelyScore = poisson?.most_likely_score || '—';
  
  // Over 2.5 e Ambas Marcam
  const over25 = poisson?.probabilities?.over_2_5 ? (poisson.probabilities.over_2_5 * 100).toFixed(1) : '—';
  const ambasMarcam = poisson?.probabilities?.btts ? (poisson.probabilities.btts * 100).toFixed(1) : '—';
  
  // Confiança (para determinar cor do hero card)
  const stars = confidence?.stars || 3;
  const confidenceScore = stars / 5; // 0 a 1
  
  // Determinar probabilidade mais alta para hero card
  const maxProb = Math.max(homeProb, drawProb, awayProb);
  
  // Risco
  const riskLevel = risk || 'medium';
  
  console.log('🎲 ANÁLISE DE RISCO:', {
    riskFromAnalysis: risk,
    riskLevel,
    consensus,
    confidenceStars: stars
  });
  
  const riskConfig = {
    low: { 
      label: 'Baixo',
      color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
      icon: '🟢'
    },
    medium: { 
      label: 'Médio',
      color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
      icon: '🟡'
    },
    high: { 
      label: 'Alto',
      color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
      icon: '🔴'
    }
  };

  // Gradient dinâmico baseado na confiança (verde = alta, amarelo = média, vermelho = baixa)
  const getHeroGradient = () => {
    if (confidenceScore >= 0.8) {
      return 'from-emerald-500 via-green-500 to-teal-500';
    } else if (confidenceScore >= 0.6) {
      return 'from-blue-500 via-indigo-500 to-purple-500';
    } else if (confidenceScore >= 0.4) {
      return 'from-amber-500 via-orange-500 to-yellow-500';
    } else {
      return 'from-gray-500 via-slate-500 to-zinc-500';
    }
  };

  // Calcular qualidade dos dados
  const hasRecentGames = analysisData.features_summary?.form?.home_weighted_form !== undefined || 
                         (enrichedData.last_matches?.home && enrichedData.last_matches.home.length > 0) ||
                         (enrichedData.last_matches?.away && enrichedData.last_matches.away.length > 0);
  
  const hasH2H = (enrichedData.h2h && enrichedData.h2h.length > 0) || 
                 analysisData.features_summary?.h2h?.total_matches > 0;
  
  const hasInjuries = (enrichedData.injuries && (enrichedData.injuries.home?.length > 0 || enrichedData.injuries.away?.length > 0)) ||
                      analysisData.features_summary?.injuries !== undefined;
  
  const hasOdds = (enrichedData.odds && enrichedData.odds.home_win) || 
                  (analysisData.market_odds && analysisData.market_odds.odds_home) ||
                  (analysisData.fair_odds && analysisData.fair_odds.home_win);
  
  const dataQualityScore = [hasRecentGames, hasH2H, hasInjuries, hasOdds].filter(Boolean).length / 4;

  return (
    <div className="space-y-5">
      <div className="flex items-center gap-2 mb-1">
        <Target className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Visão Geral</h2>
      </div>

      {/* Indicador de Qualidade dos Dados */}
      <div className="flex items-center justify-between gap-3 p-3 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
        <span className="text-xs font-semibold text-gray-700 dark:text-gray-300">
          Qualidade dos Dados:
        </span>
        
        <div className="flex items-center gap-2">
          {/* Ícones com tooltips */}
          <div className="relative group">
            {hasRecentGames ? (
              <CheckCircle className="w-4 h-4 text-green-500" />
            ) : (
              <HelpCircle className="w-4 h-4 text-yellow-500" />
            )}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
              Forma recente
            </div>
          </div>
          
          <div className="relative group">
            {hasH2H ? (
              <CheckCircle className="w-4 h-4 text-green-500" />
            ) : (
              <HelpCircle className="w-4 h-4 text-yellow-500" />
            )}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
              H2H
            </div>
          </div>
          
          <div className="relative group">
            {hasInjuries ? (
              <CheckCircle className="w-4 h-4 text-green-500" />
            ) : (
              <HelpCircle className="w-4 h-4 text-gray-400" />
            )}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
              Lesões
            </div>
          </div>
          
          <div className="relative group">
            {hasOdds ? (
              <CheckCircle className="w-4 h-4 text-green-500" />
            ) : (
              <HelpCircle className="w-4 h-4 text-yellow-500" />
            )}
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
              Odds
            </div>
          </div>
        </div>
        
        <span className={`text-xs font-bold px-2 py-1 rounded-full ${
          dataQualityScore >= 0.75 
            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
            : dataQualityScore >= 0.5
            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
            : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
        }`}>
          {dataQualityScore >= 0.75 ? '✅ Ótima' : dataQualityScore >= 0.5 ? '⚠️ Moderada' : '❌ Limitada'}
        </span>
      </div>

      {/* HERO CARD - Placar Mais Provável */}
      <div className={`relative bg-gradient-to-br ${getHeroGradient()} rounded-2xl p-6 shadow-xl overflow-hidden group hover:shadow-2xl transition-all duration-300`}>
        {/* Efeito de brilho ao hover */}
        <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Trophy className="w-5 h-5 text-white/90" />
              <span className="text-xs font-bold text-white/80 uppercase tracking-wider">Placar Mais Provável</span>
            </div>
            <div className="flex items-center gap-1">
              {[...Array(5)].map((_, i) => (
                <Star
                  key={i}
                  className={`w-4 h-4 ${i < stars ? 'fill-white text-white' : 'text-white/30'}`}
                />
              ))}
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-6xl md:text-7xl font-black text-white mb-2 tracking-tight drop-shadow-lg">
              {mostLikelyScore}
            </div>
            <div className="text-sm font-medium text-white/90">
              Baseado em análise estatística de {poisson?.total_scenarios || 81} cenários
            </div>
          </div>
        </div>
        
        {/* Padrão decorativo de fundo */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32 blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-black/5 rounded-full -ml-32 -mb-32 blur-3xl"></div>
      </div>

      {/* PROBABILIDADES 1X2 */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-5 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
          Probabilidades de Resultado
        </div>
        
        {/* Vitória Casa */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">{homeTeam}</span>
            <span className="text-lg font-black text-blue-600 dark:text-blue-400">{homeProb.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-700 ease-out shadow-sm"
              style={{ width: `${homeProb}%` }}
            ></div>
          </div>
        </div>

        {/* Empate */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Empate</span>
            <span className="text-lg font-black text-gray-600 dark:text-gray-400">{drawProb.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-gray-400 to-gray-500 h-3 rounded-full transition-all duration-700 ease-out shadow-sm"
              style={{ width: `${drawProb}%` }}
            ></div>
          </div>
        </div>

        {/* Vitória Fora */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">{awayTeam}</span>
            <span className="text-lg font-black text-red-600 dark:text-red-400">{awayProb.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-red-500 to-red-600 h-3 rounded-full transition-all duration-700 ease-out shadow-sm"
              style={{ width: `${awayProb}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* MÉTRICAS SECUNDÁRIAS - Compactas */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {/* Over 2.5 */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/10 dark:to-emerald-900/10 rounded-xl p-4 border border-green-200/50 dark:border-green-700/30">
          <div className="text-xs font-bold text-green-700 dark:text-green-400 mb-1 uppercase tracking-wide">Over 2.5</div>
          <div className="text-3xl font-black text-gray-900 dark:text-white">{over25}%</div>
        </div>

        {/* Ambas Marcam */}
        <div className="bg-gradient-to-br from-cyan-50 to-blue-50 dark:from-cyan-900/10 dark:to-blue-900/10 rounded-xl p-4 border border-cyan-200/50 dark:border-cyan-700/30">
          <div className="text-xs font-bold text-cyan-700 dark:text-cyan-400 mb-1 uppercase tracking-wide">Ambas Marcam</div>
          <div className="text-3xl font-black text-gray-900 dark:text-white">{ambasMarcam}%</div>
        </div>

        {/* Nível de Risco */}
        <div className={`col-span-2 md:col-span-1 rounded-xl p-4 border ${riskConfig[riskLevel].color}`}>
          <div className="flex items-center justify-between mb-1">
            <div className="text-xs font-bold opacity-70 uppercase tracking-wide">Risco</div>
            <button
              onClick={() => setShowRiskInfo(!showRiskInfo)}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <HelpCircle className="w-4 h-4" />
            </button>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-2xl">{riskConfig[riskLevel].icon}</span>
            <span className="text-xl font-black">
              {riskConfig[riskLevel].label}
            </span>
          </div>
        </div>
      </div>

      {/* Modal de Explicação do Risco */}
      {showRiskInfo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" onClick={() => setShowRiskInfo(false)}>
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full shadow-2xl max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <AlertTriangle className={`w-5 h-5 ${riskConfig[riskLevel]?.color}`} />
                Como calculamos o Risco
              </h3>
              <button onClick={() => setShowRiskInfo(false)} className="text-gray-400 hover:text-gray-600">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                O risco é calculado analisando 3 fatores estatísticos:
              </p>

              <div className="space-y-3">
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm flex-shrink-0">40%</div>
                  <div>
                    <h4 className="font-semibold text-sm text-gray-900 dark:text-white">Entropia da Predição</h4>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Quanto mais dispersas as probabilidades, maior o risco</p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-green-600 text-white flex items-center justify-center font-bold text-sm flex-shrink-0">30%</div>
                  <div>
                    <h4 className="font-semibold text-sm text-gray-900 dark:text-white">Confiança da IA</h4>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Baseado na avaliação de estrelas (1-5)</p>
                  </div>
                </div>

                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold text-sm flex-shrink-0">30%</div>
                  <div>
                    <h4 className="font-semibold text-sm text-gray-900 dark:text-white">Fatores Contextuais</h4>
                    <p className="text-xs text-gray-600 dark:text-gray-400">Clima adverso, lesões importantes, fadiga</p>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-green-50 to-red-50 dark:from-green-900/20 dark:to-red-900/20 rounded-lg p-4 mt-4">
                <h4 className="font-semibold text-sm mb-2">Interpretação:</h4>
                <div className="space-y-2 text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    <span className="font-semibold">BAIXO:</span>
                    <span className="text-gray-600 dark:text-gray-400">Aposta 2-3% do bankroll</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <span className="font-semibold">MÉDIO:</span>
                    <span className="text-gray-600 dark:text-gray-400">Aposta 1-2% do bankroll</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <span className="font-semibold">ALTO:</span>
                    <span className="text-gray-600 dark:text-gray-400">Aposta 0.5-1% (ou evite)</span>
                  </div>
                </div>
              </div>

              <button 
                onClick={() => setShowRiskInfo(false)}
                className="w-full mt-4 bg-primary-600 hover:bg-primary-700 text-white font-semibold py-2.5 px-4 rounded-lg transition-colors"
              >
                Entendi
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
