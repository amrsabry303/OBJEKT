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
})();
