import { useState } from 'react';
import { X, CreditCard, Loader2, XCircle, Gift } from 'lucide-react';
import api from '../services/api';
import { getAffiliateRef } from '../utils/affiliate';

export default function CheckoutModal({ plan, onClose }) {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [showPromo, setShowPromo] = useState(false);
  const [promoCode, setPromoCode] = useState(getAffiliateRef());

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setErrorMessage('');

    try {
      const body = { plan_slug: plan.slug };
      if (promoCode.trim()) {
        body.ref = promoCode.trim().toUpperCase();
      }
      const response = await api.post('/subscriptions/payments/vpay/create/', body);
      const checkoutUrl =
        response.data?.checkout_url ||
        response.data?.payment?.checkout_url ||
        response.data?.payment?.metadata?.checkout_url;
      const transactionId = response.data?.payment?.transaction_id;

      if (!checkoutUrl || !transactionId) {
        throw new Error('A VPay não devolveu os dados necessários para abrir o checkout.');
      }

      sessionStorage.setItem('vpay_pending_transaction', String(transactionId));
      window.location.assign(checkoutUrl);
    } catch (error) {
      setErrorMessage(
        error.response?.data?.error ||
        error.response?.data?.message ||
        error.message ||
        'Não foi possível iniciar o pagamento VPay. Tente novamente.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
      <div className="max-h-[90vh] w-full max-w-md overflow-y-auto rounded-2xl bg-white shadow-2xl dark:bg-gray-800">
        <div className="sticky top-0 flex items-center justify-between border-b border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Finalizar Assinatura
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">{plan.name}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={loading}
            aria-label="Fechar"
            className="rounded-lg p-2 transition-colors hover:bg-gray-100 disabled:opacity-50 dark:hover:bg-gray-700"
          >
            <X className="h-6 w-6 text-gray-600 dark:text-gray-400" />
          </button>
        </div>

        <div className="p-6">
          {errorMessage && (
            <div className="mb-6 rounded-xl border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-900/20">
              <div className="mb-2 flex items-center gap-3">
                <XCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
                <h3 className="font-bold text-red-900 dark:text-red-100">
                  Erro no pagamento
                </h3>
              </div>
              <p className="text-sm text-red-700 dark:text-red-300">{errorMessage}</p>
            </div>
          )}

          <div className="mb-6 rounded-xl border border-primary-200 bg-gradient-to-r from-primary-50 to-blue-50 p-4 dark:border-primary-800 dark:from-primary-900/20 dark:to-blue-900/20">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Plano:</span>
              <span className="font-bold text-gray-900 dark:text-gray-100">{plan.name}</span>
            </div>
            <div className="mb-2 flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Análises diárias:</span>
              <span className="font-bold text-primary-600 dark:text-primary-400">
                {plan.daily_analysis_limit}
              </span>
            </div>
            <div className="mb-2 flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Duração:</span>
              <span className="font-bold text-gray-900 dark:text-gray-100">
                {plan.duration_days} dias
              </span>
            </div>
            <div className="mt-2 flex items-center justify-between border-t border-primary-200 pt-2 dark:border-primary-700">
              <span className="text-lg font-bold text-gray-900 dark:text-gray-100">Total:</span>
              <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                {plan.price.toLocaleString()} MZN
              </span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="rounded-xl border-2 border-violet-600 bg-violet-50 p-4 ring-2 ring-violet-200 dark:border-violet-500 dark:bg-violet-900/20">
              <div className="flex flex-col items-center justify-center gap-2">
                <span className="rounded bg-violet-700 px-5 py-2 text-lg font-bold text-white">
                  VPay
                </span>
                <span className="text-xs text-gray-600 dark:text-gray-400">
                  Carteira móvel, cartão, PayPal ou QR Code
                </span>
              </div>
            </div>

            {/* Código de indicação (opcional) */}
            <div>
              <button
                type="button"
                onClick={() => setShowPromo(!showPromo)}
                className="flex items-center gap-2 text-sm font-medium text-primary-600 dark:text-primary-400 hover:underline"
              >
                <Gift className="w-4 h-4" />
                Tem um código de indicação?
              </button>
              {showPromo && (
                <input
                  type="text"
                  value={promoCode}
                  onChange={(e) => setPromoCode(e.target.value)}
                  className="input-field uppercase mt-2"
                  placeholder="Ex: JOAO123"
                />
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-primary-600 to-primary-700 py-4 font-bold text-white shadow-lg transition-all hover:from-primary-700 hover:to-primary-800 disabled:cursor-not-allowed disabled:opacity-50 dark:from-primary-500 dark:to-primary-600"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  A criar pedido VPay...
                </>
              ) : (
                <>
                  <CreditCard className="h-5 w-5" />
                  Continuar para Checkout VPay
                </>
              )}
            </button>
          </form>

          <div className="mt-4 rounded-lg bg-gray-50 p-3 dark:bg-gray-700/50">
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Pagamento seguro via checkout hospedado VPay. O estado só será confirmado
              após validação do servidor VPay.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
