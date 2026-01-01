import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Crown, TrendingUp } from 'lucide-react';
import api from '../services/api';
import Logo from './Logo';

export default function DailyLimitIndicator({ refreshTrigger }) {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log('🔔 DailyLimitIndicator useEffect disparado! refreshTrigger:', refreshTrigger);
    setLoading(true);
    loadStats();
  }, [refreshTrigger]); // Atualizar quando refreshTrigger mudar

  const loadStats = async () => {
    console.log('🔄 Iniciando loadStats...');
    try {
      const response = await api.get('/users/stats/');
      console.log('📊 Stats carregadas:', response.data);
      console.log('📊 Análises hoje:', response.data.analyses_count_today, 'de', response.data.daily_limit);
      setStats(response.data);
    } catch (error) {
      console.error('❌ Erro ao carregar stats:', error);
    } finally {
      setLoading(false);
      console.log('✅ Loading finalizado');
    }
  };

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center">
        <Logo variant="thinking" size="sm" showText={false} />
      </div>
    );
  }

  const { analyses_count_today, daily_limit, is_premium } = stats;
  const percentage = (analyses_count_today / daily_limit) * 100;
  const remaining = daily_limit - analyses_count_today;

  console.log('🎨 Renderizando DailyLimitIndicator:', { analyses_count_today, daily_limit, remaining });

  // Cor baseada na porcentagem usada
  const getColor = () => {
    if (percentage >= 90) return 'text-red-600 dark:text-red-400';
    if (percentage >= 70) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-green-600 dark:text-green-400';
  };

  return (
    <div className="flex items-center gap-2">
      {/* Badge Premium */}
      {is_premium && (
        <div className="flex items-center gap-1 px-2 py-1 bg-gradient-to-r from-yellow-400 to-yellow-500 text-yellow-900 text-xs font-bold rounded-full">
          <Crown className="w-3 h-3" />
          <span>Premium</span>
        </div>
      )}

      {/* Contador de Análises */}
      <div className="flex items-center gap-1.5 px-3 py-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full">
        <TrendingUp className={`w-4 h-4 ${getColor()}`} />
        <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
          {analyses_count_today}/{daily_limit}
        </span>
      </div>

      {/* Tooltip on hover */}
      <div className="hidden sm:block">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {remaining > 0 ? `${remaining} restantes hoje` : 'Limite atingido'}
        </p>
      </div>
    </div>
  );
}
