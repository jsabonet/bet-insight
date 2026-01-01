import Logo from './Logo';

export default function LimitReachedModal({ onClose, dailyLimit = 3 }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-2xl max-w-sm mx-4">
        <div className="flex flex-col items-center text-center">
          <Logo variant="thinking" size="lg" showText={false} />
          <h2 className="mt-4 text-lg font-bold text-gray-900 dark:text-gray-100">
            Limite diário atingido
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Você alcançou o limite de {dailyLimit} análises por dia do seu plano.
            Tente novamente amanhã ou assine o Premium para mais análises.
          </p>
          <button
            onClick={onClose}
            className="mt-6 btn-primary w-full"
          >
            Entendi
          </button>
        </div>
      </div>
    </div>
  );
}
