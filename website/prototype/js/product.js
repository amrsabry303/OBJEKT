/* Product page prototype. SAMPLE DATA ONLY.
   In the Shopify theme this object is rendered by Liquid from the product's variants,
   inventory and variant metafields (custom.fulfilment, lead_time_weeks_min/max, delivery_days_min/max). */
(function () {
  var PRODUCT = {
    material: 'To be supplied',
    lowStockAt: 5,
    variants: [
      { id: 101, finish: 'Walnut',          swatch: '#5C4033', price: 9800,  fulfilment: 'ready',         qty: 4, days: [3, 5] },
      { id: 102, finish: 'Oak',             swatch: '#C2A173', price: 9800,  fulfilment: 'ready',         qty: 0, days: [3, 5] },
      { id: 103, finish: 'Oxblood',         swatch: '#5A1F24', price: 11200, fulfilment: 'made_to_order', qty: 0, weeks: [8, 10] },
      { id: 104, finish: 'Stainless Steel', swatch: '#A9AEB3', price: 14500, fulfilment: 'made_to_order', qty: 0, weeks: [10, 12] }
    ]
  };

  var $ = function (id) { return document.getElementById(id); };
  var list = $('finish-list');
  var current = null;

  function money(n) { return 'EGP ' + n.toLocaleString('en-US'); }
  function range(a) { return a[0] + '–' + a[1]; }

  // Derived state: one function decides what the customer sees (mirrors the Liquid logic in SHOPIFY_ARCHITECTURE.md)
  function state(v) {
    if (v.fulfilment === 'ready' && v.qty <= 0) {
      return { key: 'out', label: 'Sold out', short: 'Sold out', l1: 'This finish is not currently available.', l2: 'Not converted to made to order automatically.', btn: 'Sold out', disabled: true };
    }
    if (v.fulfilment === 'ready') {
      return { key: 'ready', label: 'Ready to deliver', short: 'Ready to deliver',
        l1: v.qty <= PRODUCT.lowStockAt ? v.qty + ' available' : 'In stock',
        l2: 'Delivery in ' + range(v.days) + ' working days',
        btn: 'Add to bag' };
    }
    return { key: 'mto', label: 'Made to order', short: 'Made to order · ' + range(v.weeks) + ' wks',
      l1: 'Made after you order. Estimated production ' + range(v.weeks) + ' weeks.',
      l2: 'Purchasing terms to be confirmed by OBJEKT.',
      btn: 'Made to order' };
  }
  function dot(key) { return '<span class="dot' + (key === 'mto' ? ' dot--mto' : key === 'out' ? ' dot--out' : '') + '"></span>'; }

  // Build the option list once
  PRODUCT.variants.forEach(function (v) {
    var s = state(v);
    var row = document.createElement('label');
    row.className = 'opt' + (s.key === 'out' ? ' is-out' : '');
    row.innerHTML = '<input type="radio" name="finish" value="' + v.id + '">' +
      '<span class="sw" style="--c:' + v.swatch + '"></span><span class="nm">' + v.finish + '</span>' +
      '<span class="st">' + dot(s.key) + s.short + '</span>';
    row.querySelector('input').addEventListener('change', function () { select(v.id, true); });
    list.appendChild(row);
  });

  function select(id, fromUser) {
    var v = PRODUCT.variants.filter(function (x) { return x.id === id; })[0] || PRODUCT.variants[0];
    current = v; var s = state(v);
    list.querySelectorAll('input').forEach(function (i) { i.checked = (+i.value === v.id); });

    $('price').textContent = money(v.price);
    $('finish-name').textContent = '· ' + v.finish;
    $('spec-finish').textContent = v.finish;
    $('spec-material').textContent = PRODUCT.material;
    $('avail-state').innerHTML = dot(s.key) + s.label;
    $('avail-l1').textContent = s.l1; $('avail-l2').textContent = s.l2;

    [['add', 'sticky-add']].forEach(function (p) {
      p.forEach(function (bid) {
        var b = $(bid); b.textContent = s.btn;
        b.disabled = !!s.disabled; b.classList.toggle('btn--mto', s.key === 'mto');
      });
    });
    $('sticky-state').textContent = s.label; $('sticky-price').textContent = money(v.price);
    $('status').textContent = '';
    $('pdp').style.setProperty('--v-obj', v.swatch);
    $('gallery').style.setProperty('--v-obj', v.swatch);

    try { var u = new URL(location.href); u.searchParams.set('variant', v.id); history.replaceState(null, '', u); } catch (e) {}
    // Polite announcement for assistive tech: the avail box is an aria-live region
  }

  function add() {
    if (!current) return; var s = state(current); if (s.disabled) return;
    var cart = OBJ.load(), max = s.key === 'ready' ? current.qty : 10;
    var line = cart.lines.filter(function (l) { return l.id === current.id; })[0];
    if (line && line.qty + 1 > max) { $('status').textContent = 'Only ' + max + ' available, already in your bag'; return; }
    if (line) line.qty += 1;
    else cart.lines.push({ id: current.id, name: 'Drum side table', ref: 'SMP-02', finish: current.finish, swatch: current.swatch, price: current.price,
      kind: s.key, max: max, days: current.days || null, weeks: current.weeks || null, qty: 1, sym: 'stool', href: 'product.html?variant=' + current.id });
    OBJ.save(cart);
    $('status').textContent = s.key === 'mto'
      ? 'Added · made to order, ' + range(current.weeks) + ' weeks (prototype)'
      : 'Added to bag (prototype)';
  }
  $('add').addEventListener('click', add); $('sticky-add').addEventListener('click', add);

  // Initial variant from ?variant=
  var q = parseInt(new URLSearchParams(location.search).get('variant'), 10);
  select(q || PRODUCT.variants[0].id);

  // Mobile gallery counter
  var g = $('gallery'), n = $('g-count');
  g.addEventListener('scroll', function () {
    var kids = g.querySelectorAll('.g'), w = kids[0].getBoundingClientRect().width + 8;
    n.textContent = (Math.min(kids.length, Math.round(Math.abs(g.scrollLeft) / w) + 1)) + ' / ' + kids.length;
  }, { passive: true });

  // Sticky buy bar on small screens when the main button is off screen
  var sticky = $('sticky');
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) {
      var out = !e[0].isIntersecting && e[0].boundingClientRect.top < 0;
      sticky.hidden = !out;
    }).observe($('buy'));
  }
})();
