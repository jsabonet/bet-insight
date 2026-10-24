import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  ArrowLeft, Users, Coins, Star, ShieldOff, Shield, Download, RefreshCw, CheckCircle2, Wallet
} from 'lucide-react';
import Header from '../../components/Header';
import BottomNav from '../../components/BottomNav';
import { affiliateAdminAPI } from '../../services/api';

export default function AdminAffiliates() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [affiliates, setAffiliates] = useState([]);
  const [commissions, setCommissions] = useState([]);
  const [withdrawals, setWithdrawals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    window.scrollTo(0, 0);
    if (!user?.is_staff && !user?.is_superuser) {
      navigate('/');
      return;
    }
    loadAll();
  }, [user, navigate]);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [ov, af, pendingCommissions, availableCommissions, wd] = await Promise.all([
        affiliateAdminAPI.getOverview(),
        affiliateAdminAPI.getAffiliates(),
        affiliateAdminAPI.getCommissions({ status: 'pending' }),
        affiliateAdminAPI.getCommissions({ status: 'available' }),
        affiliateAdminAPI.getWithdrawals(),
      ]);
      setOverview(ov.data);
      setAffiliates(af.data);
      setCommissions([...pendingCommissions.data, ...availableCommissions.data]);
      setWithdrawals(wd.data);
    } catch (e) {
      console.error('Erro ao carregar afiliados:', e);
    } finally {
      setLoading(false);
    }
  };

  const fmt = (v) => Number(v || 0).toLocaleString('pt-PT', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  const showMsg = (type, text) => {
    setMessage({ type, text });
    setTimeout(() => setMessage({ type: '', text: '' }), 3000);
  };

  const approve = async (id) => {
    try {
      await affiliateAdminAPI.approveCommission(id);
      showMsg('success', 'Comissão aprovada.');
      loadAll();
    } catch (e) {
      showMsg('error', e.response?.data?.error || 'Erro.');
    }
  };

  const markPaid = async (id) => {
    try {
      await affiliateAdminAPI.markPaid(id);
      showMsg('success', 'Comissão marcada como paga.');
      loadAll();
    } catch (e) {
      showMsg('error', e.response?.data?.error || 'Erro.');
    }
  };

  const processWithdrawal = async (id) => {
    try {
      await affiliateAdminAPI.processWithdrawal(id);
      showMsg('success', 'Pedido colocado em processamento.');
      loadAll();
    } catch (e) {
      showMsg('error', e.response?.data?.error || 'Erro ao processar pedido.');
    }
  };

  const completeWithdrawal = async (id) => {
    const reference = window.prompt('Informe a referência da transação efetuada:');
    if (!reference?.trim()) return;
    try {
      await affiliateAdminAPI.completeWithdrawal(id, reference.trim());
      showMsg('success', 'Levantamento marcado como pago.');
      loadAll();
    } catch (e) {
      showMsg('error', e.response?.data?.error || 'Erro ao registar pagamento.');
    }
  };

  const rejectWithdrawal = async (id) => {
    const reason = window.prompt('Informe o motivo da rejeição:');
    if (!reason?.trim()) return;
    try {
      await affiliateAdminAPI.rejectWithdrawal(id, reason.trim());
      showMsg('success', 'Pedido rejeitado e saldo libertado.');
      loadAll();
    } catch (e) {
      showMsg('error', e.response?.data?.error || 'Erro ao rejeitar pedido.');
    }
  };

  const toggleSuspend = async (id) => {
    try {
      await affiliateAdminAPI.toggleSuspend(id);
      showMsg('success', 'Status do afiliado atualizado.');
      loadAll();
    } catch (e) {
      showMsg('error', e.response?.data?.error || 'Erro.');
    }
  };

  const setTier = async (id, tier) => {
    try {
      await affiliateAdminAPI.setTier(id, { tier });
      showMsg('success', 'Nível atualizado.');
      loadAll();
    } catch (e) {
      showMsg('error', e.response?.data?.error || 'Erro.');
    }
  };

  const exportCsv = async () => {
    try {
      const res = await affiliateAdminAPI.exportCommissions();
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = 'comissoes.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      showMsg('error', 'Erro ao exportar.');
    }
  };

  const tabs = [
    { id: 'overview', label: 'Resumo', icon: Coins },
    { id: 'affiliates', label: 'Afiliados', icon: Users },
    { id: 'commissions', label: 'Comissões', icon: Star },
    { id: 'withdrawals', label: 'Levantamentos', icon: Wallet },
  ];

  return (
    <div className="page-container">
      <Header title="Afiliados (Admin)" subtitle="Gestão do programa de afiliados" />

      <div className="page-content">
        {/* Back */}
        <button onClick={() => navigate('/admin')} className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
          <ArrowLeft className="w-4 h-4" /> Voltar ao Admin
        </button>

        {message.text && (
          <div className={`mb-4 p-3 rounded-lg text-sm ${
            message.type === 'success'
              ? 'bg-green-50 text-green-700 border border-green-200 dark:bg-green-900/20 dark:border-green-800'
              : 'bg-red-50 text-red-700 border border-red-200 dark:bg-red-900/20 dark:border-red-800'
          }`}>
            {message.text}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2 no-scrollbar">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold whitespace-nowrap transition-all ${
                activeTab === t.id
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700'
              }`}
            >
              <t.icon className="w-4 h-4" /> {t.label}
            </button>
          ))}
          <button onClick={loadAll} className="p-2.5 rounded-xl border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>

        {loading ? (
          <div className="text-center py-10 text-gray-500">A carregar...</div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="card">
                    <p className="text-3xl font-bold text-primary-600 dark:text-primary-400">{overview?.affiliates_active ?? 0}</p>
                    <p className="text-xs text-gray-500 mt-1">Afiliados ativos</p>
                  </div>
                  <div className="card">
                    <p className="text-3xl font-bold text-green-600 dark:text-green-400">{fmt(overview?.commissions_amount)}</p>
                    <p className="text-xs text-gray-500 mt-1">Total em comissões (MZN)</p>
                  </div>
                </div>

                <div className="card">
                  <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">Comissões por status</h3>
                  <div className="space-y-2">
                    {Object.entries(overview?.by_status || {}).map(([k, v]) => (
                      <div key={k} className="flex items-center justify-between">
                        <span className="text-sm capitalize text-gray-700 dark:text-gray-300">{k}</span>
                        <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">
                          {v.count} · {fmt(v.amount)} MZN
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card">
                  <h3 className="font-bold text-gray-900 dark:text-gray-100 mb-4">Top Afiliados</h3>
                  <div className="space-y-2">
                    {(overview?.top_affiliates || []).map((a) => (
                      <div key={a.id} className="flex items-center justify-between">
                        <span className="text-sm text-gray-700 dark:text-gray-300">{a.code}</span>
                        <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">{fmt(a.total)} MZN</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'affiliates' && (
              <div className="space-y-3">
                {affiliates.map((a) => (
                  <div key={a.id} className="card">
                    <div className="flex items-center justify-between mb-2">
                      <div>
                        <p className="font-bold text-gray-900 dark:text-gray-100">{a.code}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">{a.email || a.username}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {a.payout_method_display} · {a.payout_account || 'Conta não configurada'}
                        </p>
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        a.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}>
                        {a.status}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm mb-3">
                      <span className="text-gray-600 dark:text-gray-400">
                        Disponível: <span className="font-semibold text-gray-900 dark:text-gray-100">{fmt(a.available_balance)} MZN</span>
                      </span>
                      <span className="text-gray-600 dark:text-gray-400">
                        Conversões: <span className="font-semibold text-gray-900 dark:text-gray-100">{a.converted_count}</span>
                      </span>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => setTier(a.id, a.tier === 'vip' ? 'standard' : 'vip')}
                        className="flex-1 py-2 rounded-lg border border-gray-200 dark:border-gray-700 text-xs font-semibold text-gray-700 dark:text-gray-300"
                      >
                        {a.tier === 'vip' ? 'Rebaixar para Padrão' : 'Promover a VIP'}
                      </button>
                      <button
                        onClick={() => toggleSuspend(a.id)}
                        className="flex-1 py-2 rounded-lg border border-gray-200 dark:border-gray-700 text-xs font-semibold text-gray-700 dark:text-gray-300 flex items-center justify-center gap-1"
                      >
                        {a.status === 'active' ? <ShieldOff className="w-3 h-3" /> : <Shield className="w-3 h-3" />}
                        {a.status === 'active' ? 'Suspender' : 'Reativar'}
                      </button>
                    </div>
                  </div>
                ))}
                {affiliates.length === 0 && <p className="text-center text-gray-500 py-8">Sem afiliados.</p>}
              </div>
            )}

            {activeTab === 'commissions' && (
              <div className="space-y-3">
                <div className="flex justify-end">
                  <button onClick={exportCsv} className="flex items-center gap-2 px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 text-sm font-semibold text-gray-700 dark:text-gray-300">
                    <Download className="w-4 h-4" /> Exportar CSV
                  </button>
                </div>
                {commissions.map((c) => (
                  <div key={c.id} className="card">
                    <div className="flex items-center justify-between mb-2">
                      <p className="font-bold text-gray-900 dark:text-gray-100">
                        {fmt(c.amount)} MZN
                      </p>
                      <span className="text-xs font-semibold px-2 py-1 rounded-full bg-amber-100 text-amber-700">{c.status}</span>
                    </div>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                      {c.affiliate_code} → {c.buyer_email || 'comprador'}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">Plano: {c.plan}</p>
                    {c.status === 'pending' && (
                      <div className="flex gap-2">
                        <button onClick={() => approve(c.id)} className="flex-1 py-2 rounded-lg bg-green-600 text-white text-xs font-semibold flex items-center justify-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Aprovar
                        </button>
                      </div>
                    )}

                    {c.status === 'available' && c.withdrawal_allocated && (
                      <p className="text-xs text-amber-700 dark:text-amber-400">
                        Reservada por um pedido de levantamento.
                      </p>
                    )}
                    {c.status === 'available' && !c.withdrawal_allocated && (
                      <button onClick={() => markPaid(c.id)} className="w-full py-2 rounded-lg bg-blue-600 text-white text-xs font-semibold">
                        Marcar como pago
                      </button>
                    )}
                  </div>
                ))}
                {commissions.length === 0 && <p className="text-center text-gray-500 py-8">Sem comissões pendentes.</p>}
              </div>
            )}

            {activeTab === 'withdrawals' && (
              <div className="space-y-3">
                {withdrawals.map((item) => (
                  <div key={item.id} className="card">
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div>
                        <p className="font-bold text-gray-900 dark:text-gray-100">
                          {fmt(item.amount)} MZN · {item.affiliate_code}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {item.affiliate_username} · {item.affiliate_email || 'Sem email'}
                        </p>
                      </div>
                      <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                        item.status === 'paid'
                          ? 'bg-green-100 text-green-700'
                          : item.status === 'rejected'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-amber-100 text-amber-700'
                      }`}>{item.status_display}</span>
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {item.payout_method_display}: <span className="font-semibold">{item.payout_account}</span>
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                      Pedido em {new Date(item.requested_at).toLocaleString('pt-PT')}
                      {item.transaction_reference ? ` · Ref. ${item.transaction_reference}` : ''}
                      {item.rejection_reason ? ` · Motivo: ${item.rejection_reason}` : ''}
                    </p>
                    {item.status === 'requested' && (
                      <div className="flex gap-2">
                        <button onClick={() => processWithdrawal(item.id)} className="flex-1 py-2 rounded-lg bg-primary-600 text-white text-xs font-semibold">
                          Iniciar processamento
                        </button>
                        <button onClick={() => rejectWithdrawal(item.id)} className="flex-1 py-2 rounded-lg border border-red-200 text-red-700 text-xs font-semibold">
                          Rejeitar
                        </button>
                      </div>
                    )}
                    {item.status === 'processing' && (
                      <div className="flex gap-2">
                        <button onClick={() => completeWithdrawal(item.id)} className="flex-1 py-2 rounded-lg bg-blue-600 text-white text-xs font-semibold">
                          Registar pagamento
                        </button>
                        <button onClick={() => rejectWithdrawal(item.id)} className="flex-1 py-2 rounded-lg border border-red-200 text-red-700 text-xs font-semibold">
                          Rejeitar
                        </button>
                      </div>
                    )}
                  </div>
                ))}
                {withdrawals.length === 0 && <p className="text-center text-gray-500 py-8">Sem pedidos de levantamento.</p>}
              </div>
            )}
          </>
        )}
      </div>

      <BottomNav />
    </div>
  );
}
