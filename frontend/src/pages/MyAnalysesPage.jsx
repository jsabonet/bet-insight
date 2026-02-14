import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { analysisAPI } from '../services/api';
import api from '../services/api';
import { useStats } from '../context/StatsContext';
import { useAuth } from '../context/AuthContext';
import { Calendar, TrendingUp, Target, Star, Loader2, Search, X } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import EmptyState from '../components/EmptyState';
import { MatchListSkeleton } from '../components/Skeleton';
import AnalysisModalProgressive from '../components/AnalysisModalProgressive';
import SEOHead from '../components/SEO/SEOHead';

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
  
  // Estados de paginação
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [loadingMore, setLoadingMore] = useState(false);

  // Estado de pesquisa
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce da pesquisa (500ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Recarregar quando a pesquisa mudar
  useEffect(() => {
    if (debouncedSearch !== undefined) {
      setCurrentPage(1); // Resetar para página 1
      loadAnalyses(1);
    }
  }, [debouncedSearch]);

  useEffect(() => {
    window.scrollTo(0, 0);
    loadAnalyses();
    loadUserStats();
  }, []);

  useEffect(() => {
    // Atualizar métricas quando houver mudanças globais (ex: novas análises)
    loadUserStats();
  }, [refreshTrigger]);

  const loadAnalyses = async (page = 1) => {
    try {
      if (page === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }
      
      const response = await analysisAPI.getUserAnalyses(page, debouncedSearch);
      console.log('📊 Análises carregadas:', response.data);
      console.log('📊 Primeira análise (se existir):', response.data.results?.[0]);
      
      const analysesData = response.data.results || response.data || [];
      
      // Se for página 1, substitui. Senão, adiciona
      if (page === 1) {
        setAnalyses(analysesData);
      } else {
        setAnalyses(prev => [...prev, ...analysesData]);
      }
      
      // Atualizar informações de paginação
      setTotalCount(response.data.count || analysesData.length);
      setCurrentPage(page);
      
      // Calcular total de páginas (20 itens por página)
      const pageSize = 20;
      setTotalPages(Math.ceil((response.data.count || analysesData.length) / pageSize));
      
      // Calculate stats baseado no count total
      const total = response.data.count || analysesData.length;
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
      setLoadingMore(false);
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
          <MatchListSkeleton count={5} />
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <SEOHead
        title="Minhas Análises | PlacerCerto"
        description="Histórico das suas análises estatísticas de futebol. Acompanhe suas previsões, acertos e estatísticas detalhadas."
        keywords="minhas análises, histórico previsões, estatísticas pessoais"
        noindex={true}
      />
      
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

        {/* Barra de Pesquisa */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Pesquisar por time, liga ou data..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-12 py-3.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                aria-label="Limpar pesquisa"
              >
                <X className="w-5 h-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200" />
              </button>
            )}
          </div>
          {searchTerm && (
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {loading ? (
                <span className="inline-flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Pesquisando...
                </span>
              ) : totalCount === 0 ? (
                'Nenhuma análise encontrada'
              ) : (
                `${totalCount} ${totalCount === 1 ? 'análise encontrada' : 'análises encontradas'}`
              )}
            </p>
          )}
        </div>

        {/* Analyses List */}
        {!loading && analyses.length === 0 && !searchTerm ? (
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
        ) : !loading && analyses.length === 0 && searchTerm ? (
          <EmptyState
            variant="no-results"
            title="Nenhuma análise encontrada"
            description={`Não foram encontradas análises que correspondam a "${searchTerm}". Tente pesquisar por outro time, liga ou data.`}
            action={
              <button
                onClick={() => setSearchTerm('')}
                className="btn-secondary"
              >
                Limpar Pesquisa
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
                    <div className="flex items-center gap-2 mb-3 flex-wrap">
                      <span className="text-xs text-gray-600 dark:text-gray-400 font-medium bg-gray-100 dark:bg-gray-800/50 px-2 py-1 rounded">
                        {analysis.match.league.name}
                      </span>
                      {analysis.match.api_football_id && (
                        <span className="text-xs text-gray-500 dark:text-gray-500 font-mono bg-gray-50 dark:bg-gray-900/50 px-2 py-1 rounded border border-gray-200 dark:border-gray-700/50">
                          ID: {analysis.match.api_football_id}
                        </span>
                      )}
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
            
            {/* Paginação */}
            {totalPages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-2">
                <button
                  onClick={() => loadAnalyses(currentPage - 1)}
                  disabled={currentPage === 1 || loadingMore}
                  className="btn-secondary px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  ← Anterior
                </button>
                
                <div className="flex items-center gap-1">
                  {[...Array(totalPages)].map((_, idx) => {
                    const pageNum = idx + 1;
                    // Mostrar: primeira, última, atual, e adjacentes
                    const showPage = 
                      pageNum === 1 || 
                      pageNum === totalPages || 
                      Math.abs(pageNum - currentPage) <= 1;
                    
                    // Mostrar reticências
                    const showEllipsis = 
                      (pageNum === 2 && currentPage > 3) ||
                      (pageNum === totalPages - 1 && currentPage < totalPages - 2);
                    
                    if (showEllipsis) {
                      return <span key={pageNum} className="px-2 text-gray-500">...</span>;
                    }
                    
                    if (!showPage) return null;
                    
                    return (
                      <button
                        key={pageNum}
                        onClick={() => loadAnalyses(pageNum)}
                        disabled={loadingMore}
                        className={`min-w-[40px] h-10 rounded-lg font-medium transition-all ${
                          pageNum === currentPage
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                        } disabled:opacity-50`}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>
                
                <button
                  onClick={() => loadAnalyses(currentPage + 1)}
                  disabled={currentPage === totalPages || loadingMore}
                  className="btn-secondary px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Próxima →
                </button>
              </div>
            )}
            
            {loadingMore && (
              <div className="mt-4 text-center">
                <div className="inline-flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Carregando mais análises...
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <BottomNav />

      {/* Modal de Análise Progressivo */}
      {selectedAnalysis && (
        <AnalysisModalProgressive
          match={{
            id: selectedAnalysis.match.id,
            home_team: {
              ...selectedAnalysis.match.home_team,
              logo: selectedAnalysis.match.home_team.logo_url || selectedAnalysis.match.home_team.logo || '',
            },
            away_team: {
              ...selectedAnalysis.match.away_team,
              logo: selectedAnalysis.match.away_team.logo_url || selectedAnalysis.match.away_team.logo || '',
            },
            league: selectedAnalysis.match.league,
            match_date: selectedAnalysis.match.match_date,
          }}
          onClose={() => setSelectedAnalysis(null)}
          onAnalyze={async (strategy) => {
            // Retornar dados da análise salva formatados para o modal progressivo
            console.log('🔍 DEBUG MyAnalyses - selectedAnalysis:', selectedAnalysis);
            console.log('🔍 DEBUG MyAnalyses - analysis_data:', selectedAnalysis.analysis_data);
            
            // Probabilidades já vêm como 0-100 (porcentagem), precisam ficar como 0-1 (decimal)
            const consensus = {
              home_win: selectedAnalysis.home_probability / 100,
              draw: selectedAnalysis.draw_probability / 100,
              away_win: selectedAnalysis.away_probability / 100,
            };
            
            const response = {
              statistical_data: {
                consensus: consensus,
                confidence: {
                  level: selectedAnalysis.confidence,
                  score: selectedAnalysis.confidence / 5,
                  label: selectedAnalysis.confidence_display,
                },
                poisson: {
                  home_xg: selectedAnalysis.home_xg || 0,
                  away_xg: selectedAnalysis.away_xg || 0,
                },
                enriched_data: {}, // Não temos dados enriquecidos nas análises salvas
              },
              decision_data: {
                // Se analysis_data tem top_bets, usar. Senão, criar estrutura vazia
                top_bets: selectedAnalysis.analysis_data?.top_bets || [],
                recommendation: selectedAnalysis.analysis_data?.recommendation || {
                  market: selectedAnalysis.prediction,
                  outcome: selectedAnalysis.prediction_display,
                  probability: consensus[selectedAnalysis.prediction === 'home' ? 'home_win' : selectedAnalysis.prediction === 'away' ? 'away_win' : 'draw'],
                  confidence: selectedAnalysis.confidence,
                },
                risk: selectedAnalysis.analysis_data?.risk || 'medium',
              },
              ai_analysis: selectedAnalysis.reasoning || '',
            };
            
            console.log('🔍 DEBUG MyAnalyses - response sendo retornado:', response);
            return response;
          }}
        />
      )}
    </div>
  );
}
