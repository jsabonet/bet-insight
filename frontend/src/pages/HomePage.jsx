import { useState, useEffect } from 'react';
import { matchesAPI } from '../services/api';
import { Clock, Flame, CalendarDays, Sparkles } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import MatchCard from '../components/MatchCard';
import EmptyState from '../components/EmptyState';
import LoadingMascot from '../components/LoadingMascot';

export default function HomePage() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('upcoming');

  useEffect(() => {
    loadMatches();
  }, [filter]);

  const loadMatches = async () => {
    setLoading(true);
    try {
      let response;
      switch (filter) {
        case 'today':
          response = await matchesAPI.getToday();
          break;
        case 'live':
          response = await matchesAPI.getLive();
          break;
        case 'upcoming':
          response = await matchesAPI.getUpcoming();
          break;
        default:
          response = await matchesAPI.getAll();
      }
      setMatches(response.data.results || response.data);
    } catch (error) {
      console.error('Erro ao carregar partidas:', error);
    } finally {
      setLoading(false);
    }
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
                  : 'bg-white text-gray-700 hover:bg-gray-50 shadow-md border border-gray-100'
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
              <MatchCard key={match.id} match={match} />
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
    </div>
  );
}
