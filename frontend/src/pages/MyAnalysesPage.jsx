import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisAPI } from '../services/api';
import api from '../services/api';
import { useStats } from '../context/StatsContext';
import { useAuth } from '../context/AuthContext';
import { Calendar, TrendingUp, Target, Star } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import EmptyState from '../components/EmptyState';
import LoadingMascot from '../components/LoadingMascot';
import AnalysisModal from '../components/AnalysisModal';

export default function MyAnalysesPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { refreshTrigger } = useStats();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [stats, setStats] = useState({
    total: 0,
    today: 0,
    accuracy: 0,
  });
  const [userStats, setUserStats] = useState(null);

  useEffect(() => {
    loadAnalyses();
    loadUserStats();
  }, []);

  useEffect(() => {
    // Atualizar métricas quando houver mudanças globais (ex: novas análises)
    loadUserStats();
  }, [refreshTrigger]);

  const loadAnalyses = async () => {
    try {
      const response = await analysisAPI.getUserAnalyses();
      console.log('📊 Análises carregadas:', response.data);
      console.log('📊 Primeira análise (se existir):', response.data.results?.[0]);
      
      const analysesData = response.data.results || response.data || [];
      setAnalyses(analysesData);
      
      // Calculate stats
      const total = analysesData.length || 0;
      const today = analysesData.filter(a => {
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
      console.error('Detalhes:', error.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const loadUserStats = async () => {
    try {
      const res = await api.get('/users/stats/');
      setUserStats(res.data);
    } catch (error) {
      console.error('Erro ao carregar métricas de usuário:', error);
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 4) return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-950/50 border-green-200 dark:border-green-800/30';
    if (confidence >= 3) return 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/50 border-blue-200 dark:border-blue-800/30';
    return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700/30';
  };

  if (loading) {
    return (
      <div className="page-container">
        <Header title="Minhas Análises" />
        <div className="page-content">
          <LoadingMascot message="Carregando suas análises..." />
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
              <Target className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total}</p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Total</p>
          </div>

          <div className="card-flat text-center">
            <div className="flex items-center justify-center mb-2">
              <Calendar className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.today}</p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Hoje</p>
          </div>

          <div className="card-flat text-center">
            <div className="flex items-center justify-center mb-2">
              <Star className="w-8 h-8 text-yellow-600 dark:text-yellow-400" />
            </div>
            <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              {userStats?.daily_limit ?? (user?.is_premium ? '100' : '5')}
            </p>
            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">Limite</p>
            {userStats && (
              <p className="text-[10px] text-gray-500 dark:text-gray-400 mt-0.5">
              </p>
            )}
          </div>
        </div>

        {/* Analyses List */}
        {analyses.length === 0 ? (
          <EmptyState
            variant="no-analyses"
            title="Nenhuma análise ainda"
            description="Comece a analisar partidas para ver seu histórico aqui. Suas análises ajudam a melhorar suas apostas!"
            action={
              <button
                onClick={() => navigate('/')}
                className="btn-primary"
              >
                Ver Partidas Disponíveis
              </button>
            }
          />
        ) : (
          <div className="space-y-4">
            {analyses.map((analysis) => (
              <div
                key={analysis.id}
                className="match-card group animate-slide-up"
                onClick={() => setSelectedAnalysis(analysis)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-xs text-gray-600 dark:text-gray-400 font-medium bg-gray-100 dark:bg-gray-800/50 px-2 py-1 rounded">
                        {analysis.match.league.name}
                      </span>
                      <span className={`text-xs px-3 py-1 rounded-full font-semibold border ${getConfidenceColor(analysis.confidence)}`}>
                        {analysis.confidence_display}
                      </span>
                    </div>
                    
                    <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2 transition-colors">
                      {analysis.match.home_team.name} vs {analysis.match.away_team.name}
                    </h3>
                    
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      {new Date(analysis.match.match_date).toLocaleDateString('pt-PT', {
                        day: '2-digit',
                        month: 'long',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>

                    <div className="flex items-center gap-4 flex-wrap">
                      <div className="flex items-center gap-2 bg-primary-50 dark:bg-primary-900/30 border border-primary-200 dark:border-primary-800 rounded-lg px-3 py-1.5">
                        <Target className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                        <span className="text-sm font-bold text-primary-700 dark:text-primary-300">
                          {analysis.prediction_display}
                        </span>
                      </div>
                      
                      {analysis.home_xg && analysis.away_xg && (
                        <div className="flex items-center gap-2 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg px-3 py-1.5">
                          <TrendingUp className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                          <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
                            xG: {analysis.home_xg} - {analysis.away_xg}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="text-right ml-4 bg-gray-100 dark:bg-gray-800/50 rounded-lg px-3 py-2 border border-gray-200 dark:border-gray-700/50">
                    <div className="text-xs text-gray-500 dark:text-gray-500 mb-1">
                      Analisado em
                    </div>
                    <div className="text-sm font-semibold text-gray-900 dark:text-gray-300">
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

      {/* Modal de Análise */}
      {selectedAnalysis && (
        <AnalysisModal
          isOpen={!!selectedAnalysis}
          onClose={() => setSelectedAnalysis(null)}
          analysis={selectedAnalysis}
          match={selectedAnalysis.match}
        />
      )}
    </div>
  );
}
