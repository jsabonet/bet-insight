import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { toPng } from 'html-to-image';
import {
  AlertTriangle,
  ArrowLeft,
  CalendarDays,
  Camera,
  Check,
  CheckCircle2,
  ChevronRight,
  Copy,
  Download,
  Info,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Trash2,
  Wallet,
  X,
} from 'lucide-react';

import Header from '../../components/Header';
import BottomNav from '../../components/BottomNav';
import SocialProofPreview, {
  BASE_WIDTH,
  EXPORT_WIDTH,
  formatMzn,
} from '../../components/SocialProofPreview';
import { useAuth } from '../../context/AuthContext';
import { SOCIAL_PROOF_KINDS, socialProofAPI } from '../../services/socialProofAPI';

const MIN_STAKE_VALUE = 5;
const DEFAULT_STAKE_VALUE = 10;
const MAX_STAKE_VALUE = 1000000;
const HISTORY_LIMIT = 50;

function parseStakeValue(raw) {
  const text = String(raw ?? '').trim();
  if (!text) return NaN;
  const normalized = /^\d{1,3}(\.\d{3})+$/.test(text)
    ? text.replace(/\./g, '')
    : text.replace(',', '.');
  const parsed = Number.parseFloat(normalized);
  return Number.isFinite(parsed) ? parsed : NaN;
}

function localDateIso(offsetDays = 0) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  const pad = (value) => String(value).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

function formatDateLabel(isoDate) {
  if (!isoDate) return '—';
  const [year, month, day] = String(isoDate).split('-');
  if (!year || !month || !day) return isoDate;
  return `${day}/${month}/${year}`;
}

function useMeasuredSize(ref, dependency) {
  const [size, setSize] = useState({ width: 0, height: 0 });

  useLayoutEffect(() => {
    const node = ref.current;
    if (!node) {
      setSize({ width: 0, height: 0 });
      return undefined;
    }

    const update = () => {
      setSize({ width: node.offsetWidth, height: node.offsetHeight });
    };

    update();
    const observer = new ResizeObserver(update);
    observer.observe(node);
    return () => observer.disconnect();
  }, [ref, dependency]);

  return size;
}

const STATUS_STYLES = {
  candidate:
    'bg-amber-50 text-amber-700 ring-amber-500/30 dark:bg-amber-500/15 dark:text-amber-300',
  approved:
    'bg-emerald-50 text-emerald-700 ring-emerald-500/30 dark:bg-emerald-500/15 dark:text-emerald-300',
  exported: 'bg-sky-50 text-sky-700 ring-sky-500/30 dark:bg-sky-500/15 dark:text-sky-300',
  discarded:
    'bg-gray-100 text-gray-600 ring-gray-400/30 dark:bg-gray-500/15 dark:text-gray-300',
};

function StatusBadge({ status, label }) {
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold ring-1 ring-inset ${
        STATUS_STYLES[status] || STATUS_STYLES.candidate
      }`}
    >
      <span className="size-1.5 rounded-full bg-current opacity-70" aria-hidden="true" />
      {label}
    </span>
  );
}

function Alert({ tone, icon: Icon, children, onDismiss }) {
  const tones = {
    error: {
      wrapper: 'border-red-500/30 bg-red-50 text-red-800 dark:bg-red-500/10 dark:text-red-300',
      button: 'text-red-500 hover:bg-red-500/10',
    },
    success: {
      wrapper:
        'border-emerald-500/30 bg-emerald-50 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-300',
      button: 'text-emerald-600 hover:bg-emerald-500/10',
    },
    info: {
      wrapper: 'border-sky-500/30 bg-sky-50 text-sky-800 dark:bg-sky-500/10 dark:text-sky-300',
      button: 'text-sky-600 hover:bg-sky-500/10',
    },
  };
  const toneStyles = tones[tone] || tones.info;

  return (
    <div
      role={tone === 'error' ? 'alert' : 'status'}
      className={`flex items-start gap-2.5 rounded-xl border px-3 py-2.5 text-sm ${toneStyles.wrapper}`}
    >
      <Icon size={16} className="mt-0.5 shrink-0" />
      <div className="min-w-0 flex-1">{children}</div>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Fechar aviso"
          className={`-mr-1 shrink-0 rounded-lg p-1 transition ${toneStyles.button}`}
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
}

function StatTile({ label, value, highlight }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white px-3 py-2 dark:border-gray-700 dark:bg-gray-800">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
        {label}
      </p>
      <p
        className={`mt-0.5 text-lg font-bold tabular-nums ${
          highlight ? 'text-primary-600 dark:text-primary-400' : 'text-gray-900 dark:text-white'
        }`}
      >
        {value}
      </p>
    </div>
  );
}

function buildCaption(ticket) {
  const legs = ticket.legs || [];
  const lines = [
    `🎯 ${ticket.headline || 'Bilhete PlacerCerto'}`,
    '',
    ...legs.map((leg, index) => `${index + 1}. ${leg.match} — ${leg.pick || leg.market_label}`),
    '',
    `Odd total: ${Number(ticket.total_odd).toFixed(2)}`,
    `Código de reserva: ${ticket.reserve_code}`,
    '',
    ticket.disclosure,
  ];

  return lines.join('\n');
}

export default function AdminSocialProof() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [date, setDate] = useState(localDateIso(-1));
  const [kind, setKind] = useState(SOCIAL_PROOF_KINDS[0].id);
  const [candidates, setCandidates] = useState([]);
  const [ticket, setTicket] = useState(null);
  const [history, setHistory] = useState([]);
  const [stakeInput, setStakeInput] = useState(String(DEFAULT_STAKE_VALUE));

  const [loadingCandidates, setLoadingCandidates] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [viewportWidth, setViewportWidth] = useState(() =>
    typeof window === 'undefined' ? BASE_WIDTH : window.innerWidth
  );

  const sheetRef = useRef(null);
  const exportRef = useRef(null);
  const skipResetRef = useRef(false);

  const sheetSize = useMeasuredSize(sheetRef, ticket);

  const previewScale = useMemo(() => {
    const available = Math.max(0, viewportWidth - 64);
    return Math.min(1, available / BASE_WIDTH);
  }, [viewportWidth]);

  const activeKind = SOCIAL_PROOF_KINDS.find((item) => item.id === kind);

  const appliedStake = Number(
    ticket?.stake_amount ?? ticket?.stake_units ?? DEFAULT_STAKE_VALUE
  );
  const parsedStake = parseStakeValue(stakeInput);
  const stakeValid =
    Number.isFinite(parsedStake) &&
    parsedStake >= MIN_STAKE_VALUE &&
    parsedStake <= MAX_STAKE_VALUE;
  const stakeDirty = Boolean(ticket) && stakeValid && Math.abs(parsedStake - appliedStake) > 0.001;
  const previewStake = stakeValid ? parsedStake : appliedStake;
  const totalOdd = Number(ticket?.total_odd) || 0;
  const canApplyStake = Boolean(ticket) && stakeValid && stakeDirty && !busy;

  const stats = useMemo(() => {
    return history.reduce(
      (accumulator, item) => {
        accumulator.total += 1;
        if (item.status === 'candidate') accumulator.pending += 1;
        if (item.status === 'approved') accumulator.approved += 1;
        if (item.status === 'exported') accumulator.exported += 1;
        return accumulator;
      },
      { total: 0, pending: 0, approved: 0, exported: 0 }
    );
  }, [history]);

  const loadHistory = useCallback(async () => {
    setLoadingHistory(true);
    try {
      const response = await socialProofAPI.getTickets({ date, limit: HISTORY_LIMIT });
      setHistory(response.data.tickets || []);
    } catch (requestError) {
      console.error('Erro ao carregar histórico de prova social', requestError);
      setHistory([]);
    } finally {
      setLoadingHistory(false);
    }
  }, [date]);

  const loadCandidates = useCallback(async () => {
    setLoadingCandidates(true);
    setError('');
    try {
      const response = await socialProofAPI.getCandidates(date, kind);
      setCandidates(response.data.candidates || []);
    } catch (requestError) {
      console.error('Erro ao carregar candidatos', requestError);
      setCandidates([]);
      setError(
        requestError.response?.data?.error ||
          'Não foi possível calcular candidatos para esta data.'
      );
    } finally {
      setLoadingCandidates(false);
    }
  }, [date, kind]);

  useEffect(() => {
    if (!user?.is_staff && !user?.is_superuser) {
      navigate('/admin');
    }
  }, [user, navigate]);

  useEffect(() => {
    const handleResize = () => setViewportWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    loadCandidates();
    loadHistory();
  }, [loadCandidates, loadHistory]);

  useEffect(() => {
    if (skipResetRef.current) {
      skipResetRef.current = false;
      return;
    }
    setTicket(null);
    setStakeInput(String(DEFAULT_STAKE_VALUE));
    setNotice('');
  }, [kind, date]);

  const handleSyncResults = async () => {
    setBusy('sync');
    setError('');
    setNotice('');
    try {
      const response = await socialProofAPI.syncResults(date);
      const data = response.data || {};
      setNotice(
        `Resultados sincronizados: ${data.fixtures ?? 0} partidas, ${data.finished ?? 0} finalizadas.`
      );
      await Promise.all([loadCandidates(), loadHistory()]);
    } catch (requestError) {
      setError(requestError.response?.data?.error || 'Falha ao sincronizar resultados.');
    } finally {
      setBusy('');
    }
  };

  const handleGenerate = async (candidate) => {
    setBusy(candidate ? candidate.snapshot_hash : 'auto');
    setError('');
    setNotice('');

    try {
      const payload = {
        date,
        kind,
        stake_amount: stakeValid ? parsedStake : DEFAULT_STAKE_VALUE,
      };
      if (candidate?.snapshot_hash) payload.snapshot_hash = candidate.snapshot_hash;

      const response = await socialProofAPI.generate(payload);
      const appliedStake = response.data.stake_amount ?? response.data.stake_units;
      setTicket(response.data);
      setStakeInput(String(appliedStake));
      setNotice(
        response.data.created
          ? `Snapshot criado com aposta de ${formatMzn(
              appliedStake
            )}. Reveja a imagem antes de aprovar.`
          : `Snapshot já existente carregado · valor da aposta ${formatMzn(appliedStake)}.`
      );
      await loadHistory();
    } catch (requestError) {
      setError(requestError.response?.data?.error || 'Falha ao gerar o snapshot.');
    } finally {
      setBusy('');
    }
  };

  const handleSelectTicket = async (ticketId) => {
    setBusy(`load-${ticketId}`);
    setError('');
    try {
      const response = await socialProofAPI.getTicket(ticketId);
      const nextKind = response.data.kind;
      if (nextKind !== kind) {
        skipResetRef.current = true;
        setKind(nextKind);
      }
      setTicket(response.data);
      setStakeInput(String(response.data.stake_amount ?? response.data.stake_units));
      setNotice('');
    } catch (requestError) {
      setError(requestError.response?.data?.error || 'Falha ao carregar o snapshot.');
    } finally {
      setBusy('');
    }
  };

  const applyStakeIfNeeded = useCallback(async () => {
    if (!ticket || !stakeDirty) return ticket;
    const response = await socialProofAPI.updateStake(ticket.id, parsedStake);
    setTicket(response.data);
    setStakeInput(String(response.data.stake_amount ?? response.data.stake_units));
    return response.data;
  }, [ticket, stakeDirty, parsedStake]);

  const handleApplyStake = async (event) => {
    event?.preventDefault();
    if (!canApplyStake) return;

    setBusy('stake');
    setError('');
    setNotice('');
    try {
      const response = await socialProofAPI.updateStake(ticket.id, parsedStake);
      setTicket(response.data);
      setStakeInput(String(response.data.stake_amount ?? response.data.stake_units));
      setNotice(
        `Valor aplicado: ${formatMzn(
          response.data.stake_amount ?? response.data.stake_units
        )} · retorno ${formatMzn(response.data.potential_return ?? 0)}.`
      );
      loadHistory();
    } catch (requestError) {
      setError(requestError.response?.data?.error || 'Falha ao aplicar o valor da aposta.');
    } finally {
      setBusy('');
    }
  };

  const handleApprove = async () => {
    if (!ticket) return;
    setBusy('approve');
    setError('');
    try {
      await applyStakeIfNeeded();
      const response = await socialProofAPI.approve(ticket.id);
      setTicket(response.data);
      setNotice('Snapshot aprovado. Já pode exportar a imagem.');
      await loadHistory();
    } catch (requestError) {
      setError(requestError.response?.data?.error || 'Falha ao aprovar o snapshot.');
    } finally {
      setBusy('');
    }
  };

  const handleDiscard = async () => {
    if (!ticket) return;
    setBusy('discard');
    setError('');
    try {
      await socialProofAPI.discard(ticket.id);
      setTicket(null);
      setStakeInput(String(DEFAULT_STAKE_VALUE));
      setNotice('Snapshot descartado.');
      await loadHistory();
    } catch (requestError) {
      setError(requestError.response?.data?.error || 'Falha ao descartar o snapshot.');
    } finally {
      setBusy('');
    }
  };

  const handleDownload = async () => {
    if (!ticket || !exportRef.current) return;
    if (!['approved', 'exported'].includes(ticket.status)) {
      setError('Aprove o snapshot antes de exportar a imagem.');
      return;
    }
    if (stakeDirty) {
      setError('Aplique o novo valor da aposta antes de exportar a imagem.');
      return;
    }

    setBusy('export');
    setError('');
    try {
      const dataUrl = await toPng(exportRef.current, {
        cacheBust: true,
        pixelRatio: 1,
        backgroundColor: '#F4F4F6',
      });

      const link = document.createElement('a');
      link.download = `placarcerto-${ticket.ticket_code}.png`;
      link.href = dataUrl;
      link.click();

      const response = await socialProofAPI.registerExport(ticket.id);
      setTicket(response.data);
      setNotice('Imagem exportada e registada no histórico.');
      await loadHistory();
    } catch (requestError) {
      console.error('Erro ao exportar imagem', requestError);
      setError(
        requestError.response?.data?.error || 'Falha ao gerar a imagem. Tente novamente.'
      );
    } finally {
      setBusy('');
    }
  };

  const handleCopyCaption = async () => {
    if (!ticket) return;
    try {
      await navigator.clipboard.writeText(buildCaption(ticket));
      setNotice('Legenda copiada para a área de transferência.');
    } catch (copyError) {
      console.error('Erro ao copiar legenda', copyError);
      setError('Não foi possível copiar a legenda.');
    }
  };

  const exportBlocked = ticket ? !['approved', 'exported'].includes(ticket.status) : true;

  return (
    <>
      <Helmet>
        <meta name="robots" content="noindex, nofollow" />
        <title>Prova Social · Admin PlacerCerto</title>
      </Helmet>

      <div className="min-h-screen bg-gray-50 pb-24 dark:bg-gray-900">
        <Header title="Prova Social" subtitle="Área reservada a administradores" />

        <div className="mx-auto w-full max-w-7xl px-4 pt-4 sm:px-6">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <button
              type="button"
              onClick={() => navigate('/admin')}
              className="inline-flex items-center gap-2 rounded-lg px-1.5 py-1 text-sm font-medium text-gray-600 transition hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-white"
            >
              <ArrowLeft size={16} />
              Voltar ao painel
            </button>
            <span className="inline-flex items-center gap-1.5 rounded-full bg-white px-3 py-1 text-[11px] font-semibold text-gray-500 ring-1 ring-inset ring-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:ring-gray-700">
              <CalendarDays size={12} />
              {formatDateLabel(date)}
            </span>
          </div>

          <div className="mb-4 flex items-start gap-2.5 rounded-xl border border-amber-500/30 bg-amber-50 px-3 py-2.5 text-xs text-amber-800 dark:bg-amber-500/10 dark:text-amber-300">
            <ShieldCheck size={15} className="mt-0.5 shrink-0" />
            <p>
              Página interna. Os bilhetes de simulação são montados depois dos resultados
              apenas para fins de marketing — nunca como previsão.
            </p>
          </div>

          {(error || notice) && (
            <div className="mb-4 space-y-2">
              {error && (
                <Alert tone="error" icon={AlertTriangle} onDismiss={() => setError('')}>
                  {error}
                </Alert>
              )}
              {notice && (
                <Alert
                  tone="success"
                  icon={CheckCircle2}
                  onDismiss={() => setNotice('')}
                >
                  {notice}
                </Alert>
              )}
            </div>
          )}

          <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div className="flex flex-wrap items-end gap-3">
              <label className="flex min-w-[168px] flex-col gap-1">
                <span className="text-[10px] font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                  Data de referência
                </span>
                <div className="relative">
                  <CalendarDays
                    size={15}
                    className="pointer-events-none absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400"
                  />
                  <input
                    type="date"
                    value={date}
                    max={localDateIso(0)}
                    onChange={(event) => setDate(event.target.value)}
                    className="w-full rounded-xl border border-gray-300 bg-white py-2 pl-8 pr-2 text-sm font-medium text-gray-900 outline-none transition focus:border-primary-500 focus:ring-2 focus:ring-primary-100 dark:border-gray-600 dark:bg-gray-900 dark:text-white dark:focus:ring-primary-500/20"
                  />
                </div>
              </label>

              <div className="flex flex-col gap-1">
                <span className="text-[10px] font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500">
                  Tipo de bilhete
                </span>
                {SOCIAL_PROOF_KINDS.length > 1 ? (
                  <div className="flex flex-wrap gap-1.5">
                    {SOCIAL_PROOF_KINDS.map((item) => (
                      <button
                        key={item.id}
                        type="button"
                        onClick={() => setKind(item.id)}
                        className={`rounded-lg px-3 py-2 text-sm font-semibold transition ${
                          kind === item.id
                            ? 'bg-primary-600 text-white shadow-sm'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200'
                        }`}
                      >
                        {item.label}
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="inline-flex items-center gap-1.5 rounded-xl bg-primary-50 px-2.5 py-2 text-sm font-semibold text-primary-700 ring-1 ring-inset ring-primary-500/20 dark:bg-primary-500/10 dark:text-primary-300 dark:ring-primary-500/20">
                    <Sparkles size={14} />
                    {activeKind?.label}
                  </div>
                )}
              </div>

              <div className="ml-auto flex w-full flex-wrap items-center gap-2 sm:w-auto">
                <button
                  type="button"
                  onClick={handleSyncResults}
                  disabled={busy === 'sync'}
                  className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl border border-gray-300 px-3 py-2 text-sm font-semibold text-gray-700 transition hover:bg-gray-50 disabled:opacity-50 sm:flex-none dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                >
                  {busy === 'sync' ? (
                    <Loader2 size={15} className="animate-spin" />
                  ) : (
                    <RefreshCw size={15} />
                  )}
                  Sincronizar
                </button>
                <button
                  type="button"
                  onClick={() => handleGenerate(null)}
                  disabled={busy === 'auto' || loadingCandidates}
                  className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-700 disabled:opacity-50 sm:flex-none"
                >
                  {busy === 'auto' ? (
                    <Loader2 size={15} className="animate-spin" />
                  ) : (
                    <Camera size={15} />
                  )}
                  Gerar snapshot
                </button>
              </div>
            </div>

            <p className="mt-3 flex items-start gap-1.5 text-xs text-gray-500 dark:text-gray-400">
              <Info size={13} className="mt-0.5 shrink-0" />
              {activeKind?.hint}
            </p>
          </section>

          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
            <StatTile label="Snapshots do dia" value={stats.total} highlight />
            <StatTile label="Pendentes" value={stats.pending} />
            <StatTile label="Aprovados" value={stats.approved} />
            <StatTile label="Exportados" value={stats.exported} />
          </div>

          <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_460px] lg:items-start">
            <div className="order-2 min-w-0 space-y-4 lg:order-none">
              <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                <div className="mb-3 flex items-center justify-between gap-2">
                  <h2 className="flex items-center gap-2 text-sm font-bold text-gray-900 dark:text-white">
                    Candidatos
                    <span className="rounded-full bg-gray-100 px-2 py-0.5 text-[11px] font-semibold text-gray-500 dark:bg-gray-700 dark:text-gray-300">
                      {candidates.length}
                    </span>
                  </h2>
                  <button
                    type="button"
                    onClick={loadCandidates}
                    disabled={loadingCandidates}
                    aria-label="Atualizar candidatos"
                    className="inline-flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-semibold text-primary-600 transition hover:bg-primary-50 disabled:opacity-50 dark:text-primary-400 dark:hover:bg-primary-500/10"
                  >
                    <RefreshCw
                      size={13}
                      className={loadingCandidates ? 'animate-spin' : undefined}
                    />
                    Atualizar
                  </button>
                </div>

                {loadingCandidates ? (
                  <div className="flex items-center gap-2 py-8 text-sm text-gray-500 dark:text-gray-400">
                    <Loader2 size={16} className="animate-spin" /> A calcular bilhetes elegíveis…
                  </div>
                ) : candidates.length === 0 ? (
                  <div className="py-8 text-center">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-200">
                      Sem candidatos para {formatDateLabel(date)}
                    </p>
                    <p className="mx-auto mt-1 max-w-sm text-xs text-gray-500 dark:text-gray-400">
                      Sincronize os resultados e confirme que existem partidas finalizadas para
                      esta data.
                    </p>
                    <button
                      type="button"
                      onClick={handleSyncResults}
                      disabled={busy === 'sync'}
                      className="mt-3 inline-flex items-center gap-1.5 rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-semibold text-gray-700 transition hover:bg-gray-50 disabled:opacity-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                    >
                      <RefreshCw size={12} /> Sincronizar agora
                    </button>
                  </div>
                ) : (
                  <ul className="space-y-2.5">
                    {candidates.map((candidate) => (
                      <li
                        key={candidate.snapshot_hash}
                        className="rounded-xl border border-gray-200 p-3 transition hover:border-primary-400/60 hover:bg-primary-50/30 dark:border-gray-700 dark:hover:border-primary-500/40 dark:hover:bg-primary-500/5"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="min-w-0">
                            <p className="truncate text-sm font-bold text-gray-900 dark:text-white">
                              {candidate.headline}
                            </p>
                            <div className="mt-1 flex flex-wrap items-center gap-1.5">
                              <span className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-1.5 py-0.5 text-[11px] font-semibold text-gray-600 dark:bg-gray-700 dark:text-gray-200">
                                Odd {Number(candidate.total_odd).toFixed(2)}
                              </span>
                              <span className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-1.5 py-0.5 text-[11px] font-semibold text-gray-600 dark:bg-gray-700 dark:text-gray-200">
                                {candidate.legs.length} seleções
                              </span>
                              <span className="inline-flex items-center gap-1 rounded-md bg-emerald-50 px-1.5 py-0.5 text-[11px] font-semibold text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300">
                                Retorno{' '}
                                {formatMzn(
                                  Number(candidate.total_odd) *
                                    (stakeValid ? parsedStake : DEFAULT_STAKE_VALUE)
                                )}
                              </span>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => handleGenerate(candidate)}
                            disabled={busy === candidate.snapshot_hash}
                            className="inline-flex shrink-0 items-center gap-1.5 rounded-lg bg-gray-900 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-gray-700 disabled:opacity-50 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-200"
                          >
                            {busy === candidate.snapshot_hash ? (
                              <Loader2 size={13} className="animate-spin" />
                            ) : (
                              <Camera size={13} />
                            )}
                            Criar
                          </button>
                        </div>

                        <ul className="mt-2 space-y-1 rounded-lg bg-gray-50 px-2 py-1.5 text-[11px] text-gray-600 dark:bg-gray-900/60 dark:text-gray-300">
                          {candidate.legs.slice(0, 4).map((leg, index) => (
                            <li key={`${candidate.snapshot_hash}-${index}`} className="truncate">
                              {leg.pick} · {leg.match} · {Number(leg.odd).toFixed(2)}
                            </li>
                          ))}
                          {candidate.legs.length > 4 && (
                            <li className="font-medium text-gray-400">
                              + {candidate.legs.length - 4} seleções
                            </li>
                          )}
                        </ul>
                      </li>
                    ))}
                  </ul>
                )}
              </section>

              <section className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <h2 className="flex items-center gap-2 text-sm font-bold text-gray-900 dark:text-white">
                    Snapshots do dia
                    <span className="rounded-full bg-gray-100 px-2 py-0.5 text-[11px] font-semibold text-gray-500 dark:bg-gray-700 dark:text-gray-300">
                      {history.length}
                    </span>
                  </h2>
                  {loadingHistory && (
                    <Loader2 size={14} className="animate-spin text-gray-400" />
                  )}
                </div>

                {history.length === 0 && !loadingHistory ? (
                  <p className="py-6 text-center text-xs text-gray-500 dark:text-gray-400">
                    Nenhum snapshot criado para esta data.
                  </p>
                ) : (
                  <ul className="space-y-0.5">
                    {history.map((item) => {
                      const isSelected = ticket?.id === item.id;
                      return (
                        <li key={item.id}>
                          <button
                            type="button"
                            onClick={() => handleSelectTicket(item.id)}
                            disabled={busy === `load-${item.id}`}
                            className={`flex w-full items-center gap-2 rounded-xl px-2 py-2 text-left transition disabled:opacity-60 ${
                              isSelected
                                ? 'bg-primary-50 ring-1 ring-inset ring-primary-500/30 dark:bg-primary-500/10'
                                : 'hover:bg-gray-50 dark:hover:bg-gray-700/50'
                            }`}
                          >
                            <div className="min-w-0 flex-1">
                              <p className="truncate text-sm font-semibold text-gray-900 dark:text-white">
                                {item.headline}
                              </p>
                              <p className="truncate text-[11px] text-gray-500 dark:text-gray-400">
                                {item.ticket_code} · {item.reserve_code}
                              </p>
                            </div>
                            <StatusBadge status={item.status} label={item.status_display} />
                            {busy === `load-${item.id}` ? (
                              <Loader2 size={14} className="animate-spin text-gray-400" />
                            ) : (
                              <ChevronRight
                                size={14}
                                className="shrink-0 text-gray-300 dark:text-gray-500"
                              />
                            )}
                          </button>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </section>
            </div>

            <div className="order-1 min-w-0 lg:order-none lg:sticky lg:top-4">
              {!ticket ? (
                <div className="rounded-2xl border border-dashed border-gray-300 bg-white/60 p-6 text-center dark:border-gray-600 dark:bg-gray-800/40">
                  <Camera size={26} className="mx-auto text-gray-300 dark:text-gray-600" />
                  <p className="mt-2 text-sm font-semibold text-gray-700 dark:text-gray-200">
                    Nenhum snapshot aberto
                  </p>
                  <p className="mx-auto mt-1 max-w-xs text-xs text-gray-500 dark:text-gray-400">
                    Defina o valor da aposta e gere um snapshot, ou abra um snapshot do dia na
                    lista.
                  </p>

                  <label
                    htmlFor="social-proof-stake"
                    className="mt-4 flex flex-col items-center gap-1 text-[10px] font-semibold uppercase tracking-wide text-gray-400 dark:text-gray-500"
                  >
                    Valor da aposta ao gerar
                    <div className="relative">
                      <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-xs font-bold text-gray-400">
                        MT
                      </span>
                      <input
                        id="social-proof-stake"
                        type="number"
                        inputMode="decimal"
                        min={MIN_STAKE_VALUE}
                        max={MAX_STAKE_VALUE}
                        step="any"
                        value={stakeInput}
                        onChange={(event) => setStakeInput(event.target.value)}
                        aria-invalid={!stakeValid}
                        className={`w-32 rounded-xl border bg-white py-2 pl-10 pr-3 text-sm font-bold tabular-nums text-gray-900 outline-none transition focus:ring-2 dark:bg-gray-900 dark:text-white ${
                          stakeValid
                            ? 'border-gray-300 focus:border-primary-500 focus:ring-primary-100 dark:border-gray-600 dark:focus:ring-primary-500/20'
                            : 'border-rose-400 focus:border-rose-500 focus:ring-rose-100 dark:border-rose-500/60'
                        }`}
                      />
                    </div>
                    <span className="text-[11px] font-normal normal-case tracking-normal text-gray-400">
                      mínimo {formatMzn(MIN_STAKE_VALUE)}
                    </span>
                  </label>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
                    <div className="mb-3 flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="truncate text-sm font-bold text-gray-900 dark:text-white">
                          {ticket.headline}
                        </p>
                        <p className="truncate text-[11px] text-gray-500 dark:text-gray-400">
                          Ref {ticket.ticket_code} · {ticket.reserve_code}
                        </p>
                      </div>
                      <StatusBadge status={ticket.status} label={ticket.status_display} />
                    </div>

                    <div
                      className="w-full overflow-hidden rounded-xl bg-[#F4F4F6]"
                      style={{ height: sheetSize.height * previewScale || undefined }}
                    >
                      <div
                        style={{
                          transform: `scale(${previewScale})`,
                          transformOrigin: 'top left',
                          width: BASE_WIDTH,
                        }}
                      >
                        <SocialProofPreview
                          ref={sheetRef}
                          ticket={ticket}
                          scale={1}
                          stakeValue={previewStake}
                        />
                      </div>
                    </div>

                    <form
                      noValidate
                      onSubmit={handleApplyStake}
                      className="mt-3 rounded-xl border border-gray-200 bg-gray-50/80 p-3 dark:border-gray-700 dark:bg-gray-900/40"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <label
                          htmlFor="social-proof-stake"
                          className="inline-flex items-center gap-1.5 text-xs font-bold text-gray-700 dark:text-gray-200"
                        >
                          <Wallet size={14} className="text-gray-400" />
                          Valor da aposta
                        </label>
                        {stakeDirty && (
                          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-amber-700 dark:bg-amber-500/15 dark:text-amber-300">
                            Por aplicar
                          </span>
                        )}
                      </div>

                      <div className="mt-2 flex items-stretch gap-2">
                        <div className="relative flex-1">
                          <span className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-xs font-bold text-gray-400">
                            MT
                          </span>
                          <input
                            id="social-proof-stake"
                            type="number"
                            inputMode="decimal"
                            min={MIN_STAKE_VALUE}
                            max={MAX_STAKE_VALUE}
                            step="any"
                            value={stakeInput}
                            onChange={(event) => setStakeInput(event.target.value)}
                            aria-invalid={!stakeValid}
                            aria-describedby="social-proof-stake-hint"
                            className={`w-full rounded-xl border bg-white py-2 pl-10 pr-3 text-sm font-bold tabular-nums text-gray-900 outline-none transition focus:ring-2 dark:bg-gray-900 dark:text-white ${
                              stakeValid
                                ? 'border-gray-300 focus:border-primary-500 focus:ring-primary-100 dark:border-gray-600 dark:focus:ring-primary-500/20'
                                : 'border-rose-400 focus:border-rose-500 focus:ring-rose-100 dark:border-rose-500/60'
                            }`}
                          />
                        </div>
                        <button
                          type="submit"
                          disabled={!canApplyStake}
                          className="inline-flex shrink-0 items-center gap-1.5 rounded-xl bg-gray-900 px-3 py-2 text-xs font-bold text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-200"
                        >
                          {busy === 'stake' ? (
                            <Loader2 size={13} className="animate-spin" />
                          ) : (
                            <Check size={13} />
                          )}
                          Aplicar
                        </button>
                      </div>

                      <div className="mt-2 flex flex-wrap items-center justify-between gap-x-3 gap-y-1">
                        <p
                          id="social-proof-stake-hint"
                          className={`text-[11px] ${
                            stakeValid
                              ? 'text-gray-500 dark:text-gray-400'
                              : 'font-semibold text-rose-600 dark:text-rose-400'
                          }`}
                        >
                          {stakeValid
                            ? `Na imagem: ${formatMzn(appliedStake)} · mínimo ${formatMzn(
                                MIN_STAKE_VALUE
                              )}`
                            : `Informe um valor entre ${formatMzn(
                                MIN_STAKE_VALUE
                              )} e ${formatMzn(MAX_STAKE_VALUE)}.`}
                        </p>
                        <p className="text-[11px] text-gray-500 dark:text-gray-400">
                          Retorno{' '}
                          <strong className="font-bold tabular-nums text-gray-800 dark:text-gray-100">
                            {formatMzn(previewStake * totalOdd)}
                          </strong>
                        </p>
                      </div>
                    </form>

                    <div className="mt-3 grid grid-cols-2 gap-2">
                      <button
                        type="button"
                        onClick={handleApprove}
                        disabled={
                          busy === 'approve' || ['approved', 'exported'].includes(ticket.status)
                        }
                        className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-40"
                      >
                        {busy === 'approve' ? (
                          <Loader2 size={15} className="animate-spin" />
                        ) : (
                          <Check size={15} />
                        )}
                        {['approved', 'exported'].includes(ticket.status) ? 'Aprovado' : 'Aprovar'}
                      </button>

                      <button
                        type="button"
                        onClick={handleDownload}
                        disabled={busy === 'export' || exportBlocked}
                        title={exportBlocked ? 'Aprove o snapshot antes de exportar' : undefined}
                        className="inline-flex items-center justify-center gap-2 rounded-xl bg-sky-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-sky-700 disabled:opacity-40"
                      >
                        {busy === 'export' ? (
                          <Loader2 size={15} className="animate-spin" />
                        ) : (
                          <Download size={15} />
                        )}
                        PNG 1080px
                      </button>

                      <button
                        type="button"
                        onClick={handleCopyCaption}
                        className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                      >
                        <Copy size={15} />
                        Legenda
                      </button>

                      <button
                        type="button"
                        onClick={handleDiscard}
                        disabled={busy === 'discard'}
                        className="inline-flex items-center justify-center gap-2 rounded-xl border border-red-500/40 px-3 py-2 text-sm font-medium text-red-600 transition hover:bg-red-50 disabled:opacity-40 dark:text-red-400 dark:hover:bg-red-500/10"
                      >
                        {busy === 'discard' ? (
                          <Loader2 size={15} className="animate-spin" />
                        ) : (
                          <Trash2 size={15} />
                        )}
                        Descartar
                      </button>
                    </div>

                    {exportBlocked && (
                      <p className="mt-2 flex items-start gap-1.5 text-[11px] text-amber-600 dark:text-amber-400">
                        <AlertTriangle size={13} className="mt-0.5 shrink-0" />
                        Exportação bloqueada até o snapshot ser aprovado.
                      </p>
                    )}
                  </div>

                  <div className="rounded-2xl border border-gray-200 bg-white p-3 text-[11px] text-gray-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400">
                    <p>
                      <strong className="font-semibold text-gray-700 dark:text-gray-200">
                        Aviso na imagem:
                      </strong>{' '}
                      {ticket.disclosure}
                    </p>
                    <p className="mt-1.5 flex items-center gap-1.5">
                      <ChevronRight size={12} className="shrink-0" />
                      Exportações: {ticket.export_count ?? 0}
                      {ticket.last_exported_at
                        ? ` · última em ${new Date(ticket.last_exported_at).toLocaleString(
                            'pt-PT'
                          )}`
                        : ''}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Nó de exportação em tamanho real (1080px), fora do ecrã */}
        {ticket && (
          <div
            aria-hidden="true"
            style={{ position: 'fixed', left: '-10000px', top: 0, pointerEvents: 'none' }}
          >
            <SocialProofPreview
              ref={exportRef}
              ticket={ticket}
              scale={EXPORT_WIDTH / BASE_WIDTH}
              stakeValue={previewStake}
            />
          </div>
        )}

        <BottomNav />
      </div>
    </>
  );
}
