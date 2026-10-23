import { Wallet, Clock, ArrowUpRight } from 'lucide-react';

export default function BalanceCard({ available, pending, onWithdraw }) {
  const fmt = (v) => Number(v || 0).toLocaleString('pt-PT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  return (
    <div className="card animate-slide-up bg-gradient-to-br from-primary-600 to-primary-800 dark:from-primary-900 dark:to-gray-900 text-white border-0">
      <div className="flex items-center gap-2 mb-4">
        <Wallet className="w-5 h-5 text-white/80" />
        <h3 className="font-bold text-white">Saldo Disponível</h3>
      </div>
      <p className="text-4xl font-bold mb-2">{fmt(available)} MZN</p>

      <div className="flex items-center gap-2 mb-4">
        <Clock className="w-4 h-4 text-white/70" />
        <span className="text-sm text-white/80">
          Pendente: {fmt(pending)} MZN <span className="text-white/50">(libera em até 14 dias)</span>
        </span>
      </div>

      <button
        onClick={onWithdraw}
        className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-white text-primary-700 font-bold hover:bg-primary-50 transition-all"
      >
        <ArrowUpRight className="w-5 h-5" />
        Levantar
      </button>
    </div>
  );
}
