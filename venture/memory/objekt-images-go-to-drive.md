---
name: objekt-images-go-to-drive
description: "Every AI image I generate for an objekt product is saved in that product's Drive design folder (and locally in _plan/images/OBJ-nnn)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 4601baf8-5f93-4f8b-a853-4a4656133fba
  modified: 2026-11-02T11:31:50.398Z
---

Sabry said (2 Nov 2026): save all images generated for each product in its folder. First done for OBJ-003 (3 renders: Bone v1, Oxblood v1, Oxblood v2) in Drive folder 1YQ_OgCFzG2BkfD0iXeNfVaPdtK6P1AU7.

**Why:** Production and the website work from the Drive design folders, not from my local files; same reasoning as [[objekt-drawings-go-to-drive]].
**How to apply:**
- Keep a local copy in `POLYCRAFT/_plan/images/OBJ-nnn/`, named `OBJ-nnn_ai-render_<colour>_<scene>_vN.png`. Keep superseded versions (do not delete).
- Upload to the product's Drive folder (the `FOLDERS` map in the workspace has the link). Method as in the drawings skill step 11, but `file_upload` caps 10 MB per call and renders are about 5 MB, so use one hidden input per file and combine them into one DataTransfer for a single drop. Check the folder first; wait for "uploads complete" before reporting.
- These are AI renders, not photos of the prototype. Say so, and name the file `ai-render`.
- House style set 2 Nov 2026 in `POLYCRAFT/_plan/images/HOUSE-STYLE.md` (scene, prompt template, lessons, budget). Use it for every product; do not rerun scene experiments. One image per product, one at a time. Credits: 20,000 plan, about 695 spent by 2 Nov. See [[objekt-brand-guidelines]].
- **Image stickers (2 Nov 2026):** every one of the 45 book slides has a second pill `img_NNN` under the design-file pill (green "IMAGES: N AI RENDERS · الصور: N", yellow "NO IMAGES YET · لا توجد صور بعد"). When I add renders to a product, update its pill: replaceAllText on the pill text plus fill rgb 0.18,0.49,0.20 and white text (the shortened text avoids wrapping). Counts live in `POLYCRAFT/_plan/images/IMAGE-INVENTORY.csv` and `.md`; keep them in step.
- **Magnific history holds other renders:** OBJ-137 (6 renders from 26 Oct, a session before this one) are now filed. DAR-Q, Uncle Dough and Lux renders belong to other projects: never file those. Six geometric sculpture renders (elephant calf, falcon) are unmatched to a launch product.
- Slide update lesson: create stickers from a template with createShape, updateShapeProperties, insertText, updateTextStyle, updateParagraphStyle; batches of about 19 slides worked.
- **Context image for every product (Sabry, 2 Nov 2026):** each product also needs an in-context shot (real room, in use, low sun, same aesthetics) alongside the colour product shots. Use the product's own finished render as the image reference, 3:2, one or two plain props. First done for OBJ-099 Oxblood (dining table). Count it in the sticker. Details in HOUSE-STYLE.md.
- **Lesson, OBJ-169 (2 Nov 2026):** a geometry model built from my own drawing only reproduces my reading. When the drawing misread the photo (stand orientation and plate-top profile), the geometry render was wrong and looked CG. For products where the reference photo is clear, generate from the photo itself (`imagen-nano-banana-2-1`, photo as image reference), then re-place the result in the house scene by using that render as the next reference (two steps, 65 each). Never file a render that copies the reference's room or furniture. The geometry method is only for plain boxes and plates.
- **OBJ-003 (2 Nov 2026):** Sabry's own 3D model is the geometry source: thin round top, three tall egg-shaped discs (flat foot) at 120 degrees passing up through slots, a small cap (6.4 on a 40 top height, disc 46.39 tall, top 130.06 wide) showing above. When Sabry supplies a model, use it as the `preciseEdit` reference (ideogram-4-5, 80 credits): the first try kept the geometry; a second colour drifted (caps enlarged) and needed one retry with "do not change any shape ... caps only a little higher". The old 003 renders (separate half-disc fins) were wrong.
- **Colour and angle audit (2 Nov 2026, OBJ-003):** Sabry judged the Oxblood "off" and the angle unattractive. Measured: AI renders drift in hue with the light (003 came out rust on top, plum on legs, one cap pink; 099 and 167 sat browner). Fix: measure the red pixels (HSV), then recolour inside the product silhouette to the brand hex while keeping the shading (hue 354, sat 0.66, value 0.35 for Oxblood), using the geometry model's outline as the mask so floor shadows are not touched. Do not mask by colour alone (it paints the floor shadows pink). Bone needed no correction (lit p90 matched #E9E4D8). Angle: use an elevated three-quarter view (about 55 deg yaw, 21 deg elevation from the geometry model), not a flat frontal low view. Check Oxblood across 099, 167, 003 for one consistent look.

**Oxblood consistency pass (2 Nov 2026):** 099 (x2), 167, 137 (x2) recoloured to brand #5A1F25 by HSV inside a product mask (v1 files renamed superseded_). Masks must be product-only: hue-only masks painted wall shadows (167) and the chair (099 context); 167 needed a hand box mask, 137 needed exclusion boxes for floor shadows under the legs. Drive upload of the v2 files still pending Sabry's go.
