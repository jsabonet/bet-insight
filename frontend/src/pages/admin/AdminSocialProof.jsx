import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { toPng } from 'html-to-image';
import {
  AlertTriangle,
  ArrowLeft,
  Camera,
  Check,
  Copy,
  Download,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Trash2,
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

const UNIT_VALUE = 100;
const STAKE_OPTIONS = [
  { units: 5, label: 'MT 500' },
  { units: 10, label: 'MT 1 000' },
  { units: 25, label: 'MT 2 500' },
  { units: 50, label: 'MT 5 000' },
];

function localDateIso(offsetDays = 0) {
  const date = new Date();
  date.setDate(date.getDate() + offsetDays);
  const pad = (value) => String(value).padStart(2, '0');
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
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

function StatusBadge({ status, label }) {
  const styles = {
    candidate: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    approved: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    exported: 'bg-sky-500/15 text-sky-400 border-sky-500/30',
    discarded: 'bg-gray-500/15 text-gray-400 border-gray-500/30',
  };

  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold ${
        styles[status] || styles.candidate
      }`}
    >
      {label}
    </span>
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
  const [stakeUnits, setStakeUnits] = useState(10);

  const [loadingCandidates, setLoadingCandidates] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [confirmSimulation, setConfirmSimulation] = useState(false);
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

  const isSimulation = kind === 'simulation';
  const activeKind = SOCIAL_PROOF_KINDS.find((item) => item.id === kind);

  const loadHistory = useCallback(async () => {
    setLoadingHistory(true);
    try {
      const response = await socialProofAPI.getTickets({ date, limit: 50 });
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
    setConfirmSimulation(false);
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
      const payload = { date, kind };
      if (candidate?.snapshot_hash) payload.snapshot_hash = candidate.snapshot_hash;
      if (isSimulation) payload.confirm_simulation = true;

      const response = await socialProofAPI.generate(payload);
      setTicket(response.data);
      setStakeUnits(response.data.stake_units || 10);
      setNotice(
        response.data.created
          ? 'Snapshot criado. Reveja a imagem antes de aprovar.'
          : 'Já existia um snapshot igual para esta data. A carregar o existente.'
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
      setStakeUnits(response.data.stake_units || 10);
    } catch (requestError) {
      setError(requestError.response?.data?.error || 'Falha ao carregar o snapshot.');
    } finally {
      setBusy('');
    }
  };

  const handleApprove = async () => {
    if (!ticket) return;
    setBusy('approve');
    setError('');
    try {
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
      setError('Falha ao gerar a imagem. Tente novamente.');
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

  return (
    <>
      <Helmet>
        <meta name="robots" content="noindex, nofollow" />
        <title>Prova Social · Admin PlacerCerto</title>
      </Helmet>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-24">
        <Header title="Prova Social" subtitle="Área reservada a administradores" />

        <div className="mx-auto w-full max-w-6xl px-4 pt-4 sm:px-6">
          <button
            type="button"
            onClick={() => navigate('/admin')}
            className="mb-4 inline-flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white"
          >
            <ArrowLeft size={16} />
            Voltar ao painel
          </button>

          <div className="mb-4 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-800 dark:text-amber-300">
            <div className="flex items-start gap-3">
              <ShieldCheck size={18} className="mt-0.5 shrink-0" />
              <p>
                Página interna. Use apenas bilhetes reais gerados antes dos jogos. Bilhetes de
                simulação são montados depois dos resultados e saem <strong>sempre</strong> com
                marca de água e aviso de simulação.
              </p>
            </div>
          </div>

          {error && (
            <div className="mb-4 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-700 dark:text-red-300">
              {error}
            </div>
          )}
          {notice && (
            <div className="mb-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-700 dark:text-emerald-300">
              {notice}
            </div>
          )}

          <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_440px]">
            <div className="space-y-4">
              <div className="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
                <div className="flex flex-wrap items-center gap-3">
                  <label className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                    Data
                    <input
                      type="date"
                      value={date}
                      max={localDateIso(0)}
                      onChange={(event) => setDate(event.target.value)}
                      className="rounded-lg border border-gray-300 bg-white px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-900 dark:text-white"
                    />
                  </label>

                  <button
                    type="button"
                    onClick={handleSyncResults}
                    disabled={busy === 'sync'}
                    className="inline-flex items-center gap-2 rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                  >
                    {busy === 'sync' ? (
                      <Loader2 size={14} className="animate-spin" />
                    ) : (
                      <RefreshCw size={14} />
                    )}
                    Sincronizar resultados
                  </button>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {SOCIAL_PROOF_KINDS.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => setKind(item.id)}
                      className={`rounded-full px-3 py-1.5 text-sm font-medium transition ${
                        kind === item.id
                          ? 'bg-primary-600 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200'
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>

                <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">{activeKind?.hint}</p>

                {isSimulation && (
                  <label className="mt-3 flex items-start gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 text-xs text-amber-700 dark:text-amber-300">
                    <input
                      type="checkbox"
                      checked={confirmSimulation}
                      onChange={(event) => setConfirmSimulation(event.target.checked)}
                      className="mt-0.5"
                    />
                    Confirmo que este bilhete é uma simulação pós-jogo, será publicado com marca de
                    água e não será apresentado como previsão.
                  </label>
                )}

                <button
                  type="button"
                  onClick={() => handleGenerate(null)}
                  disabled={busy === 'auto' || (isSimulation && !confirmSimulation)}
                  className="mt-4 inline-flex items-center gap-2 rounded-xl bg-primary-600 px-4 py-2 text-sm font-semibold text-white hover:bg-primary-700 disabled:opacity-50"
                >
                  {busy === 'auto' ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Camera size={16} />
                  )}
                  Gerar snapshot automático
                </button>
              </div>

              <div className="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
                <div className="mb-3 flex items-center justify-between">
                  <h2 className="text-sm font-semibold text-gray-900 dark:text-white">
                    Candidatos ({candidates.length})
                  </h2>
                  <button
                    type="button"
                    onClick={loadCandidates}
                    className="text-xs font-medium text-primary-600 hover:underline dark:text-primary-400"
                  >
                    Atualizar
                  </button>
                </div>

                {loadingCandidates ? (
                  <div className="flex items-center gap-2 py-6 text-sm text-gray-500 dark:text-gray-400">
                    <Loader2 size={16} className="animate-spin" /> A calcular bilhetes elegíveis…
                  </div>
                ) : candidates.length === 0 ? (
                  <p className="py-6 text-sm text-gray-500 dark:text-gray-400">
                    Sem candidatos para esta data. Sincronize os resultados e confirme que existem
                    bilhetes gerados antes do início dos jogos.
                  </p>
                ) : (
                  <ul className="space-y-3">
                    {candidates.map((candidate) => (
                      <li
                        key={candidate.snapshot_hash}
                        className="rounded-xl border border-gray-200 p-3 dark:border-gray-700"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div>
                            <p className="text-sm font-semibold text-gray-900 dark:text-white">
                              {candidate.headline}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              Odd total {Number(candidate.total_odd).toFixed(2)} · Retorno{' '}
                              {formatMzn(candidate.total_odd * 10 * UNIT_VALUE)}
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => handleGenerate(candidate)}
                            disabled={busy === candidate.snapshot_hash}
                            className="inline-flex items-center gap-1.5 rounded-lg bg-gray-900 px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-50 dark:bg-white dark:text-gray-900"
                          >
                            {busy === candidate.snapshot_hash ? (
                              <Loader2 size={13} className="animate-spin" />
                            ) : (
                              <Check size={13} />
                            )}
                            Criar snapshot
                          </button>
                        </div>

                        <ol className="mt-2 space-y-1 text-xs text-gray-600 dark:text-gray-300">
                          {candidate.legs.slice(0, 4).map((leg, index) => (
                            <li key={`${candidate.snapshot_hash}-${index}`} className="truncate">
                              {leg.pick} · {leg.match} · {Number(leg.odd).toFixed(2)}
                            </li>
                          ))}
                          {candidate.legs.length > 4 && (
                            <li className="text-gray-400">
                              + {candidate.legs.length - 4} seleções
                            </li>
                          )}
                        </ol>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              <div className="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
                <h2 className="mb-3 text-sm font-semibold text-gray-900 dark:text-white">
                  Snapshots do dia ({history.length})
                </h2>

                {loadingHistory ? (
                  <div className="flex items-center gap-2 py-3 text-sm text-gray-500 dark:text-gray-400">
                    <Loader2 size={16} className="animate-spin" /> A carregar…
                  </div>
                ) : history.length === 0 ? (
                  <p className="py-3 text-sm text-gray-500 dark:text-gray-400">
                    Nenhum snapshot criado para esta data.
                  </p>
                ) : (
                  <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                    {history.map((item) => (
                      <li key={item.id} className="flex items-center justify-between gap-3 py-2">
                        <div className="min-w-0">
                          <p className="truncate text-sm font-medium text-gray-900 dark:text-white">
                            {item.headline}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {item.ticket_code} · {item.kind_display}
                          </p>
                        </div>
                        <div className="flex shrink-0 items-center gap-2">
                          <StatusBadge status={item.status} label={item.status_display} />
                          <button
                            type="button"
                            onClick={() => handleSelectTicket(item.id)}
                            disabled={busy === `load-${item.id}`}
                            className="rounded-lg border border-gray-300 px-2 py-1 text-xs font-medium text-gray-700 disabled:opacity-50 dark:border-gray-600 dark:text-gray-200"
                          >
                            Abrir
                          </button>
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            <div className="space-y-4">
              {!ticket ? (
                <div className="rounded-2xl border border-dashed border-gray-300 p-8 text-center text-sm text-gray-500 dark:border-gray-600 dark:text-gray-400">
                  Crie um snapshot para ver a pré-visualização do bilhete.
                </div>
              ) : (
                <>
                  <div className="rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
                    <div className="mb-3 flex items-center justify-between gap-2">
                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold text-gray-900 dark:text-white">
                          {ticket.headline}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {ticket.ticket_code}
                        </p>
                      </div>
                      <StatusBadge status={ticket.status} label={ticket.status_display} />
                    </div>

                    <div
                      className="w-full overflow-hidden"
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
                          stakeUnits={stakeUnits}
                          unitValue={UNIT_VALUE}
                        />
                      </div>
                    </div>

                    <div className="mt-4">
                      <label className="text-xs font-medium text-gray-500 dark:text-gray-400">
                        Valor da aposta
                        <select
                          value={stakeUnits}
                          onChange={(event) => setStakeUnits(Number(event.target.value))}
                          className="ml-2 rounded-lg border border-gray-300 bg-white px-2 py-1 text-xs dark:border-gray-600 dark:bg-gray-900 dark:text-white"
                        >
                          {STAKE_OPTIONS.map((option) => (
                            <option key={option.units} value={option.units}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      </label>
                      <p className="mt-1 text-[11px] text-gray-400">
                        Valor apenas para a imagem. Odd total fixa no snapshot.
                      </p>
                    </div>

                    <div className="mt-4 grid grid-cols-2 gap-2">
                      <button
                        type="button"
                        onClick={handleApprove}
                        disabled={
                          busy === 'approve' || ['approved', 'exported'].includes(ticket.status)
                        }
                        className="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50"
                      >
                        {busy === 'approve' ? (
                          <Loader2 size={15} className="animate-spin" />
                        ) : (
                          <Check size={15} />
                        )}
                        Aprovar
                      </button>

                      <button
                        type="button"
                        onClick={handleDownload}
                        disabled={busy === 'export'}
                        className="inline-flex items-center justify-center gap-2 rounded-xl bg-sky-600 px-3 py-2 text-sm font-semibold text-white hover:bg-sky-700 disabled:opacity-50"
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
                        className="inline-flex items-center justify-center gap-2 rounded-xl border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                      >
                        <Copy size={15} />
                        Copiar legenda
                      </button>

                      <button
                        type="button"
                        onClick={handleDiscard}
                        disabled={busy === 'discard'}
                        className="inline-flex items-center justify-center gap-2 rounded-xl border border-red-500/40 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-500/10 disabled:opacity-50 dark:text-red-400"
                      >
                        {busy === 'discard' ? (
                          <Loader2 size={15} className="animate-spin" />
                        ) : (
                          <Trash2 size={15} />
                        )}
                        Descartar
                      </button>
                    </div>

                    {ticket.status === 'candidate' && (
                      <p className="mt-3 flex items-start gap-2 text-[11px] text-amber-600 dark:text-amber-400">
                        <AlertTriangle size={13} className="mt-0.5 shrink-0" />
                        Exportação bloqueada até o snapshot ser aprovado.
                      </p>
                    )}
                  </div>

                  <div className="rounded-2xl border border-gray-200 bg-white p-4 text-xs text-gray-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400">
                    <p>
                      <strong className="text-gray-700 dark:text-gray-200">Aviso na imagem:</strong>{' '}
                      {ticket.disclosure}
                    </p>
                    <p className="mt-2">
                      Exportações: {ticket.export_count} · Última:{' '}
                      {ticket.last_exported_at
                        ? new Date(ticket.last_exported_at).toLocaleString('pt-PT')
                        : '—'}
                    </p>
                  </div>
                </>
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
              stakeUnits={stakeUnits}
              unitValue={UNIT_VALUE}
            />
          </div>
        )}

        <BottomNav />
      </div>
    </>
  );
}
