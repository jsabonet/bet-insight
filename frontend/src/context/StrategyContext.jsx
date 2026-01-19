import { createContext, useContext, useState, useEffect } from 'react';

const StrategyContext = createContext();

export function StrategyProvider({ children }) {
  // Inicializar com valor do localStorage ou 'value' por padrão
  const [strategy, setStrategyState] = useState(() => {
    const saved = localStorage.getItem('betting_strategy');
    return saved || 'value';
  });

  // Salvar no localStorage quando mudar
  useEffect(() => {
    localStorage.setItem('betting_strategy', strategy);
  }, [strategy]);

  const setStrategy = (newStrategy) => {
    if (newStrategy === 'value' || newStrategy === 'multiple') {
      setStrategyState(newStrategy);
    }
  };

  const value = {
    strategy,
    setStrategy,
    isValue: strategy === 'value',
    isMultiple: strategy === 'multiple',
  };

  return (
    <StrategyContext.Provider value={value}>
      {children}
    </StrategyContext.Provider>
  );
}

export function useStrategy() {
  const context = useContext(StrategyContext);
  if (!context) {
    throw new Error('useStrategy must be used within StrategyProvider');
  }
  return context;
}
