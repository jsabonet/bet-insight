import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { matchesAPI, analysisAPI } from '../services/api';
import { ArrowLeft, Brain, AlertCircle } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import LoadingMascot from '../components/LoadingMascot';
import AnalysisModal from '../components/AnalysisModal';
import { TeamLogo, LeagueLogo } from '../utils/logos';

export default function MatchDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  
  const [match, setMatch] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [isExternalMatch, setIsExternalMatch] = useState(false);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    loadMatchDetails();
  }, [id]);

  const loadMatchDetails = async () => {
    try {
      // Tentar buscar do banco de dados primeiro
      const response = await matchesAPI.getDetail(id);
      setMatch(response.data);
      setIsExternalMatch(false);
    } catch (error) {
      // Se 404, tentar buscar da API externa
      if (error.response?.status === 404) {
        try {
          const apiResponse = await matchesAPI.getApiDetail(id);
          setMatch(apiResponse.data.match);
          setIsExternalMatch(true);
        } catch (apiError) {
          console.error('Erro ao carregar partida da API:', apiError);
          setError('Erro ao carregar detalhes da partida');
        }
      } else {
        console.error('Erro ao carregar partida:', error);
        setError('Erro ao carregar detalhes da partida');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRequestAnalysis = async () => {
    setError('');
    setAnalyzing(true);

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
          football_data_id: match.football_data_id || null  // ID da Football-Data.org (para H2H)
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
        const response = await matchesAPI.quickAnalyze(payload);
        
        // LOG: Resposta recebida
        console.log('\n' + '='.repeat(80));
        console.log('📥 MATCH DETAIL PAGE: Resposta da análise recebida');
        console.log('='.repeat(80));
        console.log('✅ Status:', response.status);
        console.log('⭐ Confiança:', response.data.confidence, '/5');
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
          const enriched = response.data.enriched_data;
          
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
          
          // 🔥 TENDÊNCIAS OVER/UNDER E BTTS
          if (enriched.trends) {
            console.log('\n📊 TENDÊNCIAS (últimos 10 jogos):');
            if (enriched.trends.home) {
              console.log(`   🏠 Casa: Over 2.5: ${enriched.trends.home.over_25_pct?.toFixed(0)}% | BTTS: ${enriched.trends.home.btts_pct?.toFixed(0)}%`);
            }
            if (enriched.trends.away) {
              console.log(`   ✈️ Fora: Over 2.5: ${enriched.trends.away.over_25_pct?.toFixed(0)}% | BTTS: ${enriched.trends.away.btts_pct?.toFixed(0)}%`);
            }
            if (enriched.trends.combined_over_25_pct) {
              console.log(`   💡 Probabilidade combinada Over 2.5: ${enriched.trends.combined_over_25_pct?.toFixed(0)}%`);
              console.log(`   💡 Probabilidade combinada BTTS: ${enriched.trends.combined_btts_pct?.toFixed(0)}%`);
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
        
        setAnalysis(response.data);
      } else {
        // Usar request_analysis para partidas do DB
        const response = await analysisAPI.requestAnalysis(id);
        setAnalysis(response.data.analysis);
      }
      setShowModal(true);
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Erro ao gerar análise';
      const errorCode = err.response?.data?.code;
      
      // Mensagem específica para quota excedida
      if (errorCode === 'QUOTA_EXCEEDED' || err.response?.status === 429) {
        setError('⚠️ Limite diário de análises atingido! O plano gratuito permite 20 análises por dia. Tente novamente em algumas horas ou assine o Premium para análises ilimitadas.');
      } else {
        setError(errorMsg);
      }
    } finally {
      setAnalyzing(false);
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
      
      <div className="page-content">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-4 btn-ghost"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar
        </button>

        {/* Card da Partida */}
        <div className="card animate-slide-up mb-6">
          <div className="text-center mb-6">
            <div className="flex items-center justify-center gap-2 mb-3">
              <LeagueLogo league={match.league} size="md" />
              <span className="badge badge-info">{match.league?.name || match.league}</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mt-2">
              {match.home_team?.name || match.home_team} vs {match.away_team?.name || match.away_team}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              {new Date(match.match_date).toLocaleString('pt-PT')}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="text-center p-6 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-2xl border border-transparent dark:border-primary-700/30">
              <div className="flex justify-center mb-3">
                <TeamLogo team={match.home_team} size="xl" />
              </div>
              <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100">{match.home_team?.name || match.home_team}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Casa</p>
            </div>
            <div className="text-center p-6 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-2xl border border-transparent dark:border-blue-700/30">
              <div className="flex justify-center mb-3">
                <TeamLogo team={match.away_team} size="xl" />
              </div>
              <h3 className="font-bold text-lg text-gray-900 dark:text-gray-100">{match.away_team?.name || match.away_team}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Visitante</p>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 text-red-700 dark:text-red-400 px-4 py-3 rounded-xl mb-4 flex items-start gap-2">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {!analysis && (
            <button
              onClick={handleRequestAnalysis}
              disabled={analyzing}
              className="w-full btn-primary flex items-center justify-center gap-2"
            >
              <Brain className="w-5 h-5" />
              {analyzing ? 'Analisando com IA...' : 'Gerar Análise Inteligente'}
            </button>
          )}
        </div>

      </div>

      {/* Modal de Análise */}
      {showModal && analysis && (
        <AnalysisModal
          match={match}
          analysis={analysis}
          metadata={analysis.metadata}
          onClose={() => setShowModal(false)}
        />
      )}

      {/* Analyzing Overlay */}
      {analyzing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-2xl max-w-sm mx-4">
            <LoadingMascot message="Gerando análise com IA..." />
            <p className="text-center text-sm text-gray-600 dark:text-gray-400 mt-4">
              Isso pode levar alguns segundos...
            </p>
          </div>
        </div>
      )}

      <BottomNav />
    </div>
  );
}
