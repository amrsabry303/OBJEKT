(function () {
  var drawer = document.getElementById('drawer');
  var openBtn = document.getElementById('open-filters');
  var closeBtn = document.getElementById('close-filters');
  var form = document.getElementById('filters-form');
  var sort = document.getElementById('sort');
  if (!form) { if (sort) sort.addEventListener('change', function () { var u = new URL(location.href); u.searchParams.set('sort_by', sort.value); location.href = u.toString(); }); return; }

  function safe(fn) { try { fn(); } catch (e) { /* one failing step must not stop the rest */ } }
  function params() {
    var fd = new FormData(form), q = new URLSearchParams();
    fd.forEach(function (v, k) { if (v !== '') q.append(k, v); });
    if (sort && sort.name && sort.form !== form) q.set(sort.name, sort.value);
    return q;
  }

  // Dialog open and close. Without JS the form is shown inline and submits normally.
  safe(function () {
    if (!drawer || !drawer.showModal || !openBtn) return;
    openBtn.hidden = false; if (closeBtn) closeBtn.hidden = false;
    openBtn.addEventListener('click', function () { drawer.showModal(); });
    if (closeBtn) closeBtn.addEventListener('click', function () { drawer.close(); });
    drawer.addEventListener('click', function (e) { if (e.target === drawer) drawer.close(); });
    drawer.addEventListener('close', function () { openBtn.focus(); });
  });

  // Submit without empty parameters
  safe(function () {
    form.addEventListener('submit', function (e) { e.preventDefault(); var q = params().toString(); location.href = form.action + (q ? '?' + q : ''); });
  });

  // Sort applies at once
  safe(function () {
    if (sort) sort.addEventListener('change', function () { location.href = form.action + '?' + params().toString(); });
  });

  // Live counts: ask Shopify to render this section with the pending filters (Section Rendering API)
  safe(function () {
    var root = document.getElementById('collection-root');
    if (!root) return;
    var pending = 0;
    form.addEventListener('change', function (e) {
      if (e.target === sort) return;
      var mine = ++pending;
      var url = form.action + '?' + params().toString() + '&section_id=' + encodeURIComponent(root.dataset.sectionId);
      fetch(url, { headers: { 'X-Requested-With': 'fetch' } }).then(function (r) { return r.ok ? r.text() : Promise.reject(r.status); }).then(function (html) {
        if (mine !== pending) return;
        var doc = new DOMParser().parseFromString(html, 'text/html');
        ['show-results'].forEach(function (id) { var a = document.getElementById(id), b = doc.getElementById(id); if (a && b) a.textContent = b.textContent; });
        var open = {}; form.querySelectorAll('details.fg').forEach(function (d, i) { open[i] = d.open; });
        var a = document.getElementById('fbody'), b = doc.getElementById('fbody');
        if (a && b) { a.innerHTML = b.innerHTML; a.querySelectorAll('details.fg').forEach(function (d, i) { d.open = !!open[i]; }); }
        // the checkbox the customer just touched keeps focus
        if (e.target.name) { var again = form.querySelector('input[name="' + e.target.name + '"][value="' + e.target.value + '"]'); if (again) again.focus(); }
      }).catch(function () { /* the submit button still works with the old count */ });
    });
  });
})();
