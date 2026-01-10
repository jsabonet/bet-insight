import { useState, useEffect } from 'react';
import { 
  Target, 
  BarChart3, 
  History, 
  DollarSign, 
  Users,
  ChevronDown,
  ChevronRight,
  Menu,
  X
} from 'lucide-react';

/**
 * Menu de Navegação para Página de Detalhes da Partida
 * - Menu lateral em desktop
 * - Menu hamburger em mobile
 * - Scroll suave para seções
 * - Indicador de seção ativa
 */
export default function NavigationMenu({ sections, activeSection, onNavigate }) {
  const [isOpen, setIsOpen] = useState(false);
  const [expandedCategories, setExpandedCategories] = useState(['overview']);

  // Fechar menu ao navegar (mobile)
  const handleNavigate = (sectionId) => {
    onNavigate(sectionId);
    if (window.innerWidth < 1024) {
      setIsOpen(false);
    }
  };

  // Toggle categoria expandida
  const toggleCategory = (categoryId) => {
    setExpandedCategories(prev => 
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  // Categorias do menu
  const categories = [
    {
      id: 'overview',
      name: '🎯 Visão Geral',
      icon: Target,
      sections: [
        { id: 'at-a-glance', name: 'Resumo da Partida', component: 'AtAGlance' },
        { id: 'goals-poisson', name: 'Análise de Gols', component: 'GoalsAndPoisson' }
      ]
    },
    {
      id: 'stats',
      name: '📊 Análise Estatística',
      icon: BarChart3,
      sections: [
        { id: 'team-comparison', name: 'Comparação de Times', component: 'TeamComparison' },
        { id: 'match-stats', name: 'Estatísticas da Partida', component: 'MatchStatistics' },
        { id: 'team-form', name: 'Últimos 5 Jogos', component: 'TeamForm' }
      ]
    },
    {
      id: 'history',
      name: '🆚 Histórico',
      icon: History,
      sections: [
        { id: 'head-to-head', name: 'Confrontos Diretos', component: 'HeadToHead' },
        { id: 'standings', name: 'Classificação da Liga', component: 'LeagueStandings' }
      ]
    },
    {
      id: 'odds',
      name: '💰 Mercados & Odds',
      icon: DollarSign,
      sections: [
        { id: 'value-bets', name: 'Análise de Value Bets', component: 'ValueBetsSection' }
      ]
    },
    {
      id: 'lineups',
      name: '⚽ Escalações',
      icon: Users,
      sections: [
        { id: 'match-context', name: 'Contexto da Partida', component: 'MatchContext' },
        { id: 'lineups', name: 'Formações e Jogadores', component: 'Lineups' }
      ]
    }
  ];

  // Filtrar categorias que têm seções com dados
  const availableCategories = categories.map(category => {
    const availableSections = category.sections.filter(section => {
      const sectionData = sections.find(s => s.id === section.id);
      return sectionData && sectionData.hasData;
    });
    
    return {
      ...category,
      sections: availableSections,
      count: availableSections.length
    };
  }).filter(category => category.count > 0);

  return (
    <>
      {/* Mobile: Botão Hamburger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="lg:hidden fixed top-20 left-4 z-50 bg-white dark:bg-gray-800 rounded-lg p-2 shadow-lg border border-gray-200 dark:border-gray-700"
        aria-label="Menu de navegação"
      >
        {isOpen ? (
          <X className="w-6 h-6 text-gray-700 dark:text-gray-300" />
        ) : (
          <Menu className="w-6 h-6 text-gray-700 dark:text-gray-300" />
        )}
      </button>

      {/* Overlay mobile */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Menu Lateral */}
      <nav
        className={`
          fixed lg:sticky top-20 left-0 h-[calc(100vh-5rem)] z-40
          bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700
          transition-transform duration-300 overflow-y-auto
          ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
          w-72 lg:w-64
        `}
      >
        <div className="p-4">
          <h2 className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
            Navegação
          </h2>

          <div className="space-y-2">
            {availableCategories.map((category) => {
              const isExpanded = expandedCategories.includes(category.id);
              const Icon = category.icon;

              return (
                <div key={category.id} className="space-y-1">
                  {/* Header da Categoria */}
                  <button
                    onClick={() => toggleCategory(category.id)}
                    className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <Icon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                      <span className="text-sm font-semibold text-gray-900 dark:text-white">
                        {category.name}
                      </span>
                      <span className="text-xs bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 px-1.5 py-0.5 rounded-full">
                        {category.count}
                      </span>
                    </div>
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    )}
                  </button>

                  {/* Subseções */}
                  {isExpanded && (
                    <div className="ml-6 space-y-1">
                      {category.sections.map((section) => {
                        const isActive = activeSection === section.id;
                        
                        return (
                          <button
                            key={section.id}
                            onClick={() => handleNavigate(section.id)}
                            className={`
                              w-full text-left px-3 py-2 rounded-lg text-sm transition-colors
                              ${isActive
                                ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400 font-medium'
                                : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                              }
                            `}
                          >
                            {isActive && (
                              <span className="inline-block w-1 h-4 bg-primary-600 dark:bg-primary-400 rounded-full mr-2" />
                            )}
                            {section.name}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </nav>
    </>
  );
}
