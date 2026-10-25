import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, CheckCheck, Clock3 } from 'lucide-react';
import { notificationAPI } from '../services/api';

function formatNotificationDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';

  return new Intl.DateTimeFormat('pt-PT', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

export default function NotificationBell() {
  const navigate = useNavigate();
  const containerRef = useRef(null);
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    const loadNotifications = async (showLoading = false) => {
      if (showLoading && active) setLoading(true);
      try {
        const { data } = await notificationAPI.getAll();
        if (active) {
          setNotifications(data.results || []);
          setUnreadCount(data.unread_count || 0);
          setError('');
        }
      } catch (requestError) {
        console.error('Não foi possível carregar as notificações:', requestError);
        if (active) setError('Não foi possível carregar as notificações.');
      } finally {
        if (showLoading && active) setLoading(false);
      }
    };

    loadNotifications();
    const intervalId = window.setInterval(() => loadNotifications(), 60000);
    const handleFocus = () => loadNotifications();
    window.addEventListener('focus', handleFocus);

    return () => {
      active = false;
      window.clearInterval(intervalId);
      window.removeEventListener('focus', handleFocus);
    };
  }, []);

  useEffect(() => {
    if (!open) return undefined;

    const handlePointerDown = (event) => {
      if (!containerRef.current?.contains(event.target)) setOpen(false);
    };
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') setOpen(false);
    };

    document.addEventListener('pointerdown', handlePointerDown);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('pointerdown', handlePointerDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [open]);

  const markAllRead = async () => {
    try {
      await notificationAPI.markAllRead();
      setNotifications((current) => current.map((item) => ({ ...item, read: true })));
      setUnreadCount(0);
      setError('');
    } catch (requestError) {
      console.error('Não foi possível marcar as notificações como lidas:', requestError);
      setError('Não foi possível atualizar as notificações. Tente novamente.');
    }
  };

  const openNotification = async (notification) => {
    if (!notification.read) {
      try {
        await notificationAPI.markRead(notification.id);
        setNotifications((current) => current.map((item) => (
          item.id === notification.id ? { ...item, read: true } : item
        )));
        setUnreadCount((count) => Math.max(0, count - 1));
      } catch (requestError) {
        console.error('Não foi possível marcar a notificação como lida:', requestError);
        setError('Não foi possível atualizar esta notificação.');
        return;
      }
    }

    setOpen(false);
    if (notification.url?.startsWith('/') && !notification.url.startsWith('//')) {
      navigate(notification.url);
    }
  };

  return (
    <div ref={containerRef} className="relative">
      <button
        type="button"
        onClick={() => {
          setOpen((current) => !current);
          if (!open) {
            setError('');
            setLoading(true);
            notificationAPI.getAll()
              .then(({ data }) => {
                setNotifications(data.results || []);
                setUnreadCount(data.unread_count || 0);
              })
              .catch((requestError) => {
                console.error('Não foi possível carregar as notificações:', requestError);
                setError('Não foi possível carregar as notificações.');
              })
              .finally(() => setLoading(false));
          }
        }}
        className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-white/30 bg-white/15 transition hover:bg-white/25 dark:border-gray-600/50 dark:bg-gray-700/50 dark:hover:bg-gray-600/50"
        aria-label={unreadCount ? `Notificações, ${unreadCount} por ler` : 'Notificações'}
        aria-expanded={open}
        aria-haspopup="dialog"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full border-2 border-primary-800 bg-rose-500 px-1 text-[10px] font-bold leading-none text-white dark:border-gray-900">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <section
          role="dialog"
          aria-label="Notificações"
          className="absolute right-0 top-12 z-50 w-[min(22rem,calc(100vw-2rem))] overflow-hidden rounded-2xl border border-gray-200 bg-white text-gray-900 shadow-2xl shadow-black/20 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-100"
        >
          <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3 dark:border-gray-800">
            <div>
              <h2 className="font-bold">Notificações</h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {unreadCount ? `${unreadCount} por ler` : 'Está tudo atualizado'}
              </p>
            </div>
            {unreadCount > 0 && (
              <button
                type="button"
                onClick={markAllRead}
                className="inline-flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs font-semibold text-primary-700 transition hover:bg-primary-50 dark:text-primary-300 dark:hover:bg-gray-800"
              >
                <CheckCheck className="h-4 w-4" />
                Marcar lidas
              </button>
            )}
          </div>

          {error && (
            <p role="alert" className="mx-3 mt-3 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700 dark:bg-rose-950/40 dark:text-rose-300">
              {error}
            </p>
          )}

          <div className="max-h-[min(60vh,26rem)] overflow-y-auto">
            {loading && notifications.length === 0 ? (
              <p className="px-4 py-8 text-center text-sm text-gray-500 dark:text-gray-400">A carregar...</p>
            ) : notifications.length === 0 ? (
              <div className="px-6 py-9 text-center">
                <span className="mx-auto flex h-11 w-11 items-center justify-center rounded-full bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400">
                  <Bell className="h-5 w-5" />
                </span>
                <p className="mt-3 text-sm font-semibold">Ainda não tem notificações</p>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  As novidades sobre as suas análises e partidas aparecerão aqui.
                </p>
                <button
                  type="button"
                  onClick={() => {
                    setOpen(false);
                    navigate('/profile?tab=notifications');
                  }}
                  className="mt-4 rounded-lg px-3 py-2 text-xs font-semibold text-primary-700 transition hover:bg-primary-50 dark:text-primary-300 dark:hover:bg-gray-800"
                >
                  Configurar notificações
                </button>
              </div>
            ) : (
              notifications.map((notification) => (
                <button
                  key={notification.id}
                  type="button"
                  onClick={() => openNotification(notification)}
                  className={`flex w-full gap-3 border-b border-gray-100 px-4 py-3 text-left transition last:border-b-0 hover:bg-gray-50 dark:border-gray-800 dark:hover:bg-gray-800/70 ${
                    notification.read ? '' : 'bg-primary-50/70 dark:bg-primary-950/20'
                  }`}
                >
                  <span className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${
                    notification.read ? 'bg-gray-300 dark:bg-gray-600' : 'bg-primary-500'
                  }`} aria-hidden="true" />
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-semibold">{notification.title}</span>
                    <span className="mt-0.5 block text-xs leading-5 text-gray-600 dark:text-gray-300">
                      {notification.body}
                    </span>
                    <span className="mt-2 flex items-center gap-1 text-[11px] text-gray-500 dark:text-gray-400">
                      <Clock3 className="h-3 w-3" />
                      {formatNotificationDate(notification.created_at)}
                    </span>
                  </span>
                </button>
              ))
            )}
          </div>
        </section>
      )}
    </div>
  );
}
