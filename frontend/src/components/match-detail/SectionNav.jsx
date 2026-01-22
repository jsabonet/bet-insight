import { useState, useEffect } from 'react';
import { FileText, BarChart3, Users, TrendingUp, Table, Target, GitCompare, Goal, Award, UserCheck, ArrowUp } from 'lucide-react';

/**
 * Menu de navegação inteligente para página de detalhes
 * Sticky, com indicador de seção ativa e botão scroll to top
 */
export default function SectionNav({ sections = [] }) {
  const [activeSection, setActiveSection] = useState('');
  const [isSticky, setIsSticky] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);

  // Definir seções padrão se não fornecidas
  const defaultSections = [
    { id: 'overview', label: 'Visão Geral', icon: Target },
    { id: 'comparison', label: 'Comparação', icon: GitCompare },
    { id: 'goals', label: 'Gols', icon: Goal },
    { id: 'valuebets', label: 'Value Bets', icon: Award },
    { id: 'context', label: 'Contexto', icon: FileText },
    { id: 'lineups', label: 'Escalações', icon: UserCheck },
    { id: 'statistics', label: 'Estatísticas', icon: BarChart3 },
    { id: 'h2h', label: 'Confrontos', icon: Users },
    { id: 'form', label: 'Forma', icon: TrendingUp },
    { id: 'standings', label: 'Classificação', icon: Table },
  ];

  const navSections = sections.length > 0 ? sections : defaultSections;

  useEffect(() => {
    const handleScroll = () => {
      const scrollY = window.scrollY;
      
      // Tornar sticky após 300px
      setIsSticky(scrollY > 300);
      
      // Mostrar botão scroll to top após 500px
      setShowScrollTop(scrollY > 500);

      // Detectar seção ativa
      const scrollPosition = scrollY + 120; // Offset para o menu

      for (const section of navSections) {
        const element = document.getElementById(section.id);
        if (element) {
          const { offsetTop, offsetHeight } = element;
          if (scrollPosition >= offsetTop && scrollPosition < offsetTop + offsetHeight) {
            setActiveSection(section.id);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll);
    handleScroll(); // Check initial position

    return () => window.removeEventListener('scroll', handleScroll);
  }, [navSections]);

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      const offset = 100; // Offset para o header
      const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
      const offsetPosition = elementPosition - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    }
  };

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  // Não mostrar se nenhuma seção existe no DOM
  const hasAnySections = navSections.some(section => document.getElementById(section.id));
  if (!hasAnySections) return null;

  return (
    <>
      <nav
        className={`
          ${isSticky ? 'fixed top-0 left-0 right-0 z-40 shadow-lg animate-slide-down' : 'relative'}
          bg-white/90 dark:bg-gray-800/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-700
          transition-all duration-300
        `}
      >
        <div className="max-w-7xl mx-auto px-4">
          {/* Desktop - Horizontal */}
          <div className="hidden md:flex items-center justify-center gap-1 py-3 flex-wrap">
            {navSections.map((section) => {
              const Icon = section.icon;
              const isActive = activeSection === section.id;
              const exists = document.getElementById(section.id);
              
              if (!exists) return null;

              return (
                <button
                  key={section.id}
                  onClick={() => scrollToSection(section.id)}
                  className={`
                    flex items-center gap-2 px-3 py-2 rounded-xl font-medium text-sm
                    transition-all duration-200
                    ${isActive
                      ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30 scale-105'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100 hover:scale-105'
                    }
                  `}
                >
                  <Icon className="w-4 h-4" />
                  <span>{section.label}</span>
                </button>
              );
            })}
          </div>

          {/* Mobile - Horizontal Scroll */}
          <div className="md:hidden overflow-x-auto scrollbar-hide py-3">
            <div className="flex gap-2 min-w-max px-1">
              {navSections.map((section) => {
                const Icon = section.icon;
                const isActive = activeSection === section.id;
                const exists = document.getElementById(section.id);
                
                if (!exists) return null;

                return (
                  <button
                    key={section.id}
                    onClick={() => scrollToSection(section.id)}
                    className={`
                      flex flex-col items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium
                      transition-all duration-200 flex-shrink-0
                      ${isActive
                        ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 bg-gray-50 dark:bg-gray-800/50'
                      }
                    `}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="whitespace-nowrap">{section.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </nav>

      {/* Botão Scroll to Top */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-24 right-4 z-50 p-3 rounded-full bg-primary-500 text-white shadow-lg shadow-primary-500/30 hover:bg-primary-600 hover:scale-110 active:scale-95 transition-all duration-200 animate-slide-up"
          aria-label="Voltar ao topo"
        >
          <ArrowUp className="w-5 h-5" />
        </button>
      )}
    </>
  );
}
