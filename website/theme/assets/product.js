(function () {
  var root = document.getElementById('product-root');
  if (!root) return;
  function safe(fn) { try { fn(); } catch (e) { /* one failing step must not stop the rest */ } }
  function $(id) { return document.getElementById(id); }
  var sectionId = root.dataset.sectionId, productUrl = root.dataset.productUrl;

  function setBag(n) { document.querySelectorAll('[data-bag]').forEach(function (el) { el.textContent = n; }); }
  function say(msg) { var s = $('status'); if (s) s.textContent = msg; }

  // Sticky buy bar: only on small screens, when the main button is off screen
  var io;
  function initSticky() {
    safe(function () {
      var sticky = $('sticky-buy'), buy = $('buy');
      if (io) io.disconnect();
      if (!sticky || !buy || !('IntersectionObserver' in window)) return;
      io = new IntersectionObserver(function (e) { sticky.hidden = !(!e[0].isIntersecting && e[0].boundingClientRect.top < 0); });
      io.observe(buy);
    });
  }

  // Desktop gallery: one large framed image with a thumbnail strip beside it (CSS shows it from 881px up).
  // Small screens keep the swipe strip. Without this script every image simply shows.
  var mediaByVariant = {};
  function setActive(mediaId) {
    var gal = $('gallery'); if (!gal || !gal.classList.contains('zh')) return;
    var on = null;
    gal.querySelectorAll('.g[data-media-id]').forEach(function (g) {
      var is = g.dataset.mediaId === String(mediaId);
      g.classList.toggle('is-on', is); if (is) on = g;
    });
    if (!on) return;
    var img = on.querySelector('img'); if (img) { img.loading = 'eager'; img.removeAttribute('fetchpriority'); }
    gal.querySelectorAll('.th').forEach(function (t) {
      var is = t.dataset.mediaId === String(mediaId);
      t.classList.toggle('is-on', is); if (is) t.setAttribute('aria-current', 'true'); else t.removeAttribute('aria-current');
    });
  }
  safe(function () {
    var gal = $('gallery'); if (!gal) return;
    var tiles = gal.querySelectorAll('.g[data-media-id]'); if (tiles.length < 2) return;
    var strip = document.createElement('div'); strip.className = 'th-strip';
    tiles.forEach(function (g, i) {
      var src = (g.querySelector('img') || {}).src || '';
      var b = document.createElement('button'); b.type = 'button'; b.className = 'th'; b.dataset.mediaId = g.dataset.mediaId;
      b.setAttribute('aria-label', (i + 1) + ' / ' + tiles.length);
      var im = document.createElement('img'); im.src = src.replace(/width=\d+/, 'width=240'); im.alt = ''; im.loading = 'lazy';
      b.appendChild(im); strip.appendChild(b);
    });
    gal.insertBefore(strip, gal.firstChild);
    strip.addEventListener('click', function (e) { var t = e.target.closest && e.target.closest('.th'); if (t) setActive(t.dataset.mediaId); });
    gal.classList.add('zh');
    setActive(tiles[0].dataset.mediaId);
  });
  function mapMedia() {
    root.querySelectorAll('a.opt[data-media-id]').forEach(function (a) {
      if (a.dataset.mediaId) mediaByVariant[a.dataset.variantId] = a.dataset.mediaId;
    });
  }
  mapMedia();
  function showVariantMedia(id) {
    mapMedia();
    var m = mediaByVariant[id];
    if (!m) return;
    var gal = $('gallery');
    var g = gal && gal.querySelector('.g[data-media-id="' + m + '"]');
    if (!g) return;
    setActive(m);
    if (matchMedia('(max-width: 880px)').matches && g.scrollIntoView) {
      var calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
      g.scrollIntoView({ block: 'nearest', inline: 'start', behavior: calm ? 'auto' : 'smooth' });
    }
  }
  safe(function () {
    var cur = root.querySelector('a.opt[aria-current="true"]');
    if (cur) { var m = mediaByVariant[cur.dataset.variantId]; if (m) setActive(m); }
  });

  // Variant switch: Shopify renders the buy box (rules stay in Liquid)
  function swap(variantId, push) {
    var box = $('buy-box'); if (!box) return;
    box.setAttribute('aria-busy', 'true');
    fetch(productUrl + '?variant=' + encodeURIComponent(variantId) + '&section_id=' + encodeURIComponent(sectionId))
      .then(function (r) { return r.ok ? r.text() : Promise.reject(r.status); })
      .then(function (html) {
        var doc = new DOMParser().parseFromString(html, 'text/html'), fresh = doc.getElementById('buy-box');
        if (!fresh) throw new Error('no buy box');
        box.innerHTML = fresh.innerHTML;
        safe(function () { var u = new URL(location.href); u.searchParams.set('variant', variantId); history.replaceState(null, '', u); });
        initSticky(); safe(function () { showVariantMedia(variantId); });
        var cur = box.querySelector('.opt[aria-current="true"]'); if (cur) cur.focus();
      })
      .catch(function () { location.href = productUrl + '?variant=' + variantId; })
      .then(function () { box.removeAttribute('aria-busy'); });
  }
  safe(function () {
    root.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a.opt'); if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
      e.preventDefault(); swap(a.dataset.variantId);
    });
  });

  // Add to bag: JSON items (not FormData), show Shopify's own message on 422
  safe(function () {
    root.addEventListener('submit', function (e) {
      // form.id is shadowed by the <input name="id">, so match by selector, not by property
      var form = e.target; if (!form || !form.matches || !form.matches('#product-form')) return;
      e.preventDefault();
      var fd = new FormData(form), props = {};
      fd.forEach(function (v, k) { var m = /^properties\[(.+)\]$/.exec(k); if (m) props[m[1]] = v; });
      var btns = form.querySelectorAll('[data-add]'); btns.forEach(function (b) { b.disabled = true; });
      fetch(window.Shopify && Shopify.routes ? Shopify.routes.root + 'cart/add.js' : '/cart/add.js', {
        method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ items: [{ id: Number(fd.get('id')), quantity: 1, properties: props }] })
      }).then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (!res.ok) { say(res.j.description || res.j.message || root.dataset.error); return; }
          say(root.dataset.added);
          return fetch('/cart.js', { headers: { Accept: 'application/json' } }).then(function (r) { return r.json(); }).then(function (c) { setBag(c.item_count); });
        })
        .catch(function () { say(root.dataset.error); })
        .then(function () { btns.forEach(function (b) { b.disabled = false; }); });
    });
  });

  // Mobile gallery counter (direction-aware: scrollLeft is negative in RTL)
  safe(function () {
    var g = $('gallery'), n = $('g-count'); if (!g || !n) return;
    g.addEventListener('scroll', function () {
      var kids = g.querySelectorAll('.g'), w = kids[0].getBoundingClientRect().width + 8;
      n.textContent = Math.min(kids.length, Math.round(Math.abs(g.scrollLeft) / w) + 1) + ' / ' + kids.length;
    }, { passive: true });
  });
  initSticky();
})();
