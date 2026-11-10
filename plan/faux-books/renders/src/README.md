# How the mockups are made
3D mockups built from the design flats (`../../artwork/`), not AI renders and not photos. Three.js 0.160.0, headless Chromium (SwiftShader), scene lit by one low sun through a window opening plus soft ambient, no tone-mapping so cover colours stay close to the brand hex values.

1. `python3 mktex.py` writes one SVG texture per volume and `meta.json`; `node mktex.js` rasterizes them to PNG.
2. Serve this folder over http (`python3 -m http.server 8765`) with `npm i three@0.160.0` beside it.
3. `node run.js "$(cat cfgs.json)"` renders every shot to `out/`.

Paths inside the scripts point at the scratch folder used in the session; adjust before re-running. Fonts are not committed. The lettering in the textures is the Inter stand-in.
