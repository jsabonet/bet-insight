import { Link } from 'react-router-dom';
import { useEffect } from 'react';
import { Target, Users, Zap, Brain, TrendingUp, Shield, Heart, Mail, CheckCircle2 } from 'lucide-react';
import Logo from '../components/Logo';
import Footer from '../components/Footer';

export default function AboutPage() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  const values = [
    {
      icon: Target,
      title: 'Precisão',
      description: 'Análises baseadas em dados reais e algoritmos refinados para máxima precisão.'
    },
    {
      icon: Shield,
      title: 'Transparência',
      description: 'Metodologias claras e informações verificáveis em todas as análises.'
    },
    {
      icon: Heart,
      title: 'Paixão pelo Futebol',
      description: 'Desenvolvido por entusiastas do futebol para entusiastas do futebol.'
    },
    {
      icon: Users,
      title: 'Comunidade',
      description: 'Construindo uma comunidade de fãs informados e apaixonados.'
    }
  ];

  const team = [
    {
      name: 'Equipa de Desenvolvimento',
      role: 'Tecnologia & IA',
      description: 'Especialistas em machine learning e análise de dados desportivos.'
    },
    {
      name: 'Analistas Desportivos',
      role: 'Análise Técnica',
      description: 'Profissionais com anos de experiência em análise de futebol.'
    },
    {
      name: 'Equipa de Suporte',
      role: 'Atendimento',
      description: 'Dedicados a fornecer a melhor experiência aos nossos usuários.'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link to="/">
              <Logo variant="default" size="md" showText={true} />
            </Link>
            <Link
              to="/"
              className="text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 font-medium transition-colors"
            >
              Voltar
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl lg:text-6xl font-bold mb-6">
            Sobre o PlacarCerto
          </h1>
          <p className="text-xl text-primary-100 max-w-3xl mx-auto">
            Transformamos dados complexos de futebol em insights claros e precisos usando inteligência artificial avançada
          </p>
        </div>
      </section>

      {/* Mission */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 dark:bg-primary-900/30 rounded-full text-primary-700 dark:text-primary-300 text-sm font-semibold mb-6">
              <Target className="w-4 h-4" />
              Nossa Missão
            </div>
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-6">
              Democratizar a Análise de Futebol
            </h2>
            <div className="space-y-4 text-gray-700 dark:text-gray-300 text-lg">
              <p>
                O PlacarCerto nasceu da paixão pelo futebol e da visão de tornar análises estatísticas avançadas acessíveis a todos os fãs do desporto.
              </p>
              <p>
                Acreditamos que informação de qualidade não deve ser privilégio de poucos. Por isso, desenvolvemos uma plataforma que combina dados em tempo real, histórico completo de confrontos e inteligência artificial para fornecer análises precisas e compreensíveis.
              </p>
              <p>
                Nossa missão é empoderar fãs de futebol com informações confiáveis, ajudando-os a entender melhor o jogo que amam através de estatísticas claras e previsões baseadas em dados reais.
              </p>
            </div>
          </div>
          <div className="relative">
            <div className="bg-gradient-to-br from-primary-500 to-primary-700 rounded-3xl p-12 shadow-2xl">
              <Logo variant="default" size="2xl" showText={false} className="mx-auto mb-8" />
              <div className="grid grid-cols-2 gap-6">
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center">
                  <p className="text-4xl font-bold text-white mb-2">10K+</p>
                  <p className="text-primary-100">Usuários</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center">
                  <p className="text-4xl font-bold text-white mb-2">50K+</p>
                  <p className="text-primary-100">Análises</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center">
                  <p className="text-4xl font-bold text-white mb-2">85%</p>
                  <p className="text-primary-100">Precisão</p>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 text-center">
                  <p className="text-4xl font-bold text-white mb-2">24/7</p>
                  <p className="text-primary-100">Disponível</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="bg-white dark:bg-gray-800 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Como Funciona
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Tecnologia avançada ao seu alcance
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-20 h-20 bg-primary-100 dark:bg-primary-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <TrendingUp className="w-10 h-10 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                1. Coletamos Dados
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Agregamos estatísticas em tempo real de fontes verificadas: Football-Data.org e API-Football. Histórico completo, confrontos diretos, desempenho recente.
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-primary-100 dark:bg-primary-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Brain className="w-10 h-10 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                2. IA Analisa
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Nossa inteligência artificial processa milhares de dados, identifica padrões, tendências e fatores que influenciam o resultado das partidas.
              </p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-primary-100 dark:bg-primary-900/30 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <Zap className="w-10 h-10 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                3. Você Decide
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Receba análises claras, insights acionáveis e previsões fundamentadas para entender melhor cada partida e tomar decisões informadas.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Nossos Valores
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            O que nos guia em tudo que fazemos
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {values.map((value, i) => (
            <div
              key={i}
              className="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 text-center hover:border-primary-500 dark:hover:border-primary-500 transition-all hover:shadow-xl group"
            >
              <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <value.icon className="w-8 h-8 text-primary-600 dark:text-primary-400" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                {value.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {value.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Team */}
      <section className="bg-white dark:bg-gray-800 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Nossa Equipa
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Profissionais dedicados ao futebol e tecnologia
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {team.map((member, i) => (
              <div
                key={i}
                className="bg-gray-50 dark:bg-gray-700 rounded-2xl p-8 text-center"
              >
                <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-primary-700 rounded-full flex items-center justify-center mx-auto mb-6">
                  <Users className="w-12 h-12 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {member.name}
                </h3>
                <p className="text-primary-600 dark:text-primary-400 font-semibold mb-4">
                  {member.role}
                </p>
                <p className="text-gray-600 dark:text-gray-400">
                  {member.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Disclaimer */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-200 dark:border-yellow-800 rounded-3xl p-8 lg:p-12">
          <div className="flex items-start gap-4 mb-6">
            <div className="w-12 h-12 bg-yellow-500 rounded-2xl flex items-center justify-center flex-shrink-0">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                Isenção de Responsabilidade Importante
              </h2>
              <div className="space-y-4 text-gray-700 dark:text-gray-300">
                <p className="font-semibold text-lg">
                  O PlacarCerto é uma plataforma puramente informativa e educacional.
                </p>
                <ul className="space-y-2">
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span><strong>NÃO promovemos apostas:</strong> Nosso objetivo é fornecer análises estatísticas e insights sobre futebol.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span><strong>NÃO garantimos resultados:</strong> Análises são baseadas em dados históricos e não constituem garantias futuras.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span><strong>NÃO somos casa de apostas:</strong> Não processamos apostas nem temos ligação com operadores de jogos.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span><strong>Uso responsável:</strong> Qualquer decisão tomada com base em nossas análises é de sua inteira responsabilidade.</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-br from-primary-600 to-primary-700 rounded-3xl p-12 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Pronto Para Começar?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Junte-se a milhares de fãs de futebol que já usam análises inteligentes
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white hover:bg-gray-50 text-primary-600 rounded-xl font-semibold shadow-xl transition-all hover:scale-105"
            >
              Criar Conta Grátis
            </Link>
            <a
              href="mailto:contato@placarcerto.co.mz"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-primary-500 hover:bg-primary-400 text-white border-2 border-white/20 rounded-xl font-semibold transition-all"
            >
              <Mail className="w-5 h-5" />
              Entrar em Contato
            </a>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
