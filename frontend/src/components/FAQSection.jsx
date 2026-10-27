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
    answer: "Utilizamos modelos estatísticos, incluindo Poisson e regressão, juntamente com dados de forma recente, confrontos diretos e estatísticas das equipas para estimar probabilidades."
  },
  {
    question: "Como são calculadas as previsões?",
    answer: "As previsões são calculadas por modelos matemáticos, incluindo Poisson Bivariado e Regressão Logística, com base em dados estatísticos das partidas."
  },
  {
    question: "Quantas análises posso fazer gratuitamente?",
    answer: "O plano gratuito permite até 3 análises por dia. O Premium Vitalício custa 250 MZN, é pago uma vez e permite até 150 análises por dia."
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
    answer: "As análises são estimativas baseadas em dados estatísticos e não garantem o resultado de uma partida. O futebol é imprevisível; use as informações apenas como apoio para compreender os dados."
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
