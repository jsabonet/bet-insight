import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dailyBetsAPI } from '../services/dailyBetsAPI';
import { Target, Zap, TrendingUp, RefreshCw, ArrowLeft, ChevronRight } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import MultipleTicketCard from '../components/MultipleTicketCard';
import ValueBetCard from '../components/ValueBetCard';
import AccuracyStats from '../components/AccuracyStats';
import EmptyState from '../components/EmptyState';
import { Skeleton } from '../components/Skeleton';
import SEOHead from '../components/SEO/SEOHead';

export default function DailyBetsPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [multipleTickets, setMultipleTickets] = useState([]);
  const [valueBets, setValueBets] = useState([]);
  const [stats, setStats] = useState({});
  const [activeTab, setActiveTab] = useState('today'); // 'today', 'stats'
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDailyBets();
    loadStats();
  }, []);

  const loadDailyBets = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await dailyBetsAPI.getToday();
      const data = response.data;
      
      setMultipleTickets(data.multiple_tickets || []);
      setValueBets(data.value_bets || []);
    } catch (err) {
      console.error('Erro ao carregar bilhetes:', err);
      setError('Erro ao carregar bilhetes. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await dailyBetsAPI.getPublicStats();
      setStats(response.data || {});
    } catch (err) {
      console.error('Erro ao carregar estatísticas:', err);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDailyBets();
    await loadStats();
    setRefreshing(false);
  };

  const tabs = [
    { id: 'today', label: 'Bilhetes de Hoje', icon: Target },
    { id: 'stats', label: 'Performance', icon: TrendingUp }
  ];

  const totalBets = multipleTickets.length + valueBets.length;

  return (
    <div className="page-container">
      <SEOHead
        title="Bilhetes Automáticos - PlacerCerto | Análise Estatística de Todas as Partidas"
        description="Bilhetes prontos gerados por modelos matemáticos com análise completa de todas as partidas do dia usando 109 variáveis estatísticas. Múltiplos 3x, 5x, 7x e Value Bets com Expected Value positivo. Performance transparente e verificável."
        keywords="bilhetes prontos, apostas automaticas, value bets, bilhetes multiplos, analise estatistica, modelos matematicos, placarcerto"
      />

      <Header showLogo={true} />

      <div className="page-content">
        {/* Header Simples */}
        <div className="mb-6">
          <button
            onClick={() => navigate('/home')}
            className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-sm font-medium">Voltar</span>
          </button>

          <div className="flex items-center justify-between mb-2">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">
                Bilhetes Automáticos
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Análise completa de todas as partidas de hoje
              </p>
            </div>
            
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="p-3 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-xl border border-gray-200 dark:border-gray-700 transition-colors disabled:opacity-50"
              title="Atualizar"
            >
              <RefreshCw className={`w-5 h-5 text-gray-600 dark:text-gray-400 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {/* Stats compactas */}
          {stats.last_7_days && (
            <div className="grid grid-cols-3 gap-3 mt-4">
              <div className="bg-white dark:bg-gray-800 rounded-xl p-3 border border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Total</p>
                <p className="text-xl font-bold text-gray-900 dark:text-gray-100">{totalBets}</p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl p-3 border border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Acertos (7d)</p>
                <p className="text-xl font-bold text-emerald-600 dark:text-emerald-400">{stats.last_7_days?.win_rate || '0%'}</p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-xl p-3 border border-gray-200 dark:border-gray-700">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">ROI (7d)</p>
                <p className="text-xl font-bold text-blue-600 dark:text-blue-400">{stats.last_7_days?.roi || '0%'}</p>
              </div>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-gray-200 dark:border-gray-700">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-3 font-medium whitespace-nowrap transition-all border-b-2 ${
                activeTab === tab.id
                  ? 'border-primary-600 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        {activeTab === 'today' && (
          <>
            {loading ? (
              <div className="space-y-4">
                <Skeleton className="h-64 rounded-2xl" />
                <Skeleton className="h-64 rounded-2xl" />
                <Skeleton className="h-64 rounded-2xl" />
              </div>
            ) : error ? (
              <EmptyState
                variant="error"
                title="Erro ao Carregar"
                description={error}
                action={
                  <button onClick={loadDailyBets} className="btn-primary">
                    Tentar Novamente
                  </button>
                }
              />
            ) : totalBets === 0 ? (
              <EmptyState
                variant="no-data"
                title="Nenhum Bilhete Disponível"
                description="Os bilhetes de hoje ainda não foram gerados. Volte mais tarde!"
                action={
                  <button onClick={handleRefresh} className="btn-primary">
                    Atualizar
                  </button>
                }
              />
            ) : (
              <div className="space-y-6">
                {/* Bilhetes Múltiplos */}
                {multipleTickets.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                          <Target className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                        </div>
                        <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                          Bilhetes Múltiplos
                        </h2>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          ({multipleTickets.length})
                        </span>
                      </div>
                    </div>
                    <div className="space-y-4">
                      {multipleTickets.map((ticket, index) => (
                        <MultipleTicketCard 
                          key={index} 
                          ticket={ticket}
                          onViewDetails={(t) => console.log('Ver detalhes:', t)}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Value Bets */}
                {valueBets.length > 0 && (
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg flex items-center justify-center">
                          <Zap className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                        </div>
                        <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                          Value Bets
                        </h2>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          ({valueBets.length})
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      Apostas com Expected Value (EV) positivo
                    </p>
                    <div className="space-y-4">
                      {valueBets.map((bet, index) => (
                        <ValueBetCard 
                          key={index} 
                          bet={bet}
                          onViewAnalysis={(selection) => {
                            if (selection.match_id) {
                              navigate(`/match/${selection.match_id}`);
                            }
                          }}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {activeTab === 'stats' && (
          <AccuracyStats stats={stats} />
        )}
      </div>

      <BottomNav />

      <style>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  );
}
