import { useState } from 'react';
import { X, Wallet, Loader2 } from 'lucide-react';
import { affiliateAPI } from '../../services/api';

export default function WithdrawModal({ availableBalance, onClose, onDone }) {
  const [amount, setAmount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await affiliateAPI.withdraw(Number(amount));
      setSuccess(true);
      setTimeout(() => onDone?.(), 1500);
    } catch (err) {
      setError(err.response?.data?.error || 'Não foi possível processar o pedido.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-white shadow-2xl dark:bg-gray-800">
        <div className="flex items-center justify-between border-b border-gray-200 p-6 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">Levantar Saldo</h2>
          <button onClick={onClose} aria-label="Fechar" className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-700">
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        <div className="p-6">
          {success ? (
            <div className="text-center py-6">
              <Wallet className="w-12 h-12 text-green-500 mx-auto mb-3" />
              <p className="font-semibold text-gray-900 dark:text-gray-100">Pedido registado!</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                O pedido ficou registado e o valor foi reservado. Pode acompanhar o estado no seu painel.
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  Saldo disponível: <span className="font-bold">{Number(availableBalance).toFixed(2)} MZN</span>
                </p>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Valor (MZN)
                </label>
                <input
                  type="number"
                  min="200"
                  step="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="input-field"
                  placeholder="Ex: 200"
                  required
                />
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Valor mínimo: 200 MZN</p>
              </div>

              {error && (
                <div className="rounded-lg bg-red-50 border border-red-200 text-red-700 px-3 py-2 text-sm dark:bg-red-900/20 dark:border-red-800">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary-600 py-3 font-bold text-white transition-all hover:bg-primary-700 disabled:opacity-50"
              >
                {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Wallet className="h-5 w-5" />}
                {loading ? 'A processar...' : 'Confirmar Levantamento'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
