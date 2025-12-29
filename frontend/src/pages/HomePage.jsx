import { useState, useEffect } from 'react';
import { matchesAPI } from '../services/api';
import { Clock, Flame, CalendarDays, Sparkles } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import MatchCard from '../components/MatchCard';
import EmptyState from '../components/EmptyState';
import LoadingMascot from '../components/LoadingMascot';
import AnalysisModal from '../components/AnalysisModal';

export default function HomePage() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('upcoming');
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    loadMatches();
  }, [filter]);

  const loadMatches = async () => {
    setLoading(true);
    try {
      // Sempre buscar partidas reais da API externa
      const today = new Date().toISOString().split('T')[0];
      const response = await matchesAPI.getFromAPI(today);
      setMatches(response.data.matches || []);
    } catch (error) {
      console.error('Erro ao carregar partidas:', error);
    } finally {
      setLoading(false);
    }
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
