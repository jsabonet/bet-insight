import { Link } from 'react-router-dom';
import { useEffect } from 'react';
import { TrendingUp, Brain, Shield, Zap, Clock, Target, ArrowRight, Star, CheckCircle2 } from 'lucide-react';
import Logo from '../components/Logo';
import Footer from '../components/Footer';
import { useTheme } from '../context/ThemeContext';

export default function LandingPage() {
  const { theme } = useTheme();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const features = [
    {
      icon: Brain,
      title: 'Análise com IA',
      description: 'Inteligência artificial avançada processa estatísticas em tempo real para previsões precisas.'
    },
    {
      icon: TrendingUp,
      title: 'Estatísticas Detalhadas',
      description: 'Histórico completo, confrontos diretos e desempenho recente de cada equipa.'
    },
    {
      icon: Clock,
      title: 'Atualização em Tempo Real',
      description: 'Dados atualizados constantemente para você tomar decisões informadas.'
    },
    {
      icon: Shield,
      title: 'Seguro e Confiável',
      description: 'Seus dados protegidos e análises baseadas em fontes verificadas.'
    },
    {
      icon: Zap,
      title: 'Análise Rápida',
      description: 'Resultados instantâneos para você não perder nenhuma oportunidade.'
    },
    {
      icon: Target,
      title: 'Previsões Precisas',
      description: 'Algoritmos refinados que aprendem e melhoram continuamente.'
    }
  ];

  const stats = [
    { value: '10K+', label: 'Usuários Ativos' },
    { value: '50K+', label: 'Análises Geradas' },
    { value: '85%', label: 'Taxa de Precisão' },
    { value: '24/7', label: 'Disponibilidade' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Logo variant="default" size="md" showText={true} />
            <div className="flex items-center gap-4">
              <Link
                to="/login"
                className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 font-medium transition-colors"
              >
                Entrar
              </Link>
              <Link
                to="/register"
                className="px-6 py-2.5 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold shadow-lg shadow-primary-500/30 transition-all hover:scale-105"
              >
                Começar Grátis
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 dark:bg-primary-900/30 rounded-full text-primary-700 dark:text-primary-300 text-sm font-semibold">
              <Zap className="w-4 h-4" />
              Análise Inteligente de Futebol
            </div>
            
            <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white leading-tight">
              Previsões de Futebol
              <span className="block text-primary-600 dark:text-primary-400">
                Com Inteligência Artificial
              </span>
            </h1>
            
            <p className="text-xl text-gray-600 dark:text-gray-300 leading-relaxed">
              Tome decisões informadas com análises estatísticas avançadas, histórico de confrontos e previsões precisas baseadas em IA.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                to="/register"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold shadow-xl shadow-primary-500/30 transition-all hover:scale-105"
              >
                Começar Gratuitamente
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/about"
                className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-white border-2 border-gray-200 dark:border-gray-600 rounded-xl font-semibold transition-all"
              >
                Saiba Mais
              </Link>
            </div>

            <div className="flex items-center gap-6 pt-4">
              <div className="flex -space-x-3">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 border-2 border-white dark:border-gray-900 flex items-center justify-center text-white font-bold"
                  >
                    {i}
                  </div>
                ))}
              </div>
              <div>
                <div className="flex items-center gap-1 text-yellow-500">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Star key={i} className="w-4 h-4 fill-current" />
                  ))}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  Avaliado por <span className="font-semibold">10,000+</span> usuários
                </p>
              </div>
            </div>
          </div>

          <div className="relative lg:pl-12">
            <div className="relative bg-gradient-to-br from-primary-500 to-primary-700 rounded-3xl p-8 shadow-2xl">
              <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent rounded-3xl"></div>
              <Logo variant="default" size="2xl" showText={false} className="mx-auto" />
              <div className="mt-8 space-y-4">
                {['Análise de IA', 'Estatísticas em Tempo Real', 'Histórico Completo'].map((feature, i) => (
                  <div key={i} className="flex items-center gap-3 text-white">
                    <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
                    <span className="font-medium">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Floating Cards */}
            <div className="absolute -top-6 -right-6 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-4 animate-float">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">85%</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Precisão</p>
                </div>
              </div>
            </div>

            <div className="absolute -bottom-6 -left-6 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-4 animate-float" style={{ animationDelay: '0.5s' }}>
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center">
                  <Brain className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">IA</p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Avançada</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-white dark:bg-gray-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, i) => (
              <div key={i} className="text-center">
                <p className="text-4xl lg:text-5xl font-bold text-primary-600 dark:text-primary-400 mb-2">
                  {stat.value}
                </p>
                <p className="text-gray-600 dark:text-gray-400 font-medium">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl lg:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Recursos Poderosos
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Tudo que você precisa para fazer análises precisas e tomar decisões informadas
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, i) => (
            <div
              key={i}
              className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 transition-all hover:shadow-xl group"
            >
              <div className="w-14 h-14 bg-primary-100 dark:bg-primary-900/30 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <feature.icon className="w-7 h-7 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-br from-primary-600 to-primary-700 rounded-3xl p-12 lg:p-16 text-center shadow-2xl">
          <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
            Pronto Para Começar?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Junte-se a milhares de usuários que já estão fazendo análises inteligentes de futebol
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white hover:bg-gray-50 text-primary-600 rounded-xl font-semibold shadow-xl transition-all hover:scale-105"
            >
              Criar Conta Grátis
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-primary-500 hover:bg-primary-400 text-white border-2 border-white/20 rounded-xl font-semibold transition-all"
            >
              Já Tenho Conta
            </Link>
          </div>
        </div>
      </section>

      <Footer />

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        .animate-float {
          animation: float 3s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
