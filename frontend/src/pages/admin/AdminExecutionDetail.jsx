import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Clock,
  TrendingUp,
  Target,
  Zap,
  AlertCircle,
  CheckCircle,
  XCircle,
  Calendar,
  Users,
  BarChart3,
  Activity,
  ExternalLink,
  Globe,
  Trophy,
  Database,
  RefreshCw,
  Cpu,
  Timer
} from 'lucide-react';
import { adminAPI } from '../../services/api';
import BottomNav from '../../components/BottomNav';

export default function AdminExecutionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [execution, setExecution] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadExecutionDetail();
  }, [id]);

  const loadExecutionDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await adminAPI.getExecutionDetail(id);
      setExecution(response.data);
    } catch (err) {
      console.error('Erro ao carregar detalhes da execução:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return mins > 0 ? `${mins}min ${secs}s` : `${secs}s`;
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'running':
        return <Activity className="w-6 h-6 text-blue-500 animate-pulse" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-500" />;
      default:
        return <AlertCircle className="w-6 h-6 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400';
      case 'running':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400';
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  const groupMatchesByLeague = (matches) => {
    if (!matches || matches.length === 0) return {};
    
    const grouped = {};
    matches.forEach(match => {
      const league = match.league_name || 'Outras Ligas';
      if (!grouped[league]) {
        grouped[league] = [];
      }
      grouped[league].push(match);
    });
    
    return grouped;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
          </div>
        </div>
        <BottomNav />
      </div>
    );
  }

  if (error || !execution) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 py-8">
          <button
            onClick={() => navigate('/admin/daily-bets')}
            className="btn-ghost mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar
          </button>
          <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
            <p className="text-center text-red-700 dark:text-red-300">
              {error || 'Execução não encontrada'}
            </p>
          </div>
        </div>
        <BottomNav />
      </div>
    );
  }

  const summary = execution.result_summary || {};
  const matchesByLeague = groupMatchesByLeague(summary.analyzed_matches || []);
  const leaguesCount = Object.keys(matchesByLeague).length;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-24">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/admin/daily-bets')}
            className="btn-ghost mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Voltar
          </button>
          
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                Detalhes da Execução #{execution.id}
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                {execution.task_name === 'generate_daily_bets' 
                  ? '🎯 Geração de Bilhetes Diários' 
                  : '✅ Validação de Apostas'}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {getStatusIcon(execution.status)}
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(execution.status)}`}>
                {execution.status === 'success' ? 'Sucesso' : 
                 execution.status === 'running' ? 'Executando' : 
                 execution.status === 'failed' ? 'Falhou' : 'Desconhecido'}
              </span>
            </div>
          </div>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Partidas Analisadas</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {summary.matches_analyzed || 0}
                </p>
              </div>
              <BarChart3 className="w-10 h-10 text-blue-500 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Bilhetes Múltiplos</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {summary.multiple_count || 0}
                </p>
              </div>
              <Target className="w-10 h-10 text-purple-500 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Value Bets</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {summary.value_count || 0}
                </p>
              </div>
              <Zap className="w-10 h-10 text-green-500 opacity-20" />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Ligas Analisadas</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                  {leaguesCount}
                </p>
              </div>
              <Trophy className="w-10 h-10 text-amber-500 opacity-20" />
            </div>
          </div>
        </div>

        {/* Execution Info */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div className="card">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <Clock className="w-5 h-5" />
              Informações de Execução
            </h3>
            <div className="space-y-3">
              <div className="flex items-start justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Iniciado em</span>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {formatDate(execution.started_at)}
                </span>
              </div>

              <div className="flex items-start justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-2">
                  <Timer className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Finalizado em</span>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {formatDate(execution.finished_at)}
                </span>
              </div>

              <div className="flex items-start justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Duração Total</span>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {formatDuration(execution.duration_seconds)}
                </span>
              </div>

              <div className="flex items-start justify-between py-2">
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Iniciado por</span>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {execution.triggered_by_user || execution.triggered_by || 'Sistema'}
                </span>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <Cpu className="w-5 h-5" />
              Métricas Técnicas
            </h3>
            <div className="space-y-3">
              <div className="flex items-start justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Chamadas API</span>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {summary.api_calls || 0}
                </span>
              </div>

              <div className="flex items-start justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-2">
                  <RefreshCw className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Cache Hits</span>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {summary.cache_hits || 0}
                </span>
              </div>

              <div className="flex items-start justify-between py-2 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Modo de Busca</span>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {summary.search_mode === 'hybrid' ? '🔄 Híbrido' :
                   summary.search_mode === 'priority' ? '🎯 Prioritário' :
                   summary.search_mode === 'all' ? '🌍 Todas' : 'N/A'}
                </span>
              </div>

              <div className="flex items-start justify-between py-2">
                <div className="flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-gray-500" />
                  <span className="text-sm text-gray-600 dark:text-gray-400">Fixtures Encontrados</span>
                </div>
                <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {summary.total_fixtures_found || 0}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {execution.error_message && (
          <div className="card bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 mb-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-semibold text-red-700 dark:text-red-300 mb-1">
                  Erro na Execução
                </h4>
                <p className="text-sm text-red-600 dark:text-red-400">
                  {execution.error_message}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Matches by League */}
        {leaguesCount > 0 && (
          <div className="card">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <Trophy className="w-5 h-5" />
              Partidas por Liga ({leaguesCount} ligas)
            </h3>
            
            <div className="space-y-6">
              {Object.entries(matchesByLeague)
                .sort(([, a], [, b]) => b.length - a.length)
                .map(([league, matches]) => (
                  <div key={league} className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-0">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
                        <Globe className="w-4 h-4" />
                        {league}
                      </h4>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {matches.length} partida{matches.length !== 1 ? 's' : ''}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {matches.map((match, idx) => (
                        <Link
                          key={idx}
                          to={`/match/${match.fixture_id}`}
                          className="group card-flat border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 transition-all cursor-pointer"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs text-gray-600 dark:text-gray-400">
                              {match.date ? new Date(match.date).toLocaleDateString('pt-BR') : 'N/A'}
                            </span>
                            <ExternalLink className="w-3 h-3 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                          
                          <div className="space-y-1">
                            <p className="text-sm font-medium text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                              {match.home_team} vs {match.away_team}
                            </p>
                            
                            {match.selected_market && (
                              <div className="flex items-center gap-2 text-xs">
                                <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded">
                                  {match.selected_market}
                                </span>
                                {match.odd && (
                                  <span className="text-gray-600 dark:text-gray-400">
                                    @ {match.odd.toFixed(2)}
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </Link>
                      ))}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Progress Log */}
        {execution.progress_log && execution.progress_log.length > 0 && (
          <div className="card mt-6">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5" />
              Log de Progresso ({execution.progress_log.length} eventos)
            </h3>
            
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {execution.progress_log.slice().reverse().map((log, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg text-sm"
                >
                  <span className="text-xs text-gray-500 dark:text-gray-400 font-mono">
                    {log.timestamp ? new Date(log.timestamp).toLocaleTimeString('pt-BR') : ''}
                  </span>
                  <span className="flex-1 text-gray-700 dark:text-gray-300">
                    {log.message}
                  </span>
                  {log.stage && (
                    <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 rounded">
                      {log.stage}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
