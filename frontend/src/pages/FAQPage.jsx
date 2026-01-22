import { Link } from 'react-router-dom';
import { useEffect } from 'react';
import { HelpCircle, ArrowLeft } from 'lucide-react';
import Logo from '../components/Logo';
import Footer from '../components/Footer';
import SEOHead from '../components/SEO/SEOHead';
import FAQSection, { defaultFAQs } from '../components/FAQSection';
import { generateFAQStructuredData } from '../utils/structuredData';

export default function FAQPage() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <SEOHead
        title="Perguntas Frequentes (FAQ) | PlacerCerto"
        description="Respostas às perguntas mais frequentes sobre análise estatística de futebol, modelos Poisson, planos Premium, métodos de pagamento e muito mais."
        keywords="faq futebol, perguntas frequentes, como funciona placercerto, análise estatística, poisson, m-pesa moçambique"
        canonicalUrl="https://placarcerto.digital/faq"
        structuredData={generateFAQStructuredData(defaultFAQs)}
      />

      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link to="/">
              <Logo variant="default" size="md" showText={true} />
            </Link>
            <Link
              to="/"
              className="flex items-center gap-2 text-gray-700 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 font-medium transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Voltar
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-700 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <HelpCircle className="w-16 h-16 mx-auto mb-4 opacity-90" />
          <h1 className="text-4xl lg:text-5xl font-bold mb-4">
            Perguntas Frequentes
          </h1>
          <p className="text-xl text-primary-100">
            Tudo o que você precisa saber sobre o PlacerCerto
          </p>
        </div>
      </section>

      {/* FAQ Content */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <FAQSection faqs={defaultFAQs} />

        {/* Contact CTA */}
        <div className="mt-12 p-8 bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 rounded-2xl text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
            Ainda tem dúvidas?
          </h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Estamos aqui para ajudar! Entre em contato conosco.
          </p>
          <a
            href="mailto:suporte@placarcerto.digital"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-semibold transition-all hover:scale-105 shadow-lg"
          >
            Enviar Email
          </a>
        </div>
      </section>

      <Footer />
    </div>
  );
}
