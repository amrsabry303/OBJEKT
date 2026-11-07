/* The Edit index: topic filter. Prototype only; in Shopify topics are blog tags with real URLs (/blogs/the-edit/tagged/materials). */
(function () {
  var grid = document.getElementById('egrid'), links = document.querySelectorAll('#topics a');
  var t = new URLSearchParams(location.search).get('topic') || 'all';
  var known = Array.prototype.map.call(links, function (a) { return (a.search.match(/topic=([^&]+)/) || [0, 'all'])[1]; });
  if (known.indexOf(t) < 0) t = 'all';
  var shown = 0;
  grid.querySelectorAll('.es').forEach(function (s) { var on = t === 'all' || s.dataset.topic === t; s.hidden = !on; if (on) shown++; });
  grid.classList.toggle('is-filtered', t !== 'all');
  document.getElementById('eempty').hidden = shown > 0;
  links.forEach(function (a, i) { if (known[i] === t) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
})();
