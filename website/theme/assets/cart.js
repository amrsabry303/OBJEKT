(function () {
  var root = document.getElementById('cart-root');
  if (!root) return;
  function safe(fn) { try { fn(); } catch (e) { /* one failing step must not stop the rest */ } }
  var sectionId = root.dataset.sectionId;
  function say(msg) { var s = document.getElementById('msg'); if (s) s.textContent = msg; }
  function setBag(n) { document.querySelectorAll('[data-bag]').forEach(function (el) { el.textContent = n; }); }
  function post(url, body) {
    return fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); });
  }

  // Ask Shopify to render the bag again; rules and totals stay in Liquid
  function refresh(focusSel) {
    root.setAttribute('aria-busy', 'true');
    return fetch('/cart?section_id=' + encodeURIComponent(sectionId))
      .then(function (r) { return r.ok ? r.text() : Promise.reject(r.status); })
      .then(function (html) {
        var fresh = new DOMParser().parseFromString(html, 'text/html').getElementById('cart-root');
        if (!fresh) throw new Error('no bag');
        root.innerHTML = fresh.innerHTML; root.dataset.count = fresh.dataset.count;
        setBag(fresh.dataset.count); initSticky();
        var el = focusSel && root.querySelector(focusSel); if (el) el.focus();
      })
      .catch(function () { location.reload(); })
      .then(function () { root.removeAttribute('aria-busy'); });
  }

  function change(line, qty, focusSel) {
    return post('/cart/change.js', { line: Number(line), quantity: qty }).then(function (res) {
      if (!res.ok) { say(res.j.description || res.j.message || root.dataset.error); return refresh(focusSel); }
      return refresh(focusSel);
    }).catch(function () { say(root.dataset.error); });
  }

  safe(function () {
    root.addEventListener('click', function (e) {
      var b = e.target.closest && e.target.closest('[data-act]'); if (!b) return;
      var row = b.closest('.line'); if (!row) return;
      var input = row.querySelector('input[name^="updates["]'), line = row.dataset.line, q = parseInt(input.value, 10) || 0;
      var sel = '.line[data-line="' + line + '"] ';
      if (b.dataset.act === 'inc') { e.preventDefault(); change(line, q + 1, sel + '[data-act="inc"]'); }
      else if (b.dataset.act === 'dec') { e.preventDefault(); change(line, Math.max(0, q - 1), sel + '[data-act="dec"]'); }
      else if (b.dataset.act === 'rm') { e.preventDefault(); change(line, 0, '#cart-form a, .cart__empty a'); }
    });
    root.addEventListener('change', function (e) {
      var t = e.target;
      if (t.matches && t.matches('input[name^="updates["]')) {
        var row = t.closest('.line'); change(row.dataset.line, Math.max(0, parseInt(t.value, 10) || 0), '.line[data-line="' + row.dataset.line + '"] input[name^="updates["]');
      } else if (t.matches && t.matches('input[name="attributes[delivery_preference]"]')) {
        post('/cart/update.js', { attributes: { delivery_preference: t.value } })
          .then(function (res) { say(res.ok ? root.dataset.saved : (res.j.description || root.dataset.error)); })
          .catch(function () { say(root.dataset.error); });
      }
    });
  });

  var io;
  function initSticky() {
    safe(function () {
      var sticky = document.getElementById('sticky-checkout'), btn = document.getElementById('cart-checkout');
      if (io) io.disconnect();
      if (!sticky || !btn || !('IntersectionObserver' in window)) return;
      io = new IntersectionObserver(function (e) { sticky.hidden = !(!e[0].isIntersecting && e[0].boundingClientRect.top < 0); });
      io.observe(btn);
    });
  }
  initSticky();
})();
