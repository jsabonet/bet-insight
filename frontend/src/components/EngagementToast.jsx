import { useEffect, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { X, BookOpen, Gift, Target, Wallet } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { notificationAPI } from '../services/api';

const EVENT_PREFIXES = [
  'member_referral_reward_',
  'affiliate_referral_registered_',
  'affiliate_withdrawal_paid_',
];

function getDailyMessage(pathname, isPremium) {
  if (pathname.startsWith('/payment/confirmation')) return null;

  const dayOfYear = Math.floor(
    (Date.now() - new Date(new Date().getFullYear(), 0, 0).getTime()) / 86400000,
  );

  if (pathname === '/daily-bets') {
    return isPremium
      ? {
          icon: Target,
          title: 'As seleções do dia estão disponíveis',
          body: 'Consulte os jogos e os critérios estatísticos antes de tomar qualquer decisão.',
          action: 'Ver seleções',
          href: '/daily-bets',
        }
      : {
          icon: Target,
          title: 'Bilhetes diários para membros Premium',
          body: 'Compare os planos para consultar as seleções do dia. Nenhuma análise garante resultados.',
          action: 'Ver planos',
          href: '/premium',
        };
  }

  if (pathname.startsWith('/match/') || pathname === '/my-analyses') {
    return {
      icon: BookOpen,
      title: 'Aprenda a interpretar as análises',
      body: 'Consulte o guia educativo e lembre-se: probabilidades não são garantias.',
      action: 'Abrir FAQ',
      href: '/faq',
    };
  }

  if (isPremium) {
    if (pathname === '/profile' && dayOfYear % 3 === 0) {
      return {
        icon: Gift,
        title: 'Partilhe o PlacarCerto',
        body: 'O programa de afiliados oferece comissões por vendas confirmadas. Consulte as regras e condições.',
        action: 'Ver afiliados',
        href: '/affiliate',
      };
    }
    return {
      icon: Target,
      title: 'Já consultou os bilhetes de hoje?',
      body: 'As seleções diárias estão na área própria. Analise os dados com responsabilidade.',
      action: 'Ver bilhetes',
      href: '/daily-bets',
    };
  }

  if (dayOfYear % 3 === 1) {
    return {
      icon: Target,
      title: 'Conheça os planos disponíveis',
      body: 'Compare os limites e benefícios atuais para escolher o plano adequado.',
      action: 'Comparar planos',
      href: '/premium',
    };
  }

  if (dayOfYear % 3 === 2) {
    return {
      icon: Gift,
      title: 'Indique o serviço e receba comissão',
      body: 'O programa de afiliados oferece comissões por vendas confirmadas, sujeito às regras do programa.',
      action: 'Ver afiliados',
      href: '/affiliate',
    };
  }

  return {
    icon: Gift,
    title: 'Convide um amigo e ganhem análises',
    body: 'Quando o seu convidado concluir a primeira análise, recebem 5 análises bónus cada.',
    action: 'Partilhar convite',
    href: '/member-referrals',
  };
}

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
  const timerRef = useRef(null);
  const isPremium = Boolean(user?.is_premium_active);

  useEffect(() => {
    if (!user) return undefined;
    let active = true;
    let eventToastShown = false;
    const seenEvents = readSeenEvents(user.id);
    const sessionToastKey = `engagement-toast-session-${user.id}`;

    const loadRealEvents = async () => {
      if (sessionStorage.getItem(sessionToastKey)) return;
      try {
        const { data } = await notificationAPI.getAll();
        if (!active) return;
        const items = data.results || [];
        const event = items.find((item) => (
          !item.read
          && EVENT_PREFIXES.some((prefix) => item.event_key?.startsWith(prefix))
          && !seenEvents.has(String(item.id))
        ));
        if (!event) return;

        seenEvents.add(String(event.id));
        localStorage.setItem(
          `engagement-toast-events-${user.id}`,
          JSON.stringify([...seenEvents].slice(-50)),
        );
        eventToastShown = true;
        sessionStorage.setItem(sessionToastKey, '1');
        setToast({
          icon: event.event_key.startsWith('affiliate_withdrawal_paid_') ? Wallet : Gift,
          title: event.title,
          body: event.body,
          action: 'Ver detalhes',
          href: event.url || '/member-referrals',
        });
      } catch (error) {
        console.error('Não foi possível verificar novidades da conta:', error);
      }
    };

    loadRealEvents();
    const intervalId = window.setInterval(loadRealEvents, 60000);

    if (!sessionStorage.getItem(sessionToastKey)) {
      timerRef.current = window.setTimeout(() => {
        if (!active || eventToastShown || sessionStorage.getItem(sessionToastKey)) return;
        const message = getDailyMessage(pathname, isPremium);
        if (message) {
          setToast(message);
          sessionStorage.setItem(sessionToastKey, '1');
        }
      }, 4500);
    }

    return () => {
      active = false;
      window.clearInterval(intervalId);
      window.clearTimeout(timerRef.current);
    };
  }, [isPremium, pathname, user]);

  if (!toast) return null;
  const Icon = toast.icon;

  return (
    <aside
      role="status"
      aria-live="polite"
      className="fixed bottom-20 left-4 right-4 z-[10000] ml-auto max-w-sm rounded-2xl border border-primary-200 bg-white p-4 text-gray-900 shadow-2xl dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100 sm:bottom-6"
    >
      <div className="flex items-start gap-3">
        <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-50 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300">
          <Icon className="h-5 w-5" />
        </span>
        <div className="min-w-0 flex-1">
          <p className="pr-5 text-sm font-bold">{toast.title}</p>
          <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">{toast.body}</p>
          <Link
            to={toast.href}
            onClick={() => setToast(null)}
            className="mt-3 inline-flex rounded-lg bg-primary-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-primary-700"
          >
            {toast.action}
          </Link>
        </div>
        <button
          type="button"
          onClick={() => setToast(null)}
          aria-label="Fechar aviso"
          className="absolute right-3 top-3 rounded-lg p-1 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </aside>
  );
}
