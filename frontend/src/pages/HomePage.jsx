import { useState, useEffect } from 'react';
import { matchesAPI, authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useStats } from '../context/StatsContext';
import { Clock, Flame, CalendarDays, Sparkles, Search, X } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import MatchCard from '../components/MatchCard';
import EmptyState from '../components/EmptyState';
import { MatchListSkeleton, Skeleton } from '../components/Skeleton';
import AnalysisModalProgressive from '../components/AnalysisModalProgressive';
import LimitReachedModal from '../components/LimitReachedModal';

export default function HomePage() {
  const { user } = useAuth();
  const { refreshStats } = useStats();
  const [allMatches, setAllMatches] = useState([]); // Armazenar todas as partidas
  const [matches, setMatches] = useState([]);
  const [displayedMatches, setDisplayedMatches] = useState([]); // Partidas exibidas (paginação)
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);
  const [filter, setFilter] = useState('upcoming');
  const [selectedLeague, setSelectedLeague] = useState('all');
  const [leagues, setLeagues] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [isMockData, setIsMockData] = useState(false);
  const [dataSource, setDataSource] = useState('');
  const [showLimitModal, setShowLimitModal] = useState(false);
  
  const MATCHES_PER_PAGE = 100;

  useEffect(() => {
    loadMatches();
  }, [filter]); // Recarregar quando mudar o filtro (para buscar live)

  useEffect(() => {
    // Debounce para busca (500ms)
    console.log('🔍 useEffect searchQuery:', searchQuery);
    const timer = setTimeout(() => {
      if (searchQuery && searchQuery.length >= 3) {
        console.log('✅ Chamando handleSearch com:', searchQuery);
        handleSearch(searchQuery);
      } else if (searchQuery === '') {
        console.log('🔄 Query vazia, aplicando filtros');
        applyFilters();
      } else {
        console.log('⏳ Query muito curta:', searchQuery.length, 'caracteres');
      }
    }, 500);
    
    return () => clearTimeout(timer);
  }, [searchQuery]);

  useEffect(() => {
    // Aplicar filtros quando mudar liga ou filtro
    if (!searchQuery) {
      applyFilters();
    }
  }, [selectedLeague, allMatches, filter]);
  
  useEffect(() => {
    // Carregar partidas paginadas
    const start = 0;
    const end = page * MATCHES_PER_PAGE;
    setDisplayedMatches(matches.slice(start, end));
  }, [matches, page]);

  const loadMatches = async () => {
    setLoading(true);
    try {
      let fetchedMatches = [];
      
      // Se filtro é 'live', buscar partidas ao vivo diretamente
      if (filter === 'live') {
        console.log('🔴 Buscando partidas AO VIVO...');
        const response = await matchesAPI.getLive();
        fetchedMatches = response.data.matches || [];
        console.log(`✅ ${fetchedMatches.length} partidas ao vivo encontradas`);
      } else {
        // Buscar partidas reais da API externa
        const today = new Date().toISOString().split('T')[0];
        const response = await matchesAPI.getFromAPI(today);
        fetchedMatches = response.data.matches || [];
      }
      
      // Verificar se são dados mock ou reais
      setIsMockData(false);
      setDataSource('api-football');
      
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
      const tomorrow = new Date(now);
      tomorrow.setDate(tomorrow.getDate() + 1);
      const tomorrowStr = tomorrow.toISOString().split('T')[0];
      
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
          // Partidas futuras: hoje e amanhã apenas
          // Priorizar jogos de hoje que ainda não começaram
          return (matchDay === today || matchDay === tomorrowStr) && matchDate >= now;
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
    
    // Ordenar: PRIMEIRO por data (hoje antes de amanhã), DEPOIS por prioridade da liga
    filteredMatches.sort((a, b) => {
      const dateA = new Date(a.match_date || a.date);
      const dateB = new Date(b.match_date || b.date);
      
      // Extrair apenas o dia (sem hora) para agrupar por dia
      const dayA = dateA.toISOString().split('T')[0];
      const dayB = dateB.toISOString().split('T')[0];
      
      // Se são de dias diferentes, ordenar por dia (mais próximo primeiro)
      if (dayA !== dayB) {
        return dateA - dateB;
      }
      
      // Se são do mesmo dia, ordenar por prioridade da liga (ligas principais primeiro)
      const priorityA = a.league_priority || 3;
      const priorityB = b.league_priority || 3;
      
      if (priorityA !== priorityB) {
        return priorityA - priorityB;
      }
      
      // Se mesma prioridade e mesmo dia, ordenar por hora do jogo
      return dateA - dateB;
    });
    
    // Busca local: não filtrar aqui, será tratada pela busca híbrida
    
    setMatches(filteredMatches);
    setPage(1); // Reset página ao filtrar
  };
  
  const handleSearch = async (query) => {
    console.log('🎯 handleSearch iniciado com query:', query);
    
    if (!query || query.trim().length < 3) {
      console.log('❌ Query inválida, aplicando filtros');
      applyFilters();
      return;
    }
    
    console.log('⏳ Iniciando busca...');
    setSearchLoading(true);
    
    try {
      // 1. Busca local primeiro
      console.log('🔎 Buscando localmente em', allMatches.length, 'partidas');
      const localResults = allMatches.filter(m => {
        const q = query.toLowerCase();
        const homeTeam = (m.home_team?.name || m.home_team || '').toLowerCase();
        const awayTeam = (m.away_team?.name || m.away_team || '').toLowerCase();
        const league = (m.league?.name || m.league || '').toLowerCase();
        return homeTeam.includes(q) || awayTeam.includes(q) || league.includes(q);
      });
      
      console.log('📊 Resultados locais:', localResults.length);
      
      // Se encontrou localmente, usar esses resultados
      if (localResults.length > 0) {
        console.log('✅ Usando resultados locais');
        setMatches(localResults);
        setPage(1);
        setSearchLoading(false);
        return;
      }
      
      // 2. Se não encontrou localmente, buscar na API
      console.log('🌐 Nenhum resultado local, buscando na API...');
      const response = await matchesAPI.searchMatches(query);
      const apiResults = response.data.matches || [];
      
      console.log('📡 API retornou:', apiResults.length, 'partidas');
      
      if (apiResults.length > 0) {
        console.log('✅ Adicionando resultados da API ao cache local');
        // Adicionar resultados da API ao cache local
        setAllMatches(prev => {
          const newMatches = [...prev];
          apiResults.forEach(match => {
            if (!newMatches.find(m => m.id === match.id)) {
              newMatches.push(match);
            }
          });
          return newMatches;
        });
        
        setMatches(apiResults);
        setPage(1);
      } else {
        console.log('❌ Nenhum resultado encontrado');
        // Nenhum resultado encontrado
        setMatches([]);
      }
      
    } catch (error) {
      console.error('❌ Erro na busca:', error);
      // Fallback para busca local
      applyFilters();
    } finally {
      console.log('🏁 Busca finalizada');
      setSearchLoading(false);
    }
  };

  const handleAnalyze = (matchId) => {
    // Encontrar a partida para exibir no modal
    const match = matches.find(m => m.id === matchId);
    
    if (!match) {
      console.error('Partida não encontrada:', matchId);
      return;
    }
    
    // Abrir modal progressivo diretamente (sem loading)
    setSelectedMatch(match);
  };

  const closeModal = () => {
    setSelectedMatch(null);
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
            {searchLoading && (
              <div className="absolute right-12 top-1/2 transform -translate-y-1/2">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-500 border-t-transparent"></div>
              </div>
            )}
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
          <MatchListSkeleton count={8} />
        ) : displayedMatches.length === 0 ? (
          <EmptyState
            variant="no-matches"
            title={searchQuery ? 'Nenhuma partida encontrada' : `Nenhuma partida ${filter === 'live' ? 'ao vivo' : 'encontrada'}`}
            description={searchQuery ? `Nenhuma partida encontrada para "${searchQuery}". Tente buscar outro time ou liga.` : "Não há jogos disponíveis no momento. Tente outro filtro ou volte mais tarde."}
            action={
              filter !== 'all' && !searchQuery && (
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
          <>
            <div className="space-y-4">
              {displayedMatches.map((match) => (
                <MatchCard key={match.id} match={match} onAnalyze={handleAnalyze} />
              ))}
            </div>
            
            {/* Load More Button */}
            {displayedMatches.length < matches.length && (
              <div className="flex justify-center mt-6">
                <button
                  onClick={() => setPage(prev => prev + 1)}
                  className="px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl font-medium hover:from-primary-700 hover:to-primary-800 transition-all shadow-lg hover:shadow-xl"
                >
                  Carregar Mais ({matches.length - displayedMatches.length} restantes)
                </button>
              </div>
            )}
            
            {/* Matches Counter */}
            <div className="text-center mt-4 text-sm text-gray-500 dark:text-gray-400">
              Mostrando {displayedMatches.length} de {matches.length} partidas
            </div>
          </>
        )}

        <style>{`
          .no-scrollbar::-webkit-scrollbar {
            display: none;
          }
        `}</style>
      </div>

      <BottomNav />

      {/* Analysis Modal Progressivo */}
      {selectedMatch && (
        <AnalysisModalProgressive
          match={selectedMatch}
          onClose={closeModal}
          onAnalyze={async (strategy) => {
            // Chamar API unificada
            try {
              const response = await matchesAPI.unifiedAnalysis(selectedMatch.id, {
                strategy,
                include_ai: true
              });
              return response.data;
            } catch (error) {
              console.error('Erro ao buscar análise:', error);
              if (error.response?.status === 429 || error.response?.data?.code === 'QUOTA_EXCEEDED') {
                closeModal(); // Fechar modal antes de mostrar limite
                setShowLimitModal(true);
              }
              throw error;
            }
          }}
        />
      )}

      {/* Daily Limit Reached Modal */}
      {showLimitModal && (
        <LimitReachedModal onClose={() => setShowLimitModal(false)} dailyLimit={3} />
      )}
    </div>
  );
}
