import { MousePointerClick, Users, TrendingUp } from 'lucide-react';

export default function AffiliateStatsCard({ stats }) {
  const fmt = (v) => Number(v || 0).toLocaleString('pt-PT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  const metrics = [
    { icon: MousePointerClick, label: 'Cliques (30d)', value: stats?.clicks_30d ?? 0, color: 'text-blue-600 dark:text-blue-400' },
    { icon: Users, label: 'Conversões (30d)', value: stats?.conversions_30d ?? 0, color: 'text-green-600 dark:text-green-400' },
    { icon: TrendingUp, label: 'Receita (30d)', value: `${fmt(stats?.revenue_30d)} MZN`, color: 'text-primary-600 dark:text-primary-400' },
  ];

  return (
    <div className="card animate-slide-up">
      <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">Desempenho (últimos 30 dias)</h3>

      <div className="grid grid-cols-3 gap-3">
        {metrics.map((m) => (
          <div key={m.label} className="text-center">
            <m.icon className={`w-5 h-5 mx-auto mb-1 ${m.color}`} />
            <p className="text-lg font-bold text-gray-900 dark:text-gray-100">{m.value}</p>
            <p className="text-[11px] text-gray-500 dark:text-gray-400">{m.label}</p>
          </div>
        ))}
      </div>

      {/* Mini gráfico de barras (7 dias) */}
      {stats?.daily && stats.daily.length > 0 && (
        <div className="mt-5 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Cliques nos últimos 7 dias</p>
          <div className="flex items-end gap-1 h-20">
            {stats.daily.map((d, i) => {
              const max = Math.max(...stats.daily.map((x) => x.clicks), 1);
              const h = Math.max((d.clicks / max) * 100, 4);
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <span className="text-[10px] text-gray-500 dark:text-gray-400">{d.clicks}</span>
                  <div
                    className="w-full rounded-t-md bg-primary-500 dark:bg-primary-400"
                    style={{ height: `${h}%` }}
                  />
                  <span className="text-[9px] text-gray-400 dark:text-gray-500">
                    {new Date(d.date).getDate()}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
