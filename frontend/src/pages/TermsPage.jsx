import { Link } from 'react-router-dom';
import { useEffect } from 'react';
import { Scale, AlertTriangle, FileText, CheckCircle2, XCircle, Shield, Mail } from 'lucide-react';
import Logo from '../components/Logo';
import Footer from '../components/Footer';

export default function TermsPage() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

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

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg p-8 lg:p-12">
          <div className="flex items-center gap-4 mb-8">
            <div className="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-2xl flex items-center justify-center">
              <Scale className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
                Termos de Serviço
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Última atualização: 1 de Janeiro de 2026
              </p>
            </div>
          </div>

          <div className="prose prose-lg dark:prose-invert max-w-none space-y-8">
            {/* Introdução */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                1. Aceitação dos Termos
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                Bem-vindo ao PlacarCerto! Estes Termos de Serviço ("Termos") regem o seu acesso e uso da nossa plataforma de análise de futebol, incluindo nosso website, aplicativos móveis e serviços relacionados (coletivamente, os "Serviços").
              </p>
              <p className="text-gray-700 dark:text-gray-300">
                Ao acessar ou usar nossos Serviços, você concorda em ficar vinculado a estes Termos. Se você não concorda com qualquer parte destes Termos, não deve usar nossos Serviços.
              </p>
            </section>

            {/* Descrição do Serviço */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <CheckCircle2 className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                2. Descrição do Serviço
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                O PlacarCerto oferece:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li><strong>Análises Estatísticas:</strong> Dados e estatísticas sobre partidas de futebol</li>
                <li><strong>Previsões com IA:</strong> Análises automatizadas baseadas em inteligência artificial</li>
                <li><strong>Histórico de Confrontos:</strong> Informações sobre confrontos diretos entre equipas</li>
                <li><strong>Insights e Tendências:</strong> Análises de desempenho e padrões</li>
              </ul>
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border-l-4 border-yellow-500 p-4 mt-4">
                <p className="text-gray-700 dark:text-gray-300 font-semibold">
                  <AlertTriangle className="inline w-5 h-5 mr-2" />
                  Isenção de Responsabilidade Importante:
                </p>
                <p className="text-gray-700 dark:text-gray-300 mt-2">
                  Nossos Serviços são exclusivamente informativos e educacionais. NÃO promovemos, facilitamos ou encorajamos apostas. As análises fornecidas não constituem conselhos de apostas e não devem ser interpretadas como garantias de resultados.
                </p>
              </div>
            </section>

            {/* Elegibilidade */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Shield className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                3. Elegibilidade e Conta
              </h2>
              
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">3.1. Requisitos de Idade</h3>
              <p className="text-gray-700 dark:text-gray-300">
                Você deve ter pelo menos 18 anos de idade para criar uma conta e usar nossos Serviços. Ao criar uma conta, você declara e garante que tem 18 anos ou mais.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">3.2. Criação de Conta</h3>
              <p className="text-gray-700 dark:text-gray-300 mb-2">
                Para acessar determinados recursos, você deve criar uma conta fornecendo informações precisas e completas. Você é responsável por:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Manter a confidencialidade de suas credenciais</li>
                <li>Todas as atividades que ocorrem em sua conta</li>
                <li>Notificar-nos imediatamente de qualquer uso não autorizado</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">3.3. Suspensão de Conta</h3>
              <p className="text-gray-700 dark:text-gray-300">
                Reservamo-nos o direito de suspender ou encerrar sua conta se você violar estes Termos ou se envolvermos em atividades fraudulentas ou ilegais.
              </p>
            </section>

            {/* Uso Aceitável */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <CheckCircle2 className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                4. Uso Aceitável
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                Você concorda em NÃO:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Usar os Serviços para fins ilegais ou não autorizados</li>
                <li>Violar leis locais, estaduais, nacionais ou internacionais</li>
                <li>Tentar obter acesso não autorizado aos nossos sistemas</li>
                <li>Interferir ou interromper o funcionamento dos Serviços</li>
                <li>Usar bots, scrapers ou ferramentas automatizadas sem permissão</li>
                <li>Copiar, reproduzir ou distribuir nosso conteúdo sem autorização</li>
                <li>Fazer engenharia reversa de qualquer parte dos Serviços</li>
                <li>Criar múltiplas contas para abusar de recursos gratuitos</li>
                <li>Revender ou comercializar acesso aos nossos Serviços</li>
                <li>Usar os Serviços de maneira que possa prejudicar outros usuários</li>
              </ul>
            </section>

            {/* Planos e Pagamentos */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                5. Planos e Pagamentos
              </h2>
              
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">5.1. Planos Disponíveis</h3>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li><strong>Freemium:</strong> Plano gratuito com 3 análises por dia</li>
                <li><strong>Planos Premium:</strong> Assinaturas pagas com análises ilimitadas e recursos avançados</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">5.2. Pagamentos</h3>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Pagamentos são processados através do PaySuite (M-Pesa)</li>
                <li>Os preços são exibidos em Meticais (MZN)</li>
                <li>Você autoriza cobranças recorrentes para assinaturas</li>
                <li>Você é responsável por todos os impostos aplicáveis</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">5.3. Reembolsos e Cancelamentos</h3>
              <p className="text-gray-700 dark:text-gray-300">
                Você pode cancelar sua assinatura a qualquer momento através das configurações da sua conta. O cancelamento entra em vigor no final do período de cobrança atual. Não oferecemos reembolsos proporcionais para cancelamentos no meio do ciclo, exceto quando exigido por lei.
              </p>
            </section>

            {/* Propriedade Intelectual */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Shield className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                6. Propriedade Intelectual
              </h2>
              
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">6.1. Nosso Conteúdo</h3>
              <p className="text-gray-700 dark:text-gray-300">
                Todos os direitos, títulos e interesses nos Serviços, incluindo textos, gráficos, logos, ícones, imagens, clipes de áudio, downloads digitais, compilações de dados e software, são propriedade do PlacarCerto ou de nossos licenciadores.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">6.2. Dados de Terceiros</h3>
              <p className="text-gray-700 dark:text-gray-300">
                Utilizamos dados de provedores terceiros (Football-Data.org, API-Football). Esses dados são fornecidos sob suas respectivas licenças e termos de uso.
              </p>

              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">6.3. Licença de Uso</h3>
              <p className="text-gray-700 dark:text-gray-300">
                Concedemos a você uma licença limitada, não exclusiva, intransferível e revogável para acessar e usar os Serviços para fins pessoais e não comerciais.
              </p>
            </section>

            {/* Isenção de Garantias */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <XCircle className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                7. Isenção de Garantias
              </h2>
              <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 p-4">
                <p className="text-gray-700 dark:text-gray-300 font-semibold mb-2">
                  OS SERVIÇOS SÃO FORNECIDOS "COMO ESTÃO" E "CONFORME DISPONÍVEIS", SEM GARANTIAS DE QUALQUER TIPO.
                </p>
                <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                  <li>Não garantimos que os Serviços serão ininterruptos, seguros ou livres de erros</li>
                  <li>Não garantimos a precisão, completude ou confiabilidade das análises e previsões</li>
                  <li>Não garantimos que os Serviços atenderão suas expectativas ou necessidades específicas</li>
                  <li>As previsões e análises não constituem conselhos profissionais</li>
                  <li>Não somos responsáveis por decisões tomadas com base em nossas análises</li>
                </ul>
              </div>
            </section>

            {/* Limitação de Responsabilidade */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <AlertTriangle className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                8. Limitação de Responsabilidade
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                NA MÁXIMA EXTENSÃO PERMITIDA POR LEI:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Não seremos responsáveis por danos indiretos, incidentais, especiais ou consequenciais</li>
                <li>Nossa responsabilidade total não excederá o valor pago por você nos últimos 12 meses</li>
                <li>Não somos responsáveis por perdas resultantes de apostas ou decisões baseadas em nossas análises</li>
                <li>Não somos responsáveis por interrupções de serviço causadas por terceiros ou eventos fora de nosso controle</li>
              </ul>
            </section>

            {/* Indenização */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Shield className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                9. Indenização
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                Você concorda em indenizar, defender e isentar o PlacarCerto, seus diretores, funcionários e agentes de quaisquer reivindicações, responsabilidades, danos, perdas e despesas resultantes de:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Sua violação destes Termos</li>
                <li>Seu uso indevido dos Serviços</li>
                <li>Sua violação de direitos de terceiros</li>
                <li>Qualquer atividade fraudulenta ou ilegal</li>
              </ul>
            </section>

            {/* Modificações */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                10. Modificações dos Termos
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                Reservamo-nos o direito de modificar estes Termos a qualquer momento. Notificaremos você sobre alterações significativas através de e-mail ou notificação na plataforma. O uso continuado dos Serviços após as alterações constitui aceitação dos novos Termos.
              </p>
            </section>

            {/* Lei Aplicável */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Scale className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                11. Lei Aplicável e Jurisdição
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                Estes Termos são regidos pelas leis de Moçambique. Qualquer disputa será resolvida nos tribunais de Maputo, Moçambique.
              </p>
            </section>

            {/* Disposições Gerais */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                12. Disposições Gerais
              </h2>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li><strong>Acordo Integral:</strong> Estes Termos constituem o acordo integral entre você e o PlacarCerto</li>
                <li><strong>Renúncia:</strong> Nossa falha em fazer cumprir qualquer direito não constitui renúncia</li>
                <li><strong>Divisibilidade:</strong> Se qualquer disposição for inválida, as demais permanecerão em vigor</li>
                <li><strong>Cessão:</strong> Você não pode transferir seus direitos sem nossa autorização</li>
              </ul>
            </section>

            {/* Contato */}
            <section className="bg-primary-50 dark:bg-primary-900/20 rounded-2xl p-6">
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Mail className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                13. Contato
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                Para questões sobre estes Termos de Serviço, entre em contato:
              </p>
              <div className="space-y-2 text-gray-700 dark:text-gray-300">
                <p><strong>PlacarCerto</strong></p>
                <p>E-mail Legal: <a href="mailto:legal@placarcerto.co.mz" className="text-primary-600 dark:text-primary-400 hover:underline">legal@placarcerto.co.mz</a></p>
                <p>E-mail Geral: <a href="mailto:contato@placarcerto.co.mz" className="text-primary-600 dark:text-primary-400 hover:underline">contato@placarcerto.co.mz</a></p>
                <p>Localização: Maputo, Moçambique</p>
              </div>
            </section>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
}
