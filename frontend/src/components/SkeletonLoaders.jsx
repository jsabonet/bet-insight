/**
 * Skeleton Loaders para Progressive Loading
 * Componentes de loading state modernos e animados
 */

export const SkeletonCard = ({ className = '' }) => (
  <div className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded-lg ${className}`} />
);

export const SkeletonText = ({ lines = 3, className = '' }) => (
  <div className={`space-y-2 ${className}`}>
    {Array.from({ length: lines }).map((_, i) => (
      <div
        key={i}
        className="animate-pulse bg-gray-200 dark:bg-gray-700 rounded h-4"
        style={{ width: i === lines - 1 ? '75%' : '100%' }}
      />
    ))}
  </div>
);

export const SkeletonBetCard = () => (
  <div className="bg-white dark:bg-gray-700 border-2 border-gray-200 dark:border-gray-600 rounded-lg p-4 space-y-3 animate-pulse">
    <div className="flex items-start justify-between">
      <div className="flex items-center gap-2 flex-1">
        <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded-full" />
        <div className="space-y-2 flex-1">
          <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4" />
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2" />
        </div>
      </div>
      <div className="space-y-1">
        <div className="h-6 w-16 bg-gray-300 dark:bg-gray-600 rounded" />
        <div className="h-3 w-12 bg-gray-200 dark:bg-gray-700 rounded ml-auto" />
      </div>
    </div>
    <div className="grid grid-cols-3 gap-2">
      <div className="h-12 bg-blue-100 dark:bg-blue-900/20 rounded" />
      <div className="h-12 bg-green-100 dark:bg-green-900/20 rounded" />
      <div className="h-12 bg-purple-100 dark:bg-purple-900/20 rounded" />
    </div>
    <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full" />
  </div>
);

export const SkeletonAnalysis = () => (
  <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg p-6 space-y-4 animate-pulse">
    <div className="flex items-center gap-2">
      <div className="w-5 h-5 bg-purple-300 dark:bg-purple-700 rounded" />
      <div className="h-4 w-32 bg-purple-300 dark:bg-purple-700 rounded" />
    </div>
    <div className="space-y-3">
      <div className="h-4 bg-purple-200 dark:bg-purple-800/50 rounded w-full" />
      <div className="h-4 bg-purple-200 dark:bg-purple-800/50 rounded w-11/12" />
      <div className="h-4 bg-purple-200 dark:bg-purple-800/50 rounded w-10/12" />
      <div className="h-4 bg-purple-200 dark:bg-purple-800/50 rounded w-full" />
      <div className="h-4 bg-purple-200 dark:bg-purple-800/50 rounded w-9/12" />
      <div className="h-4 bg-purple-200 dark:bg-purple-800/50 rounded w-11/12" />
      <div className="h-4 bg-purple-200 dark:bg-purple-800/50 rounded w-3/4" />
    </div>
  </div>
);

export const SkeletonMatchDetail = () => (
  <div className="space-y-6 animate-pulse">
    {/* Header */}
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-4 flex-1">
        <div className="w-12 h-12 bg-gray-300 dark:bg-gray-600 rounded-full" />
        <div className="text-center space-y-2">
          <div className="w-8 h-4 bg-gray-200 dark:bg-gray-700 rounded mx-auto" />
          <div className="w-20 h-3 bg-gray-200 dark:bg-gray-700 rounded mx-auto" />
        </div>
        <div className="w-12 h-12 bg-gray-300 dark:bg-gray-600 rounded-full" />
      </div>
    </div>

    {/* Probabilities */}
    <div className="bg-gradient-to-br from-purple-100 to-blue-100 dark:from-purple-900/20 dark:to-blue-900/20 rounded-lg p-4">
      <div className="h-4 w-32 bg-purple-300 dark:bg-purple-700 rounded mb-3" />
      <div className="grid grid-cols-3 gap-3">
        {[1, 2, 3].map(i => (
          <div key={i} className="text-center space-y-2">
            <div className="h-3 w-16 bg-purple-200 dark:bg-purple-800 rounded mx-auto" />
            <div className="h-8 w-20 bg-purple-300 dark:bg-purple-700 rounded mx-auto" />
          </div>
        ))}
      </div>
    </div>

    {/* Confidence */}
    <div className="flex items-center justify-center gap-2">
      <div className="w-5 h-5 bg-yellow-300 rounded" />
      <div className="h-5 w-32 bg-gray-300 dark:bg-gray-600 rounded" />
    </div>
  </div>
);

export const SkeletonTopBets = () => (
  <div className="space-y-3">
    <div className="flex items-center gap-2">
      <div className="w-4 h-4 bg-purple-300 dark:bg-purple-700 rounded" />
      <div className="h-4 w-24 bg-purple-300 dark:bg-purple-700 rounded" />
    </div>
    {[1, 2, 3].map(i => (
      <SkeletonBetCard key={i} />
    ))}
  </div>
);

export const LoadingPhase = ({ phase, message, submessage, icon: Icon, color = 'purple' }) => {
  const colorClasses = {
    purple: 'text-purple-600 dark:text-purple-400',
    blue: 'text-blue-600 dark:text-blue-400',
    green: 'text-green-600 dark:text-green-400'
  };

  return (
    <div className="text-center space-y-4 py-8 animate-fade-in">
      <Icon className={`w-12 h-12 ${colorClasses[color]} animate-pulse mx-auto`} />
      <div className="space-y-2">
        <p className="text-lg font-semibold text-gray-900 dark:text-white">
          {message}
        </p>
        {submessage && (
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {submessage}
          </p>
        )}
      </div>
      <div className="flex items-center justify-center gap-2">
        {[1, 2, 3].map(i => (
          <div
            key={i}
            className={`w-2 h-2 rounded-full ${
              i <= phase ? 'bg-purple-600 dark:bg-purple-400' : 'bg-gray-300 dark:bg-gray-600'
            }`}
          />
        ))}
      </div>
    </div>
  );
};
