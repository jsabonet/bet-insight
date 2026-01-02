import { Link } from 'react-router-dom';
import { Facebook, Twitter, Instagram, Mail, MapPin, Phone } from 'lucide-react';
import Logo from './Logo';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  const links = {
    product: [
      { name: 'Funcionalidades', href: '/about' },
      { name: 'Planos e Preços', href: '/premium' },
      { name: 'Como Funciona', href: '/about' }
    ],
    legal: [
      { name: 'Termos de Serviço', href: '/terms' },
      { name: 'Política de Privacidade', href: '/privacy' },
      { name: 'Sobre Nós', href: '/about' }
    ],
    support: [
      { name: 'Suporte', href: 'mailto:suporte@placarcerto.co.mz' },
      { name: 'FAQ', href: '/about' },
      { name: 'Contato', href: 'mailto:contato@placarcerto.co.mz' }
    ]
  };

  const social = [
    { name: 'Facebook', icon: Facebook, href: '#' },
    { name: 'Twitter', icon: Twitter, href: '#' },
    { name: 'Instagram', icon: Instagram, href: '#' }
  ];

  return (
    <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-8">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Logo variant="default" size="md" showText={true} />
            <p className="mt-4 text-gray-600 dark:text-gray-400 max-w-sm">
              Análises inteligentes de futebol com inteligência artificial. Estatísticas, previsões e insights para você tomar decisões informadas.
            </p>
            
            <div className="mt-6 space-y-2">
              <a href="mailto:contato@placarcerto.co.mz" className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                <Mail className="w-4 h-4" />
                <span className="text-sm">contato@placarcerto.co.mz</span>
              </a>
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <MapPin className="w-4 h-4" />
                <span className="text-sm">Maputo, Moçambique</span>
              </div>
            </div>

            <div className="flex items-center gap-4 mt-6">
              {social.map((item) => (
                <a
                  key={item.name}
                  href={item.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-xl flex items-center justify-center text-gray-600 dark:text-gray-400 hover:bg-primary-600 hover:text-white dark:hover:bg-primary-600 transition-all hover:scale-110"
                  aria-label={item.name}
                >
                  <item.icon className="w-5 h-5" />
                </a>
              ))}
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white mb-4">Produto</h3>
            <ul className="space-y-3">
              {links.product.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white mb-4">Legal</h3>
            <ul className="space-y-3">
              {links.legal.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Support Links */}
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white mb-4">Suporte</h3>
            <ul className="space-y-3">
              {links.support.map((link) => (
                <li key={link.name}>
                  {link.href.startsWith('mailto:') ? (
                    <a
                      href={link.href}
                      className="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                    >
                      {link.name}
                    </a>
                  ) : (
                    <Link
                      to={link.href}
                      className="text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                    >
                      {link.name}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              © {currentYear} PlacarCerto. Todos os direitos reservados.
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-500">
              Este site não promove apostas. Fornecemos apenas análises estatísticas e informações educativas sobre futebol.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
