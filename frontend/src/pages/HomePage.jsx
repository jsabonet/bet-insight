import { useState, useEffect } from 'react';
import { matchesAPI } from '../services/api';
import { Clock, Flame, CalendarDays, Sparkles } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import MatchCard from '../components/MatchCard';

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
      <Header 
        title="Partidas" 
        subtitle={`${matches.length} ${filter === 'live' ? 'ao vivo' : 'disponíveis'}`}
      />

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
          <div className="flex justify-center items-center py-20">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-8 h-8 bg-primary-600 rounded-full animate-pulse"></div>
              </div>
            </div>
          </div>
        ) : matches.length === 0 ? (
          <div className="card text-center py-16 animate-slide-up">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CalendarDays className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Nenhuma partida {filter === 'live' ? 'ao vivo' : 'encontrada'}
            </h3>
            <p className="text-gray-600 mb-6">
              Tente selecionar outro filtro
            </p>
            <button
              onClick={() => setFilter('all')}
              className="btn-primary mx-auto"
            >
              Ver Todas
            </button>
          </div>
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
