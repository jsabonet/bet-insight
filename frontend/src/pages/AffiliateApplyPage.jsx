import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Gift, Smartphone, Landmark, Wallet, CheckCircle2 } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import { affiliateAPI } from '../services/api';
import { AFFILIATE_TERMS_VERSION } from '../utils/affiliateTerms';

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
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [existingAffiliate, setExistingAffiliate] = useState(false);
  const [profileLoading, setProfileLoading] = useState(true);

  useEffect(() => {
    let active = true;
    affiliateAPI.getMe().then(({ data }) => {
      if (!active) return;
      setExistingAffiliate(true);
      setPayoutMethod(data.payout_method || 'mpesa');
      setPayoutAccount(data.payout_account || '');
    }).catch((err) => {
      if (active && err.response?.status !== 404) {
        setError(err.response?.data?.error || 'Não foi possível carregar os dados de afiliado.');
      }
    }).finally(() => {
      if (active) setProfileLoading(false);
    });
    return () => { active = false; };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await affiliateAPI.apply({
        payout_method: payoutMethod,
        payout_account: payoutAccount,
        terms_version: AFFILIATE_TERMS_VERSION,
      });
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
            <h2 className="text-xl font-bold">Receba comissões por compras confirmadas</h2>
          </div>
          <p className="text-sm text-white/80">
              Partilhe o seu link para divulgar o PlacarCerto, um SaaS educativo de análise
              estatística de futebol. Não somos uma casa de apostas e não promovemos nem facilitamos apostas.
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
            required={!existingAffiliate}
          />

          <label className="mt-5 flex items-start gap-3 text-sm text-gray-700 dark:text-gray-300">
            <input
              type="checkbox"
              checked={acceptedTerms}
              onChange={(e) => setAcceptedTerms(e.target.checked)}
              className="mt-1 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              required
            />
            <span>
              Li e aceito os <a href="/affiliate/terms" target="_blank" rel="noreferrer" className="font-semibold text-primary-600 hover:underline">Termos do Programa de Afiliados</a>
              {' '}(versão {AFFILIATE_TERMS_VERSION}), incluindo a regra de não promover apostas.
              Declaro também ter pelo menos 18 anos.
            </span>
          </label>

          {error && (
            <div className="mt-4 rounded-lg bg-red-50 border border-red-200 text-red-700 px-3 py-2 text-sm dark:bg-red-900/20 dark:border-red-800">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || profileLoading || !acceptedTerms}
            className="w-full mt-6 rounded-xl bg-primary-600 py-4 font-bold text-white transition-all hover:bg-primary-700 disabled:opacity-50"
          >
            {profileLoading ? 'A carregar...' : loading ? 'A guardar...' : existingAffiliate ? 'Aceitar termos e continuar' : 'Tornar-me Afiliado'}
          </button>

          <p className="text-xs text-gray-500 dark:text-gray-400 mt-4 text-center">
            Comissão: 100 MZN por primeira compra elegível, sem comissão de renovação. Mínimo de
            levantamento: 200 MZN; taxa: 6%; prazo: até 5 dias úteis após pedido válido.
          </p>
        </form>
      </div>

      <BottomNav />
    </div>
  );
}
