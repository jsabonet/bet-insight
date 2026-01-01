import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useStats } from '../context/StatsContext';
import { Check, Star, Zap, TrendingUp, Shield, Bell } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import Logo from '../components/Logo';
import CheckoutModal from '../components/CheckoutModal';
import api from '../services/api';

export default function PremiumPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { refreshTrigger } = useStats();
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
    // Atualizar status premium quando houver mudanças globais (análises, etc.)
    loadCurrentSubscription();
    loadUserStats();
  }, [refreshTrigger]);

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
      const response = await api.get('/users/stats/');
      setUserStats(response.data);
    } catch (error) {
      console.error('Erro ao carregar estatísticas do usuário:', error);
    }
  };

  const handleSelectPlan = (plan) => {
    if (!user) {
      navigate('/login', { state: { from: '/premium' } });
      return;
    }
    
    if (plan.slug === 'freemium') {
      return; // Freemium não precisa pagamento
    }
    
    setSelectedPlan(plan);
    setShowCheckout(true);
  };

  const isCurrentPlan = (planSlug) => {
    return currentSubscription?.plan_slug === planSlug;
  };

  // Detalhes do plano atual (nome amigável e limite diário)
  const currentPlanName = currentSubscription?.plan_slug
    ? (plans.find(p => p.slug === currentSubscription.plan_slug)?.name || currentSubscription.plan_slug)
    : null;
  const currentPlanObj = currentSubscription?.plan_slug
    ? plans.find(p => p.slug === currentSubscription.plan_slug)
    : null;
  const currentDailyLimit = currentPlanObj?.daily_analysis_limit ?? userStats?.daily_limit;

  // Determinar premium ativo com base na assinatura
  const premiumActive = !!(
    currentSubscription &&
    currentSubscription.status === 'active' &&
    currentSubscription.plan_slug && currentSubscription.plan_slug !== 'freemium' &&
    (!currentSubscription.end_date || new Date(currentSubscription.end_date) > new Date())
  );

  const features = [
    {
      icon: TrendingUp,
      title: 'Análises Diárias',
      description: 'Análises de IA para suas partidas favoritas',
      free: '5 por dia',
      premium: 'Até 150 por dia',
    },
    {
      icon: Bell,
      title: 'Notificações',
      description: 'Receba alertas de análises direto no app',
      free: false,
      premium: true,
    },
    {
      icon: Zap,
      title: 'Análises Prioritárias',
      description: 'Processamento mais rápido das suas análises',
      free: false,
      premium: true,
    },
    {
      icon: Shield,
      title: 'Histórico Completo',
      description: 'Acesso ilimitado ao histórico de análises',
      free: '7 dias',
      premium: 'Ilimitado',
    },
    {
      icon: Star,
      title: 'Suporte Premium',
      description: 'Atendimento prioritário via WhatsApp',
      free: false,
      premium: true,
    },
  ];



  if (premiumActive) {
    return (
      <div className="page-container">
        <Header title="Premium" subtitle="Você já é premium!" />
        
        <div className="page-content">
          <div className="card text-center py-12">
            <div className="w-20 h-20 bg-yellow-100 dark:bg-yellow-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
              <Star className="w-10 h-10 text-yellow-600 dark:text-yellow-400 fill-yellow-600 dark:fill-yellow-400" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
              Você já é Premium! 🎉
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Aproveite todas as funcionalidades exclusivas
            </p>
            {currentPlanName && (
              <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
                Plano atual: <span className="font-semibold">{currentPlanName}</span>
              </p>
            )}
            {currentDailyLimit !== undefined && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Limite diário: <span className="font-semibold">{currentDailyLimit}</span> análises
              </p>
            )}
            {currentSubscription?.end_date && (
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Expira em: {new Date(currentSubscription.end_date).toLocaleString()}
              </p>
            )}
            <div className="mt-6">
              <button
                onClick={() => navigate('/')}
                className="btn-primary"
              >
                Ver Partidas
              </button>
            </div>
          </div>
        </div>

        <BottomNav />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="page-container">
        <Header title="Planos" subtitle="Carregando planos..." />
        <div className="page-content flex items-center justify-center">
          <Logo variant="thinking" size="lg" showText={false} />
        </div>
        <BottomNav />
      </div>
    );
  }

  return (
    <div className="page-container">
      <Header title="Seja Premium" subtitle="Análises ilimitadas e recursos exclusivos" />

      <div className="page-content">
        {/* Premium Mascot */}
        <div className="flex justify-center mb-6 animate-slide-up">
          <Logo variant="premium" size="xl" showText={false} />
        </div>

        {/* Plans */}
        <div className="grid grid-cols-1 gap-4 mb-8">
          {plans.map((plan) => {
            const isCurrent = isCurrentPlan(plan.slug);
            
            return (
              <div
                key={plan.slug}
                className={`card relative transition-all animate-slide-up ${
                  isCurrent ? 'ring-2 ring-green-500 dark:ring-green-400' : 'hover:shadow-lg dark:hover:shadow-black/30'
                } ${plan.popular ? 'border-2 border-primary-600 dark:border-primary-500' : ''}`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-primary-600 dark:bg-primary-500 text-white px-4 py-1 rounded-full text-sm font-semibold shadow-lg">
                      ⭐ Mais Popular
                    </span>
                  </div>
                )}

                {plan.trial_days && (
                  <div className="absolute -top-4 right-4">
                    <span className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-lg">
                      🎁 {plan.trial_days} dias grátis
                    </span>
                  </div>
                )}

                {isCurrent && (
                  <div className="absolute -top-4 right-4">
                    <span className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-semibold shadow-lg">
                      ✓ Plano Atual
                    </span>
                  </div>
                )}

                <div className="text-center mb-6">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    {plan.name}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{plan.description}</p>
                  
                  <div className="mb-2">
                    {plan.price === 0 ? (
                      <span className="text-4xl font-bold text-gray-900 dark:text-gray-100">
                        Grátis
                      </span>
                    ) : (
                      <>
                        <span className="text-4xl font-bold text-gray-900 dark:text-gray-100">
                          {plan.price}
                        </span>
                        <span className="text-gray-600 dark:text-gray-400 ml-2">MZN</span>
                      </>
                    )}
                  </div>
                  
                  {plan.duration_days && (
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      por {plan.duration_days} dias
                    </p>
                  )}
                  
                  {plan.savings && (
                    <p className="text-sm text-green-600 dark:text-green-400 font-medium mt-2">
                      💰 Economize {plan.savings} MZN
                    </p>
                  )}
                </div>

                {/* Features List */}
                <div className="mb-6 px-4">
                  <div className="space-y-2">
                    {plan.features && plan.features.map((feature, idx) => (
                      <div key={idx} className="flex items-start gap-2 text-left">
                        <Check className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                        <span className="text-sm text-gray-700 dark:text-gray-300">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Action Button */}
                <button
                  onClick={() => handleSelectPlan(plan)}
                  disabled={isCurrent}
                  className={`w-full py-3 rounded-2xl font-semibold transition-all ${
                    isCurrent
                      ? 'bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                      : plan.slug === 'freemium'
                      ? 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 cursor-default'
                      : plan.popular
                      ? 'bg-primary-600 dark:bg-primary-500 text-white hover:bg-primary-700 dark:hover:bg-primary-600 active:scale-95'
                      : 'bg-gray-900 dark:bg-gray-700 text-white hover:bg-gray-800 dark:hover:bg-gray-600 active:scale-95'
                  }`}
                >
                  {isCurrent ? '✓ Plano Atual' : plan.slug === 'freemium' ? 'Plano Padrão' : 'Assinar Agora'}
                </button>
              </div>
            );
          })}
        </div>

        {/* Features Comparison */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            Recursos Premium
          </h2>

          <div className="space-y-4">
            {features.map((feature, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-xl transition-colors"
              >
                <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center flex-shrink-0">
                  <feature.icon className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                </div>
                
                <div className="flex-1">
                  <h3 className="font-bold text-gray-900 dark:text-gray-100 text-sm mb-1">
                    {feature.title}
                  </h3>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {feature.description}
                  </p>
                </div>

                <div className="text-primary-600 dark:text-primary-400 font-semibold text-lg flex-shrink-0">
                  ✓
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Checkout Modal */}
      {showCheckout && selectedPlan && (
        <CheckoutModal
          plan={selectedPlan}
          onClose={() => {
            setShowCheckout(false);
          }}
        />
      )}

      <BottomNav />
    </div>
  );
}
