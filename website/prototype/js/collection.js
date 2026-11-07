/* Collection page prototype. SAMPLE DATA ONLY.
   In Shopify: filters come from Search & Discovery (collection.filters), sorting from collection.sort_by,
   availability from variant metafield custom.fulfilment (see docs/PRODUCT_SCHEMA.md). */
(function () {
  // Placeholder swatches for the objekt colour guide names (hex values not yet supplied: replace from the guide)
  var COL = { bone: '#E8E0D2', putty: '#CBBFAE', carbon: '#2B2B2B', ink: '#263A5A', oxblood: '#5A1F24', clay: '#B2705A', green: '#3F5B45' };
  var P = [
    { n: 'Tall vase',        ref: 'SMP-01', cat: 'objects',   type: 'vases',          price: 4800,  av: 'mto',   wk: [6, 8],   proc: ['moulded'],      fin: ['lacquered'],                  col: 'oxblood', rooms: ['living', 'dining'],   sym: 'vase' },
    { n: 'Drum side table',  ref: 'SMP-02', cat: 'furniture', type: 'side-tables',    price: 9800,  av: 'mixed', wk: [8, 10],  proc: ['metal'],        fin: ['brushed', 'powder-coated'],   col: 'carbon',  rooms: ['bedside', 'living'],  sym: 'stool', href: 'product.html' },
    { n: 'Pedestal',         ref: 'SMP-03', cat: 'furniture', type: 'pedestals',      price: 7400,  av: 'mto',   wk: [8, 10],  proc: ['metal'],        fin: ['powder-coated'],              col: 'carbon',  rooms: ['living', 'entry'],    sym: 'plinth' },
    { n: 'Coffee table',     ref: 'SMP-04', cat: 'furniture', type: 'coffee-tables',  price: 24500, av: 'mto',   wk: [10, 12], proc: ['curved metal'], fin: ['mirror polish'],              col: 'ink',     rooms: ['living'],             sym: 'console' },
    { n: 'Tray',             ref: 'SMP-05', cat: 'living',    type: 'trays',          price: 2600,  av: 'ready',                proc: ['metal'],        fin: ['mirror polish'],              col: 'putty',   rooms: ['dining', 'living'],   sym: 'tray' },
    { n: 'Bowl',             ref: 'SMP-06', cat: 'living',    type: 'bowls',          price: 3200,  av: 'mto',   wk: [6, 8],   proc: ['moulded'],      fin: ['lacquered'],                  col: 'bone',    rooms: ['dining', 'desk'],     sym: 'plinth' },
    { n: 'Bench',            ref: 'SMP-07', cat: 'furniture', type: 'stools-benches', price: 18500, av: 'mto',   wk: [8, 10],  proc: ['metal'],        fin: ['powder-coated'],              col: 'clay',    rooms: ['entry', 'living'],    sym: 'console' },
    { n: 'Floor planter',    ref: 'SMP-08', cat: 'planters',  type: 'floor-planters', price: 11200, av: 'mto',   wk: [10, 12], proc: ['curved metal'], fin: ['powder-coated'],              col: 'green',   rooms: ['balcony', 'living'],  sym: 'vase' },
    { n: 'Tabletop planter', ref: 'SMP-09', cat: 'planters',  type: 'tabletop-planters', price: 3900, av: 'mixed', wk: [6, 8], proc: ['moulded'],      fin: ['lacquered'],                  col: 'bone',    rooms: ['desk', 'living'],     sym: 'plinth' },
    { n: 'Candleholder',     ref: 'SMP-10', cat: 'objects',   type: 'candleholders',  price: 2100,  av: 'ready',                proc: ['metal'],        fin: ['brushed'],                    col: 'ink',     rooms: ['dining'],             sym: 'vase' },
    { n: 'Coaster set',      ref: 'SMP-11', cat: 'living',    type: 'coasters',       price: 1500,  av: 'out',                  proc: ['metal'],        fin: ['brushed'],                    col: 'putty',   rooms: ['dining'],             sym: 'tray' },
    { n: 'Wall shelf',       ref: 'SMP-12', cat: 'objects',   type: 'shelves',        price: 6900,  av: 'mto',   wk: [6, 8],   proc: ['printed'],      fin: ['lacquered'],                  col: 'oxblood', rooms: ['living', 'entry'],    sym: 'arch' }
  ];
  var G = [
    { key: 'av',  label: 'Availability', open: true, opts: [['ready', 'Ready to deliver'], ['mto', 'Made to order']],
      test: function (p, v) { return v === 'ready' ? (p.av === 'ready' || p.av === 'mixed') : (p.av === 'mto' || p.av === 'mixed'); } },
    { key: 'cat', label: 'Category', opts: [['furniture', 'Furniture'], ['living', 'Table & Living'], ['objects', 'Objects'], ['planters', 'Planters']],
      test: function (p, v) { return p.cat === v; } },
    { key: 'type', label: 'Product type', opts: [['coffee-tables', 'Coffee tables'], ['side-tables', 'Side and bedside tables'], ['stools-benches', 'Stools and benches'], ['pedestals', 'Pedestals and plinths'], ['trays', 'Trays'], ['bowls', 'Bowls and baskets'], ['coasters', 'Coasters and trivets'], ['candleholders', 'Candleholders'], ['vases', 'Vases'], ['shelves', 'Shelves'], ['floor-planters', 'Floor planters'], ['tabletop-planters', 'Tabletop planters']],
      test: function (p, v) { return p.type === v; } },
    { key: 'room', label: 'Room', opts: [['living', 'Living'], ['dining', 'Dining'], ['bedside', 'Bedside'], ['desk', 'Desk'], ['entry', 'Entry'], ['balcony', 'Balcony']],
      test: function (p, v) { return p.rooms.indexOf(v) > -1; } },
    { key: 'proc', label: 'Process', opts: [['metal', 'Metal'], ['curved metal', 'Curved metal'], ['moulded', 'Moulded'], ['printed', 'Printed']],
      test: function (p, v) { return p.proc.indexOf(v) > -1; } },
    { key: 'fin', label: 'Finish', opts: [['mirror polish', 'Mirror polish'], ['brushed', 'Brushed'], ['lacquered', 'Lacquered'], ['powder-coated', 'Powder-coated']],
      test: function (p, v) { return p.fin.indexOf(v) > -1; } },
    { key: 'col', label: 'Colour', swatch: true, opts: [['bone', 'Bone'], ['putty', 'Putty'], ['carbon', 'Carbon'], ['ink', 'Ink'], ['oxblood', 'Oxblood'], ['clay', 'Clay'], ['green', 'Objekt Green']],
      test: function (p, v) { return p.col === v; } },
    { key: 'pr',  label: 'Price (EGP)', opts: [['lt5', 'Under 5,000'], ['5to10', '5,000 to 10,000'], ['gt10', 'Over 10,000']],
      test: function (p, v) { return v === 'lt5' ? p.price < 5000 : v === 'gt10' ? p.price > 10000 : (p.price >= 5000 && p.price <= 10000); } }
  ];
  var $ = function (id) { return document.getElementById(id); };
  var F = {}, sort = 'featured';
  G.forEach(function (g) { F[g.key] = []; });

  function inGroup(p, g, vals) { return !vals.length || vals.some(function (v) { return g.test(p, v); }); }
  function matches(p, skip) { return G.every(function (g) { return g.key === skip || inGroup(p, g, F[g.key]); }); }
  function money(n) { return 'EGP ' + n.toLocaleString('en-US'); }
  function lbl(g, v) { return g.opts.filter(function (o) { return o[0] === v; })[0][1]; }

  function avail(p) {
    if (p.av === 'ready') return ['', 'Ready to deliver'];
    if (p.av === 'mixed') return ['', '<span>Ready to deliver<span class="sub">More finishes made to order</span></span>'];
    if (p.av === 'mto')   return ['dot--mto', 'Made to order · ' + p.wk[0] + '–' + p.wk[1] + ' wks'];
    return ['dot--out', 'Sold out'];
  }
  function bg(p, i) { return (p.col === 'bone' || p.col === 'putty') ? 'ph--ink' : (i % 2 ? 'ph--paper' : ''); }
  function card(p, i) {
    var a = avail(p), tag = '<span class="tag">Placeholder · sculptural studio</span>';
    var svg = function (m) { return '<svg viewBox="0 0 200 200" preserveAspectRatio="xMidYMax ' + m + '" aria-hidden="true"><use href="#' + p.sym + '"/></svg>'; };
    return '<article class="obj" style="--pc:' + COL[p.col] + '"><a href="' + (p.href || '#') + '">' +
      '<div class="ph ' + bg(p, i) + '">' + svg('meet') + tag +
      '<div class="ph ph--paper alt">' + svg('slice') + '<span class="tag">Placeholder · lifestyle</span></div></div>' +
      '<div class="cap"><div><div class="name">' + p.n + '</div><div class="avail label muted"><span class="dot ' + a[0] + '"></span>' + a[1] + '</div></div>' +
      '<div class="muted">' + money(p.price) + '<br><span class="label">' + p.ref + '</span></div></div></a></article>';
  }
  var FEATURE = '<article class="feature"><div class="ph ph--navy" role="img" aria-label="Placeholder for an editorial image"><svg viewBox="0 0 1600 600" preserveAspectRatio="xMidYMax slice" aria-hidden="true" stroke-linejoin="round" stroke-width="8"><rect y="500" width="1600" height="100" fill="#1D2E49"/><path d="M820 500V250l100-70 200 110v210z" fill="#E2D9CF" stroke="#E2D9CF"/><path d="M1180 500V340l40-40h140l40 40v160z" fill="#CFC3B4" stroke="#CFC3B4"/></svg><span class="tag">Placeholder · editorial image</span></div><p class="muted">Editorial interlude between product rows, an optional block in the section settings.</p></article>';

  // One category selected = that category's page; otherwise the unfiltered shop view
  function setTitle() {
    var name = F.cat.length === 1 ? lbl(G[1], F.cat[0]) : 'All Objects';
    var h = document.querySelector('.ctitle'); if (h) h.textContent = name;
    document.title = name + ' \u2014 OBJEKT (prototype)';
    var crumb = document.querySelector('.chead .crumbs [aria-current]'); if (crumb) crumb.textContent = name;
  }
  function render() {
    setTitle();
    var list = P.filter(function (p) { return matches(p); });
    if (sort === 'price-asc') list.sort(function (a, b) { return a.price - b.price; });
    if (sort === 'price-desc') list.sort(function (a, b) { return b.price - a.price; });
    if (sort === 'name') list.sort(function (a, b) { return a.n.localeCompare(b.n); });
    var html = list.map(function (p, i) { return card(p, P.indexOf(p)) + (i === 3 && !active() && sort === 'featured' ? FEATURE : ''); }).join('');
    $('plp').innerHTML = html; $('empty').hidden = list.length > 0;
    var n = list.length; $('rcount').textContent = n + (n === 1 ? ' object' : ' objects');
    $('show-results').textContent = 'Show ' + n + (n === 1 ? ' object' : ' objects');
    var c = active(); $('fcount').textContent = c ? '(' + c + ')' : '';
    chips(); counts(); url();
  }
  function active() { return G.reduce(function (s, g) { return s + F[g.key].length; }, 0); }

  function chips() {
    var h = '';
    G.forEach(function (g) { F[g.key].forEach(function (v) {
      h += '<button class="chip" type="button" data-g="' + g.key + '" data-v="' + v + '" aria-label="Remove filter ' + g.label + ': ' + lbl(g, v) + '">' + lbl(g, v) + '<span aria-hidden="true">×</span></button>'; }); });
    $('chips').innerHTML = h;
  }

  // Build the drawer once; update counts and disabled state in place so focus is never lost
  function build() {
    $('fbody').innerHTML = G.map(function (g) {
      return '<details class="fg"' + (g.open ? ' open' : '') + '><summary><span class="label">' + g.label + '</span><i aria-hidden="true"></i></summary><fieldset><legend class="sr">' + g.label + '</legend><ul>' +
        g.opts.map(function (o) {
          return '<li><label class="fo" data-fo="' + g.key + ':' + o[0] + '"><input type="checkbox" data-g="' + g.key + '" value="' + o[0] + '"><span class="bx"></span>' +
            (g.swatch ? '<span class="sw" style="--c:' + COL[o[0]] + '"></span>' : '') + '<span>' + o[1] + '</span><span class="ct"></span></label></li>';
        }).join('') + '</ul></fieldset></details>';
    }).join('');
  }
  function counts() {
    G.forEach(function (g) { g.opts.forEach(function (o) {
      var n = P.filter(function (p) { return matches(p, g.key) && g.test(p, o[0]); }).length;
      var row = document.querySelector('[data-fo="' + g.key + ':' + o[0] + '"]'), inp = row.querySelector('input');
      row.querySelector('.ct').textContent = n; inp.checked = F[g.key].indexOf(o[0]) > -1;
      var zero = n === 0 && !inp.checked; inp.disabled = zero; row.classList.toggle('is-zero', zero);
    }); });
  }

  function url() {
    try { var u = new URL(location.href); var keepLang = u.searchParams.get('lang'); u.search = ''; if (keepLang) u.searchParams.set('lang', keepLang);
      G.forEach(function (g) { if (F[g.key].length) u.searchParams.set(g.key, F[g.key].join(',')); });
      if (sort !== 'featured') u.searchParams.set('sort', sort);
      history.replaceState(null, '', u); } catch (e) {}
  }
  function read() {
    var q = new URLSearchParams(location.search);
    G.forEach(function (g) { var v = q.get(g.key); if (v) F[g.key] = v.split(',').filter(function (x) { return g.opts.some(function (o) { return o[0] === x; }); }); });
    if (['price-asc', 'price-desc', 'name'].indexOf(q.get('sort')) > -1) { sort = q.get('sort'); $('sort').value = sort; }
  }
  function clear() { G.forEach(function (g) { F[g.key] = []; }); render(); }

  build(); read(); render();

  $('fbody').addEventListener('change', function (e) {
    var t = e.target; if (!t.matches('input')) return;
    var a = F[t.dataset.g], i = a.indexOf(t.value); if (t.checked && i < 0) a.push(t.value); if (!t.checked && i > -1) a.splice(i, 1);
    render();
  });
  $('chips').addEventListener('click', function (e) {
    var b = e.target.closest('.chip'); if (!b) return;
    var a = F[b.dataset.g]; a.splice(a.indexOf(b.dataset.v), 1); render(); $('open-filters').focus();
  });
  $('sort').addEventListener('change', function (e) { sort = e.target.value; render(); });
  $('clear-all').addEventListener('click', clear); $('clear-empty').addEventListener('click', clear);

  var dlg = $('drawer');
  $('open-filters').addEventListener('click', function () { dlg.showModal(); document.body.style.overflow = 'hidden'; });
  function shut() { dlg.close(); }
  $('close-filters').addEventListener('click', shut); $('show-results').addEventListener('click', shut);
  dlg.addEventListener('click', function (e) { if (e.target === dlg) shut(); });
  dlg.addEventListener('close', function () { document.body.style.overflow = ''; $('open-filters').focus(); });
})();
