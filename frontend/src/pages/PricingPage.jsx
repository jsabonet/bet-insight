import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Check, Crown, Zap, TrendingUp, ArrowLeft } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import Logo from '../components/Logo';
import CheckoutModal from '../components/CheckoutModal';
import api from '../services/api';

export default function PricingPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showCheckout, setShowCheckout] = useState(false);
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [userStats, setUserStats] = useState(null);

  useEffect(() => {
    loadPlans();
    loadCurrentSubscription();
  }, []);

  useEffect(() => {
    if (user) loadUserStats();
  }, [user]);

  const loadPlans = async () => {
    try {
      const response = await api.get('/subscriptions/plans/');
      setPlans(response.data);
    } catch (error) {
      console.error('Erro ao carregar planos:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCurrentSubscription = async () => {
    if (!user) return;
    
    try {
      const response = await api.get('/subscriptions/my-subscription/');
      setCurrentSubscription(response.data);
    } catch (error) {
      console.error('Erro ao carregar assinatura:', error);
    }
  };

  const loadUserStats = async () => {
    if (!user) return;
    try {
      const res = await api.get('/users/stats/');
      setUserStats(res.data);
    } catch (err) {
      console.error('Erro ao carregar estatísticas do usuário:', err);
    }
  };

  const handleSelectPlan = (plan) => {
    if (!user) {
      navigate('/login', { state: { from: '/pricing' } });
      return;
    }

    if (plan.slug === 'freemium') {
      return; // Não faz nada, já é o plano padrão
    }

    setSelectedPlan(plan);
    setShowCheckout(true);
  };

  const getPlanIcon = (slug) => {
    switch (slug) {
      case 'freemium':
        return Zap;
      case 'monthly':
        return TrendingUp;
      case 'quarterly':
        return Crown;
      case 'yearly':
        return Crown;
      default:
        return Check;
    }
  };

  const isCurrentPlan = (planSlug) => {
    return currentSubscription?.plan_slug === planSlug;
  };

  if (loading) {
    return (
      <div className="page-container">
        <Header title="Planos" />
        <div className="page-content flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="mb-4">
              <Logo variant="thinking" size="lg" showText={false} />
            </div>
            <p className="text-gray-600 dark:text-gray-400">Carregando planos...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Header title="Escolha seu Plano" subtitle="Análises ilimitadas com IA" />
      
      <div className="page-content pb-24">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100 mb-6 btn-ghost"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar
        </button>

        {/* Info Banner */}
        <div className="card mb-6 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 border-primary-200 dark:border-primary-800">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center">
              <Crown className="w-6 h-6 text-primary-600 dark:text-primary-400" />
            </div>
            <div className="flex-1">
              <h3 className="font-bold text-gray-900 dark:text-gray-100">
                Mais análises, mais lucro!
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Análises ilimitadas com inteligência artificial avançada
              </p>
            </div>
          </div>
        </div>

        {/* Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          {plans.map((plan, index) => {
            const Icon = getPlanIcon(plan.slug);
            const isCurrent = isCurrentPlan(plan.slug);
            const isPremium = plan.price > 0;
            const isPopular = plan.popular;

            return (
              <div
                key={plan.slug}
                className={`relative bg-white dark:bg-gray-800 rounded-2xl border-2 transition-all hover:shadow-xl animate-slide-up ${
                  isPopular 
                    ? 'border-yellow-400 dark:border-yellow-500 shadow-lg' 
                    : 'border-gray-200 dark:border-gray-700'
                }`}
                style={{ animationDelay: `${index * 100}ms` }}
              >
                {/* Popular Badge */}
                {isPopular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gradient-to-r from-yellow-400 to-yellow-500 text-yellow-900 px-4 py-1 text-xs font-bold rounded-full shadow-md">
                    ⭐ MAIS POPULAR
                  </div>
                )}

                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      plan.slug === 'freemium' 
                        ? 'bg-gray-100 dark:bg-gray-700'
                        : plan.slug === 'monthly'
                        ? 'bg-primary-100 dark:bg-primary-900/30'
                        : plan.slug === 'quarterly'
                        ? 'bg-yellow-100 dark:bg-yellow-900/30'
                        : 'bg-emerald-100 dark:bg-emerald-900/30'
                    }`}>
                      <Icon className={`w-6 h-6 ${
                        plan.slug === 'freemium'
                          ? 'text-gray-600 dark:text-gray-400'
                          : plan.slug === 'monthly'
                          ? 'text-primary-600 dark:text-primary-400'
                          : plan.slug === 'quarterly'
                          ? 'text-yellow-600 dark:text-yellow-400'
                          : 'text-emerald-600 dark:text-emerald-400'
                      }`} />
                    </div>

                    {isCurrent && (
                      <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-semibold rounded-full">
                        Ativo
                      </span>
                    )}
                  </div>

                  {/* Plan Name */}
                  <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    {plan.name}
                  </h3>

                  {/* Price */}
                  <div className="mb-4">
                    <div className="flex items-baseline gap-1">
                      {plan.price === 0 ? (
                        <span className="text-4xl font-bold text-gray-900 dark:text-gray-100">
                          Grátis
                        </span>
                      ) : (
                        <>
                          <span className="text-4xl font-bold text-gray-900 dark:text-gray-100">
                            {plan.price.toLocaleString()}
                          </span>
                          <span className="text-lg text-gray-600 dark:text-gray-400">MZN</span>
                        </>
                      )}
                    </div>
                    {plan.duration_days && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        por {plan.duration_days} dias
                      </p>
                    )}
                  </div>

                  {/* Daily limit */}
                  <div className="mb-3">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Limite diário: <span className="font-semibold text-gray-900 dark:text-gray-100">{plan.daily_analysis_limit} análises</span>
                    </p>
                    {isCurrent && currentSubscription && currentSubscription.end_date && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Expira em: {new Date(currentSubscription.end_date).toLocaleString()} ({Math.max(0, Math.ceil((new Date(currentSubscription.end_date) - new Date()) / (1000*60*60*24)))} dias)
                      </p>
                    )}
                    {isCurrent && userStats && (
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        Análises restantes hoje: <span className="font-semibold">{userStats.remaining_analyses}</span>
                      </p>
                    )}
                  </div>

                  {/* Savings Badge */}
                  {plan.savings && (
                    <div className="mb-4">
                      <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-sm font-semibold rounded-full">
                        💰 Economize {plan.savings} MZN
                      </span>
                    </div>
                  )}

                  {/* Description */}
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
                    {plan.description}
                  </p>

                  {/* CTA Button */}
                  <button
                    onClick={() => handleSelectPlan(plan)}
                    disabled={isCurrent || plan.slug === 'freemium'}
                    className={`w-full py-3 rounded-xl font-semibold transition-all mb-6 ${
                      isCurrent
                        ? 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                        : plan.slug === 'freemium'
                        ? 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                        : isPopular
                        ? 'bg-gradient-to-r from-yellow-400 to-yellow-500 text-yellow-900 hover:from-yellow-500 hover:to-yellow-600 shadow-md hover:shadow-lg'
                        : 'bg-primary-600 dark:bg-primary-500 text-white hover:bg-primary-700 dark:hover:bg-primary-600'
                    }`}
                  >
                    {isCurrent 
                      ? '✓ Plano Atual' 
                      : plan.slug === 'freemium' 
                      ? 'Plano Padrão' 
                      : 'Assinar Agora'
                    }
                  </button>

                  {/* Features */}
                  <div className="space-y-3 pt-6 border-t border-gray-200 dark:border-gray-700">
                    <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                      Inclui:
                    </p>
                    {plan.features.map((feature, idx) => (
                      <div key={idx} className="flex items-start gap-2">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700 dark:text-gray-300">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* FAQ */}
        <div className="mt-8 card">
          <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">
            Perguntas Frequentes
          </h3>
          <div className="space-y-3 text-sm">
            <div>
              <p className="font-semibold text-gray-900 dark:text-gray-100">Como funciona o pagamento?</p>
              <p className="text-gray-600 dark:text-gray-400">Pagamento via M-Pesa ou e-Mola. Você recebe uma notificação no celular para confirmar.</p>
            </div>
            <div>
              <p className="font-semibold text-gray-900 dark:text-gray-100">Posso cancelar a qualquer momento?</p>
              <p className="text-gray-600 dark:text-gray-400">Sim! Você pode cancelar sua assinatura a qualquer momento no seu perfil.</p>
            </div>
            <div>
              <p className="font-semibold text-gray-900 dark:text-gray-100">O que acontece quando expira?</p>
              <p className="text-gray-600 dark:text-gray-400">Você volta para o plano gratuito com 5 análises por dia.</p>
            </div>
          </div>
        </div>
      </div>

      <BottomNav />

      {/* Checkout Modal */}
      {showCheckout && selectedPlan && (
        <CheckoutModal
          plan={selectedPlan}
          onClose={() => {
            setShowCheckout(false);
            setSelectedPlan(null);
          }}
          onSuccess={() => {
            setShowCheckout(false);
            loadCurrentSubscription();
            if (user) loadUserStats();
          }}
        />
      )}
    </div>
  );
}
