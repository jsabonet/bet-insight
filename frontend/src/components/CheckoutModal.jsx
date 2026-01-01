import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, CreditCard, Loader2, CheckCircle, XCircle, Clock, RefreshCw } from 'lucide-react';
import api from '../services/api';

// Logo M-Pesa (Vodacom)
const MPesaLogo = () => (
  <svg viewBox="0 0 120 40" className="h-8 w-auto">
    <rect width="120" height="40" fill="#E60000" rx="4"/>
    <text x="60" y="25" fontFamily="Arial, sans-serif" fontSize="18" fontWeight="bold" fill="white" textAnchor="middle">
      M-Pesa
    </text>
  </svg>
);

// Logo e-Mola (Movitel)
const EMolaLogo = () => (
  <svg viewBox="0 0 120 40" className="h-8 w-auto">
    <rect width="120" height="40" fill="#00A651" rx="4"/>
    <text x="60" y="25" fontFamily="Arial, sans-serif" fontSize="18" fontWeight="bold" fill="white" textAnchor="middle">
      e-Mola
    </text>
  </svg>
);

export default function CheckoutModal({ plan, onClose, onSuccess }) {
  const navigate = useNavigate();
  const [paymentMethod, setPaymentMethod] = useState('mpesa');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('form'); // 'form', 'created', 'tracking'
  const [transactionId, setTransactionId] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [checkoutUrl, setCheckoutUrl] = useState('');
  const [paymentStatus, setPaymentStatus] = useState('pending'); // 'pending', 'completed', 'failed'
  const [paymentData, setPaymentData] = useState(null);
  const [pollingAttempts, setPollingAttempts] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(120); // 120 segundos = 2 minutos

  // Countdown timer para mostrar tempo restante - INICIA QUANDO LINK É GERADO
  useEffect(() => {
    // Iniciar contagem quando pagamento é criado (step === 'created' ou 'tracking') e está pendente
    if ((step === 'created' || step === 'tracking') && paymentStatus === 'pending' && timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining(prev => {
          if (prev <= 1) {
            // Tempo esgotado - marcar como falho
            markPaymentAsFailed();
            return 0;
          }
          return prev - 1;
        });
      }, 1000); // Atualizar a cada 1 segundo

      return () => clearInterval(timer);
    }
  }, [step, paymentStatus, timeRemaining]);

  // Polling para verificar status do pagamento - INICIA QUANDO LINK É GERADO
  useEffect(() => {
    // Iniciar polling quando pagamento é criado (mesmo antes de clicar em "Confirmar Pagamento")
    if ((step === 'created' || step === 'tracking') && transactionId && paymentStatus === 'pending') {
      const interval = setInterval(() => {
        checkPaymentStatus();
      }, 1000); // Verificar a cada 1 SEGUNDO (conforme solicitado)

      return () => clearInterval(interval);
    }
  }, [step, transactionId, paymentStatus, pollingAttempts]);

  const markPaymentAsFailed = async () => {
    console.log('⏰ Timeout de 2 minutos atingido - marcando pagamento como falho');
    setPaymentStatus('failed');
    
    // Opcionalmente, notificar o backend para marcar como falho
    try {
      await api.post(`/subscriptions/payments/${transactionId}/mark-failed/`, {
        reason: 'Timeout de 2 minutos - pagamento não confirmado'
      });
    } catch (error) {
      console.error('Erro ao marcar pagamento como falho:', error);
    }
  };

  const checkPaymentStatus = async () => {
    // Limitar verificações a 120 tentativas (1 por segundo por 2 minutos)
    if (pollingAttempts >= 120) {
      console.log('❌ Máximo de tentativas atingido (120 tentativas = 2 minutos)');
      markPaymentAsFailed();
      return;
    }

    try {
      const response = await api.get(`/subscriptions/payments/check/${transactionId}/`);
      const payment = response.data;
      
      console.log(`🔄 Verificação ${pollingAttempts + 1}/120 - Status: ${payment.status}`);
      setPaymentData(payment);
      setPollingAttempts(prev => prev + 1);

      if (payment.status === 'completed') {
        console.log('✅ Pagamento confirmado pelo polling!');
        setPaymentStatus('completed');
        setTimeout(() => {
          if (onSuccess) onSuccess();
          onClose();
        }, 3000); // Fechar após 3 segundos
      } else if (payment.status === 'failed') {
        console.log('❌ Pagamento falhou');
        setPaymentStatus('failed');
      }
    } catch (error) {
      console.error('Erro ao verificar status:', error);
      setPollingAttempts(prev => prev + 1);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage('');

    try {
      const payload = {
        plan_slug: plan.slug,
        payment_method: paymentMethod,
      };
      
      console.log('=== CRIANDO PAGAMENTO ===');
      console.log('Plan completo:', plan);
      console.log('Payload enviado:', payload);
      
      // Criar pagamento sem telefone
      const response = await api.post('/subscriptions/payments/create/', payload);

      console.log('=== RESPOSTA DO BACKEND ===');
      console.log('Resposta completa:', response.data);
      
      const { payment } = response.data;
      const txId = payment?.transaction_id;
      
      // Tentar múltiplos caminhos para checkout_url
      const checkoutUrlLocal = 
        payment?.metadata?.checkout_url || 
        payment?.metadata?.paysuite_response?.data?.checkout_url ||
        payment?.checkout_url ||
        response.data?.checkout_url;

      console.log('Transaction ID:', txId);
      console.log('Checkout URL encontrado:', checkoutUrlLocal);
      console.log('Payment metadata:', payment?.metadata);

      if (!txId) {
        console.error('Transaction ID ausente na resposta:', response.data);
        setErrorMessage('Falha ao iniciar pagamento: ID indisponível.');
        return;
      }

      if (!checkoutUrlLocal) {
        console.warn('Checkout URL não encontrado na resposta');
      }

      setTransactionId(txId);
      setCheckoutUrl(checkoutUrlLocal || '');
      setStep('created');

    } catch (error) {
      console.error('=== ERRO AO CRIAR PAGAMENTO ===');
      console.error('Erro completo:', error);
      console.error('Resposta do erro:', error.response?.data);
      console.error('Status do erro:', error.response?.status);
      console.error('Headers do erro:', error.response?.headers);
      
      setErrorMessage(
        error.response?.data?.error || 
        error.response?.data?.message ||
        `Erro ${error.response?.status}: ${JSON.stringify(error.response?.data)}` ||
        'Erro ao processar pagamento. Tente novamente.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-md w-full max-h-[90vh] overflow-y-auto shadow-2xl animate-scale-up">
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
              Finalizar Assinatura
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {plan.name}
            </p>
          </div>
          <button
            onClick={onClose}
            disabled={loading}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-gray-600 dark:text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* ESTADO 1: Formulário Inicial */}
          {step === 'form' && (
            <>
              {/* Status de Erro */}
              {errorMessage && (
                <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
                  <div className="flex items-center gap-3 mb-2">
                    <XCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
                    <h3 className="font-bold text-red-900 dark:text-red-100">
                      Erro no pagamento
                    </h3>
                  </div>
                  <p className="text-sm text-red-700 dark:text-red-300">
                    {errorMessage}
                  </p>
                </div>
              )}

              {/* Detalhes do Plano */}
              <div className="mb-6 p-4 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-xl border border-primary-200 dark:border-primary-800">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600 dark:text-gray-400">Plano:</span>
                  <span className="font-bold text-gray-900 dark:text-gray-100">{plan.name}</span>
                </div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600 dark:text-gray-400">Análises diárias:</span>
                  <span className="font-bold text-primary-600 dark:text-primary-400">
                    {plan.daily_analysis_limit}
                  </span>
                </div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-600 dark:text-gray-400">Duração:</span>
                  <span className="font-bold text-gray-900 dark:text-gray-100">
                    {plan.duration_days} dias
                  </span>
                </div>
                <div className="pt-2 mt-2 border-t border-primary-200 dark:border-primary-700">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-bold text-gray-900 dark:text-gray-100">Total:</span>
                    <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                      {plan.price.toLocaleString()} MZN
                    </span>
                  </div>
                </div>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Método de Pagamento */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Método de Pagamento
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    <button
                      type="button"
                      onClick={() => setPaymentMethod('mpesa')}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        paymentMethod === 'mpesa'
                          ? 'border-red-600 dark:border-red-500 bg-red-50 dark:bg-red-900/20 ring-2 ring-red-200'
                          : 'border-gray-200 dark:border-gray-700 hover:border-red-300 dark:hover:border-red-700'
                      }`}
                    >
                      <div className="flex flex-col items-center justify-center gap-2">
                        <MPesaLogo />
                        <div className="text-xs text-gray-600 dark:text-gray-400">Vodacom</div>
                      </div>
                    </button>
                    <button
                      type="button"
                      onClick={() => setPaymentMethod('emola')}
                      className={`p-4 rounded-xl border-2 transition-all ${
                        paymentMethod === 'emola'
                          ? 'border-green-600 dark:border-green-500 bg-green-50 dark:bg-green-900/20 ring-2 ring-green-200'
                          : 'border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-700'
                      }`}
                    >
                      <div className="flex flex-col items-center justify-center gap-2">
                        <EMolaLogo />
                        <div className="text-xs text-gray-600 dark:text-gray-400">Movitel</div>
                      </div>
                    </button>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-4 bg-gradient-to-r from-primary-600 to-primary-700 dark:from-primary-500 dark:to-primary-600 text-white font-bold rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Criando pedido...
                    </>
                  ) : (
                    <>
                      <CreditCard className="w-5 h-5" />
                      Criar Pedido de Pagamento
                    </>
                  )}
                </button>
              </form>

              {/* Info */}
              <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  🔒 <strong>Pagamento seguro via PaySuite.</strong> Após criar o pedido, você poderá finalizar e acompanhar o pagamento.
                </p>
              </div>
            </>
          )}

          {/* ESTADO 2: Pedido Criado */}
          {step === 'created' && (
            <div className="space-y-4">
              <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
                <div className="flex items-center gap-3 mb-3">
                  <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400" />
                  <div>
                    <h3 className="font-bold text-green-900 dark:text-green-100">
                      Pedido criado com sucesso!
                    </h3>
                    <p className="text-sm text-green-700 dark:text-green-300">
                      ID: {transactionId}
                    </p>
                  </div>
                </div>
                {checkoutUrl && (
                  <>
                    <p className="text-sm text-green-800 dark:text-green-200 mb-3">
                      Clique no botão abaixo para finalizar o pagamento na página segura da PaySuite.
                    </p>
                    <a
                      href={checkoutUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block w-full py-4 bg-gradient-to-r from-green-600 to-green-700 text-white font-bold rounded-xl hover:from-green-700 hover:to-green-800 transition-all shadow-lg hover:shadow-xl text-center mb-3"
                    >
                      🔗 Abrir Página de Pagamento
                    </a>
                  </>
                )}
              </div>
              
              {checkoutUrl && (
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl">
                  <h4 className="font-bold text-blue-900 dark:text-blue-100 mb-2">
                    📱 Próximos passos:
                  </h4>
                  <ol className="text-sm text-blue-800 dark:text-blue-200 space-y-1 list-decimal list-inside">
                    <li>Clique no botão verde acima</li>
                    <li>Digite seu número ({paymentMethod === 'mpesa' ? 'M-Pesa' : 'e-Mola'})</li>
                    <li>Confirme no seu telefone</li>
                  </ol>
                </div>
              )}

              <button
                onClick={() => setStep('tracking')}
                className="w-full py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all shadow-lg flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-5 h-5" />
                Acompanhar Status do Pagamento
              </button>

              <button
                onClick={onClose}
                className="w-full py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Fechar
              </button>
            </div>
          )}

          {/* ESTADO 3: Acompanhamento de Status */}
          {step === 'tracking' && (
            <div className="space-y-4">
              {/* Pagamento Confirmado */}
              {paymentStatus === 'completed' && (
                <div className="p-6 text-center">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full mb-4">
                    <CheckCircle className="w-12 h-12 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    Pagamento Confirmado!
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Sua assinatura foi ativada com sucesso
                  </p>
                  {paymentData && (
                    <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 mb-4 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">Plano:</span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">{plan.name}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">Valor:</span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">{plan.price.toLocaleString()} MZN</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Pagamento Falhou */}
              {paymentStatus === 'failed' && (
                <div className="p-6 text-center">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 dark:bg-red-900/30 rounded-full mb-4">
                    <XCircle className="w-12 h-12 text-red-600 dark:text-red-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    Pagamento Não Confirmado
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    O pagamento não foi confirmado dentro do prazo de 2 minutos
                  </p>
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-4">
                    <p className="text-sm text-red-800 dark:text-red-200">
                      Se você já realizou o pagamento, aguarde alguns minutos e verifique suas assinaturas. 
                      Caso contrário, tente novamente.
                    </p>
                  </div>
                  <button
                    onClick={() => { 
                      setStep('form'); 
                      setErrorMessage(''); 
                      setTimeRemaining(120);
                      setPollingAttempts(0);
                      setPaymentStatus('pending');
                    }}
                    className="w-full py-4 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-bold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all mb-2"
                  >
                    Tentar Novamente
                  </button>
                </div>
              )}

              {/* Aguardando Confirmação */}
              {paymentStatus === 'pending' && (
                <div className="p-6 text-center">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-blue-100 dark:bg-blue-900/30 rounded-full mb-4">
                    <Loader2 className="w-12 h-12 text-blue-600 dark:text-blue-400 animate-spin" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    Aguardando Confirmação...
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-2">
                    Verificando status do seu pagamento
                  </p>
                  
                  {/* Timer de Contagem Regressiva */}
                  <div className={`inline-flex items-center justify-center px-6 py-3 rounded-xl mb-4 ${
                    timeRemaining <= 30 
                      ? 'bg-red-100 dark:bg-red-900/30 border-2 border-red-300 dark:border-red-700' 
                      : 'bg-blue-100 dark:bg-blue-900/30 border-2 border-blue-300 dark:border-blue-700'
                  }`}>
                    <Clock className={`w-6 h-6 mr-2 ${
                      timeRemaining <= 30 ? 'text-red-600 dark:text-red-400' : 'text-blue-600 dark:text-blue-400'
                    }`} />
                    <span className={`text-2xl font-bold ${
                      timeRemaining <= 30 ? 'text-red-700 dark:text-red-300' : 'text-blue-700 dark:text-blue-300'
                    }`}>
                      {formatTime(timeRemaining)}
                    </span>
                  </div>
                  
                  {timeRemaining <= 30 && (
                    <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-3 mb-4">
                      <p className="text-sm text-yellow-800 dark:text-yellow-200 font-medium">
                        ⚠️ Menos de 30 segundos restantes! Confirme rapidamente no seu telefone.
                      </p>
                    </div>
                  )}
                  
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-xl p-6 mb-4">
                    <div className="flex items-start gap-3">
                      <Clock className="w-6 h-6 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                      <div className="text-left">
                        <h4 className="font-bold text-blue-900 dark:text-blue-100 mb-2">
                          O que fazer agora?
                        </h4>
                        <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-1 list-disc list-inside">
                          <li>Verifique a notificação no telefone</li>
                          <li>Confirme o pagamento com seu PIN</li>
                          <li>Aguarde alguns instantes</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-4 mb-4 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Verificações:</span>
                      <span className="font-medium text-gray-900 dark:text-gray-100">
                        {pollingAttempts} / 120
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600 dark:text-gray-400">Tempo restante:</span>
                      <span className="font-medium text-gray-900 dark:text-gray-100">
                        {formatTime(timeRemaining)}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    ⏱️ Após 2 minutos sem confirmação, o pedido será automaticamente marcado como falho
                  </p>
                </div>
              )}

              {/* Timeout */}
              {paymentStatus === 'timeout' && (
                <div className="p-6 text-center">
                  <div className="inline-flex items-center justify-center w-20 h-20 bg-yellow-100 dark:bg-yellow-900/30 rounded-full mb-4">
                    <Clock className="w-12 h-12 text-yellow-600 dark:text-yellow-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    Tempo Esgotado
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Não conseguimos confirmar o pagamento
                  </p>
                  <button
                    onClick={() => { setPollingAttempts(0); setPaymentStatus('pending'); }}
                    className="w-full py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all mb-2"
                  >
                    <RefreshCw className="w-5 h-5 inline mr-2" />
                    Verificar Novamente
                  </button>
                </div>
              )}

              <button
                onClick={onClose}
                className="w-full py-3 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-medium rounded-xl hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Fechar
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
