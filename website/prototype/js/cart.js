/* Bag page prototype. SAMPLE DATA ONLY.
   Theme equivalent: cart lines from Shopify cart (/cart.js), delivery_preference saved with /cart/update.js {attributes},
   made-to-order flag and lead time from line item properties (see docs/SHOPIFY_ARCHITECTURE.md). */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var cart = OBJ.load();
  function money(n) { return 'EGP ' + n.toLocaleString('en-US'); }
  function rng(a) { return a[0] + '–' + a[1]; }
  function sum(l) { return l.reduce(function (s, x) { return s + x.price * x.qty; }, 0); }
  function span(lines, key) {
    var lo = 0, hi = 0; lines.forEach(function (l) { lo = Math.max(lo, l[key][0]); hi = Math.max(hi, l[key][1]); }); return [lo, hi];
  }
  function save() { OBJ.save(cart); render(); }

  var SAMPLE = [
    { id: 101, name: 'Drum side table', ref: 'SMP-02', finish: 'Walnut', swatch: '#5C4033', price: 9800, kind: 'ready', max: 4, days: [3, 5], weeks: null, qty: 1, sym: 'stool', href: 'product.html?variant=101' },
    { id: 103, name: 'Drum side table', ref: 'SMP-02', finish: 'Oxblood', swatch: '#5A1F24', price: 11200, kind: 'mto', max: 10, days: null, weeks: [8, 10], qty: 1, sym: 'stool', href: 'product.html?variant=103' },
    { id: 301, name: 'Tray', ref: 'SMP-05', finish: 'Stainless Steel', swatch: '#A9AEB3', price: 2600, kind: 'ready', max: 6, days: [3, 5], weeks: null, qty: 2, sym: 'tray', href: '#' }
  ];

  function lineHtml(l, i) {
    var mto = l.kind === 'mto';
    var a = mto ? '<span class="dot dot--mto"></span><span>Made to order · ' + rng(l.weeks) + ' weeks</span>' : '<span class="dot"></span><span>Ready to deliver · ' + rng(l.days) + ' working days</span>';
    var atMax = l.qty >= l.max, who = l.name + ', ' + l.finish;
    return '<li class="line" data-i="' + i + '">' +
      '<a class="line__img ph ' + (i % 2 ? 'ph--paper' : '') + '" style="--pc:' + l.swatch + '" href="' + l.href + '" tabindex="-1" aria-hidden="true"><svg viewBox="0 0 200 200" preserveAspectRatio="xMidYMax meet" aria-hidden="true"><use href="#' + l.sym + '"/></svg></a>' +
      '<div class="line__main"><a class="name" href="' + l.href + '">' + l.name + '</a>' +
      '<p class="muted">Finish: ' + l.finish + ' · <span class="label">' + l.ref + '</span></p>' +
      '<p class="avail label muted">' + a + '</p>' +
      '<div class="line__ctl"><div class="qty" role="group" aria-label="Quantity of ' + who + '">' +
      '<button type="button" data-act="dec" aria-label="Decrease quantity of ' + who + '">−</button><output aria-live="polite">' + l.qty + '</output>' +
      '<button type="button" data-act="inc" aria-label="Increase quantity of ' + who + '"' + (atMax ? ' disabled' : '') + '>+</button></div>' +
      '<button class="link" type="button" data-act="rm" aria-label="Remove ' + who + '">Remove</button></div>' +
      (atMax && !mto ? '<p class="note">Maximum available</p>' : '') + '</div>' +
      '<p class="line__price">' + money(l.price * l.qty) + (l.qty > 1 ? '<br><span class="muted label">' + money(l.price) + ' each</span>' : '') + '</p></li>';
  }
  function group(title, lines) {
    if (!lines.length) return '';
    return '<section class="group"><h2 class="label">' + title + '</h2><ul>' + lines.map(function (l) { return lineHtml(l, cart.lines.indexOf(l)); }).join('') + '</ul></section>';
  }

  function render() {
    var L = cart.lines, ready = L.filter(function (l) { return l.kind === 'ready'; }), mto = L.filter(function (l) { return l.kind === 'mto'; });
    var n = L.reduce(function (s, l) { return s + l.qty; }, 0);
    $('cart-count').textContent = n ? '(' + n + ')' : '';
    $('empty').hidden = n > 0; $('grid').hidden = n === 0;
    $('lines').innerHTML = group('Ready to deliver', ready) + group('Made to order', mto);
    var mixed = ready.length && mto.length;
    $('pref').hidden = !mixed;
    var d = $('deliv');
    if (mixed) {
      var rd = span(ready, 'days'), mw = span(mto, 'weeks');
      $('pref-together').textContent = 'Everything ships when your made-to-order pieces are ready, in about ' + rng(mw) + ' weeks.';
      $('pref-separate').textContent = 'Ready pieces ship in ' + rng(rd) + ' working days. Made-to-order pieces ship in about ' + rng(mw) + ' weeks.';
      document.querySelectorAll('input[name=pref]').forEach(function (r) { r.checked = (r.value === cart.pref); });
      d.hidden = true;
    } else if (n) {
      d.hidden = false;
      d.textContent = ready.length ? 'Estimated delivery in ' + rng(span(ready, 'days')) + ' working days.' : 'Made after you order. Estimated production ' + rng(span(mto, 'weeks')) + ' weeks.';
    }
    var total = sum(L); $('sub').textContent = money(total); $('sticky-total').textContent = money(total);
    $('dep').hidden = !mto.length;
    if (mto.length) $('dep-text').textContent = 'Made-to-order pieces (' + money(sum(mto)) + ') need a deposit. Amount, payment method and terms to be confirmed by OBJEKT.';
    $('devdata').textContent = JSON.stringify({
      attributes: mixed ? { delivery_preference: cart.pref } : {},
      items: L.map(function (l) { return { variant_id: l.id, quantity: l.qty, properties: l.kind === 'mto' ? { _fulfilment: 'made_to_order', _lead_time_weeks: rng(l.weeks) } : { _fulfilment: 'ready' } }; })
    }, null, 2);
  }

  $('lines').addEventListener('click', function (e) {
    var b = e.target.closest('button[data-act]'); if (!b) return;
    var i = +b.closest('.line').dataset.i, l = cart.lines[i], act = b.dataset.act, who = l.name + ', ' + l.finish;
    if (act === 'inc' && l.qty < l.max) l.qty += 1;
    if (act === 'dec') { l.qty -= 1; if (l.qty < 1) { cart.lines.splice(i, 1); $('msg').textContent = who + ' removed'; save(); focusAfterRemove(); return; } }
    if (act === 'rm') { cart.lines.splice(i, 1); $('msg').textContent = who + ' removed'; save(); focusAfterRemove(); return; }
    var idx = i; save();
    var again = document.querySelector('.line[data-i="' + idx + '"] [data-act="' + act + '"]'); if (again && !again.disabled) again.focus();
  });
  function focusAfterRemove() { var h = $('cart').querySelector('.line .name') || $('load-sample'); if (h) h.focus(); }

  document.querySelectorAll('input[name=pref]').forEach(function (r) { r.addEventListener('change', function () { cart.pref = r.value; OBJ.save(cart); render(); }); });
  $('load-sample').addEventListener('click', function () { cart.lines = JSON.parse(JSON.stringify(SAMPLE)); cart.pref = 'together'; save(); });
  function go() { $('msg').textContent = 'Prototype: checkout is not built. In the theme this opens Shopify checkout' + (cart.lines.some(function (l) { return l.kind === 'mto'; }) ? ', with deposit instructions after the order.' : '.'); }
  $('checkout').addEventListener('click', go); $('sticky-checkout').addEventListener('click', go);

  var sticky = $('sticky');
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) { sticky.hidden = e[0].isIntersecting || cart.lines.length === 0; }).observe($('checkout'));
  }
  render();
})();
