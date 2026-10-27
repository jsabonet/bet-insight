import { Link } from 'react-router-dom';
import { ArrowLeft, Shield, BookOpen, Coins, Clock, AlertTriangle } from 'lucide-react';
import Logo from '../components/Logo';
import Footer from '../components/Footer';
import { AFFILIATE_TERMS_VERSION } from '../utils/affiliateTerms';

const sections = [
  {
    title: '1. Natureza do serviço e do programa',
    icon: BookOpen,
    content: (
      <>
        <p>
          O PlacarCerto é um serviço SaaS educativo de análise estatística e informação sobre futebol.
          Não é uma casa de apostas, não aceita nem intermedeia apostas, não gere saldos de apostas,
          nem paga prémios de apostas. A divulgação remunerada refere-se exclusivamente ao acesso
          ao software para estudo estatístico.
        </p>
        <p>
          O programa remunera a divulgação do acesso ao software. Não remunera apostas, resultados
          desportivos, perdas ou ganhos de utilizadores. A participação não cria vínculo laboral,
          sociedade, representação ou autorização para assumir compromissos em nome do PlacarCerto.
        </p>
      </>
    ),
  },
  {
    title: '2. Elegibilidade e aceitação',
    icon: Shield,
    content: (
      <p>
        Para participar, deve ter pelo menos 18 anos, possuir uma conta válida e aceitar esta versão
        dos termos. A aceitação fica registada com a versão e a data/hora. Se os termos forem
        atualizados, será necessário aceitar a nova versão para continuar a usar o programa.
      </p>
    ),
  },
  {
    title: '3. Comissão e vendas elegíveis',
    icon: Coins,
    content: (
      <>
        <p>
          A comissão atual é de <strong>100 MZN por utilizador indicado</strong>, paga uma única vez,
          quando a primeira compra elegível desse utilizador for confirmada. Não há comissão sobre
          renovações, compras próprias, pagamentos de teste, pagamentos não concluídos ou transações
          associadas a fraude.
        </p>
        <p>
          A comissão fica pendente durante <strong>14 dias</strong> após a confirmação do pagamento.
          Depois desse período, passa a disponível se não houver reembolso, contestação ou indício
          fundamentado de fraude. Uma comissão revertida deixa de integrar o saldo levantável.
        </p>
        <p>
          O nível interno do afiliado (Padrão ou VIP) não altera este valor. Qualquer alteração
          futura às condições será comunicada e registada numa nova versão dos termos; não reduz
          retroativamente comissões já disponíveis.
        </p>
      </>
    ),
  },
  {
    title: '4. Atribuição de indicações',
    icon: Clock,
    content: (
      <p>
        O código de afiliado é conservado no navegador por até <strong>30 dias</strong>. A indicação
        é associada à conta quando o utilizador se regista. Um código promocional introduzido pelo
        utilizador pode prevalecer sobre um link anterior. Cada conta indicada pode gerar no máximo
        uma comissão, referente à primeira compra elegível.
      </p>
    ),
  },
  {
    title: '5. Levantamentos',
    icon: Coins,
    content: (
      <>
        <p>
          O valor mínimo por pedido é <strong>200 MZN</strong>. Aplica-se uma taxa de processamento
          de <strong>6%</strong>, deduzida do valor solicitado; o painel apresenta o valor bruto, a
          taxa e o valor líquido antes da confirmação. Os métodos atualmente disponíveis são M-Pesa,
          e-Mola e transferência bancária, sujeitos à disponibilidade e à validação dos dados.
        </p>
        <p>
          Pedidos válidos, com dados de pagamento corretos, serão processados em até
          <strong> 5 dias úteis</strong>. O prazo pode suspender-se enquanto forem necessários dados
          corrigidos ou verificações de segurança. O saldo solicitado fica reservado durante o
          processamento e é libertado se o pedido for rejeitado.
        </p>
        <p>
          O afiliado deve cumprir as obrigações fiscais que lhe sejam aplicáveis. A plataforma não
          presta aconselhamento fiscal.
        </p>
      </>
    ),
  },
  {
    title: '6. Regras de divulgação',
    icon: AlertTriangle,
    content: (
      <>
        <p>O afiliado deve apresentar a plataforma de forma verdadeira, clara e responsável. É proibido:</p>
        <ul className="list-disc space-y-2 pl-6">
          <li>promover, recomendar, facilitar ou direcionar pessoas para apostas, casas de apostas ou mercados de jogo;</li>
          <li>divulgar seleções, combinações ou conteúdos do PlacarCerto como recomendações para apostar;</li>
          <li>prometer ganhos, resultados certos, lucro, retorno financeiro ou sucesso em apostas;</li>
          <li>apresentar análises educativas como conselho financeiro ou garantia de resultado desportivo;</li>
          <li>usar spam, mensagens não solicitadas, publicidade enganosa, falsas identidades ou contas artificiais;</li>
          <li>usar a marca, criativos ou dados do PlacarCerto de forma não autorizada ou que sugira parceria oficial não existente.</li>
        </ul>
        <p>
          Quando divulgar um link que possa gerar comissão, deve informar de forma visível que se
          trata de um link de afiliado. O afiliado é responsável pelos canais e conteúdos que publica.
        </p>
      </>
    ),
  },
  {
    title: '7. Suspensão, encerramento e contacto',
    icon: Shield,
    content: (
      <>
        <p>
          O PlacarCerto pode suspender links, comissões pendentes ou o acesso ao programa enquanto
          investiga fraude, abuso ou violação destes termos. Decisões sobre comissões serão
          comunicadas ao afiliado. Comissões confirmadas não são anuladas apenas por encerramento
          da participação, salvo quando relacionadas com reembolso, contestação, fraude ou violação
          destes termos, observada a legislação aplicável. Para dúvidas, contacte
          {' '}<a className="text-primary-600 hover:underline" href="mailto:contato@placarcerto.co.mz">contato@placarcerto.co.mz</a>.
        </p>
      </>
    ),
  },
];

export default function AffiliateTermsPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <header className="border-b border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-4">
          <Link to="/landing"><Logo variant="default" size="md" showText /></Link>
          <Link to="/affiliate/apply" className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
            <ArrowLeft className="h-4 w-4" /> Voltar ao programa
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
        <div className="mb-6 rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-900 dark:border-blue-900 dark:bg-blue-950/40 dark:text-blue-100">
          O PlacarCerto é uma plataforma SaaS educativa. Não é uma casa de apostas e o programa de
          afiliados não promove nem facilita apostas.
        </div>
        <div className="rounded-2xl bg-white p-6 shadow-lg dark:bg-gray-800 sm:p-10">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Termos do Programa de Afiliados</h1>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Versão {AFFILIATE_TERMS_VERSION} · Última atualização: 27 de outubro de 2026
          </p>
          <div className="prose prose-gray mt-8 max-w-none space-y-7 dark:prose-invert">
            {sections.map(({ title, icon: Icon, content }) => (
              <section key={title}>
                <h2 className="flex items-center gap-2 text-xl font-semibold">
                  <Icon className="h-5 w-5 text-primary-600" /> {title}
                </h2>
                <div className="space-y-3 text-gray-700 dark:text-gray-300">{content}</div>
              </section>
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
