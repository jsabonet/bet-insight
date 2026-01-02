import { Link } from 'react-router-dom';
import { useEffect } from 'react';
import { Shield, Lock, Eye, Database, Cookie, Globe, Mail, FileText } from 'lucide-react';
import Logo from '../components/Logo';
import Footer from '../components/Footer';

export default function PrivacyPage() {
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
              <Shield className="w-8 h-8 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
                Política de Privacidade
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
                <Eye className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                1. Introdução
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                A PlacarCerto ("nós", "nosso" ou "nos") respeita a sua privacidade e está comprometida em proteger os seus dados pessoais. Esta Política de Privacidade explica como coletamos, usamos, armazenamos e protegemos as suas informações quando você usa nossa plataforma de análise de futebol.
              </p>
              <p className="text-gray-700 dark:text-gray-300">
                Ao usar nossos serviços, você concorda com a coleta e uso de informações de acordo com esta política.
              </p>
            </section>

            {/* Dados Coletados */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Database className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                2. Dados Que Coletamos
              </h2>
              
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">2.1. Dados de Registro</h3>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Nome de usuário</li>
                <li>Endereço de e-mail</li>
                <li>Número de telefone (opcional, para notificações)</li>
                <li>Senha (criptografada)</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">2.2. Dados de Uso</h3>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Histórico de análises realizadas</li>
                <li>Partidas consultadas e favoritas</li>
                <li>Estatísticas de uso da plataforma</li>
                <li>Preferências de notificações</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">2.3. Dados Técnicos</h3>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Endereço IP</li>
                <li>Tipo e versão do navegador</li>
                <li>Sistema operacional</li>
                <li>Dispositivo utilizado</li>
                <li>Logs de acesso e erros</li>
              </ul>

              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mt-6 mb-3">2.4. Dados de Pagamento</h3>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Informações de transação (processadas por PaySuite)</li>
                <li>Histórico de assinaturas e pagamentos</li>
                <li>Não armazenamos dados completos de cartão de crédito</li>
              </ul>
            </section>

            {/* Como Usamos os Dados */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Lock className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                3. Como Usamos Seus Dados
              </h2>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li><strong>Prestação de Serviços:</strong> Fornecer análises de futebol, estatísticas e previsões</li>
                <li><strong>Autenticação:</strong> Gerenciar sua conta e login</li>
                <li><strong>Personalização:</strong> Adaptar a experiência às suas preferências</li>
                <li><strong>Comunicação:</strong> Enviar notificações sobre análises, atualizações e novidades</li>
                <li><strong>Processamento de Pagamentos:</strong> Gerenciar assinaturas premium</li>
                <li><strong>Melhoria do Serviço:</strong> Analisar uso para melhorar funcionalidades</li>
                <li><strong>Segurança:</strong> Detectar e prevenir fraudes e abusos</li>
                <li><strong>Conformidade Legal:</strong> Cumprir obrigações legais e regulatórias</li>
              </ul>
            </section>

            {/* Compartilhamento de Dados */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Globe className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                4. Compartilhamento de Dados
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                Não vendemos seus dados pessoais. Compartilhamos informações apenas nas seguintes situações:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li><strong>Processadores de Pagamento:</strong> PaySuite para processar transações</li>
                <li><strong>Provedores de Serviço:</strong> Empresas que nos ajudam a operar a plataforma (hospedagem, análise, etc.)</li>
                <li><strong>APIs de Dados:</strong> Football-Data.org e API-Football para estatísticas de partidas</li>
                <li><strong>Obrigações Legais:</strong> Quando exigido por lei ou ordem judicial</li>
                <li><strong>Proteção de Direitos:</strong> Para proteger nossos direitos, segurança ou propriedade</li>
              </ul>
            </section>

            {/* Cookies */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Cookie className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                5. Cookies e Tecnologias Similares
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                Utilizamos cookies e tecnologias similares para:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li><strong>Cookies Essenciais:</strong> Necessários para o funcionamento da plataforma (autenticação, segurança)</li>
                <li><strong>Cookies de Preferências:</strong> Lembrar suas configurações e escolhas</li>
                <li><strong>Cookies de Desempenho:</strong> Analisar como você usa o site para melhorias</li>
                <li><strong>Cookies de Marketing:</strong> Exibir anúncios relevantes (se aplicável)</li>
              </ul>
              <p className="text-gray-700 dark:text-gray-300 mt-4">
                Você pode gerenciar cookies através das configurações do seu navegador. Note que desabilitar cookies pode afetar a funcionalidade do site.
              </p>
            </section>

            {/* Segurança */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Lock className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                6. Segurança dos Dados
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                Implementamos medidas de segurança para proteger seus dados:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Criptografia SSL/TLS para transmissão de dados</li>
                <li>Senhas armazenadas com hash bcrypt</li>
                <li>Autenticação JWT com tokens seguros</li>
                <li>Controle de acesso baseado em permissões</li>
                <li>Backups regulares</li>
                <li>Monitoramento de segurança contínuo</li>
              </ul>
              <p className="text-gray-700 dark:text-gray-300 mt-4">
                No entanto, nenhum método de transmissão pela internet é 100% seguro. Fazemos o possível para proteger seus dados, mas não podemos garantir segurança absoluta.
              </p>
            </section>

            {/* Direitos do Usuário */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                7. Seus Direitos (GDPR e LGPD)
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                Você tem os seguintes direitos sobre seus dados pessoais:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li><strong>Acesso:</strong> Solicitar uma cópia dos seus dados</li>
                <li><strong>Retificação:</strong> Corrigir dados incorretos ou incompletos</li>
                <li><strong>Exclusão:</strong> Solicitar a exclusão de seus dados ("direito ao esquecimento")</li>
                <li><strong>Portabilidade:</strong> Receber seus dados em formato estruturado</li>
                <li><strong>Oposição:</strong> Opor-se ao processamento de seus dados</li>
                <li><strong>Restrição:</strong> Solicitar limitação do processamento</li>
                <li><strong>Revogação de Consentimento:</strong> Retirar consentimento a qualquer momento</li>
              </ul>
              <p className="text-gray-700 dark:text-gray-300 mt-4">
                Para exercer qualquer destes direitos, entre em contato conosco através de: <a href="mailto:privacidade@placarcerto.co.mz" className="text-primary-600 dark:text-primary-400 hover:underline">privacidade@placarcerto.co.mz</a>
              </p>
            </section>

            {/* Retenção de Dados */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Database className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                8. Retenção de Dados
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                Mantemos seus dados pessoais pelo tempo necessário para:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>Fornecer nossos serviços</li>
                <li>Cumprir obrigações legais</li>
                <li>Resolver disputas</li>
                <li>Fazer cumprir nossos acordos</li>
              </ul>
              <p className="text-gray-700 dark:text-gray-300 mt-4">
                Quando você exclui sua conta, removemos permanentemente seus dados pessoais dentro de 30 dias, exceto quando a retenção é exigida por lei.
              </p>
            </section>

            {/* Menores de Idade */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Shield className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                9. Privacidade de Menores
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                Nossos serviços são destinados a usuários com 18 anos ou mais. Não coletamos intencionalmente dados de menores de 18 anos. Se você é pai/mãe ou responsável e acredita que seu filho nos forneceu dados pessoais, entre em contato conosco.
              </p>
            </section>

            {/* Alterações */}
            <section>
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <FileText className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                10. Alterações nesta Política
              </h2>
              <p className="text-gray-700 dark:text-gray-300">
                Podemos atualizar esta Política de Privacidade periodicamente. Notificaremos você sobre alterações significativas através de:
              </p>
              <ul className="list-disc pl-6 space-y-2 text-gray-700 dark:text-gray-300">
                <li>E-mail para o endereço cadastrado</li>
                <li>Notificação na plataforma</li>
                <li>Atualização da data de "Última atualização" no topo desta página</li>
              </ul>
              <p className="text-gray-700 dark:text-gray-300 mt-4">
                Recomendamos que você revise esta política periodicamente.
              </p>
            </section>

            {/* Contato */}
            <section className="bg-primary-50 dark:bg-primary-900/20 rounded-2xl p-6">
              <h2 className="flex items-center gap-3 text-2xl font-bold text-gray-900 dark:text-white mb-4">
                <Mail className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                11. Contato
              </h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                Para questões sobre esta Política de Privacidade ou sobre o tratamento de seus dados pessoais, entre em contato:
              </p>
              <div className="space-y-2 text-gray-700 dark:text-gray-300">
                <p><strong>PlacarCerto</strong></p>
                <p>E-mail: <a href="mailto:privacidade@placarcerto.co.mz" className="text-primary-600 dark:text-primary-400 hover:underline">privacidade@placarcerto.co.mz</a></p>
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
