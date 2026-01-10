import { TrendingUp, TrendingDown, Shield, Target, Zap, Activity } from 'lucide-react';

/**
 * COMPARAÇÃO VISUAL DOS TIMES
 * Layout espelhado com barras horizontais comparativas
 * Dados vêm do Feature Engineering (backend)
 */
export default function TeamComparison({ analysis, match }) {
  console.log('🔍 TeamComparison - Verificando dados:', {
    hasAnalysis: !!analysis,
    hasAnalysisData: !!analysis?.analysis_data,
    hasFeaturesSummary: !!analysis?.analysis_data?.features_summary,
    featuresSummary: analysis?.analysis_data?.features_summary
  });

  if (!analysis?.analysis_data?.features_summary) {
    console.warn('⚠️ TeamComparison: features_summary não encontrado!');
    return null;
  }

  const { strength, form } = analysis.analysis_data.features_summary;
  
  console.log('📊 TeamComparison - Dados extraídos:', {
    strength,
    form
  });
  
  console.log('🔍 DETALHES STRENGTH:', JSON.stringify(strength, null, 2));
  console.log('🔍 DETALHES FORM:', JSON.stringify(form, null, 2));
  
  // Helper para normalizar valores para escala 0-100
  const normalize = (value, max = 3) => Math.min(Math.max((value / max) * 100, 0), 100);

  const metrics = [
    {
      label: 'Força Ofensiva',
      icon: Target,
      homeValue: strength?.home_goals_per_game || 0,
      awayValue: strength?.away_goals_per_game || 0,
      format: (v) => v.toFixed(2),
      max: 3
    },
    {
      label: 'Força Defensiva',
      icon: Shield,
      homeValue: strength?.home_conceded_per_game || 0,
      awayValue: strength?.away_conceded_per_game || 0,
      format: (v) => v.toFixed(2),
      max: 2,
      inverted: true // Menor é melhor para defesa
    },
    {
      label: 'Forma Recente',
      icon: TrendingUp,
      homeValue: form?.home_weighted_form || 0,
      awayValue: form?.away_weighted_form || 0,
      format: (v) => v.toFixed(1),
      max: 3
    },
    {
      label: 'Momentum',
      icon: Zap,
      homeValue: form?.home_momentum || 0,
      awayValue: form?.away_momentum || 0,
      format: (v) => v.toFixed(1),
      max: 3
    }
  ];

  const ComparisonBar = ({ metric }) => {
    const homeNorm = normalize(metric.homeValue, metric.max);
    const awayNorm = normalize(metric.awayValue, metric.max);
    
    const homeColor = metric.inverted
      ? homeNorm < 50 ? 'bg-green-500' : 'bg-red-500'
      : homeNorm > 50 ? 'bg-primary-500' : 'bg-gray-400';
    
    const awayColor = metric.inverted
      ? awayNorm < 50 ? 'bg-green-500' : 'bg-red-500'
      : awayNorm > 50 ? 'bg-blue-500' : 'bg-gray-400';

    return (
      <div className="space-y-2">
        {/* Label com ícone */}
        <div className="flex items-center justify-center gap-2">
          <metric.icon className="w-4 h-4 text-gray-600 dark:text-gray-400" />
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">{metric.label}</span>
        </div>

        {/* Barras comparativas */}
        <div className="grid grid-cols-[1fr_auto_1fr] gap-2 items-center">
          {/* Casa */}
          <div className="flex items-center justify-end gap-2">
            <span className="text-xs font-bold text-gray-900 dark:text-white whitespace-nowrap">
              {metric.format(metric.homeValue)}
            </span>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full ${homeColor} transition-all duration-500`}
                style={{ width: `${homeNorm}%` }}
              />
            </div>
          </div>

          {/* Separador */}
          <div className="w-px h-6 bg-gray-300 dark:bg-gray-600" />

          {/* Fora */}
          <div className="flex items-center gap-2">
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full ${awayColor} transition-all duration-500`}
                style={{ width: `${awayNorm}%` }}
              />
            </div>
            <span className="text-xs font-bold text-gray-900 dark:text-white whitespace-nowrap">
              {metric.format(metric.awayValue)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-4">
        <Activity className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Comparação de Times</h2>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
        {/* Headers dos times */}
        <div className="grid grid-cols-[1fr_auto_1fr] gap-2 mb-6">
          <div className="text-center">
            <div className="text-sm font-bold text-primary-600 dark:text-primary-400">
              {match.home_team?.name || match.home_team}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Casa</div>
          </div>
          <div className="w-px" />
          <div className="text-center">
            <div className="text-sm font-bold text-blue-600 dark:text-blue-400">
              {match.away_team?.name || match.away_team}
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">Fora</div>
          </div>
        </div>

        {/* Métricas */}
        <div className="space-y-6">
          {metrics.map((metric, index) => (
            <ComparisonBar key={index} metric={metric} />
          ))}
        </div>
      </div>
    </div>
  );
}
