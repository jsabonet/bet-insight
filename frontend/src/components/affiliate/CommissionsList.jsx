import { CheckCircle2, Clock, AlertCircle } from 'lucide-react';

const STATUS_CONFIG = {
  pending: { label: 'Pendente', icon: Clock, cls: 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20' },
  available: { label: 'Disponível', icon: CheckCircle2, cls: 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20' },
  paid: { label: 'Pago', icon: CheckCircle2, cls: 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20' },
  reversed: { label: 'Revertido', icon: AlertCircle, cls: 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20' },
};

export default function CommissionsList({ commissions }) {
  if (!commissions || commissions.length === 0) {
    return (
      <div className="card animate-slide-up">
        <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-2">Últimas comissões</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Ainda não há comissões. Partilhe o seu link para começar a ganhar!
        </p>
      </div>
    );
  }

  return (
    <div className="card animate-slide-up">
      <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">Últimas comissões</h3>
      <div className="space-y-3">
        {commissions.map((c) => {
          const cfg = STATUS_CONFIG[c.status] || STATUS_CONFIG.pending;
          const Icon = cfg.icon;
          const date = c.created_at ? new Date(c.created_at).toLocaleDateString('pt-PT') : '';
          return (
            <div key={c.id} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`p-2 rounded-lg ${cfg.cls}`}>
                  <Icon className="w-4 h-4" />
                </span>
                <div>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">
                    +{Number(c.amount).toFixed(2)} MZN
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {c.plan || 'Plano'} · {date}
                  </p>
                </div>
              </div>
              <span className={`text-xs font-semibold px-2 py-1 rounded-full ${cfg.cls}`}>
                {cfg.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
