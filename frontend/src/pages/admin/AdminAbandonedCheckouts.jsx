import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock3, Mail, Phone, RefreshCw, Search, ShoppingCart } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import Header from '../../components/Header';
import BottomNav from '../../components/BottomNav';
import { adminAPI } from '../../services/api';

export default function AdminAbandonedCheckouts() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [checkouts, setCheckouts] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadCheckouts = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await adminAPI.getAbandonedCheckouts();
      setCheckouts(Array.isArray(data.results) ? data.results : []);
    } catch (requestError) {
      console.error('Erro ao carregar checkouts abandonados:', requestError);
      setError(requestError.response?.data?.detail || 'Não foi possível carregar os checkouts abandonados.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!user?.is_staff && !user?.is_superuser) {
      navigate('/');
      return;
    }
    loadCheckouts();
  }, [user, navigate, loadCheckouts]);

  const filteredCheckouts = useMemo(() => {
    const term = search.trim().toLocaleLowerCase();
    if (!term) return checkouts;
    return checkouts.filter((checkout) => [
      checkout.name,
      checkout.username,
      checkout.email,
      checkout.phone,
      checkout.transaction_id,
      checkout.vpay_order_id,
      checkout.plan_name,
    ].some((value) => String(value || '').toLocaleLowerCase().includes(term)));
  }, [checkouts, search]);

  const formatDate = (value) => new Date(value).toLocaleString('pt-MZ');
  const formatAmount = (value, currency) => (
    `${Number(value || 0).toLocaleString('pt-MZ', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${currency}`
  );

  return (
    <div className="page-container">
      <Header title="Checkouts abandonados" subtitle="Pedidos de pagamento pendentes há pelo menos 1 hora" />
      <main className="page-content space-y-4">
        <button
          type="button"
          onClick={() => navigate('/admin')}
          className="btn-ghost inline-flex items-center gap-2 text-gray-600 dark:text-gray-300"
        >
          <ArrowLeft className="h-4 w-4" />
          Voltar à administração
        </button>

        <section className="card">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300">
              <ShoppingCart className="h-6 w-6" />
            </div>
            <div className="min-w-0 flex-1">
              <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">
                {checkouts.length} checkout(s) pendente(s)
              </h2>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                Os dados de contacto são visíveis apenas para administradores. O lembrete por email é enviado uma vez,
                automaticamente, após 1 hora enquanto o pagamento continuar pendente.
              </p>
            </div>
            <button
              type="button"
              onClick={loadCheckouts}
              disabled={loading}
              className="btn-secondary inline-flex shrink-0 items-center justify-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Atualizar
            </button>
          </div>
        </section>

        <section className="card">
          <label htmlFor="abandoned-checkout-search" className="sr-only">Pesquisar checkouts abandonados</label>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              id="abandoned-checkout-search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Pesquisar por nome, telefone, email ou referência"
              className="input-field pl-10"
            />
          </div>
        </section>

        {error && (
          <div role="alert" className="rounded-xl bg-rose-50 p-4 text-sm text-rose-700 dark:bg-rose-950/40 dark:text-rose-300">
            <p>{error}</p>
            <button type="button" onClick={loadCheckouts} className="mt-2 font-semibold underline">
              Tentar novamente
            </button>
          </div>
        )}

        {loading ? (
          <div className="card text-center text-sm text-gray-500 dark:text-gray-400">A carregar checkouts...</div>
        ) : filteredCheckouts.length === 0 ? (
          <div className="card py-10 text-center">
            <ShoppingCart className="mx-auto h-10 w-10 text-gray-400" />
            <p className="mt-3 font-semibold text-gray-800 dark:text-gray-200">
              {search ? 'Nenhum checkout corresponde à pesquisa.' : 'Não há checkouts abandonados neste momento.'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {filteredCheckouts.map((checkout) => (
              <article key={checkout.payment_id} className="card space-y-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">{checkout.name}</h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">@{checkout.username}</p>
                  </div>
                  <div className="inline-flex w-fit items-center gap-2 rounded-full bg-amber-100 px-3 py-1 text-sm font-semibold text-amber-800 dark:bg-amber-900/30 dark:text-amber-200">
                    <Clock3 className="h-4 w-4" />
                    {checkout.minutes_abandoned} min pendente
                  </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <div>
                    <p className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Telefone</p>
                    {checkout.phone ? (
                      <a className="mt-1 inline-flex items-center gap-2 font-semibold text-primary-700 hover:underline dark:text-primary-300" href={`tel:${checkout.phone}`}>
                        <Phone className="h-4 w-4" />
                        {checkout.phone}
                      </a>
                    ) : (
                      <p className="mt-1 text-sm text-gray-500">Não informado</p>
                    )}
                  </div>
                  <div className="min-w-0">
                    <p className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Email</p>
                    {checkout.email ? (
                      <a className="mt-1 inline-flex max-w-full items-center gap-2 break-all text-sm text-primary-700 hover:underline dark:text-primary-300" href={`mailto:${checkout.email}`}>
                        <Mail className="h-4 w-4 shrink-0" />
                        {checkout.email}
                      </a>
                    ) : (
                      <p className="mt-1 text-sm text-gray-500">Não informado</p>
                    )}
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Plano / valor</p>
                    <p className="mt-1 font-semibold text-gray-900 dark:text-gray-100">
                      {checkout.plan_name || checkout.plan || 'Plano não identificado'}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{formatAmount(checkout.amount, checkout.currency)}</p>
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400">Lembrete de recuperação</p>
                    {checkout.recovery_email_sent_at ? (
                      <p className="mt-1 text-sm text-emerald-700 dark:text-emerald-300">
                        Enviado em {formatDate(checkout.recovery_email_sent_at)}
                      </p>
                    ) : checkout.email ? (
                      <p className="mt-1 text-sm text-amber-700 dark:text-amber-300">A aguardar envio automático</p>
                    ) : (
                      <p className="mt-1 text-sm text-gray-500">Sem email para envio</p>
                    )}
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-3 text-xs text-gray-500 dark:border-gray-700 dark:text-gray-400">
                  <p>Pedido criado: {formatDate(checkout.created_at)}</p>
                  <p className="mt-1 break-all">Referência: {checkout.transaction_id} · Pedido VPay: {checkout.vpay_order_id}</p>
                </div>
              </article>
            ))}
          </div>
        )}
      </main>
      <BottomNav />
    </div>
  );
}
