import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Check, Copy, Gift, Share2, Users } from 'lucide-react';
import Header from '../components/Header';
import BottomNav from '../components/BottomNav';
import { affiliateAPI } from '../services/api';

export default function MemberReferralsPage() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let active = true;
    affiliateAPI.getMemberReferrals()
      .then(({ data }) => {
        if (active) setSummary(data);
      })
      .catch((requestError) => {
        console.error('Não foi possível carregar os convites:', requestError);
        if (active) setError('Não foi possível carregar os dados dos convites. Tente novamente.');
      });
    return () => {
      active = false;
    };
  }, []);

  const referralLink = summary
    ? `${window.location.origin}/register?ref=${encodeURIComponent(summary.code)}`
    : '';

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(referralLink);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch (copyError) {
      console.error('Não foi possível copiar o link de convite:', copyError);
      setError('Não foi possível copiar automaticamente. Selecione e copie o link.');
    }
  };

  const shareLink = async () => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: 'Convite PlacarCerto',
          text: 'Registe-se com o meu convite. Quando concluir a primeira análise, recebemos 5 análises bónus cada.',
          url: referralLink,
        });
        return;
      }
      await copyLink();
    } catch (shareError) {
      if (shareError.name === 'AbortError') return;
      console.error('Não foi possível partilhar o convite:', shareError);
      setError('Não foi possível abrir a partilha. Copie o link e envie diretamente.');
    }
  };

  return (
    <div className="page-container">
      <Header title="Convide um membro" subtitle="Partilhe análises com amigos" />
      <main className="page-content space-y-4">
        {error && (
          <p role="alert" className="rounded-xl bg-rose-50 p-3 text-sm text-rose-700 dark:bg-rose-950/40 dark:text-rose-300">
            {error}
          </p>
        )}

        <section className="card">
          <span className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary-50 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300">
            <Gift className="h-6 w-6" />
          </span>
          <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">5 análises bónus para cada um</h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
            Partilhe o seu link. Quando uma nova pessoa criar conta com o convite e concluir a primeira análise,
            você e essa pessoa recebem 5 análises bónus.
          </p>
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            Cada conta pode participar uma vez. As análises bónus são aplicadas depois do limite diário do seu plano.
            Convites associados ao mesmo IP ou dispositivo não recebem bónus; o cadastro continua disponível.
          </p>

          {summary ? (
            <div className="mt-5 space-y-3">
              <label htmlFor="member-referral-link" className="block text-sm font-semibold">
                O seu link de convite
              </label>
              <div className="flex flex-col gap-2 sm:flex-row">
                <input
                  id="member-referral-link"
                  readOnly
                  value={referralLink}
                  className="input-field min-w-0 flex-1"
                />
                <button
                  type="button"
                  onClick={shareLink}
                  className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-emerald-600 px-3 py-2 font-semibold text-white hover:bg-emerald-700"
                >
                  <Share2 className="h-4 w-4" />
                  <span>Partilhar</span>
                </button>
                <button
                  type="button"
                  onClick={copyLink}
                  className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-primary-600 px-3 py-2 font-semibold text-white hover:bg-primary-700"
                >
                  {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                  <span className="hidden sm:inline">{copied ? 'Copiado' : 'Copiar'}</span>
                </button>
              </div>
            </div>
          ) : !error ? (
            <p className="mt-5 text-sm text-gray-500">A carregar o seu link...</p>
          ) : null}
        </section>

        {summary && (
          <section className="grid grid-cols-2 gap-3">
            <div className="card">
              <Users className="h-5 w-5 text-primary-600 dark:text-primary-400" />
              <p className="mt-3 text-2xl font-bold">{summary.total_invites}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Convites registados</p>
            </div>
            <div className="card">
              <Gift className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
              <p className="mt-3 text-2xl font-bold">{summary.bonus_analysis_credits}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Análises bónus disponíveis</p>
            </div>
            <div className="card col-span-2">
              <p className="text-2xl font-bold">{summary.completed_invites}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Convites que concluíram a primeira análise</p>
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                {summary.pending_invites} convite(s) ainda sem primeira análise concluída.
              </p>
              {summary.ineligible_invites > 0 && (
                <p className="mt-2 text-xs text-amber-700 dark:text-amber-300">
                  {summary.ineligible_invites} convite(s) não receberam recompensa por partilharem IP ou dispositivo
                  com outra conta.
                </p>
              )}
            </div>
          </section>
        )}

        <section className="card">
          <h2 className="font-bold text-gray-900 dark:text-gray-100">Programa de afiliados</h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
            Quer receber comissões por vendas confirmadas? O programa de afiliados é separado deste convite e tem regras próprias.
          </p>
          <Link to="/affiliate" className="mt-4 inline-flex font-semibold text-primary-700 hover:underline dark:text-primary-300">
            Consultar afiliados
          </Link>
        </section>
      </main>
      <BottomNav />
    </div>
  );
}
