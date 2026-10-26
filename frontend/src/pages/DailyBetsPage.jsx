import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dailyBetsAPI } from '../services/dailyBetsAPI';
import { useAuth } from '../context/AuthContext';
import { Target, Zap, TrendingUp, RefreshCw, ArrowLeft, CalendarDays, X, Crown, LockKeyhole, CheckCircle2, BarChart3 } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import MultipleTicketCard from '../components/MultipleTicketCard';
import ValueBetCard from '../components/ValueBetCard';
import AccuracyStats from '../components/AccuracyStats';
import EmptyState from '../components/EmptyState';
import { Skeleton } from '../components/Skeleton';
import SEOHead from '../components/SEO/SEOHead';
import { isUnsupportedAsianGoalMarket } from '../utils/marketUtils';

export default function DailyBetsPage() {
  const navigate = useNavigate();
  const { user, refreshProfile } = useAuth();
  const isAdmin = user?.is_staff || user?.is_superuser;
  const canAccessSelections = user?.is_premium_active || isAdmin;
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [multipleTickets, setMultipleTickets] = useState([]);
  const [valueBets, setValueBets] = useState([]);
  const [stats, setStats] = useState({});
  const [activeTab, setActiveTab] = useState('today'); // 'today', 'stats'
  const [error, setError] = useState(null);
  const [selectedDate, setSelectedDate] = useState('');
  const [displayedDate, setDisplayedDate] = useState('');

  // Data máxima permitida para o seletor (hoje, no fuso local)
  const now = new Date();
  const maxDate = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;

  useEffect(() => {
    if (canAccessSelections) {
      loadDailyBets();
    } else {
      setLoading(false);
      setMultipleTickets([]);
      setValueBets([]);
      setDisplayedDate('');
    }
    loadStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedDate, canAccessSelections]);

  useEffect(() => {
    if (!canAccessSelections) return undefined;

    let active = true;
    let checking = false;
    const verifyPremiumAccess = async () => {
      if (checking) return;
      checking = true;
      try {
        const currentUser = await refreshProfile();
        if (
          active &&
          currentUser &&
          !currentUser.is_premium_active &&
          !currentUser.is_staff &&
          !currentUser.is_superuser
        ) {
          setMultipleTickets([]);
          setValueBets([]);
          setDisplayedDate('');
          setError(null);
        }
      } finally {
        checking = false;
      }
    };

    window.addEventListener('focus', verifyPremiumAccess);
    const intervalId = window.setInterval(verifyPremiumAccess, 60_000);
    return () => {
      active = false;
      window.removeEventListener('focus', verifyPremiumAccess);
      window.clearInterval(intervalId);
    };
  }, [canAccessSelections, refreshProfile]);

  const loadDailyBets = async () => {
    if (!canAccessSelections) return;
    try {
      setLoading(true);
      setError(null);
      const response = await dailyBetsAPI.getToday(selectedDate || undefined);
      const data = response.data;
      
      setMultipleTickets((data.multiple_tickets || []).filter(
        (ticket) => !(ticket.selections || []).some(isUnsupportedAsianGoalMarket)
      ));
      setValueBets((data.value_bets || []).filter(
        (bet) => !(bet.selections || []).some(isUnsupportedAsianGoalMarket)
      ));
      setDisplayedDate(data.date || '');
    } catch (err) {
      console.error('Erro ao carregar seleções:', err);
      if (err.response?.status === 403) {
        setMultipleTickets([]);
        setValueBets([]);
        setDisplayedDate('');
        setError(null);
        await refreshProfile();
      } else {
        setError('Erro ao carregar seleções. Tente novamente.');
      }
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
    if (!canAccessSelections) return;
    setRefreshing(true);
    await loadDailyBets();
    await loadStats();
    setRefreshing(false);
  };

  const tabs = [
    { id: 'today', label: 'Seleções de Hoje', icon: Target },
    { id: 'stats', label: 'Performance', icon: TrendingUp }
  ];

  const totalBets = multipleTickets.length + valueBets.length;

  return (
    <div className="page-container">
      <SEOHead
        title="Seleções do Dia - PlacerCerto | Análise Estatística de Futebol"
        description="Análise estatística completa de todas as partidas do dia, com probabilidades calculadas por modelos matemáticos usando 109 variáveis. Seleções individuais e múltiplas com desempenho transparente e verificável."
        keywords="análise de futebol, seleções do dia, estatísticas de futebol, probabilidades, modelos matemáticos, placarcerto"
      />

      <Header showLogo={true} />

      <div className="page-content">
        {!canAccessSelections ? (
          <section className="overflow-hidden rounded-3xl border border-amber-200 bg-gradient-to-br from-white via-amber-50 to-orange-50 p-6 shadow-lg dark:border-amber-900/60 dark:from-gray-900 dark:via-gray-900 dark:to-amber-950/30 sm:p-8">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-400 to-orange-500 text-white shadow-lg shadow-amber-500/25">
              <LockKeyhole className="h-7 w-7" />
            </div>
            <span className="mt-5 inline-flex items-center gap-1.5 rounded-full bg-amber-100 px-3 py-1 text-xs font-bold uppercase tracking-wide text-amber-800 dark:bg-amber-900/40 dark:text-amber-300">
              <Crown className="h-3.5 w-3.5" />
              Exclusivo Premium
            </span>
            <h1 className="mt-3 text-2xl font-bold text-gray-900 dark:text-white sm:text-3xl">
              Seleções do Dia
            </h1>
            <p className="mt-2 max-w-md text-sm leading-6 text-gray-600 dark:text-gray-300">
              Tenha acesso às análises e seleções preparadas diariamente para ajudar a tomar decisões mais informadas sobre os jogos.
            </p>
            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <div className="rounded-2xl border border-amber-100 bg-white/80 p-4 dark:border-gray-700 dark:bg-gray-800/70">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300">
                  <Target className="h-5 w-5" />
                </div>
                <h2 className="mt-3 text-sm font-bold text-gray-900 dark:text-white">Múltiplos do dia</h2>
                <p className="mt-1 text-xs leading-5 text-gray-600 dark:text-gray-400">
                  Consulte bilhetes 3x, 5x e 7x com as seleções reunidas num só lugar.
                </p>
              </div>
              <div className="rounded-2xl border border-amber-100 bg-white/80 p-4 dark:border-gray-700 dark:bg-gray-800/70">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300">
                  <Zap className="h-5 w-5" />
                </div>
                <h2 className="mt-3 text-sm font-bold text-gray-900 dark:text-white">Análises de valor</h2>
                <p className="mt-1 text-xs leading-5 text-gray-600 dark:text-gray-400">
                  Veja seleções individuais acompanhadas por probabilidades, odds e valor esperado.
                </p>
              </div>
              <div className="rounded-2xl border border-amber-100 bg-white/80 p-4 dark:border-gray-700 dark:bg-gray-800/70">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
                  <BarChart3 className="h-5 w-5" />
                </div>
                <h2 className="mt-3 text-sm font-bold text-gray-900 dark:text-white">Desempenho transparente</h2>
                <p className="mt-1 text-xs leading-5 text-gray-600 dark:text-gray-400">
                  Acompanhe estatísticas, resultados e histórico para avaliar o desempenho ao longo do tempo.
                </p>
              </div>
              <div className="rounded-2xl border border-amber-100 bg-white/80 p-4 dark:border-gray-700 dark:bg-gray-800/70">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300">
                  <CheckCircle2 className="h-5 w-5" />
                </div>
                <h2 className="mt-3 text-sm font-bold text-gray-900 dark:text-white">Informação para decidir</h2>
                <p className="mt-1 text-xs leading-5 text-gray-600 dark:text-gray-400">
                  Consulte cada seleção e os dados associados antes de decidir se faz sentido para si.
                </p>
              </div>
            </div>
            <p className="mt-4 text-xs leading-5 text-gray-500 dark:text-gray-400">
              As análises são informativas e não garantem resultados. Aposte com responsabilidade.
            </p>
            <button
              type="button"
              onClick={() => navigate('/premium')}
              className="mt-7 inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-5 py-3 font-bold text-white shadow-lg shadow-amber-500/20 transition hover:from-amber-600 hover:to-orange-600 sm:w-auto"
            >
              <Crown className="h-5 w-5" />
              Conhecer planos Premium
            </button>
          </section>
        ) : (
          <>
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
                Seleções do Dia
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                {selectedDate
                  ? `Seleções geradas em ${displayedDate || selectedDate}`
                  : 'Análise completa de todas as partidas de hoje'}
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

        {/* Admin: seletor de data para bilhetes passados */}
        {isAdmin && (
          <div className="mb-6 flex items-center gap-3 flex-wrap">
            <label htmlFor="daily-bets-date" className="text-sm font-semibold text-gray-600 dark:text-gray-400">
              <CalendarDays className="w-4 h-4 inline mr-1 -mt-0.5" />
              Ver seleções de outra data:
            </label>
            <input
              id="daily-bets-date"
              type="date"
              max={maxDate}
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="px-4 py-2 rounded-xl text-sm font-medium bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border-2 border-gray-200 dark:border-gray-700 focus:border-primary-500 dark:focus:border-primary-500 focus:ring-4 focus:ring-primary-500/20 transition-all outline-none"
            />
            {selectedDate && (
              <button
                onClick={() => setSelectedDate('')}
                className="flex items-center gap-1 px-3 py-2 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                title="Voltar para hoje"
              >
                <X className="w-4 h-4" />
                Hoje
              </button>
            )}
          </div>
        )}

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
                title="Nenhuma Seleção Disponível"
                description={
                  selectedDate
                    ? `Nenhuma seleção foi gerada em ${displayedDate || selectedDate}.`
                    : 'As seleções de hoje ainda não foram geradas. Volte mais tarde!'
                }
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
                          Seleções Múltiplas
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
                          Análises de Valor
                        </h2>
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          ({valueBets.length})
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      Seleções com valor esperado (EV) positivo
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
          </>
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
