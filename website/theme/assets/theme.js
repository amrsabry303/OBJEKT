(function () {
  function safe(fn) { try { fn(); } catch (e) { /* one failing step must not stop the rest */ } }
  // Side pane: a native <dialog> opened without a backdrop so the header stays usable.
  // Desktop with a mouse: opens when the pointer rests on the burger, closes shortly after it leaves.
  // Everywhere: click toggles; Esc and a click outside close it.
  safe(function () {
    var dlg = document.getElementById('menu');
    var btn = document.querySelector('[data-menu-toggle]');
    if (!dlg || !btn || !dlg.show) return;
    var hover = matchMedia('(hover: hover) and (min-width: 881px)'), timer;
    function open(focus) {
      dlg.show(); btn.setAttribute('aria-expanded', 'true');
      if (focus) { var first = dlg.querySelector('a, summary'); if (first) first.focus({ preventScroll: true }); }
    }
    function later() { clearTimeout(timer); timer = setTimeout(function () { if (dlg.open) dlg.close(); }, 280); }
    function keep() { clearTimeout(timer); }
    dlg.addEventListener('close', function () { btn.setAttribute('aria-expanded', 'false'); });
    btn.addEventListener('click', function () { keep(); if (dlg.open) dlg.close(); else open(true); });
    btn.addEventListener('mouseenter', function () { if (!hover.matches) return; keep(); if (!dlg.open) open(false); });
    btn.addEventListener('mouseleave', function () { if (hover.matches) later(); });
    dlg.addEventListener('mouseenter', function () { if (hover.matches) keep(); });
    dlg.addEventListener('mouseleave', function () { if (hover.matches) later(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && dlg.open) { dlg.close(); btn.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (dlg.open && !dlg.contains(e.target) && !btn.contains(e.target)) dlg.close();
    });
  });

  // Quick add on product cards: JSON add, bag count updated, no page change
  safe(function () {
    document.addEventListener('submit', function (e) {
      var f = e.target; if (!f || !f.matches || !f.matches('form[data-quick]')) return;
      e.preventDefault();
      var btn = f.querySelector('.quick__btn'), txt = f.querySelector('.quick__txt'), plus = f.querySelector('.quick__plus'), st = f.querySelector('.quick__status');
      var label = txt.textContent, props = {};
      new FormData(f).forEach(function (v, k) { var m = /^properties\[(.+)\]$/.exec(k); if (m) props[m[1]] = v; });
      btn.disabled = true;
      function show(state, msg) { btn.dataset.state = state; txt.textContent = msg; if (plus) plus.textContent = state === 'ok' ? '\u2713' : '!'; if (st) st.textContent = msg; }
      var root = (window.Shopify && Shopify.routes && Shopify.routes.root) || '/';
      fetch(root + 'cart/add.js', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ items: [{ id: Number(f.elements.id.value), quantity: 1, properties: props }] }) })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (!res.ok) { show('err', f.dataset.error); if (st) st.textContent = res.j.description || f.dataset.error; return; }
          show('ok', f.dataset.added);
          return fetch(root + 'cart.js', { headers: { Accept: 'application/json' } }).then(function (r) { return r.json(); })
            .then(function (c) { document.querySelectorAll('[data-bag]').forEach(function (el) { el.textContent = c.item_count; }); });
        })
        .catch(function () { show('err', f.dataset.error); })
        .then(function () { btn.disabled = false; setTimeout(function () { delete btn.dataset.state; txt.textContent = label; if (plus) plus.textContent = '+'; }, 2400); });
    });
  });
})();
