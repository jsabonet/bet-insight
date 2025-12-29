import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Calendar, TrendingUp, Target, Star } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';

export default function MyAnalysesPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    today: 0,
    accuracy: 0,
  });

  useEffect(() => {
    loadAnalyses();
  }, []);

  const loadAnalyses = async () => {
    try {
      const response = await analysisAPI.getUserAnalyses();
      setAnalyses(response.data.results || response.data);
      
      // Calculate stats
      const total = response.data.results?.length || response.data.length || 0;
      const today = (response.data.results || response.data).filter(a => {
        const analysisDate = new Date(a.created_at);
        const todayDate = new Date();
        return analysisDate.toDateString() === todayDate.toDateString();
      }).length;
      
      setStats({
        total,
        today,
        accuracy: 0, // Will be calculated when we have match results
      });
    } catch (error) {
      console.error('Erro ao carregar análises:', error);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 4) return 'text-green-600 bg-green-50';
    if (confidence >= 3) return 'text-blue-600 bg-blue-50';
    return 'text-gray-600 bg-gray-50';
  };

  if (loading) {
    return (
      <div className="page-container">
        <Header title="Minhas Análises" />
        <div className="page-content text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Header title="Minhas Análises" subtitle={`${stats.total} análises realizadas`} />
      
      <div className="page-content">

        {/* Stats Cards */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="card-flat text-center">
            <div className="flex items-center justify-center mb-2">
              <Target className="w-8 h-8 text-primary-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            <p className="text-xs text-gray-600 mt-1">Total</p>
          </div>

          <div className="card-flat text-center">
            <div className="flex items-center justify-center mb-2">
              <Calendar className="w-8 h-8 text-blue-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{stats.today}</p>
            <p className="text-xs text-gray-600 mt-1">Hoje</p>
          </div>

          <div className="card-flat text-center">
            <div className="flex items-center justify-center mb-2">
              <Star className="w-8 h-8 text-yellow-600" />
            </div>
            <p className="text-2xl font-bold text-gray-900">
              {user?.is_premium ? '100' : '5'}
            </p>
            <p className="text-xs text-gray-600 mt-1">Limite</p>
          </div>
        </div>

        {/* Analyses List */}
        {analyses.length === 0 ? (
          <div className="card text-center py-16 animate-slide-up">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-10 h-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              Nenhuma análise ainda
            </h3>
            <p className="text-gray-600 mb-6">
              Comece a analisar partidas para ver seu histórico aqui
            </p>
            <button
              onClick={() => navigate('/')}
              className="btn-primary"
            >
              Ver Partidas
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {analyses.map((analysis) => (
              <div
                key={analysis.id}
                className="match-card group animate-slide-up"
                onClick={() => navigate(`/match/${analysis.match.id}`)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs text-gray-500">
                        {analysis.match.league.name}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${getConfidenceColor(analysis.confidence)}`}>
                        {analysis.confidence_display}
                      </span>
                    </div>
                    
                    <h3 className="text-lg font-bold text-gray-900 mb-1">
                      {analysis.match.home_team.name} vs {analysis.match.away_team.name}
                    </h3>
                    
                    <p className="text-sm text-gray-600 mb-3">
                      {new Date(analysis.match.match_date).toLocaleDateString('pt-PT', {
                        day: '2-digit',
                        month: 'long',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>

                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-2">
                        <Target className="w-4 h-4 text-primary-600" />
                        <span className="text-sm font-medium text-gray-900">
                          {analysis.prediction_display}
                        </span>
                      </div>
                      
                      {analysis.home_xg && analysis.away_xg && (
                        <div className="flex items-center gap-2">
                          <TrendingUp className="w-4 h-4 text-blue-600" />
                          <span className="text-sm text-gray-600">
                            xG: {analysis.home_xg} - {analysis.away_xg}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="text-right ml-4">
                    <div className="text-xs text-gray-500 mb-1">
                      Analisado em
                    </div>
                    <div className="text-sm font-medium text-gray-900">
                      {new Date(analysis.created_at).toLocaleDateString('pt-PT')}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
