/**
 * Skeleton Loading Components
 * Sistema moderno de carregamento que exibe a estrutura da página
 */

// Skeleton base com animação de shimmer
export function Skeleton({ className = '', variant = 'default' }) {
  const baseClasses = 'relative overflow-hidden rounded-lg';
  const variantClasses = {
    default: 'bg-gray-300 dark:bg-gray-700',
    light: 'bg-gray-200 dark:bg-gray-800',
    card: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
  };
  
  return (
    <div className={`${baseClasses} ${variantClasses[variant]} ${className}`}>
      {/* Shimmer effect */}
      <div className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/40 dark:via-white/10 to-transparent" />
    </div>
  );
}

// Skeleton para card de partida
export function MatchCardSkeleton() {
  return (
    <div className="card animate-pulse">
      {/* Liga */}
      <div className="flex justify-between items-start mb-4">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>
      
      {/* Times */}
      <div className="flex items-center justify-between gap-4 mb-4">
        {/* Time Casa */}
        <div className="flex-1 flex items-center gap-3">
          <Skeleton className="w-12 h-12 rounded-full flex-shrink-0" />
          <div className="flex-1">
            <Skeleton className="h-5 w-full mb-2" />
            <Skeleton className="h-4 w-3/4" />
          </div>
        </div>
        
        {/* Placar */}
        <div className="flex gap-2 items-center">
          <Skeleton className="w-8 h-10" />
          <span className="text-gray-400">-</span>
          <Skeleton className="w-8 h-10" />
        </div>
        
        {/* Time Fora */}
        <div className="flex-1 flex items-center gap-3 flex-row-reverse">
          <Skeleton className="w-12 h-12 rounded-full flex-shrink-0" />
          <div className="flex-1 text-right">
            <Skeleton className="h-5 w-full mb-2 ml-auto" />
            <Skeleton className="h-4 w-3/4 ml-auto" />
          </div>
        </div>
      </div>
      
      {/* Data e Botão */}
      <div className="flex justify-between items-center pt-4 border-t border-gray-200 dark:border-gray-700">
        <Skeleton className="h-4 w-40" />
        <Skeleton className="h-10 w-32 rounded-lg" />
      </div>
    </div>
  );
}

// Skeleton para header de match detail
export function MatchDetailHeaderSkeleton() {
  return (
    <div className="card animate-pulse">
      {/* Liga */}
      <div className="text-center mb-6">
        <Skeleton className="h-6 w-32 mx-auto rounded-full" />
      </div>

      {/* Times e Placar */}
      <div className="flex items-center justify-center gap-8 mb-4">
        {/* Time Casa */}
        <div className="flex flex-col items-center gap-3 flex-1 max-w-[200px]">
          <Skeleton className="w-20 h-20 rounded-full" />
          <Skeleton className="h-6 w-32" />
        </div>

        {/* Placar */}
        <div className="flex flex-col items-center gap-2 min-w-[120px]">
          <div className="flex items-center gap-4">
            <Skeleton className="w-16 h-16" />
            <span className="text-3xl font-bold text-gray-400">-</span>
            <Skeleton className="w-16 h-16" />
          </div>
          <Skeleton className="h-4 w-24" />
        </div>

        {/* Time Visitante */}
        <div className="flex flex-col items-center gap-3 flex-1 max-w-[200px]">
          <Skeleton className="w-20 h-20 rounded-full" />
          <Skeleton className="h-6 w-32" />
        </div>
      </div>

      {/* Data */}
      <div className="text-center mb-4">
        <Skeleton className="h-4 w-48 mx-auto" />
      </div>
    </div>
  );
}

// Skeleton para análise estatística
export function AnalysisCardSkeleton() {
  return (
    <div className="card animate-pulse space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Skeleton className="w-6 h-6 rounded" />
        <Skeleton className="h-6 w-40" />
      </div>
      
      <div className="space-y-3">
        <Skeleton className="h-20 w-full rounded-lg" />
        <Skeleton className="h-20 w-full rounded-lg" />
        <Skeleton className="h-20 w-full rounded-lg" />
      </div>
    </div>
  );
}

// Skeleton para modal de análise
export function AnalysisModalSkeleton() {
  return (
    <div className="space-y-6 p-6 animate-pulse">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4 flex-1">
          <div className="flex-1 text-right">
            <Skeleton className="w-12 h-12 mx-auto mb-2 rounded-full" />
            <Skeleton className="h-4 w-20 mx-auto" />
          </div>
          <div className="text-center px-4">
            <Skeleton className="h-3 w-12 mx-auto mb-2" />
            <Skeleton className="h-3 w-16 mx-auto" />
          </div>
          <div className="flex-1 text-left">
            <Skeleton className="w-12 h-12 mx-auto mb-2 rounded-full" />
            <Skeleton className="h-4 w-20 mx-auto" />
          </div>
        </div>
      </div>

      {/* Probabilidades */}
      <div className="bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-4">
        <Skeleton className="h-5 w-32 mb-3" />
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center space-y-2">
            <Skeleton className="h-4 w-16 mx-auto" />
            <Skeleton className="h-8 w-20 mx-auto" />
          </div>
          <div className="text-center space-y-2">
            <Skeleton className="h-4 w-16 mx-auto" />
            <Skeleton className="h-8 w-20 mx-auto" />
          </div>
          <div className="text-center space-y-2">
            <Skeleton className="h-4 w-16 mx-auto" />
            <Skeleton className="h-8 w-20 mx-auto" />
          </div>
        </div>
      </div>

      {/* Confiança */}
      <div className="flex items-center justify-center gap-2">
        <Skeleton className="w-5 h-5 rounded" />
        <Skeleton className="h-6 w-32" />
      </div>

      {/* Top Bets */}
      <div className="space-y-3">
        <Skeleton className="h-5 w-32" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="bg-white dark:bg-gray-700 border-2 border-gray-200 dark:border-gray-600 rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2 flex-1">
                <Skeleton className="w-8 h-8 rounded" />
                <div className="flex-1">
                  <Skeleton className="h-5 w-full mb-2" />
                  <Skeleton className="h-4 w-3/4" />
                </div>
              </div>
              <div className="text-right">
                <Skeleton className="h-6 w-12 mb-1" />
                <Skeleton className="h-3 w-8" />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <Skeleton className="h-12 rounded" />
              <Skeleton className="h-12 rounded" />
              <Skeleton className="h-12 rounded" />
            </div>
          </div>
        ))}
      </div>

      {/* Análise IA */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg p-6">
        <Skeleton className="h-5 w-40 mb-4" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
        </div>
      </div>
    </div>
  );
}

// Skeleton para lista de partidas (página principal)
export function MatchListSkeleton({ count = 5 }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <MatchCardSkeleton key={i} />
      ))}
    </div>
  );
}

// Skeleton para seção de detalhes
export function DetailsSectionSkeleton() {
  return (
    <div className="card animate-pulse space-y-4">
      <Skeleton className="h-6 w-48 mb-4" />
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-24" />
        </div>
        <div className="flex justify-between items-center">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-24" />
        </div>
        <div className="flex justify-between items-center">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-24" />
        </div>
      </div>
    </div>
  );
}
