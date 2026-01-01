import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, CheckCircle, XCircle, Clock, ArrowLeft } from 'lucide-react';
import api from '../services/api';

export default function PaymentConfirmation() {
  const { transactionId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('checking'); // checking, success, failed, pending
  const [payment, setPayment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [attempts, setAttempts] = useState(0);
  const maxAttempts = 120; // 10 minutos (120 * 5s)

  useEffect(() => {
    if (!transactionId) {
      navigate('/premium');
      return;
    }

    checkPaymentStatus();
    const interval = setInterval(checkPaymentStatus, 5000); // Check a cada 5 segundos

    return () => clearInterval(interval);
  }, [transactionId, attempts]);

  const checkPaymentStatus = async () => {
    if (attempts >= maxAttempts) {
      setStatus('timeout');
      setLoading(false);
      return;
    }

    try {
      const response = await api.get(`/subscriptions/payments/check/${transactionId}/`);
      const paymentData = response.data;
      
      setPayment(paymentData);

      if (paymentData.status === 'completed') {
        setStatus('success');
        setLoading(false);
      } else if (paymentData.status === 'failed') {
        setStatus('failed');
        setLoading(false);
      } else {
        setStatus('pending');
        setAttempts(prev => prev + 1);
      }
    } catch (error) {
      console.error('Erro ao verificar status:', error);
      setAttempts(prev => prev + 1);
    }
  };

  const handleBackToPremium = () => {
    navigate('/premium');
  };

  const handleRetry = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 pt-20 pb-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            Status do Pagamento
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            ID: {transactionId}
          </p>
        </div>

        {/* Status Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
          {/* Success */}
          {status === 'success' && (
            <div className="p-8">
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full mb-4">
                  <CheckCircle className="w-12 h-12 text-green-600 dark:text-green-400" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  Pagamento Confirmado!
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Sua assinatura foi ativada com sucesso
                </p>
              </div>

              {payment && (
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 mb-6 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Plano:</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                      {payment.metadata?.plan_name || 'Premium'}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Valor:</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                      {payment.amount?.toLocaleString()} MZN
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Método:</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100 uppercase">
                      {payment.payment_method}
                    </span>
                  </div>
                </div>
              )}

              <button
                onClick={handleBackToPremium}
                className="w-full py-4 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-bold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all shadow-lg hover:shadow-xl"
              >
                Voltar para Premium
              </button>
            </div>
          )}

          {/* Failed */}
          {status === 'failed' && (
            <div className="p-8">
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 dark:bg-red-900/30 rounded-full mb-4">
                  <XCircle className="w-12 h-12 text-red-600 dark:text-red-400" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  Pagamento Falhou
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  O pagamento não foi confirmado
                </p>
              </div>

              {payment?.error_message && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-6">
                  <p className="text-sm text-red-700 dark:text-red-300">
                    {payment.error_message}
                  </p>
                </div>
              )}

              <div className="space-y-3">
                <button
                  onClick={handleBackToPremium}
                  className="w-full py-4 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-bold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all shadow-lg hover:shadow-xl"
                >
                  Tentar Novamente
                </button>
                <button
                  onClick={handleBackToPremium}
                  className="w-full py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  <ArrowLeft className="w-4 h-4 inline mr-2" />
                  Voltar
                </button>
              </div>
            </div>
          )}

          {/* Pending/Checking */}
          {(status === 'pending' || status === 'checking') && (
            <div className="p-8">
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-4">
                  <Loader2 className="w-12 h-12 text-blue-600 dark:text-blue-400 animate-spin" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  Aguardando Confirmação...
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Verificando o status do seu pagamento
                </p>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6 mb-6">
                <div className="flex items-start gap-3 mb-4">
                  <Clock className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-bold text-blue-900 dark:text-blue-100 mb-2">
                      O que fazer agora?
                    </h3>
                    <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1 list-disc list-inside">
                      <li>Verifique se recebeu a notificação no seu telefone</li>
                      <li>Confirme o pagamento inserindo o PIN</li>
                      <li>Aguarde alguns instantes para a confirmação</li>
                    </ul>
                  </div>
                </div>
                <div className="text-center pt-4 border-t border-blue-200 dark:border-blue-700">
                  <p className="text-xs text-blue-700 dark:text-blue-300">
                    Esta página será atualizada automaticamente quando o pagamento for confirmado
                  </p>
                </div>
              </div>

              {payment && (
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 mb-6 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Valor:</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                      {payment.amount?.toLocaleString()} MZN
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Método:</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100 uppercase">
                      {payment.payment_method}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Tentativas:</span>
                    <span className="font-medium text-gray-900 dark:text-gray-100">
                      {attempts} / {maxAttempts}
                    </span>
                  </div>
                </div>
              )}

              <button
                onClick={handleBackToPremium}
                className="w-full py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                <ArrowLeft className="w-4 h-4 inline mr-2" />
                Voltar (e verificar depois)
              </button>
            </div>
          )}

          {/* Timeout */}
          {status === 'timeout' && (
            <div className="p-8">
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-yellow-100 dark:bg-yellow-900/30 rounded-full mb-4">
                  <Clock className="w-12 h-12 text-yellow-600 dark:text-yellow-400" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                  Tempo Esgotado
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Não conseguimos confirmar o pagamento
                </p>
              </div>

              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4 mb-6">
                <p className="text-sm text-yellow-800 dark:text-yellow-200">
                  O pagamento pode ter sido processado. Verifique suas assinaturas ou entre em contato com o suporte.
                </p>
              </div>

              <div className="space-y-3">
                <button
                  onClick={handleRetry}
                  className="w-full py-4 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-bold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all shadow-lg hover:shadow-xl"
                >
                  Verificar Novamente
                </button>
                <button
                  onClick={handleBackToPremium}
                  className="w-full py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  <ArrowLeft className="w-4 h-4 inline mr-2" />
                  Voltar
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Info */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Problemas? Entre em contato: <a href="mailto:suporte@placarcerto.co.mz" className="text-primary-600 dark:text-primary-400 hover:underline">suporte@placarcerto.co.mz</a>
          </p>
        </div>
      </div>
    </div>
  );
}
