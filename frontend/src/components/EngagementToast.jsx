import { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { X, BookOpen, Gift, Target, Wallet, Shield, Coins } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { affiliateAPI, notificationAPI } from '../services/api';

const EVENT_PREFIXES = [
  'member_referral_reward_',
  'affiliate_referral_registered_',
  'affiliate_withdrawal_paid_',
  'affiliate:',
];

const EDUCATIONAL_MESSAGES = [
  {
    icon: Target,
    title: 'Probabilidade não é certeza',
    body: 'Uma probabilidade representa uma estimativa com base nos dados disponíveis. Não prevê com certeza o resultado de uma partida.',
  },
  {
    icon: BookOpen,
    title: 'Como são feitas as estimativas?',
    body: 'As análises combinam modelos estatísticos, como Poisson Bivariado e Regressão Logística, com dados das partidas.',
  },
  {
    icon: Shield,
    title: 'O futebol continua imprevisível',
    body: 'Lesões, decisões durante o jogo e outros fatores podem alterar o resultado. Use as análises para compreender dados, não como garantia.',
  },
  {
    icon: Coins,
    title: 'Limites dos planos',
    body: 'O plano gratuito permite até 3 análises por dia. O Premium Vitalício custa 250 MZN, é pago uma vez e permite até 60 análises por dia.',
  },
  {
    icon: Shield,
    title: 'Divulgação responsável',
    body: 'O PlacarCerto é um serviço educativo de análise estatística, não uma casa de apostas. Análises não são recomendações para apostar nem promessa de ganhos.',
  },
  {
    icon: BookOpen,
    title: 'Forma recente é apenas contexto',
    body: 'Os resultados recentes ajudam a descrever o momento das equipas, mas não determinam como será a próxima partida.',
  },
  {
    icon: Target,
    title: 'Considere o fator casa e fora',
    body: 'O desempenho de uma equipa pode variar conforme joga em casa ou fora. Compare esses contextos quando os dados estiverem disponíveis.',
  },
  {
    icon: BookOpen,
    title: 'Confrontos diretos não contam tudo',
    body: 'Jogos anteriores entre duas equipas são apenas uma parte da análise: plantéis, treinadores e contexto podem mudar.',
  },
  {
    icon: Target,
    title: 'Estimativa de golos não é placar exato',
    body: 'Modelos de golos calculam cenários prováveis a partir de dados estatísticos; não indicam um resultado final garantido.',
  },
  {
    icon: Shield,
    title: 'Atenção ao tamanho da amostra',
    body: 'Uma sequência curta de partidas pode não representar o nível habitual de uma equipa. Interprete tendências com cautela.',
  },
  {
    icon: BookOpen,
    title: 'Observe mais de um indicador',
    body: 'Forma, golos e outros dados mostram ângulos diferentes da partida. Um único indicador não resume todo o desempenho.',
  },
  {
    icon: Shield,
    title: 'Dados podem estar incompletos',
    body: 'A disponibilidade de estatísticas varia entre partidas e competições. Considere essa limitação ao interpretar uma análise.',
  },
  {
    icon: Target,
    title: 'Probabilidades ajudam a comparar cenários',
    body: 'Use as probabilidades para entender quais cenários são mais ou menos prováveis segundo o modelo, sem as confundir com certezas.',
  },
];

const PREMIUM_MESSAGES = [
  {
    icon: Coins,
    title: 'Mais análises com o Premium',
    body: 'O Premium Vitalício oferece até 60 análises por dia, por um pagamento único de 250 MZN. O plano gratuito permite até 3 análises diárias.',
  },
  {
    icon: Target,
    title: 'Alertas de análises no app',
    body: 'O Premium inclui alertas de análises diretamente na aplicação, para acompanhar quando uma análise estiver disponível.',
  },
  {
    icon: BookOpen,
    title: 'Consulte o histórico de análises',
    body: 'O Premium inclui acesso ilimitado ao histórico das suas análises, conforme os recursos descritos no plano.',
  },
];

const NON_AFFILIATE_MESSAGES = [
  {
    icon: Gift,
    title: 'Conheça o programa de afiliados',
    body: 'Afiliados podem receber uma comissão única de 100 MZN por primeira compra elegível confirmada, sujeita às regras e validação de 14 dias.',
  },
  {
    icon: Shield,
    title: 'Divulgue com transparência',
    body: 'O programa é para divulgar o PlacarCerto como serviço educativo. A participação não permite prometer ganhos nem promover apostas.',
  },
];

const AFFILIATE_MESSAGES = [
  {
    icon: Coins,
    title: 'Quando uma comissão fica disponível',
    body: 'A comissão elegível fica pendente por 14 dias após o pagamento. Depois da validação, pode ficar disponível se não houver reembolso, contestação ou indício de fraude.',
  },
  {
    icon: Wallet,
    title: 'Condições para pedir levantamento',
    body: 'O pedido mínimo é 200 MZN e aplica-se uma taxa de processamento de 6%. O painel mostra o valor líquido antes da confirmação.',
  },
  {
    icon: Wallet,
    title: 'Prazo de processamento',
    body: 'Pedidos de levantamento válidos são processados em até 5 dias úteis. Este é um aviso informativo, não uma confirmação de pagamento ou de saldo.',
  },
];

const EDUCATIONAL_TOASTS_PER_VISIT = 3;
const EDUCATIONAL_TOAST_DURATION_MS = 8000;
const TOAST_GAP_MS = 4000;

function readSeenEvents(userId) {
  try {
    return new Set(JSON.parse(localStorage.getItem(`engagement-toast-events-${userId}`) || '[]'));
  } catch {
    return new Set();
  }
}

export default function EngagementToast() {
  const { user } = useAuth();
  const { pathname } = useLocation();
  const [toast, setToast] = useState(null);
  const [toastQueue, setToastQueue] = useState([]);
  const toastRef = useRef(toast);
  const hasShownToastRef = useRef(false);
  const timerRef = useRef(null);
  toastRef.current = toast;
  if (toast) hasShownToastRef.current = true;

  useEffect(() => {
    if (!user) return undefined;
    let active = true;
    const seenEvents = readSeenEvents(user.id);
    const educationalSessionKey = `engagement-toasts-session-${user.id}`;
    let loadingEvents = false;

    const loadRealEvents = async () => {
      if (loadingEvents) return;
      loadingEvents = true;
      try {
        const { data } = await notificationAPI.getAll();
        if (!active) return;
        const items = data.results || [];
        const newEvents = items.filter((item) => (
          !item.read
          && EVENT_PREFIXES.some((prefix) => item.event_key?.startsWith(prefix))
          && !seenEvents.has(String(item.id))
        ));
        if (!newEvents.length) return;

        newEvents.forEach((event) => seenEvents.add(String(event.id)));
        localStorage.setItem(
          `engagement-toast-events-${user.id}`,
          JSON.stringify([...seenEvents].slice(-50)),
        );
        const eventToasts = newEvents.map((event) => {
          const isAffiliateEvent = event.event_key.startsWith('affiliate:');
          return {
            id: `event-${event.id}`,
            icon: event.event_key.includes('withdrawal') ? Wallet
              : event.event_key.includes('commission') ? Coins : Gift,
            title: event.title,
            body: event.body,
            action: 'Ver detalhes',
            href: isAffiliateEvent || event.event_key.startsWith('affiliate_')
              ? '/affiliate'
              : event.url || '/member-referrals',
          };
        });
        if (!toastRef.current || toastRef.current.educational) {
          setToast(eventToasts[0]);
          setToastQueue((currentQueue) => [...eventToasts.slice(1), ...currentQueue]);
        } else {
          setToastQueue((currentQueue) => [...eventToasts, ...currentQueue]);
        }
      } catch (error) {
        console.error('Não foi possível verificar novidades da conta:', error);
      } finally {
        loadingEvents = false;
      }
    };

    loadRealEvents();
    const intervalId = window.setInterval(loadRealEvents, 60000);

    if (!sessionStorage.getItem(educationalSessionKey)) {
      timerRef.current = window.setTimeout(() => {
        if (!active || sessionStorage.getItem(educationalSessionKey)) return;
        if (pathname.startsWith('/payment/confirmation')) return;

        const loadProfileMessages = async () => {
          let isAffiliate = false;
          try {
            await affiliateAPI.getMe();
            isAffiliate = true;
          } catch (error) {
            if (error.response?.status === 404) {
              isAffiliate = false;
            } else if (
              error.response?.status === 403
              && error.response?.data?.code === 'affiliate_terms_required'
            ) {
              isAffiliate = true;
            } else {
              console.error('Não foi possível verificar o perfil de afiliado:', error);
            }
          }

          if (!active || sessionStorage.getItem(educationalSessionKey)) return;
          const profileMessages = [
            ...(!user.is_premium_active ? PREMIUM_MESSAGES : []),
            ...(isAffiliate ? AFFILIATE_MESSAGES : NON_AFFILIATE_MESSAGES),
          ];
          const messages = [
            ...EDUCATIONAL_MESSAGES,
            ...profileMessages,
          ];
          const cursorKey = `engagement-toasts-cursor-${user.id}`;
          const savedCursor = Number(localStorage.getItem(cursorKey) || 0);
          const startIndex = Number.isInteger(savedCursor) && savedCursor >= 0
            ? savedCursor % messages.length
            : 0;
          const visitMessages = Array.from(
            { length: Math.min(EDUCATIONAL_TOASTS_PER_VISIT, messages.length) },
            (_, index) => messages[(startIndex + index) % messages.length],
          );
          localStorage.setItem(
            cursorKey,
            String((startIndex + visitMessages.length) % messages.length),
          );
          setToastQueue((currentQueue) => [...currentQueue, ...visitMessages.map((message, index) => ({
            ...message,
            id: `education-${startIndex}-${index}`,
            educational: true,
          }))]);
          sessionStorage.setItem(educationalSessionKey, '1');
        };

        loadProfileMessages();
      }, 4500);
    }

    return () => {
      active = false;
      window.clearInterval(intervalId);
      window.clearTimeout(timerRef.current);
    };
  }, [pathname, user]);

  useEffect(() => {
    if (toast || !toastQueue.length) return undefined;
    const timeoutId = window.setTimeout(() => {
      setToast(toastQueue[0]);
      setToastQueue(toastQueue.slice(1));
    }, hasShownToastRef.current ? TOAST_GAP_MS : 0);
    return () => window.clearTimeout(timeoutId);
  }, [toast, toastQueue]);

  useEffect(() => {
    if (!toast?.educational) return undefined;
    const timeoutId = window.setTimeout(() => setToast(null), EDUCATIONAL_TOAST_DURATION_MS);
    return () => window.clearTimeout(timeoutId);
  }, [toast]);

  if (!toast) return null;
  const Icon = toast.icon;

  return (
    <aside
      key={toast.id}
      role="status"
      aria-live="polite"
      className="fixed bottom-20 left-4 right-4 z-[10000] ml-auto max-w-sm rounded-2xl border border-primary-200 bg-white p-4 text-gray-900 shadow-2xl dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 sm:bottom-6"
    >
      <div className="flex items-start gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-50 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300">
          <Icon className="h-5 w-5" />
        </span>
        <div className="min-w-0 flex-1">
          {toast.educational && (
            <p className="text-xs font-semibold uppercase tracking-wide text-primary-600 dark:text-primary-400">
              Dica educativa
            </p>
          )}
          <p className="pr-5 text-sm font-bold">{toast.title}</p>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{toast.body}</p>
          {!toast.educational && (
            <Link
              to={toast.href}
              onClick={() => setToast(null)}
              className="mt-3 inline-flex rounded-lg bg-primary-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-primary-700"
            >
              {toast.action}
            </Link>
          )}
        </div>
        <button
          type="button"
          onClick={() => setToast(null)}
          aria-label={`Fechar aviso: ${toast.title}`}
          className="absolute right-3 top-3 rounded-lg p-1 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </aside>
  );
}
