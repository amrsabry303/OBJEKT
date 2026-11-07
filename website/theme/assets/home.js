(function () {
  // Category index: the picture follows hover or keyboard focus. Progressive: the links work without it.
  try {
    var links = document.querySelectorAll('[data-pane-target]');
    if (!links.length) return;
    function show(id) { document.querySelectorAll('[data-pane]').forEach(function (p) { p.classList.toggle('on', p.dataset.pane === id); }); }
    links.forEach(function (a) {
      a.addEventListener('mouseenter', function () { show(a.dataset.paneTarget); });
      a.addEventListener('focus', function () { show(a.dataset.paneTarget); });
    });
  } catch (e) { /* the links still work */ }
})();
