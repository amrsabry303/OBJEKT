(function () {
  function safe(fn) { try { fn(); } catch (e) { /* one failing step must not stop the rest */ } }
  // Mobile menu: native <dialog> gives focus trap and Esc
  safe(function () {
    var dlg = document.getElementById('menu');
    var open = document.querySelector('[data-menu-open]');
    var close = document.querySelector('[data-menu-close]');
    if (!dlg || !open || !dlg.showModal) return;
    open.addEventListener('click', function () { dlg.showModal(); open.setAttribute('aria-expanded', 'true'); });
    function shut() { dlg.close(); }
    if (close) close.addEventListener('click', shut);
    dlg.addEventListener('close', function () { open.setAttribute('aria-expanded', 'false'); open.focus(); });
  });
  // Header panel: Esc closes it however it was opened (WCAG 1.4.13)
  safe(function () {
    document.querySelectorAll('.has-panel').forEach(function (li) {
      function undismiss() { li.classList.remove('dismiss'); }
      li.addEventListener('mouseleave', undismiss);
      li.addEventListener('focusout', function (e) { if (!li.contains(e.relatedTarget)) undismiss(); });
      document.addEventListener('keydown', function (e) {
        if (e.key !== 'Escape' || !(li.matches(':hover') || li.contains(document.activeElement))) return;
        li.classList.add('dismiss');
        var a = li.querySelector(':scope > a');
        if (a && li.contains(document.activeElement)) a.focus();
      });
    });
  });

  // Quick add on product cards: JSON add, bag count updated, no page change
  safe(function () {
    document.addEventListener('submit', function (e) {
      var f = e.target; if (!f || !f.matches || !f.matches('form[data-quick]')) return;
      e.preventDefault();
      var btn = f.querySelector('.quick__btn'), st = f.querySelector('.quick__status'), label = btn.textContent, props = {};
      new FormData(f).forEach(function (v, k) { var m = /^properties\[(.+)\]$/.exec(k); if (m) props[m[1]] = v; });
      btn.disabled = true;
      var root = (window.Shopify && Shopify.routes && Shopify.routes.root) || '/';
      fetch(root + 'cart/add.js', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ items: [{ id: Number(f.elements.id.value), quantity: 1, properties: props }] }) })
        .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
        .then(function (res) {
          if (!res.ok) { btn.textContent = f.dataset.error; if (st) st.textContent = res.j.description || f.dataset.error; return; }
          btn.textContent = f.dataset.added; if (st) st.textContent = f.dataset.added;
          return fetch(root + 'cart.js', { headers: { Accept: 'application/json' } }).then(function (r) { return r.json(); })
            .then(function (c) { document.querySelectorAll('[data-bag]').forEach(function (el) { el.textContent = c.item_count; }); });
        })
        .catch(function () { btn.textContent = f.dataset.error; })
        .then(function () { btn.disabled = false; setTimeout(function () { btn.textContent = label; }, 2200); });
    });
  });
})();
