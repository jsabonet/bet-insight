const CACHE_NAME = 'placarcerto-cache-v3';
const APP_SHELL = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/favicon.svg',
  '/offline.html'
];

// Mensagem para forçar ativação imediata
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('install', (event) => {
  console.log('🔧 SW v3 instalando...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('✅ SW v3 ativando...');
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('🗑️ Deletando cache antigo:', key);
            return caches.delete(key);
          }
        })
      )
    )
  );
  self.clients.claim();
});

// IMPORTANTE: NÃO INTERCEPTAR CHAMADAS DE API
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // NÃO interceptar API calls - deixar ir direto para o backend
  if (url.pathname.startsWith('/api/') || event.request.url.includes('/api/')) {
    console.log('🌐 Ignorando API call:', url.pathname);
    return; // Não chama event.respondWith() - deixa o fetch acontecer normalmente
  }

  // Static assets and pages
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return (
        cached ||
        fetch(event.request).then((response) => {
          const clone = response.clone();
          // Only cache GET successful responses
          if (event.request.method === 'GET' && response.status === 200) {
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        }).catch(() => {
          // Serve offline fallback for navigations
          if (event.request.mode === 'navigate') {
            return caches.match('/offline.html');
          }
        })
      );
    })
  );
});
