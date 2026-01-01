import { useState, useEffect } from 'react';
import { matchesAPI, authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useStats } from '../context/StatsContext';
import { Clock, Flame, CalendarDays, Sparkles, Search, X } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import MatchCard from '../components/MatchCard';
import EmptyState from '../components/EmptyState';
import LoadingMascot from '../components/LoadingMascot';
import AnalysisModal from '../components/AnalysisModal';
import LimitReachedModal from '../components/LimitReachedModal';

export default function HomePage() {
  const { user } = useAuth();
  const { refreshStats } = useStats();
  const [allMatches, setAllMatches] = useState([]); // Armazenar todas as partidas
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('upcoming');
  const [selectedLeague, setSelectedLeague] = useState('all');
  const [leagues, setLeagues] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [isMockData, setIsMockData] = useState(false);
  const [dataSource, setDataSource] = useState('');
  const [showLimitModal, setShowLimitModal] = useState(false);

  useEffect(() => {
    loadMatches();
  }, []); // Carregar apenas uma vez ao montar

  useEffect(() => {
    applyFilters();
  }, [selectedLeague, searchQuery, allMatches, filter]);

  const loadMatches = async () => {
    setLoading(true);
    try {
      // Buscar partidas reais da API externa
      const today = new Date().toISOString().split('T')[0];
      const response = await matchesAPI.getFromAPI(today);
      const fetchedMatches = response.data.matches || [];
      
      // Verificar se são dados mock ou reais
      setIsMockData(response.data.is_mock || false);
      setDataSource(response.data.source || 'unknown');
      
      // Armazenar todas as partidas
      setAllMatches(fetchedMatches);
      // Prevenir flash de estado vazio antes de aplicar filtros
      setMatches(fetchedMatches);
      
      // Extrair ligas únicas
      const uniqueLeagues = [...new Set(fetchedMatches.map(m => m.league?.name || m.league))];
      setLeagues(uniqueLeagues);
    } catch (error) {
      console.error('Erro ao carregar partidas:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    // Não filtrar se ainda não temos dados
    if (allMatches.length === 0) {
      return;
    }
    
    let filteredMatches = [...allMatches];
    
    // Filtrar por status (upcoming, today, live, all)
    if (filter !== 'all') {
      const now = new Date();
      const today = now.toISOString().split('T')[0];
      
      filteredMatches = filteredMatches.filter(m => {
        const matchDate = new Date(m.match_date || m.date);
        const matchDay = matchDate.toISOString().split('T')[0];
        const status = m.status;
        
        if (filter === 'live') {
          // Partidas ao vivo (em andamento)
          return ['1H', '2H', 'HT', 'ET', 'BT', 'P', 'LIVE', 'IN_PLAY'].includes(status);
        } else if (filter === 'today') {
          // Partidas de hoje
          return matchDay === today;
        } else if (filter === 'upcoming') {
          // Partidas futuras (não começaram)
          return ['NS', 'TBD', 'NOT_STARTED'].includes(status) || matchDate > now;
        }
        return true;
      });
    }
    
    // Filtrar por liga
    if (selectedLeague !== 'all') {
      filteredMatches = filteredMatches.filter(m => 
        (m.league?.name || m.league) === selectedLeague
      );
    }
    
    // Filtrar por pesquisa
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filteredMatches = filteredMatches.filter(m => {
        const homeTeam = (m.home_team?.name || m.home_team || '').toLowerCase();
        const awayTeam = (m.away_team?.name || m.away_team || '').toLowerCase();
        const league = (m.league?.name || m.league || '').toLowerCase();
        return homeTeam.includes(query) || awayTeam.includes(query) || league.includes(query);
      });
    }
    
    setMatches(filteredMatches);
  };

  const handleAnalyze = async (matchId) => {
    // Pré-checagem: evitar abrir loading se limite já atingido
    try {
      const stats = await authAPI.getStats();
      if (!stats.data.can_analyze) {
        setShowLimitModal(true);
        return;
      }
    } catch (e) {
      // Se stats falhar, continua fluxo normal
    }

    setAnalyzing(true);
    try {
      // Encontrar a partida para exibir no modal
      const match = matches.find(m => m.id === matchId);
      setSelectedMatch(match);

      // Usar quick_analyze para partidas da API (não consome limite)
      if (match) {
        const payload = {
          home_team: match.home_team.name || match.home_team,
          away_team: match.away_team.name || match.away_team,
          league: match.league.name || match.league,
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
        console.log('📤 HOMEPAGE: Enviando requisição de análise');
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

        const response = await matchesAPI.quickAnalyze(payload);
        
        // LOG: Resposta recebida
        console.log('\n' + '='.repeat(80));
        console.log('📥 HOMEPAGE: Resposta da análise recebida');
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
        
        setAnalysis(response.data);

        // Atualizar contador no header quando salvar no histórico
        if (response.data.analysis_id) {
          console.log('🔄 Atualizando contador: analysis_id encontrado, chamando refreshStats()');
          refreshStats();
        }
      }
    } catch (error) {
      console.error('Erro ao analisar partida:', error);
      const errorCode = error.response?.data?.code;
      const statusCode = error.response?.status;
      if (errorCode === 'QUOTA_EXCEEDED' || statusCode === 429) {
        // Abrir modal de limite atingido (sem alert)
        setShowLimitModal(true);
      } else {
        // Opcional: manter silencioso ou usar outro fluxo de erro amigável
      }
    } finally {
      setAnalyzing(false);
    }
  };

  const closeModal = () => {
    setSelectedMatch(null);
    setAnalysis(null);
  };

  const filters = [
    { id: 'upcoming', label: 'Próximas', icon: Clock },
    { id: 'today', label: 'Hoje', icon: CalendarDays },
    { id: 'live', label: 'Ao Vivo', icon: Flame },
    { id: 'all', label: 'Todas', icon: Sparkles },
  ];

  return (
    <div className="page-container">
      <Header showLogo={true} />

      <div className="page-content">
        {/* Data Source Indicator removed per request */}

        {/* Search Bar */}
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" />
            <input
              type="text"
              placeholder="Buscar times ou ligas..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-12 py-3.5 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-2xl border-2 border-gray-200 dark:border-gray-700 focus:border-primary-500 dark:focus:border-primary-500 focus:ring-4 focus:ring-primary-500/20 transition-all outline-none placeholder:text-gray-400 dark:placeholder:text-gray-500"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-4 top-1/2 transform -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <X className="w-4 h-4 text-gray-500 dark:text-gray-400" />
              </button>
            )}
          </div>
        </div>

        {/* League Filters */}
        {leagues.length > 0 && (
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wide">
                Ligas e Divisões
              </span>
              <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700"></div>
            </div>
            <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
              <button
                onClick={() => setSelectedLeague('all')}
                className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all duration-200 ${
                  selectedLeague === 'all'
                    ? 'bg-gradient-to-r from-accent-600 to-accent-700 text-white shadow-md'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                Todas as Ligas
              </button>
              {leagues.map((league) => (
                <button
                  key={league}
                  onClick={() => setSelectedLeague(league)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-all duration-200 ${
                    selectedLeague === league
                      ? 'bg-gradient-to-r from-accent-600 to-accent-700 text-white shadow-md'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                  }`}
                >
                  {league}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Filter Chips */}
        <div className="flex gap-2 overflow-x-auto pb-4 no-scrollbar mb-6" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
          {filters.map((f) => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-2xl font-semibold whitespace-nowrap transition-all duration-200 ${
                filter === f.id
                  ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg shadow-primary-600/30 scale-105'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 shadow-md border border-gray-100 dark:border-gray-700'
              }`}
            >
              <f.icon className="w-4 h-4" />
              {f.label}
            </button>
          ))}
        </div>

        {/* Matches List */}
        {loading ? (
          <LoadingMascot message="Carregando partidas..." />
        ) : matches.length === 0 ? (
          <EmptyState
            variant="no-matches"
            title={`Nenhuma partida ${filter === 'live' ? 'ao vivo' : 'encontrada'}`}
            description="Não há jogos disponíveis no momento. Tente outro filtro ou volte mais tarde."
            action={
              filter !== 'all' && (
                <button
                  onClick={() => setFilter('all')}
                  className="btn-primary"
                >
                  Ver Todas as Partidas
                </button>
              )
            }
          />
        ) : (
          <div className="space-y-4">
            {matches.map((match) => (
              <MatchCard key={match.id} match={match} onAnalyze={handleAnalyze} />
            ))}
          </div>
        )}

        <style>{`
          .no-scrollbar::-webkit-scrollbar {
            display: none;
          }
        `}</style>
      </div>

      <BottomNav />

      {/* Analysis Modal */}
      {analysis && (
        <AnalysisModal
          match={selectedMatch}
          analysis={analysis}
          metadata={analysis.metadata}
          onClose={closeModal}
        />
      )}

      {/* Daily Limit Reached Modal */}
      {showLimitModal && (
        <LimitReachedModal onClose={() => setShowLimitModal(false)} dailyLimit={3} />
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
    </div>
  );
}
