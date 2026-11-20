const CACHE_NAME = "boite-blanche-v1";
const PRECACHE_URLS = [
  "./",
  "./index.html",
  "./mindmap_clean_final.html",
  "./chapitre1/chapitre1.html",
  "./chapitre1/chapitre1-1.html",
  "./chapitre2/chapitre2.html",
  "./chapitre3/chapitre3.html",
  "./chapitre4/chapitre4.html",
  "./feux_tricolores/indexFeux.html",
  "./feux_tricolores/description.html",
  "./css/style.css",
  "./feux_tricolores/network.js",
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
  "./chapitre2/img/sigmoide.png",
  "./chapitre2/img/softmax.png",
  "./chapitre2/img/tablette200x400.png",
  "./chapitre2/img/tanh.png",
  "./chapitre3/img/descenteDeGradient.png",
  "./chapitre3/img/recoFaces.png",
  "./chapitre3/img/reseauA12Et3sorties.png",
  "./chapitre3/img/tangente1.png",
  "./chapitre4/img/chat.png",
  "./img/rab/ImageCouches.png",
  "./img/rab/apprentissage.png",
  "./manifest.webmanifest",
  "./icons/icon.svg"
];

self.addEventListener("install", (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    await cache.addAll(PRECACHE_URLS);

    // Best-effort cache of the only third-party runtime dependency.
    // The offline shell remains installable if the CDN is unavailable.
    try {
      const chartUrl = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js";
      const response = await fetch(chartUrl, { mode: "cors" });
      if (response.ok && response.type !== "opaque") {
        await cache.put(chartUrl, response);
      }
    } catch {
      // The traffic-light visualisation may need one online visit to warm this cache.
    }

    await self.skipWaiting();
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((key) => key.startsWith("boite-blanche-") && key !== CACHE_NAME)
      .map((key) => caches.delete(key)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  event.respondWith((async () => {
    const cached = await caches.match(event.request);
    if (cached) return cached;

    try {
      return await fetch(event.request);
    } catch {
      if (event.request.mode === "navigate") {
        return (await caches.match("./index.html")) || Response.error();
      }
      return Response.error();
    }
  })());
});
