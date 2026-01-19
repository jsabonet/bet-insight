import { useStrategy } from '../context/StrategyContext';
import { Zap, ClipboardList } from 'lucide-react';

export default function StrategySelector() {
  const { strategy, setStrategy } = useStrategy();

  return (
    <div className="bg-white/10 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl p-2 border border-white/20 dark:border-gray-700/50">
      <div className="flex gap-2">
        <button
          onClick={() => setStrategy('value')}
          className={`
            flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg
            font-medium text-sm transition-all duration-200
            ${strategy === 'value' 
              ? 'bg-gradient-to-r from-yellow-400 to-orange-500 text-gray-900 shadow-lg shadow-yellow-500/30' 
              : 'bg-white/10 dark:bg-gray-700/30 text-white/70 dark:text-gray-400 hover:bg-white/20 dark:hover:bg-gray-700/50'
            }
          `}
          aria-label="Modo Aposta Simples"
        >
          <Zap className="w-4 h-4" />
          <span className="hidden sm:inline">Aposta Simples</span>
          <span className="sm:hidden">Simples</span>
        </button>

        <button
          onClick={() => setStrategy('multiple')}
          className={`
            flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg
            font-medium text-sm transition-all duration-200
            ${strategy === 'multiple'
              ? 'bg-gradient-to-r from-blue-400 to-purple-500 text-white shadow-lg shadow-blue-500/30'
              : 'bg-white/10 dark:bg-gray-700/30 text-white/70 dark:text-gray-400 hover:bg-white/20 dark:hover:bg-gray-700/50'
            }
          `}
          aria-label="Modo Para Bilhete"
        >
          <ClipboardList className="w-4 h-4" />
          <span className="hidden sm:inline">Para Bilhete</span>
          <span className="sm:hidden">Bilhete</span>
        </button>
      </div>
    </div>
  );
}
