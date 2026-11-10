# objekt product images: house style (revised 10 Nov 2026, draft for Sabry)

How we make product images in Magnific until real photographs exist. One current rule set; older
rules are summarised under "History" at the end. Every image is an AI render: name files `ai-render`,
never call them photos in public text, and replace them with real photos when pieces exist.

## 1. The image set per product

| # | Image | Look | When |
|---|---|---|---|
| 1 | One studio shot per colour or finish (the gallery) | Clean studio (section 3) | Always |
| 2 | One editorial mood shot | Editorial (section 4), one colour | Always |
| 3 | One in-use or in-place shot | Real setting (section 5) | Furniture, planters, outdoor and large pieces; optional for small objects |
| 4 | Family shot (two or three colours together) | Clean studio | When the product sells in several colours |

All colour shots of a product come from **one** generated image, recoloured, so shape, light and angle match.
Portrait 4:5 for gallery shots; 3:2 for in-use shots that show the room.

## 2. Shape first: what decides the geometry

Never let the AI invent the shape. In order of preference:

1. **Approved drawing exists:** build the piece in 3D from the drawing's mm (three.js scene in `venture/src/`, e.g. `OBJ-166_rev0_geometry-scene.html`), render it plain grey, check it against the drawing views, then edit that render (method A).
2. **A 3D model exists** (Sabry's own model, e.g. OBJ-177 GLB): render the model in grey at real size and use it as for 1.
3. **No drawing, simple shape** (box, cube, cylinder, plate): build the shape from the best known size (template or workspace, marked approximate) and use method A. OBJ-173 cube.
4. **No drawing, complex shape** (faceted, organic): method B from a tight crop of the reference, and say on the inventory that the shape is an interpretation, not the made piece. OBJ-172 sculpture.

The reference photo shows mood and detail; it never overrides the drawing or the model.

## 3. Clean studio look (gallery shots)

- Light: soft, large, directional daylight from one side (a big window or softbox). Gentle gradient on the backdrop, soft contact shadow under every foot. No sun patches, no light beams, no long dramatic shadows.
- Backdrop: seamless warm off-white or pale warm grey sweep, matte, no visible horizon, no props.
- Camera: eye level or slightly above, 70 to 90 mm look, straight verticals, whole object in frame, slightly off-centre with headroom.
- Materials read true: powder coat matte with fine texture; brushed steel with fine lines along the stated direction; Duco gloss with crisp reflections; mirror (see rule below).
- **Mirror finish:** a mirror on a plain backdrop reads as white paint. Ask for "large black studio flags and softboxes reflected in the planes, some faces near-black, some bright, crisp reflection edges". (OBJ-172 plain shot v1 failed, v2 fixed; Sabry still preferred the studio shot with a room in the reflections.)

## 4. Editorial mood shot

- One warm window light from the left; the wall falls off into soft shade on the right; shadows soft but present.
- Limewash or plaster wall with real texture; sisal, linen, honed limestone or polished concrete underfoot.
- Medium-format film look: 90 mm, f/8, Kodak Portra 400 colour, fine grain, warm slightly desaturated grade.
- One or two chosen props that show use and are smaller than the product (a stoneware vase on the shorter plinth, a spider plant in the planter, a book). Neutral colours. Say "smaller than the top" or the prop comes out too big.
- After generation, run `venture/src/image_film_finish.py` (grain, tone curve, slight vignette) on mood shots only.

## 5. In-use or in-place shot

- A real Egyptian setting: villa garden, entry, living room, sea-facing terrace. Use Sabry's own location photos when he supplies them (OBJ-172 villa): pass the location photo plus the approved studio image of the product, and ask for "a casual natural mobile phone photo, eye height, honest daylight, real colours, slightly imperfect" when he wants that feel.
- Check scale against the room (doors are about 2.2 to 2.4 m). OBJ-172 garden B came out too large; A was right.
- The product must sit in the scene: contact shadow, grass or rug around the base, reflections matching the light. Fix with a `preciseEdit` pass that only adds contact shadow and grounding.
- If the location is a real private home, ask Sabry before it is used publicly.

## 6. Methods (Magnific)

**Method A, geometry first** (`ideogram-4-5` + `preciseEdit`, 80 credits, count 2):
1. Upload ONLY the grey geometry render. A second reference makes the model copy that reference's proportions (OBJ-002 arranged v1 failed this way).
2. Prompt: "Turn this into a real product photograph. Keep the <object> exactly as it is: same size, proportions, <parts and counts>, position and camera angle. <finish with colour name and hex, texture>. <section 3, 4 or 5 setting>. No props, no text."
3. Pick the result that keeps feet, edges and counts; zoom in on the base before choosing.
4. Recolour: run a second `preciseEdit` on the chosen image: "Change only the finish of the <object> to <colour hex, texture>. Keep everything else exactly the same." One recolour per colour.

**Method B, reference first** (`imagen-nano-banana-2-1`, 65 credits, count 2): tight crop of the product alone, prompt with 3 to 5 plain facts about shape and part counts, "only one <object>", finish, setting. Use for complex shapes with no drawing or model.

**Editing a finished image** (`preciseEdit` on the chosen output): change background, add a prop, fix grounding, fix the mirror look. The product stays as it is.

## 7. Checks before an image is shown to Sabry

1. Shape against the drawing or model: outline, part counts, feet, cut-outs, seams. Overlay or side-by-side if in doubt.
2. Proportions: height-to-width ratio and heights of a set (OBJ-166: 1000 and 850 must read as different; one mood result shortened the 850 and was rejected).
3. Colour against the hex, sampled from the image. Drift is common: Oxblood went berry and was fixed locally (hue shift 315-12 deg to 354 deg, saturation x0.8, value x0.86-0.88, inside a mask from the 3D scene).
4. Contact shadow under every foot; base not buried by a rug or grass more than a few mm.
5. No holes, artefacts or smudges (OBJ-172 garden B had a white blob; check the floor and corners).
6. Scale in context shots.
7. Then save, upload, log in `plan/IMAGE-INVENTORY.md` as "Pending Sabry".

## 8. Colours and finishes

Only from `brand/COLOURS-FINISHES.md`: Bone #E9E4D8, Putty #B9B2A5, Carbon #222222, Ink #1E2A44, Oxblood #5A1F25, Clay #A8553A, Chocolate #4A2A1B, Objekt Green #37613F. Finishes: powder coat or Duco, matte or gloss; exposed metal brushed or mirror. Finishes come from the drawing's colourways; if Sabry asks for another, render it and flag the difference.

## 9. Files, approval and cost

- Local: `plan/images/OBJ-nnn/OBJ-nnn_ai-render_<colour>_<scene>_<source>_vN.jpg` (source: `rev5-geometry`, `no-drawing`, `model`). Geometry renders in `geometry/`. Keep superseded files with `superseded_`, rejected ones with `rejected_`.
- Drive: the product's folder in the images folder (create `OBJ-nnn` if missing). Uploads from here are limited to about 3 MB per file.
- Approval: Sabry approves in chat; mark the inventory line "Approved by Sabry <date>". Only approved images go to the store, and only with his yes.
- Cost per product, typical: geometry studio 160 (2 tries) + recolours 80 each + mood 160 + in-use 130 to 160. Plan about 600 to 800 credits per product with three colours. Check the balance before a batch.

## 10. Do not

- Generate shape from the reference photo when a drawing or model exists.
- Pass two image references to `preciseEdit`.
- Use hard sun patches, light beams or dramatic shadows in studio shots.
- Put brand-coloured props in a shot, or more than two props.
- Draw foot or fixing markers on geometry models (they come out as dark dots); model the real feet instead.
- Write prices, sizes or claims on images. No text in images.
- Mention AI or renders in public copy (Sabry, 10 Nov).

## History (superseded, kept for the record)

- 2 Nov: one look for all: pale sand plaster wall and floor (#E1D9CF), no props, nano banana from the reference photo. Then the same day: hard low window sun, sunlit patches and props in use. Replaced on 10 Nov because both read as AI.
- 10 Nov: Sabry: "the AI photos look so AI"; references from @soosatelier (editorial) and five product photos (studio). Decision: clean studio for colour shots, one editorial mood shot. Rule: the approved drawing decides the shape (OBJ-038 renders from the photo did not match REV 4).
- 10 Nov: methods proven on OBJ-038, OBJ-002 (REV 5), OBJ-099, OBJ-166 (REV 0), OBJ-173 (no drawing, cube), OBJ-172 (no drawing, complex; villa context from Sabry's photo).
