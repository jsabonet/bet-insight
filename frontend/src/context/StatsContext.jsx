import { createContext, useContext, useState } from 'react';

const StatsContext = createContext();

export function StatsProvider({ children }) {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const refreshStats = () => {
    setRefreshTrigger(prev => {
      console.log('🎯 RefreshTrigger incrementado:', prev, '→', prev + 1);
      return prev + 1;
    });
  };

  return (
    <StatsContext.Provider value={{ refreshTrigger, refreshStats }}>
      {children}
    </StatsContext.Provider>
  );
}

export function useStats() {
  const context = useContext(StatsContext);
  if (!context) {
    throw new Error('useStats must be used within StatsProvider');
  }
  return context;
}
