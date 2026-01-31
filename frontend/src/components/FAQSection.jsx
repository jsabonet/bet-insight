import SEOHead from '../components/SEO/SEOHead';
import { generateFAQStructuredData } from '../utils/structuredData';

/**
 * Componente FAQ otimizado para SEO
 * Gera structured data para aparecer em "People Also Ask" do Google
 */
const FAQSection = ({ faqs }) => {
  return (
    <>
      <SEOHead
        structuredData={generateFAQStructuredData(faqs)}
      />
      
      <div className="space-y-4">
        {faqs.map((faq, index) => (
          <details
            key={index}
            className="group card-flat cursor-pointer"
          >
            <summary className="flex items-center justify-between p-6 font-semibold text-gray-900 dark:text-gray-100 list-none">
              <span>{faq.question}</span>
              <svg
                className="w-5 h-5 transition-transform group-open:rotate-180"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </summary>
            <div className="px-6 pb-6 text-gray-600 dark:text-gray-400">
              {faq.answer}
            </div>
          </details>
        ))}
      </div>
    </>
  );
};

// FAQs padrão sobre PlacerCerto
export const defaultFAQs = [
  {
    question: "Como funcionam as análises estatísticas do PlacerCerto?",
    answer: "Utilizamos modelos matemáticos avançados (Poisson Bivariado + Regressão Logística) que processam 109 variáveis por partida, incluindo forma recente, confrontos diretos, estatísticas de gols, motivação das equipas e muito mais. O ensemble combina 50% Poisson, 35% Regressão Logística e 15% market priors."
  },
  {
    question: "As previsões são feitas por inteligência artificial?",
    answer: "Não. As previsões são geradas exclusivamente por modelos estatísticos comprovados (Poisson Bivariado e Regressão Logística) com base em 109 variáveis quantitativas. Todas as análises são puramente matemáticas e verificáveis."
  },
  {
    question: "Quantas análises posso fazer gratuitamente?",
    answer: "Usuários gratuitos têm 3 análises por dia. Com o plano Premium Semanal (49 MZN) ou Mensal (149 MZN), você tem análises ilimitadas."
  },
  {
    question: "Quais ligas estão disponíveis?",
    answer: "Cobrimos as principais ligas de Moçambique (Moçambola), África (Premier League Sul-Africana, Egyptian Premier League) e Europa (Premier League, La Liga, Serie A, Bundesliga, Ligue 1), além de competições internacionais como Champions League e Copa Africana."
  },
  {
    question: "As análises são em tempo real?",
    answer: "Sim! Os dados são atualizados constantemente através da API-Football. Partidas ao vivo têm estatísticas atualizadas minuto a minuto."
  },
  {
    question: "Posso confiar nas previsões?",
    answer: "Nossas previsões são baseadas em modelos matemáticos comprovados e dados históricos reais. No entanto, o futebol é imprevisível e nenhum modelo garante 100% de acerto. Use as análises como uma ferramenta de apoio à decisão, não como garantia."
  },
  {
    question: "Como cancelo minha assinatura Premium?",
    answer: "Você pode cancelar a qualquer momento na página 'Meu Perfil'. O cancelamento é imediato e você não será cobrado novamente. Não há taxas de cancelamento."
  },
  {
    question: "Quais métodos de pagamento são aceitos?",
    answer: "Aceitamos M-Pesa, o método de pagamento móvel mais popular em Moçambique. O processo é rápido, seguro e a ativação é instantânea."
  }
];

export default FAQSection;
