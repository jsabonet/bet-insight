const CACHE_NAME = 'placarcerto-cache-v5';

// Mensagem para forçar ativação imediata
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('install', (event) => {
  console.log('🔧 SW v5 instalando...');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('✅ SW v5 ativando...');
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys
          .filter((key) => key.startsWith('placarcerto-cache-') && key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('push', (event) => {
  let payload = {};
  try {
    payload = event.data ? event.data.json() : {};
  } catch {
    payload = { body: event.data?.text() || '' };
  }

  event.waitUntil(self.registration.showNotification(payload.title || 'PlacarCerto', {
    body: payload.body || 'Há uma atualização disponível.',
    icon: payload.icon || 'https://placarcerto.digital/favicon.svg',
    badge: payload.badge || 'https://placarcerto.digital/favicon.svg',
    tag: payload.tag || 'placarcerto-update',
    data: { url: payload.url || '/' },
  }));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const target = new URL(event.notification.data?.url || '/', self.location.origin);
  if (target.origin !== self.location.origin) return;

  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    for (const client of windows) {
      if (client.url.startsWith(self.location.origin)) {
        await client.navigate(target.href);
        return client.focus();
      }
    }
    return self.clients.openWindow(target.href);
  })());
});

// IMPORTANTE: NÃO INTERCEPTAR CHAMADAS DE API
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  if (
    event.request.method !== 'GET'
    || url.origin !== self.location.origin
    || url.pathname.startsWith('/api/')
    || event.request.mode !== 'navigate'
  ) {
    return;
  }

  event.respondWith(
    fetch(event.request).catch(() => new Response(
      '<!doctype html><html lang="pt"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sem ligação</title><body><h1>Sem ligação à internet</h1><p>Verifique a sua ligação e tente novamente.</p></body></html>',
      { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
    ))
  );
});
