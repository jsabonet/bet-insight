import { useState, useEffect, useMemo } from 'react';
import { X, Star, Sparkles, TrendingUp, AlertCircle, Target, Trophy, Zap, ClipboardList, Loader2, CheckCircle2, Brain, Copy, Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useStrategy } from '../context/StrategyContext';
import { TeamLogo } from '../utils/logos';
import { Skeleton } from './Skeleton';

/**
 * AnalysisModal com Progressive Loading (3 ondas)
 * 
 * Onda 1 (instantâneo): Badge + Probabilidades + Confiança (do card/preview)
 * Onda 2 (2-4s): Top 3 apostas (modelos estatísticos)
 * Onda 3 (5-8s): Análise IA completa
 */
export default function AnalysisModalProgressive({ match, onClose, onAnalyze }) {
  const { user } = useAuth();
  const { strategy, setStrategy } = useStrategy();
  
  // Estados de loading por fase
  const [phase, setPhase] = useState(1); // 1, 2, 3
  const [statisticalData, setStatisticalData] = useState(null); // Onda 1 (preview)
  const [topBets, setTopBets] = useState(null); // Onda 2
  const [aiAnalysis, setAiAnalysis] = useState(null); // Onda 3
  const [error, setError] = useState(null);
  const [localStrategy, setLocalStrategy] = useState(strategy); // Estratégia local do modal
  const [isReloading, setIsReloading] = useState(false);
  const [copied, setCopied] = useState(false);

  // Formatar probabilidade com 1 casa decimal
  const formatProb = (prob) => {
    if (prob === undefined || prob === null || prob === 0) return '0.0';
    const numProb = typeof prob === 'string' ? parseFloat(prob) : prob;
    
    // Se o valor já está em porcentagem (>1), não multiplica
    if (numProb > 1) {
      return numProb.toFixed(1);
    }
    
    // Se está em decimal (0-1), multiplica por 100
    return (numProb * 100).toFixed(1);
  };

  // Carregar dados progressivamente
  useEffect(() => {
    loadProgressiveData();
  }, [match.id, localStrategy]);

  const loadProgressiveData = async () => {
    try {
      setIsReloading(true);
      setError(null);
      
      // ONDA 1: Dados do preview (já disponíveis, instantâneo)
      setPhase(1);
      setStatisticalData(match.preview || match.analysis_data || null);

      // ONDA 2 + 3: Chamar análise completa com estratégia local
      setPhase(2);
      const result = await onAnalyze(localStrategy);
      
      // Estruturar dados do unified endpoint
      if (result) {
        // 🔍 DEBUG: Log completo do resultado
        console.log('🔍 MODAL - Resultado recebido do onAnalyze:', {
          hasResult: !!result,
          resultKeys: Object.keys(result),
          hasStatisticalData: !!result.statistical_data,
          hasEnrichedData: !!result.enriched_data,
          enrichedDataKeys: result.enriched_data ? Object.keys(result.enriched_data) : [],
          statisticalDataHasEnriched: !!result.statistical_data?.enriched_data,
          statisticalEnrichedKeys: result.statistical_data?.enriched_data ? Object.keys(result.statistical_data.enriched_data) : [],
          hasDecisionData: !!result.decision_data,
          hasAiAnalysis: !!result.ai_analysis
        });
        
        // Se for match externo, atualizar informações do match (preservando logos)
        if (result.match_info) {
          // Preservar logo se já existir
          const existingHomeLogo = match.home_team?.logo;
          const existingAwayLogo = match.away_team?.logo;
          
          match.home_team = typeof result.match_info.home_team === 'object'
            ? { ...result.match_info.home_team, logo: result.match_info.home_team.logo || existingHomeLogo }
            : { name: result.match_info.home_team, logo: existingHomeLogo };
            
          match.away_team = typeof result.match_info.away_team === 'object'
            ? { ...result.match_info.away_team, logo: result.match_info.away_team.logo || existingAwayLogo }
            : { name: result.match_info.away_team, logo: existingAwayLogo };
            
          match.league = result.match_info.league;
          match.match_date = result.match_info.match_date;
          
          console.log('🔍 MODAL - Times atualizados preservando logos:', {
            homeTeam: match.home_team,
            awayTeam: match.away_team,
            homeHasLogo: !!match.home_team?.logo,
            awayHasLogo: !!match.away_team?.logo
          });
        }
        
        // Onda 1: Statistical data com enriched_data
        // O enriched_data pode vir em result.enriched_data OU result.statistical_data.enriched_data
        const enrichedData = result.enriched_data || result.statistical_data?.enriched_data || {};
        
        const statsWithEnriched = {
          ...(result.statistical_data || match.analysis_data || {}),
          enriched_data: enrichedData
        };
        
        console.log('🔍 MODAL - statisticalData sendo setado:', {
          hasConsensus: !!statsWithEnriched.consensus,
          hasEnrichedData: !!statsWithEnriched.enriched_data,
          enrichedDataKeys: statsWithEnriched.enriched_data ? Object.keys(statsWithEnriched.enriched_data) : [],
          hasOdds: !!statsWithEnriched.enriched_data?.odds,
          hasTrends: !!statsWithEnriched.enriched_data?.trends,
          hasH2h: !!statsWithEnriched.enriched_data?.h2h,
          hasInjuries: !!statsWithEnriched.enriched_data?.injuries,
          hasRest: !!statsWithEnriched.enriched_data?.rest_context,
          hasMotivation: !!statsWithEnriched.enriched_data?.motivation
        });
        
        setStatisticalData(statsWithEnriched);
        
        // Onda 2: Top bets
        setTopBets(result.decision_data?.top_bets || []);
        
        // Onda 3: AI Analysis
        setPhase(3);
        setAiAnalysis(result.ai_analysis || null);
      }

    } catch (err) {
      console.error('Erro no progressive loading:', err);
      setError(err.message);
    } finally {
      setIsReloading(false);
    }
  };

  // Função para trocar estratégia
  const handleStrategyChange = (newStrategy) => {
    if (newStrategy !== localStrategy) {
      setLocalStrategy(newStrategy);
      // Atualizar estratégia global também
      setStrategy(newStrategy);
    }
  };

  // Função para copiar informações do modal
  const handleCopyAnalysis = async () => {
    try {
      // 🔍 DEBUG: Log dos dados antes de copiar
      console.log('📋 COPY - Dados disponíveis para cópia:', {
        hasStatisticalData: !!statisticalData,
        statisticalDataKeys: statisticalData ? Object.keys(statisticalData) : [],
        hasEnrichedData: !!statisticalData?.enriched_data,
        enrichedDataKeys: statisticalData?.enriched_data ? Object.keys(statisticalData.enriched_data) : [],
        enrichedDataSample: statisticalData?.enriched_data,
        hasTopBets: !!topBets,
        topBetsLength: topBets?.length,
        hasAiAnalysis: !!aiAnalysis
      });
      
      const homeName = match?.home_team?.name || match?.home_team || 'Casa';
      const awayName = match?.away_team?.name || match?.away_team || 'Fora';
      const leagueName = match?.league?.name || 'Liga';
      const matchDate = match?.match_date ? new Date(match.match_date).toLocaleDateString('pt-BR') : 'Data não disponível';
      
      const consensus = statisticalData?.consensus || {};
      const confidence = statisticalData?.confidence || { stars: 0, level_pt: 'N/A' };
      
      let text = `🎯 ANÁLISE - ${homeName} vs ${awayName}\n`;
      text += `📅 ${matchDate} | ${leagueName}\n`;
      text += `📊 Estratégia: ${localStrategy === 'value' ? 'Value Bets' : 'Bilhetes Múltiplos'}\n`;
      text += `\n━━━━━━━━━━━━━━━━━━━━\n\n`;
      
      // Probabilidades
      if (consensus.home_win || consensus.draw || consensus.away_win) {
        text += `📈 PROBABILIDADES\n`;
        text += `🏠 ${homeName}: ${formatProb(consensus.home_win)}%\n`;
        text += `🤝 Empate: ${formatProb(consensus.draw)}%\n`;
        text += `✈️ ${awayName}: ${formatProb(consensus.away_win)}%\n`;
        text += `\n`;
      }
      
      // Confiança
      if (confidence.stars > 0) {
        text += `⭐ CONFIANÇA\n`;
        text += `${'⭐'.repeat(confidence.stars)} ${confidence.level_pt}\n`;
        text += `\n`;
      }
      
      // Top Bets
      if (topBets && topBets.length > 0) {
        text += `🎲 TOP APOSTAS\n`;
        topBets.forEach((bet, index) => {
          text += `${index + 1}. ${bet.market_display}\n`;
          text += `   📊 Probabilidade: ${formatProb(bet.probability)}%\n`;
          if (bet.market_odd) {
            text += `   💰 Odd: ${bet.market_odd.toFixed(2)}\n`;
          }
          if (bet.expected_value) {
            text += `   📈 Valor Esperado: ${bet.expected_value > 0 ? '+' : ''}${(bet.expected_value * 100).toFixed(1)}%\n`;
          }
          if (bet.stake_units) {
            text += `   💵 Stake: ${bet.stake_units.toFixed(1)}u\n`;
          }
          if (bet.reason) {
            text += `   ℹ️ ${bet.reason}\n`;
          }
          text += `\n`;
        });
      }
      
      // Dados Enriquecidos
      const enriched = statisticalData?.enriched_data;
      if (enriched) {
        // Odds
        if (enriched.odds) {
          text += `💰 ODDS DO MERCADO\n`;
          text += `   🏠 Casa: ${enriched.odds.home_win}\n`;
          text += `   🤝 Empate: ${enriched.odds.draw}\n`;
          text += `   ✈️ Fora: ${enriched.odds.away_win}\n`;
          if (enriched.odds.over_25) {
            text += `   ⚽ Over 2.5: ${enriched.odds.over_25}\n`;
          }
          if (enriched.odds.btts) {
            text += `   🎯 Ambas Marcam: ${enriched.odds.btts}\n`;
          }
          text += `\n`;
        }
        
        // Tendências
        if (enriched.trends) {
          text += `📊 TENDÊNCIAS (últimos 10 jogos)\n`;
          if (enriched.trends.home) {
            text += `   🏠 ${homeName}: Over 2.5 em ${enriched.trends.home.over_25_pct}% | BTTS em ${enriched.trends.home.btts_pct}%\n`;
          }
          if (enriched.trends.away) {
            text += `   ✈️ ${awayName}: Over 2.5 em ${enriched.trends.away.over_25_pct}% | BTTS em ${enriched.trends.away.btts_pct}%\n`;
          }
          text += `\n`;
        }
        
        // Lesões
        if (enriched.injuries) {
          const homeInj = enriched.injuries.filter(i => i.team === 'home').length;
          const awayInj = enriched.injuries.filter(i => i.team === 'away').length;
          if (homeInj > 0 || awayInj > 0) {
            text += `🚑 LESÕES/SUSPENSÕES\n`;
            text += `   🏠 ${homeName}: ${homeInj} jogador(es)\n`;
            text += `   ✈️ ${awayName}: ${awayInj} jogador(es)\n`;
            text += `\n`;
          }
        }
        
        // Descanso
        if (enriched.rest_context) {
          text += `⏱️ DESCANSO ENTRE JOGOS\n`;
          text += `   🏠 ${homeName}: ${enriched.rest_context.home_days_rest} dias\n`;
          text += `   ✈️ ${awayName}: ${enriched.rest_context.away_days_rest} dias\n`;
          const advantage = enriched.rest_context.advantage === 'home' ? `🏠 ${homeName}` : 
                           enriched.rest_context.advantage === 'away' ? `✈️ ${awayName}` : '⚖️ Igual';
          text += `   Vantagem física: ${advantage}\n`;
          text += `\n`;
        }
        
        // Motivação
        if (enriched.motivation) {
          text += `🎖️ MOTIVAÇÃO\n`;
          if (enriched.motivation.context) {
            text += `   ${enriched.motivation.context}\n`;
          }
          text += `   🏠 ${enriched.motivation.home}: ${enriched.motivation.home_reason}\n`;
          text += `   ✈️ ${enriched.motivation.away}: ${enriched.motivation.away_reason}\n`;
          text += `\n`;
        }
        
        // H2H
        if (enriched.h2h && Array.isArray(enriched.h2h) && enriched.h2h.length > 0) {
          let homeWins = 0, awayWins = 0, draws = 0;
          enriched.h2h.forEach(match => {
            const isHomeTeamHome = match.home_team === homeName;
            if (match.home_score > match.away_score) {
              isHomeTeamHome ? homeWins++ : awayWins++;
            } else if (match.away_score > match.home_score) {
              isHomeTeamHome ? awayWins++ : homeWins++;
            } else {
              draws++;
            }
          });
          
          text += `🔄 HISTÓRICO DIRETO (H2H)\n`;
          text += `   Total: ${enriched.h2h.length} jogos\n`;
          text += `   🏠 Vitórias ${homeName}: ${homeWins}\n`;
          text += `   ✈️ Vitórias ${awayName}: ${awayWins}\n`;
          text += `   ⚖️ Empates: ${draws}\n`;
          text += `\n`;
        }
        
        // Posição na Tabela
        if (enriched.table_context) {
          text += `📋 POSIÇÃO NA TABELA\n`;
          text += `   🏠 ${homeName}: ${enriched.table_context.home_position}° (${enriched.table_context.home_points} pts)\n`;
          text += `   ✈️ ${awayName}: ${enriched.table_context.away_position}° (${enriched.table_context.away_points} pts)\n`;
          text += `\n`;
        }
      }
      
      // Análise IA
      if (aiAnalysis) {
        text += `🤖 ANÁLISE IA\n`;
        text += `${aiAnalysis}\n`;
        text += `\n`;
      }
      
      text += `━━━━━━━━━━━━━━━━━━━━\n`;
      text += `⚠️ Aposte com responsabilidade. Esta análise não garante resultados.`;
      
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Erro ao copiar:', err);
    }
  };

  const homeName = match?.home_team?.name || match?.home_team || 'Casa';
  const awayName = match?.away_team?.name || match?.away_team || 'Fora';
  
  // Log para debug
  console.log('🔍 DEBUG LOGOS:', {
    matchHomeTeam: match?.home_team,
    matchAwayTeam: match?.away_team,
    homeTeamType: typeof match?.home_team,
    awayTeamType: typeof match?.away_team,
    homeTeamLogo: match?.home_team?.logo,
    awayTeamLogo: match?.away_team?.logo
  });
  
  // Criar objetos de times para o TeamLogo usando useMemo para recalcular quando match mudar
  const homeTeam = useMemo(() => {
    const team = typeof match?.home_team === 'object' && match?.home_team !== null
      ? { 
          name: match.home_team.name || homeName, 
          logo: match.home_team.logo || null 
        }
      : { name: homeName, logo: null };
    console.log('🔍 useMemo homeTeam:', team);
    return team;
  }, [match?.home_team, homeName]);
    
  const awayTeam = useMemo(() => {
    const team = typeof match?.away_team === 'object' && match?.away_team !== null
      ? { 
          name: match.away_team.name || awayName, 
          logo: match.away_team.logo || null 
        }
      : { name: awayName, logo: null };
    console.log('🔍 useMemo awayTeam:', team);
    return team;
  }, [match?.away_team, awayName]);
  
  console.log('🔍 DEBUG TEAM OBJECTS:', { homeTeam, awayTeam });
  
  const consensus = statisticalData?.consensus || {};
  const confidence = statisticalData?.confidence || { stars: 3, level_pt: 'Média' };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999] p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto relative shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 z-10">
          <div className="flex justify-between items-center mb-3">
            <div className="flex items-center gap-3">
              <Brain className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Análise Completa
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyAnalysis}
                disabled={!statisticalData || copied}
                className={`p-2 rounded-lg transition-all ${
                  copied
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400'
                } ${!statisticalData ? 'opacity-50 cursor-not-allowed' : ''}`}
                title="Copiar análise"
              >
                {copied ? (
                  <Check className="w-5 h-5" />
                ) : (
                  <Copy className="w-5 h-5" />
                )}
              </button>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>
          </div>
          
          {/* Strategy Selector */}
          <div className="flex gap-2">
            <button
              onClick={() => handleStrategyChange('value')}
              disabled={isReloading}
              className={`flex-1 px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                localStrategy === 'value'
                  ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              } ${isReloading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <div className="flex items-center justify-center gap-2">
                <Target className="w-4 h-4" />
                <span>Value Bets</span>
              </div>
            </button>
            <button
              onClick={() => handleStrategyChange('multiple')}
              disabled={isReloading}
              className={`flex-1 px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
                localStrategy === 'multiple'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
              } ${isReloading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <div className="flex items-center justify-center gap-2">
                <ClipboardList className="w-4 h-4" />
                <span>Bilhetes</span>
              </div>
            </button>
          </div>
          
          {isReloading && (
            <div className="mt-3 flex items-center justify-center">
              <Skeleton className="h-4 w-64" />
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Match Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 flex-1">
              <div className="flex-1 text-right">
                <TeamLogo team={homeTeam} className="w-12 h-12 mx-auto mb-2" />
                <p className="text-sm font-semibold text-gray-900 dark:text-white">{homeName}</p>
              </div>
              <div className="text-center px-4">
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">vs</p>
                <p className="text-xs text-gray-400">{match.league?.name || 'N/A'}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {match.match_date ? new Date(match.match_date).toLocaleDateString('pt-BR', {
                    day: '2-digit',
                    month: 'short'
                  }) : 'N/A'}
                </p>
              </div>
              <div className="flex-1 text-left">
                <TeamLogo team={awayTeam} className="w-12 h-12 mx-auto mb-2" />
                <p className="text-sm font-semibold text-gray-900 dark:text-white">{awayName}</p>
              </div>
            </div>
          </div>

          {/* ============ ONDA 1: Dados Instantâneos ============ */}
          {phase >= 1 && (
            <div className="space-y-4 animate-fade-in">
              {/* Strategy Badge - Removido (agora está no header) */}
              
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
                      {formatProb(consensus.home_win)}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">🤝 Empate</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {formatProb(consensus.draw)}%
                    </p>
                  </div>
                  <div className="text-center">
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">✈️ Fora</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {formatProb(consensus.away_win)}%
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
            <div className="flex flex-col items-center justify-center py-8 animate-fade-in">
              <Loader2 className="w-8 h-8 text-purple-600 dark:text-purple-400 animate-spin mb-3" />
              <p className="text-sm text-gray-600 dark:text-gray-400">Calculando melhores apostas...</p>
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
                        {formatProb(bet.probability)}%
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
                        {typeof bet.stake_units === 'number' ? bet.stake_units.toFixed(1) : bet.stake_units}u
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

          {/* ============ DADOS ENRIQUECIDOS ============ */}
          {statisticalData?.enriched_data && Object.keys(statisticalData.enriched_data).length > 0 && (
            <div className="space-y-3 animate-fade-in">
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
                <Zap className="w-4 h-4" />
                DADOS ADICIONAIS
              </h3>
              
              {/* Odds */}
              {statisticalData.enriched_data.odds && (
                <div className="bg-gradient-to-r from-amber-50 to-yellow-50 dark:from-amber-900/20 dark:to-yellow-900/20 rounded-lg p-4 border border-amber-200 dark:border-amber-800">
                  <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-2">💰 ODDS DO MERCADO</h4>
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="text-center">
                      <p className="text-gray-500 dark:text-gray-400">Casa</p>
                      <p className="font-bold text-gray-900 dark:text-white">{statisticalData.enriched_data.odds.home_win}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-500 dark:text-gray-400">Empate</p>
                      <p className="font-bold text-gray-900 dark:text-white">{statisticalData.enriched_data.odds.draw}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-500 dark:text-gray-400">Fora</p>
                      <p className="font-bold text-gray-900 dark:text-white">{statisticalData.enriched_data.odds.away_win}</p>
                    </div>
                  </div>
                  {(statisticalData.enriched_data.odds.over_25 || statisticalData.enriched_data.odds.btts) && (
                    <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
                      {statisticalData.enriched_data.odds.over_25 && (
                        <div className="text-center">
                          <p className="text-gray-500 dark:text-gray-400">Over 2.5</p>
                          <p className="font-bold text-gray-900 dark:text-white">{statisticalData.enriched_data.odds.over_25}</p>
                        </div>
                      )}
                      {statisticalData.enriched_data.odds.btts && (
                        <div className="text-center">
                          <p className="text-gray-500 dark:text-gray-400">BTTS</p>
                          <p className="font-bold text-gray-900 dark:text-white">{statisticalData.enriched_data.odds.btts}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
              
              {/* Tendências */}
              {statisticalData.enriched_data.trends && (
                <div className="bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
                  <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-2">📊 TENDÊNCIAS (últimos 10 jogos)</h4>
                  <div className="space-y-2 text-xs">
                    {statisticalData.enriched_data.trends.home && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">🏠 {homeName}</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          Over 2.5: {statisticalData.enriched_data.trends.home.over_25_pct}% | BTTS: {statisticalData.enriched_data.trends.home.btts_pct}%
                        </span>
                      </div>
                    )}
                    {statisticalData.enriched_data.trends.away && (
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">✈️ {awayName}</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          Over 2.5: {statisticalData.enriched_data.trends.away.over_25_pct}% | BTTS: {statisticalData.enriched_data.trends.away.btts_pct}%
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* Lesões + Descanso + Motivação em grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {/* Lesões */}
                {statisticalData.enriched_data.injuries && statisticalData.enriched_data.injuries.length > 0 && (
                  <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-3 border border-red-200 dark:border-red-800">
                    <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-2">🚑 LESÕES</h4>
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Casa</span>
                        <span className="font-bold text-red-600 dark:text-red-400">
                          {statisticalData.enriched_data.injuries.filter(i => i.team === 'home').length}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Fora</span>
                        <span className="font-bold text-red-600 dark:text-red-400">
                          {statisticalData.enriched_data.injuries.filter(i => i.team === 'away').length}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Descanso */}
                {statisticalData.enriched_data.rest_context && (
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-3 border border-green-200 dark:border-green-800">
                    <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-2">⏱️ DESCANSO</h4>
                    <div className="space-y-1 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Casa</span>
                        <span className="font-bold text-gray-900 dark:text-white">
                          {statisticalData.enriched_data.rest_context.home_days_rest}d
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Fora</span>
                        <span className="font-bold text-gray-900 dark:text-white">
                          {statisticalData.enriched_data.rest_context.away_days_rest}d
                        </span>
                      </div>
                      <div className="text-center pt-1 border-t border-green-200 dark:border-green-700">
                        <span className="font-semibold text-green-700 dark:text-green-300">
                          {statisticalData.enriched_data.rest_context.advantage === 'home' ? '🏠 Casa' : 
                           statisticalData.enriched_data.rest_context.advantage === 'away' ? '✈️ Fora' : '⚖️ Igual'}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Motivação */}
                {statisticalData.enriched_data.motivation && (
                  <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-3 border border-purple-200 dark:border-purple-800">
                    <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-2">🎖️ MOTIVAÇÃO</h4>
                    <div className="space-y-1 text-xs">
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Casa: </span>
                        <span className="font-bold text-purple-600 dark:text-purple-400">
                          {statisticalData.enriched_data.motivation.home?.toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600 dark:text-gray-400">Fora: </span>
                        <span className="font-bold text-purple-600 dark:text-purple-400">
                          {statisticalData.enriched_data.motivation.away?.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              {/* H2H */}
              {statisticalData.enriched_data.h2h && Array.isArray(statisticalData.enriched_data.h2h) && statisticalData.enriched_data.h2h.length > 0 && (
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg p-4 border border-indigo-200 dark:border-indigo-800">
                  <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-2">🔄 HISTÓRICO DIRETO (H2H)</h4>
                  <div className="flex justify-around text-xs">
                    <div className="text-center">
                      <p className="text-gray-500 dark:text-gray-400">🏠 Vitórias Casa</p>
                      <p className="font-bold text-xl text-gray-900 dark:text-white">
                        {statisticalData.enriched_data.h2h.filter(m => {
                          const isHomeTeamHome = m.home_team === homeName;
                          if (m.home_score > m.away_score) return isHomeTeamHome;
                          if (m.away_score > m.home_score) return !isHomeTeamHome;
                          return false;
                        }).length}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-500 dark:text-gray-400">⚖️ Empates</p>
                      <p className="font-bold text-xl text-gray-900 dark:text-white">
                        {statisticalData.enriched_data.h2h.filter(m => m.home_score === m.away_score).length}
                      </p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-500 dark:text-gray-400">✈️ Vitórias Fora</p>
                      <p className="font-bold text-xl text-gray-900 dark:text-white">
                        {statisticalData.enriched_data.h2h.filter(m => {
                          const isHomeTeamHome = m.home_team === homeName;
                          if (m.home_score > m.away_score) return !isHomeTeamHome;
                          if (m.away_score > m.home_score) return isHomeTeamHome;
                          return false;
                        }).length}
                      </p>
                    </div>
                  </div>
                  <p className="text-center text-gray-500 dark:text-gray-400 text-xs mt-2">
                    {statisticalData.enriched_data.h2h.length} confrontos analisados
                  </p>
                </div>
              )}
              
              {/* Posição na Tabela */}
              {statisticalData.enriched_data.table_context && (
                <div className="bg-gradient-to-r from-gray-50 to-slate-50 dark:from-gray-800/50 dark:to-slate-800/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
                  <h4 className="text-xs font-semibold text-gray-600 dark:text-gray-300 mb-2">📋 POSIÇÃO NA TABELA</h4>
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <p className="text-gray-500 dark:text-gray-400 mb-1">🏠 {homeName}</p>
                      <p className="font-bold text-lg text-gray-900 dark:text-white">
                        {statisticalData.enriched_data.table_context.home_position}°
                        <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
                          ({statisticalData.enriched_data.table_context.home_points} pts)
                        </span>
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500 dark:text-gray-400 mb-1">✈️ {awayName}</p>
                      <p className="font-bold text-lg text-gray-900 dark:text-white">
                        {statisticalData.enriched_data.table_context.away_position}°
                        <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
                          ({statisticalData.enriched_data.table_context.away_points} pts)
                        </span>
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ============ ONDA 3: Análise IA (Loading) ============ */}
          {phase === 3 && !aiAnalysis && (
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg p-8 animate-fade-in">
              <div className="flex flex-col items-center justify-center">
                <Sparkles className="w-10 h-10 text-purple-600 dark:text-purple-400 animate-pulse mb-3" />
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Gerando análise com IA...</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Analisando padrões e contexto</p>
              </div>
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
