import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Check, Star, Zap, TrendingUp, Shield, Bell } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import Logo from '../components/Logo';

export default function PremiumPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [selectedPlan, setSelectedPlan] = useState('monthly');

  const plans = [
    {
      id: 'monthly',
      name: 'Mensal',
      price: '499',
      period: 'mês',
      description: 'Perfeito para começar',
    },
    {
      id: 'quarterly',
      name: 'Trimestral',
      price: '1299',
      period: '3 meses',
      description: 'Economize 13%',
      savings: 'Poupe 198 MZN',
    },
    {
      id: 'annual',
      name: 'Anual',
      price: '4799',
      period: 'ano',
      description: 'Melhor valor',
      savings: 'Poupe 1189 MZN',
      popular: true,
    },
  ];

  const features = [
    {
      icon: TrendingUp,
      title: 'Análises Ilimitadas',
      description: 'Até 100 análises por dia com IA avançada',
      free: '5 por dia',
      premium: '100 por dia',
    },
    {
      icon: Bell,
      title: 'Notificações SMS',
      description: 'Receba alertas de análises direto no seu telefone',
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

  const handleSubscribe = () => {
    // TODO: Implement M-Pesa payment integration
    alert('Funcionalidade de pagamento será implementada em breve!');
  };

  if (user?.is_premium) {
    return (
      <div className="page-container">
        <Header title="Premium" subtitle="Você já é premium!" />
        
        <div className="page-content">
          <div className="card text-center py-12">
            <div className="w-20 h-20 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Star className="w-10 h-10 text-yellow-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Você já é Premium! 🎉
            </h1>
            <p className="text-gray-600 mb-6">
              Aproveite todas as funcionalidades exclusivas
            </p>
            <button
              onClick={() => navigate('/')}
              className="btn-primary"
            >
              Ver Partidas
            </button>
          </div>
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
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`card cursor-pointer transition-all animate-slide-up ${
                selectedPlan === plan.id
                  ? 'ring-2 ring-primary-600 shadow-xl scale-[1.02]'
                  : 'hover:shadow-lg'
              } ${plan.popular ? 'border-2 border-primary-600' : ''}`}
              onClick={() => setSelectedPlan(plan.id)}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-primary-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Mais Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  {plan.name}
                </h3>
                <p className="text-sm text-gray-600 mb-4">{plan.description}</p>
                
                <div className="mb-2">
                  <span className="text-4xl font-bold text-gray-900">
                    {plan.price}
                  </span>
                  <span className="text-gray-600 ml-2">MZN</span>
                </div>
                
                <p className="text-sm text-gray-600">por {plan.period}</p>
                
                {plan.savings && (
                  <p className="text-sm text-green-600 font-medium mt-2">
                    {plan.savings}
                  </p>
                )}
              </div>

              <div className={`w-6 h-6 rounded-full border-2 mx-auto ${
                selectedPlan === plan.id
                  ? 'border-primary-600 bg-primary-600'
                  : 'border-gray-300'
              }`}>
                {selectedPlan === plan.id && (
                  <Check className="w-5 h-5 text-white" />
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Features Comparison */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Recursos Premium
          </h2>

          <div className="space-y-4">
            {features.map((feature, index) => (
              <div
                key={index}
                className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-xl transition-colors"
              >
                <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center flex-shrink-0">
                  <feature.icon className="w-5 h-5 text-primary-600" />
                </div>
                
                <div className="flex-1">
                  <h3 className="font-bold text-gray-900 text-sm mb-1">
                    {feature.title}
                  </h3>
                  <p className="text-xs text-gray-600">
                    {feature.description}
                  </p>
                </div>

                <div className="text-primary-600 font-semibold text-lg flex-shrink-0">
                  ✓
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="card bg-gradient-to-br from-primary-600 to-primary-700 text-white text-center">
          <h2 className="text-xl font-bold mb-2">
            Pronto para começar?
          </h2>
          <p className="text-primary-100 mb-6 text-sm">
            Faça upgrade agora e aproveite análises ilimitadas
          </p>
          
          <button
            onClick={handleSubscribe}
            className="bg-white text-primary-600 px-6 py-3 rounded-2xl font-semibold hover:bg-gray-100 transition-all inline-flex items-center gap-2 shadow-lg active:scale-95"
          >
            <Star className="w-5 h-5" />
            Assinar por {plans.find(p => p.id === selectedPlan)?.price} MZN
          </button>
          
          <p className="text-primary-100 text-sm mt-4">
            Pagamento via M-Pesa • Cancele quando quiser
          </p>
        </div>
      </div>

      <BottomNav />
    </div>
  );
}
