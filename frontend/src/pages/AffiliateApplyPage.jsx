import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Gift, Smartphone, Landmark, Wallet, CheckCircle2 } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import { affiliateAPI } from '../services/api';

const PAYOUT_METHODS = [
  { value: 'mpesa', label: 'M-Pesa', icon: Smartphone },
  { value: 'emola', label: 'e-Mola', icon: Wallet },
  { value: 'bank', label: 'Banco', icon: Landmark },
];

export default function AffiliateApplyPage() {
  const navigate = useNavigate();
  const [payoutMethod, setPayoutMethod] = useState('mpesa');
  const [payoutAccount, setPayoutAccount] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await affiliateAPI.apply({ payout_method: payoutMethod, payout_account: payoutAccount });
      navigate('/affiliate');
    } catch (err) {
      setError(err.response?.data?.error || 'Não foi possível criar a sua conta de afiliado.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <Header title="Programa de Afiliados" subtitle="Ganhe comissões ao indicar o PlacarCerto" />

      <div className="page-content">
        {/* Value prop */}
        <div className="card animate-slide-up bg-gradient-to-br from-primary-600 to-primary-800 dark:from-primary-900 dark:to-gray-900 text-white border-0">
          <div className="flex items-center gap-2 mb-2">
            <Gift className="w-6 h-6" />
            <h2 className="text-xl font-bold">Receba comissões por vendas confirmadas</h2>
          </div>
          <p className="text-sm text-white/80">
            Partilhe o seu link e receba comissões sempre que alguém assinar o PlacarCerto
            — o infoproduto de análise matemática e estatística de futebol.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="card animate-slide-up mt-4">
          <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">Como quer receber?</h3>

          <div className="space-y-3 mb-6">
            {PAYOUT_METHODS.map((m) => (
              <button
                type="button"
                key={m.value}
                onClick={() => setPayoutMethod(m.value)}
                className={`w-full flex items-center gap-3 p-4 rounded-xl border-2 transition-all text-left ${
                  payoutMethod === m.value
                    ? 'border-primary-600 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'
                }`}
              >
                <m.icon className={`w-6 h-6 ${payoutMethod === m.value ? 'text-primary-600 dark:text-primary-400' : 'text-gray-400'}`} />
                <span className="font-semibold text-gray-900 dark:text-gray-100">{m.label}</span>
                {payoutMethod === m.value && <CheckCircle2 className="w-5 h-5 text-primary-600 ml-auto" />}
              </button>
            ))}
          </div>

          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Número / Conta
          </label>
          <input
            type="text"
            value={payoutAccount}
            onChange={(e) => setPayoutAccount(e.target.value)}
            className="input-field"
            placeholder="Ex: +258 84 XXX XXXX"
            required
          />

          {error && (
            <div className="mt-4 rounded-lg bg-red-50 border border-red-200 text-red-700 px-3 py-2 text-sm dark:bg-red-900/20 dark:border-red-800">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-6 rounded-xl bg-primary-600 py-4 font-bold text-white transition-all hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? 'A criar conta...' : 'Tornar-me Afiliado'}
          </button>

          <p className="text-xs text-gray-500 dark:text-gray-400 mt-4 text-center">
            Ao tornar-se afiliado, compromete-se a divulgar o PlacarCerto como uma ferramenta
            de análise estatística, sem prometer ganhos ou resultados de apostas.
          </p>
        </form>
      </div>

      <BottomNav />
    </div>
  );
}
