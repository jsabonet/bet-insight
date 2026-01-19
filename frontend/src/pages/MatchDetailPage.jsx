import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { matchesAPI, analysisAPI, authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useStats } from '../context/StatsContext';
import { useStrategy } from '../context/StrategyContext';
import { ArrowLeft, Brain, AlertCircle, Sparkles, ChevronDown, CheckCircle, HelpCircle, Info, X } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import LoadingMascot from '../components/LoadingMascot';
import AnalysisModal from '../components/AnalysisModal';
import LimitReachedModal from '../components/LimitReachedModal';
import { TeamLogo, LeagueLogo } from '../utils/logos';
import AtAGlance from '../components/match-detail/AtAGlance';
import GoalsAndPoisson from '../components/match-detail/GoalsAndPoisson';
import TeamComparison from '../components/match-detail/TeamComparison';
import ValueBetsSection from '../components/match-detail/ValueBetsSection';
import MatchContext from '../components/match-detail/MatchContext';
import MatchStatistics from '../components/match-detail/MatchStatistics';
import Lineups from '../components/match-detail/Lineups';
import HeadToHead from '../components/match-detail/HeadToHead';
import TeamForm from '../components/match-detail/TeamForm';
import LeagueStandings from '../components/match-detail/LeagueStandings';

export default function MatchDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { refreshStats } = useStats();
  const { strategy } = useStrategy(); // ✅ NOVO: Usar estratégia global
  
  const [match, setMatch] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [statisticalData, setStatisticalData] = useState(null); // Dados estatísticos separados da IA
  const [loading, setLoading] = useState(true);
  const [loadingStats, setLoadingStats] = useState(false); // Loading específico para dados estatísticos
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [isExternalMatch, setIsExternalMatch] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showLimitModal, setShowLimitModal] = useState(false);
  const [showDisclaimerFull, setShowDisclaimerFull] = useState(false);
  const [isMethodologyOpen, setIsMethodologyOpen] = useState(false);
  const [analysisUpdatedAt, setAnalysisUpdatedAt] = useState(null); // ✅ Timestamp última atualização
  const [secondsSinceUpdate, setSecondsSinceUpdate] = useState(0); // ✅ Contador de segundos

  // Normaliza a resposta do backend para o formato híbrido esperado pelo AnalysisModal
  const normalizeAnalysis = (raw) => {
    console.log('🔬 normalizeAnalysis - INPUT:', {
      hasRaw: !!raw,
      rawKeys: raw ? Object.keys(raw) : [],
      hasAnalysisData: !!raw?.analysis_data,
      hasEnrichedData: !!raw?.enriched_data
    });

    if (!raw || typeof raw !== 'object') return raw;

    // Se já tem analysis_data do backend híbrido, usar diretamente
    if (raw.analysis_data) {
      console.log('✅ Usando analysis_data do backend híbrido');
      return { 
        ...raw,
        // Garantir que enriched_data também está disponível
        enriched_data: raw.enriched_data || {}
      };
    }

    // Caso contrário, normalizar formato antigo
    console.log('⚠️ Normalizando formato antigo');
    
    const consensus = (raw.home_probability !== undefined && raw.draw_probability !== undefined && raw.away_probability !== undefined)
      ? {
          home_win: Number(raw.home_probability) / 100,
          draw: Number(raw.draw_probability) / 100,
          away_win: Number(raw.away_probability) / 100,
        }
      : undefined;

    const confidenceStars = typeof raw.confidence === 'number' ? raw.confidence : 3;
    const confidenceDisplay = raw.confidence_display || '';
    const levelPt = confidenceDisplay.includes('Muito') ? 'Muito Alta'
      : confidenceDisplay.includes('Alta') ? 'Alta'
      : confidenceDisplay.includes('Baixa') ? 'Baixa'
      : 'Moderada';

    const recommendation = raw.prediction_display
      ? {
          pick: raw.prediction_display,
          market_display: raw.prediction_display,
          probability: consensus ? Math.max(consensus.home_win, consensus.draw, consensus.away_win) : undefined,
          odd: (raw.odds && typeof raw.odds === 'object') ? (raw.odds.over_25 || raw.odds.home_win || raw.odds.away_win || undefined) : undefined,
        }
      : undefined;

    const decision = recommendation
      ? {
          recommendation,
          confidence: { stars: confidenceStars, level_pt: levelPt, score: confidenceStars / 5 },
          risk: 'medium',
          value_bets: raw.value_bets || [],
        }
      : undefined;

    const weatherFeatures = raw.enriched_data?.weather
      ? {
          weather_impact: raw.enriched_data.weather.weather_impact || 0,
          weather_severity: raw.enriched_data.weather.weather_severity || 'NENHUM',
          has_rain: (raw.enriched_data.weather.rain_mm || 0) > 0,
          has_snow: (raw.enriched_data.weather.snow_mm || 0) > 0,
          has_wind: (raw.enriched_data.weather.wind_speed || 0) > 0,
          temperature: raw.enriched_data.weather.temperature,
          condition: raw.enriched_data.weather.condition,
          rain_mm: raw.enriched_data.weather.rain_mm || 0,
          snow_mm: raw.enriched_data.weather.snow_mm || 0,
          wind_speed: raw.enriched_data.weather.wind_speed || 0,
        }
      : undefined;

    const features = weatherFeatures ? { weather: weatherFeatures } : undefined;

    const modelPredictions = consensus ? { consensus } : undefined;

    const analysis_data = (decision || features || modelPredictions)
      ? { 
          consensus,
          decision, 
          features, 
          model_predictions: modelPredictions,
          fair_odds: raw.fair_odds,
          market_odds: raw.market_odds,
          value_bets: raw.value_bets || [],
          poisson: raw.poisson,
          risk: raw.risk || 'medium'
        }
      : undefined;

    const result = { ...raw, analysis_data, enriched_data: raw.enriched_data || {} };
    
    console.log('🔬 normalizeAnalysis - OUTPUT:', {
      hasAnalysisData: !!result.analysis_data,
      hasEnrichedData: !!result.enriched_data,
      analysisDataKeys: result.analysis_data ? Object.keys(result.analysis_data) : []
    });

    return result;
  };

  useEffect(() => {
    loadMatchDetails();
  }, [id]);

  // Recarregar dados estatísticos quando strategy muda
  useEffect(() => {
    if (match && !loading) {
      console.log(`🔄 Strategy mudou para: ${strategy} - Recarregando análise...`);
      // Dados estatísticos são neutros, não precisam recarregar
      // A estratégia é aplicada apenas no quick_analyze (Ver Análise)
    }
  }, [strategy]);

  // Atualização automática para partidas ao vivo - OTIMIZADO (3 min)
  useEffect(() => {
    if (!match) return;
    
    const isLive = ['LIVE', '1H', '2H', 'HT'].includes(match.status);
    
    if (isLive) {
      console.log('🔴 PARTIDA AO VIVO - Iniciando atualização automática a cada 3 min');
      const interval = setInterval(() => {
        console.log('🔄 Atualizando dados da partida ao vivo...');
        loadMatchDetails();
        loadLiveProbabilities(); // ✅ Atualizar probabilidades ao vivo
      }, 180000); // Atualizar a cada 3 minutos (economizar quota API)
      
      return () => {
        console.log('⏹️ Parando atualização automática');
        clearInterval(interval);
      };
    }
  }, [match?.status]);

  // Contador de segundos desde a última atualização
  useEffect(() => {
    if (!analysisUpdatedAt) return;
    
    const interval = setInterval(() => {
      const seconds = Math.floor((Date.now() - new Date(analysisUpdatedAt).getTime()) / 1000);
      setSecondsSinceUpdate(seconds);
    }, 1000);
    
    return () => clearInterval(interval);
  }, [analysisUpdatedAt]);

  const loadLiveProbabilities = async () => {
    if (!match?.id) return;
    
    try {
      console.log('🔴 Atualizando probabilidades ao vivo...');
      const response = await matchesAPI.getLiveProbabilities(match.id);
      
      if (response.data.success) {
        console.log('✅ Probabilidades atualizadas:', {
          score: `${response.data.match_state.home_score} x ${response.data.match_state.away_score}`,
          elapsed: `${response.data.match_state.elapsed_minutes}'`,
          consensus: response.data.analysis_data.consensus
        });
        
        // Atualizar score do match se mudou
        if (response.data.match_state.home_score !== match.home_score ||
            response.data.match_state.away_score !== match.away_score) {
          setMatch(prev => ({
            ...prev,
            home_score: response.data.match_state.home_score,
            away_score: response.data.match_state.away_score
          }));
        }
        
        // Atualizar análise estatística
        setStatisticalData(prev => ({
          ...prev,
          analysis_data: response.data.analysis_data
        }));
        setAnalysisUpdatedAt(new Date(response.data.updated_at));
      }
    } catch (error) {
      console.error('❌ Erro ao atualizar probabilidades ao vivo:', error);
    }
  };

  const loadMatchDetails = async () => {
    console.log('🔵 loadMatchDetails INICIADO - ID:', id);
    try {
      // Tentar buscar do banco de dados primeiro
      console.log('📥 Buscando partida do banco de dados...');
      const response = await matchesAPI.getDetail(id);
      console.log('✅ Partida carregada do DB:', response.data);
      console.log('📋 Dados recebidos:', {
        hasLineups: !!(response.data.lineups),
        lineupsLength: response.data.lineups?.length,
        hasStatistics: !!(response.data.statistics),
        hasEvents: !!(response.data.events)
      });
      setMatch(response.data);
      setIsExternalMatch(false);
      
      // Carregar preview estatístico rápido
      console.log('🚀 Iniciando loadStatisticalData (preview rápido)...');
      await loadStatisticalData(response.data, false);
      console.log('✅ loadStatisticalData concluído');
    } catch (error) {
      // Se 404, tentar buscar da API externa
      if (error.response?.status === 404) {
        console.log('⚠️ Partida não encontrada no DB (404), buscando da API externa...');
        try {
          const apiResponse = await matchesAPI.getApiDetail(id);
          console.log('✅ Partida carregada da API:', apiResponse.data.match);
          console.log('📋 Dados recebidos:', {
            hasLineups: !!(apiResponse.data.match.lineups),
            lineupsLength: apiResponse.data.match.lineups?.length,
            hasStatistics: !!(apiResponse.data.match.statistics),
            hasEvents: !!(apiResponse.data.match.events)
          });
          setMatch(apiResponse.data.match);
          setIsExternalMatch(true);
          
          // Carregar preview estatístico rápido
          console.log('🚀 Iniciando loadStatisticalData (preview rápido)...');
          await loadStatisticalData(apiResponse.data.match, true);
          console.log('✅ loadStatisticalData concluído');
        } catch (apiError) {
          console.error('❌ Erro ao carregar partida da API:', apiError);
          setError('Erro ao carregar detalhes da partida');
        }
      } else {
        console.error('❌ Erro ao carregar partida:', error);
        setError('Erro ao carregar detalhes da partida');
      }
    } finally {
      console.log('🏁 loadMatchDetails FINALIZADO');
      setLoading(false);
    }
  };

  // Função para carregar dados estatísticos (SEM IA) - RÁPIDO
  const loadStatisticalData = async (matchData, isExternal) => {
    setLoadingStats(true);
    const startTime = performance.now();
    const timestamp = new Date().toISOString();
    
    try {
      console.log('\n' + '🔵'.repeat(80));
      console.log(`📊 CARREGANDO PREVIEW ESTATÍSTICO - ${timestamp}`);
      console.log('🔵'.repeat(80));
      console.log('⏰ Timestamp:', timestamp);
      console.log('🆔 Match ID:', matchData.id || matchData.api_football_id);
      console.log('🏠 Casa:', matchData.home_team?.name || matchData.home_team);
      console.log('✈️ Fora:', matchData.away_team?.name || matchData.away_team);
      console.log('📅 Data:', matchData.date || matchData.match_date);
      console.log('🏆 Liga:', matchData.league?.name || matchData.league);
      console.log('🌍 É partida externa?', isExternal);
      
      const payload = {
        home_team: matchData.home_team?.name || matchData.home_team,
        away_team: matchData.away_team?.name || matchData.away_team,
        league: matchData.league?.name || matchData.league,
        date: matchData.date || matchData.match_date,
        match_id: matchData.id || matchData.api_football_id,
      };

      console.log('\n📤 PAYLOAD ENVIADO:');
      console.log('-'.repeat(80));
      Object.entries(payload).forEach(([key, value]) => {
        const status = value !== null && value !== undefined && value !== '' ? '✅' : '⚠️  NULL';
        console.log(`   ${status} ${key.padEnd(15)} = ${value}`);
      });
      console.log('-'.repeat(80));
      
      console.log('\n⏳ Enviando requisição para statistical_preview...');
      const response = await matchesAPI.statisticalPreview(payload);
      const endTime = performance.now();
      const duration = ((endTime - startTime) / 1000).toFixed(2);
      
      console.log('\n✅ RESPOSTA RECEBIDA:');
      console.log('-'.repeat(80));
      console.log(`⏱️  Tempo de resposta: ${duration}s`);
      console.log('📊 Status:', response.status);
      console.log('🔑 Keys na resposta:', Object.keys(response.data));
      
      if (response.data.analysis_data) {
        console.log('\n📈 ANALYSIS_DATA:');
        console.log('   ✅ consensus:', !!response.data.analysis_data.consensus);
        console.log('   ✅ poisson:', !!response.data.analysis_data.poisson);
        console.log('   ✅ logistic:', !!response.data.analysis_data.logistic);
        console.log('   ✅ features_summary:', !!response.data.analysis_data.features_summary);
        console.log('   ✅ has_real_data:', response.data.analysis_data.has_real_data);
        
        if (response.data.analysis_data.consensus) {
          const c = response.data.analysis_data.consensus;
          console.log('\n🎯 PROBABILIDADES (Consensus):');
          console.log(`   🏠 Casa: ${(c.home_win * 100).toFixed(1)}%`);
          console.log(`   🤝 Empate: ${(c.draw * 100).toFixed(1)}%`);
          console.log(`   ✈️  Fora: ${(c.away_win * 100).toFixed(1)}%`);
        }
        
        if (response.data.analysis_data.features_summary?.strength) {
          const s = response.data.analysis_data.features_summary.strength;
          console.log('\n💪 FORÇA DOS TIMES:');
          console.log(`   🏠 Casa - Ataque: ${s.home_goals_per_game?.toFixed(2)} | Defesa: ${s.home_conceded_per_game?.toFixed(2)}`);
          console.log(`   ✈️  Fora - Ataque: ${s.away_goals_per_game?.toFixed(2)} | Defesa: ${s.away_conceded_per_game?.toFixed(2)}`);
        }
        
        if (response.data.analysis_data.features_summary?.form) {
          const f = response.data.analysis_data.features_summary.form;
          console.log('\n📈 FORMA DOS TIMES:');
          console.log(`   🏠 Casa - Forma: ${f.home_weighted_form?.toFixed(2)} | Momentum: ${f.home_momentum?.toFixed(2)}`);
          console.log(`   ✈️  Fora - Forma: ${f.away_weighted_form?.toFixed(2)} | Momentum: ${f.away_momentum?.toFixed(2)}`);
        }
        
        if (!response.data.analysis_data.features_summary) {
          console.warn('⚠️ features_summary NÃO ESTÁ PRESENTE na resposta!');
        }
      }
      
      console.log('🔵'.repeat(80) + '\n');
      
      const normalized = normalizeAnalysis(response.data);
      setStatisticalData(normalized);
      setAnalysisUpdatedAt(new Date()); // ✅ Marcar timestamp do carregamento inicial
      console.log('✅ Dados normalizados e salvos no state');
      console.log('🏁 loadStatisticalData CONCLUÍDO\n');
    } catch (err) {
      const endTime = performance.now();
      const duration = ((endTime - startTime) / 1000).toFixed(2);
      
      console.log('\n❌ ERRO AO CARREGAR PREVIEW:');
      console.log('-'.repeat(80));
      console.log(`⏱️  Tempo até erro: ${duration}s`);
      console.log('🔴 Erro:', err.message);
      console.log('📊 Status:', err.response?.status);
      console.log('💬 Detalhes:', err.response?.data);
      console.log('-'.repeat(80) + '\n');
      
      console.warn('⚠️ Não foi possível carregar preview estatístico:', err.message);
      // Não mostrar erro ao usuário, dados estatísticos são opcionais
    } finally {
      setLoadingStats(false);
    }
  };

  const handleRequestAnalysis = async () => {
    setError('');
    
    // 🕐 INÍCIO DO TIMER
    const startTime = performance.now();
    console.log('\n' + '🔵'.repeat(40));
    console.log('🚀 INICIANDO ANÁLISE');
    console.log('🔵'.repeat(40));
    console.log('⏰ Início:', new Date().toISOString());
    console.log('📍 Match ID:', id);
    console.log('🏠 Casa:', match.home_team?.name || match.home_team);
    console.log('✈️ Fora:', match.away_team?.name || match.away_team);
    
    // Pré-checagem: evitar abrir loading se limite já atingido
    try {
      const stats = await authAPI.getStats();
      if (!stats.data.can_analyze) {
        console.log('⛔ ANÁLISE BLOQUEADA: Limite atingido');
        console.log('🔵'.repeat(40) + '\n');
        setShowLimitModal(true);
        return;
      }
      console.log('✅ Pré-checagem: Limite disponível');
    } catch (e) {
      console.warn('⚠️ Erro na pré-checagem de limite:', e.message);
    }

    setAnalyzing(true);
    const loadingStartTime = performance.now();

    try {
      if (isExternalMatch) {
        const payload = {
          home_team: match.home_team?.name || match.home_team,
          away_team: match.away_team?.name || match.away_team,
          league: match.league?.name || match.league,
          date: match.date,
          status: match.status,
          venue: match.venue,
          home_score: match.home_score,
          away_score: match.away_score,
          api_id: match.api_football_id || null,  // ID da API-Football
          football_data_id: match.football_data_id || null,  // ID da Football-Data.org (para H2H)
          save_to_history: !!user  // Salvar no histórico se usuário estiver logado
        };

        // LOG: Payload completo sendo enviado
        console.log('\n' + '='.repeat(80));
        console.log('📤 MATCH DETAIL PAGE: Enviando requisição de análise');
        console.log('='.repeat(80));
        console.log('⏰ Timestamp:', new Date().toISOString());
        console.log('\n📊 PAYLOAD COMPLETO:');
        console.log('-'.repeat(80));
        Object.entries(payload).forEach(([key, value]) => {
          const status = value !== null && value !== undefined && value !== '' ? '✅' : '⚠️  NULL';
          const tipo = value === null ? 'null' : typeof value;
          console.log(`   ${status} ${key.padEnd(20)} = ${value} (${tipo})`);
        });
        console.log('-'.repeat(80));
        
        // Verificar IDs das APIs
        console.log('\n🔍 VERIFICAÇÃO DE IDs DAS APIs:');
        console.log(`   ${payload.api_id ? '✅' : '❌'} api_id (API-Football): ${payload.api_id}`);
        console.log(`   ${payload.football_data_id ? '✅' : '❌'} football_data_id (Football-Data.org): ${payload.football_data_id}`);
        console.log('='.repeat(80) + '\n');

        // Usar quick_analyze para partidas externas
        console.log('\n⏳ Enviando requisição para backend...');
        const requestStartTime = performance.now();
        const response = await matchesAPI.quickAnalyze(payload);
        const requestEndTime = performance.now();
        const requestTime = requestEndTime - requestStartTime;
        
        console.log(`✅ Resposta recebida em ${(requestTime / 1000).toFixed(2)}s`);
        console.log('🔥 DEBUG-1: response.data existe?', !!response.data);
        console.log('🔥 DEBUG-2: response.status =', response.status);
        
        // LOG: Resposta recebida
        console.log('\n' + '='.repeat(80));
        console.log('📥 MATCH DETAIL PAGE: Resposta da análise recebida');
        console.log('='.repeat(80));
        console.log('✅ Status:', response.status);
        console.log('⭐ Confiança:', response.data.confidence, '/5');
        console.log(`⏱️ Tempo de resposta da API: ${(requestTime / 1000).toFixed(2)}s`);
        if (response.data.metadata) {
          console.log('\n📊 METADATA (dados analisados):');
          console.log('   Previsões (API-Football):', response.data.metadata.has_predictions ? '✅' : '❌');
          console.log('   Estatísticas ao vivo:', response.data.metadata.has_statistics ? '✅' : '❌');
          console.log('   H2H (Football-Data):', response.data.metadata.has_h2h ? '✅' : '❌');
          if (response.data.metadata.has_h2h) {
            console.log('   └─ Jogos H2H analisados:', response.data.metadata.h2h_count);
          }
          console.log('   Detalhes da partida:', response.data.metadata.has_fixture_details ? '✅' : '❌');
        }
        
        // 🔥 NOVO: Logs de dados enriquecidos
        if (response.data.enriched_data) {
          console.log('\n🔥 DADOS ENRIQUECIDOS RECEBIDOS:');
          console.log('='.repeat(80));
          console.log('🔥 DEBUG-3: Iniciando processamento de enriched_data...');
          
          const enriched = response.data.enriched_data; // 🔥 DEFINIR VARIÁVEL
          
          // Tabela
          if (enriched.table_context) {
            console.log('\n📊 POSIÇÃO NA TABELA:');
            const home = enriched.table_context.home;
            const away = enriched.table_context.away;
            console.log(`   Casa: ${home.position}º lugar, ${home.points} pts (Forma: ${home.form})`);
            console.log(`   Fora: ${away.position}º lugar, ${away.points} pts (Forma: ${away.form})`);
          }
          
          // Lesões
          if (enriched.injuries) {
            const homeInjuries = enriched.injuries.home?.length || 0;
            const awayInjuries = enriched.injuries.away?.length || 0;
            console.log(`\n🚑 LESÕES/SUSPENSÕES: ${homeInjuries} (casa), ${awayInjuries} (fora)`);
          }
          
          // Odds
          if (enriched.odds) {
            console.log('\n💰 ODDS:');
            console.log(`   Casa: ${enriched.odds.home_win} | Empate: ${enriched.odds.draw} | Fora: ${enriched.odds.away_win}`);
            if (enriched.odds.over_25) {
              console.log(`   Over 2.5: ${enriched.odds.over_25} | Under 2.5: ${enriched.odds.under_25}`);
            }
          } else {
            console.log('\n💰 ODDS: ⚠️ Não disponíveis para esta partida');
          }
          
          // Estatísticas detalhadas
          if (enriched.home_stats || enriched.away_stats) {
            console.log('\n📈 ESTATÍSTICAS DOS TIMES:');
            if (enriched.home_stats) {
              console.log(`   Casa: ${enriched.home_stats.goals_per_game_avg?.toFixed(2)} gols/jogo`);
            }
            if (enriched.away_stats) {
              console.log(`   Fora: ${enriched.away_stats.goals_per_game_avg?.toFixed(2)} gols/jogo`);
            }
          }
          
          // 🔥 TENDÊNCIAS OVER/UNDER E AMBAS MARCAM
          if (enriched.trends) {
            console.log('\n📊 TENDÊNCIAS (últimos 10 jogos):');
            if (enriched.trends.home) {
              console.log(`   🏠 Casa: Over 2.5: ${enriched.trends.home.over_25_pct?.toFixed(0)}% | Ambas Marcam: ${enriched.trends.home.btts_pct?.toFixed(0)}%`);
            }
            if (enriched.trends.away) {
              console.log(`   ✈️ Fora: Over 2.5: ${enriched.trends.away.over_25_pct?.toFixed(0)}% | Ambas Marcam: ${enriched.trends.away.btts_pct?.toFixed(0)}%`);
            }
            if (enriched.trends.combined_over_25_pct) {
              console.log(`   💡 Probabilidade combinada Over 2.5: ${enriched.trends.combined_over_25_pct?.toFixed(0)}%`);
              console.log(`   💡 Probabilidade combinada Ambas Marcam: ${enriched.trends.combined_btts_pct?.toFixed(0)}%`);
            }
          }
          
          // ⏱️ DESCANSO ENTRE JOGOS
          if (enriched.rest_context) {
            console.log('\n⏱️ DESCANSO ENTRE JOGOS:');
            console.log(`   🏠 Casa: ${enriched.rest_context.home_days_rest} dias de descanso`);
            console.log(`   ✈️ Fora: ${enriched.rest_context.away_days_rest} dias de descanso`);
            console.log(`   📊 Vantagem física: ${enriched.rest_context.advantage === 'home' ? '🏠 Casa' : enriched.rest_context.advantage === 'away' ? '✈️ Fora' : '⚖️ Igual'}`);
          }
          
          // 🎖️ MOTIVAÇÃO
          if (enriched.motivation) {
            console.log('\n🎖️ MOTIVAÇÃO E CONTEXTO:');
            if (enriched.motivation.context) {
              console.log(`   ${enriched.motivation.context}`);
            }
            console.log(`   🏠 Casa: ${enriched.motivation.home?.toUpperCase()} - ${enriched.motivation.home_reason}`);
            console.log(`   ✈️ Fora: ${enriched.motivation.away?.toUpperCase()} - ${enriched.motivation.away_reason}`);
          }
          
          // 🔄 HISTÓRICO DIRETO (H2H) - FOOTBALL-DATA.ORG
          if (enriched.h2h && Array.isArray(enriched.h2h)) {
            console.log('\n🔄 HISTÓRICO DIRETO (H2H):');
            console.log(`   📊 Total de confrontos: ${enriched.h2h.length} jogos`);
            
            // Contar vitórias
            let homeWins = 0, awayWins = 0, draws = 0;
            enriched.h2h.forEach(match => {
              if (match.score?.fullTime) {
                const homeScore = match.score.fullTime.home;
                const awayScore = match.score.fullTime.away;
                if (homeScore > awayScore) homeWins++;
                else if (awayScore > homeScore) awayWins++;
                else draws++;
              }
            });
            
            console.log(`   🏠 Vitórias Casa: ${homeWins}`);
            console.log(`   ✈️ Vitórias Fora: ${awayWins}`);
            console.log(`   ⚖️ Empates: ${draws}`);
            
            // Mostrar últimos 3 jogos
            const recent = enriched.h2h.slice(0, 3);
            console.log(`   📋 Últimos confrontos:`);
            recent.forEach((match, i) => {
              const date = new Date(match.utcDate).toLocaleDateString('pt-BR');
              const score = match.score?.fullTime ? 
                `${match.score.fullTime.home}-${match.score.fullTime.away}` : 
                'N/A';
              console.log(`      ${i+1}. ${date}: ${match.homeTeam.name} ${score} ${match.awayTeam.name}`);
            });
          } else if (enriched.football_data_id) {
            console.log('\n🔄 HISTÓRICO DIRETO (H2H):');
            console.log(`   ℹ️ football_data_id=${enriched.football_data_id} mapeado, mas H2H não disponível`);
          } else {
            console.log('\n🔄 HISTÓRICO DIRETO (H2H):');
            console.log(`   ⚠️ Não disponível (football_data_id não mapeado)`);
          }
          
          // Contexto da temporada
          if (enriched.season_context) {
            console.log(`\n📅 TEMPORADA: ${enriched.season_context.season} - ${enriched.season_context.round}`);
          }
        }
        console.log('='.repeat(80) + '\n');
        
        console.log('🔥 DEBUG-4: Terminado processamento enriched_data');
        
        // 🔥 NOVO: Log dos dados estruturados do modal completo
        if (response.data.prediction_display) {
          console.log('\n🎯 DADOS ESTRUTURADOS PARA MODAL COMPLETO:');
          console.log('='.repeat(80));
          console.log('📊 Predição:', response.data.prediction_display);
          console.log('⭐ Confiança Display:', response.data.confidence_display);
          console.log('📈 Probabilidades:');
          console.log(`   🏠 Casa: ${response.data.home_probability}%`);
          console.log(`   🤝 Empate: ${response.data.draw_probability}%`);
          console.log(`   ✈️ Fora: ${response.data.away_probability}%`);
          console.log('🔑 Key Factors:', response.data.key_factors?.length || 0, 'itens');
          response.data.key_factors?.forEach((factor, i) => {
            console.log(`   ${i+1}. ${factor}`);
          });
          console.log('='.repeat(80) + '\n');
        }
        
        console.log('🔥 DEBUG-5: Antes de normalizar response.data');
        
        // Normalizar para formato híbrido
        console.log('\n🔬 DEBUG: Normalizando response.data...');
        console.log('   Keys em response.data:', Object.keys(response.data));
        const normalized = normalizeAnalysis(response.data);
        console.log('   ✅ Normalização concluída');
        console.log('   analysis_data adicionado?', !!normalized.analysis_data);
        console.log('   🔬 NORMALIZED tem reasoning?', !!normalized.reasoning);
        console.log('   🔬 NORMALIZED tem analysis?', !!normalized.analysis);
        if (normalized.reasoning) {
          console.log('   📝 Tamanho reasoning:', normalized.reasoning.length, 'caracteres');
          console.log('   📝 Primeiros 100 chars:', normalized.reasoning.substring(0, 100));
        }
        console.log('🔥 DEBUG-6: Antes de setAnalysis()');
        setAnalysis(normalized);
        console.log('🔥 DEBUG-7: Depois de setAnalysis(), antes de refreshStats()');
        // Atualizar contador no header
        console.log('🔄 Chamando refreshStats() após análise externa');
        refreshStats();
        console.log('🔥 DEBUG-8: Depois de refreshStats()');
        
        // 🕐 TEMPO TOTAL ANTES DE ABRIR MODAL
        const beforeModalTime = performance.now();
        const totalBeforeModal = beforeModalTime - startTime;
        console.log(`\n⏱️ TEMPO TOTAL (até setState): ${(totalBeforeModal / 1000).toFixed(2)}s`);
        console.log('   ├─ Pré-checagem + loading: ~0.1s');
        console.log(`   ├─ Requisição backend: ${(requestTime / 1000).toFixed(2)}s`);
        console.log(`   └─ Processamento response: ${((totalBeforeModal - requestTime) / 1000).toFixed(2)}s`);
        
        console.log('\n🎬 DEBUG: Saindo do bloco isExternalMatch, indo para verificação do modal...');
      } else {
        // Usar request_analysis para partidas do DB
        console.log('\n⏳ Enviando requisição para backend (DB)...');
        const requestStartTime = performance.now();
        const response = await analysisAPI.requestAnalysis(id);
        const requestEndTime = performance.now();
        const requestTime = requestEndTime - requestStartTime;
        
        console.log(`✅ Resposta recebida em ${(requestTime / 1000).toFixed(2)}s`);
        
        const normalized = normalizeAnalysis(response.data.analysis);
        setAnalysis(normalized);
        // Atualizar contador no header
        console.log('🔄 Chamando refreshStats() após análise do DB');
        refreshStats();
        
        const beforeModalTime = performance.now();
        const totalBeforeModal = beforeModalTime - startTime;
        console.log(`\n⏱️ TEMPO TOTAL (até setState): ${(totalBeforeModal / 1000).toFixed(2)}s`);
        
        console.log('\n🎬 DEBUG: Saindo do bloco DB, indo para verificação do modal...');
      }
      
      console.log('\n🎬 DEBUG: Chegou no ponto de verificação do modal (após if/else)');
      
      // 🔍 VERIFICAÇÃO ANTES DE ABRIR MODAL
      console.log('\n🔍 VERIFICANDO DADOS PARA MODAL:');
      console.log(`   match: ${match ? '✅ ' + (match.home_team?.name || match.home_team) : '❌ NULL'}`);
      console.log(`   analysis: ${analysis ? '⚠️ STATE (pode estar desatualizado)' : '❌ NULL'}`);
      console.log(`   showModal será setado: true`);
      
      if (!match) {
        console.error('❌ ERRO CRÍTICO: match não está disponível!');
        console.log('🔴 Modal NÃO PODE abrir sem match');
        console.log('🔵'.repeat(40) + '\n');
        setError('Erro: dados da partida não disponíveis');
        setAnalyzing(false);
        return;
      }
      
      // Fechar loading e abrir modal
      setAnalyzing(false);
      setShowModal(true);
      
      // 🕐 TEMPO PARA ABRIR MODAL
      const modalOpenTime = performance.now();
      const modalTime = modalOpenTime - startTime;
      console.log(`\n✅ MODAL SERÁ ABERTO em ${(modalTime / 1000).toFixed(2)}s desde o início`);
      console.log('🔵'.repeat(40) + '\n');
    } catch (err) {
      const endTime = performance.now();
      const totalTime = endTime - startTime;
      
      console.log('\n❌ ERRO NA ANÁLISE');
      console.log(`⏱️ Tempo até erro: ${(totalTime / 1000).toFixed(2)}s`);
      console.log('🔴 Erro:', err.message);
      console.log('🔵'.repeat(40) + '\n');
      
      const errorCode = err.response?.data?.code;
      const statusCode = err.response?.status;
      if (errorCode === 'QUOTA_EXCEEDED' || statusCode === 429) {
        // Mostrar modal de limite atingido e não exibir banner de erro
        setError('');
        setShowLimitModal(true);
      } else {
        const errorMsg = err.response?.data?.error || 'Erro ao gerar análise';
        setError(errorMsg);
      }
    } finally {
      setAnalyzing(false);
      const finalTime = performance.now();
      const totalFinalTime = finalTime - startTime;
      console.log(`\n🏁 PROCESSO FINALIZADO em ${(totalFinalTime / 1000).toFixed(2)}s`);
    }
  };

  if (loading) {
    return (
      <div className="page-container">
        <Header title="Carregando..." />
        <div className="page-content">
          <LoadingMascot message="Carregando detalhes da partida..." />
        </div>
      </div>
    );
  }

  if (!match) {
    return (
      <div className="page-container">
        <Header title="Erro" />
        <div className="page-content">
          <p className="text-center text-gray-600 dark:text-gray-400">Partida não encontrada</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Header title="Análise da Partida" />
      
      <div className="page-content pb-24">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-4 btn-ghost"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar
        </button>

        {/* Header da Partida */}
        <div className="card animate-slide-up mb-6">
          {/* Liga */}
          <div className="text-center mb-6">
            <span className="badge badge-info">{match.league?.name || match.league}</span>
          </div>

          {/* Times e Placar */}
          <div className="flex items-center justify-center gap-8 mb-4">
            {/* Time Casa */}
            <div className="flex flex-col items-center gap-3 flex-1 max-w-[200px]">
              <TeamLogo team={match.home_team} size="xl" />
              <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100 text-center">
                {match.home_team?.name || match.home_team}
              </h3>
              
              {/* Goleadores Casa - apenas para jogos ao vivo ou finalizados */}
              {(match.status === 'FT' || match.status === 'LIVE' || match.status === '1H' || match.status === '2H' || match.status === 'HT') && match.events && (
                <div className="w-full">
                  {match.events
                    .filter(event => 
                      event.type === 'Goal' && 
                      event.team?.name === (match.home_team?.name || match.home_team)
                    )
                    .reduce((acc, event) => {
                      // Agrupar gols por jogador
                      const playerName = event.player?.name || 'Desconhecido';
                      const minute = event.time?.elapsed || '?';
                      const existing = acc.find(g => g.player === playerName);
                      if (existing) {
                        existing.times.push(minute);
                      } else {
                        acc.push({ player: playerName, times: [minute] });
                      }
                      return acc;
                    }, [])
                    .map((goal, idx) => (
                      <div key={idx} className="text-xs text-gray-600 dark:text-gray-400 text-center">
                        ⚽ {goal.player} {goal.times.map(t => `${t}'`).join(', ')}
                      </div>
                    ))
                  }
                </div>
              )}
            </div>

            {/* Placar ou Hora */}
            <div className="flex flex-col items-center gap-2 min-w-[120px]">
              {/* Indicador de Ao Vivo */}
              {(match.status === 'LIVE' || match.status === '1H' || match.status === '2H' || match.status === 'HT') && (
                <div className="flex items-center gap-2 mb-1">
                  <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                  </span>
                  <span className="text-sm font-bold text-red-500 uppercase tracking-wider">AO VIVO</span>
                </div>
              )}
              
              {match.home_score !== null && match.away_score !== null ? (
                <div className="flex items-center gap-4">
                  <span className="text-5xl font-bold text-gray-900 dark:text-white">{match.home_score}</span>
                  <span className="text-3xl font-bold text-gray-400 dark:text-gray-500">-</span>
                  <span className="text-5xl font-bold text-gray-900 dark:text-white">{match.away_score}</span>
                </div>
              ) : (
                <span className="text-3xl font-bold text-gray-900 dark:text-white">
                  {new Date(match.match_date).toLocaleTimeString('pt-PT', {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              )}
              <span className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400 font-semibold">
                {match.status === 'NS' ? 'Não iniciado' : 
                 match.status === 'FT' ? 'Finalizado' :
                 match.status === '1H' ? '1º Tempo' :
                 match.status === 'HT' ? 'Intervalo' :
                 match.status === '2H' ? '2º Tempo' :
                 match.status === 'LIVE' ? 'Ao vivo' : match.status}
              </span>
            </div>

            {/* Time Visitante */}
            <div className="flex flex-col items-center gap-3 flex-1 max-w-[200px]">
              <TeamLogo team={match.away_team} size="xl" />
              <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100 text-center">
                {match.away_team?.name || match.away_team}
              </h3>
              
              {/* Goleadores Fora - apenas para jogos ao vivo ou finalizados */}
              {(match.status === 'FT' || match.status === 'LIVE' || match.status === '1H' || match.status === '2H' || match.status === 'HT') && match.events && (
                <div className="w-full">
                  {match.events
                    .filter(event => 
                      event.type === 'Goal' && 
                      event.team?.name === (match.away_team?.name || match.away_team)
                    )
                    .reduce((acc, event) => {
                      // Agrupar gols por jogador
                      const playerName = event.player?.name || 'Desconhecido';
                      const minute = event.time?.elapsed || '?';
                      const existing = acc.find(g => g.player === playerName);
                      if (existing) {
                        existing.times.push(minute);
                      } else {
                        acc.push({ player: playerName, times: [minute] });
                      }
                      return acc;
                    }, [])
                    .map((goal, idx) => (
                      <div key={idx} className="text-xs text-gray-600 dark:text-gray-400 text-center">
                        ⚽ {goal.player} {goal.times.map(t => `${t}'`).join(', ')}
                      </div>
                    ))
                  }
                </div>
              )}
            </div>
          </div>

          {/* Estatísticas rápidas ao vivo (cartões e últimos eventos) */}
          {(match.status === 'FT' || match.status === 'LIVE' || match.status === '1H' || match.status === '2H' || match.status === 'HT') && match.events && match.events.length > 0 && (
            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-4 mb-4">
              <div className="grid grid-cols-2 gap-4 mb-3">
                {/* Cartões Casa */}
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2">
                    {match.events.filter(e => e.type === 'Card' && e.detail === 'Yellow Card' && e.team?.name === (match.home_team?.name || match.home_team)).length > 0 && (
                      <span className="text-yellow-500 font-bold">
                        🟨 {match.events.filter(e => e.type === 'Card' && e.detail === 'Yellow Card' && e.team?.name === (match.home_team?.name || match.home_team)).length}
                      </span>
                    )}
                    {match.events.filter(e => e.type === 'Card' && e.detail === 'Red Card' && e.team?.name === (match.home_team?.name || match.home_team)).length > 0 && (
                      <span className="text-red-500 font-bold ml-2">
                        🟥 {match.events.filter(e => e.type === 'Card' && e.detail === 'Red Card' && e.team?.name === (match.home_team?.name || match.home_team)).length}
                      </span>
                    )}
                  </div>
                </div>
                
                {/* Cartões Fora */}
                <div className="text-center">
                  <div className="flex items-center justify-center gap-2">
                    {match.events.filter(e => e.type === 'Card' && e.detail === 'Yellow Card' && e.team?.name === (match.away_team?.name || match.away_team)).length > 0 && (
                      <span className="text-yellow-500 font-bold">
                        🟨 {match.events.filter(e => e.type === 'Card' && e.detail === 'Yellow Card' && e.team?.name === (match.away_team?.name || match.away_team)).length}
                      </span>
                    )}
                    {match.events.filter(e => e.type === 'Card' && e.detail === 'Red Card' && e.team?.name === (match.away_team?.name || match.away_team)).length > 0 && (
                      <span className="text-red-500 font-bold ml-2">
                        🟥 {match.events.filter(e => e.type === 'Card' && e.detail === 'Red Card' && e.team?.name === (match.away_team?.name || match.away_team)).length}
                      </span>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Últimos 3 eventos */}
              <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
                <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 text-center">Últimos Eventos</h4>
                <div className="space-y-1">
                  {match.events
                    .slice()
                    .reverse()
                    .slice(0, 5)
                    .map((event, idx) => (
                      <div key={idx} className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-900/50 rounded px-3 py-1.5">
                        <span className="font-semibold text-gray-500 dark:text-gray-500 min-w-[30px]">{event.time?.elapsed}'</span>
                        <span className="flex-1 text-center">
                          {event.type === 'Goal' && '⚽'}
                          {event.type === 'Card' && event.detail === 'Yellow Card' && '🟨'}
                          {event.type === 'Card' && event.detail === 'Red Card' && '🟥'}
                          {event.type === 'subst' && '🔄'}
                          {' '}
                          <span className="font-medium">{event.player?.name || 'Desconhecido'}</span>
                          {event.type === 'Goal' && event.assist?.name && (
                            <span className="text-gray-400 dark:text-gray-500 ml-1">({event.assist.name})</span>
                          )}
                        </span>
                        <span className="text-right text-gray-500 dark:text-gray-500 text-[10px] min-w-[80px] truncate">{event.team?.name}</span>
                      </div>
                    ))
                  }
                </div>
              </div>
            </div>
          )}

          {/* Data e Hora */}
          <div className="text-center mb-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {new Date(match.match_date).toLocaleDateString('pt-PT', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
              })} às {new Date(match.match_date).toLocaleTimeString('pt-PT', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 text-red-700 dark:text-red-400 px-4 py-3 rounded-xl flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Análise Visual - Mostra SEMPRE que houver dados estatísticos */}
        {statisticalData && (
          <div className="space-y-6 animate-fade-in">
            
            {/* Indicador de Atualização Ao Vivo */}
            {analysisUpdatedAt && ['LIVE', '1H', '2H', 'HT'].includes(match?.status) && (
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800/50 px-4 py-3 rounded-xl flex items-center gap-3">
                <div className="flex items-center gap-2 flex-1">
                  <div className="relative">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-ping absolute"></div>
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  </div>
                  <span className="text-sm font-semibold text-green-700 dark:text-green-300">
                    🔴 AO VIVO
                  </span>
                </div>
                <span className="text-xs text-green-600 dark:text-green-400">
                  {secondsSinceUpdate < 60 
                    ? `Atualizado há ${secondsSinceUpdate}s` 
                    : `Atualizado há ${Math.floor(secondsSinceUpdate / 60)}min`
                  }
                  {secondsSinceUpdate > 120 && (
                    <span className="text-amber-600 dark:text-amber-400 ml-2 font-semibold">⚠️ Dados podem estar desatualizados</span>
                  )}
                </span>
              </div>
            )}
            
            {/* Disclaimer Compacto de Responsabilidade */}
            <div className="bg-amber-50/80 dark:bg-amber-900/10 border-l-4 border-amber-500 px-3 sm:px-4 py-2.5 sm:py-3 rounded-r-lg">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs sm:text-sm text-amber-800 dark:text-amber-200">
                    <strong className="font-semibold">Aposte com responsabilidade.</strong> Análises baseadas em dados estatísticos não garantem resultados.
                    <button 
                      onClick={() => setShowDisclaimerFull(true)}
                      className="ml-1 sm:ml-2 underline font-semibold hover:text-amber-900 dark:hover:text-amber-100 transition-colors"
                    >
                      Saiba mais
                    </button>
                  </p>
                </div>
              </div>
            </div>

            {/* Botão de Análise Inteligente - Destaque no topo */}
            <div className="card bg-gradient-to-br from-primary-50 to-indigo-50 dark:from-primary-900/20 dark:to-indigo-900/20 border-2 border-primary-200 dark:border-primary-700 shadow-lg">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
                <div className="flex items-start gap-3 flex-1">
                  <div className="p-2 bg-primary-100 dark:bg-primary-800 rounded-lg">
                    <Brain className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white mb-1">
                      Análise Inteligente da IA
                    </h3>
                    <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                      Gere uma explicação detalhada e contextualizada sobre os dados estatísticos desta partida
                    </p>
                  </div>
                </div>
                <button
                  onClick={handleRequestAnalysis}
                  disabled={analyzing}
                  className="btn-primary inline-flex items-center gap-2 whitespace-nowrap w-full sm:w-auto justify-center"
                >
                  <Sparkles className="w-5 h-5" />
                  {analyzing ? 'Gerando...' : 'Gerar Análise'}
                </button>
              </div>
            </div>
            
            {/* Visão Geral Rápida */}
            <div className="card">
              <AtAGlance analysis={statisticalData} match={match} />
            </div>

            {/* Comparação Visual dos Times */}
            <div className="card">
              <TeamComparison analysis={statisticalData} match={match} />
            </div>

            {/* Gols & Poisson */}
            <div className="card">
              <GoalsAndPoisson analysis={statisticalData} />
            </div>

            {/* Value Bets & Odds */}
            <div className="card">
              <ValueBetsSection analysis={statisticalData} match={match} />
            </div>

            {/* Card "Como Analisamos" - Colapsável */}
            <div className="card overflow-hidden">
              <button 
                onClick={() => setIsMethodologyOpen(!isMethodologyOpen)}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 rounded-lg transition-colors -m-4 mb-0"
              >
                <div className="flex items-center gap-2">
                  <Brain className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                  <h3 className="text-sm sm:text-base font-bold text-gray-900 dark:text-white">
                    Como Analisamos Esta Partida
                  </h3>
                </div>
                
                <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                  <span className="hidden sm:inline text-xs text-gray-500 dark:text-gray-400">
                    {isMethodologyOpen ? 'Ocultar' : 'Ver detalhes'}
                  </span>
                  <ChevronDown 
                    className={`w-4 h-4 text-gray-500 transition-transform duration-300 ${
                      isMethodologyOpen ? 'rotate-180' : ''
                    }`} 
                  />
                </div>
              </button>

              {isMethodologyOpen && (
                <div className="pt-4 space-y-3 sm:space-y-4 animate-fade-in">
                  {/* Passo 1 */}
                  <div className="flex gap-2 sm:gap-3">
                    <div className="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs sm:text-sm">
                      1
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-sm sm:text-base text-gray-900 dark:text-white mb-1">
                        📊 Coleta de Dados Estatísticos
                      </h4>
                      <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2">
                        Coletamos dados de <strong>API-Football</strong> (mais de 200 ligas):
                      </p>
                      <ul className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                        <li>• Últimos 10 jogos de cada time (forma recente)</li>
                        <li>• Confrontos diretos históricos (H2H)</li>
                        <li>• Posição na tabela e pontuação</li>
                        <li>• Lesões, suspensões e descanso</li>
                        <li>• Odds de mercado para calibração</li>
                      </ul>
                    </div>
                  </div>

                  {/* Passo 2 */}
                  <div className="flex gap-2 sm:gap-3">
                    <div className="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs sm:text-sm">
                      2
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-sm sm:text-base text-gray-900 dark:text-white mb-1">
                        ⚙️ Processamento Estatístico
                      </h4>
                      <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2">
                        Aplicamos <strong>2 modelos matemáticos</strong> independentes:
                      </p>
                      <ul className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                        <li>• <strong>Modelo de Poisson:</strong> Calcula gols esperados</li>
                        <li>• <strong>Regressão Logística:</strong> Analisa 97 variáveis</li>
                      </ul>
                    </div>
                  </div>

                  {/* Passo 3 */}
                  <div className="flex gap-2 sm:gap-3">
                    <div className="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs sm:text-sm">
                      3
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-sm sm:text-base text-gray-900 dark:text-white mb-1">
                        🤖 Validação com IA
                      </h4>
                      <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mb-2">
                        Usamos <strong>Google Gemini</strong> para análise contextual:
                      </p>
                      <ul className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 space-y-1 ml-4">
                        <li>• Detecta padrões complexos</li>
                        <li>• Analisa motivação (títulos, rebaixamento)</li>
                        <li>• Considera fatores qualitativos</li>
                      </ul>
                    </div>
                  </div>

                  {/* Passo 4 */}
                  <div className="flex gap-2 sm:gap-3">
                    <div className="flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs sm:text-sm">
                      4
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-sm sm:text-base text-gray-900 dark:text-white mb-1">
                        🎯 Identificação de Value Bets
                      </h4>
                      <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                        Comparamos nossas probabilidades com odds do mercado para encontrar apostas com valor positivo.
                      </p>
                    </div>
                  </div>

                  {/* Resumo */}
                  <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-3 sm:p-4 border border-blue-200 dark:border-blue-800">
                    <p className="text-xs sm:text-sm text-gray-700 dark:text-gray-300">
                      <strong>💡 Importante:</strong> Analisamos com base em DADOS, não em "palpites". 
                      Mas estatísticas não preveem o futuro com 100% de certeza - elas apenas 
                      <strong> aumentam suas chances de acerto</strong>.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Contexto da Partida */}
            <div className="card">
              <MatchContext analysis={statisticalData} match={match} />

              {/* Escalações (Lineups) */}
              {match.lineups && match.lineups.length > 0 && (
                <div className="mt-8">
                  <Lineups lineups={match.lineups} match={match} />
                </div>
              )}

              {/* Estatísticas Detalhadas da Partida */}
              {match.statistics && match.statistics.length > 0 && (
                <div className="mt-8">
                  <MatchStatistics statistics={match.statistics} match={match} />
                </div>
              )}
            </div>

            {/* Confrontos Diretos (H2H) */}
            {match.h2h && match.h2h.length > 0 && (
              <div className="card">
                <HeadToHead 
                  h2h={match.h2h} 
                  homeTeam={{
                    id: match.home_team?.id,
                    name: match.home_team?.name,
                    logo: match.home_team?.logo
                  }}
                  awayTeam={{
                    id: match.away_team?.id,
                    name: match.away_team?.name,
                    logo: match.away_team?.logo
                  }}
                />
              </div>
            )}

            {/* Últimos Jogos dos Times */}
            {((match.home_last_matches && match.home_last_matches.length > 0) || 
              (match.away_last_matches && match.away_last_matches.length > 0)) && (
              <div className="card">
                <TeamForm 
                  homeTeam={{
                    id: match.home_team?.id,
                    name: match.home_team?.name,
                    logo: match.home_team?.logo
                  }}
                  awayTeam={{
                    id: match.away_team?.id,
                    name: match.away_team?.name,
                    logo: match.away_team?.logo
                  }}
                  homeLastMatches={match.home_last_matches}
                  awayLastMatches={match.away_last_matches}
                />
              </div>
            )}

            {/* Classificação da Liga */}
            {match.standings && match.standings.length > 0 && (
              <div className="card">
                <LeagueStandings 
                  standings={match.standings}
                  homeTeam={{
                    id: match.home_team?.id,
                    name: match.home_team?.name,
                    logo: match.home_team?.logo
                  }}
                  awayTeam={{
                    id: match.away_team?.id,
                    name: match.away_team?.name,
                    logo: match.away_team?.logo
                  }}
                />
              </div>
            )}
          </div>
        )}

        {/* Loading dos dados estatísticos */}
        {loadingStats && !statisticalData && (
          <div className="card">
            <div className="text-center py-8">
              <LoadingMascot message="Calculando probabilidades e estatísticas..." />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-4">
                Processando 40+ variáveis estatísticas...
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Modal de Análise - APENAS com explicação da IA */}
      {(() => {
        const shouldShow = showModal && analysis && match;
        
        return shouldShow ? (
          <AnalysisModal
            match={match}
            analysis={analysis}
            metadata={analysis.metadata}
            onClose={() => setShowModal(false)}
          />
        ) : null;
      })()}

      {/* Daily Limit Reached Modal */}
      {showLimitModal && (
        <LimitReachedModal onClose={() => setShowLimitModal(false)} dailyLimit={3} />
      )}

      {/* Disclaimer Full Modal */}
      {showDisclaimerFull && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md w-full shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-amber-600" />
                Aposte com Responsabilidade
              </h3>
              <button 
                onClick={() => setShowDisclaimerFull(false)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                  ⚠️ Aviso Importante
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Esta análise é baseada em dados estatísticos e inteligência artificial, 
                  mas <strong>NÃO garante resultados</strong>. Apostas esportivas envolvem risco financeiro.
                </p>
              </div>

              <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-4 border border-amber-200 dark:border-amber-800">
                <h4 className="font-semibold text-amber-900 dark:text-amber-100 mb-2">
                  Regras de Ouro:
                </h4>
                <ul className="text-sm text-amber-800 dark:text-amber-200 space-y-2">
                  <li className="flex items-start gap-2">
                    <span className="text-amber-600 dark:text-amber-400 flex-shrink-0">•</span>
                    <span>Aposte apenas o que <strong>pode perder</strong></span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-amber-600 dark:text-amber-400 flex-shrink-0">•</span>
                    <span>Nunca use dinheiro essencial (renda, contas, alimentação)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-amber-600 dark:text-amber-400 flex-shrink-0">•</span>
                    <span>Nossa IA serve como <strong>ferramenta de apoio</strong>, não como garantia</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-amber-600 dark:text-amber-400 flex-shrink-0">•</span>
                    <span>Defina um limite diário/mensal e respeite-o</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-amber-600 dark:text-amber-400 flex-shrink-0">•</span>
                    <span>Se perder o controle, procure ajuda profissional</span>
                  </li>
                </ul>
              </div>

              <div className="text-xs text-gray-500 dark:text-gray-400">
                <p>
                  <strong>Lembre-se:</strong> Apostas esportivas devem ser encaradas como entretenimento, 
                  nunca como fonte de renda principal.
                </p>
              </div>
            </div>

            <button
              onClick={() => setShowDisclaimerFull(false)}
              className="mt-6 w-full btn-primary"
            >
              Entendi
            </button>
          </div>
        </div>
      )}

      {/* Analyzing Overlay */}
      {analyzing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-2xl max-w-sm mx-4">
            <LoadingMascot message="Gerando análise estatística..." />
            <p className="text-center text-sm text-gray-600 dark:text-gray-400 mt-4">
              Calculando probabilidades, xG e detectando value bets...
            </p>
          </div>
        </div>
      )}

      <BottomNav />
    </div>
  );
}
