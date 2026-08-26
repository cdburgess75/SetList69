const CACHE = 'setlist69-v2026.08.26.005';
const PRECACHE = [
  './',
  './index.html',
  './setlist69.html',
  './manifest.json',
  './fonts/fraunces-latin.woff2',
  './fonts/hanken-grotesk-latin.woff2',
  './fonts/jetbrains-mono-latin.woff2',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png',
  './icons/apple-touch-icon.png',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      // cache:'reload' is LOAD-BEARING — never remove it. GitHub Pages serves with
      // max-age=600, and a plain addAll() reads the browser's HTTP cache, so a new worker
      // can precache a STALE copy of the app under the new version's name. The page and
      // worker versions then never match and the update banner loops forever (the loop
      // fixed in v2026.08.14.001). 'reload' forces every precache fetch to the network.
      .then(c => c.addAll(PRECACHE.map(u => new Request(u, { cache: 'reload' }))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// Lets the page ask which version just took over, so the update banner can name it.
self.addEventListener('message', e => {
  if (e.data === 'GET_VERSION' && e.source) {
    e.source.postMessage({ type: 'VERSION', version: CACHE.replace('setlist69-', '') });
  }
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith((async () => {
    // ignoreSearch so e.g. ./setlist69.html?x still matches the cached shell
    const cached = await caches.match(e.request, { ignoreSearch: true });
    if (cached) return cached;
    try {
      return await fetch(e.request);
    } catch (err) {
      // offline cache-miss: for a navigation, fall back to the app shell instead of the
      // browser's network-error page; otherwise surface the failure.
      if (e.request.mode === 'navigate') {
        const shell = await caches.match('./setlist69.html');
        if (shell) return shell;
      }
      throw err;
    }
  })());
});
