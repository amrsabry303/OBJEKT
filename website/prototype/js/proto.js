/* OBJEKT prototype behaviour. Intentionally tiny: becomes assets/theme.js in the Shopify theme.
   Each init step runs in its own guard so one failure can never disable the others (audit B-01). */
(function () {
  document.documentElement.classList.add('js');
  // Test hook: ?lang=ar sets Arabic and RTL (the theme will do this from the Shopify locale)
  try { if (new URLSearchParams(location.search).get('lang') === 'ar') { document.documentElement.lang = 'ar'; document.documentElement.dir = 'rtl'; } } catch (e) {}
  function safe(name, fn) { try { fn(); } catch (e) { if (window.console) console.warn('[objekt] ' + name + ' failed:', e); } }

  // Prototype cart store (localStorage). The theme uses Shopify's /cart.js and cart attributes instead.
  // load() never trusts what is stored: wrong shapes are dropped, not thrown on.
  var KEY = 'objekt-proto-cart';
  function validLine(l) {
    return l && typeof l === 'object' && typeof l.name === 'string' && typeof l.finish === 'string' &&
      typeof l.price === 'number' && isFinite(l.price) && l.price >= 0 &&
      typeof l.qty === 'number' && l.qty >= 1 && l.qty <= 99 && Math.floor(l.qty) === l.qty &&
      typeof l.max === 'number' && l.max >= 1 &&
      (l.kind === 'ready' || l.kind === 'mto') &&
      ((l.kind === 'ready' && Array.isArray(l.days)) || (l.kind === 'mto' && Array.isArray(l.weeks))) &&
      typeof l.sym === 'string' && typeof l.swatch === 'string';
  }
  function load() {
    var c = { lines: [], pref: 'together' };
    try {
      var raw = JSON.parse(localStorage.getItem(KEY));
      if (raw && Array.isArray(raw.lines)) {
        c.lines = raw.lines.filter(validLine);
        if (raw.pref === 'separate') c.pref = 'separate';
      }
    } catch (e) {}
    return c;
  }
  function refresh(c) {
    var n = (c || load()).lines.reduce(function (s, l) { return s + l.qty; }, 0);
    document.querySelectorAll('[data-bag]').forEach(function (e) { e.textContent = n; });
  }
  function save(c) { try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {} refresh(c); }
  window.OBJ = { load: load, save: save, refresh: refresh };

  // Prototype-only notice bar height, so the hero fits the viewport exactly (the theme has no bar)
  safe('bar', function () {
    var bar = document.querySelector('.proto-bar');
    function barH() { if (bar) document.documentElement.style.setProperty('--bar-h', bar.offsetHeight + 'px'); }
    barH(); window.addEventListener('resize', barH);
  });
  safe('bag count', function () { refresh(); });

  // Mobile menu: native <dialog> gives focus trap and Esc
  safe('menu', function () {
    var dlg = document.getElementById('menu');
    var open = document.querySelector('[data-menu-open]');
    var close = document.querySelector('[data-menu-close]');
    if (!(dlg && open && close)) return;
    open.addEventListener('click', function () { dlg.showModal(); open.setAttribute('aria-expanded', 'true'); document.body.style.overflow = 'hidden'; });
    function shut() { dlg.close(); }
    close.addEventListener('click', shut);
    dlg.addEventListener('close', function () { open.setAttribute('aria-expanded', 'false'); document.body.style.overflow = ''; open.focus(); });
    dlg.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', shut); });
  });

  // Shop panel: Esc closes it and returns focus to the Shop link
  safe('shop panel', function () {
    var items = document.querySelectorAll('.has-panel');
    items.forEach(function (li) {
      li.addEventListener('mouseleave', function () { li.classList.remove('dismiss'); });
      li.addEventListener('focusout', function (e) { if (!li.contains(e.relatedTarget)) li.classList.remove('dismiss'); });
    });
    // Esc closes the panel however it was opened (hover or focus), without moving the pointer (WCAG 1.4.13)
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      items.forEach(function (li) {
        var focusInside = li.contains(document.activeElement);
        if (li.matches(':hover') || focusInside) { li.classList.add('dismiss'); if (focusInside) li.querySelector('a').focus(); }
      });
    });
  });

  // Scroll reveal (CSS neutralises it under prefers-reduced-motion)
  safe('reveal', function () {
    var els = document.querySelectorAll('.reveal');
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
      }, { rootMargin: '0px 0px -8% 0px' });
      els.forEach(function (el) { io.observe(el); });
    } else { els.forEach(function (el) { el.classList.add('in'); }); }
  });

  // Category list drives the preview pane (hover or keyboard focus)
  safe('category preview', function () {
    var panes = document.querySelectorAll('[data-pane]');
    document.querySelectorAll('[data-cat]').forEach(function (a) {
      function show() { panes.forEach(function (p) { p.classList.toggle('on', p.dataset.pane === a.dataset.cat); }); }
      a.addEventListener('mouseenter', show); a.addEventListener('focus', show);
    });
  });

  // Prototype only: newsletter form does nothing
  safe('newsletter', function () {
    var f = document.querySelector('[data-news]');
    if (f) f.addEventListener('submit', function (e) { e.preventDefault(); f.querySelector('button').textContent = 'Prototype only'; });
  });
})();
