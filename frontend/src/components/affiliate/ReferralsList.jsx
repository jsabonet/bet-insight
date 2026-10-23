import { UserPlus, CheckCircle2 } from 'lucide-react';

export default function ReferralsList({ referrals }) {
  if (!referrals || referrals.length === 0) {
    return (
      <div className="card animate-slide-up">
        <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-2">Indicações recentes</h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Ainda não há contas criadas com o seu link. Partilhe-o para começar!
        </p>
      </div>
    );
  }

  return (
    <div className="card animate-slide-up">
      <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">Indicações recentes</h3>
      <div className="space-y-3">
        {referrals.map((r) => {
          const date = r.first_touch_at
            ? new Date(r.first_touch_at).toLocaleDateString('pt-PT')
            : '';
          return (
            <div key={r.id} className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`p-2 rounded-lg ${r.converted ? 'bg-green-50 dark:bg-green-900/20' : 'bg-blue-50 dark:bg-blue-900/20'}`}>
                  {r.converted
                    ? <CheckCircle2 className="w-4 h-4 text-green-600 dark:text-green-400" />
                    : <UserPlus className="w-4 h-4 text-blue-600 dark:text-blue-400" />}
                </span>
                <div>
                  <p className="font-semibold text-gray-900 dark:text-gray-100">
                    {r.user_name || r.user_email}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {r.source_display || 'Link'} · {date}
                  </p>
                </div>
              </div>
              <span className={`text-xs font-semibold px-2 py-1 rounded-full ${r.converted ? 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20' : 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'}`}>
                {r.converted ? 'Convertido' : 'Registado'}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
