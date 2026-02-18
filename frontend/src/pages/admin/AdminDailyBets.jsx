import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  ArrowLeft,
  Play,
  CheckCircle,
  Clock,
  XCircle,
  Calendar,
  TrendingUp,
  Activity,
  RefreshCw,
  Zap,
  AlertCircle,
} from 'lucide-react';
import Header from '../../components/Header';
import BottomNav from '../../components/BottomNav';
import { adminAPI } from '../../services/api';

export default function AdminDailyBets() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [generatorStats, setGeneratorStats] = useState(null);
  const [executions, setExecutions] = useState([]);
  const [summary, setSummary] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [validating, setValidating] = useState(false);
  
  // ✅ NOVO: Estados para tracking de progresso em tempo real
  const [generationProgress, setGenerationProgress] = useState(null);
  const [showProgress, setShowProgress] = useState(false);
  const pollingIntervalRef = useRef(null);

  useEffect(() => {
    // Verificar se é admin
    if (!user?.is_staff && !user?.is_superuser) {
      navigate('/admin');
      return;
    }
    loadData();
    checkActiveGeneration(); // Verificar se há geração ativa ao montar
  }, [user, navigate]);
  
  // ✅ NOVO: Polling resiliente - retoma após refresh
  useEffect(() => {
    if (showProgress) {
      // Limpar interval existente se houver
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
      
      // Iniciar polling a cada 2 segundos
      pollingIntervalRef.current = setInterval(async () => {
        try {
          const response = await adminAPI.getGenerationProgress();
          const data = response.data;
          
          if (data.is_running) {
            setGenerationProgress(data);
            setGenerating(true);
          } else {
            // Geração concluída
            setShowProgress(false);
            setGenerating(false);
            setGenerationProgress(null);
            if (pollingIntervalRef.current) {
              clearInterval(pollingIntervalRef.current);
              pollingIntervalRef.current = null;
            }
            loadData(); // Recarregar dados
          }
        } catch (error) {
          console.error('Erro ao buscar progresso:', error);
        }
      }, 2000);
      
      return () => {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      };
    } else {
      // Limpar polling quando showProgress é false
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }
  }, [showProgress]);
  
  // ✅ NOVO: Verificar se há geração ativa ao montar/retornar à página
  const checkActiveGeneration = async () => {
    try {
      const response = await adminAPI.getGenerationProgress();
      const data = response.data;
      
      if (data.is_running) {
        setShowProgress(true);
        setGenerationProgress(data);
        setGenerating(true);
      }
    } catch (error) {
      console.error('Erro ao verificar geração ativa:', error);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsResponse, statusResponse] = await Promise.all([
        adminAPI.getGeneratorStats(),
        adminAPI.getExecutionStatus(10),
      ]);

      setGeneratorStats(statsResponse.data);
      setExecutions(statusResponse.data.executions);
      setSummary(statusResponse.data.summary);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
      alert('Erro ao carregar dados. Verifique o console para mais detalhes.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateNow = async () => {
    if (!confirm('Deseja executar a geração de Daily Bets agora?')) return;

    setGenerating(true);
    setShowProgress(true); // Iniciar visualização de progresso
    
    try {
      // Iniciar geração (não aguardar resposta - processo pode demorar)
      adminAPI.generateDailyBets().catch(error => {
        console.error('Erro ao gerar daily bets:', error);
        alert('❌ ' + (error.response?.data?.message || 'Erro ao gerar daily bets'));
        setGenerating(false);
        setShowProgress(false);
      });
      
      // Após 1 segundo, começar a monitorar progresso
      setTimeout(() => {
        checkActiveGeneration();
      }, 1000);
      
    } catch (error) {
      console.error('Erro ao iniciar geração:', error);
      alert('❌ Erro ao iniciar geração');
      setGenerating(false);
      setShowProgress(false);
    }
  };

  const handleValidateNow = async () => {
    if (!confirm('Deseja executar a validação de apostas agora?')) return;

    setValidating(true);
    try {
      const response = await adminAPI.validateDailyBets();
      alert(response.data.message || '✅ Validação executada com sucesso!');
      
      // Recarregar dados após 3 segundos
      setTimeout(() => {
        loadData();
      }, 3000);
    } catch (error) {
      console.error('Erro ao validar apostas:', error);
      alert('❌ ' + (error.response?.data?.message || 'Erro ao validar apostas'));
    } finally {
      setValidating(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      success: { icon: CheckCircle, color: 'green', label: 'Sucesso' },
      running: { icon: Clock, color: 'yellow', label: 'Em Execução' },
      failed: { icon: XCircle, color: 'red', label: 'Falhou' },
      pending: { icon: Clock, color: 'gray', label: 'Pendente' },
    };

    const badge = badges[status] || badges.pending;
    const Icon = badge.icon;

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-${badge.color}-100 dark:bg-${badge.color}-900/30 text-${badge.color}-700 dark:text-${badge.color}-300`}>
        <Icon className="w-3 h-3" />
        {badge.label}
      </span>
    );
  };

  const getCeleryStatusBadge = (status) => {
    const badges = {
      running: { color: 'green', label: 'Online', icon: CheckCircle },
      idle: { color: 'blue', label: 'Ocioso', icon: Activity },
      unknown: { color: 'gray', label: 'Desconhecido', icon: AlertCircle },
    };

    const badge = badges[status] || badges.unknown;
    const Icon = badge.icon;

    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-${badge.color}-100 dark:bg-${badge.color}-900/30 text-${badge.color}-700 dark:text-${badge.color}-300`}>
        <Icon className="w-3 h-3" />
        Celery: {badge.label}
      </span>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Nunca';
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pt-PT', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '-';
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}m ${secs}s`;
  };
  
  const getStageLabel = (stage) => {
    const labels = {
      'searching': '🔍 Buscando partidas...',
      'analyzing': '📊 Analisando partidas...',
      'creating': '🎫 Criando bilhetes...',
      'completed': '✅ Concluído',
      'starting': '⏳ Iniciando...',
    };
    return labels[stage] || stage;
  };

  if (loading) {
    return (
      <div className="page-container">
        <Header title="Daily Bets" subtitle="Gerenciamento" />
        <div className="page-content text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-primary-400"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Header title="Daily Bets" subtitle="Gerenciamento de Apostas Automáticas" />

      <div className="page-content">
        <button
          onClick={() => navigate('/admin')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-6 btn-ghost"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar
        </button>

        {/* Status do Sistema */}
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
              Status do Sistema
            </h3>
            {summary && getCeleryStatusBadge(summary.celery_status)}
          </div>

          {summary && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Última Geração</p>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {formatDate(summary.last_generation)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Última Validação</p>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {formatDate(summary.last_validation)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Apostas Pendentes</p>
                <p className="text-lg font-bold text-primary-600 dark:text-primary-400">
                  {summary.pending_bets_count}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Execuções</p>
                <p className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  {summary.total_executions}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* ✅ NOVO: Visualização Inline de Progresso em Tempo Real */}
        {showProgress && generationProgress && (
          <div className="card mb-6 border-2 border-primary-500 dark:border-primary-400">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <div className="relative">
                  <RefreshCw className="w-5 h-5 text-primary-600 dark:text-primary-400 animate-spin" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                  Geração em Andamento
                </h3>
              </div>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300">
                <Clock className="w-4 h-4" />
                {Math.floor(generationProgress.timing.elapsed_seconds / 60)}m {generationProgress.timing.elapsed_seconds % 60}s
              </span>
            </div>

            {/* Barra de Progresso */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {getStageLabel(generationProgress.current_stage)}
                </span>
                <span className="text-sm font-bold text-primary-600 dark:text-primary-400">
                  {generationProgress.progress.percentage}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all duration-500 ease-out relative overflow-hidden"
                  style={{ width: `${generationProgress.progress.percentage}%` }}
                >
                  <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                </div>
              </div>
            </div>

            {/* Estatísticas em Tempo Real */}
            <div className="grid grid-cols-3 gap-3 mb-4">
              <div className="card-flat bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
                <p className="text-xs text-blue-600 dark:text-blue-400 mb-1">Partidas Encontradas</p>
                <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                  {generationProgress.progress.matches_found}
                </p>
              </div>
              <div className="card-flat bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800">
                <p className="text-xs text-purple-600 dark:text-purple-400 mb-1">Processadas</p>
                <p className="text-2xl font-bold text-purple-700 dark:text-purple-300">
                  {generationProgress.progress.matches_processed}/{generationProgress.progress.matches_found}
                </p>
              </div>
              <div className="card-flat bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800">
                <p className="text-xs text-green-600 dark:text-green-400 mb-1">Apostas Criadas</p>
                <p className="text-2xl font-bold text-green-700 dark:text-green-300">
                  {generationProgress.progress.bets_created}
                </p>
              </div>
            </div>

            {/* Log de Progresso (últimas 5 mensagens) */}
            {generationProgress.progress_log && generationProgress.progress_log.length > 0 && (
              <div className="border-t border-gray-200 dark:border-gray-700 pt-3">
                <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-2">
                  📋 Log de Atividades
                </p>
                <div className="space-y-1 max-h-32 overflow-y-auto">
                  {generationProgress.progress_log.slice(-5).reverse().map((log, idx) => (
                    <div key={idx} className="text-xs text-gray-600 dark:text-gray-400 flex items-start gap-2">
                      <span className="text-gray-400 dark:text-gray-500 flex-shrink-0">
                        {new Date(log.timestamp).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </span>
                      <span className="flex-1">{log.message}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Estatísticas do Gerador */}
        {generatorStats && (
          <div className="card mb-6">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
              Estatísticas de Hoje
            </h3>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="card-flat">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Bilhetes Múltiplos</p>
                <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                  {generatorStats.today.multiple_count}
                </p>
              </div>
              <div className="card-flat">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Value Bets</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {generatorStats.today.value_count}
                </p>
              </div>
              <div className="card-flat">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Partidas Analisadas</p>
                <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
                  {generatorStats.today.matches_analyzed}
                </p>
              </div>
              <div className="card-flat">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">Status</p>
                <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                  {generatorStats.today.generated ? '✅ Gerado' : '❌ Não Gerado'}
                </p>
              </div>
            </div>

            {/* Performance */}
            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <h4 className="text-sm font-bold text-gray-900 dark:text-gray-100 mb-3">
                Performance (30 dias)
              </h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-gray-600 dark:text-gray-400">Win Rate Múltiplos</p>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    {generatorStats.performance.win_rate_multiple.toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 dark:text-gray-400">ROI Múltiplos</p>
                  <p className={`font-medium ${generatorStats.performance.roi_multiple >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                    {generatorStats.performance.roi_multiple > 0 ? '+' : ''}{generatorStats.performance.roi_multiple.toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 dark:text-gray-400">Win Rate Value</p>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    {generatorStats.performance.win_rate_value.toFixed(1)}%
                  </p>
                </div>
                <div>
                  <p className="text-gray-600 dark:text-gray-400">ROI Value</p>
                  <p className={`font-medium ${generatorStats.performance.roi_value >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                    {generatorStats.performance.roi_value > 0 ? '+' : ''}{generatorStats.performance.roi_value.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Ações Rápidas */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <button
            onClick={handleGenerateNow}
            disabled={generating}
            className="btn-primary flex items-center justify-center gap-2 py-4"
          >
            {generating ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Gerando...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Gerar Agora
              </>
            )}
          </button>

          <button
            onClick={handleValidateNow}
            disabled={validating}
            className="btn-secondary flex items-center justify-center gap-2 py-4"
          >
            {validating ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                Validando...
              </>
            ) : (
              <>
                <CheckCircle className="w-5 h-5" />
                Validar Agora
              </>
            )}
          </button>
        </div>

        {/* Histórico de Execuções */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">
              Últimas Execuções
            </h3>
            <button
              onClick={loadData}
              className="btn-ghost p-2"
              title="Atualizar"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-3">
            {executions.length === 0 ? (
              <p className="text-center text-gray-600 dark:text-gray-400 py-8">
                Nenhuma execução encontrada
              </p>
            ) : (
              executions.map((execution) => (
                <div
                  key={execution.id}
                  onClick={() => navigate(`/admin/execution/${execution.id}`)}
                  className="card-flat border border-gray-200 dark:border-gray-700 cursor-pointer hover:border-blue-500 dark:hover:border-blue-500 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-gray-100 text-sm">
                        {execution.task_name === 'generate_daily_bets'
                          ? '🎯 Geração Daily Bets'
                          : '✅ Validação Apostas'}
                      </p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {formatDate(execution.started_at)}
                      </p>
                    </div>
                    {getStatusBadge(execution.status)}
                  </div>

                  {execution.result_summary && (
                    <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
                      <div className="text-center">
                        <p className="text-xs text-gray-600 dark:text-gray-400">Partidas</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {execution.result_summary.matches_analyzed}
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-600 dark:text-gray-400">Múltiplos</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {execution.result_summary.multiple_count}
                        </p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-gray-600 dark:text-gray-400">Value</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {execution.result_summary.value_count}
                        </p>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-600 dark:text-gray-400">
                    <span>
                      Por: {execution.triggered_by_user || execution.triggered_by}
                    </span>
                    <span>
                      Duração: {formatDuration(execution.duration_seconds)}
                    </span>
                  </div>

                  {execution.error_message && (
                    <div className="mt-2 p-2 bg-red-50 dark:bg-red-900/20 rounded text-xs text-red-700 dark:text-red-300">
                      Erro: {execution.error_message}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
