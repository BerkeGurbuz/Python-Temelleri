/* Serdivan 3D İşletme Haritası
 * Harita: MapLibre GL JS + OpenFreeMap karoları · Veri: OpenStreetMap (data/isletmeler.geojson)
 */
(() => {
  'use strict';

  // ---------------------------------------------------------------- Ayarlar
  const BASLANGIC = { center: [30.3608, 40.7668], zoom: 14.6, pitch: 62, bearing: -18 };
  const STILLER = {
    acik: 'https://tiles.openfreemap.org/styles/liberty',
    koyu: 'https://tiles.openfreemap.org/styles/dark',
  };
  const ARAZI_KARO = 'https://elevation-tiles-prod.s3.amazonaws.com/terrarium/{z}/{x}/{y}.png';
  const LISTE_ADIM = 150;

  const KATEGORILER = {
    'yeme-icme': { ad: 'Yeme & İçme', renk: '#e8590c', simge: '🍽️' },
    'market-gida': { ad: 'Market & Gıda', renk: '#2f9e44', simge: '🛒' },
    alisveris: { ad: 'Alışveriş', renk: '#ae3ec9', simge: '🛍️' },
    saglik: { ad: 'Sağlık', renk: '#e03131', simge: '⚕️' },
    finans: { ad: 'Banka & ATM', renk: '#1971c2', simge: '🏦' },
    egitim: { ad: 'Eğitim', renk: '#f08c00', simge: '🎓' },
    konaklama: { ad: 'Konaklama', renk: '#6741d9', simge: '🛏️' },
    arac: { ad: 'Araç & Akaryakıt', renk: '#495057', simge: '⛽' },
    guzellik: { ad: 'Güzellik & Bakım', renk: '#d6336c', simge: '💇' },
    hizmet: { ad: 'Hizmet & Ofis', renk: '#0c8599', simge: '💼' },
    'spor-eglence': { ad: 'Spor & Eğlence', renk: '#5c940d', simge: '🎯' },
    kamu: { ad: 'Kamu Kurumları', renk: '#846358', simge: '🏛️' },
    diger: { ad: 'Diğer', renk: '#64748b', simge: '📍' },
  };
  const katBilgi = (k) => KATEGORILER[k] || KATEGORILER.diger;
  const SAGLAYICI = { meta: 'Meta', Microsoft: 'Microsoft', Foursquare: 'Foursquare', AllThePlaces: 'All The Places' };

  const $ = (s) => document.querySelector(s);
  const el = {
    panel: $('#panel'),
    ozet: $('#ozet'),
    arama: $('#arama'),
    kategoriler: $('#kategoriler'),
    sonuc: $('#sonuc-sayisi'),
    sadeceGorunen: $('#sadece-gorunen'),
    liste: $('#liste'),
    listeGorunumu: $('#liste-gorunumu'),
    detay: $('#detay'),
    veriTarihi: $('#veri-tarihi'),
    bildirim: $('#bildirim'),
    btnEv: $('#btn-ev'),
    btn3d: $('#btn-3d'),
    btnDon: $('#btn-don'),
    btnArazi: $('#btn-arazi'),
    btnTema: $('#btn-tema'),
  };

  const sakla = {
    oku(anahtar) {
      try { return localStorage.getItem(anahtar); } catch { return null; }
    },
    yaz(anahtar, deger) {
      try { localStorage.setItem(anahtar, deger); } catch { /* özel pencere vb. */ }
    },
  };

  const durum = {
    tum: [], // tüm işletmeler (GeoJSON Feature)
    kimlik: new Map(), // id -> Feature
    suzulmus: [],
    aktifKat: new Set(Object.keys(KATEGORILER)),
    arama: '',
    sadeceGorunen: false,
    listeSinir: LISTE_ADIM,
    secili: null,
    sinir: null,
    tema: sakla.oku('serdivan-tema') === 'koyu' ? 'koyu' : 'acik',
    arazi: sakla.oku('serdivan-arazi') === 'acik', // arazi ağır bir katman: isteyen açar
    donuyor: false,
  };

  // ---------------------------------------------------------------- Yardımcılar
  const kacis = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));

  const sade = (s) => String(s ?? '')
    .toLocaleLowerCase('tr')
    .replace(/[çğıöşüâîû]/g, (c) => ({ ç: 'c', ğ: 'g', ı: 'i', ö: 'o', ş: 's', ü: 'u', â: 'a', î: 'i', û: 'u' }[c]));

  const guvenliUrl = (u) => (/^https?:\/\//i.test(u || '') ? u : null);

  function mesafe(a, b) {
    const R = 6371000;
    const r = Math.PI / 180;
    const dLat = (b[1] - a[1]) * r;
    const dLng = (b[0] - a[0]) * r;
    const h = Math.sin(dLat / 2) ** 2 + Math.cos(a[1] * r) * Math.cos(b[1] * r) * Math.sin(dLng / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(h));
  }

  const mesafeYazi = (m) => (m < 950 ? `${Math.round(m / 10) * 10} m` : `${(m / 1000).toFixed(1)} km`);

  // İşletmeyi temsil eden 3B sütunun tabanı (metre cinsinden altıgen)
  function altigen([lng, lat], yaricap) {
    const dLat = yaricap / 111320;
    const dLng = yaricap / (111320 * Math.cos((lat * Math.PI) / 180));
    const halka = [];
    for (let i = 0; i <= 6; i += 1) {
      const a = (Math.PI / 3) * i;
      halka.push([lng + dLng * Math.cos(a), lat + dLat * Math.sin(a)]);
    }
    return [halka];
  }

  const GUNLER = { Mo: 'Pzt', Tu: 'Sal', We: 'Çar', Th: 'Per', Fr: 'Cum', Sa: 'Cmt', Su: 'Paz', PH: 'Resmî tatil' };
  function saatYazi(s) {
    if (!s) return '';
    if (s.trim() === '24/7') return '7/24 açık';
    return s
      .split(';')
      .map((p) => p.trim().replace(/\b(Mo|Tu|We|Th|Fr|Sa|Su|PH)\b/g, (g) => GUNLER[g]).replace(/\boff\b/g, 'kapalı'))
      .filter(Boolean)
      .join('\n');
  }

  let bildirimZaman;
  function bildir(mesaj, kalici = false) {
    el.bildirim.textContent = mesaj;
    el.bildirim.hidden = false;
    clearTimeout(bildirimZaman);
    if (!kalici) bildirimZaman = setTimeout(() => { el.bildirim.hidden = true; }, 3200);
  }

  const mobil = () => window.matchMedia('(max-width: 760px)').matches;

  // ---------------------------------------------------------------- Harita
  document.documentElement.dataset.tema = durum.tema;
  // Bağlantıda harita konumu yoksa (yalnızca #isletme=...), açılışta seçili işletmeye uçulur.
  const baglantidaKonumVar = /(?:^#|&)harita=/.test(location.hash);

  let harita;
  try {
    harita = new maplibregl.Map({
      container: 'harita',
      style: STILLER[durum.tema],
      ...BASLANGIC,
      minZoom: 9.5,
      maxPitch: 78,
      hash: 'harita',
      maxBounds: [[29.75, 40.4], [30.95, 41.15]],
      attributionControl: false,
    });
  } catch (hata) {
    console.error(hata);
    bildir('Harita başlatılamadı: tarayıcınız WebGL desteklemiyor olabilir.', true);
    return;
  }

  harita.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');
  harita.addControl(new maplibregl.GeolocateControl({
    positionOptions: { enableHighAccuracy: true },
    trackUserLocation: true,
  }), 'top-right');
  harita.addControl(new maplibregl.FullscreenControl(), 'top-right');
  harita.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-right');
  harita.addControl(new maplibregl.AttributionControl({
    compact: true,
    customAttribution: 'Arazi: <a href="https://registry.opendata.aws/terrain-tiles/" target="_blank" rel="noopener">Mapzen / AWS</a>',
  }), 'bottom-right');

  function dolgulamaAyarla() {
    if (mobil()) {
      const y = el.panel.classList.contains('kucuk') ? 132 : Math.round(window.innerHeight * 0.46);
      harita.setPadding({ top: 50, bottom: y, left: 0, right: 0 });
    } else {
      harita.setPadding({ top: 0, bottom: 0, left: el.panel.offsetWidth + 12, right: 0 });
    }
  }
  dolgulamaAyarla();
  window.addEventListener('resize', dolgulamaAyarla);

  const isaretEl = document.createElement('div');
  isaretEl.className = 'isaret';
  const isaret = new maplibregl.Marker({ element: isaretEl });
  const ipucu = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 14, className: 'ipucu' });

  const bosKoleksiyon = () => ({ type: 'FeatureCollection', features: [] });

  function noktaVerisi() {
    return { type: 'FeatureCollection', features: durum.suzulmus };
  }

  function sutunVerisi() {
    return {
      type: 'FeatureCollection',
      features: durum.suzulmus.map((f) => ({
        type: 'Feature',
        properties: { id: f.properties.id, renk: f.properties.renk },
        geometry: { type: 'Polygon', coordinates: altigen(f.geometry.coordinates, 4.2) },
      })),
    };
  }

  function seciliVerisi() {
    const f = durum.secili;
    if (!f) return bosKoleksiyon();
    return {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature',
        properties: { renk: f.properties.renk },
        geometry: { type: 'Polygon', coordinates: altigen(f.geometry.coordinates, 6.5) },
      }],
    };
  }

  function maskeVerisi() {
    if (!durum.sinir) return bosKoleksiyon();
    const g = durum.sinir.geometry;
    const cokgenler = g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
    const dunya = [[20, 30], [45, 30], [45, 48], [20, 48], [20, 30]];
    return {
      type: 'FeatureCollection',
      features: [{
        type: 'Feature',
        properties: {},
        geometry: { type: 'Polygon', coordinates: [dunya, ...cokgenler.map((c) => c[0])] },
      }],
    };
  }

  function haritaVerisiniGuncelle() {
    harita.getSource('isletmeler')?.setData(noktaVerisi());
    harita.getSource('sutunlar')?.setData(sutunVerisi());
  }

  // Taban stil her (yeniden) yüklendiğinde kendi katmanlarımızı kurar.
  function katmanlariKur() {
    const stil = harita.getStyle();
    const koyu = durum.tema === 'koyu';
    const vektor = Object.keys(stil.sources).find((k) => stil.sources[k].type === 'vector');

    // Taban haritanın kendi POI simgelerini gizle: işletmeleri biz çiziyoruz.
    for (const k of stil.layers) {
      if (k['source-layer'] === 'poi') harita.setLayoutProperty(k.id, 'visibility', 'none');
    }
    if (harita.getLayer('building-3d')) harita.removeLayer('building-3d');
    const ilkEtiket = stil.layers.find((k) => k.type === 'symbol' && k.id !== 'building-3d')?.id;

    harita.setSky(koyu
      ? { 'sky-color': '#0b1026', 'horizon-color': '#1e293b', 'fog-color': '#0f172a', 'sky-horizon-blend': 0.6, 'horizon-fog-blend': 0.7, 'fog-ground-blend': 0.2 }
      : { 'sky-color': '#7ab8f5', 'horizon-color': '#e6f1fb', 'fog-color': '#f4f7fa', 'sky-horizon-blend': 0.6, 'horizon-fog-blend': 0.7, 'fog-ground-blend': 0.2 });

    // Arazi (yükselti) ve gölgelendirme
    const dem = { type: 'raster-dem', tiles: [ARAZI_KARO], encoding: 'terrarium', tileSize: 256, maxzoom: 13 };
    harita.addSource('arazi', dem);
    harita.addSource('arazi-golge', dem);
    harita.addLayer({
      id: 'arazi-golge',
      type: 'hillshade',
      source: 'arazi-golge',
      paint: {
        'hillshade-exaggeration': koyu ? 0.35 : 0.22,
        'hillshade-shadow-color': koyu ? '#000000' : '#5a6b7a',
        'hillshade-highlight-color': koyu ? '#334155' : '#ffffff',
      },
    }, ilkEtiket);
    harita.setTerrain(durum.arazi ? { source: 'arazi', exaggeration: 1.25 } : null);

    // İlçe dışını hafifçe karart, sınırı çiz
    harita.addSource('maske', { type: 'geojson', data: maskeVerisi() });
    harita.addSource('sinir', { type: 'geojson', data: durum.sinir || bosKoleksiyon() });
    harita.addLayer({
      id: 'maske',
      type: 'fill',
      source: 'maske',
      paint: { 'fill-color': koyu ? '#020617' : '#334155', 'fill-opacity': koyu ? 0.5 : 0.2 },
    }, ilkEtiket);
    harita.addLayer({
      id: 'sinir-cizgi',
      type: 'line',
      source: 'sinir',
      paint: {
        'line-color': koyu ? '#2dd4bf' : '#0f766e',
        'line-width': ['interpolate', ['linear'], ['zoom'], 10, 1.5, 15, 3],
        'line-dasharray': [3, 2],
        'line-opacity': 0.9,
      },
    }, ilkEtiket);

    // 3B binalar
    if (vektor) {
      harita.addLayer({
        id: 'binalar-3b',
        type: 'fill-extrusion',
        source: vektor,
        'source-layer': 'building',
        minzoom: 13,
        filter: ['!=', ['get', 'hide_3d'], true],
        paint: {
          'fill-extrusion-color': ['interpolate', ['linear'], ['coalesce', ['get', 'render_height'], 5],
            0, koyu ? '#273449' : '#e9e4dc',
            20, koyu ? '#334766' : '#d9d2c7',
            60, koyu ? '#4a6591' : '#c2bfc4'],
          'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 13, 0, 14.5, ['coalesce', ['get', 'render_height'], 5]],
          'fill-extrusion-base': ['interpolate', ['linear'], ['zoom'], 13, 0, 14.5, ['coalesce', ['get', 'render_min_height'], 0]],
          'fill-extrusion-opacity': koyu ? 0.85 : 0.9,
        },
      }, ilkEtiket);
    }

    // İşletmeler
    harita.addSource('isletmeler', { type: 'geojson', data: noktaVerisi() });
    harita.addSource('sutunlar', { type: 'geojson', data: sutunVerisi() });
    harita.addSource('secili', { type: 'geojson', data: seciliVerisi() });

    harita.addLayer({
      id: 'isletme-sutun',
      type: 'fill-extrusion',
      source: 'sutunlar',
      minzoom: 14,
      paint: {
        'fill-extrusion-color': ['get', 'renk'],
        'fill-extrusion-height': ['interpolate', ['linear'], ['zoom'], 14, 0, 15.5, 26],
        'fill-extrusion-opacity': 0.88,
      },
    });
    harita.addLayer({
      id: 'secili-sutun',
      type: 'fill-extrusion',
      source: 'secili',
      paint: {
        'fill-extrusion-color': ['get', 'renk'],
        'fill-extrusion-height': 64,
        'fill-extrusion-opacity': 0.95,
      },
    });
    harita.addLayer({
      id: 'isletme-nokta',
      type: 'circle',
      source: 'isletmeler',
      paint: {
        'circle-color': ['get', 'renk'],
        'circle-radius': ['interpolate', ['linear'], ['zoom'], 10, 1.4, 13, 2.4, 15, 3.8, 17, 6, 19, 9],
        'circle-stroke-color': koyu ? '#0b1220' : '#ffffff',
        'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 11, 0, 14, 1.2, 18, 2],
        'circle-opacity': 0.95,
      },
    });
    harita.addLayer({
      id: 'isletme-etiket',
      type: 'symbol',
      source: 'isletmeler',
      minzoom: 15.3,
      filter: ['!', ['get', 'adsiz']],
      layout: {
        'text-field': ['get', 'ad'],
        'text-font': ['Noto Sans Bold'],
        'text-size': ['interpolate', ['linear'], ['zoom'], 15, 10.5, 18, 13],
        'text-anchor': 'top',
        'text-offset': [0, 0.7],
        'text-max-width': 9,
        'text-padding': 4,
      },
      paint: {
        'text-color': koyu ? '#f1f5f9' : '#1e293b',
        'text-halo-color': koyu ? 'rgba(2, 6, 23, 0.9)' : 'rgba(255, 255, 255, 0.95)',
        'text-halo-width': 1.4,
      },
    });
  }

  harita.on('style.load', katmanlariKur);

  // Fare / dokunma etkileşimi
  const TIKLANIR = ['isletme-nokta', 'isletme-sutun'];
  let ipucuId = null;

  harita.on('mousemove', (e) => {
    if (!harita.getLayer('isletme-nokta')) return;
    const bulunan = harita.queryRenderedFeatures(e.point, { layers: TIKLANIR })[0];
    const f = bulunan && durum.kimlik.get(bulunan.properties.id);
    harita.getCanvas().style.cursor = f ? 'pointer' : '';
    if (!f) {
      ipucuId = null;
      ipucu.remove();
      return;
    }
    if (ipucuId !== f.properties.id) {
      ipucuId = f.properties.id;
      ipucu.setHTML(`${kacis(f.properties.ad)}<small>${kacis(f.properties.tur)}</small>`);
    }
    ipucu.setLngLat(f.geometry.coordinates).addTo(harita);
  });
  harita.on('mouseout', () => { ipucuId = null; ipucu.remove(); });

  harita.on('click', (e) => {
    if (!harita.getLayer('isletme-nokta')) return;
    const kutu = [[e.point.x - 6, e.point.y - 6], [e.point.x + 6, e.point.y + 6]];
    const bulunan = harita.queryRenderedFeatures(kutu, { layers: TIKLANIR });
    if (!bulunan.length) return;
    // Kutunun içindekilerden tıklanan noktaya en yakın olanı seç
    let enIyi = null;
    let enIyiUzaklik = Infinity;
    for (const b of bulunan) {
      const f = durum.kimlik.get(b.properties.id);
      if (!f) continue;
      const p = harita.project(f.geometry.coordinates);
      const u = b.layer.id === 'isletme-sutun' ? 0 : Math.hypot(p.x - e.point.x, p.y - e.point.y);
      if (u < enIyiUzaklik) { enIyi = f; enIyiUzaklik = u; }
    }
    if (enIyi) sec(enIyi.properties.id);
  });

  harita.on('moveend', () => {
    if (durum.sadeceGorunen) suz();
  });

  // ---------------------------------------------------------------- Süzme + liste
  function eslesenler({ kategoriHaric = false } = {}) {
    const q = sade(durum.arama.trim());
    const sinirlar = durum.sadeceGorunen ? harita.getBounds() : null;
    return durum.tum.filter((f) => {
      const p = f.properties;
      if (!kategoriHaric && !durum.aktifKat.has(p.kat)) return false;
      if (q && !p._ara.includes(q)) return false;
      if (sinirlar && !sinirlar.contains(f.geometry.coordinates)) return false;
      return true;
    });
  }

  function suz() {
    durum.suzulmus = eslesenler();
    durum.listeSinir = LISTE_ADIM;
    haritaVerisiniGuncelle();
    kategorileriCiz();
    listeyiCiz();
  }

  function kategorileriCiz() {
    const sayim = {};
    for (const f of eslesenler({ kategoriHaric: true })) sayim[f.properties.kat] = (sayim[f.properties.kat] || 0) + 1;
    const hepsi = durum.aktifKat.size === Object.keys(KATEGORILER).length;
    const toplam = Object.values(sayim).reduce((a, b) => a + b, 0);
    let html = `<button type="button" class="cip" data-kat="*" aria-pressed="${hepsi}">Tümü <b>${toplam}</b></button>`;
    for (const [k, b] of Object.entries(KATEGORILER)) {
      const basili = !hepsi && durum.aktifKat.has(k);
      html += `<button type="button" class="cip" data-kat="${k}" aria-pressed="${hepsi ? 'mixed' : basili}" style="--renk:${b.renk}"><i></i>${kacis(b.ad)} <b>${sayim[k] || 0}</b></button>`;
    }
    el.kategoriler.innerHTML = html;
  }

  el.kategoriler.addEventListener('click', (e) => {
    const cip = e.target.closest('.cip');
    if (!cip) return;
    const k = cip.dataset.kat;
    const tumu = Object.keys(KATEGORILER);
    if (k === '*') {
      durum.aktifKat = new Set(tumu);
    } else if (durum.aktifKat.size === tumu.length) {
      durum.aktifKat = new Set([k]);
    } else {
      if (durum.aktifKat.has(k)) durum.aktifKat.delete(k);
      else durum.aktifKat.add(k);
      if (durum.aktifKat.size === 0) durum.aktifKat = new Set(tumu);
    }
    suz();
  });

  function ogeHtml(f, ek = '') {
    const p = f.properties;
    const b = katBilgi(p.kat);
    const alt = [p.tur, ek || p.adres].filter(Boolean).join(' · ');
    return `<li><button type="button" class="oge" data-id="${kacis(p.id)}" style="--renk:${b.renk}">
      <span class="rozet" aria-hidden="true">${b.simge}</span>
      <span><strong>${kacis(p.ad)}</strong><small>${kacis(alt)}</small></span>
    </button></li>`;
  }

  function listeyiCiz() {
    const n = durum.suzulmus.length;
    el.sonuc.textContent = `${n.toLocaleString('tr')} işletme`;
    if (!n) {
      el.liste.innerHTML = '<li class="bos">Bu ölçütlere uyan işletme bulunamadı.</li>';
      return;
    }
    let html = durum.suzulmus.slice(0, durum.listeSinir).map((f) => ogeHtml(f)).join('');
    if (n > durum.listeSinir) {
      html += `<li class="daha"><button type="button" id="daha-fazla">Daha fazla göster (${(n - durum.listeSinir).toLocaleString('tr')})</button></li>`;
    }
    el.liste.innerHTML = html;
  }

  function listeTiklama(e) {
    if (e.target.closest('#daha-fazla')) {
      durum.listeSinir += LISTE_ADIM * 2;
      listeyiCiz();
      return;
    }
    const oge = e.target.closest('.oge');
    if (oge) sec(oge.dataset.id);
  }
  el.liste.addEventListener('click', listeTiklama);

  let aramaZaman;
  el.arama.addEventListener('input', () => {
    clearTimeout(aramaZaman);
    aramaZaman = setTimeout(() => { durum.arama = el.arama.value; suz(); }, 120);
  });

  el.sadeceGorunen.addEventListener('change', () => {
    durum.sadeceGorunen = el.sadeceGorunen.checked;
    suz();
  });

  // ---------------------------------------------------------------- Seçim + detay
  function hashGuncelle() {
    const parcalar = location.hash.replace(/^#/, '').split('&').filter((p) => p && !p.startsWith('isletme='));
    if (durum.secili) parcalar.push(`isletme=${encodeURIComponent(durum.secili.properties.id)}`);
    history.replaceState(null, '', `${location.pathname}${location.search}#${parcalar.join('&')}`);
  }

  function hashtenIsletme() {
    const m = location.hash.match(/(?:^#|&)isletme=([^&]+)/);
    return m ? decodeURIComponent(m[1]) : null;
  }

  function sec(id, { uc = true } = {}) {
    const f = durum.kimlik.get(id);
    if (!f) return;
    durum.secili = f;
    donmeyiDurdur();
    isaretEl.style.setProperty('--renk', f.properties.renk);
    isaret.setLngLat(f.geometry.coordinates).addTo(harita);
    harita.getSource('secili')?.setData(seciliVerisi());
    detayiCiz(f);
    if (mobil()) panelBoyutu('orta');
    if (uc) {
      harita.flyTo({
        center: f.geometry.coordinates,
        zoom: Math.max(harita.getZoom(), 16.8),
        pitch: Math.max(harita.getPitch(), 55),
        speed: 1.1,
        essential: true,
      });
    }
    hashGuncelle();
  }

  function secimiKaldir() {
    durum.secili = null;
    isaret.remove();
    harita.getSource('secili')?.setData(seciliVerisi());
    el.detay.hidden = true;
    el.listeGorunumu.hidden = false;
    hashGuncelle();
  }

  function satir(baslik, icerikHtml) {
    return icerikHtml ? `<div><dt>${baslik}</dt><dd>${icerikHtml}</dd></div>` : '';
  }

  function detayiCiz(f) {
    const p = f.properties;
    const b = katBilgi(p.kat);
    const [lng, lat] = f.geometry.coordinates;
    const web = guvenliUrl(p.web);
    const sosyal = guvenliUrl(p.sosyal);
    const sosyalAd = /instagram\.com/i.test(sosyal || '') ? 'Instagram' : /facebook\.com/i.test(sosyal || '') ? 'Facebook' : 'Sosyal medya';
    const kaynak = p.kaynak === 'osm'
      ? `<a target="_blank" rel="noopener" href="https://www.openstreetmap.org/${kacis(p.osm)}">OpenStreetMap kaydı</a>`
      : `Overture Maps${SAGLAYICI[p.saglayici] ? ` (${SAGLAYICI[p.saglayici]})` : ''}${p.guven ? ` · güven %${Number(p.guven)}` : ''}`;
    const konum = `${lat.toFixed(6)},${lng.toFixed(6)}`;
    const aramaMetni = encodeURIComponent(p.adsiz ? konum : `${p.ad}, Serdivan, Sakarya`);

    const yakin = durum.tum
      .filter((d) => d !== f)
      .map((d) => ({ d, m: mesafe(f.geometry.coordinates, d.geometry.coordinates) }))
      .filter((x) => x.m <= 400)
      .sort((x, y) => x.m - y.m)
      .slice(0, 6);

    const telefonlar = (p.tel || '').split(/[;,]/).map((t) => t.trim()).filter(Boolean)
      .map((t) => `<a href="tel:${kacis(t.replace(/[^\d+]/g, ''))}">${kacis(t)}</a>`).join('<br>');

    el.detay.innerHTML = `
      <button type="button" class="geri" id="detay-geri">← Listeye dön</button>
      <div class="detay-ust" style="--renk:${b.renk}">
        <span class="detay-rozet" aria-hidden="true">${b.simge}</span>
        <div><h2>${kacis(p.ad)}</h2><p>${kacis(p.tur)} · ${kacis(b.ad)}</p></div>
      </div>
      <div class="eylemler">
        <a class="dugme ana" target="_blank" rel="noopener" href="https://www.google.com/maps/dir/?api=1&destination=${konum}">Yol tarifi</a>
        ${p.tel ? `<a class="dugme" href="tel:${kacis(p.tel.split(/[;,]/)[0].replace(/[^\d+]/g, ''))}">Ara</a>` : ''}
        ${web ? `<a class="dugme" target="_blank" rel="noopener" href="${kacis(web)}">Web sitesi</a>` : ''}
        <a class="dugme" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query=${aramaMetni}">Google Haritalar</a>
        <button type="button" class="dugme" id="detay-paylas">Bağlantıyı kopyala</button>
      </div>
      <dl class="bilgi">
        ${satir('Adres', kacis(p.adres))}
        ${satir('Telefon', telefonlar)}
        ${satir('Çalışma saati', kacis(saatYazi(p.saat)))}
        ${satir('Mutfak', kacis(p.mutfak))}
        ${satir('Marka', kacis(p.marka))}
        ${satir('İşleten', kacis(p.isleten))}
        ${satir('E-posta', p.eposta ? `<a href="mailto:${kacis(p.eposta)}">${kacis(p.eposta)}</a>` : '')}
        ${satir('Web', web ? `<a target="_blank" rel="noopener" href="${kacis(web)}">${kacis(web.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, ''))}</a>` : '')}
        ${satir('Sosyal medya', sosyal ? `<a target="_blank" rel="noopener" href="${kacis(sosyal)}">${sosyalAd} sayfası</a>` : '')}
        ${satir('Erişilebilirlik', kacis(p.engelli))}
        ${satir('Konum', `${lat.toFixed(5)}, ${lng.toFixed(5)}`)}
        ${satir('Kaynak', kaynak)}
      </dl>
      ${p.kaynak === 'osm' ? '' : '<p class="not">Bu kayıt otomatik derlenmiş açık veriden gelir; konumu yaklaşık, bilgileri güncel olmayabilir.</p>'}
      ${yakin.length ? `<h3 class="yakin-baslik">Yakındaki işletmeler</h3><ul class="yakin">${yakin.map((x) => ogeHtml(x.d, mesafeYazi(x.m))).join('')}</ul>` : ''}
    `;
    el.listeGorunumu.hidden = true;
    el.detay.hidden = false;
    el.detay.scrollTop = 0;
  }

  el.detay.addEventListener('click', async (e) => {
    if (e.target.closest('#detay-geri')) { secimiKaldir(); return; }
    if (e.target.closest('#detay-paylas')) {
      try {
        await navigator.clipboard.writeText(location.href);
        bildir('Bağlantı panoya kopyalandı.');
      } catch {
        bildir('Bağlantı kopyalanamadı; adres çubuğundan kopyalayabilirsiniz.');
      }
      return;
    }
    listeTiklama(e);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && durum.secili) secimiKaldir();
  });

  // ---------------------------------------------------------------- Araç çubuğu
  el.btnEv.addEventListener('click', () => {
    donmeyiDurdur();
    harita.flyTo({ ...BASLANGIC, essential: true });
  });

  el.btn3d.addEventListener('click', () => {
    const ucBoyut = harita.getPitch() < 20;
    harita.easeTo({ pitch: ucBoyut ? 62 : 0, bearing: ucBoyut ? harita.getBearing() : 0, duration: 800 });
  });
  harita.on('pitchend', () => el.btn3d.setAttribute('aria-pressed', String(harita.getPitch() >= 20)));

  let sonKare = 0;
  function donmeKaresi(t) {
    if (!durum.donuyor) return;
    const dt = sonKare ? Math.min(t - sonKare, 100) : 16;
    sonKare = t;
    harita.setBearing((harita.getBearing() + dt * 0.006) % 360);
    requestAnimationFrame(donmeKaresi);
  }
  function donmeyiDurdur() {
    durum.donuyor = false;
    el.btnDon.setAttribute('aria-pressed', 'false');
  }
  el.btnDon.addEventListener('click', () => {
    durum.donuyor = !durum.donuyor;
    el.btnDon.setAttribute('aria-pressed', String(durum.donuyor));
    if (durum.donuyor) {
      sonKare = 0;
      if (harita.getPitch() < 30) harita.setPitch(60);
      requestAnimationFrame(donmeKaresi);
    }
  });
  for (const olay of ['mousedown', 'touchstart', 'wheel']) {
    harita.getCanvas().addEventListener(olay, donmeyiDurdur, { passive: true });
  }

  el.btnArazi.setAttribute('aria-pressed', String(durum.arazi));
  el.btnArazi.addEventListener('click', () => {
    durum.arazi = !durum.arazi;
    sakla.yaz('serdivan-arazi', durum.arazi ? 'acik' : 'kapali');
    el.btnArazi.setAttribute('aria-pressed', String(durum.arazi));
    harita.setTerrain(durum.arazi ? { source: 'arazi', exaggeration: 1.25 } : null);
    if (durum.arazi) bildir('Arazi yükseltisi açıldı. Harita yavaşlarsa yeniden kapatabilirsiniz.');
  });

  el.btnTema.setAttribute('aria-pressed', String(durum.tema === 'koyu'));
  el.btnTema.addEventListener('click', () => {
    durum.tema = durum.tema === 'koyu' ? 'acik' : 'koyu';
    sakla.yaz('serdivan-tema', durum.tema);
    document.documentElement.dataset.tema = durum.tema;
    el.btnTema.setAttribute('aria-pressed', String(durum.tema === 'koyu'));
    harita.setTerrain(null);
    harita.setStyle(STILLER[durum.tema], { diff: false });
  });

  // Mobil alt sayfa
  function panelBoyutu(boyut) {
    el.panel.classList.toggle('kucuk', boyut === 'kucuk');
    el.panel.classList.toggle('buyuk', boyut === 'buyuk');
    dolgulamaAyarla();
  }
  $('#panel-tutamac').addEventListener('click', () => {
    if (el.panel.classList.contains('kucuk')) panelBoyutu('orta');
    else if (el.panel.classList.contains('buyuk')) panelBoyutu('kucuk');
    else panelBoyutu('buyuk');
  });
  el.arama.addEventListener('focus', () => { if (mobil()) panelBoyutu('buyuk'); });

  // ---------------------------------------------------------------- Veri
  async function veriYukle() {
    const [isletmeler, sinir] = await Promise.all([
      fetch('data/isletmeler.geojson').then((r) => { if (!r.ok) throw new Error(`isletmeler: ${r.status}`); return r.json(); }),
      fetch('data/serdivan-sinir.geojson').then((r) => (r.ok ? r.json() : null)).catch(() => null),
    ]);

    durum.sinir = sinir && (sinir.type === 'FeatureCollection' ? sinir.features[0] : sinir);
    durum.tum = isletmeler.features;
    for (const f of durum.tum) {
      const p = f.properties;
      p.renk = katBilgi(p.kat).renk;
      p.adsiz = Boolean(p.adsiz);
      durum.kimlik.set(p.id, f);
      Object.defineProperty(p, '_ara', {
        value: sade([p.ad, p.tur, katBilgi(p.kat).ad, p.adres, p.marka, p.mutfak].filter(Boolean).join(' ')),
        enumerable: false, // harita kaynağına kopyalanmasın
      });
    }
    durum.tum.sort((a, b) => (a.properties.adsiz - b.properties.adsiz) || a.properties.ad.localeCompare(b.properties.ad, 'tr'));

    const meta = isletmeler.meta || {};
    el.ozet.textContent = `Sakarya · ${durum.tum.length.toLocaleString('tr')} işletme · 3 boyutlu etkileşimli harita`;
    if (meta.tarih) el.veriTarihi.textContent = `· güncelleme: ${meta.tarih}`;

    harita.getSource('maske')?.setData(maskeVerisi());
    if (durum.sinir) harita.getSource('sinir')?.setData(durum.sinir);
    suz();

    const istenen = hashtenIsletme();
    if (istenen && durum.kimlik.has(istenen)) sec(istenen, { uc: !baglantidaKonumVar });
  }

  veriYukle().catch((hata) => {
    console.error(hata);
    el.ozet.textContent = 'İşletme verisi yüklenemedi.';
    bildir(location.protocol === 'file:'
      ? 'Veri yüklenemedi: sayfayı dosyadan değil, yerel bir sunucudan açın (ör. "python -m http.server").'
      : 'İşletme verisi yüklenemedi. Sayfayı yenilemeyi deneyin.', true);
  });

  harita.on('error', (e) => console.warn('Harita hatası:', e.error?.message || e));

  window.serdivanHarita = { harita, durum, sec }; // konsoldan denemek için
})();
