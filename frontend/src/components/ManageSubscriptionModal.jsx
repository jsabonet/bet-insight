import { useState, useEffect } from 'react';
import { X, Shield, Calendar, Zap, TrendingUp, Crown, Info } from 'lucide-react';
import api from '../services/api';
import Logo from './Logo';

export default function ManageSubscriptionModal({ user, isOpen, onClose, onSuccess }) {
  const [plans, setPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState('');
  const [durationDays, setDurationDays] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingPlans, setLoadingPlans] = useState(true);
  const [error, setError] = useState('');
  const [currentSubscription, setCurrentSubscription] = useState(null);

  useEffect(() => {
    if (isOpen && user) {
      loadPlans();
      loadCurrentSubscription();
    }
  }, [isOpen, user]);

  const loadPlans = async () => {
    try {
      const response = await api.get('/subscriptions/plans/');
      setPlans(response.data);
    } catch (err) {
      console.error('Erro ao carregar planos:', err);
    } finally {
      setLoadingPlans(false);
    }
  };

  const loadCurrentSubscription = async () => {
    try {
      // Tentar buscar assinatura atual do usuário
      const response = await api.get(`/subscriptions/my-subscription/`);
      setCurrentSubscription(response.data);
    } catch (err) {
      // Usuário pode não ter assinatura ativa
      setCurrentSubscription(null);
    }
  };

  const handleAssignPlan = async (e) => {
    e.preventDefault();
    
    if (!selectedPlan) {
      setError('Selecione um plano');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const payload = {
        user_id: user.id,
        plan_slug: selectedPlan,
      };

      if (durationDays) {
        payload.duration_days = parseInt(durationDays);
      }

      await api.post('/subscriptions/admin/assign-subscription/', payload);
      onSuccess(`Plano ${selectedPlan} atribuído com sucesso!`);
      onClose();
    } catch (err) {
      console.error('Erro ao atribuir plano:', err);
      setError(err.response?.data?.error || 'Erro ao atribuir plano');
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveSubscription = async () => {
    if (!window.confirm('Tem certeza que deseja remover a assinatura atual deste usuário?')) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      await api.post('/subscriptions/admin/remove-subscription/', {
        user_id: user.id
      });
      onSuccess('Assinatura removida com sucesso!');
      onClose();
    } catch (err) {
      console.error('Erro ao remover assinatura:', err);
      setError(err.response?.data?.error || 'Erro ao remover assinatura');
    } finally {
      setLoading(false);
    }
  };

  const getPlanIcon = (slug) => {
    switch (slug) {
      case 'freemium':
        return Zap;
      case 'teste':
        return Info;
      case 'starter':
        return TrendingUp;
      case 'pro':
      case 'vip':
        return Crown;
      default:
        return Shield;
    }
  };

  const getPlanColor = (color) => {
    const colors = {
      gray: 'bg-gray-100 dark:bg-gray-800 border-gray-300 dark:border-gray-600',
      green: 'bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700',
      blue: 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700',
      primary: 'bg-primary-50 dark:bg-primary-900/20 border-primary-300 dark:border-primary-700',
      yellow: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-300 dark:border-yellow-700',
    };
    return colors[color] || colors.gray;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Gerenciar Assinatura
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {user?.username} - {user?.email}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/50 dark:hover:bg-gray-700/50 rounded-full transition-all"
          >
            <X className="w-6 h-6 text-gray-500 dark:text-gray-400" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[70vh]">
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-700 dark:text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Current Subscription */}
          {currentSubscription && (
            <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-xl">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-bold text-green-900 dark:text-green-100 mb-1">
                    ✓ Assinatura Atual
                  </h3>
                  <p className="text-lg font-semibold text-green-700 dark:text-green-300">
                    {currentSubscription.plan_name || currentSubscription.plan_slug}
                  </p>
                  <p className="text-sm text-green-600 dark:text-green-400 mt-1">
                    Status: {currentSubscription.status === 'active' ? '✓ Ativa' : 
                             currentSubscription.status === 'pending' ? '⏳ Pendente' :
                             currentSubscription.status === 'expired' ? '❌ Expirada' : 
                             '🚫 Cancelada'}
                  </p>
                  {currentSubscription.end_date && (
                    <p className="text-sm text-green-600 dark:text-green-400">
                      Válida até: {new Date(currentSubscription.end_date).toLocaleDateString('pt-BR')}
                    </p>
                  )}
                </div>
                <button
                  onClick={handleRemoveSubscription}
                  disabled={loading}
                  className="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-xl text-sm font-medium hover:bg-red-200 dark:hover:bg-red-900/50 transition-all disabled:opacity-50"
                >
                  Remover
                </button>
              </div>
            </div>
          )}

          {/* Assign New Plan Form */}
          <form onSubmit={handleAssignPlan} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Atribuir Novo Plano
              </label>
              
              {loadingPlans ? (
                <div className="text-center py-8">
                  <Logo variant="thinking" size="md" showText={false} />
                  <p className="text-sm text-gray-500 mt-2">Carregando planos...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-3">
                  {plans.map((plan) => {
                    const Icon = getPlanIcon(plan.slug);
                    const isSelected = selectedPlan === plan.slug;
                    
                    return (
                      <button
                        key={plan.slug}
                        type="button"
                        onClick={() => setSelectedPlan(plan.slug)}
                        className={`p-4 border-2 rounded-xl text-left transition-all ${
                          isSelected
                            ? 'border-primary-500 dark:border-primary-400 bg-primary-50 dark:bg-primary-900/20 shadow-md'
                            : `border-gray-200 dark:border-gray-700 ${getPlanColor(plan.color)} hover:border-primary-300 dark:hover:border-primary-600`
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Icon className={`w-5 h-5 ${
                                isSelected ? 'text-primary-600 dark:text-primary-400' : 'text-gray-500 dark:text-gray-400'
                              }`} />
                              <h3 className="font-bold text-gray-900 dark:text-gray-100">
                                {plan.name}
                              </h3>
                              {plan.popular && (
                                <span className="px-2 py-0.5 bg-yellow-400 text-yellow-900 text-xs font-bold rounded-full">
                                  Popular
                                </span>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                              {plan.description}
                            </p>
                            <div className="flex items-center gap-4 text-sm">
                              <span className="font-bold text-primary-600 dark:text-primary-400">
                                {plan.price === 0 ? 'Grátis' : `${plan.price} MZN`}
                              </span>
                              {plan.duration_days && (
                                <span className="text-gray-600 dark:text-gray-400">
                                  • {plan.duration_days} dias
                                </span>
                              )}
                              <span className="text-gray-600 dark:text-gray-400">
                                • {plan.daily_analysis_limit} análises/dia
                              </span>
                            </div>
                          </div>
                          {isSelected && (
                            <div className="ml-2">
                              <div className="w-6 h-6 bg-primary-600 dark:bg-primary-500 rounded-full flex items-center justify-center">
                                <Shield className="w-4 h-4 text-white fill-current" />
                              </div>
                            </div>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Duration Override */}
            {selectedPlan && selectedPlan !== 'freemium' && (
              <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl">
                <label className="block text-sm font-medium text-blue-900 dark:text-blue-100 mb-2">
                  <Calendar className="w-4 h-4 inline mr-1" />
                  Duração Personalizada (opcional)
                </label>
                <input
                  type="number"
                  value={durationDays}
                  onChange={(e) => setDurationDays(e.target.value)}
                  placeholder="Ex: 30 (padrão do plano será usado)"
                  className="input-field"
                  min="1"
                />
                <p className="text-xs text-blue-700 dark:text-blue-300 mt-2">
                  💡 Deixe vazio para usar a duração padrão do plano. Use valores personalizados 
                  para casos especiais (ex: 7 dias de teste grátis).
                </p>
              </div>
            )}

            {/* Info Alert */}
            <div className="p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl">
              <p className="text-sm text-amber-800 dark:text-amber-200">
                ⚠️ <strong>Atenção:</strong> Atribuir um novo plano cancelará automaticamente 
                qualquer assinatura ativa anterior do usuário.
              </p>
            </div>

            {/* Buttons */}
            <div className="flex gap-3 pt-4">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 py-3 px-4 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-xl hover:bg-gray-200 dark:hover:bg-gray-600 transition-all"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading || !selectedPlan}
                className="flex-1 py-3 px-4 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-bold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all disabled:opacity-50"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <div className="w-5 h-5 mr-2">
                      <Logo variant="thinking" size="sm" showText={false} />
                    </div>
                    Atribuindo...
                  </span>
                ) : (
                  'Atribuir Plano'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
