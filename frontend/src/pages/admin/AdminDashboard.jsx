import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { 
  Users, 
  TrendingUp, 
  Shield, 
  Activity,
  Calendar,
  DollarSign,
  ArrowLeft,
  BarChart3
} from 'lucide-react';
import Header from '../../components/Header';
import BottomNav from '../../components/BottomNav';

export default function AdminDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalUsers: 0,
    premiumUsers: 0,
    totalAnalyses: 0,
    todayAnalyses: 0,
    activeMatches: 0,
    revenue: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Verificar se é admin
    if (!user?.is_staff && !user?.is_superuser) {
      navigate('/');
      return;
    }
    loadStats();
  }, [user, navigate]);

  const loadStats = async () => {
    try {
      // TODO: Implementar chamada à API de estatísticas admin
      // Simulando dados por enquanto
      setStats({
        totalUsers: 156,
        premiumUsers: 23,
        totalAnalyses: 1847,
        todayAnalyses: 89,
        activeMatches: 12,
        revenue: 11477,
      });
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    {
      title: 'Total de Usuários',
      value: stats.totalUsers,
      icon: Users,
      color: 'primary',
      bgLight: 'bg-primary-100',
      bgDark: 'dark:bg-primary-900/30',
      textColor: 'text-primary-600 dark:text-primary-400',
    },
    {
      title: 'Usuários Premium',
      value: stats.premiumUsers,
      icon: Shield,
      color: 'yellow',
      bgLight: 'bg-yellow-100',
      bgDark: 'dark:bg-yellow-900/30',
      textColor: 'text-yellow-600 dark:text-yellow-400',
    },
    {
      title: 'Análises Hoje',
      value: stats.todayAnalyses,
      icon: Activity,
      color: 'blue',
      bgLight: 'bg-blue-100',
      bgDark: 'dark:bg-blue-900/30',
      textColor: 'text-blue-600 dark:text-blue-400',
    },
    {
      title: 'Total Análises',
      value: stats.totalAnalyses,
      icon: TrendingUp,
      color: 'green',
      bgLight: 'bg-green-100',
      bgDark: 'dark:bg-green-900/30',
      textColor: 'text-green-600 dark:text-green-400',
    },
    {
      title: 'Partidas Ativas',
      value: stats.activeMatches,
      icon: Calendar,
      color: 'purple',
      bgLight: 'bg-purple-100',
      bgDark: 'dark:bg-purple-900/30',
      textColor: 'text-purple-600 dark:text-purple-400',
    },
    {
      title: 'Receita (MZN)',
      value: `${stats.revenue.toLocaleString()}`,
      icon: DollarSign,
      color: 'emerald',
      bgLight: 'bg-emerald-100',
      bgDark: 'dark:bg-emerald-900/30',
      textColor: 'text-emerald-600 dark:text-emerald-400',
    },
  ];

  const adminActions = [
    {
      title: 'Gerenciar Usuários',
      description: 'Visualizar, editar e gerenciar usuários',
      icon: Users,
      path: '/admin/users',
      color: 'primary',
    },
    {
      title: 'Partidas',
      description: 'Gerenciar partidas e resultados',
      icon: Calendar,
      path: '/admin/matches',
      color: 'blue',
    },
    {
      title: 'Análises',
      description: 'Histórico e estatísticas de análises',
      icon: BarChart3,
      path: '/admin/analyses',
      color: 'green',
    },
  ];

  if (loading) {
    return (
      <div className="page-container">
        <Header title="Admin" />
        <div className="page-content text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-primary-400"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Header title="Administração" subtitle="Painel de Controle" />
      
      <div className="page-content">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-6 btn-ghost"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar
        </button>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {statCards.map((stat, index) => (
            <div
              key={index}
              className="card-flat animate-slide-up"
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <div className={`w-10 h-10 ${stat.bgLight} ${stat.bgDark} rounded-xl flex items-center justify-center mb-3`}>
                <stat.icon className={`w-5 h-5 ${stat.textColor}`} />
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {stat.value}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                {stat.title}
              </p>
            </div>
          ))}
        </div>

        {/* Admin Actions */}
        <div className="space-y-3 mb-6">
          <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-4">
            Ações Rápidas
          </h3>
          {adminActions.map((action, index) => (
            <button
              key={index}
              onClick={() => navigate(action.path)}
              className="w-full card hover:scale-[1.02] active:scale-95 transition-all text-left"
            >
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 bg-${action.color}-100 dark:bg-${action.color}-900/30 rounded-xl flex items-center justify-center`}>
                  <action.icon className={`w-6 h-6 text-${action.color}-600 dark:text-${action.color}-400`} />
                </div>
                <div className="flex-1">
                  <h4 className="font-bold text-gray-900 dark:text-gray-100">
                    {action.title}
                  </h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {action.description}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
