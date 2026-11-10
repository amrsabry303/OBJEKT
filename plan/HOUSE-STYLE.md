# objekt product images: house style (revised 11 Nov 2026 with Sabry's notes)

How we make product images in Magnific until real photographs exist. One current rule set; older
rules are summarised under "History" at the end. Every image is an AI render: name files `ai-render`,
never call them photos in public text, and replace them with real photos when pieces exist.

## 1. The image set per product

| # | Image | Look | When |
|---|---|---|---|
| 1 | One studio shot per colour or finish (the gallery) | Clean studio (section 3) | Always |
| 2 | One or more editorial shots | Editorial (section 4), one colour each | Always |
| 3 | One in-use or in-place shot | Real setting (section 5) | Furniture, planters, outdoor and large pieces; optional for small objects |
| 4 | Family shot (two or three colours together) | Clean studio | When the product sells in several colours |

All colour shots of a product come from **one** generated image, recoloured, so shape, light and angle match.
Portrait 4:5 for gallery shots; 2:3 or 4:5 for editorial; 3:2 for in-use shots that show a wide room. Every image gets the camera finish (section 7).

## 2. Shape first: what decides the geometry

Never let the AI invent the shape. In order of preference:

1. **Approved drawing exists:** build the piece in 3D from the drawing's mm (three.js scene in `venture/src/`, e.g. `OBJ-166_rev0_geometry-scene.html`), render it plain grey, check it against the drawing views, then edit that render (method A).
2. **A 3D model exists** (Sabry's own model, e.g. OBJ-177 GLB): render the model in grey at real size and use it as for 1.
3. **No drawing, simple shape** (box, cube, cylinder, plate): build the shape from the best known size (template or workspace, marked approximate) and use method A. OBJ-173 cube.
4. **No drawing, complex shape** (faceted, organic): method B from a tight crop of the reference, and say on the inventory that the shape is an interpretation, not the made piece. OBJ-172 sculpture.

The reference photo shows mood and detail; it never overrides the drawing or the model.

## 3. Clean studio look (gallery shots)

- Light: soft, large, directional daylight from one side (a big window or softbox). Gentle gradient on the backdrop, soft contact shadow under every foot. No sun patches, no light beams, no long dramatic shadows.
- Backdrop: seamless warm greige or warm off-white sweep, matte, no visible horizon, no props. Never pure white or cold grey: the references never go above about 235 in the highlights and are always warm.
- Camera: choose the angle that shows the object best (low for a bench or table, close and high for a tray, straight-on for a wall piece). 70 to 90 mm look, straight verticals, whole object in frame. **All colour variants of one product use the same angle and framing** (they come from one image).
- Materials read true: powder coat matte with fine texture; brushed steel with fine lines along the stated direction; Duco gloss with crisp reflections; mirror (see rule below).
- **Mirror finish:** a mirror on a plain backdrop reads as white paint. Ask for "large black studio flags and softboxes reflected in the planes, some faces near-black, some bright, crisp reflection edges". (OBJ-172 plain shot v1 failed, v2 fixed; Sabry still preferred the studio shot with a room in the reflections.)

## 4. Editorial shot (mood)

Not one fixed scene. Choose the environment, light and composition that suit the piece: a dark sofa and a
pale rug with a slice of low sun, a quiet corner with a pedestal and a vase, a doorway looking into a
furnished living room, a calm bedroom, a garden or terrace. What keeps them objekt (from Sabry's references, 11 Nov):
- **Restrained palette:** warm neutrals (greige, sand, cream, taupe, brown), one darker anchor (charcoal sofa, dark wood), no loud colours except the product's own.
- **Real interiors are allowed:** a fully furnished room can still look minimal: few objects, each one chosen, plenty of quiet wall. Props are natural, not counted: books, a stone, a ceramic vase, a throw, a lamp. They support the product and never compete with it.
- **Natural light with direction:** soft window light, or a single soft-edged slice of sun across the floor (reference 1). Shadows warm, never blue.
- **The product is the clear subject:** largest object in focus, or framed through a doorway; it may be cut by the frame edge when that helps the composition.
- **Composition varies:** close crop on the product, product in the corner of a room, view through a door. Portrait 2:3 or 4:5.
- **Camera:** the best angle for the piece (not fixed at eye level); natural lens, no wide-angle distortion.
- Always finished with the camera finish (section 7).

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

## 7. Camera finish: grain and tone (every image)

Measured on Sabry's five references (11 Nov). This is what makes them read as photographs, and it is what our
renders lack (our studio shots measured: almost no grain, near-white highlights, neutral or blue shadows):

| | References | Our raw renders |
|---|---|---|
| Grain on plain walls (high-pass, 0-255) | 1.9 to 3.4 | 0.4 to 1.1 |
| Grain type | monochrome, clumped 2-3 px at 2000 px tall, strongest in the mid-tones | none or fine colour noise |
| Brightest tones (99th pct) | 199 to 238, cream | 234, neutral white |
| Darkest tones (1st pct) | 11 to 28, soft | 15 to 38 |
| Shadows | warm brown (R above B by 9 to 31) | neutral or blue |
| Saturation | 0.14 to 0.27, warm | 0.05 to 0.15 |

How to apply:
1. In the prompt: warm greige surroundings, warm light, deep but soft shadows; no pure white backdrop.
2. After generation, always run `venture/src/image_film_finish.py <in> <out> studio` (gallery) or `editorial` (mood and in-use). It rolls the whites off to cream, lifts the blacks slightly, warms shadows and highlights, softens a touch and adds monochrome clumped grain at the reference strength. It does not change saturation, so product colours stay on their hex.
3. Check with `python image_film_finish.py --measure <file>`: every value should read ok. If blacks or saturation are out, the generation is too flat or too cold: regenerate with a darker anchor or warmer setting rather than forcing it in the finish.

## 8. Checks before an image is shown to Sabry

1. Shape against the drawing or model: outline, part counts, feet, cut-outs, seams. Overlay or side-by-side if in doubt.
2. Proportions: height-to-width ratio and heights of a set (OBJ-166: 1000 and 850 must read as different; one mood result shortened the 850 and was rejected).
3. Colour against the hex, sampled from the image (after the finish). Drift is common: Oxblood went berry and was fixed locally (hue shift 315-12 deg to 354 deg, saturation x0.8, value x0.86-0.88, inside a mask from the 3D scene).
4. Contact shadow under every foot; base not buried by a rug or grass more than a few mm.
5. No holes, artefacts or smudges (OBJ-172 garden B had a white blob; check the floor and corners).
6. Scale in context shots.
7. Camera finish applied and `--measure` reads ok.
8. Then save, upload, log in `plan/IMAGE-INVENTORY.md` as "Pending Sabry".

## 9. Colours and finishes

Only from `brand/COLOURS-FINISHES.md`: Bone #E9E4D8, Putty #B9B2A5, Carbon #222222, Ink #1E2A44, Oxblood #5A1F25, Clay #A8553A, Chocolate #4A2A1B, Objekt Green #37613F. Finishes: powder coat or Duco, matte or gloss; exposed metal brushed or mirror. Finishes come from the drawing's colourways; if Sabry asks for another, render it and flag the difference.

## 10. Files, approval and cost

- Local: `plan/images/OBJ-nnn/OBJ-nnn_ai-render_<colour>_<scene>_<source>_vN.jpg` (source: `rev5-geometry`, `no-drawing`, `model`). Geometry renders in `geometry/`. Keep superseded files with `superseded_`, rejected ones with `rejected_`.
- Drive: the product's folder in the images folder (create `OBJ-nnn` if missing). Uploads from here are limited to about 3 MB per file.
- Approval: Sabry approves in chat; mark the inventory line "Approved by Sabry <date>". Only approved images go to the store, and only with his yes.
- Cost per product, typical: geometry studio 160 (2 tries) + recolours 80 each + mood 160 + in-use 130 to 160. Plan about 600 to 800 credits per product with three colours. Check the balance before a batch.

## 11. Do not

- Generate shape from the reference photo when a drawing or model exists.
- Pass two image references to `preciseEdit`.
- Use hard sun patches, light beams or dramatic shadows in studio (gallery) shots. A soft slice of sun is fine in editorial shots.
- Let props compete with the product (loud colours, bigger or busier than the piece).
- Draw foot or fixing markers on geometry models (they come out as dark dots); model the real feet instead.
- Write prices, sizes or claims on images. No text in images.
- Mention AI or renders in public copy (Sabry, 10 Nov).

## History (superseded, kept for the record)

- 2 Nov: one look for all: pale sand plaster wall and floor (#E1D9CF), no props, nano banana from the reference photo. Then the same day: hard low window sun, sunlit patches and props in use. Replaced on 10 Nov because both read as AI.
- 10 Nov: Sabry: "the AI photos look so AI"; references from @soosatelier (editorial) and five product photos (studio). Decision: clean studio for colour shots, one editorial mood shot. Rule: the approved drawing decides the shape (OBJ-038 renders from the photo did not match REV 4).
- 11 Nov (Sabry): no fixed eye-level camera (best angle per object, same angle across colours); no prop limit (restrained but natural, furnished rooms allowed); editorial not locked to limewash and film grain (varied settings sharing the objekt identity). Grain and tone measured on his five references and built into the camera finish for every image.
- 10 Nov: methods proven on OBJ-038, OBJ-002 (REV 5), OBJ-099, OBJ-166 (REV 0), OBJ-173 (no drawing, cube), OBJ-172 (no drawing, complex; villa context from Sabry's photo).
