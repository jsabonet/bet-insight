import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BellRing, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { pushAPI } from '../services/api';
import { createPushSubscription } from '../utils/pushNotifications';

const SNOOZE_DURATION = 7 * 24 * 60 * 60 * 1000;

function getUnsupportedMessage() {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  const isInstalled = window.matchMedia('(display-mode: standalone)').matches
    || window.navigator.standalone === true;

  if (isIOS && !isInstalled) {
    return 'No iPhone ou iPad, adicione primeiro o PlacarCerto ao ecrã principal e abra a app instalada. As notificações Web Push requerem iOS/iPadOS 16.4 ou posterior.';
  }

  return 'Este navegador ou endereço não permite notificações push. Tente abrir o PlacarCerto num navegador compatível e através de uma ligação HTTPS.';
}

export default function PushNotificationPrompt() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [visible, setVisible] = useState(false);
  const [publicKey, setPublicKey] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const dismiss = useCallback(() => {
    if (user?.id) {
      localStorage.setItem(
        `push_prompt_dismissed_until_${user.id}`,
        String(Date.now() + SNOOZE_DURATION),
      );
    }
    setVisible(false);
  }, [user?.id]);

  useEffect(() => {
    if (!user?.id) return undefined;

    const snoozeKey = `push_prompt_dismissed_until_${user.id}`;
    const dismissedUntil = Number(localStorage.getItem(snoozeKey) || 0);
    if (dismissedUntil > Date.now()) return undefined;

    let cancelled = false;
    const timer = window.setTimeout(() => {
      pushAPI.getStatus()
        .then(async ({ data }) => {
          if (cancelled || !data.available || !data.public_key) return;

          setPublicKey(data.public_key);
          let deviceSubscribed = false;
          const browserSupportsPush = window.isSecureContext
            && 'serviceWorker' in navigator
            && 'PushManager' in window
            && 'Notification' in window;

          if (browserSupportsPush) {
            try {
              const registration = await navigator.serviceWorker.ready;
              deviceSubscribed = Boolean(await registration.pushManager.getSubscription());
            } catch (subscriptionError) {
              console.error('Não foi possível verificar a inscrição push deste dispositivo:', subscriptionError);
            }
          }

          if (!cancelled && (!data.push_enabled || !deviceSubscribed)) {
            setVisible(true);
          }
        })
        .catch((requestError) => {
          console.error('Não foi possível verificar o estado das notificações push:', requestError);
        });
    }, 2500);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [user?.id]);

  useEffect(() => {
    if (!visible) return undefined;

    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && !loading) dismiss();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [visible, loading, dismiss]);

  const activateNotifications = async () => {
    setError('');
    if (
      !window.isSecureContext
      || !('serviceWorker' in navigator)
      || !('PushManager' in window)
      || !('Notification' in window)
    ) {
      setError(getUnsupportedMessage());
      return;
    }

    setLoading(true);
    try {
      if (!publicKey) {
        setError('As notificações push não estão configuradas no servidor neste momento.');
        return;
      }
      await createPushSubscription(publicKey);
      await pushAPI.updatePreferences({ push_enabled: true });
      setVisible(false);
    } catch (activationError) {
      setError(
        activationError.response?.data?.error
          || activationError.message
          || 'Não foi possível ativar as notificações. Verifique as permissões do navegador e tente novamente.',
      );
    } finally {
      setLoading(false);
    }
  };

  if (!visible) return null;

  const browserSupportsPush = window.isSecureContext
    && 'serviceWorker' in navigator
    && 'PushManager' in window
    && 'Notification' in window;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-end justify-center bg-black/60 p-4 backdrop-blur-sm sm:items-center"
      onClick={(event) => {
        if (event.target === event.currentTarget && !loading) dismiss();
      }}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="push-prompt-title"
        className="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-2xl dark:border-gray-700 dark:bg-gray-800"
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary-100 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300">
            <BellRing className="h-6 w-6" />
          </div>
          <button
            type="button"
            onClick={dismiss}
            disabled={loading}
            aria-label="Fechar lembrete"
            className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 disabled:opacity-50 dark:hover:bg-gray-700"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <h2 id="push-prompt-title" className="mt-4 text-xl font-bold text-gray-900 dark:text-white">
          Não perca as suas análises
        </h2>
        <p className="mt-2 text-sm leading-6 text-gray-600 dark:text-gray-300">
          Ative as notificações para saber quando uma análise estiver pronta e receber lembretes das partidas que acompanha.
        </p>

        {!browserSupportsPush && (
          <p className="mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950/40 dark:text-amber-200">
            {getUnsupportedMessage()}
          </p>
        )}
        {error && (
          <p role="alert" className="mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-900 dark:bg-amber-950/40 dark:text-amber-200">
            {error}
          </p>
        )}

        <div className="mt-6 flex flex-col gap-3">
          {browserSupportsPush ? (
            <button
              type="button"
              onClick={activateNotifications}
              disabled={loading}
              className="inline-flex min-h-11 items-center justify-center rounded-xl bg-primary-600 px-4 py-3 font-semibold text-white transition hover:bg-primary-700 disabled:cursor-wait disabled:opacity-60"
            >
              {loading ? 'A ativar...' : 'Ativar notificações'}
            </button>
          ) : (
            <button
              type="button"
              onClick={() => {
                dismiss();
                navigate('/profile?tab=notifications');
              }}
              className="inline-flex min-h-11 items-center justify-center rounded-xl border border-gray-300 px-4 py-3 font-semibold text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
            >
              Ver instruções
            </button>
          )}
          <button
            type="button"
            onClick={dismiss}
            disabled={loading}
            className="min-h-10 text-sm font-medium text-gray-500 hover:text-gray-700 disabled:opacity-50 dark:text-gray-400 dark:hover:text-gray-200"
          >
            Agora não
          </button>
        </div>
      </section>
    </div>
  );
}
