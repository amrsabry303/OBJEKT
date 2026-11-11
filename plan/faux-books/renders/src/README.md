# How the mockups are made
3D mockups at size M (18 x 25 x 2.8 cm) built from the print generator (`../../print/src/make_print.py`), not AI renders and not photos. Three.js 0.160.0, headless Chromium (SwiftShader), one low sun through a window opening plus soft ambient light, no tone-mapping so cover colours stay close to the brand hex values.

1. Generate the textures first: `python3 ../../print/src/make_print.py <repo root> M` (cow and tiger images land in `../../print/textures/`).
2. `python3 mktex.py` writes one SVG texture per volume and `meta.json`; `node mktex.js` rasterises them to PNG (make `tex/` and `out/` folders first).
3. Serve this folder over http (`python3 -m http.server 8765`) with `npm i three@0.160.0` beside it.
4. `node run.js "$(cat cfgs.json)"` renders every shot to `out/`.

The scripts have the path `/home/user/OBJEKT` written in; change it for another machine. Fonts are not committed. Lettering is the Inter stand-in.
