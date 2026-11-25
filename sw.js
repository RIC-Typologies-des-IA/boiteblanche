// The build replaces this token with the published commit/build identifier.
const CACHE_NAME = "boite-blanche-__BUILD_ID__";
const PRECACHE_URLS = [
  "./",
  "./index.html",
  "./chapitre1/chapitre1.html",
  "./chapitre1/chapitre1-1.html",
  "./chapitre2/chapitre2.html",
  "./chapitre3/chapitre3.html",
  "./chapitre4/chapitre4.html",
  "./feux_tricolores/indexFeux.html",
  "./feux_tricolores/description.html",
  "./css/style.css",
  "./feux_tricolores/network.js",
  "./vendor/chart.js/chart.umd.min.js",
  "./vendor/chart.js/LICENSE.md",
  "./chapitre1/img/000.png",
  "./chapitre1/img/001.png",
  "./chapitre1/img/010.png",
  "./chapitre1/img/100.png",
  "./chapitre1/img/NeuronesUneCoucheVertical.png",
  "./chapitre1/img/neuroneBio.png",
  "./chapitre1/img/perceptronUnique.png",
  "./chapitre1/img/troisDroites.png",
  "./chapitre1/img/uneDroite.png",
  "./chapitre1/img/uneDroite_H.png",
  "./chapitre2/img/ReLU.png",
  "./chapitre2/img/cercleA12droites.png",
  "./chapitre2/img/derivable.png",
  "./chapitre2/img/derivable_4.png",
  "./chapitre2/img/relief01.png",
  "./chapitre2/img/reseauA12.png",
  "./chapitre2/img/reseauA12Et3sorties.png",
  "./chapitre2/img/sigmoid.png",
  "./chapitre2/img/softmax.png",
  "./chapitre2/img/tablette200x400.png",
  "./chapitre2/img/tanh.png",
  "./chapitre3/img/descenteDeGradient.png",
  "./chapitre3/img/recoFaces.png",
  "./chapitre3/img/reseauA12Et3sorties.png",
  "./chapitre3/img/tangente1.png",
  "./chapitre4/img/chat.png",
  "./manifest.webmanifest",
  "./icons/icon.svg"
];

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);

    // Fetch the published files rather than reusing a potentially stale HTTP cache.
    await Promise.all(PRECACHE_URLS.map(async (url) => {
      const request = new Request(new URL(url, self.registration.scope), {
        cache: "reload"
      });
      const response = await fetch(request);
      if (!response.ok) {
        throw new Error(`Unable to precache ${url}: HTTP ${response.status}`);
      }
      await cache.put(request, response);
    }));

    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys
      .filter((key) => key.startsWith("boite-blanche-") && key !== CACHE_NAME)
      .map((key) => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  // HTML must be fresh whenever the device is online, while retaining an
  // offline fallback to the last successfully cached page.
  if (event.request.mode === "navigate") {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE_NAME);
      try {
        const response = await fetch(event.request);
        if (response.ok) {
          await cache.put(event.request, response.clone());
        }
        return response;
      } catch {
        return (await cache.match(event.request))
          || (await cache.match(new URL("./index.html", self.registration.scope)))
          || Response.error();
      }
    })());
    return;
  }

  // Static resources remain cache-first for reliable offline operation.
  event.respondWith((async () => {
    const cached = await caches.match(event.request);
    if (cached) return cached;

    try {
      return await fetch(event.request);
    } catch {
      return Response.error();
    }
  })());
});
