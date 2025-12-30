import { useState, useEffect } from 'react';
import { matchesAPI } from '../services/api';
import { Clock, Flame, CalendarDays, Sparkles, Search, X } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import MatchCard from '../components/MatchCard';
import EmptyState from '../components/EmptyState';
import LoadingMascot from '../components/LoadingMascot';
import AnalysisModal from '../components/AnalysisModal';

export default function HomePage() {
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
    setAnalyzing(true);
    try {
      // Encontrar a partida para exibir no modal
      const match = matches.find(m => m.id === matchId);
      setSelectedMatch(match);

      // Usar quick_analyze para partidas da API (não consome limite)
      if (match) {
        const response = await matchesAPI.quickAnalyze({
          home_team: match.home_team.name || match.home_team,
          away_team: match.away_team.name || match.away_team,
          league: match.league.name || match.league
        });
        setAnalysis(response.data);
      }
    } catch (error) {
      console.error('Erro ao analisar partida:', error);
      alert(error.response?.data?.error || 'Erro ao gerar análise. Tente novamente.');
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
        {/* Data Source Indicator */}
        {!loading && (
          <div className={`mb-4 px-4 py-2.5 rounded-xl text-sm font-medium flex items-center gap-2 ${
            isMockData 
              ? 'bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800' 
              : 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300 border border-green-200 dark:border-green-800'
          }`}>
            <div className={`w-2 h-2 rounded-full ${isMockData ? 'bg-amber-500' : 'bg-green-500'} animate-pulse`}></div>
            {isMockData ? (
              <span>📋 Dados de exemplo - Pausa de fim de ano (partidas reais voltam em Janeiro 2026)</span>
            ) : (
              <span>✅ Dados reais da API-Football</span>
            )}
          </div>
        )}

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
          onClose={closeModal}
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
    </div>
  );
}
